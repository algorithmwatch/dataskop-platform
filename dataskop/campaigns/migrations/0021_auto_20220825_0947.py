# Generated by Django 3.2.15 on 2022-08-25 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0020_auto_20220509_1847"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalcampaign",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical campaign",
                "verbose_name_plural": "historical campaigns",
            },
        ),
        migrations.AlterField(
            model_name="historicalcampaign",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
