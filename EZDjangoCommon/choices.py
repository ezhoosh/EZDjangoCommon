from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class UserTypes(IntegerChoices):
    ADMIN = 1, _("Admin")
    NORMAL = 2, _("Normal")
