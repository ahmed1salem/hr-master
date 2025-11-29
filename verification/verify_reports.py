
from playwright.sync_api import sync_playwright
import time
import datetime

def verify_reports(page):
    # Mock Firebase
    page.route("**/*firebase*", lambda route: route.abort())

    # Enable console logging
    page.on("console", lambda msg: print(f"Console: {msg.text}"))

    page.add_init_script("""
        window.firebaseLoaded = true;
        window.auth = {
            currentUser: { uid: 'hr_user', email: 'hr@example.com', role: 'HR' }
        };

        const nowSeconds = Math.floor(Date.now() / 1000);

        const mockUsers = [
            { id: 'u1', uid: 'u1', name: 'Alice Smith', department: 'Engineering', role: 'Employee', salary: 5000, status: 'active', shiftStart: '09:00' },
            { id: 'u2', uid: 'u2', name: 'Bob Jones', department: 'Sales', role: 'Manager', salary: 6000, status: 'active', shiftStart: '09:00' }
        ];

        const mockAttendance = [
            { id: 'a1', userId: 'u1', userName: 'Alice Smith', type: 'in', timestamp: { seconds: nowSeconds - 3600 }, location: 'Office' },
            { id: 'a2', userId: 'u1', userName: 'Alice Smith', type: 'out', timestamp: { seconds: nowSeconds }, location: 'Office' }
        ];

        window.db = {};

        // Mock Firestore functions
        window.doc = (db, coll, id) => ({ _path: { segments: [coll, id] }, type: 'doc' });
        window.collection = (db, coll) => ({ _path: { segments: [coll] }, type: 'collection' });
        window.query = (coll, ...args) => coll;
        window.where = () => {};
        window.orderBy = () => {};

        // Mock onAuthStateChanged
        window.onAuthStateChanged = (auth, callback) => {
            setTimeout(() => callback({ uid: 'hr_user', email: 'hr@example.com' }), 50);
            return () => {};
        };

        // Mock onSnapshot
        window.onSnapshot = (ref, next, error) => {
             if (ref.type === 'doc' && ref._path.segments[0] === 'users' && ref._path.segments[1] === 'hr_user') {
                 setTimeout(() => next({ exists: () => true, data: () => ({ uid: 'hr_user', name: 'HR Manager', role: 'HR', department: 'HR', status: 'active' }) }), 100);
                 return () => {};
             }
             if (ref.type === 'collection' && ref._path.segments[0] === 'requests') {
                 setTimeout(() => next({ docs: [] }), 100);
                 return () => {};
             }
             if (ref.type === 'collection' && ref._path.segments[0] === 'users') {
                 setTimeout(() => next({ docs: mockUsers.map(u => ({ id: u.id, uid: u.id, data: () => u })) }), 100);
                 return () => {};
             }
             setTimeout(() => next({ docs: [] }), 100);
             return () => {};
        };

        // Mock getDocs for Reports
        window.getDocs = async (query) => {
             await new Promise(r => setTimeout(r, 200));
             const coll = query._path.segments[0];

             if (coll === 'attendance') {
                 return { docs: mockAttendance.map(d => ({ id: d.id, data: () => d })) };
             }
             return { docs: [] };
        };

        window.signOut = () => {};
    """)

    page.goto("http://localhost:8080")

    # Wait for Dashboard
    page.wait_for_selector("text=Welcome back, HR Manager", timeout=15000)

    # Click on Reports in Sidebar (Analytics)
    page.click("button:has-text('Analytics')")

    # Wait for Reports page
    page.wait_for_selector("h2:has-text('Analytics')", timeout=5000)

    # Check default view (Attendance)
    page.wait_for_selector("text=Attendance Report", timeout=5000)

    # Screenshot 1: Default Report View
    page.screenshot(path="verification/report_attendance.png")

    # Change Report Type to Financials
    page.select_option("select >> nth=0", "financials")

    # Wait for Financials Table Headers
    page.wait_for_selector("text=Net Salary", timeout=5000)

    # Screenshot 2: Financials Report
    page.screenshot(path="verification/report_financials.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_reports(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
