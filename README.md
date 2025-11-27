# HR Master - Smart Management System

HR Master is a comprehensive, single-file React application designed to streamline Human Resources management. It provides a robust set of tools for managing attendance, employees, requests, payroll, communication, and reporting, all within a modern, responsive interface.

## Features

-   **Dashboard**: Overview of user status, role, and department.
-   **Attendance Tracking**: Geo-tagged check-in and check-out functionality with logs.
-   **Employee Management**: HR-exclusive module to add, edit, and view employee details.
-   **Reports**: Generate and print reports for employee directories and attendance logs with filtering options.
-   **Requests Management**: Submit and manage leave, loan, and overtime requests with approval workflows.
-   **Communication**: Real-time team chat and meeting scheduling (online/onsite).
-   **Multilingual Support**: Switch seamlessly between English and Arabic interfaces.
-   **Role-Based Access Control**: Differentiated access for HR Managers, Managers, and Employees.
-   **Firebase Integration**: Real-time data persistence using Firestore and Authentication.

## Setup

This application is built as a single HTML file using React, Babel Standalone, and Tailwind CSS via CDN. No build step is required.

1.  **Clone the repository** (or download the `index.html` file).
2.  **Open `index.html`** in any modern web browser.
3.  **Firebase Configuration**:
    -   The application comes with a live Firebase configuration.
    -   If you wish to use your own Firebase project, replace the `firebaseConfig` object in the `<head>` section of `index.html`.
    -   Ensure Firestore rules allow read/write access or are properly configured for the app's security model.

## Usage

### Authentication
-   **Login**: Use your registered email and password.
-   **Register**: Create a new account. By default, new accounts are assigned the "Employee" role.
-   **Demo Mode**: If Firebase is not configured or offline, the app may offer a demo login.

### Roles
-   **HR Manager**: Full access to all modules, including Employee Management and Reports.
-   **Manager**: Access to manage requests and view reports.
-   **Employee**: Access to attendance, personal requests, chat, and meetings.

### Navigation
Use the sidebar to navigate between different modules:
-   **Dashboard**: Your personal hub.
-   **Attendance**: Mark your daily attendance.
-   **Employees**: (HR only) Manage staff records.
-   **Reports**: (HR/Manager) View and print analytics.
-   **Requests**: Submit or approve requests.
-   **Meetings**: Schedule and join team meetings.
-   **Team Chat**: communicate with your colleagues.

## Technologies Used
-   **React 18**: UI Library.
-   **Tailwind CSS**: Styling.
-   **Firebase**: Backend-as-a-Service (Auth, Firestore).
-   **Lucide Icons**: Iconography.
-   **Babel Standalone**: In-browser JSX compilation.
