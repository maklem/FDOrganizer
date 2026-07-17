import re
from playwright.sync_api import Page, expect


def test_solo_reviewer_happy_path(page: Page, fdorganizer_url: str) -> None:
    page.goto(f"{fdorganizer_url}/login")

    # Log in
    page.locator("#organisation-selector").select_option(label="Login of Example University [Local]")
    page.get_by_role("textbox", name="Username").fill("reviewer")
    page.get_by_role("textbox", name="Password").fill("reviewer")
    page.get_by_role("button", name="Login").click()

    # Create Package
    page.get_by_role("link", name="Editor").click()
    page.get_by_role("button", name="+ Add project").click()
    page.get_by_role("textbox", name="Choose a name:").fill("Testproject")
    page.get_by_role("button", name="Create project").click()
    page.get_by_role("button", name="Abort").click()

    # Upload a file
    page.get_by_text("Testproject", exact=True).click()
    page.get_by_role("button", name="Edit project").click()
    page.locator(".add-files").click()
    page.get_by_label("", exact=True).set_input_files("tests/dummy.dat")
    page.get_by_role("button", name="Start Upload").click()
    page.get_by_role("button", name="Yes").click()

    # Set mandatory metadata
    page.get_by_role("link", name="Archive").click()
    page.get_by_role("button").nth(2).click() # "The Book"
    page.get_by_role("heading", name="Required").click()
    page.get_by_label("Type of identifier").select_option("resourceIdentifierNotApplicable")
    page.get_by_label("Creator").select_option("personal")
    page.get_by_label("NamenameORCiD---").select_option("name")
    page.get_by_role("textbox", name="Last Name").fill("Test")
    page.get_by_role("textbox", name="First Name").fill("Profile")
    page.get_by_label("Affiliated").select_option("name")
    page.get_by_role("textbox", name="Name", exact=True).fill("Testiversity")
    page.get_by_label("Published resource?").select_option("false")
    page.get_by_label("Type of title").select_option("mainTitle")
    page.get_by_role("textbox", name="Title").fill("The way of testing")
    page.get_by_label("General resource").select_option("workflow")
    page.get_by_label("Type of description").select_option("descriptionNotApplicable")
    page.get_by_role("button", name="Save").click()

    # set legal fields
    page.get_by_role("button").nth(4).click() # "The Wheel"
    page.get_by_role("button", name="Legal").click()
    page.get_by_role("checkbox", name="I have read and understood").check()
    page.get_by_role("checkbox", name="I attest that the cost for").check()
    page.get_by_placeholder("yy").fill("5")
    page.get_by_role("checkbox", name="I attest that all personal").check()
    page.get_by_role("radio", name="All existing personal data in this package was removed").check()
    page.get_by_role("button", name="Save").click()

    # hand in for review
    page.get_by_text("Testproject").click()
    page.get_by_role("button", name="Submit package").click()

    # accept package for archive
    page.get_by_role("link", name="Review").click()
    page.get_by_text("Testproject").click()
    page.get_by_role("button", name="Accept for Archive").click()

    # assert download button
    page.get_by_text("Accepted").click()
    page.get_by_text("Testproject").click()
    expect(page.locator("#app-container")).to_contain_text("Download Package")
