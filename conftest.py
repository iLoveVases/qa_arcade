import base64
import pytest
from pytest_html import extras as html_extras


def attach_screenshot_to_report(rep, item) -> None:
    """
    [Helper] if current phase failed, try to capture a screenshot from Playwright Page
    and attach it to pytest-html report via rep.extras.
    """

    # only when given phase was not successful helper continues:
    is_failed_phase = rep.failed and rep.when in {"setup", "call"}
    if not is_failed_phase:
        return

    # try to get standard page or manually attached one
    page = None
    if "page" in item.fixturenames:
        page = item.funcargs["page"] # <-- item.funcargs - dictionary of fixture names and values used in the test
    elif hasattr(item, "_attached_page"):
        page = item._attached_page
    # only when page is available hook continues:
    if page is None:
        return

    extras_list = list(getattr(rep, "extras", [])) # <-- if current extras in the report is None, use empty list

    try:
        b64 = base64.b64encode(page.screenshot(full_page=True)).decode("ascii")
        extras_list.append(html_extras.png(b64, name=f"{item.name} screenshot"))
    except Exception as e:
        extras_list.append(html_extras.text(f"Screenshot failed: {e}", name="screenshot-error"))

    # attach screenshot (or error) to report
    rep.extras = extras_list



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    [Hook] called by pytest for each phase of a test.
    We delegate the real work to attach_screenshot_to_report.
    """

    outcome = yield # <-- Let TC be executed first
    rep = outcome.get_result() # <-- rep - test report object
    attach_screenshot_to_report(rep, item)