from rest_framework.serializers import ModelSerializer

from recipes.models import Tag


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""

    class Meta:
        model = Tag
        fields = '__all__'
