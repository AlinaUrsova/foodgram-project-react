from django.contrib import admin
#from django.contrib.admin import display

from recipes.models import Tag, Recipe, Ingridient, IngredientRecipes


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientRecipes
    extra = 1


@admin.register(Recipe)
class ReceptAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    inlines = (RecipeIngredientInline, )

@admin.register(Ingridient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)