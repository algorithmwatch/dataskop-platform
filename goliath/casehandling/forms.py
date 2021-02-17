import re

from django.forms import CharField, Form, ModelForm

from .models import Case


class CaseStatusForm(ModelForm):
    class Meta:
        model = Case
        fields = ["status"]


def get_admin_form_preview(ct):
    form_fields = {}

    context_variables = re.findall(r"\{\{(.*?)\}\}", ct.letter_template) + re.findall(
        r"\{\%(.*?)\%\}", ct.letter_template
    )
    context_variables = [
        x.strip().lower()
        for x in context_variables
        if x.strip().lower() not in ["if", "else", "endif", "for", "endfor"]
    ]

    # remove all expressions, only keep variables
    context_variables = [x.split("==")[0].split("!=")[0] for x in context_variables]
    context_variables = [
        re.sub(r"^(if|for) ", "", x).strip() for x in context_variables
    ]

    # make unique
    for var in set(context_variables):
        form_fields[var] = CharField(required=False)

    # ok now form_fields has all the fields for our form
    return type("DynamicForm", (Form,), form_fields)
