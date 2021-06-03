from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.generic import View
from django.views.generic.edit import UpdateView
from sesame.utils import get_user

from .forms import MagicLinkLoginForm
from .signals import post_magic_email_verified

# from dataskop.casehandling.models import PostCaseCreation


User = get_user_model()


@method_decorator(never_cache, name="dispatch")
class UserUpdate(LoginRequiredMixin, UpdateView):
    template_name = "account/index.html"
    model = User
    fields = ["first_name", "last_name"]

    def get_object(self, queryset=None):
        return self.request.user


@never_cache
def magic_link_login_view(request):
    if request.method == "POST":
        form = MagicLinkLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            email_obj = EmailAddress.objects.filter(email=email).first()

            if not email_obj:
                raise PermissionDenied
            user = email_obj.user

            user.send_magic_link(email, "magic_login")
            messages.info(
                request, "Ein Link zum Login wurde an Ihre E-Mail-Adresse versandt."
            )

    else:
        form = MagicLinkLoginForm()

    return render(request, "account/login_magic.html", {"form": form})


@method_decorator(never_cache, name="dispatch")
class MagicLinkHandleConfirmationLink(View):
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


@method_decorator(never_cache, name="dispatch")
class MagicLinkHandleRegistrationLink(View):
    def get(self, request):
        """
        Scope for each email to ensure the token was actually sent to this
        specific email since we are verifying it.
        """
        email_str = request.GET.get("email")
        user = get_user(request, scope=email_str)

        if user is None:
            raise PermissionDenied

        email_address = EmailAddress.objects.filter(user=user, email=email_str).first()

        if not email_address:
            raise PermissionDenied

        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()

        # login
        login(request, user)

        messages.success(request, "Account erfolgreich verifiziert. Danke!")

        post_magic_email_verified.send(request, user, email_str)

        return redirect("/")


@require_GET
@never_cache
def export_text(request):
    user = request.user
    export_string = ""

    # for case in user.case_set.all():
    #     for m in case.all_messages:
    #         m_text = ", ".join(
    #             [f"{k}: {v}" for (k, v) in m.__dict__.items() if k != "_state"]
    #         )
    #         export_string += m_text + "\n\n"

    return HttpResponse(export_string, content_type="text/plain; charset=UTF-8")
