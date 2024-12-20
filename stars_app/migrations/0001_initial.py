# Generated by Django 5.1.3 on 2024-12-10 06:57

import django.core.validators
import django.db.models.deletion
import stars_app.models.defaultforecast
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CelestialEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('event_type', models.CharField(choices=[('METEOR', 'Meteor Shower'), ('ECLIPSE', 'Eclipse'), ('PLANET', 'Planetary Event'), ('AURORA', 'Aurora'), ('OTHER', 'Other'), ('COMET', 'Comet')], max_length=10)),
                ('description', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('elevation', models.FloatField(help_text='Elevation in meters')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('viewing_radius', models.FloatField(help_text='Optimal viewing radius in km')),
            ],
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('forecast', models.JSONField(default=list, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ViewingLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('elevation', models.FloatField(help_text='Elevation in meters')),
                ('formatted_address', models.CharField(blank=True, help_text='Full formatted address from geocoding or user input', max_length=500, null=True)),
                ('administrative_area', models.CharField(blank=True, help_text='State/Province/Region', max_length=200, null=True)),
                ('locality', models.CharField(blank=True, help_text='City/Town', max_length=200, null=True)),
                ('country', models.CharField(blank=True, max_length=200, null=True)),
                ('cloudCoverPercentage', models.FloatField(null=True)),
                ('light_pollution_value', models.FloatField(blank=True, help_text='Light pollution in magnitude per square arcsecond (higher values = darker skies)', null=True)),
                ('quality_score', models.FloatField(blank=True, help_text='Overall viewing quality score (0-100) based on light pollution and elevation', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forecast', models.ForeignKey(default=stars_app.models.defaultforecast.defaultforecast, on_delete=django.db.models.deletion.CASCADE, to='stars_app.forecast')),
            ],
        ),
        migrations.CreateModel(
            name='LocationReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(help_text='Rating from 1 to 5 stars', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True, help_text='Optional review comment', max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_reviews', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='stars_app.viewinglocation')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'location')},
            },
        ),
        migrations.CreateModel(
            name='FavoriteLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_locations', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='stars_app.viewinglocation')),
            ],
            options={
                'unique_together': {('user', 'location')},
            },
        ),
    ]
