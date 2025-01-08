from rest_framework.viewsets import GenericViewSet

from .mixins import (
    CustomListModelMixin,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    CustomRetrieveModelMixin,
)


class CustomReadOnlyModelViewSet(
    CustomRetrieveModelMixin, CustomListModelMixin, GenericViewSet
):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """

    pass


class CustomModelViewSet(
    CustomCreateModelMixin,
    CustomRetrieveModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    CustomListModelMixin,
    GenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    pass
