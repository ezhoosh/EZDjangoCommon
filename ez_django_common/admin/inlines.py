from django.db import models
from image_uploader_widget.widgets import ImageUploaderWidget
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.contrib.inlines.admin import (
    NonrelatedStackedInline,
    NonrelatedTabularInline,
    StackedInline,
    TabularInline,
)


class TabularInline(TabularInline):
    """
    Custom inline class for Django admin interface that organizes inline models
    into separate tabs based on specified class names.

    This class extends `admin.TabularInline` and adds functionality to dynamically
    assign inlines to specific tabs in the admin interface based on their class names.

    Usage:
        1. Define inline classes inheriting from `TabInline`.
        2. Specify these inline classes in the `inlines` attribute of your `ModelAdmin`.
        3. Use the `fieldsets` attribute to organize fields into tabs, using the `classes`
           attribute to specify which inline classes should appear in each tab.
    Example:
        class CategoryInline(TabInline):
            ...
        class MyModelAdmin(ModelAdmin):
            ...
            fieldsets = (
                ...,
                (
                    "Category Section",
                    {
                        "classes": ["tab", "CategoryInline" ],
                        "fields": [],
                    },
                ),
    """

    # @property
    # def class_name(self):
    #     return self.__class__.__name__

    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super().get_formset(request, obj, **kwargs)
    #     formset.class_name = self.class_name
    #     return formset

    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        models.ImageField: {"widget": ImageUploaderWidget},
        models.FileField: {"widget": ImageUploaderWidget},
    }


class StackedInline(StackedInline):
    """
    Custom inline class for Django admin interface that organizes inline models
    into separate tabs based on specified class names.

    This class extends `admin.StackedInline` and adds functionality to dynamically
    assign inlines to specific tabs in the admin interface based on their class names.

    Usage:
        1. Define inline classes inheriting from `TabInline`.
        2. Specify these inline classes in the `inlines` attribute of your `ModelAdmin`.
        3. Use the `fieldsets` attribute to organize fields into tabs, using the `classes`
           attribute to specify which inline classes should appear in each tab.
    Example:
        class CategoryInline(TabInline):
            ...
        class MyModelAdmin(ModelAdmin):
            ...
            fieldsets = (
                ...,
                (
                    "Category Section",
                    {
                        "classes": ["tab", "CategoryInline" ],
                        "fields": [],
                    },
                ),
    """

    @property
    def class_name(self):
        return self.__class__.__name__

    def get_formset(self, request, obj: None = ..., **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.class_name = self.class_name
        return formset

    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        models.ImageField: {"widget": ImageUploaderWidget},
        models.FileField: {"widget": ImageUploaderWidget},
    }


class NonrelatedStackedInline(NonrelatedStackedInline):
    """
    Custom inline class for Django admin interface that organizes inline models
    into separate tabs based on specified class names.

    This class extends `admin.StackedInline` and adds functionality to dynamically
    assign inlines to specific tabs in the admin interface based on their class names.

    Usage:
        1. Define inline classes inheriting from `TabInline`.
        2. Specify these inline classes in the `inlines` attribute of your `ModelAdmin`.
        3. Use the `fieldsets` attribute to organize fields into tabs, using the `classes`
           attribute to specify which inline classes should appear in each tab.
    Example:
        class CategoryInline(TabInline):
            ...
        class MyModelAdmin(ModelAdmin):
            ...
            fieldsets = (
                ...,
                (
                    "Category Section",
                    {
                        "classes": ["tab", "CategoryInline" ],
                        "fields": [],
                    },
                ),
    """

    @property
    def class_name(self):
        return self.__class__.__name__

    def get_form_queryset(self, obj):
        """
        Gets all nonrelated objects needed for inlines. Method must be implemented.
        """
        return self.model.objects.all()

    def save_new_instance(self, parent, instance):
        """
        Extra save method which can for example update inline instances based on current
        main model object. Method must be implemented.
        """
        pass

    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        models.ImageField: {"widget": ImageUploaderWidget},
        models.FileField: {"widget": ImageUploaderWidget},
    }


class NonrelatedTabularInline(NonrelatedTabularInline):
    """
    Custom inline class for Django admin interface that organizes inline models
    into separate tabs based on specified class names.

    This class extends `admin.TabularInline` and adds functionality to dynamically
    assign inlines to specific tabs in the admin interface based on their class names.

    Usage:
        1. Define inline classes inheriting from `TabInline`.
        2. Specify these inline classes in the `inlines` attribute of your `ModelAdmin`.
        3. Use the `fieldsets` attribute to organize fields into tabs, using the `classes`
           attribute to specify which inline classes should appear in each tab.
    Example:
        class CategoryInline(TabInline):
            ...
        class MyModelAdmin(ModelAdmin):
            ...
            fieldsets = (
                ...,
                (
                    "Category Section",
                    {
                        "classes": ["tab", "CategoryInline" ],
                        "fields": [],
                    },
                ),
    """

    @property
    def class_name(self):
        return self.__class__.__name__

    def get_form_queryset(self, obj):
        """
        Gets all nonrelated objects needed for inlines. Method must be implemented.
        """
        return self.model.objects.all()

    def save_new_instance(self, parent, instance):
        """
        Extra save method which can for example update inline instances based on current
        main model object. Method must be implemented.
        """
        pass

    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
        models.ImageField: {"widget": ImageUploaderWidget},
        models.FileField: {"widget": ImageUploaderWidget},
    }
