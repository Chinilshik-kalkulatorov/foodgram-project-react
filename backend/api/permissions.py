from rest_framework import permissions


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    """
    GET - открытый доступ;
    POST, PATCH, DEL - автор, admin, moderator, superuser.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or (request.user.is_authenticated and (
                request.user.is_admin
                or request.user.is_moderator)
                )
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    GET - открытый доступ;
    POST, PATCH, DEL - только admin и superuser.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdmin(permissions.BasePermission):
    """Доступ только для admin и superuser по всем запросам."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser)
                )
