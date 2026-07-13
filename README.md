<div align="center">

# Hostel Leave Management System

### A Flask Web Platform with Flutter Mobile Support for Digital Hostel Leave Management

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Local-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Render](https://img.shields.io/badge/Hosted_on-Render-46E3B7?logo=render&logoColor=white)](https://render.com/)
[![Flutter](https://img.shields.io/badge/Mobile_Client-Flutter-02569B?logo=flutter&logoColor=white)](https://flutter.dev/)
[![Windows](https://img.shields.io/badge/Desktop-Windows-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

[![Open Live Application](https://img.shields.io/badge/Open_Live_Application-Visit_Now-28A745?style=for-the-badge&logo=render&logoColor=white)](https://hostel-leave-management-system-w0nu.onrender.com)

Developed by **Vivan Kumar**  
BCA (Artificial Intelligence & Data Science), K.R. Mangalam University

</div>

---

## Overview

The **Hostel Leave Management System** digitizes the complete hostel leave workflow. Students can create accounts, submit leave applications, monitor their status, receive decision notifications, and download leave-history reports. Wardens use a separate dashboard to review applications and approve or reject them.

The project provides:

- a responsive browser-based interface;
- a Windows desktop wrapper powered by PyWebView;
- a Flutter mobile client that communicates with the backend JSON API;
- automatic SQLite storage for local use; and
- PostgreSQL support for deployment.

> The Flask backend and desktop wrapper are present in this repository. The Flutter application is maintained as a separate client project and uses the mobile API described below.

The system replaces slow, error-prone paper registers with a centralized and transparent process.

## Key Objectives

- Make leave applications faster and easier for hostel students.
- Give wardens a centralized view of all leave requests.
- Keep students informed throughout the approval process.
- Maintain searchable, persistent digital leave records.
- Support local development and cloud deployment from the same codebase.
- Provide a responsive interface across desktop and mobile screen sizes.

## Features

### Student Module

- Student registration with duplicate-email validation
- Student login and session management
- Dashboard with total, pending, approved, and rejected counts
- Online leave application
- Leave-history and status tracking
- Decision notifications
- Student profile view
- Password change
- Downloadable PDF leave report
- Logout

### Warden Module

- Separate warden login
- Central dashboard of student leave applications
- Student name, email, reason, and leave-date visibility
- Approve or reject leave requests
- Automatic notification creation after a decision
- Leave-record management
- Logout

### Additional Capabilities

- Flutter mobile workflow for students and wardens through the REST-style API
- REST-style JSON endpoints for student and warden mobile workflows
- PDF report generation with ReportLab
- Local SQLite and hosted PostgreSQL database support
- Windows desktop experience through PyWebView
- Windows installer configuration through Inno Setup
- Responsive Bootstrap interface

## System Workflow

```mermaid
flowchart LR
    S["Student registers or logs in"] --> A["Submits leave request"]
    A --> D[("SQLite or PostgreSQL")]
    D --> W["Warden reviews request"]
    W --> C{"Decision"}
    C -->|Approve| AP["Status: Approved"]
    C -->|Reject| RJ["Status: Rejected"]
    AP --> N["Student notification"]
    RJ --> N
    N --> H["Dashboard, history, and PDF report"]
```

## Architecture

```mermaid
flowchart TB
    B["Web browser"] --> F["Flask application"]
    P["Windows desktop wrapper"] --> F
    M["Mobile client"] --> API["JSON API"]
    API --> F
    F --> T["Jinja templates and Bootstrap UI"]
    F --> R["ReportLab PDF generator"]
    F --> DB{"Database selection"}
    DB -->|Local| S[("SQLite")]
    DB -->|DATABASE_URL set| PG[("PostgreSQL")]
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5.3, JavaScript, Font Awesome, Google Fonts |
| Mobile client | Flutter and Dart |
| Backend | Python, Flask, Gunicorn |
| Local database | SQLite |
| Production database | PostgreSQL with `psycopg2` |
| Reporting | ReportLab |
| Desktop wrapper | PyWebView |
| Desktop packaging | PyInstaller and Inno Setup |
| Deployment | Render |
| Version control | Git and GitHub |

## Project Structure

```text
Hostel-Leave-Management-System/
├── app.py                                  # Main Flask app, database logic, and API
├── launcher.py                             # PyWebView desktop launcher
├── main.py                                 # Desktop application entry point
├── splash.py                               # Desktop splash screen
├── config.py                               # Project configuration
├── requirements.txt                        # Python dependencies
├── render.yaml                             # Render deployment configuration
├── Hostel Leave Management System Installer.iss
│                                             # Inno Setup installer script
├── assets/                                 # Desktop icons and artwork
├── screenshots/                            # Application screenshots
├── static/
│   └── css/
│       └── style.css                       # Shared styling
├── templates/
│   ├── admin/                              # Warden pages
│   ├── student/                            # Student pages
│   ├── base.html                           # Shared page layout
│   └── home.html                           # Landing page
├── models/                                 # Model package
└── routes/                                 # Route package
```

### Flutter Mobile Client

The Flutter client is a separate project that consumes the Flask API. Its recommended structure is:

```text
flutter_app/
├── lib/
│   ├── main.dart                           # Application entry point
│   ├── screens/                            # Login, dashboard, leave, and notification screens
│   ├── services/                           # Backend API service
│   ├── models/                             # Student, leave, and notification models
│   └── widgets/                            # Reusable UI components
├── assets/                                 # Images and app assets
└── pubspec.yaml                            # Flutter dependencies and metadata
```

Keep the Flutter project in its own repository or add it as a `flutter_app/` folder when publishing a combined source-code submission.

## Getting Started

### Prerequisites

- Python 3.10 or later
- `pip`
- Git

PostgreSQL is optional. Without a `DATABASE_URL`, the application automatically creates and uses a local `hostel.db` SQLite database.

### 1. Clone the Repository

```bash
git clone https://github.com/Vivan178/Hostel-Leave-Management-System.git
cd Hostel-Leave-Management-System
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Environment

For local SQLite use, only a secure Flask secret is recommended:

Windows PowerShell:

```powershell
$env:SECRET_KEY="replace-with-a-long-random-value"
```

Linux or macOS:

```bash
export SECRET_KEY="replace-with-a-long-random-value"
```

For PostgreSQL, also provide its connection URL:

```text
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### 5. Run the Web Application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

### 6. Run the Desktop Wrapper (Optional)

```bash
python launcher.py
```

This starts the Flask server locally and opens it in a native desktop window.

### 7. Connect the Flutter Application (Optional)

In the Flutter project's API service, set the base URL to the deployed API:

```text
https://hostel-leave-management-system-w0nu.onrender.com
```

For Android emulator development against a local Flask server, use:

```text
http://10.0.2.2:5000
```

For a physical phone, use the computer's local-network IP address and ensure the phone and computer are on the same network. Start the Flutter application from its own project folder with:

```bash
flutter pub get
flutter run
```

## Database Design

### `students`

| Field | Purpose |
|---|---|
| `id` | Unique student identifier |
| `name` | Student name |
| `email` | Unique login email |
| `password` | Student password |

### `leaves`

| Field | Purpose |
|---|---|
| `id` | Unique leave-request identifier |
| `student_id` | Student who submitted the request |
| `reason` | Reason for leave |
| `from_date` | Leave start date |
| `to_date` | Leave end date |
| `status` | `Pending`, `Approved`, or `Rejected` |

### `admins`

| Field | Purpose |
|---|---|
| `id` | Unique warden identifier |
| `username` | Warden login name |
| `password` | Warden password |

### `notifications`

| Field | Purpose |
|---|---|
| `id` | Unique notification identifier |
| `student_id` | Notification recipient |
| `message` | Decision message |
| `status` | `Read` or `Unread` state |

## Mobile API

The Flask backend includes JSON endpoints for the Flutter mobile client. The client can support student login, leave submission, dashboard counts, leave history, notifications, warden login, request listing, and status updates.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/test` | Check API availability |
| `POST` | `/api/student/login` | Authenticate a student |
| `POST` | `/api/student/apply_leave` | Submit a leave request |
| `POST` | `/api/student/dashboard` | Retrieve student details and leave totals |
| `POST` | `/api/student/leave_history` | Retrieve a student's leave history |
| `POST` | `/api/student/notifications` | Retrieve status-based notifications |
| `POST` | `/api/warden/login` | Authenticate a warden |
| `POST` | `/api/warden/leaves` | Retrieve all leave requests |
| `POST` | `/api/warden/update_leave_status` | Approve or reject a leave request |

Example health check:

```bash
curl https://hostel-leave-management-system-w0nu.onrender.com/api/test
```

> The current mobile endpoints are intended for academic demonstration. Production use should add token-based authentication, authorization checks, request-rate limiting, and stricter input validation.

## Flutter Client Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Flutter App
    participant A as Flask API
    participant D as Database

    U->>F: Signs in or submits a leave request
    F->>A: Sends JSON request
    A->>D: Reads or updates data
    D-->>A: Returns stored data
    A-->>F: Returns JSON response
    F-->>U: Shows dashboard, history, or decision status
```

## Deployment on Render

The included `render.yaml` defines the web service:

```yaml
services:
  - type: web
    name: hostel-leave-management-system
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

Set these environment variables in the Render dashboard:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Signs and protects Flask session data |

Never commit database credentials or production secrets to the repository.

## Screenshots

### Home Page

![Home page](screenshots/home.png)

### Student Login

![Student login](screenshots/student_login.png)

### Student Registration

![Student registration](screenshots/student_register.png)

### Student Dashboard

![Student dashboard](screenshots/student_dashboard.png)

### Apply for Leave

![Apply for leave](screenshots/apply_leave.png)

### Student Notifications

![Student notifications](screenshots/notifications.png)

### Student Profile

![Student profile](screenshots/profile.png)

### Change Password

![Change password](screenshots/change_password.png)

### Warden Login

![Warden login](screenshots/warden_login.png)

### Warden Dashboard

![Warden dashboard](screenshots/warden_dashboard.png)

### Approved Leave Request

![Approved leave request](screenshots/approved_leave.png)

## Testing Checklist

| Test Area | Expected Result |
|---|---|
| Home page | Loads successfully |
| Student registration | Creates a new student account |
| Duplicate registration | Rejects an existing email address |
| Student authentication | Accepts valid credentials and rejects invalid ones |
| Leave submission | Stores a new request as `Pending` |
| Student dashboard | Displays correct status totals and history |
| Warden authentication | Opens the protected warden dashboard |
| Approval and rejection | Updates the selected leave status |
| Notifications | Shows the warden's decision to the student |
| Password change | Updates the student's password after validation |
| PDF report | Downloads the student's leave history |
| Database selection | Uses SQLite locally and PostgreSQL when configured |
| Responsive layout | Remains usable on common screen sizes |

## Security Status

This is an academic application. It uses parameterized database queries and protects browser dashboards with session checks. However, the current implementation stores passwords as plain text, provides a default development warden account, and identifies mobile users by database ID rather than an access token.

Before production use, the following changes are required:

- hash passwords with Werkzeug, Argon2, or bcrypt;
- remove all default credentials;
- require a strong `SECRET_KEY` with no insecure fallback;
- add CSRF protection to state-changing browser actions;
- use authenticated `POST` requests for approval and rejection;
- add token-based mobile authentication and role authorization;
- validate dates and all submitted fields server-side;
- configure secure cookies, HTTPS enforcement, rate limiting, and audit logs; and
- add database foreign keys, constraints, and migrations.

## Future Enhancements

- Email and SMS notifications
- Parent or guardian approval
- Multiple-hostel support
- Search, filtering, and pagination for wardens
- Leave cancellation and modification
- Supporting-document uploads
- Analytics and downloadable administrative reports
- QR-based gate verification
- Two-factor authentication
- Automated tests and continuous integration
- Role-based administration and audit history

## Developer

**Vivan Kumar**  
Bachelor of Computer Applications  
Specialization: Artificial Intelligence & Data Science  
K.R. Mangalam University

## Acknowledgements

- K.R. Mangalam University
- Flask and Python communities
- Bootstrap team
- PostgreSQL and SQLite communities
- Render and GitHub

## Academic Use

This project was developed as an academic submission for the Bachelor of Computer Applications in Artificial Intelligence & Data Science program at K.R. Mangalam University.

© 2026 Vivan Kumar. All rights reserved.

---

<div align="center">

If this project is useful to you, consider giving the repository a star.

Made with Python, Flask, and Bootstrap.

</div>
