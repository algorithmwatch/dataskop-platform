from django_filters import rest_framework as filters
from rest_framework import serializers, viewsets

from .models import CaseType, ExternalSupport


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
    queryset = ExternalSupport.search
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


case_type_search_fields = ["title", "claim", "short_description", "description"]
case_type_search_fields_high = [f"{x}_highlighted" for x in case_type_search_fields]


class CaseTypeSerializer(serializers.ModelSerializer):
    title_highlighted = serializers.CharField(allow_null=True, required=False)
    claim_highlighted = serializers.CharField(allow_null=True, required=False)
    short_description_highlighted = serializers.CharField(
        allow_null=True, required=False
    )
    description_highlighted = serializers.CharField(allow_null=True, required=False)
    tags = TagSerializerField()
    url = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = CaseType
        fields = (
            case_type_search_fields
            + case_type_search_fields_high
            + ["tags", "icon_name", "url"]
        )

    def __init__(self, *args, **kwargs):
        # when searching, only return highlighted results
        request = kwargs.get("context", {}).get("request")
        is_searching = request.GET.get("q", None) if request else None

        super(CaseTypeSerializer, self).__init__(*args, **kwargs)

        if is_searching:
            for x in case_type_search_fields:
                self.fields.pop(x)
        else:
            for x in case_type_search_fields_high:
                self.fields.pop(x)


class CaseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CaseType.search
    serializer_class = CaseTypeSerializer
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
