from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework import viewsets

from .models import ExternalSupport


class ExternalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSupport
        fields = "__all__"


class ExternalFilter(filters.FilterSet):
    q = filters.CharFilter(method="search_fulltext")

    def search_fulltext(self, queryset, field_name, value):
        return queryset
        # return queryset.search(value)

    class Meta:
        model = ExternalSupport
        fields = ["q"]


class ExternalSupportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalSupport.objects
    serializer_class = ExternalSerializer
    filterset_class = ExternalFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        tag_list = self.request.GET.getlist("tag")
        if len(tag_list) != 0:
            queryset = queryset.filter(tags__name__in=tag_list).distinct()

        return queryset
        # TODO: order by rank?
        # return queryset.order_by("-date")
