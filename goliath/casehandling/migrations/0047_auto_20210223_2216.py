# Generated by Django 3.1.5 on 2021-02-23 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0046_auto_20210222_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalreceivedmessage',
            name='to_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='historicalsentmessage',
            name='to_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='receivedmessage',
            name='to_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='sentmessage',
            name='to_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]