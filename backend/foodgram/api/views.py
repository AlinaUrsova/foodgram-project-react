from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from djoser.serializers import SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend
#from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from api.serializers import (TagSerializer, RecipeSerializer, 
                             IngredientSerializer, RecipeCreateSerializer,
                             CustomUserSerializer,
                             RecipeShortSerializer, FavoriteSerializer,
                             ShoppingCartSerializer)
from recipes.models import Tag, Recipe, Ingredient, Favorite, IngredientRecipes, ShoppingCart
#from users.models import User
from api.permissions import AuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
#from rest_framework.permissions import SAFE_METHODS
from rest_framework.decorators import action
from rest_framework import permissions


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

