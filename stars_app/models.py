# models.py

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ViewingLocation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField(help_text="Elevation in meters")

    light_pollution_value = models.FloatField(null=True, blank=True, help_text="Calculated light pollution value from tiles")
    quality_score = models.FloatField(null=True, blank=True)

    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

class CelestialEvent(models.Model):
    EVENT_TYPES = [
        ('METEOR', 'Meteor Shower'),
        ('ECLIPSE', 'Eclipse'),
        ('PLANET', 'Planetary Event'),
        ('AURORA', 'Aurora'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()
    viewing_radius = models.FloatField(help_text="Optimal viewing radius in km")

    recommended_locations = models.ManyToManyField(
        ViewingLocation,
        through='EventLocation',
        blank=True
    )

    def __str__(self):
        return f'{self.name} ({self.start_time.date()})'

class EventLocation(models.Model):
    event = models.ForeignKey(CelestialEvent, on_delete=models.CASCADE)
    location = models.ForeignKey(ViewingLocation, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)