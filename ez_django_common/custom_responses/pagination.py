from django.utils.translation import gettext as _
from rest_framework import pagination
from .response import CustomResponse


class CustomPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return CustomResponse(
            data=data,
            pagination={
                "limit": self.limit,
                "offset": self.offset,
                "total": self.count,
                "services": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
            },
            message=_("List retrieved successfully"),
        )
