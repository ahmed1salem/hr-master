
// Verification test for lateness calculation
// This script simulates the logic used in EmployeeProfile component

const DEFAULT_SHIFT_START = "09:00";

function testLatenessCalculation() {
    console.log("Starting verification test...");

    // Mock employee with NO shiftStart (undefined)
    const employee = {
        name: "John Doe",
        // shiftStart is undefined
    };

    // Mock logTime: Today at 09:30 AM
    // We need to create a Firestore-like timestamp { seconds: ... }
    const now = new Date();
    now.setHours(9, 30, 0, 0);
    const logTime = { seconds: Math.floor(now.getTime() / 1000) };

    console.log(`Log Time: ${now.toLocaleTimeString()}`);
    console.log(`Employee Shift Start: ${employee.shiftStart}`);

    // The logic being tested (must match the code in index.html)
    const calculateLateness = (logTime) => {
        const shiftStart = employee.shiftStart || DEFAULT_SHIFT_START;
        const [sH, sM] = shiftStart.split(':').map(Number);
        const shiftDate = new Date(); shiftDate.setHours(sH, sM, 0, 0);
        const logDate = new Date(logTime.seconds * 1000);
        const compareDate = new Date(); compareDate.setHours(logDate.getHours(), logDate.getMinutes(), 0, 0);
        const diff = Math.floor((compareDate - shiftDate) / 60000);
        return diff > 5 ? diff : 0;
    };

    const lateness = calculateLateness(logTime);
    console.log(`Calculated Lateness: ${lateness} minutes`);

    if (lateness === 30) {
        console.log("PASS: Lateness is 30.");
    } else {
        console.error(`FAIL: Expected 30, got ${lateness}`);
        process.exit(1);
    }
}

testLatenessCalculation();
