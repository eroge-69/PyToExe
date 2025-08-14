
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QMimeData, QRectF, QDate
from PySide6.QtGui import QAction, QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QListWidget, QListWidgetItem, QFormLayout, QMessageBox, QComboBox,
    QLineEdit, QGroupBox, QSplitter, QFileDialog, QTextEdit, QSpinBox, QDateEdit,
    QDialog, QDialogButtonBox, QListView, QCheckBox, QGraphicsView, QGraphicsScene
)

APP_DIR = Path.home() / ".kanban_desktop"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "kanban.db"

COLUMNS_DEFAULT = ["Backlog", "To Do", "In Progress", "Review", "Done"]

def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

def to_iso(d: Optional[QDate]) -> Optional[str]:
    if not d or not d.isValid(): return None
    return f"{d.year():04d}-{d.month():02d}-{d.day():02d}T00:00:00"

def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect_db()
    cur = con.cursor()
    cur.executescript("""
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, code TEXT, created_at TEXT DEFAULT (datetime('now')));
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS columns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, order_index INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER,
  title TEXT NOT NULL,
  description TEXT,
  assignee_id INTEGER,
  column_id INTEGER,
  priority TEXT,
  estimate_hours REAL,
  started_at TEXT,
  due_date TEXT,
  done_at TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT,
  health TEXT
);
CREATE TABLE IF NOT EXISTS subtasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  is_done INTEGER DEFAULT 0,
  order_index INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS dependencies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  depends_on_task_id INTEGER NOT NULL
);
""")
    # Seed columns
    cur.execute("SELECT COUNT(*) FROM columns")
    if cur.fetchone()[0] == 0:
        for i, name in enumerate(COLUMNS_DEFAULT):
            cur.execute("INSERT INTO columns (name, order_index) VALUES (?,?)", (name, i))
    # Seed project/user
    cur.execute("SELECT COUNT(*) FROM projects")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO projects (name, code) VALUES (?,?)", ("Projekt domyślny", "PRJ-1"))
    cur.execute("SELECT COUNT(*) FROM users WHERE is_active=1")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (name, is_active) VALUES (?,1)", ("Użytkownik 1",))
    con.commit()
    con.close()

def fetch_all(sql, params=()):
    con = connect_db()
    cur = con.cursor()
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def fetch_one(sql, params=()):
    con = connect_db()
    cur = con.cursor()
    cur.execute(sql, params)
    r = cur.fetchone()
    con.close()
    return dict(r) if r else None

def execute(sql, params=()):
    con = connect_db()
    cur = con.cursor()
    cur.execute(sql, params)
    con.commit()
    rid = cur.lastrowid
    con.close()
    return rid

def execute_many(sql, seq):
    con = connect_db()
    cur = con.cursor()
    cur.executemany(sql, seq)
    con.commit()
    con.close()

class TaskItem(QListWidgetItem):
    def __init__(self, task):
        super().__init__(f"{task['title']}  •  {task.get('priority') or '-'}")
        self.task = task
        self.setFlags(self.flags() | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable)

class DroppableList(QListWidget):
    def __init__(self, board, column, parent=None):
        super().__init__(parent)
        self.board = board
        self.column = column  # dict
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(260)
        self.itemDoubleClicked.connect(self.open_task_dialog)

    def open_task_dialog(self, item: TaskItem):
        dlg = TaskDialog(self.board, item.task["id"], self)
        if dlg.exec() == QDialog.Accepted:
            self.board.reload_board()

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        data = e.mimeData().text()
        try:
            task_id = int(data)
        except:
            return
        self.board.move_task(task_id, self.column)

class TaskDialog(QDialog):
    def __init__(self, board, task_id: int, parent=None):
        super().__init__(parent)
        self.board = board
        self.task_id = task_id
        self.setWindowTitle("Zadanie — szczegóły")
        self.resize(560, 520)

        task = fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
        users = fetch_all("SELECT * FROM users WHERE is_active=1 ORDER BY name")
        deps = fetch_all("SELECT depends_on_task_id FROM dependencies WHERE task_id=?", (task_id,))
        dep_ids = set([d["depends_on_task_id"] for d in deps])

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.title = QLineEdit(task["title"])
        self.desc = QTextEdit(task.get("description") or "")
        self.assignee = QComboBox()
        self.assignee.addItem("—", None)
        for u in users:
            self.assignee.addItem(u["name"], u["id"])
        idx = self.assignee.findData(task.get("assignee_id"))
        if idx >= 0: self.assignee.setCurrentIndex(idx)

        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        if task.get("priority"): self.priority.setCurrentText(task["priority"])

        self.estimate = QSpinBox()
        self.estimate.setRange(0, 10000)
        self.estimate.setValue(int(task.get("estimate_hours") or 0))

        self.due = QDateEdit()
        self.due.setCalendarPopup(True)
        if task.get("due_date"):
            dt = datetime.fromisoformat(task["due_date"].replace("Z",""))
            self.due.setDate(QDate(dt.year, dt.month, dt.day))

        form.addRow("Tytuł:", self.title)
        form.addRow("Opis:", self.desc)
        form.addRow("Osoba:", self.assignee)
        form.addRow("Priorytet:", self.priority)
        form.addRow("Estymata (h):", self.estimate)
        form.addRow("Termin:", self.due)

        # Subtasks
        self.subtasks_list = QListWidget()
        subs = fetch_all("SELECT * FROM subtasks WHERE task_id=? ORDER BY order_index, id", (task_id,))
        for s in subs:
            cb = QCheckBox(s["title"])
            cb.setChecked(bool(s["is_done"]))
            item = QListWidgetItem()
            self.subtasks_list.addItem(item)
            self.subtasks_list.setItemWidget(item, cb)
            # attach id
            item.setData(Qt.UserRole, s["id"])

        self.new_sub = QLineEdit()
        btn_add_sub = QPushButton("Dodaj pod-zadanie")
        btn_add_sub.clicked.connect(self.add_subtask)

        sub_box = QVBoxLayout()
        sub_box.addWidget(QLabel("Pod-zadania:"))
        sub_box.addWidget(self.subtasks_list, 1)
        row = QHBoxLayout()
        row.addWidget(self.new_sub, 1)
        row.addWidget(btn_add_sub)
        sub_box.addLayout(row)

        # Dependencies
        dep_box = QVBoxLayout()
        dep_box.addWidget(QLabel("Zależności (blokery) – wybierz zadania, które MUSZĄ być w Done:"))

        self.deps_list = QListWidget()
        self.deps_list.setSelectionMode(QListWidget.MultiSelection)
        all_same_project_tasks = fetch_all("SELECT id, title FROM tasks WHERE project_id=(SELECT project_id FROM tasks WHERE id=?) AND id<>? ORDER BY created_at DESC", (task_id, task_id))
        for t in all_same_project_tasks:
            it = QListWidgetItem(f"{t['id']}: {t['title']}")
            it.setData(Qt.UserRole, t["id"])
            if t["id"] in dep_ids:
                it.setSelected(True)
            self.deps_list.addItem(it)

        dep_box.addWidget(self.deps_list)

        root.addLayout(form)
        root.addLayout(sub_box)
        root.addLayout(dep_box)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.on_save)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def add_subtask(self):
        title = self.new_sub.text().strip()
        if not title: return
        order = fetch_one("SELECT COALESCE(MAX(order_index),0)+1 as oi FROM subtasks WHERE task_id=?", (self.task_id,))["oi"]
        execute("INSERT INTO subtasks (task_id, title, is_done, order_index) VALUES (?,?,0,?)", (self.task_id, title, order))
        self.new_sub.clear()
        # refresh list
        self.subtasks_list.clear()
        subs = fetch_all("SELECT * FROM subtasks WHERE task_id=? ORDER BY order_index, id", (self.task_id,))
        for s in subs:
            cb = QCheckBox(s["title"])
            cb.setChecked(bool(s["is_done"]))
            item = QListWidgetItem()
            self.subtasks_list.addItem(item)
            self.subtasks_list.setItemWidget(item, cb)
            item.setData(Qt.UserRole, s["id"])

    def on_save(self):
        # Save main fields
        due_iso = to_iso(self.due.date()) if self.due.date().isValid() else None
        execute("""UPDATE tasks SET
            title=?, description=?, assignee_id=?, priority=?, estimate_hours=?, due_date=?, updated_at=?
            WHERE id=?""",
            (self.title.text().strip(), self.desc.toPlainText().strip() or None,
             self.assignee.currentData(), self.priority.currentText(),
             float(self.estimate.value()), due_iso, now_iso(), self.task_id)
        )
        # Save subtasks
        for i in range(self.subtasks_list.count()):
            item = self.subtasks_list.item(i)
            wid = self.subtasks_list.itemWidget(item)
            sid = item.data(Qt.UserRole)
            execute("UPDATE subtasks SET is_done=? WHERE id=?", (1 if wid.isChecked() else 0, sid))
        # Save dependencies
        execute("DELETE FROM dependencies WHERE task_id=?", (self.task_id,))
        to_ins = []
        for i in range(self.deps_list.count()):
            it = self.deps_list.item(i)
            if it.isSelected():
                to_ins.append((self.task_id, it.data(Qt.UserRole)))
        if to_ins:
            execute_many("INSERT INTO dependencies (task_id, depends_on_task_id) VALUES (?,?)", to_ins)
        self.accept()

class TimelineTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        ctl = QHBoxLayout()
        ctl.addWidget(QLabel("Projekt:"))
        self.sel_project = QComboBox()
        for p in fetch_all("SELECT * FROM projects ORDER BY created_at DESC"):
            self.sel_project.addItem(p["name"], p["id"])
        self.sel_project.currentIndexChanged.connect(self.reload)
        ctl.addWidget(self.sel_project, 1)
        root.addLayout(ctl)

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        root.addWidget(self.view, 1)

        self.reload()

    def reload(self):
        pid = self.sel_project.currentData()
        tasks = fetch_all("SELECT * FROM tasks WHERE project_id=?", (pid,))
        if not tasks:
            self.scene.clear()
            return
        # compute min/max
        dates = []
        for t in tasks:
            for key in ("started_at","created_at","due_date","done_at"):
                if t.get(key):
                    try:
                        dates.append(datetime.fromisoformat(t[key].replace("Z","")))
                    except:
                        pass
        if not dates:
            self.scene.clear()
            return
        start = min(dates)
        end = max(dates)
        total = (end - start).total_seconds() or 1

        self.scene.clear()
        W = 1000
        H = 24 * len(tasks) + 40
        y = 20
        self.scene.setSceneRect(0, 0, W+40, H+40)

        # grid
        pen = QPen(QColor("#dddddd"))
        for i in range(0,11):
            x = 20 + (W * i/10)
            self.scene.addLine(x, 10, x, H, pen)

        # bars
        for t in tasks:
            a = t.get("started_at") or t.get("created_at")
            b = t.get("done_at") or t.get("due_date") or t.get("created_at")
            try:
                a_dt = datetime.fromisoformat(a.replace("Z",""))
                b_dt = datetime.fromisoformat(b.replace("Z",""))
            except:
                continue
            ax = 20 + int(((a_dt - start).total_seconds() / total) * W)
            bx = 20 + int(((b_dt - start).total_seconds() / total) * W)
            rect = QRectF(ax, y, max(6, bx-ax), 16)
            brush = QBrush(QColor("#a5b4fc") if not t.get("done_at") else QColor("#86efac"))
            self.scene.addRect(rect, QPen(Qt.NoPen), brush)
            self.scene.addText(t["title"]).setPos(24, y-14)
            y += 24

class BoardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = fetch_all("SELECT * FROM projects ORDER BY created_at DESC")
        self.users = fetch_all("SELECT * FROM users WHERE is_active=1 ORDER BY name")
        self.columns = fetch_all("SELECT * FROM columns ORDER BY order_index")
        self.current_project_id = self.projects[0]["id"] if self.projects else None

        root = QVBoxLayout(self)
        ctl = QHBoxLayout()
        ctl.addWidget(QLabel("Projekt:"))
        self.sel_project = QComboBox()
        for p in self.projects:
            self.sel_project.addItem(p["name"], p["id"])
        self.sel_project.currentIndexChanged.connect(self.on_project_change)
        ctl.addWidget(self.sel_project, 1)

        self.title = QLineEdit(); self.title.setPlaceholderText("Tytuł zadania")
        self.desc = QLineEdit(); self.desc.setPlaceholderText("Opis (opcjonalnie)")
        self.assignee = QComboBox(); self.assignee.addItem("—", None)
        for u in self.users: self.assignee.addItem(u["name"], u["id"])
        self.priority = QComboBox(); self.priority.addItems(["Low","Medium","High"]); self.priority.setCurrentText("Medium")
        self.estimate = QSpinBox(); self.estimate.setRange(0,10000); self.estimate.setPrefix("ETAh "); self.estimate.setValue(0)
        self.due = QDateEdit(); self.due.setCalendarPopup(True); self.due.setDate(QDate.currentDate())

        ctl.addWidget(self.title, 2)
        ctl.addWidget(self.desc, 3)
        ctl.addWidget(self.assignee, 1)
        ctl.addWidget(self.priority, 1)
        ctl.addWidget(self.estimate, 1)
        ctl.addWidget(self.due, 1)

        btn = QPushButton("Dodaj zadanie"); btn.clicked.connect(self.add_task)
        ctl.addWidget(btn)

        root.addLayout(ctl)

        self.split = QSplitter()
        self.col_widgets = []
        for c in self.columns:
            box = QGroupBox(c["name"])
            v = QVBoxLayout(box)
            lw = DroppableList(self, c, self)
            v.addWidget(lw)
            self.col_widgets.append((c, lw))
            self.split.addWidget(box)
        root.addWidget(self.split, 1)

        self.reload_board()

    def on_project_change(self):
        self.current_project_id = self.sel_project.currentData()
        self.reload_board()

    def reload_board(self):
        if not self.current_project_id:
            return
        tasks = fetch_all("SELECT * FROM tasks WHERE project_id=? ORDER BY updated_at DESC, created_at DESC", (self.current_project_id,))
        self.tasks_by_col = {}
        for t in tasks:
            self.tasks_by_col.setdefault(t["column_id"], []).append(t)
        for (col, lw) in self.col_widgets:
            lw.clear()
            for t in self.tasks_by_col.get(col["id"], []):
                it = TaskItem(t)
                lw.addItem(it)

    def move_task(self, task_id: int, target_col: dict):
        # Enforce dependencies when moving forward (to a column with higher order_index)
        t = fetch_one("SELECT * FROM tasks WHERE id=?", (task_id,))
        if not t: return
        source_col = fetch_one("SELECT * FROM columns WHERE id=?", (t["column_id"],))
        if not source_col: return
        if target_col["order_index"] > source_col["order_index"]:
            # moving forward -> check blockers
            blockers = fetch_all("SELECT depends_on_task_id FROM dependencies WHERE task_id=?", (task_id,))
            blocker_ids = [b["depends_on_task_id"] for b in blockers]
            if blocker_ids:
                # any blocker not in Done?
                q = """
                SELECT COUNT(*) as n
                FROM tasks
                JOIN columns ON columns.id = tasks.column_id
                WHERE tasks.id IN (%s) AND columns.name <> 'Done'
                """ % (",".join("?"*len(blocker_ids)))
                not_done = fetch_one(q, tuple(blocker_ids))["n"]
                if not_done > 0:
                    QMessageBox.warning(self, "Zablokowane",
                        "Nie można przenieść zadania do przodu.\nIstnieją blokery, które nie są w kolumnie Done.")
                    return
        # set timestamps
        started_at = t["started_at"]
        done_at = t["done_at"]
        if target_col["name"] == "In Progress" and not started_at:
            started_at = now_iso()
        if target_col["name"] == "Done":
            done_at = now_iso()
        if target_col["name"] != "Done":
            done_at = None
        execute("UPDATE tasks SET column_id=?, started_at=?, done_at=?, updated_at=? WHERE id=?",
                (target_col["id"], started_at, done_at, now_iso(), task_id))
        self.reload_board()

    def add_task(self):
        title = self.title.text().strip()
        if not title:
            QMessageBox.warning(self, "Brak tytułu", "Wpisz tytuł zadania.")
            return
        desc = self.desc.text().strip() or None
        assignee_id = self.assignee.currentData()
        priority = self.priority.currentText()
        est = float(self.estimate.value())
        due_iso = to_iso(self.due.date())
        first_col = self.columns[0]["id"]
        execute("""INSERT INTO tasks
            (project_id, title, description, assignee_id, column_id, priority, estimate_hours, due_date, created_at, updated_at, health)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (self.current_project_id, title, desc, assignee_id, first_col, priority, est, due_iso, now_iso(), now_iso(), "on_track"))
        self.title.clear(); self.desc.clear(); self.estimate.setValue(0)
        self.reload_board()

class SettingsTab(QWidget):
    def __init__(self, on_data_changed, parent=None):
        super().__init__(parent)
        self.on_data_changed = on_data_changed
        root = QHBoxLayout(self)

        # Projects
        proj_box = QGroupBox("Projekty")
        form_p = QFormLayout()
        self.p_name = QLineEdit(); self.p_code = QLineEdit()
        btn_add_p = QPushButton("Dodaj projekt"); btn_add_p.clicked.connect(self.add_project)
        form_p.addRow("Nazwa:", self.p_name); form_p.addRow("Kod:", self.p_code); form_p.addRow("", btn_add_p)
        self.projects_list = QListWidget()
        btn_del_p = QPushButton("Usuń zaznaczony projekt"); btn_del_p.clicked.connect(self.delete_project)
        v1 = QVBoxLayout(); v1.addLayout(form_p); v1.addWidget(QLabel("Istniejące projekty:")); v1.addWidget(self.projects_list,1); v1.addWidget(btn_del_p)
        proj_box.setLayout(v1)

        # Users
        user_box = QGroupBox("Osoby / zespół")
        form_u = QFormLayout()
        self.u_name = QLineEdit()
        btn_add_u = QPushButton("Dodaj osobę"); btn_add_u.clicked.connect(self.add_user)
        form_u.addRow("Imię i nazwisko:", self.u_name); form_u.addRow("", btn_add_u)
        self.users_list = QListWidget()
        btn_deact = QPushButton("Deaktywuj zaznaczoną osobę"); btn_deact.clicked.connect(self.deactivate_user)
        v2 = QVBoxLayout(); v2.addLayout(form_u); v2.addWidget(QLabel("Aktywni użytkownicy:")); v2.addWidget(self.users_list,1); v2.addWidget(btn_deact)
        user_box.setLayout(v2)

        root.addWidget(proj_box, 1)
        root.addWidget(user_box, 1)
        self.reload_lists()

    def reload_lists(self):
        self.projects_list.clear()
        for p in fetch_all("SELECT * FROM projects ORDER BY created_at DESC"):
            it = QListWidgetItem(f"{p['name']} ({p.get('code') or '-'})")
            it.setData(Qt.UserRole, p["id"])
            self.projects_list.addItem(it)
        self.users_list.clear()
        for u in fetch_all("SELECT * FROM users WHERE is_active=1 ORDER BY name"):
            it = QListWidgetItem(u["name"])
            it.setData(Qt.UserRole, u["id"])
            self.users_list.addItem(it)

    def add_project(self):
        name = self.p_name.text().strip(); code = self.p_code.text().strip() or None
        if not name:
            QMessageBox.warning(self, "Brak nazwy", "Podaj nazwę projektu."); return
        execute("INSERT INTO projects (name, code) VALUES (?,?)", (name, code))
        self.p_name.clear(); self.p_code.clear(); self.reload_lists(); self.on_data_changed()

    def delete_project(self):
        it = self.projects_list.currentItem()
        if not it: return
        pid = it.data(Qt.UserRole)
        if QMessageBox.question(self, "Potwierdź", "Usunąć projekt i jego zadania?") != QMessageBox.Yes: return
        execute("DELETE FROM subtasks WHERE task_id IN (SELECT id FROM tasks WHERE project_id=?)", (pid,))
        execute("DELETE FROM dependencies WHERE task_id IN (SELECT id FROM tasks WHERE project_id=?)", (pid,))
        execute("DELETE FROM tasks WHERE project_id=?", (pid,))
        execute("DELETE FROM projects WHERE id=?", (pid,))
        self.reload_lists(); self.on_data_changed()

    def add_user(self):
        name = self.u_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Brak danych", "Podaj imię i nazwisko."); return
        execute("INSERT INTO users (name, is_active) VALUES (?,1)", (name,))
        self.u_name.clear(); self.reload_lists()

    def deactivate_user(self):
        it = self.users_list.currentItem()
        if not it: return
        uid = it.data(Qt.UserRole)
        execute("UPDATE users SET is_active=0 WHERE id=?", (uid,))
        execute("UPDATE tasks SET assignee_id=NULL WHERE assignee_id=?", (uid,))
        self.reload_lists()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kanban Desktop (Python Pro)")
        self.resize(1280, 820)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.board_tab = BoardTab()
        self.tabs.addTab(self.board_tab, "Tablica Kanban")

        self.timeline_tab = TimelineTab()
        self.tabs.addTab(self.timeline_tab, "Timeline")

        self.settings_tab = SettingsTab(on_data_changed=self.on_data_changed)
        self.tabs.addTab(self.settings_tab, "Ustawienia")

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Plik")
        act_backup = file_menu.addAction("Kopia bazy…"); act_backup.triggered.connect(self.backup_db)
        act_restore = file_menu.addAction("Przywróć bazę…"); act_restore.triggered.connect(self.restore_db)
        file_menu.addSeparator()
        act_quit = file_menu.addAction("Zamknij"); act_quit.triggered.connect(self.close)

        self.statusBar().showMessage(f"Baza: {DB_PATH}")

    def on_data_changed(self):
        # Refresh other tabs
        self.board_tab.projects = fetch_all("SELECT * FROM projects ORDER BY created_at DESC")
        self.board_tab.users = fetch_all("SELECT * FROM users WHERE is_active=1 ORDER BY name")
        self.board_tab.sel_project.clear()
        for p in self.board_tab.projects:
            self.board_tab.sel_project.addItem(p["name"], p["id"])
        if self.board_tab.projects:
            self.board_tab.current_project_id = self.board_tab.projects[0]["id"]
            self.board_tab.sel_project.setCurrentIndex(0)
        self.board_tab.assignee.clear(); self.board_tab.assignee.addItem("—", None)
        for u in self.board_tab.users: self.board_tab.assignee.addItem(u["name"], u["id"])
        self.board_tab.reload_board()
        self.timeline_tab.reload()

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Zapisz kopię bazy", str(Path.home() / "kanban_backup.db"), "SQLite DB (*.db)")
        if not path: return
        try:
            Path(path).write_bytes(Path(DB_PATH).read_bytes())
            QMessageBox.information(self, "OK", f"Zapisano kopię: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def restore_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik bazy", str(Path.home()), "SQLite DB (*.db)")
        if not path: return
        try:
            Path(DB_PATH).write_bytes(Path(path).read_bytes())
            QMessageBox.information(self, "OK", "Przywrócono bazę.")
            self.on_data_changed()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

def main():
    init_db()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
