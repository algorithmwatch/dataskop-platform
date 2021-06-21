from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.decorators.cache import cache_control
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("account/", include("allauth.urls")),
    path("", include("dataskop.users.urls")),
    path("", include("dataskop.campaigns.urls")),
    path("", include("dataskop.pages.urls")),
]


# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

    # watch herald emails locally
    urlpatterns = [
        re_path(r"^herald/", include("herald.urls")),
    ] + urlpatterns

# 1) the catchall flatpages must be placed in the bottom
# 2) the regex ensures that the `append slash & redirect` middleware works
urlpatterns += [
    re_path(
        r"^(?P<url>.*/)$", cache_control(max_age=3600, public=True)(views.flatpage)
    ),
]
