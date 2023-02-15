# Generated by Django 3.2.15 on 2022-11-09 18:32

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("mailjetsync", "0002_newslettersubscription_has_donated"),
    ]

    operations = [
        migrations.AddField(
            model_name="newslettersubscription",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="created",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscription",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="modified",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscription",
            name="token",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="newslettersubscription",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
