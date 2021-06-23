from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(required=True, label="Vorname")
        self.fields["last_name"] = forms.CharField(required=True, label="Nachname")


class MagicLinkLoginForm(forms.Form):
    email = forms.EmailField(label="E-Mail-Adresse", max_length=255)
