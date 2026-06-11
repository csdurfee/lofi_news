from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from frontend.models import UserProfile, user_profile_default_value

from datastar_py.django import DatastarResponse

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

class IndexViewTest(TestCase):
    fixtures = ["DataSource", "Story"]

    def test_index_returns_200_with_content(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 0)

class VoteViewTest(TestCase):
    def test_get_vote_returns_405(self):
        response = self.client.get("/vote/up/276")
        self.assertEqual(response.status_code, 405)

class MoreViewTest(TestCase):
    fixtures = ["DataSource", "Story"]

    def test_nonget_more_returns_405(self):
        response = self.client.post(reverse("more"))
        self.assertEqual(response.status_code, 405)

    def test_no_params_unsets_load_more(self):
        """
        response without datastar param or header should contain
        a datastar signal to stop loading more on the client side
        """

        response = self.client.get(reverse("more"))

        # ensure it's a datastar response and OK
        self.assertEqual(type(response), DatastarResponse)

        # ensure contains removal signal
        self.assertContains(response, "data: mode remove", status_code=200)

        # it's a streaming response, so we need to refetch
        response = self.client.get(reverse("more"))
        self.assertContains(response, "data: selector #load-more")


    def test_with_params_has_content(self):
        """
        send a request with the proper signal and ensure there's
        content loaded.
        """
        response = self.client.get("/more",
                                   {'datastar': "{\"lastId\":290}"},
                                   **{'HTTP_Datastar-Request': 'true'})

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Madison Square Garden")
