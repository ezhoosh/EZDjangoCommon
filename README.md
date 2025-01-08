# EZDjangoCommon

# Installation

run this command to install the package:

``` bash
pip install git+https://github.com/ezhoosh/EZDjangoCommon.git
```

or if the repo is private:

``` bash
pip install git+ssh://git@github.com/ezhoosh/EZDjangoCommon.git
```

add these packages to INSTALLED_APPS:

``` python
INSTALLED_APPS = [
    'ez_django_common',
    'image_uploader_widget',
    'tinymce',
    ...
]
```

# Usage

## Unfold
To use unfold for panel admin, first add unfold to INSTALLED_APPS:

``` python
INSTALLED_APPS = [
    'unfold', # before django.admin.contrib
    ...
]
```

then use BaseModelAdmin instead of admin.ModelAdmin in admin classes:

``` python
from ez_django_common.admin import BaseModelAdmin

@admin.register(ModelName)
class ModelNameAdmin(BaseModelAdmin):
    ...
```

## Custom Responses
To use custom responses, you can do this:

``` python
from ez_django_common.custom_responses.enveloper import enveloper

@extend_schema(
    responses=enveloper(SampleRetrieveSerializer, many=False),
)
def retrieve(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)
```

or if your response is a list of objects:

``` python
from ez_django_common.custom_responses.enveloper import enveloper_pagination

@extend_schema(
    ...
    responses=enveloper_pagination(SampleRetrieveSerializer, many=True),
)
def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)
```

And this is the custom exception handler function:

``` python
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.translation import gettext_lazy as _


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ValidationError):
            response.data = {
                "error": _("please provide correct data."),
                "fields": response.data,
            }
        elif isinstance(exc, InvalidToken):
            response.data = {
                "error": _("please login again"),
            }
        else:
            response.data = {"error": str(exc)}
        response.data["status_code"] = response.status_code

    return response
```

And to use it, you can do this:

``` python
REST_FRAMEWORK = {
    ...
    "EXCEPTION_HANDLER": "ez_django_common.custom_responses.exception.custom_exception_handler",
    ...
}
```
