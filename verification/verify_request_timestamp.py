
from playwright.sync_api import sync_playwright
import time
import datetime

def verify_request_timestamp(page):
    # Enable console logging
    page.on("console", lambda msg: print(f"Console: {msg.text}"))

    # Mock Firebase
    page.route("**/*firebase*", lambda route: route.abort())

    page.add_init_script("""
        window.firebaseLoaded = true;

        // Mock Lucide to render text
        window.lucide = {
            createIcons: ({ root }) => {
                const icons = root.querySelectorAll('[data-lucide]');
                icons.forEach(icon => {
                    icon.textContent = icon.getAttribute('data-lucide');
                });
            }
        };

        // Define users for testing roles
        const users = {
            hr: { uid: 'hr1', email: 'hr@example.com', role: 'HR', name: 'HR User', department: 'HR' },
            emp: { uid: 'emp1', email: 'emp@example.com', role: 'Employee', name: 'Emp User', department: 'Engineering' }
        };

        window.auth = { currentUser: users.hr };

        window.db = {};
        window.mockData = {
            requests: [
                { id: 'r1', userId: 'emp1', userName: 'Emp User', type: 'Leave', reason: 'Vacation', status: 'Pending', timestamp: { seconds: 1715670000 } }
            ]
        };

        // Mock Firestore functions
        window.doc = (db, coll, id) => ({ _path: { segments: [coll, id] }, type: 'doc' });
        window.collection = (db, coll) => ({ _path: { segments: [coll] }, type: 'collection' });
        window.query = (coll, ...args) => coll;
        window.where = () => {};
        window.orderBy = () => {};
        window.serverTimestamp = () => ({ seconds: Math.floor(Date.now()/1000) });

        window.onAuthStateChanged = (auth, callback) => {
            setTimeout(() => callback(window.auth.currentUser), 50);
            return () => {};
        };

        window.onSnapshot = (ref, next, error) => {
             const coll = ref._path.segments[0];
             const id = ref._path.segments[1];

             if (coll === 'users' && id === window.auth.currentUser.uid) {
                 setTimeout(() => next({ exists: () => true, data: () => window.auth.currentUser }), 100);
                 return () => {};
             }
             if (window.mockData[coll]) {
                 setTimeout(() => next({ docs: window.mockData[coll].map(d => ({ id: d.id, data: () => d })) }), 100);
                 return () => {};
             }
             if (coll === 'users') {
                 setTimeout(() => next({ docs: Object.values(users).map(u => ({ id: u.uid, data: () => u })) }), 100);
                 return () => {};
             }
             setTimeout(() => next({ docs: [] }), 100);
             return () => {};
        };

        window.signOut = () => {};
    """)

    # 1. Login as HR
    page.goto("http://localhost:8080")
    page.wait_for_selector("text=Welcome back, HR User", timeout=15000)

    # Go to Requests
    page.click("button:has-text('Requests')")
    page.wait_for_selector("h2:has-text('Requests')")

    # Check if timestamp is displayed
    # Timestamp 1715670000 is 2024-05-14
    # The locale string format depends on the machine, but it should contain 2024 or 5/14

    # Wait for the timestamp text
    page.wait_for_selector("text=2024", timeout=5000)

    page.screenshot(path="verification/request_timestamp.png")

    print("Verification Successful")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_request_timestamp(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_timestamp.png")
        finally:
            browser.close()
