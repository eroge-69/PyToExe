# reto_empatia_web.py
# Flask app para Reto Empatía automatizado con sopa de letras y carrera por tiempo.
# Cómo ejecutar:
# 1) pip install flask
# 2) python3 reto_empatia_web.py
# 3) Abre en tu red local: http://TU_IP_LOCAL:5000/  (genera QR con esa URL)
#
# Nota: Para usar con teléfonos, tu laptop y los teléfonos deben estar en la misma red,
# o despliega en un servicio público (Replit, Fly, Railway, etc.).

from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import uuid, csv, os, time, datetime, random, html

app = Flask(__name__)
DATA_CSV = "responses_game.csv"
WORDS_DEFAULT = ["ESFUERZO","AYUDA","RISAS","PERSISTENCIA","APOYO","RESPETO","COMPAÑERISMO","CREATIVIDAD","CONSTANCIA","SOLIDARIDAD"]

# Ensure CSV exists with header
if not os.path.exists(DATA_CSV):
    with open(DATA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id","timestamp_submit","name","phrase","start_ts","finish_ts","duration_seconds"])

# Simple helper to append row
def append_row(row):
    with open(DATA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

# Home/form page
FORM_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reto Empatía — Inscripción</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;padding:20px;max-width:720px;margin:auto}
    label{display:block;margin-top:10px}
    textarea{width:100%;height:80px}
    input[type=text]{width:100%;padding:8px}
    button{margin-top:12px;padding:10px 16px;font-size:16px}
    .note{color:#555;font-size:0.95em}
  </style>
</head>
<body>
  <h2>Reto Empatía — Inscríbete</h2>
  <p class="note">Escribe tu nombre (o alias) y completa: <strong>Me identifico con las personas que...</strong></p>
  <form method="post" action="/enter">
    <label>Nombre o alias (opcional, si quieres participar por el premio):</label>
    <input name="name" type="text" placeholder="Ej: Juan23" />
    <label>Completa la frase (obligatorio):</label>
    <textarea name="phrase" required placeholder="Me identifico con las personas que..."></textarea>
    <label>
      <input type="checkbox" name="public_read" checked> Acepto que mi frase pueda leerse en voz alta (anónimo si no dejo nombre)
    </label>
    <button type="submit">Entrar al Reto y jugar</button>
  </form>
  <p style="margin-top:18px;font-size:0.9em;color:#444">
    Instrucciones para el expositor: abre /results para ver tiempos y ganador en vivo.
  </p>
</body>
</html>
"""

# Minimal wordsearch generator (creates square grid filled with letters and places words horizontally/vertically/diagonal)
def generate_wordsearch(words, size=12):
    words = [w.upper() for w in words]
    size = max(size, int(max(len(w) for w in words) + 1))
    grid = [['' for _ in range(size)] for _ in range(size)]
    directions = [(0,1),(1,0),(1,1),(-1,1)]  # right, down, diag down-right, diag up-right
    placed = []
    for w in words:
        placed_flag = False
        attempts = 0
        while not placed_flag and attempts < 200:
            attempts += 1
            dirx,diry = random.choice(directions)
            if dirx == -1:
                row = random.randint(len(w)-1, size-1)
            else:
                row = random.randint(0, size-1)
            col = random.randint(0, size-1)
            # check fit
            endr = row + dirx*(len(w)-1)
            endc = col + diry*(len(w)-1)
            if not (0 <= endr < size and 0 <= endc < size): 
                continue
            ok = True
            r,c = row,col
            for ch in w:
                if grid[r][c] not in ('', ch):
                    ok = False; break
                r += dirx; c += diry
            if not ok: continue
            # place
            r,c = row,col
            for ch in w:
                grid[r][c] = ch
                r += dirx; c += diry
            placed.append(w)
            placed_flag = True
        # if not placed, skip the word
    # fill blanks
    import string
    letters = string.ascii_uppercase
    for i in range(size):
        for j in range(size):
            if grid[i][j] == '':
                grid[i][j] = random.choice(letters)
    # return grid and placed list
    return grid, placed

# Route: show form
@app.route("/", methods=["GET"])
def index():
    return render_template_string(FORM_HTML)

# Route: handle form submission, create participant id, save and redirect to game
@app.route("/enter", methods=["POST"])
def enter():
    name = request.form.get("name","").strip()
    phrase = request.form.get("phrase","").strip()
    if not phrase:
        return "La frase es obligatoria. Vuelve atrás.", 400
    pid = str(uuid.uuid4())[:8]
    ts_submit = int(time.time())
    # choose words for the puzzle: include some words extracted from phrase or default
    # Try to pull some keywords from phrase
    words = []
    # simple split and keep unique uppercase words length>=4
    for w in phrase.replace(","," ").split():
        ww = ''.join(ch for ch in w if ch.isalpha()).upper()
        if len(ww) >= 4:
            words.append(ww)
    # if not enough, add defaults
    if len(words) < 5:
        additional = [w for w in WORDS_DEFAULT if w not in words]
        while len(words) < 6 and additional:
            words.append(additional.pop(0))
    # randomize final list
    random.shuffle(words)
    size = 11
    grid, placed = generate_wordsearch(words, size=size)
    # save initial row with start_ts blank (we'll set start when they open the game)
    append_row([pid, ts_submit, name, phrase, "", "", ""])
    # render game page passing grid and pid
    return render_template_string(GAME_HTML, pid=pid, grid=grid, words=placed)

# Game HTML with JS that records start time via AJAX and allows user to find words.
# We'll implement a simple clickable wordlist: when the user clicks each word as "found", we mark it.
# When all found, send finish to server.
GAME_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Sopa de letras — Reto Empatía</title>
<style>
  body{font-family:Arial,Helvetica,sans-serif;padding:12px;max-width:980px;margin:auto}
  .grid{display:grid;grid-template-columns:repeat({{cols}}, 36px);gap:4px;margin-top:8px}
  .cell{width:36px;height:36px;border:1px solid #ccc;display:flex;align-items:center;justify-content:center;font-weight:bold;cursor:default;background:#fafafa}
  .words{margin-top:12px}
  .word{display:inline-block;padding:6px 8px;margin:4px;border-radius:6px;background:#eee;cursor:pointer}
  .found{background: #b2f5b4 !important; text-decoration:line-through}
  #status{margin-top:14px;font-weight:bold}
</style>
</head>
<body>
  <h2>Sopa de Letras — Reto Empatía</h2>
  <p>Encuentra todas las palabras listadas abajo. Haz clic en cada palabra cuando la encuentres. El tiempo empieza ahora.</p>
  <div id="grid" class="grid"></div>
  <div class="words"><strong>Palabras:</strong><br><div id="wordlist"></div></div>
  <div id="status">Palabras encontradas: <span id="count">0</span> / <span id="total">0</span></div>
  <div style="margin-top:12px"><button id="finishBtn" disabled>Terminé</button></div>

<script>
const pid = "{{pid}}";
const gridData = {{grid|tojson}};
const words = {{words|tojson}};
const cols = gridData[0].length;
const total = words.length;
document.getElementById('total').innerText = total;

// render grid
const gridDiv = document.getElementById('grid');
gridDiv.style.gridTemplateColumns = 'repeat(' + cols + ', 36px)';
for(let r=0;r<gridData.length;r++){
  for(let c=0;c<gridData[r].length;c++){
    let cell = document.createElement('div');
    cell.className = 'cell';
    cell.innerText = gridData[r][c];
    gridDiv.appendChild(cell);
  }
}

// render words
const wl = document.getElementById('wordlist');
words.forEach(w=>{
  let el = document.createElement('div');
  el.className = 'word';
  el.innerText = w;
  el.onclick = function(){ toggleFound(el, w); };
  wl.appendChild(el);
});

let found = new Set();
function toggleFound(el, w){
  if(found.has(w)){
    found.delete(w);
    el.classList.remove('found');
  } else {
    found.add(w);
    el.classList.add('found');
  }
  document.getElementById('count').innerText = found.size;
  document.getElementById('finishBtn').disabled = (found.size < words.length);
}

// start: tell server that this pid started now
function notifyStart(){
  fetch('/start/'+pid, {method:'POST'})
    .then(resp=>resp.json())
    .then(data=>{ console.log('start saved', data); })
    .catch(e=>console.warn(e));
}
// finish: tell server finish timestamp and duration (client side)
function notifyFinish(){
  const finish_ts = Math.floor(Date.now()/1000);
  fetch('/finish/'+pid, {
    method:'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({finish_ts: finish_ts})
  }).then(r=>r.json()).then(data=>{
    alert('¡Bien hecho! Tiempo registrado: ' + data.duration_seconds + ' segundos. Gracias por participar.');
    // Optionally redirect to a "thank you" page or results
    window.location.href = '/thanks';
  }).catch(e=>{ alert('Error al registrar tiempo.'); console.error(e); });
}

document.getElementById('finishBtn').addEventListener('click', function(){
  if(confirm('¿Estás seguro que completaste todas las palabras?')) notifyFinish();
});

// call start on load
window.addEventListener('load', function(){ notifyStart(); });
</script>
</body>
</html>
"""

# Endpoint to record start time for pid
@app.route("/start/<pid>", methods=["POST"])
def start_pid(pid):
    ts = int(time.time())
    # read all rows, update the row matching pid start_ts if empty
    rows = []
    found = False
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == pid and (row["start_ts"] == "" or row["start_ts"] is None):
                row["start_ts"] = str(ts)
                found = True
            rows.append(row)
    if found:
        # write back
        with open(DATA_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id","timestamp_submit","name","phrase","start_ts","finish_ts","duration_seconds"])
            for r in rows:
                writer.writerow([r["id"],r["timestamp_submit"],r["name"],r["phrase"],r["start_ts"],r["finish_ts"],r["duration_seconds"]])
        return jsonify({"status":"ok","start_ts":ts})
    else:
        return jsonify({"status":"not_found_or_already_started"}), 404

# Endpoint to record finish timestamp and compute duration
@app.route("/finish/<pid>", methods=["POST"])
def finish_pid(pid):
    data = request.get_json() or {}
    finish_ts = int(data.get("finish_ts", int(time.time())))
    rows = []
    updated = False
    dur = None
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id"] == pid and (row["finish_ts"] == "" or row["finish_ts"] is None):
                # compute duration using stored start_ts if available
                try:
                    start_ts = int(row["start_ts"]) if row["start_ts"] else None
                except:
                    start_ts = None
                if start_ts:
                    dur = finish_ts - start_ts
                else:
                    dur = None
                row["finish_ts"] = str(finish_ts)
                row["duration_seconds"] = str(dur) if dur is not None else ""
                updated = True
            rows.append(row)
    if updated:
        with open(DATA_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id","timestamp_submit","name","phrase","start_ts","finish_ts","duration_seconds"])
            for r in rows:
                writer.writerow([r["id"],r["timestamp_submit"],r["name"],r["phrase"],r["start_ts"],r["finish_ts"],r["duration_seconds"]])
        return jsonify({"status":"ok","duration_seconds":dur})
    else:
        return jsonify({"status":"not_found_or_already_finished"}), 404

# Thank you page after finishing
@app.route("/thanks", methods=["GET"])
def thanks():
    return "<h3>Gracias por participar. Puedes volver a tu lugar y esperar los resultados.</h3>"

# Results page for the expositor (shows leaderboard)
RESULTS_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Resultados — Reto Empatía</title>
<style>body{font-family:Arial;padding:16px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:8px;text-align:left} th{background:#f4f4f4}</style>
</head>
<body>
  <h2>Resultados del Reto Empatía</h2>
  <p>Ganador = menor tiempo (segundos) entre quienes completaron la sopa.</p>
  <table>
    <thead><tr><th>#</th><th>Nombre / Alias</th><th>Frase</th><th>Tiempo (s)</th><th>Inicio</th><th>Fin</th></tr></thead>
    <tbody>
      {% for i,row in rows %}
      <tr>
        <td>{{i}}</td>
        <td>{{row.name}}</td>
        <td>{{row.phrase}}</td>
        <td>{{row.duration}}</td>
        <td>{{row.start}}</td>
        <td>{{row.finish}}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <p style="margin-top:12px">Actualiza la página para ver nuevas participaciones.</p>
</body>
</html>
"""

@app.route("/results")
def results():
    # read CSV and compute rows with duration numeric
    rows = []
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            dur = r.get("duration_seconds")
            try:
                durn = float(dur) if dur else None
            except:
                durn = None
            rows.append({
                "name": html.escape(r.get("name","")),
                "phrase": html.escape(r.get("phrase","")),
                "duration": int(durn) if durn is not None else "",
                "start": datetime.datetime.fromtimestamp(int(r["start_ts"])).strftime("%H:%M:%S") if r["start_ts"] else "",
                "finish": datetime.datetime.fromtimestamp(int(r["finish_ts"])).strftime("%H:%M:%S") if r["finish_ts"] else ""
            })
    # sort by duration ascending, place blanks at end
    rows_sorted = sorted(rows, key=lambda x: (x["duration"]=="" , x["duration"] if x["duration"]!="" else 999999))
    enumerated = list(enumerate(rows_sorted, start=1))
    return render_template_string(RESULTS_HTML, rows=enumerated)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)