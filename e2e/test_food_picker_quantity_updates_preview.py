def test_food_picker_quantity_updates_preview(page):
    page.goto("http://127.0.0.1:8000/app/meals/222/edit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url, f"Redirigido a login: {page.url}"

    food_search = page.locator("#food-search")
    food_list = page.locator("#food-list")
    quantity_input = page.locator("#food-quantity")
    qty_kcal = page.locator("#qty-kcal")

    food_search.wait_for()
    food_search.fill("Pechuga Pollo Cocida")

    page.wait_for_timeout(700)

    first_result = food_list.locator("li").first
    first_result.wait_for()
    first_result.click()

    page.wait_for_timeout(700)

    initial_kcal = qty_kcal.text_content()

    quantity_input.wait_for()
    quantity_input.fill("250")

    page.wait_for_timeout(700)

    updated_kcal = qty_kcal.text_content()

    assert initial_kcal is not None and initial_kcal.strip() != ""
    assert updated_kcal is not None and updated_kcal.strip() != ""
    assert initial_kcal != updated_kcal, "Las kcal no cambiaron al modificar la cantidad"