from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


def enveloper(serializer_class, many):
    component_name = "Enveloped{}{}".format(
        serializer_class.__name__.replace("Serializer", ""),
        "List" if many else "",
    )

    @extend_schema_serializer(many=False, component_name=component_name)
    class EnvelopeSerializer(serializers.Serializer):
        data = serializer_class(many=many)  # the enveloping part
        error = serializers.CharField(
            allow_blank=True, required=False
        )  # some arbitrary envelope field
        message = serializers.CharField(
            allow_blank=True, required=False
        )  # some arbitrary envelope field

    return EnvelopeSerializer


def enveloper_pagination(serializer_class, many, action="create", object_name="Object"):
    component_name = "Enveloped{}{}".format(
        serializer_class.__name__.replace("Serializer", ""),
        "List" if many else "",
    )

    class LinksSerializer(serializers.Serializer):
        next = serializers.URLField()
        previous = serializers.URLField()

    class PaginationSerializer(serializers.Serializer):
        total = serializers.IntegerField()
        limit = serializers.IntegerField()
        offset = serializers.IntegerField()
        links = LinksSerializer()

    @extend_schema_serializer(many=False, component_name=component_name)
    class EnvelopeSerializer(serializers.Serializer):
        data = serializer_class(many=many)  # the enveloping part
        error = serializers.CharField(
            allow_blank=True, required=False
        )  # some arbitrary envelope field
        message = serializers.CharField(
            allow_blank=True,
            required=False,
            default=f"{object_name + 's' if action == 'list' else object_name} {action} successfully",
        )  # some arbitrary envelope field
        pagination = PaginationSerializer(allow_null=True, required=False)

    return EnvelopeSerializer
