from api.views import (CustomUserViewSet, FavoriteViewSet, IngredientViewSet,
                       RecipeViewSet, ShoppingCartViewSet, TagViewSet)
from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", CustomUserViewSet, basename="users")
router_v1.register(r"recipes", RecipeViewSet, basename="recipe")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredient")
router_v1.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path(
        "recipes/<int:pk>/favorite/",
        FavoriteViewSet.as_view(
            {"post": "add_and_delete_favorite",
             "delete": "add_and_delete_favorite"}
        ),
        name="add_favorite-remove_favorite",
    ),
    path(
        "recipes/<int:pk>/shopping_cart/",
        ShoppingCartViewSet.as_view(
            {"post": "action_recipe_in_cart",
             "delete": "action_recipe_in_cart"}
        ),
        name="add_shopping_cart-remove_shopping_cart",
    ),
    path(
        "recipes/download_shopping_cart/",
        ShoppingCartViewSet.as_view({"get": "download_shopping_cart"}),
        name="download_shopping_cart",
    ),
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
