from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    """Custom permission class"""
    def has_permission(self, request, view):
        """Authorised or read only"""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Unsave methods and GET method for shopping lists"""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (obj.author == request.user or request.method == 'POST'))
        )