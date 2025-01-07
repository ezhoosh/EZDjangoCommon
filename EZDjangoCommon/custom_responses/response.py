from rest_framework.response import Response
from rest_framework import status as rest_status


class CustomResponse(Response):
    def __init__(
        self,
        data=None,
        message="",
        error=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        pagination=None,
    ):
        formatted_data = {"data": data, "message": message, "error": error}
        h_status = status
        if status is None:
            h_status = rest_status.HTTP_200_OK

        if not error:
            del formatted_data["error"]

        if pagination:
            formatted_data["pagination"] = pagination
        super().__init__(
            data=formatted_data,
            status=h_status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )
