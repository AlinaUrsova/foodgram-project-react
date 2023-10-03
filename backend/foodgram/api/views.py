from http import HTTPStatus
from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets, exceptions
from djoser.serializers import SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend
#from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
#from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.serializers import (TagSerializer, RecipeSerializer, 
                             IngredientSerializer, RecipeCreateSerializer,
                             CustomUserSerializer,
                             RecipeShortSerializer, FavoriteSerializer,
                             ShoppingCartSerializer, SubscriptionReadSerializer,
                             SubscriptionSerializer)
from recipes.models import Tag, Recipe, Ingredient, Favorite, IngredientRecipes, ShoppingCart
from users.models import Subscription
from api.permissions import AuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
#from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from rest_framework import permissions
from api.utils import create_shopping_cart, create_object, delete_object
from api.pagination import CustomPagination


User = get_user_model()

def index(request):
    return HttpResponse('index')


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Обрабатываем запросы к модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ['^name', ]
    


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorOrReadOnly,]
    ordering_fields = ()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'amount_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer
    
    
class CustomUserViewSet(UserViewSet):
    """Вьюсет для создания обьектов класса User."""

    quryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']

            if self.request.user.check_password(current_password):
                self.request.user.set_password(new_password)
                self.request.user.save()
                return Response(status=204)
            else:
                return Response({'detail': 'Пароли не совпадают.'},
                                status=400)
        else:
            return Response(serializer.errors, status=400)
    
    @action(
        detail=False,
        methods=['GET'],
        serializer_class=SubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.follower.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Нельзя подписаться на самого себя'
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'На этого автора уже есть подписка'
                )
            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=HTTPStatus.CREATED)

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Нет такой подписки'
                )
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(status=HTTPStatus.METHOD_NOT_ALLOWED)


class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def add_and_delete_favorite(self, request, pk):
        """Позволяет пользователю добавлять|удалять рецепты в|из избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeShortSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        favorite_recipe = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ViewSet):
    """Вьюсет для взаимодействий со списком покупок"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShoppingCartSerializer
    pagination_class = None

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def action_recipe_in_cart(self, request, pk):
        """Позволяет пользователю добавлять/удалять рецепты
        в|из список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeShortSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет пользователю загрузить список покупок."""
        ingredients_cart = (
            IngredientRecipes.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)

