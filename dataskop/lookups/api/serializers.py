import base64

from rest_framework import serializers

from dataskop.lookups.models import Lookup, LookupJob


class BinaryField(serializers.Field):
    def to_representation(self, value):
        return base64.b64encode(value).decode("ascii")

    def to_internal_value(self, data):
        return base64.b64decode(data.encode("ascii"))


class LookupSerializer(serializers.ModelSerializer):
    data = BinaryField

    class Meta:
        model = Lookup
        fields = ["id", "data"]


class LookupJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookupJob
        fields = ["id", "input_todo", "input_done"]
