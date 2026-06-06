from django.test import TestCase
from django.urls import reverse


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
