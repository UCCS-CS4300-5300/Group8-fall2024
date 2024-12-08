from django.shortcuts import render, redirect
from django.urls import reverse_lazy

# Importing other things from project files:
from .models import User, FavoriteLocation
from stars_app.models import ViewingLocation, CelestialEvent
from stars_app.utils import LightPollutionCalculator
from .forms import ChangePasswordForm

# Authentication libraries:
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView

# To display error/success messages:
from django.contrib import messages

# Rest Framework:
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stars_app.serializers import ViewingLocationSerializer, CelestialEventSerializer

# Tile libraries:
import os
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.views.decorators.cache import cache_control
from osgeo import gdal
import subprocess
from django.contrib.admin.views.decorators import staff_member_required

# Distance
from geopy.distance import geodesic


# ---------------------------------------------------------------- #
# Location Management Views:
class CelestialEventViewSet(viewsets.ModelViewSet):
    queryset = CelestialEvent.objects.all()
    serializer_class = CelestialEventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set elevation to 0 if not provided
        serializer.save(elevation=serializer.validated_data.get('elevation', 0))


class ViewingLocationViewSet(viewsets.ModelViewSet):
    queryset = ViewingLocation.objects.all()
    serializer_class = ViewingLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ViewingLocation.objects.all()
        favorites_only = self.request.query_params.get('favorites_only', 'false')
        if favorites_only.lower() == 'true':
            queryset = queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        # Calculate light pollution before saving
        calculator = LightPollutionCalculator()

        # Get values from serializer:
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        elevation = serializer.validated_data.get('elevation', 0)

        # Calculate values:
        pollution_value = calculator.calculate_light_pollution(latitude, longitude, radius_km=1)
        quality_score = calculator.calculate_quality_score(
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            viewing_radius_km=1
        )
        serializer.save(
            added_by=self.request.user,
            light_pollution_value=pollution_value,
            quality_score=quality_score
        )

    @action(detail=True, methods=['POST', 'GET'])
    def favorite(self, request, pk=None):
        location = self.get_object()

        # Handle GET request case:
        if request.method == "GET":
            is_favorited = FavoriteLocation.objects.filter(
                user=request.user,
                location=location
            ).exists()
            return Response({
                'is_favorited': is_favorited,
                'detail': 'Location is favorited' if is_favorited else 'Location is not favorited'
            })


        # Check if already favorited:
        existing_favorite = FavoriteLocation.objects.filter(
            user=request.user,
            location=location
        ).first()

        if existing_favorite:
            return Response(
                {'detail': 'Location already favorited'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new favorite:
        FavoriteLocation.objects.create(
            user=request.user,
            location=location
        )
        serializer = self.get_serializer(location)
        return Response(serializer.data)

    @action(detail=True, methods=['POST', 'GET'])
    def unfavorite(self, request, pk=None):
        location = self.get_object()

        # If it's a GET request, just return the current status
        if request.method == 'GET':
            is_favorited = FavoriteLocation.objects.filter(
                user=request.user,
                location=location
            ).exists()
            return Response({
                'is_favorited': is_favorited,
                'detail': 'Location is favorited' if is_favorited else 'Location is not favorited'
            })

        deleted_count, _ = FavoriteLocation.objects.filter(
            user=request.user,
            location=location
        ).delete()

        if deleted_count:
            serializer = self.get_serializer(location)
            return Response(serializer.data)
        return Response(
            {'detail': 'Location was not favorited'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['GET'])
    def favorites(self, request):
        favorites = self.get_queryset().filter(favorited_by__user=request.user)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

# ---------------------------------------------------------------- #
# Update All Forecasts Button on Upload Page
@staff_member_required
def update_forecast(request):
    locations = ViewingLocation.objects.all()

    for loc in locations:
        loc.updateForecast()

    return render(request, 'stars_app/upload_tif.html')

# ---------------------------------------------------------------- #
# Tile Views:
@staff_member_required
def upload_and_process_tif(request):
    if request.method == 'POST' and request.FILES.get('tif_file'):
        try:
            # Get the uploaded file
            tif_file = request.FILES['tif_file']

            # Ensure the file is a .tif
            if not tif_file.name.endswith('.tif'):
                messages.error(request, 'Please upload a .tif file')
                return redirect('upload_and_process_tif')

            # Create necessary directories
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            os.makedirs(settings.TILES_DIR, exist_ok=True)

            # Save the original file
            original_path = os.path.join(settings.MEDIA_ROOT, 'night_lights.tif')
            with open(original_path, 'wb+') as destination:
                for chunk in tif_file.chunks():
                    destination.write(chunk)

            # Reproject to Web Mercator
            reprojected_path = os.path.join(settings.MEDIA_ROOT, 'night_lights_3857.tif')
            warp_options = gdal.WarpOptions(
                dstSRS='EPSG:3857',
                resampleAlg=gdal.GRA_Bilinear,
                format='GTiff',
                creationOptions=['COMPRESS=LZW']
            )

            gdal.Warp(
                destNameOrDestDS=reprojected_path,
                srcDSOrSrcDSTab=original_path,
                options=warp_options
            )

            # Add overviews
            ds = gdal.Open(reprojected_path, 1)  # 1 = GA_Update
            if ds is not None:
                ds.BuildOverviews("AVERAGE", [2, 4, 8, 16, 32])
                ds = None  # Close the dataset
            else:
                raise Exception("Failed to open reprojected file for overview generation")

            # Generate tiles
            subprocess.run([
                'gdal2tiles.py',
                '--zoom=0-8',
                '--processes=4',
                '--webviewer=none',
                '--resampling=bilinear',
                '--profile=mercator',
                reprojected_path,
                settings.TILES_DIR
            ], check=True)  # Added check=True to raise exception if command fails

            messages.success(request, 'File uploaded and tiles generated successfully!')
            return redirect('map')

        except subprocess.CalledProcessError as e:
            messages.error(request, f'Error generating tiles: {str(e)}')
            return redirect('upload_and_process_tif')

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('upload_and_process_tif')

    return render(request, 'stars_app/upload_tif.html')


@cache_control(max_age=86400)
def serve_tile(request, z, x, y):
    # Mapbox uses XYZ coordinates, whereas GDAL uses TMZ coordinates.
    # We will need to convert XYZ/TMZ, mostly focused on the y coord...
    tms_y = (1 <<z) - 1 -y

    # Serve individual map tiles:
    tile_path = os.path.join(settings.TILES_DIR, str(z), str(x), f"{tms_y}.png")

    if os.path.exists(tile_path):
        response = FileResponse(open(tile_path, 'rb'), content_type='image/png')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    else:
        return HttpResponse('Tile not found', status=404)


# ---------------------------------------------------------------- #
# Navigation Views:
def home(request):
    return render(request, 'stars_app/home.html')

def map(request):
    return render(request, 'stars_app/map.html')

def event_list(request):
    event_list = CelestialEvent.objects.all()
    return render(request, 'stars_app/list.html', {'events':event_list})

def details(request, event_id):
    event = CelestialEvent.objects.get(pk=event_id)
    viewing_locations = ViewingLocation.objects.all()

    closet_loc = viewing_locations[0]
    for loc in viewing_locations:
        event_point = (event.latitude, event.longitude)
        closest_point = (closet_loc.latitude, closet_loc.longitude)
        current_point = (loc.latitude, loc.longitude)

        closest_distance = geodesic(event_point, closest_point).kilometers
        current_distance = geodesic(event_point, current_point).kilometers
        if current_distance < closest_distance:
            closet_loc = loc

    current_data = {
        'event': event,
        'view_loc': closet_loc
    }
    return render(request, 'stars_app/details.html', current_data)

@login_required(login_url='/login/')
def account(request, pk):
    favorites = FavoriteLocation.objects.filter(user=pk)
    return render(request, 'stars_app/account.html', {'favorites':favorites})

class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('home')
    template_name = 'stars_app/change_password.html'


# ---------------------------------------------------------------- #
# Authentication Views:
def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')

            # We are going to define a user filter to check for existing usernames:
            user = User.objects.filter(username=username.lower())

            # Check if the username already exists in our database:
            if user.exists():
                messages.error(request, 'Username already exists...')
                return redirect('register')

            # Check if the password confirmation doesn't match:
            if pass1 != pass2:
                messages.error(request, 'Passwords do not match...')
                return redirect('register')

            # We are creating a user after verifying everything is correct:
            user = User.objects.create(username=username.lower(), email=email)
            user.set_password(pass1)
            user.save()

            # Notify the user that their account has been created successfully:
            messages.success(request, 'Account created successfully')
            return redirect('login')

        except Exception as e:
            # Display a message to the user that registration was unsuccessful:
            messages.error(request, 'Something went wrong...')
            return redirect('register')

    # If we didn't call a post method, direct user to register page:
    return render(request, 'stars_app/register.html')

def custom_login(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            # We are getting the user model from an imported library in models.py:
            user = User.objects.filter(username=username.lower())

            # Check for the case that the user doesn't exist in our database:
            if not user.exists():
                messages.error(request, 'Username not found')
                return redirect('login')

            # Check for matching username & password:
            user = authenticate(request, username=username.lower(), password=password)
            if user is not None:
                login(request, user)
                return redirect('home')     # Low-key I hate this shit can we redirect it to user's previous page?

            # If user couldn't authenticate above, display wrong password message:
            messages.error(request, 'Wrong password...')
            return redirect('login')

        except Exception as e:
            # Display a message to the user that login was unsuccessful:
            messages.error(request, 'Something went wrong...')
            return redirect('home')

    # If we didn't call a post method, direct user to login page:
    return render(request, 'stars_app/login.html')

@login_required(login_url='/login/')
def custom_logout(request):
    logout(request)
    return redirect('home')
