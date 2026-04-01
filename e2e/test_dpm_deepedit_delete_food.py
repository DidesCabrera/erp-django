def test_dpm_deepedit_delete_food_removes_row(page):
    page.goto("http://127.0.0.1:8000/app/dailyplans/122/meals/343/deepedit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url, f"Redirigido a login: {page.url}"

    edit_buttons = page.locator(".edit-food-btn")
    initial_count = edit_buttons.count()

    assert initial_count > 0, "No hay filas para borrar en la tabla de foods"

    first_row = page.locator("table.table-foods--dpm tbody tr").first
    first_row.wait_for()

    delete_button = first_row.locator('button[type="submit"]').first
    delete_button.wait_for()
    delete_button.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    assert "/deepedit/" in page.url, f"La vista no volvió a deepedit: {page.url}"

    updated_count = page.locator(".edit-food-btn").count()

    assert updated_count == initial_count - 1, (
        f"La cantidad de filas no disminuyó tras borrar. "
        f"Antes: {initial_count}, después: {updated_count}"
    )