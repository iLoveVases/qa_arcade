import pytest
from playwright.sync_api import Browser, expect
import logging

logger = logging.getLogger(__name__)
URL = "https://the-internet.herokuapp.com/checkboxes"


def _setup_page(browser: Browser, request: pytest.FixtureRequest, attach_page):
    ctx = browser.new_context()
    request.addfinalizer(ctx.close)
    page = attach_page(ctx.new_page())

    logger.info(f"|| Open URL: {URL}")
    resp = page.goto(URL)
    logger.info("|| Verify if page and heading are loaded")
    assert resp and resp.status == 200, f"Failed to load page, status: {resp.status}"
    expect(page.get_by_role("heading", name="Checkboxes")).to_be_visible()
    expect(page.locator("input[type='checkbox']")).to_have_count(2)
    return page


@pytest.mark.parametrize(
    "index, target_checked, mode",
    [
        pytest.param(0, True,  "direct_set", id="cb1_set_true_direct_set"),
        pytest.param(0, False, "direct_set", id="cb1_set_false_direct_set"),
        pytest.param(1, True,  "direct_set", id="cb2_set_true_direct_set"),
        pytest.param(1, False, "direct_set", id="cb2_set_false_direct_set"),

        pytest.param(0, True,  "mouse", id="cb1_set_true_mouse"),
        pytest.param(0, False, "mouse", id="cb1_set_false_mouse"),
        pytest.param(1, True,  "mouse", id="cb2_set_true_mouse"),
        pytest.param(1, False, "mouse", id="cb2_set_false_mouse"),
    ]
)
# Two modes are tested:
# - direct_set: force checkbox into desired state with set_checked()
# - mouse: simulate user action with click()
def test_checkboxes(
    browser: Browser, attach_page, request: pytest.FixtureRequest, index: int, target_checked: bool, mode: str) -> None:

    page = _setup_page(browser, request, attach_page)
    cb = page.locator("input[type='checkbox']").nth(index)
    state = "checked" if target_checked else "unchecked"

    logger.info(f"|| Checkbox {index+1} | initial={"checked" if cb.is_checked() else "unchecked"} | mode={mode} |"
                f" target={state}")

    if mode == "direct_set":
        logger.info(f"|| set_checked({state}) on checkbox {index+1}")
        cb.set_checked(target_checked, timeout=500, force=True)

    elif mode == "mouse":
        opposite = not target_checked
        logger.info(f"|| set_checked({opposite}) on checkbox {index+1} before mouse click")
        cb.set_checked(opposite, timeout=1000, force=True)
        logger.info(f"|| click() on checkbox {index+1} to reach target={state}")
        cb.click(timeout=500)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if target_checked:
        expect(cb).to_be_checked()
    else:
        expect(cb).not_to_be_checked()

    logger.info(f"|| checkbox {index+1} final_state={"checked" if cb.is_checked() else "unchecked"}")
    assert page.url == URL, f"Unexpected URL: {page.url}"
