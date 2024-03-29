# Generated by Django 3.2.11 on 2022-02-09 18:06

from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ("campaigns", "0012_auto_20220209_1804"),
        ("campaigns", "0013_alter_donornotification_draft"),
    ]

    dependencies = [
        ("campaigns", "0011_auto_20211019_1439"),
    ]

    operations = [
        migrations.AddField(
            model_name="provider",
            name="client",
            field=models.CharField(
                default="DataSkop Electron app",
                help_text="Name of the software that collects the data, e.g., DataSkop Electron app",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="donornotification",
            name="draft",
            field=models.BooleanField(
                default=True,
                help_text="If you set draft to false, the email will get sent to the chosen         campaign (and can't be changed anymore).",
            ),
        ),
        migrations.AlterField(
            model_name="provider",
            name="name",
            field=models.CharField(
                help_text="Platform or website from which the data is scraped, e.g., YouTube",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="provider",
            name="scraping_config_schema",
            field=models.JSONField(
                blank=True,
                help_text="Optional JSON schema to validate the `scraping_config` of `Campaign`",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="donornotification",
            name="draft",
            field=models.BooleanField(
                default=True,
                help_text="If you set draft to false, the email will get sent to the chosen campaign (and can't be changed anymore).",
            ),
        ),
    ]
