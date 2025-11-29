
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the index.html file directly from the file system
        file_path = os.path.abspath('index.html')
        page.goto(f'file://{file_path}')

        # Force 'demo mode' by simulating firebase load failure or just setting the flag
        # The app uses window.firebaseLoaded. If false, it falls back to demo mode on login.
        # However, to see the dashboard, we need to login.

        # Override firebaseLoaded to false to trigger demo mode in AuthScreen
        page.evaluate('window.firebaseLoaded = false')

        # Wait for the login screen to appear
        page.wait_for_selector('text=Sign In')

        # Fill in demo credentials (any email/pass works in demo mode if firebaseLoaded is false)
        page.fill('input[type="email"]', 'demo@example.com')
        page.fill('input[type="password"]', 'password')
        page.click('button:has-text("Sign In")')

        # Wait for dashboard to load
        page.wait_for_selector('text=Welcome back')

        # Go to Employee Profile if possible, or just verify dashboard loads without errors
        # The demo user has role 'HR', so 'Staff Directory' should be visible
        page.click('button:has-text("Staff Directory")')

        # Wait for employees list
        page.wait_for_selector('text=Staff Directory')

        # Take a screenshot
        page.screenshot(path='verification/screenshot.png')
        print('Screenshot saved to verification/screenshot.png')

        browser.close()

if __name__ == '__main__':
    run()
