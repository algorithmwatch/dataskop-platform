from rest_framework import serializers

from dataskop.campaigns.models import Donation


class DonationUnauthorizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["results", "campaign", "unauthorized_email"]

        extra_kwargs = {"url": {"view_name": "api:donation-unauthorized"}}


class DonationAuthorizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["results", "campaign", "user"]

        extra_kwargs = {"url": {"view_name": "api:donation-authorized"}}
