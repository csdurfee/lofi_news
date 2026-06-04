from django.test import TestCase
from django.urls import reverse


class IndexViewTest(TestCase):
    def test_index_returns_200_with_content(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 0)
