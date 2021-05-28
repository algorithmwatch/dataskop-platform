import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

from dataskop.users.forms import CustomSignupForm
from dataskop.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserCreationForm:
    def test_clean_email(self):
        # A user with proto_user params does not exist yet.
        proto_user = UserFactory.build()

        # mock a request via https://stackoverflow.com/a/65018715/4028896
        mocked_request = RequestFactory().get("/")
        middleware = SessionMiddleware()
        middleware.process_request(mocked_request)
        mocked_request.session.save()

        form = CustomSignupForm(
            {
                "email": proto_user.email,
                "first_name": proto_user.first_name,
                "last_name": proto_user.last_name,
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert form.is_valid()
        assert form.clean_email() == proto_user.email

        # Creating a user.
        form.save(mocked_request)

        # The user with proto_user params already exists,
        # hence cannot be created.
        form = CustomSignupForm(
            {
                "email": proto_user.email,
                "first_name": proto_user.first_name,
                "last_name": proto_user.last_name,
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
