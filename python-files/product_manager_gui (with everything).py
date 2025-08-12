# product_manager_shared_fixed_fonts.py
# Product & QC Manager — Lab (Shared DB, Auto-backup, Single shared log, single-user lock)
# Fixed, refactored and UI font sizes enforced to original (larger) settings.
# Author: ChatGPT (updated fonts per user request)

import os
import sqlite3
import csv
import logging
import logging.handlers
import traceback
import time
import shutil
import atexit
import json
import socket
import getpass
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# matplotlib + embedding to Tk
import matplotlib
try:
    matplotlib.use("TkAgg")
except Exception:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# optional modules
try:
    import sv_ttk
    SV_TTK_AVAILABLE = True
except Exception:
    SV_TTK_AVAILABLE = False

try:
    import mplcursors
    MPLCURSORS_AVAILABLE = True
except Exception:
    MPLCURSORS_AVAILABLE = False

# -------------------------
# CONFIG (font sizes set to original values)
# -------------------------
SHARED_DB_PATH = r"T:\Laboratory\Rubber data and QC manager\products.db"
DEFAULT_LOCAL_DB = "products.db"

SHARED_LOG_NAME = "product_manager_shared.log"
LOCAL_LOG_NAME = "product_manager.log"

BACKUP_INTERVAL_HOURS = 6
BACKUP_KEEP = 90

BASE_FONT_FAMILY = "Segoe UI"
BASE_FONT_SIZE = 15   # ← original size requested
BASE_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE)
SMALL_FONT = (BASE_FONT_FAMILY, max(11, BASE_FONT_SIZE - 2))

# Minimal temporary console logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

# -------------------------
# Lock helpers
# -------------------------
def lock_file_path_for_db(db_path):
    db_dir = os.path.dirname(os.path.abspath(db_path)) or "."
    return os.path.join(db_dir, "products.lock")

def acquire_lock(lock_path, max_attempts=1):
    """
    Try to create lock file atomically (O_EXCL).
    Returns (True, info) if acquired.
    If exists, returns (False, info_read).
    """
    info = {"host": socket.gethostname(), "user": getpass.getuser(), "pid": os.getpid(), "ts": datetime.now().isoformat()}
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    mode = 0o644
    try:
        fd = os.open(lock_path, flags, mode)
        try:
            os.write(fd, json.dumps(info).encode("utf-8"))
        finally:
            os.close(fd)
        logging.info(f"Lock created at {lock_path}")
        return True, info
    except FileExistsError:
        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                raw = f.read()
                existing = json.loads(raw) if raw else {}
        except Exception:
            existing = {}
        return False, existing
    except Exception as e:
        logging.exception("Error acquiring lock")
        return False, {"error": str(e)}

def release_lock(lock_path):
    try:
        if os.path.exists(lock_path):
            os.remove(lock_path)
            logging.info(f"Lock removed: {lock_path}")
    except Exception:
        logging.exception("Failed to release lock")

# -------------------------
# Logging to single shared file (fallback to local)
# -------------------------
def configure_shared_log(db_path, shared_name=SHARED_LOG_NAME, fallback_name=LOCAL_LOG_NAME,
                         max_bytes=10*1024*1024, backup_count=5):
    try:
        db_dir = os.path.dirname(os.path.abspath(db_path)) or "."
    except Exception:
        db_dir = "."
    shared_path = os.path.join(db_dir, shared_name)
    try:
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        with open(shared_path, "a", encoding="utf-8"):
            pass
        target = shared_path
    except Exception as e:
        logging.warning(f"Cannot write shared log {shared_path}: {e}. Falling back to local.")
        try:
            with open(fallback_name, "a", encoding="utf-8"):
                pass
            target = fallback_name
        except Exception:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
            logging.getLogger().warning("Cannot create any log file; using console logging only.")
            return

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.INFO)
    try:
        fh = logging.handlers.RotatingFileHandler(target, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
        root.warning("Failed to set file handler; using console only.")
        return
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)
    root.info(f"Logging initialized to: {target}")

# -------------------------
# SQLite helpers (retries)
# -------------------------
def get_sqlite_conn(path, tries=6, backoff=0.2, timeout_ms=5000):
    last_exc = None
    for attempt in range(tries):
        try:
            conn = sqlite3.connect(path, timeout=timeout_ms/1000.0, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute("PRAGMA foreign_keys = ON")
                cur.execute("PRAGMA journal_mode = WAL")
                cur.execute("PRAGMA synchronous = NORMAL")
                cur.execute(f"PRAGMA busy_timeout = {int(timeout_ms)}")
            except Exception:
                pass
            conn.commit()
            return conn
        except sqlite3.OperationalError as e:
            last_exc = e
            sleep_for = backoff * (2 ** attempt)
            logging.warning(f"DB open attempt {attempt+1} failed: {e}; sleeping {sleep_for:.2f}s")
            time.sleep(sleep_for)
    logging.error("DB open retries exhausted")
    raise last_exc

def execute_write_sql(path, sql, params=(), tries=6, timeout_ms=5000):
    last_exc = None
    for attempt in range(tries):
        conn = None
        try:
            conn = get_sqlite_conn(path, tries=1, timeout_ms=timeout_ms)
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return getattr(cur, "lastrowid", None)
        except sqlite3.OperationalError as e:
            last_exc = e
            if "locked" in str(e).lower() or "busy" in str(e).lower():
                sleep_for = 0.1 * (2 ** attempt)
                logging.warning(f"DB locked, retry {attempt+1}, sleep {sleep_for:.2f}s")
                time.sleep(sleep_for)
                continue
            else:
                logging.exception("execute_write_sql non-lock error")
                raise
        except Exception:
            logging.exception("execute_write_sql unexpected error")
            raise
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
    logging.error("execute_write_sql retries exhausted")
    raise last_exc

# -------------------------
# DB Manager & Parameter Manager
# -------------------------
class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        try:
            self.conn = get_sqlite_conn(self.db_path)
        except Exception:
            logging.exception("Can't open shared DB; falling back to local.")
            self.db_path = DEFAULT_LOCAL_DB
            self.conn = get_sqlite_conn(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

    def close(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            logging.exception("Error closing DB")

    def execute_write(self, sql, params=(), return_lastrow=False):
        lastrow = execute_write_sql(self.db_path, sql, params)
        if return_lastrow:
            return lastrow
        return None

    def recreate_products_table(self, params):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if cur.fetchone():
            cur.execute("PRAGMA table_info(products)")
            old_info = cur.fetchall()
            old_cols = [info[1] for info in old_info]
            old_param_cols = [c for c in old_cols if c.startswith("param")]
            select_cols = ["id", "code", "name"] + old_param_cols
            if "update_date" in old_cols:
                select_cols.append("update_date")
            cur.execute(f"SELECT {', '.join(select_cols)} FROM products")
            backup_rows = cur.fetchall()
            cur.execute("DROP TABLE products")
            self.conn.commit()
        else:
            backup_rows = []
            old_param_cols = []

        param_defs = ", ".join([f"param{i+1} TEXT" for i in range(len(params))]) if params else ""
        sql = f"""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT,
                {param_defs},
                update_date TEXT
            )
        """
        cur.execute(sql)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)")
        self.conn.commit()

        if backup_rows:
            new_param_cols = [f"param{i+1}" for i in range(len(params))]
            cols_to_insert = ["code", "name"] + new_param_cols + ["update_date"]
            placeholders = ", ".join(["?"] * len(cols_to_insert))
            insert_sql = f"INSERT INTO products ({', '.join(cols_to_insert)}) VALUES ({placeholders})"
            old_colnames = [c[1] for c in old_info] if old_info else []
            for row in backup_rows:
                rl = list(row)
                code = rl[1] if len(rl) > 1 else ""
                name = rl[2] if len(rl) > 2 else ""
                if "update_date" in old_colnames:
                    update_date = rl[-1] or datetime.now().strftime("%Y-%m-%d")
                    old_vals = rl[3:-1]
                else:
                    update_date = datetime.now().strftime("%Y-%m-%d")
                    old_vals = rl[3:]
                old_vals = list(old_vals)
                if len(old_vals) < len(new_param_cols):
                    old_vals.extend([""] * (len(new_param_cols) - len(old_vals)))
                elif len(old_vals) > len(new_param_cols):
                    old_vals = old_vals[:len(new_param_cols)]
                vals = [code, name] + old_vals + [update_date]
                try:
                    cur.execute(insert_sql, vals)
                except Exception:
                    logging.exception("Failed restore row")
            self.conn.commit()

    def ensure_products_table(self, params):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cur.fetchone():
            self.recreate_products_table(params)
            return
        cur.execute("PRAGMA table_info(products)")
        cols = [info[1] for info in cur.fetchall()]
        current_param_cols = [c for c in cols if c.startswith("param")]
        if len(current_param_cols) != len(params):
            logging.info("Products schema param count mismatch — migrating")
            self.recreate_products_table(params)

    def ensure_qc_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qc_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                param_index INTEGER NOT NULL,
                qc_value TEXT,
                qc_date TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_qc_product_param ON qc_records(product_id, param_index)")
        self.conn.commit()

class ParameterManager:
    def __init__(self, conn):
        self.conn = conn
        self.params = []
        self._ensure_table()
        self.load_params()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

    def load_params(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM parameters ORDER BY id")
        rows = [r[0] for r in cur.fetchall()]
        if rows:
            self.params = rows
            return
        default = [
            "Dispersion", "Specific Gravity", "Hardness", "M100", "M300", "M500",
            "Elongation at Break", "Tensile Strength", "Abrasion",
            "90 Minute Elongation", "90-Min Tension Set (10 Min)", "90-Min Tension Set (30 Min)",
            "Tension Set (100% Strain) 1 Day at 70C", "Tension Set (100% Strain) 3 Days at 23C",
            "Head Tear Strength", "Trouser Tear Strength", "Crescent Tear Strength",
            "Ozone Resistance", "Vol Swell - Water", "Vol Swell - AMF",
            "Vol Swell - Sulphuric Acid", "Vol Swell - Nitric Acid"
        ]
        for p in default:
            try:
                cur.execute("INSERT OR IGNORE INTO parameters (name) VALUES (?)", (p,))
            except Exception:
                pass
        self.conn.commit()
        self.params = default

    def add_param(self, name):
        if not name or not name.strip():
            return False, "Name empty"
        name = name.strip()
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO parameters (name) VALUES (?)", (name,))
            self.conn.commit()
            self.params.append(name)
            return True, None
        except sqlite3.IntegrityError:
            return False, "Duplicate"
        except Exception:
            logging.exception("add_param error")
            return False, "DB error"

    def remove_param(self, name):
        if name not in self.params:
            return False
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM parameters WHERE name=?", (name,))
            self.conn.commit()
            self.params.remove(name)
            return True
        except Exception:
            logging.exception("remove_param")
            return False

    def rename_param(self, old, new):
        if old not in self.params:
            return False, "Old not found"
        if not new or not new.strip():
            return False, "Invalid new name"
        new = new.strip()
        if new in self.params:
            return False, "Duplicate name"
        cur = self.conn.cursor()
        try:
            cur.execute("UPDATE parameters SET name=? WHERE name=?", (new, old))
            self.conn.commit()
            idx = self.params.index(old)
            self.params[idx] = new
            return True, None
        except Exception:
            logging.exception("rename_param")
            return False, "DB error"

    def reorder_params(self, new_order):
        """
        Reorder parameters and shift product param columns + update qc_records indexes.
        """
        cur = self.conn.cursor()
        old = list(self.params)
        if set(old) != set(new_order) or len(old) != len(new_order):
            logging.error("reorder_params: mismatch")
            return False
        try:
            cur.execute("BEGIN")
            n = len(old)
            if n == 0:
                cur.execute("DELETE FROM parameters")
                for nm in new_order:
                    cur.execute("INSERT INTO parameters (name) VALUES (?)", (nm,))
                self.conn.commit()
                self.params = list(new_order)
                return True

            name_to_old_idx = {name: i+1 for i, name in enumerate(old)}
            select_parts = ["code", "name"]
            for i, newname in enumerate(new_order):
                old_idx = name_to_old_idx.get(newname)
                if old_idx is None:
                    select_parts.append("'' AS param{}".format(i+1))
                else:
                    select_parts.append(f"param{old_idx} AS param{i+1}")
            select_parts.append("update_date")
            cur.execute("CREATE TABLE IF NOT EXISTS products_new (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, name TEXT, " +
                        ", ".join([f"param{i+1} TEXT" for i in range(n)]) + ", update_date TEXT)")
            select_sql = "SELECT " + ", ".join(select_parts) + " FROM products"
            insert_cols = ["code", "name"] + [f"param{i+1}" for i in range(n)] + ["update_date"]
            insert_sql = f"INSERT INTO products_new ({', '.join(insert_cols)}) {select_sql}"
            cur.execute(insert_sql)
            cur.execute("DROP TABLE products")
            cur.execute("ALTER TABLE products_new RENAME TO products")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)")

            # Update qc_records param_index mapping
            cases = []
            for old_idx, name in enumerate(old, start=1):
                new_idx = new_order.index(name) + 1
                if new_idx != old_idx:
                    cases.append(f"WHEN {old_idx} THEN {new_idx}")
            if cases:
                case_sql = "CASE param_index " + " ".join(cases) + " ELSE param_index END"
                cur.execute(f"UPDATE qc_records SET param_index = {case_sql}")

            cur.execute("DELETE FROM parameters")
            for nm in new_order:
                cur.execute("INSERT INTO parameters (name) VALUES (?)", (nm,))
            self.conn.commit()
            self.params = list(new_order)
            logging.info("reorder_params success")
            return True
        except Exception:
            logging.exception("reorder_params failed")
            try:
                self.conn.rollback()
            except Exception:
                logging.exception("rollback failed")
            return False

    def get_params(self):
        return list(self.params)

# -------------------------
# UI helper messageboxes (safe)
# -------------------------
class UIHelpers:
    @staticmethod
    def ask_string(title, prompt, initial=""):
        try:
            return simpledialog.askstring(title, prompt, initialvalue=initial)
        except Exception:
            tmp = tk.Tk()
            tmp.withdraw()
            try:
                res = simpledialog.askstring(title, prompt, initialvalue=initial, parent=tmp)
            finally:
                try:
                    tmp.destroy()
                except Exception:
                    pass
            return res

    @staticmethod
    def show_info(title, message):
        try:
            messagebox.showinfo(title, message)
        except Exception:
            tmp = tk.Tk()
            tmp.withdraw()
            try:
                messagebox.showinfo(title, message, parent=tmp)
            finally:
                try:
                    tmp.destroy()
                except Exception:
                    pass

    @staticmethod
    def show_error(title, message):
        try:
            messagebox.showerror(title, message)
        except Exception:
            tmp = tk.Tk()
            tmp.withdraw()
            try:
                messagebox.showerror(title, message, parent=tmp)
            finally:
                try:
                    tmp.destroy()
                except Exception:
                    pass

    @staticmethod
    def show_warning(title, message):
        try:
            messagebox.showwarning(title, message)
        except Exception:
            tmp = tk.Tk()
            tmp.withdraw()
            try:
                messagebox.showwarning(title, message, parent=tmp)
            finally:
                try:
                    tmp.destroy()
                except Exception:
                    pass

# -------------------------
# Main Application
# -------------------------
class ProductManagerApp(tk.Tk):
    def __init__(self, db_path, lock_path):
        super().__init__()
        self.title("Product & QC Manager — Lab (Shared)")
        self.geometry("3840x2160")
        self.minsize(1100, 700)

        # Ensure big base font applied globally
        self.base_font = BASE_FONT
        self.small_font = SMALL_FONT
        # Apply globally to widgets
        self.option_add("*Font", self.base_font)
        # Apply to menus specifically
        self.option_add("*Menu.font", self.base_font)

        # ttk styling with enforced fonts
        self.style = ttk.Style(self)
        if SV_TTK_AVAILABLE:
            sv_ttk.set_theme("light")
        else:
            try:
                self.style.theme_use('clam')
            except Exception:
                pass

        # Centralize style font settings so tabs/buttons/entries/tree use the large font
        try:
            self.style.configure("TFrame", background="#eef6ff")
            self.style.configure("TLabel", background="#eef6ff", foreground="#0f1724", font=self.base_font)
            self.style.configure("TButton", padding=6, font=self.base_font)
            self.style.configure("TEntry", relief="flat", fieldbackground="#ffffff", background="#ffffff", font=self.base_font)
            self.style.configure("Treeview", background="#ffffff", foreground="#0f1724", fieldbackground="#ffffff", font=self.base_font, rowheight=30)
            self.style.configure("Treeview.Heading", font=(BASE_FONT_FAMILY, BASE_FONT_SIZE, "bold"))
            self.style.configure("TCombobox", padding=6, font=self.base_font)
            self.style.configure("TNotebook.Tab", font=(BASE_FONT_FAMILY, BASE_FONT_SIZE + 1, "bold"), padding=[8, 6])
        except Exception:
            logging.exception("style configure failed")

        # store lock path for release on exit
        self._lock_path = lock_path

        # DB managers
        self.db = DBManager(db_path)
        self.param_manager = ParameterManager(self.db.conn)
        self.db.ensure_products_table(self.param_manager.get_params())
        self.db.ensure_qc_table()

        # backup folder
        self.backup_dir = None
        self._ensure_backup_dir()
        try:
            self._do_backup("startup")
        except Exception:
            logging.exception("startup backup failed")

        # state
        self.selected_product_id = None
        self.selected_param_index = None

        # UI variables
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.on_search_change())
        self.status_var = tk.StringVar(value="Ready")
        self.dark_mode = tk.BooleanVar(value=False)

        # DB watcher
        self._db_mtime = None
        self._db_watcher_interval = 2000

        # periodic backup
        self._backup_interval_ms = int(BACKUP_INTERVAL_HOURS * 3600 * 1000)
        self._next_backup_job = None

        # build UI
        self._build_menu()
        self._build_main_notebook()  # builds tabs and internal tab UIs
        self._build_status_bar()

        # Notebook tab change safe binding
        try:
            self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        except Exception:
            logging.exception("Notebook binding failed")

        # keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.add_new_product())
        self.bind("<Control-s>", lambda e: self.save_product())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())

        # initial loads
        self.load_products()
        self.load_qc_products()
        self.load_params_list()

        # start watcher & periodic backup
        self._start_db_watcher()
        self._schedule_periodic_backup()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---- backups ----
    def _ensure_backup_dir(self):
        try:
            db_dir = os.path.dirname(os.path.abspath(self.db.db_path)) or "."
            bdir = os.path.join(db_dir, "backups")
            os.makedirs(bdir, exist_ok=True)
            self.backup_dir = bdir
            logging.info(f"Backup dir: {bdir}")
        except Exception:
            logging.exception("ensure backup dir")
            self.backup_dir = None

    def _do_backup(self, reason="manual"):
        if not self.backup_dir:
            logging.warning("No backup dir")
            return False
        src = self.db.db_path
        if not os.path.exists(src):
            logging.warning("DB missing for backup")
            return False
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(self.backup_dir, f"products_{ts}.db")
            shutil.copy2(src, dst)
            logging.info(f"Backup {reason}: {dst}")
            self.status_set(f"Backup created ({reason})")
            files = [f for f in os.listdir(self.backup_dir) if f.startswith("products_") and f.endswith(".db")]
            files.sort(reverse=True)
            for old in files[BACKUP_KEEP:]:
                try:
                    os.remove(os.path.join(self.backup_dir, old))
                except Exception:
                    logging.exception("remove old backup")
            return True
        except Exception:
            logging.exception("backup failed")
            self.status_set("Backup failed")
            return False

    def _schedule_periodic_backup(self):
        try:
            if self._backup_interval_ms > 0:
                self._next_backup_job = self.after(self._backup_interval_ms, self._periodic_backup_job)
        except Exception:
            logging.exception("schedule backup failed")

    def _periodic_backup_job(self):
        try:
            self._do_backup("periodic")
        except Exception:
            logging.exception("periodic backup")
        finally:
            self._schedule_periodic_backup()

    # ---- UI: menu, notebook, status ----
    def _build_menu(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=False)
        filem.add_command(label="Import Products CSV...", command=self.import_products_csv)
        filem.add_command(label="Export Products CSV...", command=self.export_products_csv)
        filem.add_separator()
        filem.add_command(label="Backup Now", command=lambda: self._do_backup("manual"))
        filem.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=filem)

        viewm = tk.Menu(menubar, tearoff=False)
        viewm.add_checkbutton(label="Dark Theme (sv_ttk)", variable=self.dark_mode, command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=viewm)

        helpm = tk.Menu(menubar, tearoff=False)
        helpm.add_command(label="About", command=lambda: UIHelpers.show_info("About", "Product & QC Manager — Lab"))
        menubar.add_cascade(label="Help", menu=helpm)

        self.config(menu=menubar)

    def toggle_theme(self):
        if SV_TTK_AVAILABLE:
            sv_ttk.set_theme("dark" if self.dark_mode.get() else "light")
            self.status_set("Theme switched")
        else:
            UIHelpers.show_info("Theme", "sv_ttk not installed")

    def _build_main_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(6,0))

        self.products_frame = ttk.Frame(self.notebook)
        self.qc_frame = ttk.Frame(self.notebook)
        self.param_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.products_frame, text="Products")
        self.notebook.add(self.qc_frame, text="QC Management")
        self.notebook.add(self.param_frame, text="Parameters")

        # Build content of each tab
        self._build_products_tab()
        self._build_qc_tab()
        self._build_param_tab()

    def _build_status_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", side="bottom")
        self.status_label = ttk.Label(bar, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=8, pady=6)

    def status_set(self, text):
        try:
            self.status_var.set(text)
        except Exception:
            pass
        logging.info(text)

    # -------------------------
    # Products tab
    # -------------------------
    def _build_products_tab(self):
        c = self.products_frame
        for w in c.winfo_children():
            w.destroy()
        top = ttk.Frame(c)
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Search (formulation code or name):").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(top, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Show All", command=self.show_all_products).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Import CSV", command=self.import_products_csv).grid(row=0, column=5, padx=4)
        ttk.Button(top, text="Export CSV", command=self.export_products_csv).grid(row=0, column=6, padx=4)

        main = ttk.Frame(c)
        main.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        c.rowconfigure(1, weight=1)
        c.columnconfigure(0, weight=1)
        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=7)
        main.rowconfigure(0, weight=1)

        left_btn = ttk.Frame(left)
        left_btn.grid(row=0, column=0, sticky="ew", pady=(0,6))
        ttk.Button(left_btn, text="Add", command=self.add_new_product).pack(side="left", padx=(0,6))
        ttk.Button(left_btn, text="Delete", command=self.delete_product).pack(side="left", padx=(0,6))

        self.product_tree = ttk.Treeview(left, columns=("code","name"), show="headings", selectmode="browse")
        self.product_tree.heading("code", text="Formulation Code")
        self.product_tree.heading("name", text="Name")
        self.product_tree.column("code", width=180, anchor="w")
        self.product_tree.column("name", width=420, anchor="w")
        self.product_tree.grid(row=1, column=0, sticky="nsew", padx=(0,4))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.product_tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.product_tree.configure(yscrollcommand=sb.set)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        self.product_tree.bind("<Double-1>", lambda e: self.quick_edit_product())

        def _on_mousewheel_tree(event):
            if getattr(event,"num",None)==4:
                self.product_tree.yview_scroll(-1,"units")
            elif getattr(event,"num",None)==5:
                self.product_tree.yview_scroll(1,"units")
            else:
                if event.delta>0:
                    self.product_tree.yview_scroll(-1,"units")
                elif event.delta<0:
                    self.product_tree.yview_scroll(1,"units")
            return "break"
        self.product_tree.bind("<MouseWheel>", _on_mousewheel_tree)
        self.product_tree.bind("<Button-4>", _on_mousewheel_tree)
        self.product_tree.bind("<Button-5>", _on_mousewheel_tree)

        # detail area
        detail_container = ttk.Frame(main)
        detail_container.grid(row=0, column=1, sticky="nsew", padx=(12,0))
        detail_canvas = tk.Canvas(detail_container, highlightthickness=0)
        detail_canvas.pack(side="left", fill="both", expand=True)
        self.detail_canvas = detail_canvas
        detail_scroll = ttk.Scrollbar(detail_container, orient="vertical", command=detail_canvas.yview)
        detail_scroll.pack(side="right", fill="y")
        detail_canvas.configure(yscrollcommand=detail_scroll.set)
        self.detail_inner = ttk.Frame(detail_canvas)
        self.detail_window = detail_canvas.create_window((0,0), window=self.detail_inner, anchor="nw")
        def _cfg(e):
            try:
                detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
            except Exception:
                pass
        self.detail_inner.bind("<Configure>", _cfg)

        def _on_mousewheel_detail(event):
            if getattr(event,"num",None)==4:
                self.detail_canvas.yview_scroll(-1,"units")
            elif getattr(event,"num",None)==5:
                self.detail_canvas.yview_scroll(1,"units")
            else:
                if event.delta>0:
                    self.detail_canvas.yview_scroll(-1,"units")
                elif event.delta<0:
                    self.detail_canvas.yview_scroll(1,"units")
            return "break"
        detail_canvas.bind("<MouseWheel>", _on_mousewheel_detail)
        detail_canvas.bind("<Button-4>", _on_mousewheel_detail)
        detail_canvas.bind("<Button-5>", _on_mousewheel_detail)

        r = 0
        ttk.Label(self.detail_inner, text="Formulation Code:").grid(row=r, column=0, sticky="e", padx=6, pady=6)
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(self.detail_inner, textvariable=self.code_var, state="disabled")
        self.code_entry.grid(row=r, column=1, sticky="ew", padx=6, pady=6)
        self.detail_inner.columnconfigure(1, weight=1)

        r+=1
        ttk.Label(self.detail_inner, text="Product Name:").grid(row=r, column=0, sticky="e", padx=6, pady=6)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.detail_inner, textvariable=self.name_var, state="disabled")
        self.name_entry.grid(row=r, column=1, sticky="ew", padx=6, pady=6)

        # parameter fields - generated dynamically
        self.param_vars = []
        self.param_entries = []
        params = self.param_manager.get_params()
        start_row = r+1
        row = start_row
        for i, pname in enumerate(params):
            lbl = ttk.Label(self.detail_inner, text=f"{pname}:")
            lbl.grid(row=row, column=0, sticky="e", padx=6, pady=4)
            v = tk.StringVar()
            e = ttk.Entry(self.detail_inner, textvariable=v, width=32)
            e.grid(row=row, column=1, sticky="ew", padx=6, pady=4)
            self.param_vars.append(v)
            self.param_entries.append(e)
            row += 1
        end_row = row
        ttk.Label(self.detail_inner, text="Update Date:").grid(row=end_row, column=0, sticky="e", padx=6, pady=8)
        self.update_date_var = tk.StringVar()
        self.update_date_entry = ttk.Entry(self.detail_inner, textvariable=self.update_date_var, state="disabled")
        self.update_date_entry.grid(row=end_row, column=1, sticky="w", padx=6, pady=8)

        try:
            entries = [self.code_entry, self.name_entry, self.update_date_entry] + list(self.param_entries)
            for w in entries:
                w.bind("<MouseWheel>", _on_mousewheel_detail)
                w.bind("<Button-4>", _on_mousewheel_detail)
                w.bind("<Button-5>", _on_mousewheel_detail)
        except Exception:
            pass

        btn_frame = ttk.Frame(self.detail_inner)
        btn_frame.grid(row=end_row+1, column=0, columnspan=4, pady=12)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.edit_product)
        self.edit_btn.pack(side="left", padx=6)
        self.save_btn = ttk.Button(btn_frame, text="Save", command=self.save_product, state="disabled")
        self.save_btn.pack(side="left", padx=6)
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit, state="disabled")
        self.cancel_btn.pack(side="left", padx=6)

    def on_search_change(self):
        self.load_products()

    def show_all_products(self):
        self.search_var.set("")
        self.load_products()

    def load_products(self):
        txt = self.search_var.get().strip()
        cur = self.db.conn.cursor()
        params = self.param_manager.get_params()
        param_cols = ", ".join([f"param{i+1}" for i in range(len(params))]) if params else ""
        select_cols = "id, code, name"
        if param_cols:
            select_cols = f"{select_cols}, {param_cols}"
        sql = f"SELECT {select_cols} FROM products"
        vals = ()
        if txt:
            sql += " WHERE code LIKE ? OR name LIKE ?"
            like = f"%{txt}%"
            vals = (like, like)
        sql += " ORDER BY code, name"
        try:
            cur.execute(sql, vals)
            rows = cur.fetchall()
            self.product_tree.delete(*self.product_tree.get_children())
            for r in rows:
                self.product_tree.insert("", "end", iid=str(r["id"]), values=(r["code"], r["name"]))
            self.status_set(f"Loaded {len(rows)} products.")
            self.clear_product_details()
        except Exception:
            logging.exception("load_products")
            UIHelpers.show_error("Error", "Failed to load products.")

    def clear_product_details(self):
        self.selected_product_id = None
        self.code_var.set("")
        self.name_var.set("")
        for v in self.param_vars:
            v.set("")
        self.update_date_var.set("")
        self._set_product_editable(False)

    def on_product_select(self, event=None):
        sel = self.product_tree.selection()
        if not sel:
            return
        try:
            pid = int(sel[0])
        except Exception:
            return
        cur = self.db.conn.cursor()
        params = self.param_manager.get_params()
        param_cols = ", ".join([f"param{i+1}" for i in range(len(params))]) if params else ""
        select_cols = "code, name"
        if param_cols:
            select_cols = f"{select_cols}, {param_cols}"
        select_cols = f"{select_cols}, update_date"
        try:
            cur.execute(f"SELECT {select_cols} FROM products WHERE id = ?", (pid,))
            row = cur.fetchone()
        except Exception:
            logging.exception("on_product_select query")
            row = None
        if row:
            self.selected_product_id = pid
            self.code_var.set(row["code"])
            self.name_var.set(row["name"])
            for i in range(len(params)):
                key = f"param{i+1}"
                try:
                    self.param_vars[i].set(row[key] if row[key] is not None else "")
                except Exception:
                    self.param_vars[i].set("")
            self.update_date_var.set(row["update_date"] if row["update_date"] else "")
            self._set_product_editable(False)
            self.status_set(f"Selected {row['code']} - {row['name']}")

    def _set_product_editable(self, editable: bool):
        state = "normal" if editable else "disabled"
        try:
            self.code_entry.config(state=state)
            self.name_entry.config(state=state)
            for e in self.param_entries:
                e.config(state=state)
            self.edit_btn.config(state="disabled" if editable or self.selected_product_id is None else "normal")
            self.save_btn.config(state="normal" if editable else "disabled")
            self.cancel_btn.config(state="normal" if editable else "disabled")
        except Exception:
            logging.exception("_set_product_editable")

    def edit_product(self):
        if not self.selected_product_id:
            UIHelpers.show_warning("Warning", "Select a product first.")
            return
        self._set_product_editable(True)

    def cancel_edit(self):
        if self.selected_product_id:
            self.on_product_select(None)
        else:
            self.clear_product_details()

    def save_product(self):
        code = self.code_var.get().strip()
        name = self.name_var.get().strip()
        if not code:
            UIHelpers.show_warning("Validation", "Formulation code cannot be empty.")
            return
        param_vals = [v.get().strip() for v in self.param_vars]
        now = datetime.now().strftime("%Y-%m-%d")
        try:
            if self.selected_product_id:
                set_parts = ["code=?", "name=?"] + [f"param{i+1}=?" for i in range(len(param_vals))] + ["update_date=?"]
                sql = f"UPDATE products SET {', '.join(set_parts)} WHERE id=?"
                params = (code, name, *param_vals, now, self.selected_product_id)
                self.db.execute_write(sql, params)
            else:
                cols = ["code", "name"] + [f"param{i+1}" for i in range(len(param_vals))] + ["update_date"]
                placeholders = ", ".join(["?"] * len(cols))
                sql = f"INSERT INTO products ({', '.join(cols)}) VALUES ({placeholders})"
                params = (code, name, *param_vals, now)
                lastid = self.db.execute_write(sql, params, return_lastrow=True)
                if lastid:
                    self.selected_product_id = lastid
            self.update_date_var.set(now)
            self._set_product_editable(False)
            self.load_products()
            self.status_set("Saved product.")
        except Exception:
            logging.exception("save_product")
            UIHelpers.show_error("Error", "Failed to save product.")

    def add_new_product(self):
        popup = tk.Toplevel(self)
        popup.title("New Formulation")
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)

        frm = ttk.Frame(popup, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        ttk.Label(frm, text="Formulation Code:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        code_var = tk.StringVar()
        init = self.search_var.get().strip()
        if init:
            code_var.set(init)
        code_entry = ttk.Entry(frm, textvariable=code_var, width=40)
        code_entry.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(6,0))
        def on_add():
            code = code_var.get().strip()
            if not code:
                UIHelpers.show_warning("Validation", "Formulation code cannot be empty.")
                return
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()
            self.selected_product_id = None
            self.code_var.set(code)
            self.name_var.set("")
            for v in self.param_vars:
                v.set("")
            self.update_date_var.set("")
            self._set_product_editable(True)
            try:
                self.name_entry.focus_set()
            except Exception:
                pass
            self.status_set("Adding new product.")
        def on_cancel():
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()
            self.status_set("Add cancelled.")
        ttk.Button(btn_frame, text="Add", command=on_add).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side="left", padx=6)
        try:
            popup.update_idletasks()
            code_entry.focus_set()
            code_entry.selection_range(0, tk.END)
        except Exception:
            pass
        self.wait_window(popup)

    def delete_product(self):
        if not self.selected_product_id:
            UIHelpers.show_warning("Warning", "Select a product to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected product AND its QC records?"):
            return
        try:
            self.db.execute_write("DELETE FROM products WHERE id = ?", (self.selected_product_id,))
            self.db.execute_write("DELETE FROM qc_records WHERE product_id = ?", (self.selected_product_id,))
            self.selected_product_id = None
            self.load_products()
            self.clear_product_details()
            self.status_set("Deleted product.")
        except Exception:
            logging.exception("delete_product")
            UIHelpers.show_error("Error", "Failed to delete product.")

    def quick_edit_product(self):
        sel = self.product_tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        cur = self.db.conn.cursor()
        cur.execute("SELECT code, name FROM products WHERE id = ?", (pid,))
        row = cur.fetchone()
        if not row:
            return
        dlg = tk.Toplevel(self)
        dlg.title("Quick Edit")
        dlg.transient(self)
        dlg.grab_set()
        ttk.Label(dlg, text="Formulation Code:").grid(row=0, column=0, padx=8, pady=8)
        code_var = tk.StringVar(value=row["code"])
        code_entry = ttk.Entry(dlg, textvariable=code_var)
        code_entry.grid(row=0, column=1, padx=8, pady=8)
        ttk.Label(dlg, text="Name:").grid(row=1, column=0, padx=8, pady=8)
        name_var = tk.StringVar(value=row["name"])
        name_entry = ttk.Entry(dlg, textvariable=name_var)
        name_entry.grid(row=1, column=1, padx=8, pady=8)
        def on_save():
            code = code_var.get().strip()
            name = name_var.get().strip()
            if not code:
                UIHelpers.show_warning("Validation", "Formulation code cannot be empty.")
                return
            try:
                self.db.execute_write("UPDATE products SET code = ?, name = ? WHERE id = ?", (code, name, pid))
                dlg.destroy()
                self.load_products()
                self.status_set("Product updated (quick).")
            except Exception:
                logging.exception("quick_edit save")
                UIHelpers.show_error("Error", "Failed to update product.")
        ttk.Button(dlg, text="Save", command=on_save).grid(row=2, column=0, columnspan=2, pady=8)

    # -------------------------
    # CSV import/export - products
    # -------------------------
    def export_products_csv(self):
        params = self.param_manager.get_params()
        param_cols = [f"param{i+1}" for i in range(len(params))]
        cur = self.db.conn.cursor()
        cols = ["code", "name"] + param_cols + ["update_date"]
        try:
            cur.execute(f"SELECT {', '.join(cols)} FROM products ORDER BY code, name")
            rows = cur.fetchall()
        except Exception:
            logging.exception("export_products query")
            UIHelpers.show_error("Error", "Failed to read products.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not file:
            return
        try:
            with open(file, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["formulation_code","name"] + params + ["update_date"])
                for r in rows:
                    out = [r["code"], r["name"]]
                    for pc in param_cols:
                        out.append(r[pc] if r[pc] is not None else "")
                    out.append(r["update_date"] if r["update_date"] is not None else "")
                    w.writerow(out)
            UIHelpers.show_info("Exported", f"Products exported to {file}")
            self.status_set(f"Products exported to {file}")
        except Exception:
            logging.exception("export_products write")
            UIHelpers.show_error("Error", "Failed to export products.")

    def import_products_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not file:
            return
        params = self.param_manager.get_params()
        param_cols = [f"param{i+1}" for i in range(len(params))]
        count_new = 0
        try:
            with open(file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = (row.get('formulation_code') or row.get('code') or "").strip()
                    name = (row.get('name') or "").strip()
                    if not code:
                        continue
                    param_values = [row.get(p, "").strip() for p in params]
                    now = datetime.now().strftime("%Y-%m-%d")
                    sql = f"INSERT INTO products (code, name, {', '.join(param_cols)}, update_date) VALUES ({', '.join(['?']*(2+len(param_cols)+1))})"
                    try:
                        self.db.execute_write(sql, (code, name, *param_values, now))
                        count_new += 1
                    except Exception:
                        logging.exception("import row failed")
            UIHelpers.show_info("Import complete", f"Imported {count_new} products.")
            self.status_set(f"Imported {count_new} products.")
            self.load_products()
            self.load_qc_products()
        except Exception:
            logging.exception("import_products")
            UIHelpers.show_error("Error", "Failed to import products.")

    # -------------------------
    # QC tab (autocomplete popup, QC list, plot)
    # -------------------------
    def _build_qc_tab(self):
        c = self.qc_frame
        for w in c.winfo_children():
            w.destroy()
        c.rowconfigure(3, weight=1)
        c.columnconfigure(0, weight=1)

        top = ttk.Frame(c)
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=6)
        top.columnconfigure(3, weight=1)

        ttk.Label(top, text="Product:").grid(row=0, column=0, sticky="w", padx=4)
        self.qc_product_entry = ttk.Entry(top, width=50)
        self.qc_product_entry.grid(row=0, column=1, sticky="w", padx=4)
        self._product_popup = None
        self._product_popup_lb = None
        self._product_display_list = []
        self.qc_product_map = {}

        self.qc_product_entry.bind("<KeyRelease>", self._qc_keyrelease)
        self.qc_product_entry.bind("<Down>", self._qc_focus_popup)
        self.qc_product_entry.bind("<Return>", lambda e: self._qc_enter())
        self.qc_product_entry.bind("<Escape>", lambda e: self._hide_product_popup())

        ttk.Label(top, text="Parameter:").grid(row=0, column=2, sticky="w", padx=4)
        self.qc_param_cb = ttk.Combobox(top, state="readonly", width=30)
        self.qc_param_cb.grid(row=0, column=3, sticky="ew", padx=4)
        self.qc_param_cb.bind("<<ComboboxSelected>>", lambda e: self.qc_param_changed())

        input_frame = ttk.Frame(c)
        input_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        input_frame.columnconfigure(7, weight=1)

        ttk.Label(input_frame, text="QC Value:").grid(row=0, column=0, sticky="w", padx=4)
        self.qc_value_var = tk.StringVar()
        self.qc_value_entry = ttk.Entry(input_frame, textvariable=self.qc_value_var, width=15)
        self.qc_value_entry.grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=2, sticky="w", padx=4)
        self.qc_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.qc_date_entry = ttk.Entry(input_frame, textvariable=self.qc_date_var, width=15)
        self.qc_date_entry.grid(row=0, column=3, sticky="w", padx=4)

        self.qc_add_btn = ttk.Button(input_frame, text="Add QC", command=self.add_qc_record)
        self.qc_add_btn.grid(row=0, column=4, padx=6)
        self.qc_delete_btn = ttk.Button(input_frame, text="Delete Selected", command=self.delete_qc_record)
        self.qc_delete_btn.grid(row=0, column=5, padx=6)
        ttk.Button(input_frame, text="Import QC CSV", command=self.import_qc_csv).grid(row=0, column=6, padx=6)
        ttk.Button(input_frame, text="Export QC CSV", command=self.export_qc_csv).grid(row=0, column=7, padx=6)

        self.qc_tree = ttk.Treeview(c, columns=("value","date"), show="headings")
        self.qc_tree.heading("value", text="QC Value")
        self.qc_tree.heading("date", text="Date")
        self.qc_tree.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        sb = ttk.Scrollbar(c, orient="vertical", command=self.qc_tree.yview)
        sb.grid(row=2, column=1, sticky="ns")
        self.qc_tree.configure(yscrollcommand=sb.set)
        try:
            self.qc_tree.tag_configure("alert", foreground="red")
        except Exception:
            pass

        graph_frame = ttk.Frame(c)
        graph_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=6)
        self.qc_fig, self.qc_ax = plt.subplots(figsize=(8,4))
        self.qc_canvas = FigureCanvasTkAgg(self.qc_fig, master=graph_frame)
        self.qc_canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_qc_products(self):
        cur = self.db.conn.cursor()
        try:
            cur.execute("SELECT id, code, name FROM products ORDER BY code, name")
            rows = cur.fetchall()
        except Exception:
            logging.exception("load_qc_products")
            rows = []
        display = []
        dmap = {}
        for r in rows:
            txt = f"{r['code']} — {r['name']}"
            if txt in dmap:
                txt = f"{txt} (#{r['id']})"
            display.append((txt, r["id"]))
            dmap[txt] = r["id"]
        self._product_display_list = display
        self.qc_product_map = dmap
        # select first if available
        if display:
            txt, pid = display[0]
            self.qc_product_entry.delete(0, tk.END)
            self.qc_product_entry.insert(0, txt)
            self.selected_product_id = pid
            self.load_params_into_qc()
            self.load_qc_records()
            self.status_set(f"Loaded {len(display)} products for QC.")
        else:
            self.qc_product_entry.delete(0, tk.END)
            self.qc_tree.delete(*self.qc_tree.get_children())
            self.status_set("No products for QC.")
            self._clear_qc_graph()

    def load_params_into_qc(self):
        vals = self.param_manager.get_params()
        try:
            self.qc_param_cb['values'] = vals
            if vals and not self.qc_param_cb.get():
                self.qc_param_cb.current(0)
        except Exception:
            pass

    def _create_product_popup(self):
        if self._product_popup and tk.Toplevel.winfo_exists(self._product_popup):
            return
        popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        frame = ttk.Frame(popup, relief="flat", borderwidth=1)
        frame.pack(fill="both", expand=True)
        lb = tk.Listbox(frame, activestyle="dotbox", exportselection=False, highlightthickness=0, font=self.base_font)
        lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.config(yscrollcommand=sb.set)
        lb.bind("<Double-Button-1>", lambda e: self._qc_popup_choose())
        lb.bind("<Return>", lambda e: self._qc_popup_choose())
        lb.bind("<Escape>", lambda e: self._hide_product_popup())
        lb.bind("<Up>", lambda e: self._qc_popup_nav(e))
        lb.bind("<Down>", lambda e: self._qc_popup_nav(e))
        lb.bind("<FocusOut>", lambda e: self._hide_product_popup_delayed())
        self._product_popup = popup
        self._product_popup_lb = lb

    def _position_popup(self):
        if not self._product_popup or not tk.Toplevel.winfo_exists(self._product_popup):
            return
        try:
            x = self.qc_product_entry.winfo_rootx()
            y = self.qc_product_entry.winfo_rooty() + self.qc_product_entry.winfo_height()
            width = max(self.qc_product_entry.winfo_width(), 300)
            self._product_popup.geometry(f"{width}x200+{x}+{y}")
            self._product_popup.deiconify()
        except Exception:
            pass

    def _hide_product_popup(self):
        if self._product_popup and tk.Toplevel.winfo_exists(self._product_popup):
            try:
                self._product_popup.withdraw()
            except Exception:
                pass

    def _hide_product_popup_delayed(self):
        self.after(100, self._hide_product_popup)

    def _qc_keyrelease(self, event):
        txt = self.qc_product_entry.get().strip().lower()
        if not txt:
            self._hide_product_popup()
            return
        matches = []
        for display, pid in self._product_display_list:
            if txt in display.lower():
                matches.append(display)
        if matches:
            self._create_product_popup()
            lb = self._product_popup_lb
            lb.delete(0, tk.END)
            for d in matches[:200]:
                lb.insert(tk.END, d)
            self._position_popup()
            try:
                lb.selection_clear(0, tk.END)
                lb.selection_set(0)
                lb.activate(0)
            except Exception:
                pass
        else:
            self._hide_product_popup()

    def _qc_focus_popup(self, event):
        if not self._product_popup or not tk.Toplevel.winfo_exists(self._product_popup):
            return "break"
        try:
            self._product_popup_lb.focus_set()
            if self._product_popup_lb.size() > 0:
                self._product_popup_lb.selection_clear(0, tk.END)
                self._product_popup_lb.selection_set(0)
                self._product_popup_lb.activate(0)
        except Exception:
            pass
        return "break"

    def _qc_popup_choose(self):
        if not self._product_popup_lb:
            return
        sel = self._product_popup_lb.curselection()
        if not sel:
            return
        text = self._product_popup_lb.get(sel[0])
        if text in self.qc_product_map:
            pid = self.qc_product_map[text]
            self.qc_product_entry.delete(0, tk.END)
            self.qc_product_entry.insert(0, text)
            self.selected_product_id = pid
            self._hide_product_popup()
            self.load_params_into_qc()
            self.load_qc_records()

    def _qc_popup_nav(self, event):
        lb = self._product_popup_lb
        if not lb:
            return "break"
        sz = lb.size()
        if sz == 0:
            return "break"
        cur = lb.curselection()
        if not cur:
            idx = 0
        else:
            idx = cur[0]
        if event.keysym == "Up":
            new = max(0, idx - 1)
        else:
            new = min(sz - 1, idx + 1)
        lb.selection_clear(0, tk.END)
        lb.selection_set(new)
        lb.activate(new)
        lb.see(new)
        return "break"

    def _qc_enter(self):
        txt = self.qc_product_entry.get().strip()
        if not txt:
            return
        if txt in self.qc_product_map:
            self.selected_product_id = self.qc_product_map[txt]
            self._hide_product_popup()
            self.load_params_into_qc()
            self.load_qc_records()
            return
        if self._product_popup_lb and self._product_popup_lb.size() > 0:
            first = self._product_popup_lb.get(0)
            if first in self.qc_product_map:
                self.qc_product_entry.delete(0, tk.END)
                self.qc_product_entry.insert(0, first)
                self.selected_product_id = self.qc_product_map[first]
                self._hide_product_popup()
                self.load_params_into_qc()
                self.load_qc_records()
                return
        self.qc_tree.delete(*self.qc_tree.get_children())
        self._clear_qc_graph()
        self.status_set("Select valid product.")

    def qc_param_changed(self):
        self.load_qc_records()

    def load_qc_records(self):
        product_id = self.selected_product_id
        param_name = self.qc_param_cb.get()
        if product_id is None or not param_name:
            self.qc_tree.delete(*self.qc_tree.get_children())
            self.status_set("Select product and parameter.")
            self._clear_qc_graph()
            return
        try:
            param_index = self.param_manager.get_params().index(param_name) + 1
        except ValueError:
            self.qc_tree.delete(*self.qc_tree.get_children())
            self.status_set("Parameter not found.")
            self._clear_qc_graph()
            return
        self.selected_param_index = param_index
        cur = self.db.conn.cursor()
        cur.execute("""SELECT id, qc_value, qc_date FROM qc_records
                       WHERE product_id = ? AND param_index = ?
                       ORDER BY qc_date""", (product_id, param_index))
        rows = cur.fetchall()
        self.qc_tree.delete(*self.qc_tree.get_children())
        pname = (param_name or "").strip().lower()
        for r in rows:
            qcv = r["qc_value"]
            alert = False
            try:
                num = float(qcv)
                if pname == "head tear strength" and num <= 450:
                    alert = True
            except Exception:
                alert = False
            if alert:
                try:
                    self.qc_tree.insert("", "end", iid=str(r["id"]), values=(r["qc_value"], r["qc_date"]), tags=("alert",))
                except Exception:
                    self.qc_tree.insert("", "end", iid=str(r["id"]), values=(r["qc_value"], r["qc_date"]))
            else:
                self.qc_tree.insert("", "end", iid=str(r["id"]), values=(r["qc_value"], r["qc_date"]))
        self.status_set(f"Loaded {len(rows)} QC records.")
        self._plot_qc_graph(rows)

    def add_qc_record(self):
        pid = self.selected_product_id
        pidx = self.selected_param_index
        val = self.qc_value_var.get().strip()
        date_s = self.qc_date_var.get().strip()
        if pid is None or pidx is None:
            UIHelpers.show_warning("Warning", "Select product and parameter.")
            return
        if not val:
            UIHelpers.show_warning("Warning", "QC value cannot be empty.")
            return
        try:
            datetime.strptime(date_s, "%Y-%m-%d")
        except ValueError:
            UIHelpers.show_warning("Warning", "Date must be YYYY-MM-DD.")
            return
        try:
            self.db.execute_write("INSERT INTO qc_records (product_id, param_index, qc_value, qc_date) VALUES (?, ?, ?, ?)",
                                  (pid, pidx, val, date_s))
            self.qc_value_var.set("")
            self.qc_date_var.set(datetime.now().strftime("%Y-%m-%d"))
            self.load_qc_records()
            self.status_set("QC record added.")
        except Exception:
            logging.exception("add_qc")
            UIHelpers.show_error("Error", "Failed to add QC record.")

    def delete_qc_record(self):
        sel = self.qc_tree.selection()
        if not sel:
            UIHelpers.show_warning("Warning", "Select a QC record to delete.")
            return
        rec_id = int(sel[0])
        if not messagebox.askyesno("Confirm", "Delete selected QC record?"):
            return
        try:
            self.db.execute_write("DELETE FROM qc_records WHERE id = ?", (rec_id,))
            self.load_qc_records()
            self.status_set("QC record deleted.")
        except Exception:
            logging.exception("delete_qc_record")
            UIHelpers.show_error("Error", "Failed to delete QC record.")

    def _clear_qc_graph(self):
        try:
            self.qc_ax.clear()
            self.qc_canvas.draw()
        except Exception:
            pass

    def _plot_qc_graph(self, records):
        try:
            self.qc_ax.clear()
            if not records:
                self.qc_canvas.draw()
                return
            dates = []
            vals = []
            for rec in records:
                try:
                    dates.append(datetime.strptime(rec["qc_date"], "%Y-%m-%d"))
                    vals.append(float(rec["qc_value"]))
                except Exception:
                    continue
            if not dates or not vals:
                self.qc_canvas.draw()
                return
            pname = (self.qc_param_cb.get() or "").strip().lower()
            colors = None
            if pname == "head tear strength":
                colors = ["red" if (v <= 450) else "blue" for v in vals]
            # baseline
            try:
                self.qc_ax.plot(dates, vals, linestyle='-', color='lightgray', zorder=1)
                if colors:
                    self.qc_ax.scatter(dates, vals, c=colors, zorder=2)
                else:
                    self.qc_ax.plot(dates, vals, marker='o', linestyle='-', zorder=2)
                title = f"QC: {self.qc_param_cb.get()} for {self.qc_product_entry.get()}"
                self.qc_ax.set_title(title)
                self.qc_ax.set_xlabel("Date")
                self.qc_ax.set_ylabel("Value")
                self.qc_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                self.qc_fig.autofmt_xdate()
                if MPLCURSORS_AVAILABLE:
                    try:
                        if colors and self.qc_ax.collections:
                            mplcursors.cursor(self.qc_ax.collections[-1], hover=True)
                        elif self.qc_ax.lines:
                            mplcursors.cursor(self.qc_ax.lines[-1], hover=True)
                    except Exception:
                        pass
            except Exception:
                logging.exception("plotting")
            self.qc_canvas.draw()
        except Exception:
            logging.exception("plot_qc_graph failed")

    def export_qc_csv(self):
        cur = self.db.conn.cursor()
        cur.execute("SELECT p.code as product_code, r.param_index, r.qc_value, r.qc_date FROM qc_records r JOIN products p ON p.id = r.product_id ORDER BY p.code, r.param_index, r.qc_date")
        rows = cur.fetchall()
        params = self.param_manager.get_params()
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not file:
            return
        try:
            with open(file, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["formulation_code","parameter","qc_value","qc_date"])
                for r in rows:
                    pname = params[r["param_index"]-1] if 0 < r["param_index"] <= len(params) else f"param{r['param_index']}"
                    w.writerow([r["product_code"], pname, r["qc_value"], r["qc_date"]])
            UIHelpers.show_info("Exported", f"QC exported to {file}")
            self.status_set(f"QC exported to {file}")
        except Exception:
            logging.exception("export_qc")
            UIHelpers.show_error("Error", "Failed to export QC records.")

    def import_qc_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not file:
            return
        params = self.param_manager.get_params()
        inserted = 0
        try:
            with open(file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    product_code = (row.get('formulation_code') or row.get('product_code') or "").strip()
                    param_name = (row.get('parameter') or "").strip()
                    qc_value = (row.get('qc_value') or "").strip()
                    qc_date = (row.get('qc_date') or "").strip()
                    if not product_code or not param_name:
                        continue
                    cur = self.db.conn.cursor()
                    cur.execute("SELECT id FROM products WHERE code = ? LIMIT 1", (product_code,))
                    p = cur.fetchone()
                    if not p:
                        continue
                    try:
                        param_index = params.index(param_name) + 1
                    except ValueError:
                        continue
                    try:
                        datetime.strptime(qc_date, "%Y-%m-%d")
                    except Exception:
                        qc_date = datetime.now().strftime("%Y-%m-%d")
                    try:
                        self.db.execute_write("INSERT INTO qc_records (product_id, param_index, qc_value, qc_date) VALUES (?, ?, ?, ?)",
                                              (p["id"], param_index, qc_value, qc_date))
                        inserted += 1
                    except Exception:
                        logging.exception("import qc row failed")
            UIHelpers.show_info("Import complete", f"Imported {inserted} QC records.")
            self.status_set(f"Imported {inserted} QC records.")
            self.load_qc_records()
        except Exception:
            logging.exception("import_qc")
            UIHelpers.show_error("Error", "Failed to import QC records.")

    # -------------------------
    # Parameters tab
    # -------------------------
    def _build_param_tab(self):
        c = self.param_frame
        for w in c.winfo_children():
            w.destroy()
        c.columnconfigure(0, weight=1)
        c.rowconfigure(1, weight=1)
        btns = ttk.Frame(c)
        btns.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        ttk.Button(btns, text="Add", command=self.add_parameter).pack(side="left", padx=6)
        ttk.Button(btns, text="Rename", command=self.rename_parameter).pack(side="left", padx=6)
        ttk.Button(btns, text="Delete", command=self.delete_parameter).pack(side="left", padx=6)
        ttk.Button(btns, text="Move Up", command=lambda: self.move_param(-1)).pack(side="left", padx=6)
        ttk.Button(btns, text="Move Down", command=lambda: self.move_param(1)).pack(side="left", padx=6)
        ttk.Button(btns, text="Refresh", command=self.load_params_list).pack(side="left", padx=6)
        self.param_listbox = tk.Listbox(c, font=self.base_font, height=20, exportselection=False)
        self.param_listbox.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        self.load_params_list()

    def load_params_list(self):
        try:
            cur_sel = self.param_listbox.curselection()
            cur_index = cur_sel[0] if cur_sel else None
        except Exception:
            cur_index = None
        self.param_listbox.delete(0, tk.END)
        for p in self.param_manager.get_params():
            self.param_listbox.insert(tk.END, p)
        try:
            vals = self.param_manager.get_params()
            self.qc_param_cb['values'] = vals
            if vals and not self.qc_param_cb.get():
                self.qc_param_cb.current(0)
        except Exception:
            pass
        try:
            if cur_index is not None:
                size = self.param_listbox.size()
                if size>0:
                    sel = min(max(0,cur_index), size-1)
                    self.param_listbox.selection_clear(0, tk.END)
                    self.param_listbox.selection_set(sel)
                    self.param_listbox.activate(sel)
                    self.param_listbox.see(sel)
        except Exception:
            pass

    def add_parameter(self):
        name = UIHelpers.ask_string("Add Parameter", "Enter new parameter name:")
        if not name:
            return
        ok, err = self.param_manager.add_param(name)
        if ok:
            UIHelpers.show_info("Success", f"Parameter '{name}' added.")
            self.load_params_list()
            self.db.ensure_products_table(self.param_manager.get_params())
            self._rebuild_products_ui()
        else:
            UIHelpers.show_error("Error", f"Failed to add parameter: {err}")

    def rename_parameter(self):
        sel = self.param_listbox.curselection()
        if not sel:
            UIHelpers.show_warning("Warning", "Select a parameter to rename.")
            return
        old = self.param_listbox.get(sel[0])
        new = UIHelpers.ask_string("Rename Parameter", f"New name for '{old}':", initial=old)
        if not new:
            return
        ok, err = self.param_manager.rename_param(old, new)
        if ok:
            UIHelpers.show_info("Success", f"Renamed '{old}' to '{new}'.")
            self.load_params_list()
            self._rebuild_products_ui()
        else:
            UIHelpers.show_error("Error", f"Rename failed: {err}")

    def move_param(self, direction):
        sel = self.param_listbox.curselection()
        if not sel:
            self.status_set("Select a parameter to move.")
            return
        idx = sel[0]
        params = self.param_manager.get_params()
        new_idx = idx + direction
        if not (0 <= new_idx < len(params)):
            return
        new_order = list(params)
        item = new_order.pop(idx)
        new_order.insert(new_idx, item)
        if self.param_manager.reorder_params(new_order):
            self.load_params_list()
            self.db.ensure_products_table(self.param_manager.get_params())
            self._rebuild_products_ui()
            try:
                size = self.param_listbox.size()
                sel_pos = min(max(0, new_idx), size-1)
                self.param_listbox.selection_clear(0, tk.END)
                self.param_listbox.selection_set(sel_pos)
                self.param_listbox.activate(sel_pos)
                self.param_listbox.see(sel_pos)
                self.param_listbox.focus_set()
            except Exception:
                pass
            self.status_set("Parameter order updated.")
        else:
            UIHelpers.show_error("Error", "Failed to reorder parameters.")

    def delete_parameter(self):
        sel = self.param_listbox.curselection()
        if not sel:
            UIHelpers.show_warning("Warning", "Select a parameter to delete.")
            return
        name = self.param_listbox.get(sel[0])
        if not messagebox.askyesno("Confirm", f"Delete parameter '{name}'? This removes it from products and QC data."):
            return
        try:
            idx = None
            try:
                idx = self.param_manager.get_params().index(name) + 1
            except ValueError:
                idx = None
            if self.param_manager.remove_param(name):
                if idx is not None:
                    self.db.execute_write("DELETE FROM qc_records WHERE param_index = ?", (idx,))
                    self.db.execute_write("UPDATE qc_records SET param_index = param_index - 1 WHERE param_index > ?", (idx,))
                UIHelpers.show_info("Success", f"Parameter '{name}' deleted.")
                self.load_params_list()
                self.db.ensure_products_table(self.param_manager.get_params())
                self._rebuild_products_ui()
            else:
                UIHelpers.show_error("Error", "Failed to delete parameter.")
        except Exception:
            logging.exception("delete_parameter")
            UIHelpers.show_error("Error", "Failed to delete parameter.")

    def _rebuild_products_ui(self):
        # rebuild whole products tab to reflect new parameters
        self._build_products_tab()
        self.load_products()
        self.load_qc_products()

    # -------------------------
    # DB watcher
    # -------------------------
    def _start_db_watcher(self):
        try:
            self._check_db_updated()
        except Exception:
            logging.exception("start_db_watcher")

    def _check_db_updated(self):
        try:
            if os.path.exists(self.db.db_path):
                m = os.path.getmtime(self.db.db_path)
                if self._db_mtime is None:
                    self._db_mtime = m
                elif m != self._db_mtime:
                    self._db_mtime = m
                    editing = (hasattr(self, "save_btn") and self.save_btn['state'] == "normal" and self.edit_btn['state'] == "disabled")
                    if not editing:
                        self.load_products()
                        self.load_qc_products()
                        self.status_set("DB changed externally — reloaded.")
                    else:
                        self.status_set("DB changed externally; reload deferred (editing).")
        except Exception:
            logging.exception("db watcher")
        finally:
            self.after(self._db_watcher_interval, self._check_db_updated)

    def _on_tab_changed(self, event=None):
        try:
            cur = self.notebook.select()
            widget = self.notebook.nametowidget(cur) if cur else None
            if widget is not self.qc_frame:
                self._hide_product_popup()
        except Exception:
            logging.exception("_on_tab_changed")

    # -------------------------
    # Close
    # -------------------------
    def on_close(self):
        try:
            try:
                self._do_backup("close")
            except Exception:
                pass
            try:
                if self._lock_path:
                    release_lock(self._lock_path)
            except Exception:
                logging.exception("release lock on close")
            self.db.close()
        except Exception:
            logging.exception("on_close")
        try:
            if self._next_backup_job:
                try:
                    self.after_cancel(self._next_backup_job)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            try:
                tmp = tk.Tk()
                tmp.destroy()
            except Exception:
                pass

# -------------------------
# Startup
# -------------------------
def choose_db():
    path = SHARED_DB_PATH
    try:
        if path:
            d = os.path.dirname(os.path.abspath(path)) or "."
            if os.path.isdir(d):
                logging.info(f"Using configured shared DB path: {path}")
                return path
            else:
                logging.warning(f"Shared DB dir not found: {d} — fallback to local")
    except Exception:
        logging.exception("choose_db")
    return DEFAULT_LOCAL_DB

if __name__ == "__main__":
    try:
        dbp = choose_db()
        lockp = lock_file_path_for_db(dbp)
        ok, info = acquire_lock(lockp)
        if not ok:
            msg = "Another user appears to be using the shared database.\n\n"
            try:
                user = info.get("user","unknown")
                host = info.get("host","unknown")
                pid = info.get("pid","unknown")
                ts = info.get("ts","unknown")
                msg += f"User: {user}\nHost: {host}\nPID: {pid}\nStarted: {ts}\n\n"
            except Exception:
                pass
            msg += "To prevent DB corruption the app will exit. If you think this is wrong, check the lock file or contact admin."
            try:
                messagebox.showerror("Database Locked", msg)
            except Exception:
                print(msg)
            raise SystemExit("DB locked")

        atexit.register(lambda: release_lock(lockp))

        configure_shared_log(dbp)

        app = ProductManagerApp(dbp, lockp)
        app.mainloop()
    except SystemExit:
        pass
    except Exception as e:
        logging.exception("Fatal error")
        try:
            messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")
        except Exception:
            try:
                tmp = tk.Tk()
                tmp.withdraw()
                messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}", parent=tmp)
                tmp.destroy()
            except Exception:
                print("Fatal Error:", e)
                traceback.print_exc()
