from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from api.views import index, CustomUserViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]