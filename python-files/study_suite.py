import sys, os, sqlite3, datetime, json, pandas as pd, math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QInputDialog, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import matplotlib.pyplot as plt
from io import BytesIO

DB_NAME = "study_data.db"
TEMPLATE_FILE = "syllabus_template.xlsx"
SETTINGS_FILE = "settings.json"

# ---------------- SETTINGS ----------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {"font_size": 12, "cheer_enabled": True, "streak": 0, "last_login": str(datetime.date.today())}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS syllabus (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 book TEXT,
                 chapter TEXT,
                 topic TEXT,
                 status TEXT DEFAULT 'pending',
                 time_spent INTEGER DEFAULT 0,
                 last_revised TEXT
                 )""")
    c.execute("""CREATE TABLE IF NOT EXISTS daily_plan (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 date TEXT,
                 topic_id INTEGER)""")
    conn.commit()
    conn.close()

# ---------------- TEMPLATE CREATION ----------------
def create_template_if_not_exists():
    if not os.path.exists(TEMPLATE_FILE):
        df = pd.DataFrame([
            ["Polity", "Chapter 1: Constitution", "Historical Background"],
            ["Polity", "Chapter 1: Constitution", "Features of Constitution"],
            ["Economy", "Chapter 2: Growth", "GDP Measurement"]
        ], columns=["Book", "Chapter", "Topic"])
        df.to_excel(TEMPLATE_FILE, index=False)

# ---------------- SYLLABUS QUERIES ----------------
def import_syllabus_from_excel():
    df = pd.read_excel(TEMPLATE_FILE)
    if not {"Book","Chapter","Topic"}.issubset(df.columns):
        raise ValueError("Excel must have Book, Chapter, Topic columns!")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for _, row in df.iterrows():
        c.execute("INSERT INTO syllabus (book,chapter,topic) VALUES (?,?,?)",
                  (row['Book'], row['Chapter'], row['Topic']))
    conn.commit()
    conn.close()

def get_syllabus_hierarchy():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id,book,chapter,topic,status FROM syllabus")
    rows = c.fetchall()
    conn.close()
    hierarchy = {}
    for tid, book, chap, topic, status in rows:
        hierarchy.setdefault(book, {}).setdefault(chap, []).append((tid, topic, status))
    return hierarchy

def get_all_topics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, topic, status, book, chapter, time_spent, last_revised FROM syllabus")
    rows = c.fetchall()
    conn.close()
    return rows

def update_topic_status(topic_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE syllabus SET status=?, last_revised=? WHERE id=?", (status, str(datetime.date.today()), topic_id))
    conn.commit()
    conn.close()

def update_topic_time(topic_id, minutes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE syllabus SET time_spent = time_spent + ? WHERE id=?", (minutes, topic_id))
    conn.commit()
    conn.close()

def update_topic_name(topic_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE syllabus SET topic=? WHERE id=?", (new_name, topic_id))
    conn.commit()
    conn.close()

def delete_topic_by_id(topic_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM syllabus WHERE id=?", (topic_id,))
    conn.commit()
    conn.close()

def delete_by_book(book):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM syllabus WHERE book=?", (book,))
    conn.commit()
    conn.close()

def delete_by_chapter(book, chap):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM syllabus WHERE book=? AND chapter=?", (book,chap))
    conn.commit()
    conn.close()

def get_progress():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) FROM syllabus")
    total, done = c.fetchone()
    conn.close()
    return total or 0, done or 0

# ---------------- DAILY PLAN ----------------
def get_today_plan_details():
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT s.id, s.topic FROM daily_plan d JOIN syllabus s ON d.topic_id=s.id WHERE d.date=?", (today,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- NEWS & AI ----------------
def fetch_news(keywords):
    headlines = []
    for kw in keywords[:3]:
        headlines.append(f"Latest update on {kw}")
    return headlines if headlines else ["No news"]

def get_ai_tips(pending_topics):
    if not pending_topics:
        return "All syllabus done! 🎉"
    return f"Focus today on: {', '.join(pending_topics[:3])}. Break into 25-min sessions!"

# ---------------- DASHBOARD TAB ----------------
class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.today_list = QListWidget()
        layout.addWidget(QLabel("✅ Today’s Tasks"))
        layout.addWidget(self.today_list)

        self.progress_lbl = QLabel()
        layout.addWidget(self.progress_lbl)

        layout.addWidget(QLabel("📰 Latest News"))
        self.news_box = QTextEdit()
        self.news_box.setReadOnly(True)
        layout.addWidget(self.news_box)

        layout.addWidget(QLabel("🤖 AI Tips"))
        self.ai_box = QTextEdit()
        self.ai_box.setReadOnly(True)
        layout.addWidget(self.ai_box)

        btn_refresh = QPushButton("🔄 Refresh Dashboard")
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.today_list.clear()
        today_tasks = get_today_plan_details()
        if not today_tasks:
            fallback = [(t[0], t[1]) for t in get_all_topics() if t[2]!="done"][:3]
            today_tasks = fallback

        for tid, topic in today_tasks:
            item = QListWidgetItem(topic)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, tid)
            self.today_list.addItem(item)
        self.today_list.itemChanged.connect(self.mark_done_from_list)

        total, done = get_progress()
        percent = int((done/total*100) if total else 0)
        self.progress_lbl.setText(f"📊 Progress: {done}/{total} ({percent}%)")
        all_topics = [t[1] for t in get_all_topics()]
        self.news_box.setPlainText("\\n".join(fetch_news(all_topics)))
        pending_topics = [t[1] for t in get_all_topics() if t[2]!=\"done\"]
        self.ai_box.setPlainText(get_ai_tips(pending_topics))

    def mark_done_from_list(self, item):
        if item.checkState() == Qt.Checked:
            tid = item.data(Qt.UserRole)
            update_topic_status(tid, \"done\")
            QMessageBox.information(self, \"✅ Done!\", \"Great job! Keep going!\")
            self.refresh()

# ---------------- SYLLABUS TAB ----------------
class SyllabusTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        btn_import = QPushButton(\"📥 Import Syllabus from Template\")
        btn_import.clicked.connect(self.import_syllabus)
        layout.addWidget(btn_import)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([\"Syllabus\", \"Status\"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        layout.addWidget(self.tree)

        self.setLayout(layout)
        self.refresh_tree()

    def import_syllabus(self):
        try:
            import_syllabus_from_excel()
            QMessageBox.information(self, \"Imported\", \"Syllabus imported from template!\")
            self.refresh_tree()
        except Exception as e:
            QMessageBox.warning(self, \"Error\", str(e))

    def refresh_tree(self):
        self.tree.clear()
        hierarchy = get_syllabus_hierarchy()
        for book, chapters in hierarchy.items():
            book_item = QTreeWidgetItem([f\"📖 {book}\"])
            self.tree.addTopLevelItem(book_item)
            for chap, topics in chapters.items():
                chap_item = QTreeWidgetItem([f\"📄 {chap}\"])
                book_item.addChild(chap_item)
                for tid, topic, status in topics:
                    topic_item = QTreeWidgetItem([f\"{tid}|{topic}\", status])
                    chap_item.addChild(topic_item)
        self.tree.expandAll()

    def open_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        text = item.text(0)
        menu = QMenu()

        if \"|\" in text:
            tid = int(text.split(\"|\")[0])
            menu.addAction(\"✅ Mark Done\", lambda: self.mark_done(tid))
            menu.addAction(\"⏳ Mark Pending\", lambda: self.mark_pending(tid))
            menu.addAction(\"✏ Edit\", lambda: self.edit_topic(tid))
            menu.addAction(\"🗑 Delete\", lambda: self.delete_topic(tid))
        elif text.startswith(\"📄\"):
            chap = text.replace(\"📄 \",\"\")
            parent_book = item.parent().text(0).replace(\"📖 \",\"\")
            menu.addAction(\"🗑 Delete Chapter\", lambda: self.delete_chapter(parent_book, chap))
        elif text.startswith(\"📖\"):
            book = text.replace(\"📖 \",\"\")
            menu.addAction(\"🗑 Delete Book\", lambda: self.delete_book(book))

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def mark_done(self, tid):
        update_topic_status(tid, \"done\")
        self.refresh_tree()

    def mark_pending(self, tid):
        update_topic_status(tid, \"pending\")
        self.refresh_tree()

    def edit_topic(self, tid):
        new_name, ok = QInputDialog.getText(self, \"Edit Topic\", \"Enter new topic name:\")
        if ok and new_name.strip():
            update_topic_name(tid, new_name.strip())
            self.refresh_tree()

    def delete_topic(self, tid):
        delete_topic_by_id(tid)
        self.refresh_tree()

    def delete_book(self, book):
        delete_by_book(book)
        self.refresh_tree()

    def delete_chapter(self, book, chap):
        delete_by_chapter(book, chap)
        self.refresh_tree()

# ---------------- FOCUS MODE TAB ----------------
class FocusModeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_task = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0

        layout = QVBoxLayout()
        self.task_label = QLabel(\"🎯 Focus Mode - Next Task\")
        layout.addWidget(self.task_label)

        self.time_label = QLabel(\"⏱ Time: 00:00\")
        layout.addWidget(self.time_label)

        self.start_btn = QPushButton(\"▶ Start\")
        self.start_btn.clicked.connect(self.start_focus)
        layout.addWidget(self.start_btn)

        self.done_btn = QPushButton(\"✅ Done\")
        self.done_btn.clicked.connect(self.mark_done_and_next)
        layout.addWidget(self.done_btn)

        self.next_btn = QPushButton(\"⏭ Skip\")
        self.next_btn.clicked.connect(self.load_next_task)
        layout.addWidget(self.next_btn)

        self.setLayout(layout)
        self.load_next_task()

    def load_next_task(self):
        pending = [t for t in get_all_topics() if t[2] != 'done']
        if not pending:
            self.task_label.setText(\"🎉 All tasks done!\")
            self.start_btn.setEnabled(False)
            self.done_btn.setEnabled(False)
            return
        self.current_task = pending[0]
        self.task_label.setText(f\"🎯 {self.current_task[1]} ({self.current_task[3]} → {self.current_task[4]})\")
        self.elapsed_seconds = 0
        self.update_timer_label()

    def start_focus(self):
        self.timer.start(1000)

    def update_timer(self):
        self.elapsed_seconds += 1
        self.update_timer_label()

    def update_timer_label(self):
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        self.time_label.setText(f\"⏱ Time: {mins:02}:{secs:02}\")

    def mark_done_and_next(self):
        if not self.current_task: return
        self.timer.stop()
        minutes = max(1, self.elapsed_seconds // 60)
        update_topic_time(self.current_task[0], minutes)
        update_topic_status(self.current_task[0], 'done')
        QMessageBox.information(self, \"✅ Completed!\", f\"{self.current_task[1]} done! Time: {minutes} min\")
        self.load_next_task()

# ---------------- REVISION TRACKER TAB ----------------
class RevisionTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.list = QListWidget()
        layout.addWidget(QLabel(\"🔄 Topics Needing Revision Today\"))
        layout.addWidget(self.list)

        btn_refresh = QPushButton(\"🔄 Refresh Revision List\")
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.list.clear()
        today = datetime.date.today()
        for tid, topic, status, book, chap, time_spent, last_rev in get_all_topics():
            if status == 'done' and last_rev:
                last_date = datetime.datetime.strptime(last_rev, \"%Y-%m-%d\").date()
                days_since = (today - last_date).days
                if days_since in [1, 7, 21]:
                    self.list.addItem(f\"{topic} ({book}/{chap}) → revise after {days_since} days\")

# ---------------- MOTIVATION TAB ----------------
def get_motivational_quote():
    quotes = [
        \"Success is the sum of small efforts, repeated day in and day out.\",
        \"Don’t watch the clock; do what it does. Keep going!\",
        \"Dream big. Work hard. Stay focused.\",
        \"Your future is created by what you do today, not tomorrow.\"
    ]
    return quotes[datetime.datetime.now().second % len(quotes)]

class MotivationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.quote_lbl = QLabel(get_motivational_quote())
        layout.addWidget(QLabel(\"💡 Daily Motivation\"))
        layout.addWidget(self.quote_lbl)

        self.streak_lbl = QLabel()
        layout.addWidget(QLabel(\"🔥 Study Streak\"))
        layout.addWidget(self.streak_lbl)

        btn_refresh = QPushButton(\"🔄 Refresh Motivation\")
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.quote_lbl.setText(get_motivational_quote())
        today = str(datetime.date.today())
        if settings.get(\"last_login\") != today:
            settings[\"streak\"] += 1
            settings[\"last_login\"] = today
            save_settings(settings)
        self.streak_lbl.setText(f\"🔥 {settings['streak']} day streak\")

# ---------------- ANALYTICS TAB ----------------
class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(\"📊 Progress Analytics\"))

        self.chart_label = QLabel()
        layout.addWidget(self.chart_label)

        btn_refresh = QPushButton(\"🔄 Refresh Analytics\")
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        total, done = get_progress()
        pending = total - done
        if total == 0:
            self.chart_label.setText(\"No syllabus yet\")
            return

        fig, ax = plt.subplots(figsize=(3, 3))
        ax.pie([done, pending], labels=[\"Done\", \"Pending\"], autopct=\"%1.1f%%\", colors=[\"green\", \"red\"])
        ax.set_title(\"Completion Progress\")

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        self.chart_label.setPixmap(pixmap)
        plt.close(fig)

# ---------------- MAIN APP WINDOW ----------------
class StudyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(\"UPSC + IIT Super Study Suite\")
        self.resize(900, 700)
        font = QFont()
        font.setPointSize(settings.get(\"font_size\", 12))
        self.setFont(font)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.dashboard_tab = DashboardTab()
        self.syllabus_tab = SyllabusTab()
        self.focus_tab = FocusModeTab()
        self.revision_tab = RevisionTab()
        self.analytics_tab = AnalyticsTab()
        self.motivation_tab = MotivationTab()

        self.tabs.addTab(self.dashboard_tab, \"🏠 Dashboard\")
        self.tabs.addTab(self.syllabus_tab, \"📚 Syllabus\")
        self.tabs.addTab(self.focus_tab, \"🎯 Focus Mode\")
        self.tabs.addTab(self.revision_tab, \"🔄 Revision\")
        self.tabs.addTab(self.analytics_tab, \"📊 Analytics\")
        self.tabs.addTab(self.motivation_tab, \"💡 Motivation\")

        self.settings_btn = QPushButton(\"⚙ Settings\")
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)

        self.setLayout(layout)

    def open_settings(self):
        font_size, ok = QInputDialog.getInt(self, \"Font Size\", \"Enter font size:\", value=settings.get(\"font_size\", 12), min=8, max=30)
        if ok:
            settings[\"font_size\"] = font_size
            save_settings(settings)
            QMessageBox.information(self, \"Saved\", \"Font size updated! Restart app to apply.\")

# ---------------- MAIN EXEC ----------------
if __name__ == \"__main__\":
    init_db()
    create_template_if_not_exists()

    app = QApplication(sys.argv)
    main_win = StudyApp()
    main_win.show()
    sys.exit(app.exec_())
