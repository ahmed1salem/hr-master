
from playwright.sync_api import sync_playwright
import time

def verify_deletion_logic(page):
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
            hr: { uid: 'hr1', email: 'hr@example.com', role: 'HR', name: 'HR User' },
            manager: { uid: 'mgr1', email: 'mgr@example.com', role: 'Manager', name: 'Manager User' },
            employee: { uid: 'emp1', email: 'emp@example.com', role: 'Employee', name: 'Emp User' }
        };

        window.auth = { currentUser: users.hr };

        window.db = {};
        window.mockData = {
            requests: [
                { id: 'r1', userId: 'emp1', userName: 'Emp User', type: 'Leave', reason: 'Vacation', status: 'Pending', timestamp: { seconds: 1715670000 } }
            ],
            deletion_requests: []
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

        window.addDoc = async (coll, data) => {
            console.log("addDoc called on " + coll._path.segments[0], JSON.stringify(data));
            if (coll._path.segments[0] === 'deletion_requests') {
                window.mockData.deletion_requests.push({ id: 'del_' + Date.now(), ...data });
                return { id: 'del_' + Date.now() };
            }
            return { id: 'new_' + Date.now() };
        };

        window.deleteDoc = async (docRef) => {
            const coll = docRef._path.segments[0];
            const id = docRef._path.segments[1];
            console.log(`deleteDoc called on ${coll}/${id}`);
            if (window.mockData[coll]) {
                window.mockData[coll] = window.mockData[coll].filter(d => d.id !== id);
            }
        };

        window.signOut = () => {};
        window.updateDoc = async () => {};
    """)

    # 1. Login as HR
    page.goto("http://localhost:8080")
    page.wait_for_selector("text=Welcome back, HR User", timeout=15000)

    # Go to Requests
    page.click("button:has-text('Requests')")
    page.wait_for_selector("h2:has-text('Requests')")

    # Check if mock data loaded
    page.wait_for_selector("text=Vacation")

    # Accept confirm dialogs
    page.on("dialog", lambda dialog: dialog.accept())

    # Click delete button (last button in the card)
    page.click(".grid .bg-white button:last-child")

    # Expect toast: Deletion Request Sent to Manager
    page.wait_for_selector("text=Deletion Request Sent to Manager")
    page.screenshot(path="verification/hr_deletion_request.png")

    # 2. Login as Manager (Reload)
    page.add_init_script("window.auth.currentUser = { uid: 'mgr1', email: 'mgr@example.com', role: 'Manager', name: 'Manager User' };")
    page.reload()
    page.wait_for_selector("text=Welcome back, Manager User", timeout=15000)

    # Go to Requests
    page.click("button:has-text('Requests')")

    # Click Deletion Requests Tab
    page.click("button:has-text('Deletion Requests')")

    # Should see the request
    page.wait_for_selector("text=HR User wants to delete Request: Leave by Emp User")
    page.screenshot(path="verification/mgr_approval_view.png")

    # Approve
    page.click("button:has-text('Delete')")

    # Expect success
    page.wait_for_selector("text=Request Approved & Item Deleted")
    page.screenshot(path="verification/mgr_approved.png")

    print("Verification Successful")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_deletion_logic(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_del.png")
        finally:
            browser.close()
