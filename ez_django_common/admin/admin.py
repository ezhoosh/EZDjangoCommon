import copy
from typing import Any, Dict, List, Optional
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from media_uploader_widget.widgets import MediaUploaderWidget
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin


class BaseModelAdmin(ModelAdmin):
    """
    Base admin class with automatic boolean field translation.
    Simply include boolean fields in list_display - translation is handled automatically.
    """
    
    formfield_overrides = {
        models.TextField: {
            "widget": TinyMCE(),
        },
        models.FileField: {
            "widget": MediaUploaderWidget,
        },
        models.ImageField: {
            "widget": MediaUploaderWidget,
        },
    }
    
    list_per_page = 30
    compressed_fields = True
    list_filter_submit = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_boolean_translation()
    
    def _setup_boolean_translation(self):
        """Automatically create translatable display methods for boolean fields."""
        if not hasattr(self, 'model') or not self.model or not hasattr(self, 'list_display'):
            return
            
        if not self.list_display:
            return
            
        # Get boolean fields from model
        boolean_fields = {
            field.name: field for field in self.model._meta.fields 
            if isinstance(field, models.BooleanField)
        }
        
        if not boolean_fields:
            return
            
        # Process list_display
        list_display = list(self.list_display)
        
        for i, field_name in enumerate(list_display):
            if field_name in boolean_fields:
                method_name = f"__{field_name}_translated"
                
                # Create the display method
                self._create_boolean_method(field_name, method_name, boolean_fields[field_name])
                
                # Replace in list_display
                list_display[i] = method_name
        
        self.list_display = tuple(list_display)
    
    def _create_boolean_method(self, field_name: str, method_name: str, field_obj):
        """Create a boolean display method that returns translatable strings."""
        def display_method(admin_self, obj):
            value = getattr(obj, field_name)
            return _('True') if value else _('False')
        
        # Set admin display properties
        display_method.boolean = True
        display_method.short_description = field_obj.verbose_name
        display_method.__name__ = method_name
        
        # Bind method to this instance
        setattr(self, method_name, display_method.__get__(self, self.__class__))
    
    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[Dict[str, bool]] = None,
    ) -> Any:
        if extra_context is None:
            extra_context = {}
            
        new_formfield_overrides = copy.deepcopy(self.formfield_overrides)
        self.formfield_overrides = new_formfield_overrides
        
        actions = []
        if object_id:
            for action in self.get_actions_detail(request, object_id):
                actions.append(
                    {
                        "title": action.description,
                        "attrs": action.method.attrs,
                        "path": reverse(
                            f"admin:{action.action_name}", args=(object_id,)
                        ),
                    }
                )
        
        extra_context.update(
            {
                "actions_submit_line": self.get_actions_submit_line(request, object_id),
                "actions_detail": actions,
            }
        )
        
        return super(ModelAdmin, self).changeform_view(
            request, object_id, form_url, extra_context
        )