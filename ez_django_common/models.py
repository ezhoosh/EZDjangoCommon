from django.conf import settings
from logging import getLogger
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin
from googletrans import Translator
from modeltranslation.translator import translator

logger = getLogger(__name__)


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

    def save(self, *args, **kwargs):
        """
        Override save to automatically translate missing language fields.
        """
        # Only auto-translate if all requirements are available
        if getattr(settings, "AUTO_TRANSLATE_ENABLED", False):
            self._auto_translate_fields()

        super().save(*args, **kwargs)

    def _auto_translate_fields(self):
        """
        Automatically translate fields that are missing in target languages.
        """
        # Check if this model has translatable fields
        trans_opts = translator.get_options_for_model(self.__class__)
        if not trans_opts:
            return

        # Get all translatable fields
        translatable_fields = trans_opts.fields

        # Get supported languages from settings
        supported_languages = dict(settings.LANGUAGES)
        target_languages = [
            lang_code
            for lang_code, _ in supported_languages.items()
            if lang_code != settings.LANGUAGE_CODE  # Skip default language
        ]

        # Initialize translator
        if not hasattr(self, "_translator_instance"):
            self._translator_instance = Translator()

        for field_name in translatable_fields:
            # Get the source field value (base language field)
            source_value = getattr(self, field_name, None)

            # Skip if no source value
            if not source_value or not str(source_value).strip():
                continue

            # Translate to each target language if missing
            for lang_code in target_languages:
                target_field = f"{field_name}_{lang_code}"

                # Check if target field exists
                if not hasattr(self, target_field):
                    continue

                # Get current value of target field
                target_value = getattr(self, target_field, None)

                # Only translate if target field is empty
                if target_value and str(target_value).strip():
                    continue

                # Perform translation
                try:
                    translated_text = self._translate_text(str(source_value), lang_code)
                    if translated_text and translated_text != str(source_value):
                        setattr(self, target_field, translated_text)
                except Exception as e:
                    # Log error but don't fail the save operation
                    logger.warning(
                        f"Auto-translation error for {self.__class__.__name__}.{target_field}: {str(e)}"
                    )

    def _translate_text(self, text: str, target_lang: str) -> str:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_lang: Target language code

        Returns:
            Translated text
        """
        if not text or not isinstance(text, str):
            return text

        text = text.strip()
        if len(text) == 0:
            return text

        try:
            result = self._translator_instance.translate(text, dest=target_lang)
            return result.text
        except Exception:
            # Return original text if translation fails
            return text
