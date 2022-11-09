from rest_framework import serializers

from dataskop.mailjetsync.models import NewsletterSubscription


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ["email", "has_donated", "needs_double_optin", "ip_address"]
