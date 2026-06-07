from django.test import TestCase
from django.urls import reverse

from datastar_py.django import DatastarResponse

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