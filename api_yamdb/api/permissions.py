from django.contrib.auth import get_user_model
from rest_framework.permissions import SAFE_METHODS, BasePermission

User = get_user_model()


class IsAdmin(BasePermission):
    """
    Проверка, есть ли у пользователя права администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Проверка, есть ли у пользователя права администратора.
    Иначе доступ только на чтение.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class CreateOrIsAuthorOrReadOnly(BasePermission):
    """
    Права доступа пользователя.
    """
    def has_permission(self, request, view):
        """
        Неавторизованный пользователь имеет права только на чтение.
        """
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return True

    def has_object_permission(self, request, view, obj):
        """
        Пользователь имеет права доступа к объекту, если:
        1. Пользователь авторизован и:
        1.1. Пользователь имеет права администратора;
        1.2. Пользователь имеет права модератора;
        1.3. Пользователь - автор объекта;
        1.4. Требуется доступ на чтение или создание объекта
        Или:
        2. Пользователь не авторизован и:
        2.1. Требуется доступ на чтение.
        """
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moder
            or request.user == obj.author
        )


class IsGuest(BasePermission):
    """
    Проверка, является ли пользователь ананоимным.
    """
    def has_permission(self, request, view):
        """
        Действие доступно только неавторизованному пользователю.
        """
        return request.user.is_anonymous
