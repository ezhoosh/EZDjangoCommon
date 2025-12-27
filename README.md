# EZDjangoCommon

`ez_django_common` is a Django package designed to simplify and standardize common tasks in Django projects. It provides a set of utilities, custom responses, admin enhancements, and other reusable components that can be easily integrated into any Django project. This package aims to reduce boilerplate code and improve consistency across your Django applications.

## Features

- **Custom Admin Enhancements**: Enhanced Django admin interface with custom widgets, inline models, and improved form handling.
- **Custom Responses**: Standardized API responses with support for pagination, error handling, and success messages.
- **JWT Utilities**: Custom JWT token views for authentication.
- **Model Mixins**: Reusable mixins for common CRUD operations in Django viewsets.
- **Permissions**: Customizable Django model permissions with support for additional permissions.
- **Utilities**: Helper functions for logging, SMS, and file uploads.

## Installation

You can install `ez_django_common` via pip:

``` bash
pip install ez-django-common
```

Or if you want to install from source, you can run this command to install the package:

``` bash
pip install git+https://github.com/ezhoosh/EZDjangoCommon.git
```

### Optional Features

**Watchlog (OpenTelemetry Integration)**

If you want to use the watchlog feature for distributed tracing with OpenTelemetry, install with the `watchlog` extra:

``` bash
pip install ez-django-common[watchlog]
```

Or from source:

``` bash
pip install "ez-django-common[watchlog] @ git+https://github.com/ezhoosh/EZDjangoCommon.git"
```

This will install the required OpenTelemetry packages:
- `opentelemetry-api`
- `opentelemetry-sdk`
- `opentelemetry-exporter-otlp`
- `opentelemetry-instrumentation`
- `opentelemetry-instrumentation-django`

Then add these packages to INSTALLED_APPS:

``` python
INSTALLED_APPS = [
    'ez_django_common',
    'image_uploader_widget',
    'tinymce',
    ...
]
```

## Usage

### Custom Admin Enhancements

#### BaseModelAdmin

The `BaseModelAdmin` class provides a set of default configurations for Django admin models, including custom widgets for text and file fields.

```python
from ez_django_common.admin import BaseModelAdmin
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(BaseModelAdmin):
    list_display = ('name', 'created_at')
```

### Custom Inlines

The package provides custom inline classes (TabularInline, StackedInline, NonrelatedTabularInline, NonrelatedStackedInline) that can be used to organize inline models in the admin interface.

``` python
from ez_django_common.admin import TabularInline
from django.contrib import admin
from .models import MyModel, RelatedModel

class RelatedModelInline(TabularInline):
    model = RelatedModel

@admin.register(MyModel)
class MyModelAdmin(BaseModelAdmin):
    inlines = [RelatedModelInline]
```

### Unfold
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

### Custom Responses
The enveloper function wraps your serializers in a standardized response format, including fields for data, error, and message.

``` python
from ez_django_common.custom_responses.enveloper import enveloper

@extend_schema(
    responses=enveloper(SampleRetrieveSerializer, many=False),
)
def retrieve(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)
```

Or if your response is a list of objects:

``` python
from ez_django_common.custom_responses.enveloper import enveloper_pagination

@extend_schema(
    ...
    responses=enveloper_pagination(SampleRetrieveSerializer, many=True),
)
def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)
```


### Custom Exception Handler

The custom_exception_handler provides a standardized way to handle exceptions in your Django REST Framework views.

``` python
REST_FRAMEWORK = {
    ...
    "EXCEPTION_HANDLER": "ez_django_common.custom_responses.exception.custom_exception_handler",
    ...
}
```

### JWT Utilities
* CustomTokenViewBase

The CustomTokenViewBase class provides a base for custom JWT token views, including token refresh and verification.

``` python
from ez_django_common.custom_responses.jwt import CustomTokenRefreshView, CustomTokenVerifyView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
]
```

### Model Mixins

The package includes several mixins for common CRUD operations in Django viewsets.

``` python
from ez_django_common.custom_responses.viewsets import CustomModelViewSet
from .models import MyModel
from .serializers import MySerializer

class MyModelViewSet(CustomModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

### Permissions
* CustomDjangoModelPermissions

The CustomDjangoModelPermissions class extends Django's default model permissions, allowing you to add additional permissions.

``` python
from ez_django_common.permissions import get_custom_model_permissions
from rest_framework.permissions import IsAuthenticated

permission_classes = [IsAuthenticated, get_custom_model_permissions(['myapp.view_mymodel'])]
```

### Auto-Translation (Optional)

The `BaseModel` includes automatic translation functionality for Django models with `django-modeltranslation`. To enable this feature:

1. Install the required dependencies:
```bash
pip install googletrans==4.0.0rc1 django-modeltranslation
```

2. Add to your Django settings:
```python
# Enable auto-translation
AUTO_TRANSLATE_ENABLED = True

# Configure languages (required for translation)
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Persian'),
    ('ar', 'Arabic'),
]
LANGUAGE_CODE = 'en'  # Default language
```

3. Use the BaseModel in your models:
```python
from ez_django_common.models import BaseModel

class MyModel(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()

# When you save an instance, missing translations will be automatically generated
```

**Note**: Auto-translation only works if:
- `AUTO_TRANSLATE_ENABLED = True` in settings
- `django-modeltranslation` is installed and configured
- `googletrans` library is available
- Your model is registered with `modeltranslation`

### Watchlog (OpenTelemetry Integration)

The watchlog feature provides distributed tracing capabilities using OpenTelemetry. To use this feature:

1. Install with the watchlog extra:
```bash
pip install ez-django-common[watchlog]
```

2. Add to your Django settings:
```python
# Enable watchlog
USE_WATCHLOG = True

# Configure Watchlog service
WATCHLOG_SERVICE_NAME = 'my-django-service'
WATCHLOG_SERVICE_ENDPOINT = 'http://watchlog-agent:3774/apm/YOUR_APP_NAME/v1/traces'
```

3. The package will automatically instrument your Django application with OpenTelemetry when `USE_WATCHLOG = True`.

4. (Optional) To add request/response tracing middleware, add it to your Django settings:
```python
MIDDLEWARE = [
    # ... other middleware
    'ez_django_common.middleware.OpenTelemetryMiddleware',  # Only if watchlog extra is installed
    # ... other middleware
]
```

**Important**: 
- The OpenTelemetry dependencies are only installed when you use the `[watchlog]` extra.
- If you don't need distributed tracing, you can install the base package without these dependencies.
- If you set `USE_WATCHLOG = True` or try to use `OpenTelemetryMiddleware` without installing the watchlog extra, you will get a helpful error message telling you to install it.

### Utilities
* Upload_to

The upload_to function provides a standardized way to handle file uploads in Django models.

``` python
from ez_django_common.storages import upload_to
from django.db import models

def upload_to_path(instance, filename):
    return upload_to(instance, filename, folder="path")

class MyModel(models.Model):
    file = models.FileField(upload_to=upload_to_path)
```
