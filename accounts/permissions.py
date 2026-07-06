from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Admin").exists()


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Staff").exists()
            or request.user.groups.filter(name="Admin").exists()
        )


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    