from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db import models
from django.db.models import F


class SearchExpertnalSupportQuerySet(models.QuerySet):
    def search(self, search_text, highlight=True):
        if search_text is None:
            return self

        search_query = SearchQuery(
            search_text, config="german", search_type="websearch"
        )

        qs = self.filter(search_vector=search_query)
        qs = qs.annotate(rank=SearchRank(F("search_vector"), search_query)).order_by(
            "-rank"
        )

        if highlight:
            qs = qs.annotate(
                name_highlighted=SearchHeadline(
                    "name", search_query, config="german", highlight_all=True
                ),
                description_highlighted=SearchHeadline(
                    "description", search_query, config="german", highlight_all=True
                ),
            )

        return qs

    def sync_search(self):
        self.update(
            search_vector=SearchVector("name", weight="A", config="german")
            + SearchVector("description", weight="B", config="german")
        )
