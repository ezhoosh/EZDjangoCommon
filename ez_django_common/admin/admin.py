import copy
from typing import Any, Dict, List, Optional

from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from media_uploader_widget.widgets import MediaUploaderWidget
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin, UnfoldAction, UnfoldBooleanSwitchWidget


class BaseModelAdmin(ModelAdmin):
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
    # Display submit button in filters
    list_filter_submit = True

    def get_actions_detail(
        self, request: HttpRequest, object_id: int = None
    ) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_detail()
        )

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
        new_formfield_overrides.update(
            {models.BooleanField: {"widget": UnfoldBooleanSwitchWidget}}
        )

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
