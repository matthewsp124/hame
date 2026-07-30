from django.test import TestCase
from django.db import IntegrityError
from hame.models import LocationCategory, Location, UserEntry

class LocationCategoryModelTests(TestCase):
    def test_default_category_creation(self):
        loc = Location.objects.create(name = "Test", address = "123 Test St", lat = 0.0, lng = 0.0)
        self.assertEqual(loc.category.name, "Uncategorised")

    def test_duplicate_osm_category_constraint(self):
        LocationCategory.objects.create(name = "TestCategory", osm_key = "testkey", osm_value = "testvalue")
        with self.assertRaises(IntegrityError):
            LocationCategory.objects.create(name = "SecondCategory", osm_key = "testkey", osm_value = "testvalue")

class LocationModelTests(TestCase):
    def test_duplicate_osm_source_constraint(self):
        cat = LocationCategory.objects.create(name = "TestCategory")
        Location.objects.create(name = "TestLocation1", address = "123 Test St", lat = 0.0, lng = 0.0, 
                                category = cat, source = "osm", osm_type = "n", osm_id = 123)
        with self.assertRaises(IntegrityError):
            Location.objects.create(name = "TestLocation2", address = "456 Test St", lat = 1.0, lng = 1.0, 
                                    category = cat, source = "osm", osm_type = "n", osm_id = 123)

    def test_tags(self):
        cat = LocationCategory.objects.create(name = "TestCategory", osm_key = "testkey", osm_value = "testvalue")
        loc = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0, 
                                       category = cat, tags = {"wheelchair": "yes", "toilets": "no"})
        loc.refresh_from_db()
        self.assertEqual(loc.tags["wheelchair"], "yes")
        