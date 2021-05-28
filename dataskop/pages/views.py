from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic.base import TemplateView


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
