from playwright.sync_api import Page, expect


def test_login_reviewer(page: Page, fdorganizer_url: str) -> None:
    page.goto(f"{fdorganizer_url}/login")
    page.locator("#organisation-selector").select_option(label="Login of Example University [Local]")
    page.get_by_role("textbox", name="Username").fill("reviewer")
    page.get_by_role("textbox", name="Password").fill("reviewer")
    page.get_by_role("button", name="Login").click()
    expect(page.locator(".navbar-whoami")).to_contain_text("reviewer")
    expect(page.locator(".navbar-whoami")).to_contain_text("Example University")


def test_login_user(page: Page, fdorganizer_url: str) -> None:
    page.goto(f"{fdorganizer_url}/login")
    page.locator("#organisation-selector").select_option(label="Login of Example University [Local]")
    page.get_by_role("textbox", name="Username").fill("nutzer1")
    page.get_by_role("textbox", name="Password").fill("passwort1")
    page.get_by_role("button", name="Login").click()
    expect(page.locator(".navbar-whoami")).to_contain_text("nutzer1")
    expect(page.locator(".navbar-whoami")).to_contain_text("Example University")

