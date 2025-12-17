import copy
from typing import Any, Dict, List, Optional
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
import jdatetime
from unfold.decorators import display
from django.utils.translation import gettext_lazy as _
from media_uploader_widget.widgets import MediaUploaderWidget
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminTextareaWidget,
)
from django_jalali.admin.widgets import AdminSplitjDateTime, AdminjDateWidget


class BaseModelAdmin(ModelAdmin):
    """
    Base admin class for common Django admin customizations.
    """

    formfield_overrides = {
        models.DateTimeField: {"widget": AdminSplitjDateTime},
        models.DateField: {"widget": AdminjDateWidget},
        models.CharField: {"widget": UnfoldAdminTextInputWidget},
        models.TextField: {"widget": UnfoldAdminTextareaWidget},
        models.FileField: {"widget": MediaUploaderWidget},
        models.ImageField: {"widget": MediaUploaderWidget},
    }

    def _format_jalali(self, dt):
        """Helper to format datetime into Jalali string."""
        if dt:
            return jdatetime.fromgregorian(datetime=dt).strftime("%Y/%m/%d %H:%M:%S")
        return "-"

    @display(description=_("Created At"))
    def created_at_jalali(self, obj):
        """Display created_at in Jalali datetime format."""
        return self._format_jalali(getattr(obj, "created_at", None))

    @display(description=_("Updated At"))
    def updated_at_jalali(self, obj):
        """Display updated_at in Jalali datetime format."""
        return self._format_jalali(getattr(obj, "updated_at", None))

    list_per_page = 30
    compressed_fields = True
    list_filter_submit = True

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
