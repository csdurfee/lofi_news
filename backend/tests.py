import unittest

from backend.strategy import rss

class RSSProcessingTest(unittest.TestCase):
    """
    these don't touch the database, so it's not using the django TestCase class.
    """
    def test_removes_links(self):
        test_str = "https://example.com for more details"
        cleaned = rss.remove_links(test_str)
        self.assertEqual(cleaned, " for more details")

    def test_fixes_no_space_after_periods(self):
        test_str = "Hello.Is it me you're looking.For"
        cleaned = rss.fix_no_space_after_periods(test_str)
        self.assertEqual(cleaned, "Hello. Is it me you're looking. For")

    def test_filters_baloney(self):
        mock_parsed = {}

        mock_parsed['text'] = "This contains content not supported so it is baloney even though it's long enough"
        baloney_result = rss.is_baloney(mock_parsed)
        self.assertEqual(baloney_result, True)

        mock_parsed['text'] = "This text is OK because it is long enough to be considered a good story"
        baloney_result = rss.is_baloney(mock_parsed)
        self.assertEqual(baloney_result, False)

        mock_parsed['text'] = "Too short"
        baloney_result = rss.is_baloney(mock_parsed)
        self.assertEqual(baloney_result, True)
