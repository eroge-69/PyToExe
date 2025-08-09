from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'το_μυστικό_σου_εδώ'
bcrypt = Bcrypt(app)

DATABASE = 'services.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        user_email TEXT NOT NULL,
        datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        seen BOOLEAN DEFAULT 0,
        FOREIGN KEY(service_id) REFERENCES services(id)
    );
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user = session.get('user_fullname')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT services.*, users.fullname FROM services
        JOIN users ON services.user_id = users.id
    ''')
    services = cursor.fetchall()
    conn.close()
    return render_template('home.html', user=user, services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)',
                           (fullname, email, hashed_pw))
            conn.commit()
            flash('Εγγραφή επιτυχής! Μπορείτε τώρα να συνδεθείτε.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Το email υπάρχει ήδη.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_fullname'] = user['fullname']
            flash('Επιτυχής σύνδεση!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Λάθος email ή κωδικός.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Αποσυνδεθήκατε.', 'info')
    return redirect(url_for('home'))

@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείτε για να προσθέσετε υπηρεσία.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        user_id = session['user_id']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO services (user_id, name, description, price) VALUES (?, ?, ?, ?)',
                       (user_id, name, description, price))
        conn.commit()
        conn.close()
        flash('Υπηρεσία προστέθηκε!', 'success')
        return redirect(url_for('home'))

    return render_template('add_service.html')

@app.route('/book/<int:service_id>', methods=['GET', 'POST'])
def book_service(service_id):
    if request.method == 'POST':
        user_email = request.form['email']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO bookings (service_id, user_email) VALUES (?, ?)',
                       (service_id, user_email))
        conn.commit()
        conn.close()
        flash('Η κράτησή σας καταχωρήθηκε!', 'success')
        return redirect(url_for('home'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = cursor.fetchone()
    conn.close()
    if not service:
        flash('Η υπηρεσία δεν βρέθηκε.', 'danger')
        return redirect(url_for('home'))

    return render_template('book_service.html', service=service)

@app.route('/new_bookings_count')
def new_bookings_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE seen = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify({"new_count": count})

@app.route('/owner_bookings')
def owner_bookings():
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείτε.', 'warning')
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.*, services.name AS service_name, users.fullname AS owner_name 
        FROM bookings
        JOIN services ON bookings.service_id = services.id
        JOIN users ON services.user_id = users.id
        WHERE services.user_id = ?
        ORDER BY bookings.datetime DESC
    ''', (session['user_id'],))
    bookings = cursor.fetchall()

    cursor.execute("UPDATE bookings SET seen = 1 WHERE seen = 0 AND service_id IN (SELECT id FROM services WHERE user_id = ?)", (session['user_id'],))
    conn.commit()
    conn.close()

    return render_template('owner_bookings.html', bookings=bookings)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
