def test_login_and_save_state(page):
    page.goto("http://127.0.0.1:8000/accounts/login/")

    # Ajusta estos selectores a tu formulario real
    page.locator('input[name="login"]').fill("DonFelipes@gmail.com")
    page.locator('input[name="password"]').fill("12341234")
    page.get_by_role("button").click()

    page.wait_for_load_state("networkidle")

    # Verifica que NO sigues en login
    assert "/accounts/login/" not in page.url

    # Verifica acceso real a una ruta protegida
    page.goto("http://127.0.0.1:8000/app/dailyplans/122/meals/343/deepedit/")
    page.wait_for_load_state("networkidle")

    assert "/accounts/login/" not in page.url

    page.context.storage_state(path="e2e/auth/state.json")