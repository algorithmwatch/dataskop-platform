from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(required=True)
        self.fields["last_name"] = forms.CharField(required=True)


class MagicLinkSignupForm(forms.Form):
    first_name = forms.CharField(label="Vorname", max_length=255)
    last_name = forms.CharField(label="Nachname", max_length=255)
    email = forms.EmailField(label="E-Mail-Adresse", max_length=255)


class MagicLinkLoginForm(forms.Form):
    email = forms.EmailField(label="E-Mail-Adresse", max_length=255)
