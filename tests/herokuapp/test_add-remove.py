from playwright.sync_api import Page, expect

URL = "https://the-internet.herokuapp.com/add_remove_elements/"

def add_button(page: Page):
    return page.get_by_role(role="button", name="Add Element")

def delete_buttons(page: Page):
    return page.get_by_role(role="button", name="Delete")


def test_add_remove_single(page: Page) -> None:
    """Adding a single element and removing it should restore the initial state."""
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    # init state
    expect(dels).to_have_count(0)
    expect(add).to_be_visible()

    # add and verify
    add.click()
    expect(dels).to_have_count(1)
    expect(dels.first).to_be_visible()
    expect(dels.first).to_have_text("Delete")

    # remove and verify if count is back to zero
    dels.first.click()
    expect(dels).to_have_count(0)
    expect(add).to_be_visible()


def test_add_three_remove_two(page: Page) -> None:
    """Adding three elements and removing two should leave exactly one."""
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    for _ in range(3):
        add.click()
    expect(dels).to_have_count(3)
    dels.first.click()
    expect(dels).to_have_count(2)

    dels.first.click()
    expect(dels).to_have_count(1)

    expect(dels.first).to_be_visible()
    expect(add).to_be_visible()


def test_add_many_then_remove_all(page: Page) -> None:
    """Adding N elements and then removing all should bring the count back to zero."""
    page.goto(URL)

    dels = delete_buttons(page)
    add = add_button(page)

    n = 50
    for _ in range(n):
        add.click()
    expect(dels).to_have_count(n)

    # remove all one by one
    for i in range(n):
        dels.first.click()
        expect(dels).to_have_count(n - i - 1)

    expect(dels).to_have_count(0)
    expect(add).to_be_visible()


def test_url_and_header_consistency(page: Page) -> None:
    """Verify URL, page heading and Add Element button consistency."""
    page.goto(URL)

    expect(page).to_have_url(URL)
    expect(page.get_by_role(role="heading", name="Add/Remove Elements")).to_be_visible()

    btn = add_button(page)
    expect(btn).to_be_enabled()
    expect(btn).to_have_text("Add Element")
