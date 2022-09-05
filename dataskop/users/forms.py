from allauth.account.forms import SignupForm
from django import forms


class MagicLinkLoginForm(forms.Form):
    email = forms.EmailField(label="E-Mail-Adresse", max_length=255)
