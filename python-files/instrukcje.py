import os
import time
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

app = Flask(__name__)
app.secret_key = "tajny_klucz"  # do sesji logowania
UPLOAD_FOLDER = "instrukcje"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
DATA_FOLDER = "dane"
if not os.path.exists(DATA_FOLDER):
    os.mkdir(DATA_FOLDER)

# --- Prosta baza użytkowników i potwierdzeń ---
USERS_FILE = os.path.join(DATA_FOLDER, "users.txt")
CONFIRM_FILE = os.path.join(DATA_FOLDER, "confirmations.txt")
TIME_FILE = os.path.join(DATA_FOLDER, "time_settings.txt")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {"admin": {"password": "admin", "is_admin": True}}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    users = {}
    for line in lines:
        login, password, is_admin = line.strip().split(";")
        users[login] = {"password": password, "is_admin": (is_admin == "1")}
    return users

def save_user(login, password, is_admin):
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{login};{password};{int(is_admin)}\n")

def load_confirmations():
    if not os.path.exists(CONFIRM_FILE):
        return []
    with open(CONFIRM_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split(";") for line in f.readlines()]

def save_confirmation(login, instrukcja, timestamp):
    with open(CONFIRM_FILE, "a", encoding="utf-8") as f:
        f.write(f"{login};{instrukcja};{timestamp}\n")

def get_time_settings():
    if not os.path.exists(TIME_FILE):
        return {}
    with open(TIME_FILE, "r", encoding="utf-8") as f:
        return dict(line.strip().split(";") for line in f.readlines())

def save_time_setting(filename, seconds):
    with open(TIME_FILE, "a", encoding="utf-8") as f:
        f.write(f"{filename};{seconds}\n")

@app.route("/", methods=["GET", "POST"])
def login():
    users = load_users()
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        if login in users and users[login]["password"] == password:
            session["login"] = login
            session["is_admin"] = users[login]["is_admin"]
            return redirect(url_for("panel"))
        else:
            return render_template_string(LOGIN_HTML, error="Błędny login lub hasło")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/panel")
def panel():
    if "login" not in session:
        return redirect(url_for("login"))
    files = os.listdir(UPLOAD_FOLDER)
    confirm = load_confirmations()
    confirmed = [c for c in confirm if c[0] == session["login"]]
    if session.get("is_admin"):
        return render_template_string(ADMIN_PANEL, files=files, users=load_users(), confirm=confirm)
    else:
        return render_template_string(USER_PANEL, files=files, confirmed=[c[1] for c in confirmed])

@app.route("/add_user", methods=["POST"])
def add_user():
    if not session.get("is_admin"):
        return redirect(url_for("panel"))
    login = request.form["new_login"]
    password = request.form["new_password"]
    save_user(login, password, False)
    return redirect(url_for("panel"))

@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("panel"))
    file = request.files["file"]
    min_time = int(request.form["min_time"])
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    save_time_setting(filename, min_time)
    return redirect(url_for("panel"))

@app.route("/instrukcja/<filename>")
def instrukcja(filename):
    if "login" not in session:
        return redirect(url_for("login"))
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    time_settings = get_time_settings()
    min_time = int(time_settings.get(filename, 20))
    return render_template_string(VIEWER_HTML, filename=filename, num_pages=num_pages, min_time=min_time)

@app.route("/pdf/<filename>")
def pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/potwierdz/<filename>")
def potwierdz(filename):
    if "login" not in session:
        return redirect(url_for("login"))
    save_confirmation(session["login"], filename, str(int(time.time())))
    return redirect(url_for("panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- HTML templates (w uproszczeniu) ---
LOGIN_HTML = """
<!doctype html>
<title>Logowanie</title>
<h2>Logowanie</h2>
<form method=post>
  Login: <input name=login required>
  Hasło: <input type=password name=password required>
  <input type=submit value="Zaloguj">
</form>
{% if error %}<p style="color:red;">{{error}}</p>{% endif %}
"""

ADMIN_PANEL = """
<!doctype html>
<title>Panel Admina</title>
<h2>Panel Administratora</h2>
<a href="/logout">Wyloguj</a><br>
<h3>Dodaj pracownika</h3>
<form method=post action="/add_user">
  Login: <input name=new_login required>
  Hasło: <input type=password name=new_password required>
  <input type=submit value="Dodaj">
</form>
<h3>Wgraj instrukcję PDF</h3>
<form method=post enctype=multipart/form-data action="/upload">
  Plik PDF: <input type=file name=file required>
  Minimalny czas na stronę (sekundy): <input type=number name=min_time value=20 min=5 required>
  <input type=submit value="Wgraj">
</form>
<h3>Lista instrukcji:</h3>
<ul>
{% for f in files %}
  <li>{{f}}</li>
{% endfor %}
</ul>
<h3>Raport potwierdzeń:</h3>
<table border=1>
<tr><th>Pracownik</th><th>Instrukcja</th><th>Czas potwierdzenia</th></tr>
{% for c in confirm %}
<tr>
<td>{{c[0]}}</td><td>{{c[1]}}</td><td>{{c[2]}}</td>
</tr>
{% endfor %}
</table>
"""

USER_PANEL = """
<!doctype html>
<title>Panel Pracownika</title>
<h2>Panel Pracownika</h2>
<a href="/logout">Wyloguj</a><br>
<h3>Instrukcje do przeczytania:</h3>
<ul>
{% for f in files %}
  <li>
    {{f}} 
    {% if f not in confirmed %}
      <a href="/instrukcja/{{f}}">Przeczytaj</a>
    {% else %}
      ✔️ przeczytana
    {% endif %}
  </li>
{% endfor %}
</ul>
"""

# Wyświetlanie PDF w przeglądarce – prosta blokada czasu
VIEWER_HTML = """
<!doctype html>
<title>Instrukcja PDF</title>
<h2>Instrukcja: {{filename}}</h2>
<div id="pdf-viewer"></div>
<div>
  <button id="next-page" disabled>Dalej</button>
  <span id="timer"></span>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.13.216/pdf.min.js"></script>
<script>
let pdfDoc = null;
let pageNum = 1;
let numPages = {{num_pages}};
let minTime = {{min_time}};
let timer = minTime;
let allowNext = false;

function loadPage(num) {
  allowNext = false;
  document.getElementById("next-page").disabled = true;
  timer = minTime;
  document.getElementById("timer").innerText = "Odliczanie: " + timer + " s";
  let loadingTask = pdfjsLib.getDocument("/pdf/{{filename}}");
  loadingTask.promise.then(function(pdf) {
    pdfDoc = pdf;
    pdf.getPage(num).then(function(page) {
      let scale = 1.2;
      let viewport = page.getViewport({scale: scale});
      let canvas = document.createElement("canvas");
      let context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      page.render({canvasContext: context, viewport: viewport});
      let viewer = document.getElementById("pdf-viewer");
      viewer.innerHTML = "";
      viewer.appendChild(canvas);
    });
  });
  let interval = setInterval(function(){
    timer -= 1;
    document.getElementById("timer").innerText = "Odliczanie: " + timer + " s";
    if (timer <= 0) {
      clearInterval(interval);
      allowNext = true;
      document.getElementById("next-page").disabled = false;
      document.getElementById("timer").innerText = "Możesz przejść dalej";
    }
  }, 1000);
}

document.addEventListener("DOMContentLoaded", function() {
  loadPage(pageNum);
  document.getElementById("next-page").addEventListener("click", function() {
    if (!allowNext) return;
    if (pageNum < numPages) {
      pageNum += 1;
      loadPage(pageNum);
    } else {
      window.location = "/potwierdz/{{filename}}";
    }
  });
});
</script>
"""

if __name__ == "__main__":
    app.run(debug=True)
