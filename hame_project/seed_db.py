import os
from pathlib import Path
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hame_project.settings")
django.setup()

import osmium
from hame.models import LocationCategory, LocationCategoryKey, Location

# get file stored outside of django project directory
osmpbf_file = Path(__file__).parent.parent / 'osm_data' / 'data' / 'edinburgh.osm.pbf'

# primary feature keys taken from https://wiki.openstreetmap.org/wiki/Map_Features and https://wiki.openstreetmap.org/wiki/Top-level_tag
primary_keys = ["aerialway", "aeroway", "amenity", "barrier", "craft", 
                "education", "emergency", "geological", "healthcare", "historic", 
                "leisure", "man_made", "military", "natural", "office", "public_transport", 
                "railway", "shop", "tourism"]

def build_address(tags):
    parts = [
        tags.get('addr:street', ''),
        tags.get('addr:city', ''),
        tags.get('addr:postcode', '')
    ]
    return ', '.join(p for p in parts if p)

class POIHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.count = 0 

    def node(self, n):
        tags = n.tags
        if 'name' not in tags:
            return
        
        key = next((k for k in primary_keys if k in tags), None)
        if key is None:
            return
        value = tags[key]

        key_obj, _ = LocationCategoryKey.objects.get_or_create(osm_key=key)
        category, _ = LocationCategory.objects.get_or_create(
            key = key_obj,
            osm_value = value,
        )

        location, created = Location.objects.get_or_create(
            osm_id = n.id,
            osm_type = 'n',
            defaults = {
                'name': tags.get('name'),
                'address': build_address(tags),
                'lat': n.location.lat,
                'lng': n.location.lon,
                'osm_type': 'n',
                'tags': dict(tags),
            },
        )

        location.categories.add(category)

        if created:
            self.count += 1

    def way(self, w):
        # adds locations for highways based on the approximate midpoint of the way
        tags = w.tags
        if 'highway' not in tags:
            return

        try:
            nodes = [n for n in w.nodes if n.location.valid()]
            if not nodes:
                return
            midpoint = nodes[len(nodes) // 2].location
        except Exception as e:
            print(f"Error processing way {w.id}: {e}")
            return

        value = tags['highway']
        highway_key, _ = LocationCategoryKey.objects.get_or_create(osm_key='highway')
        highway_category, _ = LocationCategory.objects.get_or_create(
            key = highway_key,
            osm_value = value,
        )

        way_location, created = Location.objects.get_or_create(
            osm_id = w.id,           
            defaults = {
                'name': '',
                'address': build_address(tags),
                'lat': midpoint.lat,
                'lng': midpoint.lon,
                'osm_type': 'w',
                'tags': dict(tags),
            }
        )

        way_location.categories.add(highway_category)

        if created:
            self.count += 1
            

if __name__ == "__main__":
    handler = POIHandler()
    handler.apply_file(str(osmpbf_file), locations = True)
    print(f"Created {handler.count} new locations from {osmpbf_file}")


            
        
        

