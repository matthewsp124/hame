from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User

from hame.models import LocationCategoryKey, LocationCategory, Location, UserEntry

class LocationCategoryKeyModelTests(TestCase):
    def test_str_method(self):
        key = LocationCategoryKey.objects.create(osm_key = "amenity")
        self.assertEqual(str(key), "amenity")

    def test_unique_osm_key_constraint(self):
        LocationCategoryKey.objects.create(osm_key = "amenity")
        with self.assertRaises(IntegrityError):
            LocationCategoryKey.objects.create(osm_key = "amenity")

class LocationCategoryModelTests(TestCase):
    def setUp(self):
        self.key = LocationCategoryKey.objects.create(osm_key = "amenity")

    def test_str_method(self):
        category = LocationCategory.objects.create(key = self.key, osm_value = "restaurant")
        self.assertEqual(str(category), "amenity=restaurant")

    def test_duplicate_key_value_constraint(self):
        LocationCategory.objects.create(key = self.key, osm_value = "restaurant")
        with self.assertRaises(IntegrityError):
            LocationCategory.objects.create(key = self.key, osm_value = "restaurant")

    def test_same_value_different_key(self):
        other_key = LocationCategoryKey.objects.create(osm_key = "shop")
        LocationCategory.objects.create(key = self.key, osm_value = "restaurant")
        LocationCategory.objects.create(key = other_key, osm_value = "restaurant")  # should not raise an error

    def test_null_key(self):
        category = LocationCategory.objects.create(key = self.key, osm_value = "cafe")
        self.key.delete()
        category.refresh_from_db()
        self.assertIsNone(category.key)

class LocationModelTests(TestCase):
    def setUp(self):
        self.key = LocationCategoryKey.objects.create(osm_key = "amenity")
        self.category = LocationCategory.objects.create(key = self.key, osm_value = "restaurant")

    def test_str_method_uses_name(self):
        loc = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0)
        self.assertEqual(str(loc), f"{loc.osm_id} - {loc.name} ({loc.lat}, {loc.lng})")

    def test_str_method_uses_address_when_no_name(self):
        loc = Location.objects.create(address = "123 Test St", lat = 0.0, lng = 0.0)
        self.assertEqual(str(loc), f"{loc.osm_id} - {loc.address} ({loc.lat}, {loc.lng})")

    def test_category_assignment(self):
        loc = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0)
        loc.categories.add(self.category)
        self.assertIn(self.category, loc.categories.all())

    def test_duplicate_osm_type_and_id_constraint(self):
        Location.objects.create(name = "TestLocation1", address = "123 Test St", lat = 0.0, lng = 0.0, 
                                       osm_type = "n", osm_id = 123)
        with self.assertRaises(IntegrityError):
            Location.objects.create(name = "TestLocation2", address = "456 Test St", lat = 1.0, lng = 1.0, 
                                    osm_type = "n", osm_id = 123)

    def test_same_id_different_type_allowed(self):
        Location.objects.create(name = "TestLocation1", address = "123 Test St", lat = 0.0, lng = 0.0, 
                                       osm_type = "n", osm_id = 123)
        Location.objects.create(name = "TestLocation2", address = "456 Test St", lat = 1.0, lng = 1.0, 
                                osm_type = "w", osm_id = 123)  # should not raise an error

    def test_tags_default_empty(self):
        loc = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0)
        self.assertEqual(loc.tags, {})

    def test_tags_storage_and_retrieval(self):
        loc = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0, 
                                       tags = {"wheelchair": "yes", "toilets": "no"})
        loc.refresh_from_db()
        self.assertEqual(loc.tags["wheelchair"], "yes")
        self.assertEqual(loc.tags["toilets"], "no")

    def test_coords_required(self):
        with self.assertRaises(IntegrityError):
            Location.objects.create(name = "NoCoords")

class UserEntryModelTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name = "TestLocation", address = "123 Test St", lat = 0.0, lng = 0.0)
        self.user = User.objects.create_user(username = "testuser", password = "12345")

    def test_create_user_entry_with_defaults(self):
        entry = UserEntry.objects.create(location = self.location, user = self.user)

        self.assertEqual(entry.location, self.location)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.wheelchair, 'U')
        self.assertEqual(entry.auto_doors, 'U')
        self.assertEqual(entry.level_floor_or_lift, 'U')
        self.assertEqual(entry.accessible_toilet, 'U')
        self.assertEqual(entry.parking, 'U')
        self.assertEqual(entry.disabled_bay, 'U')
        self.assertEqual(entry.braille_signage, 'U')
        self.assertEqual(entry.hearing_loop, 'U')
        self.assertEqual(entry.quiet_space, 'U')
        self.assertEqual(entry.tactile_paving, 'U')
        self.assertEqual(entry.nonvisual_crossing_cues, 'U')
        self.assertEqual(entry.surface_type, 'U')
        self.assertEqual(entry.gradient, 'U')
        self.assertIsNone(entry.text_body)
        self.assertIsNotNone(entry.created_at)

    def test_location_entry_count(self):
        UserEntry.objects.create(location = self.location, user = self.user)
        UserEntry.objects.create(location = self.location, user = self.user)
        self.assertEqual(self.location.user_entries.count(), 2)

    def test_null_user_allowed(self):
        entry = UserEntry.objects.create(location = self.location, user = None)
        self.assertIsNone(entry.user)

    def test_user_deletion_protected(self):
        UserEntry.objects.create(location = self.location, user = self.user)
        with self.assertRaises(IntegrityError):
            self.user.delete()

    def test_location_deletion_cascades(self):
        UserEntry.objects.create(location = self.location, user = self.user)
        self.location.delete()
        self.assertEqual(UserEntry.objects.count(), 0)