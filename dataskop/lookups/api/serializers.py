from rest_framework import serializers

from dataskop.lookups.models import Lookup


class LookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lookup
        fields = ["id", "data"]
