from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlquote
from django.views.generic import View
from django.views.generic.edit import UpdateView
from sesame.utils import get_query_string, get_user
from django.contrib import messages

User = get_user_model()


class UserUpdate(UpdateView):
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


def send_magic_link(user, email, viewname):
    magic_link = settings.URL_ORIGIN + (
        reverse(viewname)
        + get_query_string(user, scope=email)
        + "&email="
        + urlquote(email)
    )

    send_mail(
        "Email Login",
        "Click the link " + magic_link,
        "noreply@aw.jfilter.de",
        [email],
        html_message=f"""<html><a href="{magic_link}">Click the link to login</a></html>""",
    )


class MagicLinkLogin(View):
    def post(self, request):
        email = request.POST["email"]
        user = EmailAddress.objects.filter(email=email).first()

        if not user:
            raise PermissionDenied
        user = user.user

        send_magic_link(user, email, "sesame_login")
        messages.info(
            request, "Ein Link zum Login wurde an Ihre E-Mail-Adresse versandt."
        )
        return redirect("account_login")

    def get(self, request):
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


class MagicLinkRegistration(View):
    def post(self, request):
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        user = User.objects.create_user(
            username=" ", first_name=first_name, last_name=last_name, email=email
        )
        EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=False
        )
        send_magic_link(user, email, "sesame_registration")
        messages.success(
            request,
            "Ein Link zum Abschluss der Registrierung wrude an Ihre E-Mail-Adresse versandt.",
        )
        return redirect("account_signup")

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
