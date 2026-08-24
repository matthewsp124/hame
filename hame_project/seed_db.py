import os
import json
from pathlib import Path
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hame_project.settings")
django.setup()

import osmium
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from hame.models import LocationCategory, LocationCategoryKey, Location

# get file stored outside of django project directory
osmpbf_file = Path(__file__).parent.parent / 'osm_data' / 'data' / 'edinburgh.osm.pbf'

# edinburgh boundary geojson
boundary_file = Path(__file__).parent.parent / 'osm_data' / 'data'/ 'edinburgh.geojson'

# primary feature keys taken from https://wiki.openstreetmap.org/wiki/Map_Features and https://wiki.openstreetmap.org/wiki/Top-level_tag
primary_keys = ["aerialway", "aeroway", "amenity", "barrier", "craft", 
                "education", "emergency", "geological", "healthcare", "historic", 
                "leisure", "man_made", "military", "natural", "office", "public_transport", 
                "railway", "shop", "tourism"]

# irrelevant tags largely sourced from https://taginfo.openstreetmap.org/
bad_tags = ["source", "source_ref", "source:", "attribution", "created_by", "todo", "ref", "ref:"
            "editor", "naptan:", "note", "note:", "fixme", "fixme:", "comment", "comment:", "import",
            "maxspeed", "start_date", "end_date", "leaf_type", "leaf_cycle", "roof:", "material", 
            "wikidata", "wikipedia", "network", "check_date", "description", "gauge", "species"]

def get_boundary_polygon(boundary_file):
    with open(boundary_file) as f:
        data = json.load(f)

    geoms = []
    if data.get("type") == "FeatureCollection":
        for feature in data["features"]:
            geoms.append(shape(feature["geometry"]))
    elif data.get("type") == "Feature":
        geoms.append(shape(data["geometry"]))
    else:
        geoms.append(shape(data))

    return geoms[0] if len(geoms) == 1 else unary_union(geoms)


def build_address(tags):
    parts = [
        tags.get('addr:housenumber', ''),
        tags.get('addr:street', ''),
        tags.get('addr:city', ''),
        tags.get('addr:postcode', '')
    ]
    return ', '.join(p for p in parts if p)

def strip_bad_tags(tags):
    return {k: v for k, v in dict(tags).items() if not any(k.startswith(t) or k == t for t in bad_tags)}

class POIHandler(osmium.SimpleHandler):
    def __init__(self, boundary):
        super().__init__()
        self.boundary = boundary
        self.created_count = 0
        self.updated_count = 0
        self.skipped_outside_count = 0

    def inside_boundary(self, lat, lon):
        # shapely Point uses (lng, lat) order
        return self.boundary.contains(Point(lon, lat))

    def node(self, n):
        tags = strip_bad_tags(n.tags)
        if 'name' not in tags:
            return
        
        key = next((k for k in primary_keys if k in tags), None)
        if key is None:
            return
        value = tags[key]

        lat = n.location.lat
        lon = n.location.lon

        if not self.inside_boundary(lat, lon):
            self.skipped_outside_count += 1
            return

        key_obj, _ = LocationCategoryKey.objects.get_or_create(osm_key=key)
        category, _ = LocationCategory.objects.get_or_create(
            key = key_obj,
            osm_value = value,
        )

        node_location, created = Location.objects.update_or_create(
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

        node_location.categories.set([category])

        if created:
            self.created_count += 1
        else:
            self.updated_count += 1

    def way(self, w):
        # adds locations for highways based on the approximate midpoint of the way
        tags = strip_bad_tags(w.tags)
        if 'highway' not in tags:
            return

        try:
            nodes = [n for n in w.nodes if n.location.valid()]

            if not nodes:
                return
            if not all(self.inside_boundary(n.location.lat, n.location.lon) for n in nodes):
                self.skipped_outside_count += 1
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

        way_location, created = Location.objects.update_or_create(
            osm_id = w.id,
            osm_type = 'w',           
            defaults = {
                'name': tags.get('name', ''),
                'address': build_address(tags),
                'lat': midpoint.lat,
                'lng': midpoint.lon,
                'osm_type': 'w',
                'tags': dict(tags),
            }
        )

        way_location.categories.set([highway_category])

        if created:
            self.created_count += 1
        else:
            self.updated_count += 1
            

if __name__ == "__main__":
    boundary = get_boundary_polygon(boundary_file)
    handler = POIHandler(boundary)
    handler.apply_file(str(osmpbf_file), locations = True)
    print(f"Created {handler.created_count} new locations and updated {handler.updated_count} locations from {osmpbf_file}")
    print(f"Skipped {handler.skipped_outside_count} locations outside the boundary")


            
        
        

