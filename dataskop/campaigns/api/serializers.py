from rest_framework import serializers

from dataskop.campaigns.models import Campaign, Donation, Event


class DonationUnauthorizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["results", "campaign", "unauthorized_email", "ip_address"]

        extra_kwargs = {"url": {"view_name": "api:donation-unauthorized"}}


class DonationAuthorizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["results", "campaign", "user"]

        extra_kwargs = {"url": {"view_name": "api:donation-authorized"}}


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "scraping_config",
            "image",
            "provider",
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["campaign", "message", "data", "ip_address"]
