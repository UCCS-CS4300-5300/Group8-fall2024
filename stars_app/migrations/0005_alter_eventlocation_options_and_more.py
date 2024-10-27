# Generated by Django 4.2 on 2024-10-27 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stars_app', '0004_celestialevent_eventlocation_viewinglocation_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventlocation',
            options={},
        ),
        migrations.RemoveField(
            model_name='eventlocation',
            name='quality_score',
        ),
        migrations.AddField(
            model_name='viewinglocation',
            name='quality_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
