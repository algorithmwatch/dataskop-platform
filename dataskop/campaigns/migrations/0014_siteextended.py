# Generated by Django 3.2.12 on 2022-02-22 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("campaigns", "0013_auto_20220222_1247"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteExtended",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "support_email",
                    models.CharField(default="support@example.com", max_length=255),
                ),
                (
                    "from_email",
                    models.CharField(default="info@example.com", max_length=255),
                ),
                ("https", models.BooleanField(default=True)),
                (
                    "site",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="sites.site"
                    ),
                ),
            ],
        ),
    ]
