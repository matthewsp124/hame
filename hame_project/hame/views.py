from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Location

def index(request):
    return render(request, 'hame/index.html')

def about(request):
    return render(request, 'hame/about.html')

def resources(request):
    return render(request, 'hame/resources.html')


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
