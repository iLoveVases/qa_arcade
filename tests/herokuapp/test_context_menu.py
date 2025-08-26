import pytest
from playwright.sync_api import Browser, expect
import logging

logger = logging.getLogger(__name__)

URL = "https://the-internet.herokuapp.com/context_menu"
ALERT_TEXT = "You selected a context menu"


def _setup_page(browser: Browser, request: pytest.FixtureRequest, attach_page):
    ctx = browser.new_context()
    request.addfinalizer(ctx.close)
    page = attach_page(ctx.new_page())
    logger.info(f"|| Open URL: {URL}")
    resp = page.goto(URL)
    logger.info(f"|| Verify if page and heading are loaded")
    assert resp and resp.status == 200, f"Failed to load page, status: {resp.status if resp else 'no response'}"
    expect(page.get_by_role("heading", name="Context Menu")).to_be_visible()
    expect(page.locator("#hot-spot")).to_be_visible()
    return page


def test_right_click_opens_alert_with_expected_text(browser: Browser, attach_page, request: pytest.FixtureRequest):

    page = _setup_page(browser, request, attach_page)
    captured = {"msg": None}

    def _auto_accept(d):
        captured["msg"] = d.message
        d.accept()

    page.once("dialog", _auto_accept)

    logger.info("|| Press Right Mouse Button on hot spot")
    page.locator("#hot-spot").click(button="right", force=True, timeout=300)

    logger.info("|| Verify alert text and URL")
    assert captured["msg"] is not None, "Alert did not appeared"
    assert captured["msg"] == ALERT_TEXT, f"Unexpected alert text: {captured['msg']}"
    assert page.url == URL, f"Unexpected URL after alert: {page.url}"
