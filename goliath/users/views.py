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


class MagicLinkLogin(View):
    def post(self, request, case_type):
        pass

    def get(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        return render(request, "casehandling/case_new.html", {"case_type": case_type})


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

        magic_link = settings.URL_ORIGIN + (
            reverse("sesam_registration")
            + get_query_string(user, scope=email)
            + "&email="
            + urlquote(email)
        )

        send_mail(
            "Email Login",
            "Click the link" + magic_link,
            "noreply@aw.jfilter.de",
            [email],
            html_message=f"<html>Click the link: {magic_link}</html>",
        )
        return redirect("home")

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

        return redirect("home")
