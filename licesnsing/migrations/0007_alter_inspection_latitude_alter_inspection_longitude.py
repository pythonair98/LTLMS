# Generated by Django 5.1.5 on 2025-02-19 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("licesnsing", "0006_remove_inspection_cars_building_photo_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspection",
            name="latitude",
            field=models.IntegerField(verbose_name="Latitude"),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="longitude",
            field=models.IntegerField(verbose_name="Longitude"),
        ),
    ]
