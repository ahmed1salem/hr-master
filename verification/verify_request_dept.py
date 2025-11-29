
from playwright.sync_api import sync_playwright
import time

def verify_request_dept(page):
    # Mock Firebase
    page.route("**/*firebase*", lambda route: route.abort())

    page.add_init_script("""
        window.firebaseLoaded = true;
        window.auth = {
            currentUser: { uid: 'hr_user', email: 'hr@example.com', role: 'HR' }
        };

        window.db = {};

        // Mock Firestore functions
        window.doc = (db, coll, id) => ({ _path: { segments: [coll, id] }, type: 'doc' });
        window.collection = (db, coll) => ({ _path: { segments: [coll] }, type: 'collection' });
        window.query = (coll, ...args) => coll;
        window.where = () => {};
        window.orderBy = () => {};
        window.serverTimestamp = () => ({ seconds: Math.floor(Date.now()/1000) });

        // Mock onAuthStateChanged
        window.onAuthStateChanged = (auth, callback) => {
            setTimeout(() => callback({ uid: 'hr_user', email: 'hr@example.com' }), 50);
            return () => {};
        };

        const mockUsers = [
            { id: 'u1', uid: 'u1', name: 'Alice Smith', department: 'Engineering', role: 'Employee', salary: 5000, status: 'active' },
            { id: 'u2', uid: 'u2', name: 'Bob Jones', department: 'Sales', role: 'Manager', salary: 6000, status: 'active' },
            { id: 'hr_user', uid: 'hr_user', name: 'HR Manager', department: 'HR', role: 'HR', salary: 7000, status: 'active' }
        ];

        const mockRequests = [
            { id: 'r1', userId: 'u1', userName: 'Alice Smith', type: 'Leave', reason: 'Vacation', status: 'Pending', timestamp: { seconds: 1715670000 } }
        ];

        // Mock onSnapshot
        window.onSnapshot = (ref, next, error) => {
             // User Profile
             if (ref.type === 'doc' && ref._path.segments[0] === 'users' && ref._path.segments[1] === 'hr_user') {
                 setTimeout(() => next({ exists: () => true, data: () => mockUsers[2] }), 100);
                 return () => {};
             }
             // Requests collection
             if (ref.type === 'collection' && ref._path.segments[0] === 'requests') {
                  setTimeout(() => next({ docs: mockRequests.map(r => ({ id: r.id, data: () => r })) }), 100);
                  return () => {};
             }
             // Users collection (for App -> Requests prop)
             if (ref.type === 'collection' && ref._path.segments[0] === 'users') {
                  setTimeout(() => next({ docs: mockUsers.map(u => ({ id: u.id, data: () => u })) }), 100);
                  return () => {};
             }

             setTimeout(() => next({ docs: [] }), 100);
             return () => {};
        };

        window.signOut = () => {};
    """)

    page.goto("http://localhost:8080")

    # Wait for Dashboard
    page.wait_for_selector("text=Welcome back, HR Manager", timeout=15000)

    # Go to Requests
    page.click("button:has-text('Requests')")

    # Wait for Requests page
    page.wait_for_selector("h2:has-text('Requests')")

    # Wait for the request from Alice
    page.wait_for_selector("text=Alice Smith")

    # Check for Department "Engineering" under name
    # We look for "Engineering" text which is uppercase in my code? No, in mock it is "Engineering".
    # In my code: <p className="text-[10px] uppercase text-slate-300">{reqUser.department}</p>
    # So it should be "ENGINEERING" if CSS uppercase works, or text-transform is applied.
    # CSS `uppercase` class applies text-transform: uppercase.
    # Playwright's `has-text` matches text content, which might be the original text if CSS transforms it.
    # But usually Playwright matches visible text.
    # Let's wait for "ENGINEERING" or "Engineering"

    page.wait_for_selector("text=ENGINEERING")

    page.screenshot(path="verification/request_dept.png")

    print("Verification Successful")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_request_dept(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_dept.png")
        finally:
            browser.close()
