from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import os
import qrcode

from io import BytesIO
from reportlab.pdfgen import canvas



app = Flask(__name__)

app.secret_key = "hostel_management_secret"




# ================= DATABASE =================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR,"hostel.db")




def get_db():

    return sqlite3.connect(DATABASE)







# ================= INITIALIZE DATABASE =================


def init_db():

    conn = get_db()

    cursor = conn.cursor()



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





    # Default Admin


    cursor.execute(
        "SELECT * FROM admins WHERE username=?",
        ("warden",)
    )


    admin = cursor.fetchone()



    if admin is None:


        cursor.execute(
        "SELECT * FROM admins WHERE username=?",
        ("warden",)
    )

    admin = cursor.fetchone()

    # Insert only if not exists
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


@app.route("/register", methods=["GET","POST"])
def register():


    if request.method=="POST":


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

            """,
            (
                name,
                email,
                password
            ))



            conn.commit()



        except sqlite3.IntegrityError:


            conn.close()

            return "Email already registered"




        conn.close()



        return redirect(url_for("login"))




    return render_template("student/register.html")










# ================= STUDENT LOGIN =================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Empty fields check
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
        """,
        (
            email,
            password
        ))

        student = cursor.fetchone()

        conn.close()

        # Login Success
        if student:

            session["student_id"] = student[0]
            session["student_name"] = student[1]

            return redirect(url_for("dashboard"))

        # Login Failed
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



    conn=get_db()

    cursor=conn.cursor()




    cursor.execute("""
    SELECT reason,from_date,to_date,status

    FROM leaves

    WHERE student_id=?

    ORDER BY id DESC

    """,
    (
        session["student_id"],
    ))



    leaves=cursor.fetchall()




    total=len(leaves)

    pending=0

    approved=0

    rejected=0




    for leave in leaves:


        if leave[3]=="Pending":

            pending+=1


        elif leave[3]=="Approved":

            approved+=1


        elif leave[3]=="Rejected":

            rejected+=1






    # Unread notification count


    cursor.execute("""
    SELECT COUNT(*)

    FROM notifications

    WHERE student_id=?

    AND status='Unread'

    """,
    (
        session["student_id"],
    ))



    notification_count=cursor.fetchone()[0]



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


@app.route("/apply_leave",methods=["GET","POST"])
def apply_leave():


    if "student_id" not in session:

        return redirect(url_for("login"))




    if request.method=="POST":


        reason=request.form["reason"]

        from_date=request.form["from_date"]

        to_date=request.form["to_date"]




        conn=get_db()

        cursor=conn.cursor()



        cursor.execute("""
        INSERT INTO leaves

        (student_id,reason,from_date,to_date)

        VALUES(?,?,?,?)

        """,
        (
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




    conn=get_db()

    cursor=conn.cursor()



    cursor.execute("""
    SELECT name,email

    FROM students

    WHERE id=?

    """,
    (
        session["student_id"],
    ))



    student=cursor.fetchone()



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
        """,
        (
            session["student_id"],
        ))

        current = cursor.fetchone()

        # =========================
        # VALIDATION
        # =========================

        errors = []

        # Current password check
        if current[0] != old:
            errors.append("Current Password is incorrect.")

        # New password & confirm password check
        if new != confirm:
            errors.append("New Password and Confirm Password do not match.")

        # If any error exists
        if errors:

            conn.close()

            return render_template(
                "student/change_password.html",
                errors=errors
            )

        # =========================
        # UPDATE PASSWORD
        # =========================

        cursor.execute("""
            UPDATE students
            SET password=?
            WHERE id=?
        """,
        (
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




    conn=get_db()

    cursor=conn.cursor()



    cursor.execute("""
    SELECT name,email

    FROM students

    WHERE id=?

    """,
    (
        session["student_id"],
    ))



    student=cursor.fetchone()






    cursor.execute("""
    SELECT reason,from_date,to_date,status

    FROM leaves

    WHERE student_id=?

    ORDER BY id DESC

    """,
    (
        session["student_id"],
    ))



    leaves=cursor.fetchall()



    conn.close()



    pdf_buffer=BytesIO()



    pdf=canvas.Canvas(pdf_buffer)





    pdf.setFont(
        "Helvetica-Bold",
        18
    )



    pdf.drawString(
        120,
        750,
        "HOSTEL LEAVE MANAGEMENT SYSTEM"
    )




    pdf.setFont(
        "Helvetica",
        12
    )



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



    y=630



    pdf.setFont(
        "Helvetica-Bold",
        12
    )


    pdf.drawString(50,y,"Reason")

    pdf.drawString(200,y,"From")

    pdf.drawString(300,y,"To")

    pdf.drawString(420,y,"Status")



    y-=30




    pdf.setFont(
        "Helvetica",
        10
    )



    for leave in leaves:


        pdf.drawString(50,y,str(leave[0]))

        pdf.drawString(200,y,str(leave[1]))

        pdf.drawString(300,y,str(leave[2]))

        pdf.drawString(420,y,str(leave[3]))


        y-=25




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




    conn=get_db()

    cursor=conn.cursor()



    # Mark notifications as read


    cursor.execute("""
    UPDATE notifications

    SET status='Read'

    WHERE student_id=?

    """,
    (
        session["student_id"],
    ))



    conn.commit()





    cursor.execute("""
    SELECT message,status

    FROM notifications

    WHERE student_id=?

    ORDER BY id DESC

    """,
    (
        session["student_id"],
    ))



    notifications=cursor.fetchall()



    conn.close()




    return render_template(

        "student/notifications.html",

        notifications=notifications

    )








# ================= STUDENT LOGOUT =================


@app.route("/logout")
def logout():


    session.clear()


    return redirect(url_for("login"))











# ==================================================
#                    ADMIN MODULE
# ==================================================





# ================= ADMIN LOGIN =================


# ================= WARDEN LOGIN =================

@app.route("/warden/login", methods=["GET", "POST"])
def warden_login():

    print("WARDEN PAGE OPENED")

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        print("Entered Username:", username)
        print("Entered Password:", password)

        # Empty fields check
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

        print("DB Result:", admin)

        conn.close()

        # Login Success
        if admin:

            session.clear()

            session["warden_id"] = admin[0]
            session["warden_name"] = admin[1]

            print("✅ LOGIN SUCCESS")

            return redirect(url_for("admin_dashboard"))

        # Login Failed
        print("❌ LOGIN FAILED")

        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )

    return render_template(
        "admin/login.html",
        error=None
    )



# ================= ADMIN DASHBOARD =================


# ================= WARDEN DASHBOARD =================

@app.route("/admin/dashboard")
def admin_dashboard():

    # ✅ Correct session check
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

    return render_template("admin/dashboard.html", leaves=leaves)
# ================= WARDEN LOGOUT =================

@app.route("/warden/logout")
def warden_logout():

    session.clear()

    return redirect(url_for("warden_login"))   # ✅ correct
# ================= APPROVE LEAVE =================


@app.route("/admin/approve/<int:id>")
def approve_leave(id):


    conn=get_db()

    cursor=conn.cursor()




    cursor.execute("""
    SELECT student_id,status

    FROM leaves

    WHERE id=?

    """,
    (
        id,
    ))



    leave=cursor.fetchone()





    if leave and leave[1]!="Approved":



        student_id=leave[0]




        cursor.execute("""
        UPDATE leaves

        SET status='Approved'

        WHERE id=?

        """,
        (
            id,
        ))





        cursor.execute("""
        INSERT INTO notifications

        (student_id,message,status)

        VALUES(?,?,?)

        """,
        (
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


    conn=get_db()

    cursor=conn.cursor()




    cursor.execute("""
    SELECT student_id,status

    FROM leaves

    WHERE id=?

    """,
    (
        id,
    ))



    leave=cursor.fetchone()





    if leave and leave[1]!="Rejected":



        student_id=leave[0]




        cursor.execute("""
        UPDATE leaves

        SET status='Rejected'

        WHERE id=?

        """,
        (
            id,
        ))





        cursor.execute("""
        INSERT INTO notifications

        (student_id,message,status)

        VALUES(?,?,?)

        """,
        (
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












# ================= INITIALIZE DATABASE =================

init_db()


# ================= RUN APPLICATION =================

if __name__ == "__main__":
    app.run(debug=True)