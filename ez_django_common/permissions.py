from rest_framework.permissions import DjangoModelPermissions
from rest_framework import exceptions


class CustomDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def __init__(self, other_permissions=None):
        super(CustomDjangoModelPermissions, self).__init__()
        self.other_permissions = other_permissions or []

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            "app_label": model_cls._meta.app_label,
            "model_name": model_cls._meta.model_name,
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        required_permissions = [perm % kwargs for perm in self.perms_map[method]]

        required_permissions.extend(self.other_permissions)

        return required_permissions

    def has_permission(self, request, view):
        if (not request.user and request.user.is_active) or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return request.user.has_perms(perms)


def get_custom_model_permissions(other_permissions):
    """
    Returns a custom permission class that extends DjangoModelPermissions
    and includes additional permissions.

    Usage:
    1. Import this function:
       from utils.permissions import custom_model_permissions

    2. Incorporate the returned permission class into your view or viewset:
       Example 1: Using custom permissions alone
       permission_classes = [custom_model_permissions(["users.view_user", "users.add_user"])]

       Example 2: Combining with other permissions
       permission_classes = [IsAuthenticated, custom_model_permissions(["users.view_user", "users.add_user"])]

    Parameters:
    - other_permissions (list): List of additional permission codes to include.

    Returns:
    - CustomDjangoModelPermissionsWrapper class: A subclass of DjangoModelPermissions
      with extended permissions as specified.
    """

    class CustomDjangoModelPermissionsWrapper(CustomDjangoModelPermissions):
        def __init__(self):
            super(CustomDjangoModelPermissionsWrapper, self).__init__(other_permissions)

    return CustomDjangoModelPermissionsWrapper
