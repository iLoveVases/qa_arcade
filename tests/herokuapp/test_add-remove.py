import logging
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

URL = "https://the-internet.herokuapp.com/add_remove_elements/"


def add_button(page: Page):
    return page.get_by_role(role="button", name="Add Element")

def delete_buttons(page: Page):
    return page.get_by_role(role="button", name="Delete")


def test_add_remove_single(page: Page) -> None:
    """Adding a single element and removing it should restore the initial state."""
    logger.info(f"|| Open page: {URL}")
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    logger.info(f"|| Initial state: 0 Delete_Button, Add button visible")
    expect(dels).to_have_count(0)
    expect(add).to_be_visible()

    logger.info(f"|| Click Add_Button and verify 1 Delete_Buttons appears")
    add.click()
    expect(dels).to_have_count(1)
    expect(dels.first).to_be_visible()
    expect(dels.first).to_have_text("Delete")

    logger.info(f"|| Click Delete_Button and verify 0 Delete_Buttons remains")
    dels.first.click()
    expect(dels).to_have_count(0)
    expect(add).to_be_visible()


def test_url_and_header_consistency(page: Page) -> None:
    """Verify URL, page heading and Add Element button consistency."""
    logger.info(f"|| Open page: {URL}")
    page.goto(URL)

    logger.info(f"|| Verify page heading")
    expect(page).to_have_url(URL)
    expect(page.get_by_role(role="heading", name="Add/Remove Elements")).to_be_visible()

    logger.info(f"|| Verify Add_Button properties")
    add = add_button(page)
    expect(add).to_be_enabled()
    expect(add).to_have_text("Add Element")

    logger.info(f"|| Verify Delete_Button properties")
    add.click()
    delete = delete_buttons(page)
    expect(delete).to_be_enabled()
    expect(delete).to_have_text("Delete")


def test_add_three_remove_two(page: Page) -> None:
    """Adding three elements and removing two should leave exactly one."""
    logger.info(f"|| Open page: {URL}")
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    logger.info(f"|| Add 3 elements, expect 3 Delete_Buttons")

    for _ in range(3):
        add.click()
    expect(dels).to_have_count(3)

    logger.info(f"|| Click Delete_Button once, expect 2 Delete_Buttons and 1 Add_Button remain")
    dels.first.click()
    expect(dels).to_have_count(2)
    expect(add).to_have_count(1)

    logger.info(f"|| Click Delete_Button once, expect 1 Delete_Button and 1 Add_Button remain")
    dels.first.click()
    expect(dels).to_have_count(1)
    expect(add).to_have_count(1)

    logger.info(f"|| Verify that last Delete_Button is visible and Add_Button is still visible")
    expect(dels.first).to_be_visible()
    expect(add).to_be_visible()


def test_add_many_then_remove_all(page: Page) -> None:
    """Adding N elements and then removing all should bring the count back to zero."""
    logger.info(f"|| Open page: {URL}")
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    n = 50
    logger.info(f"|| Add {n} Delete_Buttons")
    for _ in range(n):
        add.click()
    expect(dels).to_have_count(n)

    logger.info(f"|| Remove all Delete_Buttons one by one")
    for i in range(n):
        dels.first.click()
        expect(dels).to_have_count(n - i - 1)

    logger.info(f"|| Check if there is 0 Delete_Button remain and 1 Add_Button is visible")
    expect(dels).to_have_count(0)
    expect(add).to_have_count(1)
    expect(add).to_be_visible()



