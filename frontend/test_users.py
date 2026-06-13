from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from frontend.models import UserProfile, user_profile_default_value


class UserProfileSignalTest(TestCase):
    def test_profile_created_with_user(self):
        user = User.objects.create_user(username='signaltest', password='pw123!')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_profile_usable(self):
        """
        Ensure user profile is created with default settings and works correctly.
        """
        user = User.objects.create_user(username='signaltest', password='pw123!')
        user_id = user.id
        self.assertDictEqual(user.profile.settings,
                             user_profile_default_value())

        user.profile.settings['testkey'] = 'testvalue'
        user.profile.save()

        user2 = User.objects.get(id=user_id)
        self.assertTrue(user2.profile.settings['testkey'], 'testvalue')

class LoginTest(TestCase):
    TEST_USER = "testing"
    CORRECT_PASSWORD = "obviouspw314"
    WRONG_PASSWORD = "somethingelse123"

    fixtures = ["User"]

    def test_login_with_correct_password(self):
        response = self.client.post('/accounts/login/', {
            'username': self.TEST_USER,
            'password': self.CORRECT_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        self.client.login(username=self.TEST_USER, password=self.CORRECT_PASSWORD)
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 302)

    def test_login_with_wrong_password(self):
        response = self.client.post('/accounts/login/', {
            'username': self.TEST_USER,
            'password': self.WRONG_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)


class JoinViewTest(TestCase):
    def test_get_join_returns_200(self):
        response = self.client.get(reverse("join"))
        self.assertEqual(response.status_code, 200)

    def test_valid_registration_redirects(self):
        response = self.client.post(reverse("join"), {
            'username': 'newuser',
            'password1': 'complexpassword99!',
            'password2': 'complexpassword99!',
        })
        self.assertEqual(response.status_code, 302)

    def test_mismatched_passwords_returns_200(self):
        response = self.client.post(reverse("join"), {
            'username': 'newuser',
            'password1': 'complexpassword99!',
            'password2': 'wrongpassword99!',
        })
        self.assertEqual(response.status_code, 200)
