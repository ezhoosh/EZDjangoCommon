from django.utils.html import format_html
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def image_preview(instance, field_name: str, width=110, height=110):
    """
    Global utility function to display an image preview in the Django admin panel.

    :param instance: The instance of the model containing the image field.
    :param field_name: The name of the image field (e.g., 'media', 'thumbnail').
    :param width: The width of the image preview (default: 100).
    :param height: The height of the image preview (default: 100).
    :return: HTML formatted string for image preview or a message if no image is available.
    """
    image_field = getattr(instance, field_name, None)
    if image_field and hasattr(image_field, "url"):
        return format_html(
            f'<img src="{image_field.url}" width="{width}" height="{height}" />'
        )
    return "No Image"
