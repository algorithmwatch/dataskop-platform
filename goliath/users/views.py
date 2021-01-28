from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.generic.edit import UpdateView
from sesame.utils import get_user

from ..utils.magic_link import send_magic_link

from .forms import MagicLinkLoginForm, MagicLinkSignupForm

User = get_user_model()


class UserUpdate(LoginRequiredMixin, UpdateView):
    template_name = "account/index.html"
    model = User
    fields = ["first_name", "last_name"]

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super(UserUpdate, self).get_form(form_class)
        for f in self.fields:
            form.fields[f].required = False
        return form


def magic_link_signup_view(request):
    if request.method == "POST":
        form = MagicLinkSignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]

            try:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                # use cleaned email address in user from now on
                email = user.email
                EmailAddress.objects.create(
                    user=user, email=email, primary=True, verified=False
                )
                send_magic_link(request, user, email, "magic_registration")
                messages.success(
                    request,
                    "Ein Link zum Abschluss der Registrierung wurde an Ihre E-Mail-Adresse versandt.",
                )

            except IntegrityError as e:
                if "unique constraint" in str(e.args):
                    messages.error(
                        request,
                        "Mit dieser E-mail-Adresse wurde schon ein Account erstellt.",
                    )
    else:
        form = MagicLinkSignupForm()

    return render(request, "account/signup_email.html", {"form": form})


def magic_link_login_view(request):
    if request.method == "POST":
        form = MagicLinkLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = EmailAddress.objects.filter(email=email).first()

            if not user:
                raise PermissionDenied
            user = user.user

            send_magic_link(request, user, email, "magic_login")
            messages.info(
                request, "Ein Link zum Login wurde an Ihre E-Mail-Adresse versandt."
            )

    else:
        form = MagicLinkLoginForm()

    return render(request, "account/login.html", {"form": form})


class MagicLinkLoginEmail(View):
    def get(self, request):
        """
        login when person opened magic link from email
        """
        email = request.GET.get("email")
        user = get_user(request, scope=email)

        if user is None:
            messages.error(
                request, "Es wurde kein Account mit diese E-Mail-Adresse gefunden."
            )
            return redirect("account_login")
        messages.success(request, "Login erfolgreich")
        login(request, user)
        return redirect("account_index")


class MagicLinkVerifyEmail(View):
    def get(self, request):
        """
        Scope for each email to ensure the token was actually sent to this
        specific email since we are verifying it.
        """
        email = request.GET.get("email")
        user = get_user(request, scope=email)

        if user is None:
            raise PermissionDenied

        email_address = EmailAddress.objects.filter(user=user, email=email).first()

        if email_address:
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            login(request, user)
        else:
            raise PermissionDenied

        messages.success(request, "Account erfolgreich erstellt.")
        return redirect("account_index")
