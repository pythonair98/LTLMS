# Generated by Django 5.1.5 on 2025-02-11 10:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("licesnsing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="arduinoreader",
            name="date_created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 11, 10, 51, 44, 350780, tzinfo=datetime.timezone.utc
                ),
                editable=False,
                help_text="Timestamp when the RFID entry was created",
            ),
        ),
    ]
