from django.contrib import admin

from dataskop.mailjetsync.models import NewsletterSubscription


class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    search_fields = ("email",)
    list_display = ("email", "needs_double_optin", "confirmed_at")
    list_filter = ("needs_double_optin", "confirmed_at")


admin.site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)
