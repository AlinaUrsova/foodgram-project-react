from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from recipes.models import Tag, IngredientRecipes, Ingredient, Recipe


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения данных из модели с ингрединтами."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientRecipesSerializer(ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""
    tags = TagSerializer(many=True)
    ingridients = IngredientRecipesSerializer(many=True, 
                                              source='ingredientrecipes_set')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    class Meta:
        model = Recipe
        fields = '__all__'
    
    

#class RecipeSerializer(ModelSerializer):
#    tags = TagSerializer(many=True)
#    ingridients = IngredientRecipesSerializer(many=True, 
#                                              source='ingredientrecipes_set')


#    class Meta:
#        model = Recipe
#        fields = '__all__'


#class RecipteIngredientCreateSerializer(ModelSerializer):
#    id = serializers.PrimaryKeyRelatedField(
#        source='ingredient',
#        queryset=Ingridient.objects.all(),
#        many=True
#        )


#    class Meta:
#        model = IngredientRecipes
#        fields = ('id', 'amount')


#class RecipeCreateSerializer(ModelSerializer):
#    ingredients = RecipteIngredientCreateSerializer(many=True)


#    class Meta:
#        model = Recipe
#        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients')
    

#    def create(self, validated_data):
#        tags = validated_data.pop('tags')
#        ingredients = validated_data.pop('ingredients')
#        recipe = Recipe.objects.create(**validated_data)
#        recipe.tags.set(tags)
#        self.create_ingredients(recipe=recipe, ingredients=ingredients)
#        return recipe
