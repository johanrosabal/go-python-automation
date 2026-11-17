"""
Preconditions Fixtures for Demo Application.

Provides reusable role-based authentication fixtures that transition the browser
into an authenticated state on the Inventory Page before executing business tests.

Supports both:
- Isolation Mode (persistent_session = False, default): Fresh browser per test.
- Persistence Mode (persistent_session = True): Shared browser across class tests.
  Automatically reuses active session if role matches, or performs an identity switch
  (clearing cookies/storage) if a different role is requested.
"""
import pytest
import allure


def authenticate_as_role(app, role: str) -> None:
    """
    Session-aware authentication helper.
    
    1. If the browser is ALREADY authenticated with the requested role on Inventory:
       Reuses the active session (preserving state and avoiding redundant logins).
    2. If the browser is authenticated with a DIFFERENT role:
       Performs an identity switch (clearing session cookies/storage).
    3. If the browser is not authenticated:
       Navigates to the login page and logs in with the role's credentials from YAML.
    """
    current_role = getattr(app, "_current_authenticated_role", None)

    # 1. Re-use existing session if role matches and browser is on Inventory
    if current_role == role:
        try:
            if "/inventory.html" in app.driver.current_url:
                with allure.step(f"Precondition: Reusing active session for role '{role}'"):
                    return
        except Exception:
            pass

    # 2. Identity Switch: If currently logged in as a different role, reset session
    if current_role and current_role != role:
        with allure.step(f"Precondition: Switching identity from '{current_role}' to '{role}'"):
            try:
                app.driver.delete_all_cookies()
                try:
                    app.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
                except Exception:
                    pass
            except Exception:
                pass

    # 3. Authenticate with requested role credentials from environment config
    username = app.get_username(role)
    password = app.get_password(role)

    with allure.step(f"Precondition: Authenticate session as role '{role}' ({username})"):
        login_page = app.login_page.open()
        login_page.login(username=username, password=password)
        app.inventory_page.wait_until_loaded()
        app._current_authenticated_role = role


@pytest.fixture
def as_standard_user(app):
    """Precondition: Authenticates as 'standard' user on Inventory Page."""
    authenticate_as_role(app, "standard")
    return app


@pytest.fixture
def as_problem_user(app):
    """Precondition: Authenticates as 'problem' user (known UI/image defects)."""
    authenticate_as_role(app, "problem")
    return app


@pytest.fixture
def as_performance_glitch_user(app):
    """Precondition: Authenticates as 'performance' glitch user (simulated latency)."""
    authenticate_as_role(app, "performance")
    return app


@pytest.fixture
def as_error_user(app):
    """Precondition: Authenticates as 'error' user (broken click handlers / cart issues)."""
    authenticate_as_role(app, "error")
    return app


@pytest.fixture
def as_visual_user(app):
    """Precondition: Authenticates as 'visual' user (visual regression shifts)."""
    authenticate_as_role(app, "visual")
    return app


@pytest.fixture
def logged_in_session(app):
    """Backwards-compatible generic pre-condition using the default role."""
    authenticate_as_role(app, app.default_role or "standard")
    return app
