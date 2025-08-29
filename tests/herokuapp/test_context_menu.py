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

@pytest.mark.parametrize(
    "button, expect_alert",
    [
        pytest.param("right",  True,  id="right-click"),
        pytest.param("left",   False, id="left-click"),
        pytest.param("middle", False, id="middle-click")
    ]
)
def test_context_menu_buttons(browser: Browser, attach_page, request: pytest.FixtureRequest,
                              button: str, expect_alert: bool):
    page = _setup_page(browser, request, attach_page)

    captured_msg = [None]
    def _auto_accept(d):
        captured_msg[0] = d.message
        d.accept()
    page.once("dialog", _auto_accept)

    logger.info(f"|| Click with {button} mouse button on hot spot")
    page.locator("#hot-spot").click(button=button, force=True, timeout=300)

    page.wait_for_timeout(200)

    if expect_alert:
        assert captured_msg[0] == ALERT_TEXT, f"Unexpected alert text: {captured_msg[0]}"
    else:
        assert captured_msg[0] is None, f"Unexpected alert appeared: {captured_msg[0]}"
    assert page.url == URL
