# Generated by Django 3.1.5 on 2021-01-19 23:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_auto_20210119_2330"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True, max_length=254, unique=True, verbose_name="email address"
            ),
        ),
    ]
