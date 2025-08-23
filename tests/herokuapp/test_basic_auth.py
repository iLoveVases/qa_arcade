import pytest
from playwright.sync_api import Browser, Error, expect

URL = "https://the-internet.herokuapp.com/basic_auth"

@pytest.mark.parametrize(
    "username,password,is_ok",
    [
        ("admin", "admin", True),
        # case sensitivity:
        ("ADMIN", "ADMIN", False),
        ("Admin", "admin", False),
        ("admin", "Admin", False),
        ("Admin", "Admin", False),
        ("adMin", "adMin", False),
        # incorrect string/partially correct/Unicode:
        ("admin", "wrong", False),
        ("wrong", "admin", False),
        ("wrong", "wrong", False),
        ("admin123", "admin123", False),
        ("admin", "admin123", False),
        ("admin123", "admin", False),
        ("admiń", "admiń", False),
        ("アドミン", "アドミン", False), # admin in Japanese
        # empty:
        ("", "", False),
        (None, None, False), #
        ("admin", "", False),
        ("wrong", "", False),
        ("", "admin", False),
        ("", "wrong", False),
        # symbols:
        (" ", " ", False),
        ("@dmin", "@dmin", False),
        (".", ".", False),
        ("?", "?", False),
        ("#####", "#####", False),
        ("*****", "*****", False),
        # long:
        ("admin"*20, "admin"*20, False),
        ("admin"*20, "", False),
        ("", "admin"*20, False),

    ],
)
def test_basic_auth(browser: Browser, username: str, password: str, is_ok: bool) -> None:
    """
    To check various authentication combination
    """
    if username is None and password is None:
        context = browser.new_context()
    else:
        context = browser.new_context(http_credentials={"username": username, "password": password})
    page = context.new_page()

    if is_ok:
        resp = page.goto(URL)
        assert resp is not None and resp.status == 200
        expect(page.locator("body")).to_contain_text("Congratulations")


    elif username is None and password is None:
        # unauthorized page is rendered
        with pytest.raises(Error) as err:
            page.goto(URL)
        assert "ERR_INVALID_AUTH_CREDENTIALS" in str(err.value)

    else:
        # invalid credentials:
        resp = page.goto(URL)
        assert resp is not None and resp.status == 401
        expect(page.locator("body")).to_contain_text("Not authorized")

    context.close()