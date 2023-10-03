from django.contrib import admin

# from django.contrib.admin import display

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    IngredientRecipes,
    Favorite,
    ShoppingCart,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    list_filter = (
        "name",
        "slug",
    )
    search_fields = ("name",)
    empty_value_display = "empty"


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class ReceptAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = ("author", "name", "tags")
    search_fields = ("name",)
    filter_horizontal = ("tags",)
    inlines = (RecipeIngredientInline,)
    fields = (
        "name",
        "author",
        "image",
        "cooking_time",
        "text",
        "tags",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    search_fields = ("name",)
    empty_value_display = "empty"


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(IngredientRecipes)
