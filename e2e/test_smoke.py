def test_homepage_loads(page):
    page.goto("http://127.0.0.1:8000/")
    assert page.title() is not None