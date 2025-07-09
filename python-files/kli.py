import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
DATABASE = 'military_training.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        clearance TEXT NOT NULL DEFAULT 'none'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soldier_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS literature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        security_level TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        location TEXT,
        unit_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        type_id INTEGER NOT NULL,
        FOREIGN KEY (unit_id) REFERENCES units (id),
        FOREIGN KEY (category_id) REFERENCES soldier_categories (id),
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        FOREIGN KEY (type_id) REFERENCES activity_types (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_literature (
        activity_id INTEGER,
        literature_id INTEGER,
        PRIMARY KEY (activity_id, literature_id),
        FOREIGN KEY (activity_id) REFERENCES activities (id),
        FOREIGN KEY (literature_id) REFERENCES literature (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_equipment (
        activity_id INTEGER,
        equipment_id INTEGER,
        PRIMARY KEY (activity_id, equipment_id),
        FOREIGN KEY (activity_id) REFERENCES activities (id),
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    if not admin:
        password_hash = generate_password_hash('admin')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, clearance) VALUES (?, ?, ?, ?)",
            ('admin', password_hash, 'admin', 'special_importance')
        )

    test_data = [
        ('units', ['name', 'description'], [
            ('Рота связи', 'Подразделение связи и коммуникаций'),
            ('Инженерная рота', 'Инженерно-саперное подразделение')
        ]),
        ('soldier_categories', ['name'], [
            ('Офицерский состав',),
            ('Сержантский состав',),
            ('Рядовой состав',)
        ]),
        ('subjects', ['name'], [
            ('Тактическая подготовка',),
            ('Огневая подготовка',),
            ('Специальная подготовка',)
        ]),
        ('activity_types', ['name'], [
            ('Учетное занятие',),
            ('Выезд на полигон',),
            ('Тактические учения',),
            ('Практические занятия',)
        ]),
        ('literature', ['title', 'author', 'security_level'], [
            ('Боевой устав Сухопутных войск', 'Минобороны', 'secret'),
            ('Инструкция по радиоэлектронной борьбе', 'Генштаб', 'top_secret'),
            ('Спецоперации в современных конфликтах', 'Центр спецназначения', 'special_importance')
        ]),
        ('equipment', ['name', 'description'], [
            ('Танк Т-90', 'Основной боевой танк'),
            ('БТР-82А', 'Бронетранспортер'),
            ('Комплекс связи Р-168', 'Цифровой комплекс связи')
        ])
    ]

    for table, columns, data in test_data:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        if cursor.fetchone()[0] == 0:
            placeholders = ', '.join(['?'] * len(columns))
            cursor.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                data
            )

    db.commit()


def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Пожалуйста, войдите в систему", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def clearance_required(required_level):
    def decorator(f):
        @login_required
        def wrapper(*args, **kwargs):
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT clearance FROM users WHERE id = ?", (session['user_id'],))
            user_clearance = cursor.fetchone()[0]

            clearance_levels = ['none', 'secret', 'top_secret', 'special_importance']
            user_level = clearance_levels.index(user_clearance)
            required_idx = clearance_levels.index(required_level)

            if user_level < required_idx:
                flash("Недостаточный уровень доступа", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Заполните все поля", "danger")
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['clearance'] = user['clearance']
            flash("Вы успешно вошли в систему", "success")
            return redirect(url_for('index'))
        else:
            flash("Неверное имя пользователя или пароль", "danger")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Вы вышли из системы", "info")
    return redirect(url_for('login'))


@app.route('/units')
@clearance_required('secret')
def units():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM units")
    units = cursor.fetchall()
    return render_template('units.html', units=units)


@app.route('/add_unit', methods=['GET', 'POST'])
@clearance_required('special_importance')
def add_unit():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash("Название обязательно", "danger")
            return redirect(url_for('add_unit'))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO units (name, description) VALUES (?, ?)",
                (name, description)
            )
            db.commit()
            flash("Подразделение успешно добавлено", "success")
            return redirect(url_for('units'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при добавлении подразделения: {str(e)}", "danger")

    return render_template('add_unit.html')


@app.route('/activities')
@clearance_required('secret')
def activities():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
    SELECT 
        activities.id, 
        activities.date, 
        activities.location,
        units.name AS unit_name,
        soldier_categories.name AS category_name,
        subjects.name AS subject_name,
        activity_types.name AS type_name
    FROM activities
    JOIN units ON activities.unit_id = units.id
    JOIN soldier_categories ON activities.category_id = soldier_categories.id
    JOIN subjects ON activities.subject_id = subjects.id
    JOIN activity_types ON activities.type_id = activity_types.id
    ORDER BY activities.date DESC
    ''')
    activities = cursor.fetchall()

    activity_literature = {}
    cursor.execute('''
    SELECT 
        activity_literature.activity_id,
        literature.title,
        literature.security_level
    FROM activity_literature
    JOIN literature ON activity_literature.literature_id = literature.id
    ''')
    for row in cursor.fetchall():
        activity_id = row['activity_id']
        if activity_id not in activity_literature:
            activity_literature[activity_id] = []
        activity_literature[activity_id].append(f"{row['title']} ({row['security_level']})")

    activity_equipment = {}
    cursor.execute('''
    SELECT 
        activity_equipment.activity_id,
        equipment.name
    FROM activity_equipment
    JOIN equipment ON activity_equipment.equipment_id = equipment.id
    ''')
    for row in cursor.fetchall():
        activity_id = row['activity_id']
        if activity_id not in activity_equipment:
            activity_equipment[activity_id] = []
        activity_equipment[activity_id].append(row['name'])

    return render_template(
        'activities.html',
        activities=activities,
        activity_literature=activity_literature,
        activity_equipment=activity_equipment
    )


@app.route('/literature')
@clearance_required('secret')
def literature():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM literature ORDER BY title")
    literature = cursor.fetchall()
    return render_template('literature.html', literature=literature)


@app.route('/equipment')
@clearance_required('secret')
def equipment():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM equipment ORDER BY name")
    equipment = cursor.fetchall()
    return render_template('equipment.html', equipment=equipment)


@app.route('/add_activity', methods=['GET', 'POST'])
@clearance_required('secret')
def add_activity():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            cursor.execute('''
            INSERT INTO activities (date, location, unit_id, category_id, subject_id, type_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form.get('date'),
                request.form.get('location'),
                request.form.get('unit'),
                request.form.get('category'),
                request.form.get('subject'),
                request.form.get('type')
            ))
            activity_id = cursor.lastrowid

            for lit_id in request.form.getlist('literature'):
                cursor.execute(
                    "INSERT INTO activity_literature (activity_id, literature_id) VALUES (?, ?)",
                    (activity_id, lit_id)
                )

            for eq_id in request.form.getlist('equipment'):
                cursor.execute(
                    "INSERT INTO activity_equipment (activity_id, equipment_id) VALUES (?, ?)",
                    (activity_id, eq_id)
                )

            db.commit()
            flash("Занятие успешно добавлено", "success")
            return redirect(url_for('activities'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при добавлении занятия: {str(e)}", "danger")

    units = cursor.execute("SELECT * FROM units ORDER BY name").fetchall()
    categories = cursor.execute("SELECT * FROM soldier_categories ORDER BY name").fetchall()
    subjects = cursor.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    types = cursor.execute("SELECT * FROM activity_types ORDER BY name").fetchall()
    literature = cursor.execute("SELECT * FROM literature ORDER BY title").fetchall()
    equipment = cursor.execute("SELECT * FROM equipment ORDER BY name").fetchall()

    return render_template(
        'add_activity.html',
        units=units,
        categories=categories,
        subjects=subjects,
        types=types,
        literature=literature,
        equipment=equipment
    )


@app.route('/add_literature', methods=['GET', 'POST'])
@clearance_required('special_importance')
def add_literature():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        security_level = request.form.get('security_level')

        if not title or not security_level:
            flash("Заполните обязательные поля", "danger")
            return redirect(url_for('add_literature'))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO literature (title, author, security_level) VALUES (?, ?, ?)",
                (title, author, security_level)
            )
            db.commit()
            flash("Литература успешно добавлена", "success")
            return redirect(url_for('literature'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при добавлении литературы: {str(e)}", "danger")

    return render_template('add_literature.html')


@app.route('/add_equipment', methods=['GET', 'POST'])
@clearance_required('special_importance')
def add_equipment():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash("Название обязательно", "danger")
            return redirect(url_for('add_equipment'))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO equipment (name, description) VALUES (?, ?)",
                (name, description)
            )
            db.commit()
            flash("Техника успешно добавлена", "success")
            return redirect(url_for('equipment'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при добавлении техники: {str(e)}", "danger")

    return render_template('add_equipment.html')


@app.route('/add_subject', methods=['GET', 'POST'])
@clearance_required('special_importance')
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash("Название обязательно", "danger")
            return redirect(url_for('add_subject'))

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO subjects (name) VALUES (?)",
                (name,)
            )
            db.commit()
            flash("Дисциплина успешно добавлена", "success")
            return redirect(url_for('add_activity'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при добавлении дисциплины: {str(e)}", "danger")

    return render_template('add_subject.html')


@app.route('/register', methods=['GET', 'POST'])
@clearance_required('special_importance')
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        clearance = request.form.get('clearance')

        if not username or not password:
            flash("Заполните все обязательные поля", "danger")
            return redirect(url_for('register'))

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                flash("Имя пользователя уже занято", "danger")
                return redirect(url_for('register'))

            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, clearance) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, clearance)
            )
            db.commit()

            flash("Пользователь успешно зарегистрирован", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            flash(f"Ошибка при регистрации: {str(e)}", "danger")

    return render_template('register.html')


@app.context_processor
def inject_user():
    if 'user_id' in session:
        return {
            'current_user': {
                'id': session['user_id'],
                'username': session['username'],
                'role': session['role'],
                'clearance': session['clearance']
            }
        }
    return {'current_user': None}


templates = {
    'base.html': '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Военный учет - {% block title %}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .table-container {
            max-height: 600px;
            overflow-y: auto;
        }
        .sticky-header {
            position: sticky;
            top: 0;
            background-color: #f8f9fa;
            z-index: 100;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">Учет подготовки</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('units') }}">Подразделения</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('activities') }}">Занятия</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('literature') }}">Литература</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('equipment') }}">Техника</a></li>
                    {% if current_user and current_user.role == 'admin' %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('register') }}">Регистрация</a></li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if current_user %}
                    <li class="nav-item"><span class="navbar-text">Пользователь: {{ current_user.username }} ({{ current_user.role }})</span></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">Выйти</a></li>
                    {% else %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Войти</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'index.html': '''{% extends "base.html" %}
{% block title %}Главная страница{% endblock %}
{% block content %}
<h1 class="mb-4">Система учета подготовки подразделений</h1>
<div class="row">
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">Подразделения</h5>
                <p class="card-text">Управление воинскими подразделениями</p>
                <a href="{{ url_for('units') }}" class="btn btn-primary">Перейти</a>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">Учебные занятия</h5>
                <p class="card-text">Учет проведенных занятий</p>
                <a href="{{ url_for('activities') }}" class="btn btn-primary">Перейти</a>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">Ресурсы</h5>
                <p class="card-text">Литература и техника</p>
                <div class="d-flex gap-2">
                    <a href="{{ url_for('literature') }}" class="btn btn-primary">Литература</a>
                    <a href="{{ url_for('equipment') }}" class="btn btn-primary">Техника</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'login.html': '''{% extends "base.html" %}
{% block title %}Вход в систему{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <h2 class="mb-4">Авторизация</h2>
        <form method="POST" action="{{ url_for('login') }}">
            <div class="mb-3">
                <label for="username" class="form-label">Имя пользователя</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Войти</button>
        </form>
    </div>
</div>
{% endblock %}''',

    'units.html': '''{% extends "base.html" %}
{% block title %}Подразделения{% endblock %}
{% block content %}
<h2 class="mb-4">Список подразделений</h2>
{% if current_user.clearance == 'special_importance' %}
<a href="{{ url_for('add_unit') }}" class="btn btn-success mb-3">Добавить подразделение</a>
{% endif %}
<div class="table-container">
    <table class="table table-striped">
        <thead class="sticky-header">
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Описание</th>
            </tr>
        </thead>
        <tbody>
            {% for unit in units %}
            <tr>
                <td>{{ unit['id'] }}</td>
                <td>{{ unit['name'] }}</td>
                <td>{{ unit['description'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'activities.html': '''{% extends "base.html" %}
{% block title %}Учебные занятия{% endblock %}
{% block content %}
<h2 class="mb-4">Учет занятий</h2>
<a href="{{ url_for('add_activity') }}" class="btn btn-success mb-3">Добавить занятие</a>
<div class="table-container">
    <table class="table table-striped">
        <thead class="sticky-header">
            <tr>
                <th>Дата</th>
                <th>Подразделение</th>
                <th>Категория</th>
                <th>Дисциплина</th>
                <th>Тип занятия</th>
                <th>Место</th>
                <th>Литература</th>
                <th>Техника</th>
            </tr>
        </thead>
        <tbody>
            {% for activity in activities %}
            <tr>
                <td>{{ activity['date'] }}</td>
                <td>{{ activity['unit_name'] }}</td>
                <td>{{ activity['category_name'] }}</td>
                <td>{{ activity['subject_name'] }}</td>
                <td>{{ activity['type_name'] }}</td>
                <td>{{ activity['location'] }}</td>
                <td>
                    {% if activity['id'] in activity_literature %}
                        {{ activity_literature[activity['id']]|join('<br>')|safe }}
                    {% endif %}
                </td>
                <td>
                    {% if activity['id'] in activity_equipment %}
                        {{ activity_equipment[activity['id']]|join('<br>')|safe }}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'literature.html': '''{% extends "base.html" %}
{% block title %}Литература{% endblock %}
{% block content %}
<h2 class="mb-4">Учетная литература</h2>
{% if current_user.clearance == 'special_importance' %}
<a href="{{ url_for('add_literature') }}" class="btn btn-success mb-3">Добавить литературу</a>
{% endif %}
<div class="table-container">
    <table class="table table-striped">
        <thead class="sticky-header">
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Автор</th>
                <th>Уровень секретности</th>
            </tr>
        </thead>
        <tbody>
            {% for item in literature %}
            <tr>
                <td>{{ item['id'] }}</td>
                <td>{{ item['title'] }}</td>
                <td>{{ item['author'] }}</td>
                <td>{{ item['security_level'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'equipment.html': '''{% extends "base.html" %}
{% block title %}Техника и оборудование{% endblock %}
{% block content %}
<h2 class="mb-4">Учет техники</h2>
{% if current_user.clearance == 'special_importance' %}
<a href="{{ url_for('add_equipment') }}" class="btn btn-success mb-3">Добавить технику</a>
{% endif %}
<div class="table-container">
    <table class="table table-striped">
        <thead class="sticky-header">
            <tr>
                <th>ID</th>
                <th>Наименование</th>
                <th>Описание</th>
            </tr>
        </thead>
        <tbody>
            {% for item in equipment %}
            <tr>
                <td>{{ item['id'] }}</td>
                <td>{{ item['name'] }}</td>
                <td>{{ item['description'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'add_activity.html': '''{% extends "base.html" %}
{% block title %}Добавить занятие{% endblock %}
{% block content %}
<h2 class="mb-4">Добавить новое занятие</h2>
<form method="POST">
    <div class="row mb-3">
        <div class="col-md-4">
            <label class="form-label">Дата*</label>
            <input type="date" class="form-control" name="date" required>
        </div>
        <div class="col-md-4">
            <label class="form-label">Место проведения*</label>
            <input type="text" class="form-control" name="location" required>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-md-3">
            <label class="form-label">Подразделение*</label>
            <select class="form-select" name="unit" required>
                <option value="" selected disabled>Выберите подразделение</option>
                {% for unit in units %}
                <option value="{{ unit['id'] }}">{{ unit['name'] }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label">Категория военнослужащих*</label>
            <select class="form-select" name="category" required>
                <option value="" selected disabled>Выберите категорию</option>
                {% for category in categories %}
                <option value="{{ category['id'] }}">{{ category['name'] }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label">Дисциплина*</label>
            <div class="input-group">
                <select class="form-select" name="subject" required>
                    <option value="" selected disabled>Выберите дисциплину</option>
                    {% for subject in subjects %}
                    <option value="{{ subject['id'] }}">{{ subject['name'] }}</option>
                    {% endfor %}
                </select>
                {% if current_user.clearance == 'special_importance' %}
                <a href="{{ url_for('add_subject') }}" class="btn btn-outline-secondary" type="button">Добавить</a>
                {% endif %}
            </div>
        </div>
        <div class="col-md-3">
            <label class="form-label">Вид занятия*</label>
            <select class="form-select" name="type" required>
                <option value="" selected disabled>Выберите вид занятия</option>
                {% for type in types %}
                <option value="{{ type['id'] }}">{{ type['name'] }}</option>
                {% endfor %}
            </select>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-md-6">
            <label class="form-label">Используемая литература</label>
            <select multiple class="form-select" name="literature" size="5">
                {% for lit in literature %}
                <option value="{{ lit['id'] }}">{{ lit['title'] }} ({{ lit['security_level'] }})</option>
                {% endfor %}
            </select>
            {% if current_user.clearance == 'special_importance' %}
            <div class="mt-2">
                <a href="{{ url_for('add_literature') }}" class="btn btn-sm btn-outline-secondary">Добавить литературу</a>
            </div>
            {% endif %}
        </div>
        <div class="col-md-6">
            <label class="form-label">Используемая техника</label>
            <select multiple class="form-select" name="equipment" size="5">
                {% for eq in equipment %}
                <option value="{{ eq['id'] }}">{{ eq['name'] }}</option>
                {% endfor %}
            </select>
            {% if current_user.clearance == 'special_importance' %}
            <div class="mt-2">
                <a href="{{ url_for('add_equipment') }}" class="btn btn-sm btn-outline-secondary">Добавить технику</a>
            </div>
            {% endif %}
        </div>
    </div>

    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Сохранить занятие</button>
        <a href="{{ url_for('activities') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}''',

    'add_literature.html': '''{% extends "base.html" %}
{% block title %}Добавить литературу{% endblock %}
{% block content %}
<h2 class="mb-4">Добавить новую литературу</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Название*</label>
        <input type="text" class="form-control" name="title" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Автор</label>
        <input type="text" class="form-control" name="author">
    </div>
    <div class="mb-3">
        <label class="form-label">Уровень секретности*</label>
        <select class="form-select" name="security_level" required>
            <option value="secret">Секретно</option>
            <option value="top_secret">Совершенно секретно</option>
            <option value="special_importance">Особой важности</option>
        </select>
    </div>
    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Добавить</button>
        <a href="{{ url_for('literature') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}''',

    'add_equipment.html': '''{% extends "base.html" %}
{% block title %}Добавить технику{% endblock %}
{% block content %}
<h2 class="mb-4">Добавить новую технику</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Название*</label>
        <input type="text" class="form-control" name="name" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Описание</label>
        <textarea class="form-control" name="description" rows="3"></textarea>
    </div>
    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Добавить</button>
        <a href="{{ url_for('equipment') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}''',

    'add_subject.html': '''{% extends "base.html" %}
{% block title %}Добавить дисциплину{% endblock %}
{% block content %}
<h2 class="mb-4">Добавить новую дисциплину</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Название*</label>
        <input type="text" class="form-control" name="name" required>
    </div>
    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Добавить</button>
        <a href="{{ url_for('add_activity') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}''',

    'add_unit.html': '''{% extends "base.html" %}
{% block title %}Добавить подразделение{% endblock %}
{% block content %}
<h2 class="mb-4">Добавить новое подразделение</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Название*</label>
        <input type="text" class="form-control" name="name" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Описание</label>
        <textarea class="form-control" name="description" rows="3"></textarea>
    </div>
    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Добавить</button>
        <a href="{{ url_for('units') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}''',

    'register.html': '''{% extends "base.html" %}
{% block title %}Регистрация пользователя{% endblock %}
{% block content %}
<h2 class="mb-4">Регистрация нового пользователя</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Имя пользователя*</label>
        <input type="text" class="form-control" name="username" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Пароль*</label>
        <input type="password" class="form-control" name="password" required>
    </div>
    <div class="row mb-3">
        <div class="col-md-6">
            <label class="form-label">Роль*</label>
            <select class="form-select" name="role" required>
                <option value="" selected disabled>Выберите роль</option>
                <option value="admin">Администратор</option>
                <option value="instructor">Преподаватель</option>
                <option value="user">Пользователь</option>
            </select>
        </div>
        <div class="col-md-6">
            <label class="form-label">Уровень доступа*</label>
            <select class="form-select" name="clearance" required>
                <option value="" selected disabled>Выберите уровень доступа</option>
                <option value="none">Нет доступа</option>
                <option value="secret">Секретно</option>
                <option value="top_secret">Совершенно секретно</option>
                <option value="special_importance">Особой важности</option>
            </select>
        </div>
    </div>
    <div class="d-flex gap-2">
        <button type="submit" class="btn btn-primary">Зарегистрировать</button>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Отмена</a>
    </div>
</form>
{% endblock %}'''
}

os.makedirs('templates', exist_ok=True)
for name, content in templates.items():
    with open(f'templates/{name}', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
