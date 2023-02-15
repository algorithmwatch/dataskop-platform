import re

from django.db import migrations


def fix_event_messages(apps, schema_editor):
    Event = apps.get_model("campaigns", "Event")
    for e in Event.objects.filter(message__icontains="donation deleted: "):
        digits = re.findall(r"\d+", e.message)
        if len(digits) == 0:
            continue
        elif len(digits) == 1:
            digits = int(digits[0])
        else:
            raise ValueError(
                "Something is wrong, we found too many digits in the message"
            )

        e.message = "donation deleted"
        e.data = {"donation": digits}
        e.save()

    for e in Event.objects.filter(message__icontains="user deleted: "):
        digits = re.findall(r"\d+", e.message)
        if len(digits) == 0:
            continue
        elif len(digits) == 1:
            digits = int(digits[0])
        else:
            raise ValueError(
                "Something is wrong, we found too many digits in the message"
            )

        e.message = "user deleted"
        e.data = {"user": digits}
        e.save()


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0017_siteextended_port"),
    ]

    operations = [migrations.RunPython(fix_event_messages, migrations.RunPython.noop)]
