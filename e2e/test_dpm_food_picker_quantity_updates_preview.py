def test_dpm_food_picker_quantity_updates_preview(page):
    page.goto("http://127.0.0.1:8000/app/dailyplans/122/meals/343/deepedit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url, f"Redirigido a login: {page.url}"

    food_search = page.locator("#food-search")
    food_list = page.locator("#food-list")
    quantity_input = page.locator("#food-quantity")
    qty_kcal = page.locator("#qty-kcal")

    food_search.fill("Pechuga Pollo Cocida")
    page.wait_for_timeout(700)

    food_list.locator("li").first.click()
    page.wait_for_timeout(700)

    initial_kcal = qty_kcal.text_content()

    quantity_input.fill("250")
    page.wait_for_timeout(700)

    updated_kcal = qty_kcal.text_content()

    assert initial_kcal != updated_kcal, "Las kcal no cambiaron al modificar la cantidad"