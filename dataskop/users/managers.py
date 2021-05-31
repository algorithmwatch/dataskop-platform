from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_user(self, email, first_name, last_name):
        """
        Create a user account without password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_unusable_password()
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password):
        """
        Create superuser account with email + password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.password = make_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


    def create_unverified_user_send_mail(self, email):
        user = self.create_user(first_name="first_name", last_name="last_name", email=email)
        # cleaned version
        email = user.email

        EmailAddress.objects.create(user=user, email=email, primary=True, verified=False)

        user.send_magic_link(email, "magic_registration")
