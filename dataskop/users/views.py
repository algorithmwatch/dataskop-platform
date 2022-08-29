from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from ratelimit.decorators import ratelimit
from sesame.utils import get_user

from dataskop.users.forms import MagicLinkLoginForm
from dataskop.users.models import User
from dataskop.users.signals import post_magic_email_verified


@method_decorator(never_cache, name="dispatch")
class UserUpdateView(LoginRequiredMixin, DetailView):
    template_name = "account/index.html"
    model = User

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(
    ratelimit(key="ip", rate="100/h", method="POST", block=True), name="post"
)
@method_decorator(
    ratelimit(key="ip", rate="10/m", method="POST", block=True), name="post"
)
class MagicLinkFormView(SuccessMessageMixin, FormView):
    template_name = "account/login_magic.html"
    form_class = MagicLinkLoginForm
    success_message = "Ein Link zum Login wurde an Ihre E-Mail-Adresse versandt."
    success_url = "/"

    def form_valid(self, form):
        self.send_magic_email(form.cleaned_data)
        return super().form_valid(form)

    def send_magic_email(self, cleaned_data):
        email = cleaned_data["email"]
        email_obj = EmailAddress.objects.filter(email=email).first()

        ip_address = self.request.META.get("REMOTE_ADDR")

        site = get_current_site(self.request)
        if email_obj:
            user = email_obj.user
            user.send_magic_login(email, ip_address, site)
        else:
            User.objects.create_unverified_user_send_mail(email, ip_address, site)

    # redirect if user is already logged in
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        return redirect("/")


@method_decorator(never_cache, name="dispatch")
class MagicLinkHandleConfirmationLink(View):
    def get(self, request):
        """
        Scope for each email to ensure the token was actually sent to this
        specific email since we are verifying it.
        """
        email_str = request.GET.get("email")

        if email_str is None:
            raise PermissionDenied("Etwas stimmt nicht mit der E-Mail-Adresse.")

        ip_address = self.request.META.get("REMOTE_ADDR")
        user = get_user(request, scope=email_str + ip_address)

        if user is None:
            raise PermissionDenied(
                "Der Link hat nicht funktioniert. Dies kann folgende Gründe haben: 1. Der Link ist abgelaufen, 2. Du hast eine andere IP-Adresse (z. B. durch einen Proxy). Bitte logge dich erneut hier auf der Seite ein."
            )

        email_address = EmailAddress.objects.filter(user=user, email=email_str).first()

        if not email_address:
            raise PermissionDenied("E-Mail-Adresse nicht gefunden.")

        # if registration
        if email_address.verified:
            messages.success(request, "Login erfolgreich")
        else:
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

            messages.success(request, "Account erfolgreich verifiziert. Danke!")
            post_magic_email_verified.send(request, user=user, email=email_str)

        if request.user.is_authenticated:
            logout(request)

        login(request, user)

        return redirect("my_donations_list")


# can't use SuccessMessageMixin https://stackoverflow.com/a/25325228/4028896
class UserDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "account/user_confirm_delete.html"
    model = User
    success_url = reverse_lazy("home")
    success_message = "Ihr Account und all Ihre Spenden wurden erfolgreich gelöscht."

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UserDeleteView, self).delete(request, *args, **kwargs)
