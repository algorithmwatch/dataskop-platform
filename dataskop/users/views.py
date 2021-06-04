from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django.views.generic.edit import DeleteView, UpdateView
from sesame.utils import get_user

from .forms import MagicLinkLoginForm
from .signals import post_magic_email_verified

User = get_user_model()


@method_decorator(never_cache, name="dispatch")
class UserUpdateView(LoginRequiredMixin, UpdateView):
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
