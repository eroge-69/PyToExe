from flask import Flask, request, redirect, url_for, flash, session, render_template_string
import json, os
from functools import wraps

app = Flask(__name__)
app.secret_key = "inplayhax-secret"

USERS_FILE = 'users.json'
DATA_FILE = 'accounts.json'

DEFAULT_USERS = {
    "admin": {"password": "inplayhax", "role": "admin"},
    "inplayhax": {"password": "admin", "role": "viewer"}
}

def load_users():
    return json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else DEFAULT_USERS.copy()

def save_users(users):
    json.dump(users, open(USERS_FILE, 'w'), indent=4)

def load_accounts():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}

def save_accounts(data):
    json.dump(data, open(DATA_FILE, 'w'), indent=4)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'email' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        user = users.get(email)
        if user and user['password'] == password:
            session['email'] = email
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.")
    return render_template_string(login_template)

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        if not email or not password:
            flash("All fields are required.")
        elif email in users:
            flash("User already exists.")
        else:
            users[email] = {"password": password, "role": "viewer"}
            save_users(users)
            flash("Registration successful. Please login.")
            return redirect(url_for('login'))
    return render_template_string(register_template)

@app.route('/dashboard')
@login_required
def dashboard():
    categories = {
        "cf": "Crossfire Account",
        "work": "Roblox Account",
        "social": "Garena Account"
    }
    return render_template_string(dashboard_template, categories=categories)

@app.route('/vault/<category>', methods=['GET', 'POST'])
@login_required
def vault(category):
    category_names = {
        "cf": "Crossfire Account",
        "work": "Roblox Account",
        "social": "Garena Account"
    }
    accounts = load_accounts()
    display = category_names.get(category, "Unknown")
    filtered = {k: v for k, v in accounts.items() if v.get("category") == category}

    if request.method == 'POST':
        site = request.form['site'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if site and username and password:
            accounts[site] = {"username": username, "password": password, "category": category}
            save_accounts(accounts)
            flash(f"{site} added successfully.")
            return redirect(url_for('vault', category=category))
        else:
            flash("All fields are required.")

    return render_template_string(vault_template, accounts=filtered, display=display, category=category)

@app.route('/delete/<category>/<site>')
@login_required
def delete_account(category, site):
    if session.get("role") != "admin":
        flash("Only admin can delete accounts.")
        return redirect(url_for('vault', category=category))

    accounts = load_accounts()
    if site in accounts:
        del accounts[site]
        save_accounts(accounts)
        flash(f"{site} deleted.")
    return redirect(url_for('vault', category=category))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

# ========== HTML TEMPLATES ==========

login_template = '''
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
<h2>Login</h2>
{% with messages = get_flashed_messages() %}
  {% for m in messages %}<p style="color:red;">{{ m }}</p>{% endfor %}
{% endwith %}
<form method="POST">
    Email: <input name="email"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Login</button>
</form>
<a href="{{ url_for('register') }}">Register</a>
</body>
</html>
'''

register_template = '''
<!DOCTYPE html>
<html>
<head><title>Register</title></head>
<body>
<h2>Register</h2>
{% with messages = get_flashed_messages() %}
  {% for m in messages %}<p style="color:red;">{{ m }}</p>{% endfor %}
{% endwith %}
<form method="POST">
    Email: <input name="email"><br>
    Password: <input type="password" name="password"><br>
    <button type="submit">Register</button>
</form>
<a href="{{ url_for('login') }}">Back to Login</a>
</body>
</html>
'''

dashboard_template = '''
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h2>Welcome, {{ session['email'] }}!</h2>

{% with messages = get_flashed_messages() %}
  {% for m in messages %}<p style="color:green;">{{ m }}</p>{% endfor %}
{% endwith %}

<p>Select a category:</p>
<ul>
  {% for key, label in categories.items() %}
    <li><a href="{{ url_for('vault', category=key) }}">{{ label }}</a></li>
  {% endfor %}
</ul>
<a href="{{ url_for('logout') }}">Logout</a>
</body>
</html>
'''

vault_template = '''
<!DOCTYPE html>
<html>
<head><title>{{ display }}</title></head>
<body>
<h2>{{ display }}</h2>
<a href="{{ url_for('dashboard') }}">Back to Dashboard</a> | 
<a href="{{ url_for('logout') }}">Logout</a>
<br><br>

<form method="POST">
    Website: <input name="site">
    Username: <input name="username">
    Password: <input name="password">
    <button type="submit">Add</button>
</form>

{% with messages = get_flashed_messages() %}
  {% for m in messages %}<p style="color:green;">{{ m }}</p>{% endfor %}
{% endwith %}

<h3>Accounts:</h3>
<ul>
    {% for site, acc in accounts.items() %}
        <li>
            <strong>{{ site }}</strong><br>
            Username: {{ acc["username"] }}<br>
            Password: {{ acc["password"] }}<br>
            {% if session['role'] == 'admin' %}
                <a href="{{ url_for('delete_account', category=category, site=site) }}">Delete</a>
            {% endif %}
        </li><br>
    {% else %}
        <p>No accounts yet.</p>
    {% endfor %}
</ul>
</body>
</html>
'''

# ========== RUN APP ==========
if __name__ == "__main__":
    app.run(debug=True)
