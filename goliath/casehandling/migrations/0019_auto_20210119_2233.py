# Generated by Django 3.1.5 on 2021-01-19 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0018_auto_20210111_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='status',
            field=models.CharField(choices=[('UV', 'Waiting user verification'), ('ES', 'Waiting until email sent'), ('WR', 'Waiting for response'), ('WU', 'Waiting for user input'), ('CN', 'Closed, given up'), ('CP', 'Closed, case resolved'), ('CM', 'Closed, mixed feelings')], max_length=2),
        ),
        migrations.AlterField(
            model_name='historicalcase',
            name='status',
            field=models.CharField(choices=[('UV', 'Waiting user verification'), ('ES', 'Waiting until email sent'), ('WR', 'Waiting for response'), ('WU', 'Waiting for user input'), ('CN', 'Closed, given up'), ('CP', 'Closed, case resolved'), ('CM', 'Closed, mixed feelings')], max_length=2),
        ),
    ]
