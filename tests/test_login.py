from playwright.sync_api import Page, expect


def test_login_reviewer(page: Page, fdorganizer_url: str) -> None:
    page.goto(f"{fdorganizer_url}/login")
    page.locator("#organisation-selector").select_option(label="Login of Example University [Local]")
    page.locator("#auth-username").fill("reviewer")
    page.locator("#auth-password").fill("reviewer")
    page.get_by_role("button", name="Zustimmen und Einloggen").click()
    expect(page.locator(".navbar-whoami")).to_contain_text("reviewer")
    expect(page.locator(".navbar-whoami")).to_contain_text("Example University")


def test_login_user(page: Page, fdorganizer_url: str) -> None:
    page.goto(f"{fdorganizer_url}/login")
    page.locator("#organisation-selector").select_option(label="Login of Example University [Local]")
    page.locator("#auth-username").fill("nutzer1")
    page.locator("#auth-password").fill("passwort1")
    page.get_by_role("button", name="Zustimmen und Einloggen").click()
    expect(page.locator(".navbar-whoami")).to_contain_text("nutzer1")
    expect(page.locator(".navbar-whoami")).to_contain_text("Example University")

