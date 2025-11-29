(function(global) {
    const DEFAULT_SHIFT_START = "09:00";

    /**
     * Calculates lateness in minutes based on shift start time.
     * @param {number} logTimeSeconds - Timestamp in seconds
     * @param {string} shiftStart - HH:MM string (default "09:00")
     * @returns {number} Minutes late (0 if early/on-time or within 5 min grace)
     */
    function calculateLateness(logTimeSeconds, shiftStart) {
        const actualShiftStart = shiftStart || DEFAULT_SHIFT_START;
        const [sH, sM] = actualShiftStart.split(':').map(Number);

        // Normalize shift date to today
        const shiftDate = new Date();
        shiftDate.setHours(sH, sM, 0, 0);

        // Normalize log date to today
        const logDate = new Date(logTimeSeconds * 1000);
        const compareDate = new Date();
        compareDate.setHours(logDate.getHours(), logDate.getMinutes(), 0, 0);

        const diff = Math.floor((compareDate - shiftDate) / 60000);
        return diff > 5 ? diff : 0;
    }

    /**
     * Calculates financial metrics.
     * @param {Object} employee - Employee object { salary, shiftStart }
     * @param {Array} logs - Array of attendance logs { type, timestamp: { seconds } }
     * @param {Array} deductionsList - Array of deductions { amount }
     * @returns {Object} { totalLateness, totalDeductions, hourlyRate, lateCost, netSalary }
     */
    function calculateFinancials(employee, logs, deductionsList) {
        // Calculate total lateness
        const totalLateness = logs
            .filter(l => l.type === 'in')
            .reduce((acc, curr) => acc + calculateLateness(curr.timestamp.seconds, employee.shiftStart), 0);

        // Calculate total deductions
        const totalDeductions = deductionsList.reduce((acc, curr) => acc + Number(curr.amount || 0), 0);

        // Calculate hourly rate (Salary / 240)
        const hourlyRate = (Number(employee.salary) || 0) / 240;

        // Calculate late cost
        const lateCost = Math.round((totalLateness / 60) * hourlyRate);

        // Calculate net salary
        const netSalary = (Number(employee.salary) || 0) - totalDeductions - lateCost;

        return {
            totalLateness,
            totalDeductions,
            hourlyRate,
            lateCost,
            netSalary
        };
    }

    const utils = {
        calculateLateness,
        calculateFinancials,
        DEFAULT_SHIFT_START
    };

    // Export for Node.js
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = utils;
    }
    // Export for Browser
    else {
        global.HRUtils = utils;
    }

})(this);
