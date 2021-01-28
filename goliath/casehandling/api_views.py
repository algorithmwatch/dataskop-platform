from django_filters import rest_framework as filters
from rest_framework import serializers, viewsets

from .models import ExternalSupport


class TagSerializerField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        return data.values_list("name", flat=True)


class ExternalSupportSerializer(serializers.ModelSerializer):
    name_highlighted = serializers.CharField(allow_null=True, required=False)
    description_highlighted = serializers.CharField(allow_null=True, required=False)
    tags = TagSerializerField()

    class Meta:
        model = ExternalSupport
        exclude = ["search_vector"]

    def __init__(self, *args, **kwargs):
        # when searching, only return highlighted results
        request = kwargs.get("context", {}).get("request")
        is_searching = request.GET.get("q", None) if request else None

        super(ExternalSupportSerializer, self).__init__(*args, **kwargs)

        if is_searching:
            self.fields.pop("name")
            self.fields.pop("description")
        else:
            self.fields.pop("name_highlighted")
            self.fields.pop("description_highlighted")


class ExternalSupportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalSupport.objects
    serializer_class = ExternalSupportSerializer
    pagination_class = None

    def filter_queryset(self, queryset):
        # couldn't really make use of django-filter here, FIXME?
        queryset = super().filter_queryset(queryset)
        q = self.request.GET.get("q")
        if q is not None:
            queryset = queryset.search(q)

        tag_list = self.request.GET.getlist("tag")
        if len(tag_list) != 0:
            queryset = queryset.filter(tags__name__in=tag_list).distinct()

        return queryset
