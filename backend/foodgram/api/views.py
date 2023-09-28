from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
#from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
#                                        IsAuthenticatedOrReadOnly)

from api.serializers import (TagSerializer, RecipeSerializer, 
                             IngredientSerializer)
from recipes.models import Tag, Recipe, Ingridient
from api.permissions import RecipePermission

def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(ReadOnlyModelViewSet):
    """Обрабатываем запросы к модели ингредиентов."""
    queryset = Ingridient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

#class RecipeViewSet(ModelViewSet):
#    queryset = Recipe.objects.all()
#    serializer_class = RecipeSerializer
#    permission_classes = [RecipePermission]
#    ordering_fields = ()

#    def get_queryset(self):
#        recipes = Recipe.objects.prefetch_related(
#            'amount_ingredients__ingredient', 'tags'
#        ).all()
#        return recipes

#    def perform_create(self, serializer):
#        return serializer.save(author=self.request.user)

#    def get_serializer_class(self):
#        if self.action == 'create':
#            return RecipeCreateSerializer
#        return RecipeSerializer