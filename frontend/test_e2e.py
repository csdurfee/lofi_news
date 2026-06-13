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

    def _login_helper(self):
        page = self.browser.new_page()

        page.goto(f"{self.live_server_url}/accounts/login/")
        page.get_by_label("Username").fill("testing")
        page.get_by_label("Password").fill("obviouspw314")
        page.get_by_role("button", name="Log in").click()
        return page

    def test_has_stories(self):
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/")
        locator = page.locator("#main-content > article")
        expect(locator).to_have_count(10)

    def test_can_login(self):
        page = self._login_helper()

        expect(page).to_have_url(f"{self.live_server_url}/")

        # saved button only shows when user is logged in.
        locator = page.locator("#saved-btn")
        expect(locator).to_have_text("Saved")

    def test_infinite_scroll(self):
        """
        this test ensures that when someone scrolls to the bottom
        of the page, it will load more content.
        """
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/")

        page.locator("#load-more").scroll_into_view_if_needed()
        articles = page.locator("#main-content > article")
        expect(articles).to_have_count(20)

        # 2nd infinite scrolll page.
        page.locator("#load-more").scroll_into_view_if_needed()
        articles = page.locator("#main-content > article")
        expect(articles).to_have_count(30)


    def test_save_button(self):
        page = self._login_helper()
        #page.screenshot(path="test_screenshots/test_vote_before.png")

        # save a couple stories
        page.locator(".save-btn").nth(1).click()

        page.locator(".save-btn").nth(3).click()

        page.locator(".save-btn").nth(4).click()

        # goto saved page, see if they're there
        # TODO: this could be tighter
        page.goto(f"{self.live_server_url}/saved")
        page.screenshot(path="test_screenshots/test_vote_after.png")
        locator = page.locator("#main-content > article")
        expect(locator).to_have_count(3)
