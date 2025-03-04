# Generated by Django 5.1.5 on 2025-02-12 09:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("licesnsing", "0002_alter_arduinoreader_date_created"),
    ]

    operations = [
        migrations.AlterField(
            model_name="arduinoreader",
            name="date_created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 12, 9, 46, 42, 522720, tzinfo=datetime.timezone.utc
                ),
                editable=False,
                help_text="Timestamp when the RFID entry was created",
            ),
        ),
    ]
