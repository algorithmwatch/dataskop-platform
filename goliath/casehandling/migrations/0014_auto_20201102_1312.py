# Generated by Django 3.0.10 on 2020-11-02 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0013_auto_20201029_2114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='text',
            new_name='answers_text',
        ),
        migrations.RenameField(
            model_name='historicalcase',
            old_name='text',
            new_name='answers_text',
        ),
    ]