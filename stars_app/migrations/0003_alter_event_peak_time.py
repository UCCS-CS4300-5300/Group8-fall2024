# Generated by Django 4.2 on 2024-10-12 20:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stars_app', '0002_alter_event_peak_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='peak_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
