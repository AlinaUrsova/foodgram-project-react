from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from api.views import (index, CustomUserViewSet, TagViewSet, 
                       RecipeViewSet, IngredientViewSet,FavoriteViewSet)


app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')
router_v1.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('recipes/<int:pk>/favorite/',
         FavoriteViewSet.as_view({'post': 'add_and_delete_favorite',
                                  'delete': 'add_and_delete_favorite'}),
         name='add_favorite-remove_favorite'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]