from pathlib import Path

import pytest


STATE_FILE = Path("e2e/auth/state.json")


@pytest.fixture
def context(browser, request):
    test_file = str(request.node.fspath)

    # El test de login debe correr sin sesión previa
    if "test_login_and_save_state.py" in test_file:
        context = browser.new_context()
        yield context
        context.close()
        return

    if not STATE_FILE.exists():
        pytest.fail(
            "Falta e2e/auth/state.json. Primero corre el test de login para guardar la sesión."
        )

    context = browser.new_context(storage_state=str(STATE_FILE))
    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()