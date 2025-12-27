from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class EzDjangoCommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ez_django_common"
    verbose_name = _("Ez Django Common")

    def ready(self):
        # Check if USE_WATCHLOG is enabled (default to False if not set)
        use_watchlog = getattr(settings, 'USE_WATCHLOG', False)
        
        if use_watchlog:
            try:
                from ez_django_common.watchlog import (
                    trace,
                    Resource,
                    TracerProvider,
                    WatchlogJSONExporter,
                    SimpleSpanProcessor,
                    OPENTELEMETRY_AVAILABLE,
                )
            except ImportError:
                raise ImportError(
                    "USE_WATCHLOG is enabled but OpenTelemetry is not installed. "
                    "Please install it with: pip install ez-django-common[watchlog]"
                )
            
            if not OPENTELEMETRY_AVAILABLE:
                raise ImportError(
                    "USE_WATCHLOG is enabled but OpenTelemetry is not installed. "
                    "Please install it with: pip install ez-django-common[watchlog]"
                )
            # Configure OpenTelemetry
            resource = Resource.create(
                {
                    "service.name": settings.WATCHLOG_SERVICE_NAME,
                }
            )

            trace.set_tracer_provider(TracerProvider(resource=resource))

            # Get OTLP endpoint from environment variable
            # Watchlog uses custom endpoint format: http://watchlog-agent:3774/apm/YOUR_APP_NAME/v1/traces
            otlp_endpoint_full = settings.WATCHLOG_SERVICE_ENDPOINT

            # Use custom JSON exporter for Watchlog
            watchlog_exporter = WatchlogJSONExporter(endpoint=otlp_endpoint_full, resource=resource)

            # Use SimpleSpanProcessor for immediate export (better for testing)
            # In production, you might want to use BatchSpanProcessor for better performance
            span_processor = SimpleSpanProcessor(watchlog_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            # Django instrumentation - must be imported after setting up the tracer provider
            try:
                from opentelemetry.instrumentation.django import DjangoInstrumentor
            except ImportError:
                raise ImportError(
                    "USE_WATCHLOG is enabled but OpenTelemetry Django instrumentation is not installed. "
                    "Please install it with: pip install ez-django-common[watchlog]"
                )

            DjangoInstrumentor().instrument()
