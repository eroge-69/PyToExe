
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "mitarbeiter.db"
EXCEL_PATH = "mitarbeiter.xlsx"

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE mitarbeiter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vorname TEXT,
                name TEXT NOT NULL,
                abteilung TEXT,
                email TEXT
            )
        ''')
        conn.commit()
        conn.close()

def get_all_mitarbeiter():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM mitarbeiter")
    mitarbeiter = c.fetchall()
    conn.close()
    return mitarbeiter

def get_mitarbeiter_by_id(mitarbeiter_id):
    conn = sqlite3.connect(DBATH)
    c = conn.cursor()
    c.execute("SELECT * FROM mitarbeiter WHERE id=?", (mitarbeiter_id,))
    mitarbeiter = c.fetchone()
    conn.close()
    return mitarbeiter

def delete_mitarbeiter(mitarbeiter_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM mitarbeiter WHERE id=?", (mitarbeiter_id,))
    conn.commit()
    conn.close()

def update_mitarbeiter(mitarbeiter_id, vorname, name, abteilung, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE mitarbeiter SET vorname=?, name=?, abteilung=?, email=? WHERE id=?",
              (vorname, name, abteilung, email, mitarbeiter_id))
    conn.commit()
    conn.close()

def add_mitarbeiter(vorname, name, abteilung, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO mitarbeiter (vorname, name, abteilung, email) VALUES (?, ?, ?, ?)",
              (vorname, name, abteilung, email))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    mitarbeiter = get_all_mitarbeiter()
    return render_template("index.html", mitarbeiter=mitarbeiter)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        add_mitarbeiter(request.form["vorname"], request.form["name"],
                        request.form["abteilung"], request.form["email"])
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    m = get_mitarbeiter_by_id(id)
    if request.method == "POST":
        update_mitarbeiter(id, request.form["vorname"], request.form["name"],
                           request.form["abteilung"], request.form["email"])
        return redirect(url_for("index"))
    return render_template("edit.html", mitarbeiter=m)

@app.route("/delete/<int:id>")
def delete(id):
    delete_mitarbeiter(id)
    return redirect(url_for("index"))

init_db()
