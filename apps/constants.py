from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated

# class IsAdminOrAuthenticated(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.role in ['Admin', 'Service Povider']

# class IsAdminOrAuthenticated(IsAuthenticated):
#     def has_permission(self, request, view):
#         return super().has_permission(request, view) and request.user.role is not None


class IsAdminOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return True

        return user.role in ["Admin", "admin", "Service Provider"]
