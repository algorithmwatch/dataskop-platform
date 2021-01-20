from django.views.generic.edit import UpdateView

from django.contrib.auth import get_user_model


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
