# Generated by Django 4.2 on 2024-11-20 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stars_app', '0013_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]