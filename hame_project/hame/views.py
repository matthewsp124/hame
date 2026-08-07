from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Location
from .forms import UserForm

def index(request):
    return render(request, 'hame/index.html')

def about(request):
    return render(request, 'hame/about.html')

def resources(request):
    return render(request, 'hame/resources.html')

def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            return redirect(reverse('hame:login'))
        else:
            print(user_form.errors)

    else:  # if not POST request, render registration form
        user_form = UserForm()

    return render(request, 'hame/register.html', context = {'user_form': user_form})

@login_required
def profile(request):
    context_dict = {}

    return render(request, 'hame/profile.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('hame:index'))


def locations_geojson(request):
    # API between database and map - returns locations as GeoJSON for map display

    # prefetch to avoid separate database queries for each location's categories
    locations = Location.objects.prefetch_related('categories__key').all() 

    features = []
    for loc in locations:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc.lng, loc.lat],
            },
            "properties": {
                "id": loc.id,
                "name": loc.name,
                "address": loc.address,
                "categories": ", ".join(str(cat) for cat in loc.categories.all()),
                # start with just categories, can add all tags later if needed
            },
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features,
    })
