from django.db import models


class Tag(models.Model):
    """ Модель Тэг """

    name = models.CharField('Название',
                            max_length=200)
    color = models.CharField('Цвет в HEX',
                             max_length=7)
    slug = models.CharField('Уникальный слаг',
                            max_length=200,
                            unique=True)
