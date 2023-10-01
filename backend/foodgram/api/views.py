from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.serializers import (TagSerializer, RecipeSerializer, 
                             IngredientSerializer, RecipeCreateSerializer,
                             CustomUserSerializer)
from recipes.models import Tag, Recipe, Ingredient
#from users.models import User
from api.permissions import AuthorOrReadOnly, AdminOrReadOnly

User = get_user_model()

def index(request):
    return HttpResponse('index')


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Обрабатываем запросы к модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    permission_classes = [AuthorOrReadOnly, AdminOrReadOnly]
    ordering_fields = ()

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'amount_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer


class CustomUserViewSet(UserViewSet):
    """Вьюсет для создания обьектов класса User."""

    quryset = User.objects.all()
    serializer_class = CustomUserSerializer


