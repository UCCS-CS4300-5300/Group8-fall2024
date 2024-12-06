# Generated by Django 4.2 on 2024-12-05 00:19

from django.db import migrations, models
import django.db.models.deletion
import stars_app.models.defaultforecast


class Migration(migrations.Migration):

    dependencies = [
        ('stars_app', '0015_favoritelocation_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viewinglocation',
            name='forecast',
            field=models.ForeignKey(default=stars_app.models.defaultforecast.defaultforecast, on_delete=django.db.models.deletion.CASCADE, to='stars_app.forecast'),
        ),
    ]