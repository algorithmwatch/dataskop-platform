# Generated by Django 3.1.5 on 2021-01-21 18:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_auto_20210119_2335"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
