from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db import models
from django.db.models import F
from django.utils.text import smart_split


class SearchExpertnalSupportQuerySet(models.QuerySet):
    def search(self, search_text, highlight=True):
        if search_text is None:
            return self

        tokens = [f"{t}:*" for t in smart_split(search_text)]
        search_query = SearchQuery(
            " & ".join(tokens), config="german", search_type="raw"
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


class SearchCaseTypeQuerySet(models.QuerySet):
    def search(self, search_text, highlight=True):
        if search_text is None:
            return self

        tokens = [f"{t}:*" for t in smart_split(search_text)]
        search_query = SearchQuery(
            " & ".join(tokens), config="german", search_type="raw"
        )

        qs = self.filter(search_vector=search_query)
        qs = qs.annotate(rank=SearchRank(F("search_vector"), search_query)).order_by(
            "-rank"
        )

        if highlight:
            qs = qs.annotate(
                title_highlighted=SearchHeadline(
                    "title", search_query, config="german", highlight_all=True
                ),
                claim_highlighted=SearchHeadline(
                    "claim", search_query, config="german", highlight_all=True
                ),
                short_description_highlighted=SearchHeadline(
                    "short_description",
                    search_query,
                    config="german",
                    highlight_all=True,
                ),
                description_highlighted=SearchHeadline(
                    "description", search_query, config="german", highlight_all=True
                ),
            )

        return qs

    def sync_search(self):
        self.update(
            search_vector=SearchVector("title", weight="A", config="german")
            + SearchVector("claim", weight="A", config="german")
            + SearchVector("short_description", weight="B", config="german")
            + SearchVector("description", weight="C", config="german")
        )
