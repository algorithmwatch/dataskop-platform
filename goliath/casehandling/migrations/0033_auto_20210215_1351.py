# Generated by Django 3.1.5 on 2021-02-15 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0032_auto_20210211_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='casetype',
            name='letter_template',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcasetype',
            name='letter_template',
            field=models.TextField(blank=True, null=True),
        ),
    ]
