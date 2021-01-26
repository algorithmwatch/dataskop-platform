from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

from goliath.users.views import (
    UserUpdate,
    MagicLinkVerifyEmail,
    MagicLinkLoginEmail,
    magic_link_signup_view,
    magic_link_login_view,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "ueber-uns/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    path(
        "sesame/registration/",
        MagicLinkVerifyEmail.as_view(),
        name="sesame_registration",
    ),
    path(
        "sesame/login/",
        MagicLinkLoginEmail.as_view(),
        name="sesame_login",
    ),
    path(
        "account/signup/email/",
        magic_link_signup_view,
        name="account_signup_email",
    ),
    # overriding allauth specific login page
    path(
        "account/login/",
        magic_link_login_view,
        name="account_login",
    ),
    # hacking simple account page here
    path("account/", UserUpdate.as_view(), name="account_index"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("account/", include("allauth.urls")),
    path("", include("goliath.casehandling.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
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
