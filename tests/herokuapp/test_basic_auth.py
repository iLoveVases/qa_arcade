import pytest
from typing import Optional
from playwright.sync_api import Browser, Error, expect
import logging

logger = logging.getLogger(__name__)

URL = "https://the-internet.herokuapp.com/basic_auth"

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
# hook to attach page to request for screenshot on failure
def attach_page(request):
    def _attach(p):
        request.node._attached_page = p
        return p
    return _attach

@pytest.mark.parametrize(
    "username,password,is_ok",
    [
        pytest.param("admin", "admin", True, id="valid credentials"),
        # case sensitivity
        pytest.param("ADMIN", "ADMIN", False, id="uppercase"),
        pytest.param("Admin", "admin", False, id="username capitalized"),
        pytest.param("admin", "Admin", False, id="password capitalized"),
        pytest.param("Admin", "Admin", False, id="both capitalized"),
        pytest.param("adMin", "adMin", False, id="mixed case"),
        # incorrect string / partially correct / Unicode
        pytest.param("admin", "wrong", False, id="wrong password"),
        pytest.param("wrong", "admin", False, id="wrong username"),
        pytest.param("wrong", "wrong", False, id="both wrong"),
        pytest.param("admin123", "admin123", False, id="admin123/admin123"),
        pytest.param("admin", "admin123", False, id="admin/admin123"),
        pytest.param("admin123", "admin", False, id="admin123/admin"),
        pytest.param("admiń", "admiń", False, id="unicode pl"),
        pytest.param("アドミン", "アドミン", False, id="unicode jp"),
        # empty / none
        pytest.param("", "", False, id="empty/empty"),
        pytest.param(None, None, False, id="no credentials"),
        pytest.param("admin", "", False, id="admin/empty"),
        pytest.param("", "admin", False, id="empty/admin"),
        pytest.param("wrong", "", False, id="wrong/empty"),
        pytest.param("", "wrong", False, id="empty/wrong"),
        # symbols
        pytest.param(" ", " ", False, id="space/space"),
        pytest.param("@dmin", "@dmin", False, id="@dmin/@dmin"),
        pytest.param(".", ".", False, id="dot/dot"),
        pytest.param("?", "?", False, id="question/question"),
        pytest.param("#####", "#####", False, id="hashes"),
        pytest.param("*****", "*****", False, id="stars"),
        # long
        pytest.param("admin" * 20, "admin" * 20, False, id="very long/very long"),
        pytest.param("admin" * 20, "", False, id="very long/empty"),
        pytest.param("", "admin" * 20, False, id="empty/very long"),
    ])

def test_basic_auth(browser: Browser,
                    username: Optional[str],
                    password: Optional[str],
                    is_ok: bool,
                    attach_page,
                    request: pytest.FixtureRequest) -> None:
    """To check various authentication combination"""
    logger.info(f"|| Open page: {URL}")
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
        resp = page.goto(URL)
        assert resp is not None, "No response from page.goto()"
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        logger.info("Check if body contains 'Congratulations'")
        expect(page.locator("body")).to_contain_text("Congratulations")

    # unauthorized page is rendered:
    elif username is None and password is None:
        try:
            # for headless testing mode:
            resp = page.goto(URL)
            assert resp is not None, "No response from page.goto()"
            assert resp.status == 401, f"Expected 401, got {resp.status}"
            logger.info("|| Check if body contains 'Not authorized'")
            expect(page.locator("body")).to_contain_text("Not authorized")
        except Error as e:
            # for headed testing mode:
            assert "ERR_INVALID_AUTH_CREDENTIALS" in str(e), f"Expected 'ERR_INVALID_AUTH_CREDENTIALS', got {e}"

    # invalid credentials:
    else:
        resp = page.goto(URL)
        assert resp is not None, "No response from page.goto()"
        assert resp.status == 401, f"Expected 401, got {resp.status}"
        logger.info("|| Check if body contains 'Not authorized'")
        expect(page.locator("body")).to_contain_text("Not authorized")