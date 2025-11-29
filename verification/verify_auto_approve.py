
from playwright.sync_api import sync_playwright
import time

def verify_auto_approve(page):
    # Enable console logging
    page.on("console", lambda msg: print(f"Console: {msg.text}"))

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

        // Mock onSnapshot
        window.onSnapshot = (ref, next, error) => {
             // User Profile
             if (ref.type === 'doc' && ref._path.segments[0] === 'users' && ref._path.segments[1] === 'hr_user') {
                 setTimeout(() => next({ exists: () => true, data: () => ({ uid: 'hr_user', name: 'HR Manager', role: 'HR', department: 'HR', status: 'active' }) }), 100);
                 return () => {};
             }
             // Requests collection
             if (ref.type === 'collection' && ref._path.segments[0] === 'requests') {
                  // We will push to this list when addDoc is called
                  if (!window.mockRequests) window.mockRequests = [];
                  setTimeout(() => next({ docs: window.mockRequests.map(r => ({ id: r.id, data: () => r })) }), 100);
                  // Setup a listener mechanism
                  window.requestsListener = next;
                  return () => {};
             }

             setTimeout(() => next({ docs: [] }), 100);
             return () => {};
        };

        // Mock addDoc
        window.addDoc = async (coll, data) => {
            console.log("addDoc called with", JSON.stringify(data));
            const newDoc = { id: 'req_' + Date.now(), ...data };
            if (!window.mockRequests) window.mockRequests = [];
            window.mockRequests.push(newDoc);
            if (window.requestsListener) {
                 window.requestsListener({ docs: window.mockRequests.map(r => ({ id: r.id, data: () => r })) });
            }
            return { id: newDoc.id };
        };

        window.signOut = () => {};
    """)

    page.goto("http://localhost:8080")

    # Wait for Dashboard
    page.wait_for_selector("text=Welcome back, HR Manager", timeout=15000)

    # Go to Requests (New Request button in dashboard or sidebar)
    # Sidebar "Requests" button
    page.click("button:has-text('Requests')")

    # Wait for Requests page
    page.wait_for_selector("h2:has-text('Requests')")

    # Click New Request
    page.click("button:has-text('New Request')")

    # Fill form
    page.fill("textarea[placeholder='Description']", "Auto approve test")

    # Submit
    page.click("button:has-text('Submit')")

    # Wait for the request to appear in the list
    page.wait_for_selector("text=Auto approve test")

    # Check status
    # The status should be "Approved" (green badge)
    # We can check for the text "Approved" near the description

    page.screenshot(path="verification/auto_approve_test.png")

    # Verify text content
    content = page.content()
    if "Approved" in content and "Auto approve test" in content:
        print("Verification Successful: Request is Approved")
    else:
        print("Verification Failed: Request not found or not Approved")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_auto_approve(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_approve.png")
        finally:
            browser.close()
