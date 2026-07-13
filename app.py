from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import sqlite3
import qrcode

from io import BytesIO
from reportlab.pdfgen import canvas

try:
    import psycopg2
except ImportError:
    psycopg2 = None


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hostel_management_secret")


# ================= DATABASE =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DATABASE = os.path.join(BASE_DIR, "hostel.db")
DATABASE_URL = os.environ.get("DATABASE_URL")


class DatabaseCursor:
    """
    Small compatibility wrapper.

    SQLite uses ? placeholders.
    PostgreSQL uses %s placeholders.

    This wrapper lets the rest of the application keep using ?.
    """

    def __init__(self, cursor, is_postgres):
        self._cursor = cursor
        self._is_postgres = is_postgres

    def execute(self, query, parameters=()):
        if self._is_postgres:
            query = query.replace("?", "%s")

        self._cursor.execute(query, parameters)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class DatabaseConnection:
    def __init__(self, connection, is_postgres):
        self._connection = connection
        self.is_postgres = is_postgres

    def cursor(self):
        return DatabaseCursor(
            self._connection.cursor(),
            self.is_postgres
        )

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def get_db():
    """
    Render:
        Uses PostgreSQL when DATABASE_URL is configured.

    Local computer:
        Uses hostel.db SQLite automatically.
    """

    if DATABASE_URL:
        if psycopg2 is None:
            raise RuntimeError(
                "PostgreSQL support is missing. "
                "Run: pip install psycopg2-binary"
            )

        postgres_connection = psycopg2.connect(
            DATABASE_URL,
            sslmode="require"
        )

        return DatabaseConnection(
            postgres_connection,
            is_postgres=True
        )

    sqlite_connection = sqlite3.connect(SQLITE_DATABASE)

    return DatabaseConnection(
        sqlite_connection,
        is_postgres=False
    )


def is_integrity_error(error):
    if isinstance(error, sqlite3.IntegrityError):
        return True

    return (
        psycopg2 is not None
        and isinstance(error, psycopg2.IntegrityError)
    )


# ================= INITIALIZE DATABASE =================

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    if conn.is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaves(
                id SERIAL PRIMARY KEY,
                student_id INTEGER,
                reason TEXT,
                from_date TEXT,
                to_date TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins(
                id SERIAL PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications(
                id SERIAL PRIMARY KEY,
                student_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'Unread'
            )
        """)

    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaves(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                reason TEXT,
                from_date TEXT,
                to_date TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'Unread'
            )
        """)

    cursor.execute(
        "SELECT * FROM admins WHERE username=?",
        ("warden",)
    )

    admin = cursor.fetchone()

    if admin is None:
        cursor.execute(
            "INSERT INTO admins(username,password) VALUES(?,?)",
            ("warden", "12345")
        )
        print("✅ Warden user created")

    conn.commit()
    conn.close()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("home.html")


# ================= STUDENT REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO students
                (name,email,password)
                VALUES(?,?,?)
            """, (
                name,
                email,
                password
            ))

            conn.commit()

        except Exception as error:
            conn.rollback()
            conn.close()

            if is_integrity_error(error):
                return render_template(
                    "student/register.html",
                    error="Email already registered."
                )

            raise

        conn.close()
        return redirect(url_for("login"))

    return render_template(
        "student/register.html",
        error=None
    )


# ================= STUDENT LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template(
                "student/login.html",
                error="Please enter both email and password."
            )

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM students
            WHERE email=?
            AND password=?
        """, (
            email,
            password
        ))

        student = cursor.fetchone()
        conn.close()

        if student:
            session["student_id"] = student[0]
            session["student_name"] = student[1]
            return redirect(url_for("dashboard"))

        return render_template(
            "student/login.html",
            error="Invalid email or password."
        )

    return render_template(
        "student/login.html",
        error=None
    )


# ================= STUDENT DASHBOARD =================

@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reason,from_date,to_date,status
        FROM leaves
        WHERE student_id=?
        ORDER BY id DESC
    """, (
        session["student_id"],
    ))

    leaves = cursor.fetchall()

    total = len(leaves)
    pending = 0
    approved = 0
    rejected = 0

    for leave in leaves:
        if leave[3] == "Pending":
            pending += 1
        elif leave[3] == "Approved":
            approved += 1
        elif leave[3] == "Rejected":
            rejected += 1

    cursor.execute("""
        SELECT COUNT(*)
        FROM notifications
        WHERE student_id=?
        AND status='Unread'
    """, (
        session["student_id"],
    ))

    notification_count = cursor.fetchone()[0]
    conn.close()

    return render_template(
        "student/dashboard.html",
        name=session["student_name"],
        leaves=leaves,
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        notification_count=notification_count
    )


# ================= APPLY LEAVE =================

@app.route("/apply_leave", methods=["GET", "POST"])
def apply_leave():
    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        reason = request.form["reason"]
        from_date = request.form["from_date"]
        to_date = request.form["to_date"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leaves
            (student_id,reason,from_date,to_date)
            VALUES(?,?,?,?)
        """, (
            session["student_id"],
            reason,
            from_date,
            to_date
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("student/apply_leave.html")


# ================= PROFILE =================

@app.route("/profile")
def profile():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name,email
        FROM students
        WHERE id=?
    """, (
        session["student_id"],
    ))

    student = cursor.fetchone()
    conn.close()

    return render_template(
        "student/profile.html",
        student=student
    )


# ================= CHANGE PASSWORD =================

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        old = request.form["old_password"].strip()
        new = request.form["new_password"].strip()
        confirm = request.form["confirm_password"].strip()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password
            FROM students
            WHERE id=?
        """, (
            session["student_id"],
        ))

        current = cursor.fetchone()
        errors = []

        if current is None or current[0] != old:
            errors.append("Current Password is incorrect.")

        if new != confirm:
            errors.append(
                "New Password and Confirm Password do not match."
            )

        if errors:
            conn.close()

            return render_template(
                "student/change_password.html",
                errors=errors
            )

        cursor.execute("""
            UPDATE students
            SET password=?
            WHERE id=?
        """, (
            new,
            session["student_id"]
        ))

        conn.commit()
        conn.close()

        return render_template(
            "student/change_password.html",
            success="Password changed successfully!"
        )

    return render_template("student/change_password.html")


# ================= PDF LEAVE REPORT =================

@app.route("/download_report")
def download_report():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name,email
        FROM students
        WHERE id=?
    """, (
        session["student_id"],
    ))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT reason,from_date,to_date,status
        FROM leaves
        WHERE student_id=?
        ORDER BY id DESC
    """, (
        session["student_id"],
    ))

    leaves = cursor.fetchall()
    conn.close()

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        120,
        750,
        "HOSTEL LEAVE MANAGEMENT SYSTEM"
    )

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        50,
        700,
        f"Student Name : {student[0]}"
    )
    pdf.drawString(
        50,
        680,
        f"Email : {student[1]}"
    )

    y = 630

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Reason")
    pdf.drawString(200, y, "From")
    pdf.drawString(300, y, "To")
    pdf.drawString(420, y, "Status")

    y -= 30
    pdf.setFont("Helvetica", 10)

    for leave in leaves:
        pdf.drawString(50, y, str(leave[0]))
        pdf.drawString(200, y, str(leave[1]))
        pdf.drawString(300, y, str(leave[2]))
        pdf.drawString(420, y, str(leave[3]))

        y -= 25

        if y < 50:
            pdf.showPage()
            y = 750
            pdf.setFont("Helvetica", 10)

    pdf.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="leave_report.pdf",
        mimetype="application/pdf"
    )


# ================= NOTIFICATIONS =================

@app.route("/notifications")
def notifications():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET status='Read'
        WHERE student_id=?
    """, (
        session["student_id"],
    ))

    conn.commit()

    cursor.execute("""
        SELECT message,status
        FROM notifications
        WHERE student_id=?
        ORDER BY id DESC
    """, (
        session["student_id"],
    ))

    student_notifications = cursor.fetchall()
    conn.close()

    return render_template(
        "student/notifications.html",
        notifications=student_notifications
    )


# ================= STUDENT LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================================================
#                    ADMIN MODULE
# ==================================================


# ================= WARDEN LOGIN =================

@app.route("/warden/login", methods=["GET", "POST"])
def warden_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template(
                "admin/login.html",
                error="Please enter both username and password."
            )

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )

        admin = cursor.fetchone()
        conn.close()

        if admin:
            session.clear()
            session["warden_id"] = admin[0]
            session["warden_name"] = admin[1]

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )

    return render_template(
        "admin/login.html",
        error=None
    )


# ================= WARDEN DASHBOARD =================

@app.route("/admin/dashboard")
def admin_dashboard():
    if "warden_id" not in session:
        return redirect(url_for("warden_login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            leaves.id,
            students.name,
            students.email,
            leaves.reason,
            leaves.from_date,
            leaves.to_date,
            leaves.status
        FROM leaves
        JOIN students
        ON leaves.student_id = students.id
        ORDER BY leaves.id DESC
    """)

    leaves = cursor.fetchall()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        leaves=leaves
    )


# ================= WARDEN LOGOUT =================

@app.route("/warden/logout")
def warden_logout():
    session.clear()
    return redirect(url_for("warden_login"))


# ================= APPROVE LEAVE =================

@app.route("/admin/approve/<int:id>")
def approve_leave(id):
    if "warden_id" not in session:
        return redirect(url_for("warden_login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id,status
        FROM leaves
        WHERE id=?
    """, (
        id,
    ))

    leave = cursor.fetchone()

    if leave and leave[1] != "Approved":
        student_id = leave[0]

        cursor.execute("""
            UPDATE leaves
            SET status='Approved'
            WHERE id=?
        """, (
            id,
        ))

        cursor.execute("""
            INSERT INTO notifications
            (student_id,message,status)
            VALUES(?,?,?)
        """, (
            student_id,
            "Your leave request has been approved by Warden ✅",
            "Unread"
        ))

        conn.commit()

    conn.close()
    return redirect(url_for("admin_dashboard"))


# ================= REJECT LEAVE =================

@app.route("/admin/reject/<int:id>")
def reject_leave(id):
    if "warden_id" not in session:
        return redirect(url_for("warden_login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id,status
        FROM leaves
        WHERE id=?
    """, (
        id,
    ))

    leave = cursor.fetchone()

    if leave and leave[1] != "Rejected":
        student_id = leave[0]

        cursor.execute("""
            UPDATE leaves
            SET status='Rejected'
            WHERE id=?
        """, (
            id,
        ))

        cursor.execute("""
            INSERT INTO notifications
            (student_id,message,status)
            VALUES(?,?,?)
        """, (
            student_id,
            "Your leave request has been rejected by Warden ❌",
            "Unread"
        ))

        conn.commit()

    conn.close()
    return redirect(url_for("admin_dashboard"))


# ================= ADMIN LOGOUT =================

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("warden_login"))

# ================= MOBILE API =================

@app.route("/api/test")
def api_test():
    return jsonify({
        "success": True,
        "message": "Hostel Leave Management API is working."
    })

@app.route("/api/student/login", methods=["POST"])
def api_student_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email
        FROM students
        WHERE email=?
        AND password=?
    """, (
        email,
        password
    ))

    student = cursor.fetchone()
    conn.close()

    if student:
        return jsonify({
            "success": True,
            "student": {
                "id": student[0],
                "name": student[1],
                "email": student[2]
            }
        })

    return jsonify({
        "success": False,
        "message": "Invalid email or password."
    }), 401
@app.route("/api/student/apply_leave", methods=["POST"])
def api_student_apply_leave():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    student_id = data.get("student_id")
    reason = data.get("reason", "").strip()
    from_date = data.get("from_date", "").strip()
    to_date = data.get("to_date", "").strip()

    if not student_id or not reason or not from_date or not to_date:
        return jsonify({
            "success": False,
            "message": "All leave details are required."
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM students
        WHERE id=?
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    if student is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Student account not found."
        }), 404

    try:
        cursor.execute("""
            INSERT INTO leaves
            (student_id, reason, from_date, to_date, status)
            VALUES(?, ?, ?, ?, ?)
        """, (
            student_id,
            reason,
            from_date,
            to_date,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Leave request submitted successfully."
        }), 201

    except Exception:
        conn.rollback()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Unable to submit leave request."
        }), 500
@app.route("/api/student/dashboard", methods=["POST"])
def api_student_dashboard():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    student_id = data.get("student_id")

    if not student_id:
        return jsonify({
            "success": False,
            "message": "Student ID is required."
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email
        FROM students
        WHERE id=?
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    if student is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Student account not found."
        }), 404

    cursor.execute("""
        SELECT status
        FROM leaves
        WHERE student_id=?
    """, (
        student_id,
    ))

    leaves = cursor.fetchall()
    conn.close()

    total = len(leaves)
    pending = 0
    approved = 0
    rejected = 0

    for leave in leaves:
        status = leave[0]

        if status == "Pending":
            pending += 1
        elif status == "Approved":
            approved += 1
        elif status == "Rejected":
            rejected += 1

    return jsonify({
        "success": True,
        "student": {
            "id": student[0],
            "name": student[1],
            "email": student[2]
        },
        "counts": {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "total": total
        }
    })
    
# ================= INITIALIZE DATABASE =================

init_db()


# ================= RUN APPLICATION =================

if __name__ == "__main__":
    app.run(debug=True)