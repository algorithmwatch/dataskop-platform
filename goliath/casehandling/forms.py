from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

from .models import Case


class CaseStatusForm(ModelForm):
    class Meta:
        model = Case
        fields = ["status"]

    helper = FormHelper()
    helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
    helper.form_method = "POST"
