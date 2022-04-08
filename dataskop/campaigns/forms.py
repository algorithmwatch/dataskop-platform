from django import forms

from .models import Campaign, Donation, DonorNotificationSetting


class DonorNotificationSettingForm(forms.ModelForm):
    class Meta:
        model = DonorNotificationSetting
        fields = ["disable_all", "disabled_campaigns"]

    disable_all = forms.BooleanField(
        label="Benachrichtungen für alle Kampagnen ausstellen"
    )
    disabled_campaigns = forms.ModelMultipleChoiceField(
        label="Benachrichtigungen für einzelne Kampagnen austellen",
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # only select campaigns the user has donated to
        participated_campaigns = Donation.objects.filter(
            donor=self.instance.user
        ).values_list("campaign", flat=True)

        self.fields["disabled_campaigns"].queryset = Campaign.objects.filter(
            pk__in=participated_campaigns
        )


class DonorNotificationDisableForm(forms.Form):
    disable = forms.BooleanField(initial=True)


class DashboardForm(forms.Form):
    campaign = forms.ModelChoiceField(queryset=Campaign.objects)
