from http import HTTPStatus

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly, SAFE_METHODS
from api.serializers import (CustomUserSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, RecipeShortSerializer,
                             ShoppingCartSerializer, TagSerializer,
                             SubscriptionSerializer)
from api.utils import create_shopping_cart
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipes, Recipe, ShoppingCart, Tag)
from rest_framework import (decorators, permissions, response,
                            status, viewsets)
from users.models import Subscription
from api.pagination import PageLimitPagination

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = [
        "^name",
    ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Recipe."""

    permission_classes = [
        AuthorOrReadOnly,
    ]
    ordering_fields = ()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            "amount_ingredients__ingredient", "tags"
        ).all()
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer


class CustomUserViewSet(UserViewSet):
    """Вьюсет для создания обьектов класса User."""

    quryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageLimitPagination

    @decorators.action(detail=False, methods=["POST"])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            current_password = serializer.validated_data["current_password"]
            new_password = serializer.validated_data["new_password"]

            if self.request.user.check_password(current_password):
                self.request.user.set_password(new_password)
                self.request.user.save()
                return response.Response(status=204)
            else:
                return response.Response(
                    {"detail": "Пароли не совпадают."},
                    status=400)
        else:
            return response.Response(serializer.errors, status=400)

    @decorators.action(methods=['POST', 'DELETE'],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return response.Response({'error': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return response.Response({'error': 'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(author, context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return response.Response(status=status.HTTP_204_NO_CONTENT)
            return response.Response({'error': 'Вы не подписаны на этого пользователя'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = SubscriptionSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class FavoriteViewSet(viewsets.ViewSet):
    """Вьюсет для создания обьектов класса Favorite."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer

    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def add_and_delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"user": request.user.id, "recipe": recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeShortSerializer(recipe)
            return response.Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        favorite_recipe = get_object_or_404(Favorite,
                                            user=request.user, recipe=recipe)
        favorite_recipe.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ViewSet):
    """Вьюсет для создания обьектов класса ShoppingCart."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShoppingCartSerializer
    pagination_class = None

    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def action_recipe_in_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            serializer = ShoppingCartSerializer(
                data={"user": request.user.id, "recipe": recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeShortSerializer(recipe)
            return response.Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        shopping_cart_recipe.delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients_cart = (
            IngredientRecipes.objects.filter(
                recipe__shopping_cart__user=request.user)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .order_by("ingredient__name")
            .annotate(ingredient_value=Sum("amount"))
        )
        return create_shopping_cart(ingredients_cart)
