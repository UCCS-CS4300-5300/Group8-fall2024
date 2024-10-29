# Generated by Django 4.2 on 2024-10-29 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stars_app', '0008_remove_celestialevent_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celestialevent',
            name='elevation',
            field=models.FloatField(help_text='Elevation in meters'),
        ),
        migrations.AlterField(
            model_name='celestialevent',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='celestialevent',
            name='longitude',
            field=models.FloatField(),
        ),
    ]
