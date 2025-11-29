
// Test Runner Framework
const colors = {
    reset: "\x1b[0m",
    green: "\x1b[32m",
    red: "\x1b[31m",
    yellow: "\x1b[33m",
    blue: "\x1b[34m"
};

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function describe(name, fn) {
    console.log(`\n${colors.blue}📦 ${name}${colors.reset}`);
    fn();
}

function it(name, fn) {
    totalTests++;
    try {
        fn();
        passedTests++;
        console.log(`  ${colors.green}✅ ${name}${colors.reset}`);
    } catch (e) {
        failedTests++;
        console.error(`  ${colors.red}❌ ${name}${colors.reset}`);
        console.error(`     Error: ${e.message}`);
    }
}

function expect(actual) {
    return {
        toBe: (expected) => {
            if (actual !== expected) {
                throw new Error(`Expected ${expected}, but got ${actual}`);
            }
        },
        toEqual: (expected) => {
            const actualStr = JSON.stringify(actual);
            const expectedStr = JSON.stringify(expected);
            if (actualStr !== expectedStr) {
                throw new Error(`Expected ${expectedStr}, but got ${actualStr}`);
            }
        },
        toBeGreaterThan: (expected) => {
            if (!(actual > expected)) {
                throw new Error(`Expected > ${expected}, but got ${actual}`);
            }
        },
        toBeCloseTo: (expected, precision = 2) => {
            if (Math.abs(actual - expected) > Math.pow(10, -precision) / 2) {
                throw new Error(`Expected ${expected} (approx), but got ${actual}`);
            }
        }
    };
}

// ==========================================
// IMPORT BUSINESS LOGIC
// ==========================================
// Now we import the shared code instead of duplicating it
const utils = require('./utils.js');
const { calculateLateness, calculateFinancials } = utils;

// Helper to create timestamp seconds from HH:MM
function makeTime(hour, minute) {
    const d = new Date();
    d.setHours(hour, minute, 0, 0);
    return Math.floor(d.getTime() / 1000);
}

// ==========================================
// TESTS
// ==========================================

describe("Lateness Calculation Logic", () => {

    it("should return 0 when employee is on time", () => {
        const shiftStart = "09:00";
        const logTime = makeTime(9, 0); // 09:00
        expect(calculateLateness(logTime, shiftStart)).toBe(0);
    });

    it("should return 0 when employee is early", () => {
        const shiftStart = "09:00";
        const logTime = makeTime(8, 50); // 08:50
        expect(calculateLateness(logTime, shiftStart)).toBe(0);
    });

    it("should return 0 when within grace period (5 mins)", () => {
        const shiftStart = "09:00";
        const logTime = makeTime(9, 5); // 09:05
        expect(calculateLateness(logTime, shiftStart)).toBe(0);
    });

    it("should return exact minutes late when exceeding grace period (6 mins)", () => {
        const shiftStart = "09:00";
        const logTime = makeTime(9, 6); // 09:06
        expect(calculateLateness(logTime, shiftStart)).toBe(6);
    });

    it("should return correct minutes for significant lateness", () => {
        const shiftStart = "09:00";
        const logTime = makeTime(9, 30); // 09:30
        expect(calculateLateness(logTime, shiftStart)).toBe(30);
    });

    it("should use DEFAULT_SHIFT_START (09:00) if shiftStart is missing", () => {
        const shiftStart = undefined;
        const logTime = makeTime(9, 30); // 09:30
        expect(calculateLateness(logTime, shiftStart)).toBe(30);
    });

    it("should handle different shift starts correctly", () => {
        const shiftStart = "10:00";
        const logTime = makeTime(10, 30); // 10:30
        expect(calculateLateness(logTime, shiftStart)).toBe(30);
    });
});

describe("Financial Calculation Logic", () => {

    it("should calculate net salary correctly with no lateness and no deductions", () => {
        const employee = { salary: 2400, shiftStart: "09:00" };
        const logs = [
            { type: 'in', timestamp: { seconds: makeTime(9, 0) } } // On time
        ];
        const deductions = [];

        const result = calculateFinancials(employee, logs, deductions);

        expect(result.hourlyRate).toBe(10); // 2400 / 240
        expect(result.totalLateness).toBe(0);
        expect(result.lateCost).toBe(0);
        expect(result.totalDeductions).toBe(0);
        expect(result.netSalary).toBe(2400);
    });

    it("should deduct late fees correctly", () => {
        const employee = { salary: 2400, shiftStart: "09:00" }; // Hourly rate = 10
        const logs = [
            { type: 'in', timestamp: { seconds: makeTime(10, 0) } } // 60 mins late
        ];
        const deductions = [];

        const result = calculateFinancials(employee, logs, deductions);

        expect(result.totalLateness).toBe(60);
        // Cost = (60 / 60) * 10 = 10
        expect(result.lateCost).toBe(10);
        expect(result.netSalary).toBe(2390); // 2400 - 10
    });

    it("should handle multiple late logs", () => {
        const employee = { salary: 4800, shiftStart: "09:00" }; // Hourly rate = 20
        const logs = [
            { type: 'in', timestamp: { seconds: makeTime(9, 30) } }, // 30 mins late
            { type: 'in', timestamp: { seconds: makeTime(10, 0) } }  // 60 mins late (another day hypothetically)
        ];
        const deductions = [];

        const result = calculateFinancials(employee, logs, deductions);

        expect(result.totalLateness).toBe(90);
        // Cost = (90 / 60) * 20 = 1.5 * 20 = 30
        expect(result.lateCost).toBe(30);
        expect(result.netSalary).toBe(4770);
    });

    it("should sum manual deductions correctly", () => {
        const employee = { salary: 2400 };
        const logs = [];
        const deductions = [
            { amount: 50 },
            { amount: "100" } // String number
        ];

        const result = calculateFinancials(employee, logs, deductions);

        expect(result.totalDeductions).toBe(150);
        expect(result.netSalary).toBe(2250);
    });

    it("should handle zero salary gracefully", () => {
        const employee = { salary: 0, shiftStart: "09:00" };
        const logs = [
            { type: 'in', timestamp: { seconds: makeTime(10, 0) } } // Late
        ];
        const deductions = [{ amount: 50 }];

        const result = calculateFinancials(employee, logs, deductions);

        expect(result.hourlyRate).toBe(0);
        expect(result.lateCost).toBe(0);
        expect(result.netSalary).toBe(-50); // 0 - 50 - 0
    });

    it("should handle rounding in late cost", () => {
        // Salary 2400 => rate 10.
        // Late 30 mins => 0.5 hours. Cost 5.
        const employee = { salary: 2400, shiftStart: "09:00" };
        const logs = [{ type: 'in', timestamp: { seconds: makeTime(9, 30) } }];

        const result = calculateFinancials(employee, logs, []);
        expect(result.lateCost).toBe(5);

        // Salary 2500 => rate 10.4166...
        // Late 30 mins => 0.5 * 10.4166 = 5.208. Rounded => 5.
        const employee2 = { salary: 2500, shiftStart: "09:00" };
        const result2 = calculateFinancials(employee2, logs, []);
        expect(result2.lateCost).toBe(5);
    });
});

// Summary
console.log(`\n================================`);
console.log(`Total Tests: ${totalTests}`);
console.log(`${colors.green}Passed:      ${passedTests}${colors.reset}`);
console.log(`${failedTests > 0 ? colors.red : colors.green}Failed:      ${failedTests}${colors.reset}`);
console.log(`================================\n`);

if (failedTests > 0) process.exit(1);
