try:
    from opentelemetry import trace
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None


if OPENTELEMETRY_AVAILABLE:
    tracer = trace.get_tracer(__name__)
else:
    tracer = None


class OpenTelemetryMiddleware:
    """
    Middleware to automatically trace all incoming HTTP requests and responses.
    Requires OpenTelemetry to be installed (pip install ez-django-common[watchlog]).
    """

    def __init__(self, get_response):
        if not OPENTELEMETRY_AVAILABLE:
            raise ImportError(
                "OpenTelemetry is not installed. "
                "Please install it with: pip install ez-django-common[watchlog]"
            )
        self.get_response = get_response

    def __call__(self, request):
        with tracer.start_as_current_span(f"{request.method} {request.path}") as span:
            # --- Request tracing ---
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", request.build_absolute_uri())
            span.set_attribute("http.query_params", str(request.GET.dict()))

            try:
                body = request.body.decode("utf-8") if request.body else ""
            except Exception:
                body = "<cannot decode body>"
            span.set_attribute("http.body", body)

            headers = {k: v for k, v in request.headers.items()}
            span.set_attribute("http.headers", str(headers))
            span.set_attribute("user.id", str(getattr(request.user, "id", "anonymous")))

            # --- Call the next middleware / view ---
            response = self.get_response(request)

            # --- Response tracing ---
            span.set_attribute(
                "http.status_code", getattr(response, "status_code", "unknown")
            )
            if hasattr(response, "content"):
                try:
                    response_body = response.content.decode("utf-8")
                except Exception:
                    response_body = "<cannot decode response body>"
                span.set_attribute("http.response.body", response_body)

            if hasattr(response, "headers"):
                span.set_attribute("http.response.headers", str(dict(response.headers)))

            return response
