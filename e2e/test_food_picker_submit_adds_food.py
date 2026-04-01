def test_food_picker_submit_adds_food(page):
    page.goto("http://127.0.0.1:8000/app/meals/222/edit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url, f"Redirigido a login: {page.url}"

    food_search = page.locator("#food-search")
    food_list = page.locator("#food-list")
    food_preview = page.locator("#food-preview")
    quantity_input = page.locator("#food-quantity")
    add_button = page.locator("#btn-add-food")

    food_search.wait_for()
    food_search.fill("Pechuga Pollo Cocida")

    page.wait_for_timeout(700)

    first_result = food_list.locator("li").first
    first_result.wait_for()
    first_result.click()

    page.wait_for_timeout(700)

    assert food_preview.is_visible(), "El preview no se mostró tras seleccionar un alimento"

    quantity_input.wait_for()
    quantity_input.fill("250")

    page.wait_for_timeout(700)

    add_button.wait_for()
    add_button.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    assert "Pechuga Pollo Cocida" in page.content(), (
        "El alimento no apareció en la página después de agregarlo"
    )