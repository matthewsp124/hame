from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegisterViewTests(TestCase):

    def test_get_renders_empty_form(self):
        response = self.client.get(reverse('hame:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_post_valid_data_creates_user_and_redirects(self):
        response = self.client.post(reverse('hame:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SuperSecret123!',
            'password2': 'SuperSecret123!',
        })
        self.assertRedirects(response, reverse('hame:login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_post_duplicate_email_shows_error(self):
        User.objects.create_user(username='existinguser', email='dupe@example.com', password='SuperSecret123!')

        response = self.client.post(reverse('hame:register'), {
            'username': 'newuser',
            'email': 'dupe@example.com',
            'password1': 'SuperSecret123!',
            'password2': 'SuperSecret123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertFormError(response.context['user_form'], 'email', 'A user with that email address already exists.')

    def test_post_mismatched_passwords_shows_error(self):
        response = self.client.post(reverse('hame:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SuperSecret123!',
            'password2': 'DifferentPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='SuperSecret123!')

    def test_get_renders_login_form(self):
        response = self.client.get(reverse('hame:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_post_valid_credentials_redirects(self):
        response = self.client.post(reverse('hame:login'), {
            'username': 'testuser',
            'password': 'SuperSecret123!',
        })
        self.assertRedirects(response, reverse('hame:index'))

    def test_post_invalid_credentials_does_not_log_in(self):
        response = self.client.post(reverse('hame:login'), {
            'username': 'testuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_post_nonexistent_user_does_not_log_in(self):
        response = self.client.post(reverse('hame:login'), {
            'username': 'nonexistentuser',
            'password': 'SomePassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='SuperSecret123!')

    def test_logout_clear_session(self):
        self.client.login(username='testuser', password='SuperSecret123!')
        self.assertIn('_auth_user_id', self.client.session)

        self.client.post(reverse('hame:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)