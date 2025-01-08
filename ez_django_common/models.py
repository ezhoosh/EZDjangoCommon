from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Manager
from django_lifecycle import LifecycleModelMixin


class ActiveManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def delete(self):
        return super().get_queryset().update(is_active=False, deleted_at=timezone.now())

    def hard_delete(self):
        return super().get_queryset().delete()

    def restore(self):
        return super().get_queryset().update(is_active=True, deleted_at=None)


class BaseModel(LifecycleModelMixin, models.Model):
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated At"), auto_now=True)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    deleted_at = models.DateTimeField(
        verbose_name=_("Deleted At"), null=True, blank=True
    )
    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
