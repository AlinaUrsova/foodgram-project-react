from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from recipes.models import Tag, Recipe, IngredientRecipes


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipesSerializer(ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingridients = IngredientRecipesSerializer(many=True, 
                                              source='ingredientrecipes_set')


    class Meta:
        model = Recipe
        fields = '__all__'
