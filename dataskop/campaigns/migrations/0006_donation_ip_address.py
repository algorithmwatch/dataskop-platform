# Generated by Django 3.1.9 on 2021-06-23 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0005_auto_20210618_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
