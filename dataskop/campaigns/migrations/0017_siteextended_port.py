# Generated by Django 3.2.12 on 2022-02-22 19:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0016_auto_20220222_1629"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteextended",
            name="port",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
