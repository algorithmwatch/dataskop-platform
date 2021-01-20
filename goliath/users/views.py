from django.views.generic.edit import UpdateView

from django.contrib.auth import get_user_model


User = get_user_model()


class UserUpdate(UpdateView):
    template_name = "account/index.html"
    model = User
    fields = ["first_name", "last_name"]

    def get_object(self, queryset=None):
        return self.request.user
