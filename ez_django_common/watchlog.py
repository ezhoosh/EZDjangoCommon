import json
import http.client
from typing import Sequence
import urllib.parse

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        SimpleSpanProcessor,
        SpanExporter,
        SpanExportResult,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import StatusCode
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Create dummy classes/objects to avoid NameError
    trace = None
    TracerProvider = None
    SimpleSpanProcessor = None
    SpanExporter = object
    SpanExportResult = None
    Resource = None
    StatusCode = None


class WatchlogJSONExporter(SpanExporter):
    def __init__(self, endpoint: str, resource: Resource = None):
        self.endpoint = endpoint
        self.resource = resource
        parsed = urllib.parse.urlparse(endpoint)
        self.host = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.path = parsed.path
        self.scheme = parsed.scheme
        self.use_ssl = parsed.scheme == "https"

    def export(self, spans: Sequence) -> SpanExportResult:
        if not spans:
            return SpanExportResult.SUCCESS

        try:
            # Convert spans to JSON format
            json_data = self._spans_to_json(spans)
            json_str = json.dumps(json_data)

            conn = (
                http.client.HTTPConnection(self.host, self.port)
                if not self.use_ssl
                else http.client.HTTPSConnection(self.host, self.port)
            )

            headers = {
                "Content-Type": "application/json",
            }

            conn.request("POST", self.path, json_str, headers)
            response = conn.getresponse()
            conn.close()

            if response.status == 200:
                return SpanExportResult.SUCCESS
            else:
                return SpanExportResult.FAILURE
        except Exception as e:
            import logging

            print(f"❌ Error exporting spans to watchlog: {e}")
            logging.getLogger(__name__).error(f"Error exporting spans to watchlog: {e}")
            return SpanExportResult.FAILURE

    def _spans_to_json(self, spans):
        """Convert OpenTelemetry spans to JSON format (OTLP JSON format)"""
        span_list = []

        for span in spans:
            span_data = {
                "traceId": format(span.context.trace_id, "032x"),
                "spanId": format(span.context.span_id, "016x"),
                "name": span.name,
                "kind": "SPAN_KIND_INTERNAL",
                "startTimeUnixNano": str(span.start_time),
                "endTimeUnixNano": (
                    str(span.end_time) if span.end_time else str(span.start_time)
                ),
                "attributes": (
                    self._attributes_to_array(span.attributes)
                    if span.attributes
                    else []
                ),
            }

            # Add parent span ID if exists
            if span.parent and span.parent.span_id:
                span_data["parentSpanId"] = format(span.parent.span_id, "016x")

            # Add status if exists
            if span.status:
                span_data["status"] = {
                    "code": (
                        "STATUS_CODE_ERROR"
                        if span.status.status_code == StatusCode.ERROR
                        else "STATUS_CODE_OK"
                    )
                }
                if span.status.description:
                    span_data["status"]["message"] = span.status.description

            # Add events if exists
            if span.events:
                span_data["events"] = [
                    {
                        "timeUnixNano": str(event.timestamp),
                        "name": event.name,
                        "attributes": (
                            self._attributes_to_array(event.attributes)
                            if event.attributes
                            else []
                        ),
                    }
                    for event in span.events
                ]

            span_list.append(span_data)


        # OTLP JSON format
        # Convert resource attributes to array format
        resource_attrs = []
        if (
            self.resource
            and hasattr(self.resource, "attributes")
            and self.resource.attributes
        ):
            resource_attrs = self._attributes_to_array(self.resource.attributes)

        return {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource_attrs},
                    "scopeSpans": [{"spans": span_list}],
                }
            ]
        }

    def _attributes_to_array(self, attributes):
        """Convert OpenTelemetry attributes to OTLP JSON format array of {key, value}"""
        result = []
        for key, value in attributes.items():
            # OTLP JSON format: {key: string, value: {stringValue, intValue, doubleValue, boolValue, ...}}
            attr_obj = {"key": key}

            if isinstance(value, str):
                attr_obj["value"] = {"stringValue": value}
            elif isinstance(value, bool):
                attr_obj["value"] = {"boolValue": value}
            elif isinstance(value, int):
                attr_obj["value"] = {"intValue": str(value)}
            elif isinstance(value, float):
                attr_obj["value"] = {"doubleValue": value}
            elif isinstance(value, bytes):
                attr_obj["value"] = {"bytesValue": value.hex()}
            else:
                # Default to string
                attr_obj["value"] = {"stringValue": str(value)}

            result.append(attr_obj)
        return result

    def shutdown(self):
        pass
