### Estructura general del proyecto

```
facial_recognition_app/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── face_match.py
│   ├── user_log.py
│   ├── static/ (para servir imágenes)
│   └── templates/
├── frontend/
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── Login.jsx
│       ├── Upload.jsx
│       ├── Report.jsx
│       └── api.js
├── database/
│   └── users.db
├── requirements.txt
└── README.md
```

---
### backend/app.py
```python
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from auth import auth_blueprint
from face_match import face_blueprint
from user_log import log_blueprint

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(face_blueprint)
app.register_blueprint(log_blueprint)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

---
### backend/auth.py
```python
from flask import Blueprint, request, jsonify
import bcrypt
import sqlite3
import time

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())

    with sqlite3.connect('database/users.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

    return jsonify({"message": "User registered successfully"})

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    with sqlite3.connect('database/users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        if row and bcrypt.checkpw(password.encode(), row[0]):
            cur.execute("INSERT INTO logs (username, login_time) VALUES (?, ?)", (username, int(time.time())))
            return jsonify({"message": "Login successful"})

    return jsonify({"error": "Invalid credentials"}), 401
```

---
### backend/face_match.py
```python
from flask import Blueprint, request, jsonify
import face_recognition
import os
from werkzeug.utils import secure_filename
import uuid

face_blueprint = Blueprint('face', __name__)
UPLOAD_FOLDER = 'backend/static/uploads'
SAMPLES_FOLDER = 'backend/static/samples'

@face_blueprint.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files['image']
    filename = secure_filename(image.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    image.save(filepath)

    # Simulated comparison
    results = []
    try:
        uploaded_encoding = face_recognition.face_encodings(face_recognition.load_image_file(filepath))[0]
        for sample in os.listdir(SAMPLES_FOLDER):
            sample_path = os.path.join(SAMPLES_FOLDER, sample)
            sample_encoding = face_recognition.face_encodings(face_recognition.load_image_file(sample_path))[0]
            match = face_recognition.compare_faces([sample_encoding], uploaded_encoding)[0]
            if match:
                results.append({
                    "sample_image": sample,
                    "match": True,
                    "similarity": "High"
                })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"results": results})
```

---
### backend/user_log.py
```python
from flask import Blueprint, jsonify
import sqlite3
import time

log_blueprint = Blueprint('logs', __name__)

@log_blueprint.route('/user-logs')
def get_logs():
    today = int(time.time()) - 86400
    with sqlite3.connect('database/users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, login_time FROM logs WHERE login_time > ?", (today,))
        logs = cur.fetchall()

    report = []
    for username, login_time in logs:
        usage_time = int(time.time()) - login_time
        report.append({
            "username": username,
            "login_time": login_time,
            "usage_seconds": usage_time
        })

    return jsonify(report)
```

---
### database/init.sql
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password BLOB
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time INTEGER
);
```

---
### frontend/src/App.jsx
```jsx
import React from 'react';
import Login from './Login';
import Upload from './Upload';
import Report from './Report';

function App() {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Facial Recognition App</h1>
      <Login />
      <Upload />
      <Report />
    </div>
  );
}

export default App;
```

---
### frontend/src/api.js
```jsx
const API_URL = 'http://localhost:5000';

export async function login(username, password) {
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return res.json();
}

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append('image', file);
  const res = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  return res.json();
}

export async function getUserLogs() {
  const res = await fetch(`${API_URL}/user-logs`);
  return res.json();
}
```

---
### README.md
```md
# Facial Recognition Web App

### Funcionalidades:
- Login de usuario seguro
- Carga y comparación de imágenes
- Informe de coincidencias
- Reporte de acceso diario

### Uso de bases de datos reales:
Para conectar con bases de datos públicas o privadas, reemplaza `SAMPLES_FOLDER` en `face_match.py` por una ruta a imágenes reales o integrar un scraper/API con consentimiento. Considerar fuentes como:
- API de medios noticiosos
- Registros públicos con imágenes
- Metadatos de imágenes

### Para correr el proyecto:
```bash
cd backend
pip install -r requirements.txt
sqlite3 ../database/users.db < ../database/init.sql
python app.py
```

Y en otra terminal:
```bash
cd frontend
npm install
npm start
```
```

---

¿Quieres que prepare este proyecto como un repositorio o que genere un archivo `.zip` descargable con todos los componentes listos? También puedo ayudarte a conectarlo con APIs reales cuando estés listo para escalar. 💡
