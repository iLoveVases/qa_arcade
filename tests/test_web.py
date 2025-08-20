def test_open_python(page):
    page.goto("https://www.python.org")
    assert "Python" in page.title()
