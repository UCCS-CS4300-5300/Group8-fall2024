from django.db.models import Avg
from rest_framework import serializers

from stars_app.models.celestialevent import CelestialEvent
from stars_app.models.favoritelocation import FavoriteLocation
from stars_app.models.viewinglocation import ViewingLocation
from stars_app.models.locationreview import LocationReview


# Location Review Serializer -------------------------------------- #
class LocationReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = LocationReview
        fields = ['id', 'location', 'user', 'user_full_name',
                 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'user_full_name']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


# Viewing Location Serializer ------------------------------------- #
class ViewingLocationSerializer(serializers.ModelSerializer):
    added_by = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    reviews = LocationReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = ViewingLocation
        fields = ['id', 'name', 'latitude', 'longitude', 'elevation',
                  'formatted_address', 'administrative_area', 'locality', 'country',
                  'light_pollution_value', 'quality_score', 'added_by',
                  'created_at', 'is_favorited', 'cloudCoverPercentage', 'forecast',
                  'reviews', 'average_rating', 'review_count']
        read_only_fields = ['light_pollution_value', 'quality_score', 'added_by',
                          'created_at', 'formatted_address', 'administrative_area',
                          'locality', 'country']

    def get_added_by(self, obj):
        return {
            'id': obj.added_by.id,
            'username': obj.added_by.username
        } if obj.added_by else None

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteLocation.objects.filter(
                user=request.user,
                location=obj
            ).exists()

        # Otherwise return false since no favorites:
        return False


# Celestial Event Serializer -------------------------------------- #
class CelestialEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CelestialEvent
        fields = ['id', 'name', 'event_type', 'description',
                  'latitude', 'longitude', 'elevation',
                  'start_time', 'end_time',
                  'viewing_radius']
