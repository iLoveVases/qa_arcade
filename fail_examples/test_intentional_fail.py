import pytest
from typing import Optional
from playwright.sync_api import Browser, Error, expect, Page
import logging


logger = logging.getLogger(__name__)

BASICAUTH_URL = "https://the-internet.herokuapp.com/basic_auth"
ADD_REMOVE_URL = "https://the-internet.herokuapp.com/add_remove_elements/"

def _format_value(value: str | None | bool) -> str:
    if value is None:
        return "None"
    elif value == "":
        return '""'
    elif value is True:
        return 'Login'
    elif value is False:
        return 'Rejected'
    else:
        return value

@pytest.fixture
# fixture to attach page to request for screenshot on failure
def attach_page(request):
    def _attach(p):
        request.node._attached_page = p
        return p
    return _attach

@pytest.mark.parametrize(
    "username,password,is_ok",
    [
        pytest.param("admin", "admin", False, id="valid credentials"),  # Intentional fail here (should be True)
        pytest.param("ADMIN", "ADMIN", True, id="uppercase"), # Intentional fail here (should be False)
        pytest.param("アドミン", "アドミン", True, id="unicode jp"), # Intentional fail here (should be False)

    ])
@pytest.mark.order(1)
def test_00_basic_auth_intentional_fail(browser: Browser,
                    username: Optional[str],
                    password: Optional[str],
                    is_ok: bool,
                    attach_page,
                    request: pytest.FixtureRequest) -> None:
    """To check various authentication combination"""
    logger.info(f"|| Open page: {BASICAUTH_URL}")
    logger.info(f"|| Basic Authentication Credentials:"
                f" Login:{_format_value(username)}, Password:{_format_value(password)}"
                f" [Expected: {_format_value(is_ok)}]")
    if username is None and password is None:
        context = browser.new_context()
    else:
        context = browser.new_context(http_credentials={"username": username, "password": password})

    request.addfinalizer(context.close) # ensure that context is closed after test
    page = attach_page(context.new_page()) # ensure that page is attached for screenshot on failure

    # correct credentials:
    if is_ok:
        resp = page.goto(BASICAUTH_URL)
        assert resp is not None, "No response from page.goto()"
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        logger.info("Check if body contains 'Congratulations'")
        expect(page.locator("body")).to_contain_text("Congratulations")

    # unauthorized page is rendered:
    elif username is None and password is None:
        try:
            # for headless testing mode:
            resp = page.goto(BASICAUTH_URL)
            assert resp is not None, "No response from page.goto()"
            assert resp.status == 401, f"Expected 401, got {resp.status}"
            logger.info("|| Check if body contains 'Not authorized'")
            expect(page.locator("body")).to_contain_text("Not authorized")
        except Error as e:
            # for headed testing mode:
            assert "ERR_INVALID_AUTH_CREDENTIALS" in str(e), f"Expected 'ERR_INVALID_AUTH_CREDENTIALS', got {e}"

    # invalid credentials:
    else:
        resp = page.goto(BASICAUTH_URL)
        assert resp is not None, "No response from page.goto()"
        assert resp.status == 401, f"Expected 401, got {resp.status}"
        logger.info("|| Check if body contains 'Not authorized'")
        expect(page.locator("body")).to_contain_text("Not authorized")






def add_button(page: Page):
    return page.get_by_role(role="button", name="Add Element")

def delete_buttons(page: Page):
    return page.get_by_role(role="button", name="Delete")

@pytest.mark.order(2)
def test_add_many_then_remove_all_intentional_fail(page: Page) -> None:
    """Adding N elements and then removing all should bring the count back to zero."""
    logger.info(f"|| Open page: {ADD_REMOVE_URL}")
    page.goto(ADD_REMOVE_URL)

    dels = delete_buttons(page)
    add = add_button(page)

    n = 100
    logger.info(f"|| Add {n} Delete_Buttons")
    for _ in range(n):
        add.click()
    expect(dels).to_have_count(n)

    logger.info(f"|| Remove all Delete_Buttons one by one")
    for i in range(n):
        dels.first.click()
        expect(dels).to_have_count(n - i - 1 + 1)  # Intentional fail here (should be n - i - 1)

    logger.info(f"|| Check if there is 0 Delete_Button remain and 1 Add_Button is visible")
    expect(dels).to_have_count(0)
    expect(add).to_have_count(1)
    expect(add).to_be_visible()