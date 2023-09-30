from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from recipes.models import Tag, IngredientRecipes, Ingredient, Recipe


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения данных из модели с ингрединтами."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientRecipesSerializer(ModelSerializer):
    '''
    Сериалайзер для модели IngredientRecipes.
    Используется для коректного отображения полей ингредиента при чтении.
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipes
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipteIngredientCreateSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
        many=True
        )


    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериалайзер для модели Recipe.
    Используется на отображение необходимых полей при чтеннии.
    '''
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipesSerializer(
        many=True, source='amount_ingredients'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели Recipe.
    Используется для записи рецепта.
    '''
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipteIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )

    def create_ingredients(self, ingredients, recipe):
        '''Метод создания ингредиентов с количеством ингредиентов.'''
        for ingredient in ingredients:
            ingredients, status = IngredientRecipes.objects.get_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
            print(ingredient)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        IngredientRecipes.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeCreateSerializer(instance,
                                    context=context).data

