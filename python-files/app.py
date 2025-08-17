import os, sqlite3, json, webbrowser, threading, traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template

APP_NAME = "Arnab Tally"
DEFAULT_DB_DIR = r"F:\ArnabTallyData"
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "arnab_tally.db")
LOG_PATH = os.path.join(DEFAULT_DB_DIR, "arnab_tally.log")

app = Flask(__name__, template_folder="templates")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def log(msg):
    try:
        ensure_dir(DEFAULT_DB_DIR)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}\n")
    except Exception:
        pass

# ---- DB management with clear error if F: is not available ----
DB_PATH = DEFAULT_DB_PATH
DB_ERROR = None

def connect(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    global DB_PATH, DB_ERROR
    try:
        ensure_dir(os.path.dirname(DB_PATH))
        conn = connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS ledgers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            group_name TEXT NOT NULL,
            opening_balance REAL NOT NULL DEFAULT 0,
            balance_type TEXT NOT NULL CHECK(balance_type in ('Dr','Cr')),
            gstin TEXT DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS vouchers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            dr_ledger TEXT NOT NULL,
            cr_ledger TEXT NOT NULL,
            amount REAL NOT NULL,
            narration TEXT DEFAULT ''
        )""")
        conn.commit()
        conn.close()
        log("Database initialized at " + DB_PATH)
    except Exception as e:
        DB_ERROR = f"Cannot create or open the database at {DB_PATH}. Details: {e}"
        log("DB init error: " + traceback.format_exc())

init_db()

# -------------------- Helpers --------------------
def get_conn():
    if DB_ERROR:
        raise RuntimeError(DB_ERROR)
    return connect(DB_PATH)

def json_error(message, status=400):
    return jsonify({"ok": False, "error": message}), status

# -------------------- UI --------------------
@app.route("/")
def home():
    return render_template("index.html", app_name=APP_NAME, db_path=DB_PATH, db_error=DB_ERROR or "")

# -------------------- Ledgers API --------------------
@app.route("/api/ledgers", methods=["GET", "POST", "DELETE"])
def api_ledgers():
    if DB_ERROR:
        return json_error(DB_ERROR, 500)

    if request.method == "GET":
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM ledgers ORDER BY name COLLATE NOCASE")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return jsonify({"ok": True, "data": rows})

    if request.method == "POST":
        data = request.get_json(force=True)
        required = ["name","group_name","opening_balance","balance_type"]
        for k in required:
            if k not in data or (isinstance(data[k], str) and not data[k].strip()):
                return json_error(f"Missing field: {k}")
        try:
            conn = get_conn(); c = conn.cursor()
            c.execute("""INSERT INTO ledgers(name,group_name,opening_balance,balance_type,gstin)
                         VALUES (?,?,?,?,?)""",
                         (data["name"].strip(), data["group_name"].strip(),
                          float(data["opening_balance"]), data["balance_type"],
                          data.get("gstin","").strip()))
            conn.commit(); conn.close()
            return jsonify({"ok": True})
        except sqlite3.IntegrityError as e:
            return json_error(f"Ledger exists or invalid: {e}")
        except Exception as e:
            log("Add ledger error: " + traceback.format_exc())
            return json_error(str(e), 500)

    # DELETE by name
    name = request.args.get("name","").strip()
    if not name:
        return json_error("Specify ?name=... to delete")
    try:
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM ledgers WHERE name = ?", (name,))
        conn.commit(); conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        log("Delete ledger error: " + traceback.format_exc())
        return json_error(str(e), 500)

# -------------------- Vouchers API --------------------
@app.route("/api/vouchers", methods=["GET","POST","DELETE"])
def api_vouchers():
    if DB_ERROR:
        return json_error(DB_ERROR, 500)
    if request.method == "GET":
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM vouchers ORDER BY date DESC, id DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return jsonify({"ok": True, "data": rows})

    if request.method == "POST":
        data = request.get_json(force=True)
        required = ["date","type","dr_ledger","cr_ledger","amount"]
        for k in required:
            if k not in data or (isinstance(data[k], str) and not data[k].strip()):
                return json_error(f"Missing field: {k}")
        try:
            amt = float(data["amount"])
            if amt <= 0: return json_error("Amount must be > 0")
            conn = get_conn(); c = conn.cursor()
            c.execute("""INSERT INTO vouchers(date,type,dr_ledger,cr_ledger,amount,narration)
                         VALUES (?,?,?,?,?,?)""",
                         (data["date"], data["type"], data["dr_ledger"], data["cr_ledger"],
                          amt, data.get("narration","")))
            conn.commit(); conn.close()
            return jsonify({"ok": True})
        except Exception as e:
            log("Add voucher error: " + traceback.format_exc())
            return json_error(str(e), 500)

    # DELETE by id
    vid = request.args.get("id","").strip()
    if not vid.isdigit():
        return json_error("Specify ?id=... to delete")
    try:
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM vouchers WHERE id = ?", (int(vid),))
        conn.commit(); conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        log("Delete voucher error: " + traceback.format_exc())
        return json_error(str(e), 500)

# -------------------- Reports API --------------------
def _trial_balance(conn):
    c = conn.cursor()
    c.execute("SELECT dr_ledger AS l, SUM(amount) AS d FROM vouchers GROUP BY dr_ledger")
    dr = {r["l"]: r["d"] for r in c.fetchall()}
    c.execute("SELECT cr_ledger AS l, SUM(amount) AS c FROM vouchers GROUP BY cr_ledger")
    cr = {r["l"]: r["c"] for r in c.fetchall()}
    # Include all ledgers
    c.execute("SELECT name FROM ledgers")
    for r in c.fetchall():
        dr.setdefault(r["name"], 0.0)
        cr.setdefault(r["name"], 0.0)
    rows = [{"ledger": l, "debit": float(dr.get(l,0)), "credit": float(cr.get(l,0))}
            for l in sorted(set(dr.keys()) | set(cr.keys()), key=lambda x: x.lower())]
    return rows

@app.route("/api/reports/trial")
def api_trial():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    conn = get_conn()
    rows = _trial_balance(conn)
    conn.close()
    total_dr = sum(r["debit"] for r in rows)
    total_cr = sum(r["credit"] for r in rows)
    return jsonify({"ok": True, "data": rows, "total_dr": total_dr, "total_cr": total_cr})

@app.route("/api/reports/pnl")
def api_pnl():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    conn = get_conn()
    trial = _trial_balance(conn)
    # heuristic buckets
    sales = sum(r["credit"] for r in trial if "sale" in r["ledger"].lower())
    purchases = sum(r["debit"] for r in trial if "purchase" in r["ledger"].lower())
    expenses = sum(r["debit"] for r in trial if any(k in r["ledger"].lower() for k in ["expense","rent","salary","wages","electric","admin"]))
    gross = sales - purchases
    net = gross - expenses
    conn.close()
    return jsonify({"ok": True, "sales": sales, "purchases": purchases, "expenses": expenses, "gross": gross, "net": net})

@app.route("/api/reports/ledger_statement")
def api_ledger_statement():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    ledger = request.args.get("ledger","").strip()
    if not ledger: return json_error("Provide ?ledger=Name")
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT date, type, dr_ledger, cr_ledger, amount, narration, id
                 FROM vouchers
                 WHERE dr_ledger = ? OR cr_ledger = ?
                 ORDER BY date, id""", (ledger, ledger))
    rows = [dict(r) for r in c.fetchall()]
    # running balance: Dr positive, Cr negative
    bal = 0.0; stmt = []
    for r in rows:
        if r["dr_ledger"] == ledger: bal += r["amount"]
        else: bal -= r["amount"]
        r["balance"] = bal
        stmt.append(r)
    conn.close()
    return jsonify({"ok": True, "data": stmt, "closing": bal})

@app.route("/api/reports/gst_summary")
def api_gst():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    # Very simple: sum Sales and Purchases ledgers that contain GST rate hints in narration like "GST18"
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM vouchers")
    sales=0; purchases=0
    for r in c.fetchall():
        t = (r["narration"] or "").lower()
        if "gst" in t:
            if "sale" in r["type"].lower(): sales += r["amount"]
            if "purchase" in r["type"].lower(): purchases += r["amount"]
    conn.close()
    return jsonify({"ok": True, "sales_gst_base": sales, "purchase_gst_base": purchases})

# -------------------- Backup / Restore --------------------
@app.route("/api/backup", methods=["GET"])
def api_backup():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM ledgers"); ledgers = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM vouchers"); vouchers = [dict(r) for r in c.fetchall()]
    conn.close()
    path = os.path.join(DEFAULT_DB_DIR, "ArnabTallyData.json")
    ensure_dir(DEFAULT_DB_DIR)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ledgers": ledgers, "vouchers": vouchers}, f, indent=2)
    return jsonify({"ok": True, "path": path})

@app.route("/api/restore", methods=["POST"])
def api_restore():
    if DB_ERROR: return json_error(DB_ERROR, 500)
    body = request.get_json(force=True)
    path = body.get("path", "").strip() or os.path.join(DEFAULT_DB_DIR, "ArnabTallyData.json")
    if not os.path.exists(path): return json_error(f"Backup not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    conn = get_conn(); c = conn.cursor()
    for l in data.get("ledgers", []):
        try:
            c.execute("""INSERT OR IGNORE INTO ledgers(name,group_name,opening_balance,balance_type,gstin)
                         VALUES (?,?,?,?,?)""",
                         (l["name"], l["group_name"], float(l["opening_balance"]), l["balance_type"], l.get("gstin","")))
        except Exception:
            pass
    for v in data.get("vouchers", []):
        try:
            c.execute("""INSERT OR IGNORE INTO vouchers(id,date,type,dr_ledger,cr_ledger,amount,narration)
                         VALUES (?,?,?,?,?,?,?)""",
                         (v.get("id"), v["date"], v["type"], v["dr_ledger"], v["cr_ledger"], float(v["amount"]), v.get("narration","")))
        except Exception:
            pass
    conn.commit(); conn.close()
    return jsonify({"ok": True})

# -------------------- Settings --------------------
@app.route("/api/status")
def api_status():
    return jsonify({"ok": DB_ERROR is None, "db_path": DB_PATH, "db_error": DB_ERROR or ""})

# -------------------- Main --------------------
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
