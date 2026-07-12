# 🏨 Hostel Leave Management System

A modern **Hostel Leave Management System** developed using **Python Flask**, **SQLite**, **HTML**, **CSS**, and **Bootstrap**. This web application simplifies the hostel leave approval process by allowing students to apply for leave online while enabling wardens to review and manage requests through a dedicated dashboard.

---

## 🌐 Live Demo

**Website:** https://hostel-leave-management-system-w0nu.onrender.com

---

## 📌 Project Overview

The Hostel Leave Management System replaces the traditional paper-based leave process with a secure and user-friendly digital platform.

Students can:
- Register and log in
- Apply for hostel leave
- Track leave status
- View notifications
- Download leave approval documents

Wardens can:
- Log in securely
- View all leave applications
- Approve or reject requests
- Manage student leave records

---

## ✨ Features

### 👨‍🎓 Student Module

- Student Registration
- Secure Login
- Dashboard
- Apply Leave
- View Leave History
- Notifications
- Profile Management
- Change Password
- QR Code Generation
- PDF Leave Slip

### 👮 Warden Module

- Secure Login
- Dashboard
- View Leave Requests
- Approve Leave
- Reject Leave
- Student Leave Management

---

## 🛠 Technology Stack

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Font Awesome

### Backend

- Python
- Flask

### Database

- SQLite

### Libraries Used

- Flask
- Flask-Login
- Flask-WTF
- SQLAlchemy
- ReportLab
- QRCode
- Pillow
- python-dotenv

### Version Control

- Git
- GitHub

### Deployment

- Render
---

# 📂 Project Structure

```text
Hostel Leave Management System/
│
├── app.py
├── hostel.db
├── requirements.txt
├── render.yaml
├── README.md
│
├── static/
│   ├── css/
│   ├── images/
│   └── qr_codes/
│
├── templates/
│   ├── student/
│   ├── admin/
│   └── home.html
│
└── reports/
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Vivan178/Hostel-Leave-Management-System.git
```

## Move into the Project

```bash
cd Hostel-Leave-Management-System
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

# 👨‍💻 User Roles

## Student

- Register Account
- Login
- Apply Leave
- Track Leave Status
- View Notifications
- Generate QR Code
- Download PDF

---

## Warden

- Secure Login
- View Student Requests
- Approve Leave
- Reject Leave
- Manage Leave Records
---

# 📸 Application Screenshots

> *(Add screenshots of your application here after capturing them.)*

| Home Page | Student Dashboard |
|------------|-------------------|
| ![Home](screenshots/home.png) | ![Dashboard](screenshots/dashboard.png) |

| Apply Leave | Warden Dashboard |
|--------------|------------------|
| ![Apply Leave](screenshots/apply_leave.png) | ![Warden Dashboard](screenshots/warden_dashboard.png) |

---

# 🔒 Security Features

- Secure user authentication
- Session management
- Protected dashboards
- Separate Student and Warden access
- SQLite database integration
- Input validation using Flask-WTF

---

# 🌟 Key Highlights

- Responsive Bootstrap UI
- Professional glassmorphism design
- Student & Warden modules
- Leave approval workflow
- QR Code generation
- PDF Leave Slip generation
- Live deployment on Render
- GitHub version control

---

# 🚀 Future Enhancements

- Email notifications
- SMS alerts
- Parent approval module
- Multi-hostel support
- Admin analytics dashboard
- PostgreSQL integration
- Cloud file storage
- Mobile application

---

# 🧪 Testing

The application has been tested for:

- Student Registration
- Student Login
- Leave Application
- Leave Approval
- Leave Rejection
- Notifications
- PDF Generation
- QR Code Generation
- Responsive Design

---

# 👨‍💻 Developed By

**Vivan Kumar**

B.Tech CSE Student

K.R. Mangalam University

---

# 🙏 Acknowledgements

Special thanks to:

- K.R. Mangalam University
- Flask Community
- Bootstrap Team
- SQLite Team
- Render

---

# 📄 License

This project is developed for educational purposes as part of the B.Tech Computer Science Engineering curriculum.

© 2026 Vivan Kumar. All Rights Reserved.