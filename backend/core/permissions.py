from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access to admin users only."""
    message = 'Access denied. Admin accounts only.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsNurse(BasePermission):
    """Allow access to nurse users only."""
    message = 'Access denied. Nurse accounts only.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'nurse')


class IsEmployer(BasePermission):
    """Allow access to employer users only."""
    message = 'Access denied. Employer accounts only.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'employer')


class IsAdminOrReadOnly(BasePermission):
    """Allow read access to anyone authenticated, write access to admins only."""
    message = 'Access denied. Admin accounts only for write operations.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role == 'admin'


class IsNurseOrAdmin(BasePermission):
    """Allow access to nurses and admins."""
    message = 'Access denied. Nurse or admin accounts only.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role in ('nurse', 'admin')
        )


class IsEmployerOrAdmin(BasePermission):
    """Allow access to employers and admins."""
    message = 'Access denied. Employer or admin accounts only.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            request.user.role in ('employer', 'admin')
        )
