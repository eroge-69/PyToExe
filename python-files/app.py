from flask import Flask, render_template, request, redirect, url_for, send_file, session, abort
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os
import io
import base64

# Optional: barcode (Code128) for print slip
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except Exception:
    BARCODE_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ==========================
# DB Helpers
# ==========================
DB_PATH = "visitors.db"

def get_conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purpose TEXT NOT NULL,
            contact TEXT,
            city TEXT,
            status TEXT,
            who_to_meet TEXT,
            in_time TEXT,
            out_time TEXT
        )
    """)
    # Add column if old DB
    try:
        cur.execute("ALTER TABLE visitors ADD COLUMN who_to_meet TEXT")
    except:
        pass
    con.commit()
    con.close()

init_db()

# ==========================
# Auth
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("intro"))
        error = "Invalid Username or Password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# ==========================
# Intro Page
# ==========================
@app.route("/intro")
def intro():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("intro.html")

# ==========================
# Dashboard / List
# ==========================
@app.route("/")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM visitors ORDER BY id DESC")
    records = cur.fetchall()
    con.close()
    return render_template("list.html", records=records)

# ==========================
# Add Visitor
# ==========================
@app.route("/add", methods=["POST"])
def add_visitor():
    if not session.get("admin"):
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    purpose = request.form.get("purpose", "").strip()
    contact = request.form.get("contact", "").strip()
    city = request.form.get("city", "").strip()
    who_to_meet = request.form.get("who_to_meet", "").strip()
    in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not name or not purpose:
        abort(400, "Name and Purpose are required")

    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO visitors (name, purpose, contact, city, status, who_to_meet, in_time, out_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, purpose, contact, city, "Inside", who_to_meet, in_time, None))
    visitor_id = cur.lastrowid
    con.commit()
    con.close()

    return redirect(url_for("print_slip", visitor_id=visitor_id))

# ==========================
# Checkout Visitor
# ==========================
@app.route("/checkout/<int:visitor_id>")
def checkout(visitor_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = get_conn()
    cur = con.cursor()
    cur.execute("UPDATE visitors SET status=?, out_time=? WHERE id=?",
                ("Checked Out", out_time, visitor_id))
    con.commit()
    con.close()
    return redirect(url_for("dashboard"))

# ==========================
# Print Slip (with barcode)
# ==========================
def generate_barcode_base64(data_str: str) -> str:
    if not BARCODE_AVAILABLE:
        return ""
    code = barcode.get('code128', data_str, writer=ImageWriter())
    buf = io.BytesIO()
    code.write(buf, options={"module_height": 15.0, "font_size": 10, "text_distance": 1})
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@app.route("/print/<int:visitor_id>")
def print_slip(visitor_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM visitors WHERE id=?", (visitor_id,))
    visitor = cur.fetchone()
    con.close()

    if not visitor:
        abort(404, "Visitor not found")

    return render_template("print_slip.html", visitor=visitor)

# ==========================
# Export (Excel / PDF) with date filter
# ==========================
def _export_excel_path() -> str:
    return "visitors.xlsx"

@app.route("/export/excel")
@app.route("/export_excel")
def export_excel():
    if not session.get("admin"):
        return redirect(url_for("login"))

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    con = get_conn()
    query = "SELECT * FROM visitors WHERE 1=1"
    params = []
    if from_date:
        query += " AND date(in_time) >= ?"
        params.append(from_date)
    if to_date:
        query += " AND date(in_time) <= ?"
        params.append(to_date)
    query += " ORDER BY id DESC"

    df = pd.read_sql_query(query, con, params=params)
    con.close()

    fp = _export_excel_path()
    df.to_excel(fp, index=False)
    return send_file(fp, as_attachment=True)

@app.route("/export/pdf")
@app.route("/export_pdf")
def export_pdf():
    if not session.get("admin"):
        return redirect(url_for("login"))

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    con = get_conn()
    cur = con.cursor()
    query = "SELECT * FROM visitors WHERE 1=1"
    params = []
    if from_date:
        query += " AND date(in_time) >= ?"
        params.append(from_date)
    if to_date:
        query += " AND date(in_time) <= ?"
        params.append(to_date)
    query += " ORDER BY id DESC"

    cur.execute(query, params)
    visitors = cur.fetchall()
    con.close()

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Visitor Report", ln=True, align="C")
    pdf.ln(5)

    # Header
    pdf.set_font("Arial", "B", 9)
    headers = ["Pass No", "Name", "Purpose", "Who to Meet", "Contact", "City", "Status", "In Time", "Out Time"]
    col_w = [12, 28, 28, 30, 22, 18, 22, 30, 30]
    for w, h in zip(col_w, headers):
        pdf.cell(w, 8, h, border=1, align="C")
    pdf.ln(8)

    # Rows
    pdf.set_font("Arial", "", 8)
    for v in visitors:
        pdf.cell(col_w[0], 7, str(v["id"]), border=1)
        pdf.cell(col_w[1], 7, str(v["name"])[:18], border=1)
        pdf.cell(col_w[2], 7, str(v["purpose"])[:18], border=1)
        pdf.cell(col_w[3], 7, str(v["who_to_meet"] or ""), border=1)
        pdf.cell(col_w[4], 7, str(v["contact"] or ""), border=1)
        pdf.cell(col_w[5], 7, str(v["city"] or ""), border=1)
        pdf.cell(col_w[6], 7, str(v["status"] or ""), border=1)
        pdf.cell(col_w[7], 7, str(v["in_time"] or ""), border=1)
        pdf.cell(col_w[8], 7, str(v["out_time"] or ""), border=1)
        pdf.ln(7)

    file_path = "visitors.pdf"
    pdf.output(file_path)
    return send_file(file_path, as_attachment=True)

# ==========================
# Delete Visitor
# ==========================
@app.route("/delete/<int:visitor_id>")
def delete_visitor(visitor_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    con = get_conn()
    cur = con.cursor()
    cur.execute("DELETE FROM visitors WHERE id=?", (visitor_id,))
    con.commit()
    con.close()
    return redirect(url_for("dashboard"))

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
