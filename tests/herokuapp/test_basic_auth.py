import pytest
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

@pytest.mark.parametrize(
    "username,password,is_ok",
    [
        pytest.param("admin", "admin", True, id="valid credentials (expected: login)"),
        # case sensitivity
        pytest.param("ADMIN", "ADMIN", True, id="uppercase (expected: reject)"),
        pytest.param("Admin", "admin", False, id="username capitalized (expected: reject)"),
        pytest.param("admin", "Admin", False, id="password capitalized (expected: reject)"),
        pytest.param("Admin", "Admin", False, id="both capitalized (expected: reject)"),
        pytest.param("adMin", "adMin", False, id="mixed case (expected: reject)"),
        # incorrect string / partially correct / Unicode
        pytest.param("admin", "wrong", False, id="wrong password (expected: reject)"),
        pytest.param("wrong", "admin", False, id="wrong username (expected: reject)"),
        pytest.param("wrong", "wrong", False, id="both wrong (expected: reject)"),
        pytest.param("admin123", "admin123", False, id="admin123/admin123 (expected: reject)"),
        pytest.param("admin", "admin123", False, id="admin/admin123 (expected: reject)"),
        pytest.param("admin123", "admin", False, id="admin123/admin (expected: reject)"),
        pytest.param("admiń", "admiń", False, id="unicode pl (expected: reject)"),
        pytest.param("アドミン", "アドミン", False, id="unicode jp (expected: reject)"),
        # empty / none
        pytest.param("", "", False, id="empty: ''/'' (expected: reject)"),
        pytest.param(None, None, False, id="no credentials (expected: reject)"),
        pytest.param("admin", "", False, id="admin/empty (expected: reject)"),
        pytest.param("", "admin", False, id="empty/admin (expected: reject)"),
        pytest.param("wrong", "", False, id="wrong/empty (expected: reject)"),
        pytest.param("", "wrong", False, id="empty/wrong (expected: reject)"),
        # symbols
        pytest.param(" ", " ", False, id="space/space (expected: reject)"),
        pytest.param("@dmin", "@dmin", False, id="@ as A(expected: reject)"),
        pytest.param(".", ".", False, id="dot/dot (expected: reject)"),
        pytest.param("?", "?", False, id="question/question (expected: reject)"),
        pytest.param("#####", "#####", False, id="hashes (expected: reject)"),
        pytest.param("*****", "*****", False, id="stars (expected: reject)"),
        # long
        pytest.param("admin"*20, "admin"*20, False, id="very long/very long (expected: reject)"),
        pytest.param("admin"*20, "", False, id="very long/empty (expected: reject)"),
        pytest.param("", "admin"*20, False, id="empty/very long (expected: reject)"),
    ])

def test_basic_auth(browser: Browser, username: str, password: str, is_ok: bool) -> None:
    """To check various authentication combination"""
    logger.info(f"|| Basic Authentication Case:"
                f" Login:{_format_value(username)}, Password:{_format_value(password)}"
                f" [Expected: {_format_value(is_ok)}]")

    if username is None and password is None:
        context = browser.new_context()
    else: context = browser.new_context(http_credentials={"username": username, "password": password})
    page = context.new_page()

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

    context.close()