def test_food_picker_shows_results_when_typing(page):
    page.goto("http://127.0.0.1:8000/app/meals/222/edit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url, f"Redirigido a login: {page.url}"

    food_search = page.locator("#food-search")
    food_list = page.locator("#food-list")

    food_search.wait_for()
    assert food_search.is_visible()
    assert not food_list.is_visible()

    food_search.fill("Pechuga Pollo Cocida")

    page.wait_for_timeout(700)

    assert food_list.is_visible(), "La lista no se mostró después de escribir en el buscador"
