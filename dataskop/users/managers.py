from allauth.account.models import EmailAddress
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.db import IntegrityError


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
        # create an email address to work properly w/ Django Allauth
        EmailAddress.objects.create(
            user=user, email=email, verified=False, primary=True
        )
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

        # create an email address to work properly w/ Django Allauth
        EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
        return user

    def create_unverified_user_send_mail(self, email, ip_address, site, donation=None):
        try:
            user = self.create_user(
                first_name="first_name", last_name="last_name", email=email
            )
            # cleaned version
            email = user.email
            user.send_magic_registration(email, ip_address, site, donation)
        except IntegrityError:
            pass
