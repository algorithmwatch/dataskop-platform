from django.template import Context, Library, Template
from django.utils.safestring import mark_safe

register = Library()


@register.simple_tag(takes_context=True)
def meta_tags(
    context,
    title="DataSkop",
    description=None,
    social_media_image=None,
):
    context["title"] = title + " - DataSkop"
    context["description"] = description or "Mit DataSkop entsteht eine Plattform für Datenspenden, um mit deren Hilfe algorithmische Entscheidungssysteme zu untersuchen und die digitale Souveränität der Nutzer·innen zu stärken"
    context["social_media_image"] = social_media_image or "/static/img/ogimage.png"

    # build absolute URL if needed
    context["social_media_image"] = context["request"].build_absolute_uri(
        context["social_media_image"]
    )

    t = Template(
        """
    <title>{{ title }}</title>

    <meta name="description" content="{{ description }}" />
    <meta name="author" content="AlgorithmWatch" />

    {# Open Graph #}
    <meta property="og:title" content="{{ title }}" />
    <meta property="og:url" content="{{ request.build_absolute_uri }}" />
    <meta property="og:description" content="{{ description }}" />
    <meta property="og:site_name" content="DataSkop" />
    <meta property="og:image" content="{{ social_media_image }}" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@dataskop_net">
    <meta name="twitter:image" content="{{ social_media_image }}" >
    """
    )

    return mark_safe(t.render(Context(context)))
