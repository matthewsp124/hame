import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Location, UserEntry
from .forms import UserForm, UserEntryForm

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'hame/index.html')

@login_required
def add_review(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    entry = UserEntry.objects.filter(location=location, user=request.user).first()

    if request.method == 'POST':
        form = UserEntryForm(request.POST, instance = entry)  # if entry exists, edit it, otherwise create new entry
        if form.is_valid():
            entry = form.save(commit=False)
            entry.location = location
            entry.user = request.user
            entry.save()
            return redirect(reverse('hame:index'))
    else:
        form = UserEntryForm(instance = entry)

    return render(request, 'hame/add_review.html', {'form': form, 'location': location, 'is_edit': entry is not None})

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
    entries = (UserEntry.objects
            .filter(user=request.user)
            .select_related('location')
            .order_by('-created_at'))

    return render(request, 'hame/profile.html', {'entries': entries})

@require_POST
@login_required
def delete_review(request, entry_id):
    entry = get_object_or_404(UserEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect(reverse('hame:profile'))

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('hame:index'))


# consolidate multiple choice questions
BAR_FIELDS = [
    ('wheelchair', 'Wheelchair accessible entrance'),
    ('auto_doors', 'Automatic doors'),
    ('level_floor_or_lift', 'Level flooring / lift access'),
    ('accessible_toilet', 'Accessible toilet'),
    ('parking', 'Parking on-site'),
    ('disabled_bay', 'Disabled parking bay'),
    ('braille_signage', 'Braille signs'),
    ('hearing_loop', 'Hearing loop'),
    ('quiet_space', 'Quiet space available'),
    ('tactile_paving', 'Tactile paving present'),
    ('nonvisual_crossing_cues', 'Auditory / tactile road crossing cues'),
]

def location_reviews(request, location_id):
    try:
        location = get_object_or_404(Location, id = location_id)
        entries = (UserEntry.objects
                .filter(location_id=location_id)
                .select_related('user')
                .order_by('-created_at'))

        counts = {field: {'Y': 0, 'N': 0, 'NA': 0} for field, _ in BAR_FIELDS}
        for entry in entries:
            for field, _ in BAR_FIELDS:
                value = getattr(entry, field)
                if value in counts[field]:
                    counts[field][value] += 1

        stats = []
        for field, label in BAR_FIELDS:
            c = counts[field]
            total = c['Y'] + c['N'] + c['NA']
            if total == 0:  # no answers for this field
                continue

            yes_pct = round(c['Y'] / total * 100)
            na_pct = round(c['NA'] / total * 100)
            no_pct = 100 - yes_pct - na_pct

            stats.append({
                'label': label,
                'yes_pct': yes_pct,
                'na_pct': na_pct,
                'no_pct': no_pct,
                'yes_count': c['Y'],
                'na_count': c['NA'],
                'no_count': c['N'],
                'total': total,
            })

        reviews = [{
            'username': entry.user.username if entry.user else 'Anonymous',  # Anon should be exceptional
            'created_at': entry.created_at.strftime('%Y-%m-%d'),
            'text_body': entry.text_body,
        } for entry in entries if entry.text_body]

        return JsonResponse({'stats': stats, 'reviews': reviews})
    
    except Exception as e:
        logger.exception(f"Error loading reviews for location {location_id}")
        return JsonResponse({'error': str(e)}, status=500)

def _locations_to_geojson(locations):
    features = []
    for loc in locations:
        tags = loc.tags
        properties = {
            "id": loc.id,
            "name": loc.name,
            "address": loc.address,
            "categories": ", ".join(str(cat) for cat in loc.categories.all()),
        }

        if "website" in tags:
            properties["website"] = tags["website"]
        if "phone" in tags:
            properties["phone"] = tags["phone"]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc.lng, loc.lat],
            },
            "properties": properties
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }

def locations_geojson(request):
    # API between database and map - returns locations as GeoJSON for map display
    locations = Location.objects.prefetch_related('categories__key').all()  # prefetch to avoid separate database queries for each location's categories
    return JsonResponse(_locations_to_geojson(locations))


CATEGORY_PREFIXES = ('category:', 'cat:', 'type:')

def search_locations(request):
    # same as locations_geojson but with search query filtering
    query = request.GET.get('q', '').strip()
    locations = Location.objects.prefetch_related('categories__key').all()

    if query:
        category_text = []
        name_text = []

        for word in query.split():
            lower_word = word.lower()
            matched_prefix = next((p for p in CATEGORY_PREFIXES if lower_word.startswith(p)), None)
            if matched_prefix:
                value = word[len(matched_prefix):]
                if value:
                    category_text.append(value)
            else:
                name_text.append(word)

        if category_text:
            category_filter = Q()  # Q builds and/or conditions for queries
            for cat in category_text:
                category_filter |= (  # location matches if any of its osm_value's or osm_keys contain the category text
                    Q(categories__osm_value__icontains = cat) |  # icontains = case insensitive
                    Q(categories__key__osm_key__icontains = cat)
                )
            locations = locations.filter(category_filter)

        if name_text:
            text = ' '.join(name_text)
            locations = locations.filter(
                Q(name__icontains = text) | Q(address__icontains = text)
            )

        locations = locations.distinct()  # deduplication where multiple categories match the same location

    return JsonResponse(_locations_to_geojson(locations))