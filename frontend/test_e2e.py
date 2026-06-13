import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import expect, sync_playwright


class E2ETestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()


class IndexPageTest(E2ETestCase):
    fixtures = ["DataSource", "Story", "User"]

    def test_has_stories(self):
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/")
        locator = page.locator("#main-content > article")
        expect(locator).to_have_count(10)

    def test_can_login(self):
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/accounts/login/")
        page.get_by_label("Username").fill("testing")
        page.get_by_label("Password").fill("obviouspw314")
        page.get_by_role("button", name="Log in").click()
        expect(page).to_have_url(f"{self.live_server_url}/")

        # saved button only shows when user is logged in.
        locator = page.locator("#saved-btn")
        expect(locator).to_have_text("Saved")

        # page.get_by_role("a", name="Log in").click()
        # expect(page).to_have_url("/accounts/login/")

    
