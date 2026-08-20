from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from hame.models import LocationCategoryKey, LocationCategory, Location, UserEntry
from hame.forms import UserEntryForm

# helper function for setup
def make_location():
    key = LocationCategoryKey.objects.create(osm_key = "amenity")
    category = LocationCategory.objects.create(key = key, osm_value = "restaurant")
    location = Location.objects.create(name = "Testaurant", address = "123 Test St", lat = 56.0, lng = 3.0)
    location.categories.add(category)
    return location

class UserEntryFormTests(TestCase):
    def setUp(self):
        self.location = make_location()

    def test_valid_form_all_fields(self):
        form = UserEntryForm(data = {
            'wheelchair': 'Y',
            'auto_doors': 'N',
            'level_floor_or_lift': 'U',
            'accessible_toilet': 'Y',
            'parking': 'NA',
            'disabled_bay': 'U',
            'braille_signage': 'U',
            'hearing_loop': 'U',
            'quiet_space': 'U',
            'tactile_paving': 'U',
            'nonvisual_crossing_cues': 'U',
            'surface_type': 'P',
            'gradient': 'F',
            'text_body': 'This is a test review.',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_excludes_auto_filled_fields(self):
        form = UserEntryForm()
        for field in ('user', 'location', 'created_at'):
            self.assertNotIn(field, form.fields)

class AddReviewViewTests(TestCase):
    def setUp(self):
        self.location = make_location()
        self.user = User.objects.create_user(username = 'testuser', password = 'testpass123!')
        self.url = reverse('hame:add_review', args = [self.location.id])

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_get_shows_form(self):
        self.client.login(username = 'testuser', password = 'testpass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_valid_post_creates_entry_and_redirects(self):
        self.client.login(username = 'testuser', password = 'testpass123!')
        response = self.client.post(self.url, data = {
            'wheelchair': 'Y',
            'auto_doors': 'U',
            'level_floor_or_lift': 'U',
            'accessible_toilet': 'U',
            'parking': 'U',
            'disabled_bay': 'U',
            'braille_signage': 'U',
            'hearing_loop': 'U',
            'quiet_space': 'U',
            'tactile_paving': 'U',
            'nonvisual_crossing_cues': 'U',
            'surface_type': 'U',
            'gradient': 'U',
            'text_body': 'This is another test review.',
        })
        self.assertRedirects(response, reverse('hame:index'))

        entry = UserEntry.objects.get(location = self.location)
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.wheelchair, 'Y')
        self.assertEqual(entry.text_body, 'This is another test review.')

    def test_invalid_post_does_not_create_entry(self):
        self.client.login(username = 'testuser', password = 'testpass123!')
        response = self.client.post(self.url, data = {'wheelchair': 'InvalidChoice'})
        self.assertEqual(response.status_code, 200)  # form re-rendered without redirect
        self.assertEqual(UserEntry.objects.count(), 0)  # no entry created

    def test_404_for_nonexistent_location(self):
        self.client.login(username = 'testuser', password = 'testpass123!')
        bad_url = reverse('hame:add_review', args = [999999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)

class LocationReviewsViewTests(TestCase):
    def setUp(self):
        self.location = make_location()
        self.user = User.objects.create_user(username = 'testuser', password = 'testpass123!')
        self.url = reverse('hame:location_reviews', args = [self.location.id])

    # helper function to create a default UserEntry for testing
    def make_entry(self, **arg_overrides):
        defaults = dict(location = self.location, user = self.user, text_body = '')
        defaults.update(arg_overrides)
        return UserEntry.objects.create(**defaults)

    def test_no_entries_returns_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['stats'], [])
        self.assertEqual(data['reviews'], [])

    def test_unknown_not_counted(self):
        self.make_entry(wheelchair = 'Y')
        self.make_entry(wheelchair = 'N')
        self.make_entry(wheelchair = 'N')
        self.make_entry(wheelchair = 'U')

        response = self.client.get(self.url)
        data = response.json()
        wheelchair_stat = next(s for s in data['stats'] if s['label'] == 'Wheelchair accessible entrance')

        self.assertEqual(wheelchair_stat['total'], 3)
        self.assertEqual(wheelchair_stat['yes_pct'], 33)
        self.assertEqual(wheelchair_stat['no_pct'], 67)

    def test_field_excluded_if_all_answers_unknown(self):
        self.make_entry(wheelchair = 'U')
        self.make_entry(wheelchair = 'U')

        response = self.client.get(self.url)
        data = response.json()
        labels = [s['label'] for s in data['stats']]

        self.assertNotIn('Wheelchair accessible entrance', labels)

    def test_only_entries_with_text_body_in_reviews(self):
        self.make_entry(wheelchair = 'Y', text_body = 'First review')
        self.make_entry(wheelchair = 'N', text_body = '')

        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(len(data['reviews']), 1)
        self.assertEqual(data['reviews'][0]['text_body'], 'First review')

    def test_reviews_ordered_chronologically(self):
        first = self.make_entry(text_body = 'First review')
        second = self.make_entry(text_body = 'Second review')

        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(data['reviews'][0]['text_body'], 'Second review')  # most recent first
        self.assertEqual(data['reviews'][1]['text_body'], 'First review')

    
