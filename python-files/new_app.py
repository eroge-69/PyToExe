import sys, os, sqlite3, datetime, json, requests, pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QCalendarWidget, QSpinBox, QMenu,
    QInputDialog, QListWidget, QListWidgetItem, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QTimer

DB_NAME = "study_data.db"
TEMPLATE_FILE = "syllabus_template.xlsx"
SETTINGS_FILE = "settings.json"

# ---------------- SETTINGS ----------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {"font_size": 12, "cheer_enabled": True, "streak": 0, "last_login": ""}

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
                 status TEXT DEFAULT 'pending')""")

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
    c.execute("SELECT id, topic, status, book, chapter FROM syllabus")
    rows = c.fetchall()
    conn.close()
    return rows

def update_topic_status(topic_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE syllabus SET status=? WHERE id=?", (status, topic_id))
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
def clear_daily_plan():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM daily_plan")
    conn.commit()
    conn.close()

def auto_plan(start_date, days):
    topics = [t[0] for t in get_all_topics() if t[2] != 'done']
    if not topics: return

    per_day = max(1, len(topics)//days)
    d = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    clear_daily_plan()

    idx=0
    for day in range(days):
        day_str = (d + datetime.timedelta(days=day)).strftime("%Y-%m-%d")
        for _ in range(per_day):
            if idx>=len(topics): break
            c.execute("INSERT INTO daily_plan(date,topic_id) VALUES (?,?)", (day_str, topics[idx]))
            idx+=1
    conn.commit()
    conn.close()

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

# ---------------- Cheer Detection ----------------
def check_chapter_book_completion():
    data = get_all_topics()
    books = {}
    chapters = {}
    for tid, topic, status, book, chap in data:
        books.setdefault(book, []).append(status)
        chapters.setdefault((book,chap), []).append(status)

    completed_books = [b for b, sts in books.items() if all(s=="done" for s in sts)]
    completed_chaps = [(b,c) for (b,c),sts in chapters.items() if all(s=="done" for s in sts)]
    return completed_books, completed_chaps

# ---------------- UI TABS ----------------
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
        self.news_box.setPlainText("\n".join(fetch_news(all_topics)))
        pending_topics = [t[1] for t in get_all_topics() if t[2]!="done"]
        self.ai_box.setPlainText(get_ai_tips(pending_topics))

    def mark_done_from_list(self, item):
        if item.checkState() == Qt.Checked:
            tid = item.data(Qt.UserRole)
            update_topic_status(tid, "done")
            self.celebrate_if_needed()
            self.refresh()

    def celebrate_if_needed(self):
        completed_books, completed_chaps = check_chapter_book_completion()
        if completed_chaps:
            b,c = completed_chaps[-1]
            if settings.get("cheer_enabled",True):
                QMessageBox.information(self, "🎉 Chapter Completed!", f"You completed {c} in {b}! Keep going!")
        if completed_books:
            b = completed_books[-1]
            if settings.get("cheer_enabled",True):
                QMessageBox.information(self, "🏆 Book Completed!", f"Amazing! You finished all chapters of {b}!")

class SyllabusTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        btn_import = QPushButton("📥 Import Syllabus from Template")
        btn_import.clicked.connect(self.import_syllabus)
        layout.addWidget(btn_import)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Syllabus", "Status"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        layout.addWidget(self.tree)

        self.setLayout(layout)
        self.refresh_tree()

    def import_syllabus(self):
        try:
            import_syllabus_from_excel()
            QMessageBox.information(self, "Imported", "Syllabus imported from template!")
            self.refresh_tree()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def refresh_tree(self):
        self.tree.clear()
        hierarchy = get_syllabus_hierarchy()
        for book, chapters in hierarchy.items():
            book_item = QTreeWidgetItem([f"📖 {book}"])
            self.tree.addTopLevelItem(book_item)
            for chap, topics in chapters.items():
                chap_item = QTreeWidgetItem([f"📄 {chap}"])
                book_item.addChild(chap_item)
                for tid, topic, status in topics:
                    topic_item = QTreeWidgetItem([f"{tid}|{topic}", status])
                    chap_item.addChild(topic_item)
        self.tree.expandAll()

    def open_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        text = item.text(0)
        menu = QMenu()

        if "|" in text:  # topic
            tid = int(text.split("|")[0])
            menu.addAction("✅ Mark Done", lambda: self.mark_done(tid))
            menu.addAction("⏳ Mark Pending", lambda: self.mark_pending(tid))
            menu.addAction("✏ Edit", lambda: self.edit_topic(tid))
            menu.addAction("🗑 Delete", lambda: self.delete_topic(tid))
        elif text.startswith("📄"):
            chap = text.replace("📄 ","")
            parent_book = item.parent().text(0).replace("📖 ","")
            menu.addAction("🗑 Delete Chapter", lambda: self.delete_chapter(parent_book, chap))
        elif text.startswith("📖"):
            book = text.replace("📖 ","")
            menu.addAction("🗑 Delete Book", lambda: self.delete_book(book))

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def mark_done(self, tid):
        update_topic_status(tid, "done")
        self.refresh_tree()

    def mark_pending(self, tid):
        update_topic_status(tid, "pending")
        self.refresh_tree()

    def edit_topic(self, tid):
        new_name, ok = QInputDialog.getText(self, "Edit Topic", "Enter new topic name:")
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

class PlannerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        layout.addWidget(QLabel("Days to finish syllabus:"))
        self.days_spin = QSpinBox()
        self.days_spin.setMinimum(1)
        self.days_spin.setValue(10)
        layout.addWidget(self.days_spin)
        btn_auto = QPushButton("⚡ Auto Plan from Selected Date")
        btn_auto.clicked.connect(self.auto_plan)
        layout.addWidget(btn_auto)
        self.setLayout(layout)

    def auto_plan(self):
        start_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        days = self.days_spin.value()
        auto_plan(start_date, days)
        QMessageBox.information(self, "Planned", f"Auto planned syllabus in {days} days!")

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Font Size:"))
        self.font_box = QComboBox()
        self.font_box.addItems(["10","12","14","16","18"])
        self.font_box.setCurrentText(str(settings.get("font_size",12)))
        layout.addWidget(self.font_box)

        self.cheer_box = QCheckBox("Enable Cheer Popups")
        self.cheer_box.setChecked(settings.get("cheer_enabled",True))
        layout.addWidget(self.cheer_box)

        btn_save = QPushButton("💾 Save Settings")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def save(self):
        settings["font_size"] = int(self.font_box.currentText())
        settings["cheer_enabled"] = self.cheer_box.isChecked()
        save_settings(settings)
        QMessageBox.information(self, "Saved", "Settings updated! Restart app to apply font.")

# ---------------- NEW TABS ----------------
class FocusModeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_task = None
        self.elapsed_seconds = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        layout = QVBoxLayout()
        self.task_label = QLabel("🎯 Focus Mode - Next Pending Topic")
        layout.addWidget(self.task_label)

        self.time_label = QLabel("⏱ Time: 00:00")
        layout.addWidget(self.time_label)

        self.start_btn = QPushButton("▶ Start Focus")
        self.start_btn.clicked.connect(self.start_focus)
        layout.addWidget(self.start_btn)

        self.done_btn = QPushButton("✅ Done & Next")
        self.done_btn.clicked.connect(self.complete_and_next)
        layout.addWidget(self.done_btn)

        self.skip_btn = QPushButton("⏭ Skip Task")
        self.skip_btn.clicked.connect(self.load_next_task)
        layout.addWidget(self.skip_btn)

        self.setLayout(layout)
        self.load_next_task()

    def load_next_task(self):
        pending = [t for t in get_all_topics() if t[2] != 'done']
        if not pending:
            self.task_label.setText("🎉 All tasks completed!")
            self.start_btn.setEnabled(False)
            self.done_btn.setEnabled(False)
            self.skip_btn.setEnabled(False)
            return
        self.current_task = pending[0]
        self.task_label.setText(f"🎯 {self.current_task[1]} ({self.current_task[3]} → {self.current_task[4]})")
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
        self.time_label.setText(f"⏱ Time: {mins:02}:{secs:02}")

    def complete_and_next(self):
        if not self.current_task:
            return
        self.timer.stop()
        update_topic_status(self.current_task[0], "done")
        QMessageBox.information(self, "✅ Completed!", f"{self.current_task[1]} completed!")
        self.load_next_task()

class RevisionTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.rev_list = QListWidget()
        layout.addWidget(QLabel("🔄 Topics Needing Revision Today"))
        layout.addWidget(self.rev_list)

        btn_refresh = QPushButton("🔄 Refresh Revision List")
        btn_refresh.clicked.connect(self.refresh_list)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.rev_list.clear()
        today = datetime.date.today()
        for tid, topic, status, book, chap in get_all_topics():
            if status == 'done':
                # simulate revision schedule
                days_since = (today - datetime.date.today()).days  # placeholder
                if days_since in [1, 7, 21]:
                    self.rev_list.addItem(f"{topic} ({book}/{chap}) needs revision")

def get_motivational_quote():
    quotes = [
        "Success is the sum of small efforts, repeated daily.",
        "Don’t watch the clock; do what it does. Keep going!",
        "Dream big. Work hard. Stay focused.",
        "Your future is created by what you do today!"
    ]
    return quotes[datetime.datetime.now().second % len(quotes)]

class MotivationAnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        # Motivation
        self.quote_lbl = QLabel(get_motivational_quote())
        layout.addWidget(QLabel("💡 Daily Motivation"))
        layout.addWidget(self.quote_lbl)

        # Progress
        self.progress_lbl = QLabel()
        layout.addWidget(QLabel("📊 Progress Overview"))
        layout.addWidget(self.progress_lbl)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.quote_lbl.setText(get_motivational_quote())
        total, done = get_progress()
        percent = int((done/total*100) if total else 0)
        self.progress_lbl.setText(f"Progress: {done}/{total} ({percent}%)")

# ---------------- MAIN APP ----------------
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📚 Departmental Exam Study Planner")

        tabs = QTabWidget()
        tabs.addTab(DashboardTab(), "🏠 Dashboard")
        tabs.addTab(SyllabusTab(), "📖 Syllabus")
        tabs.addTab(PlannerTab(), "📅 Planner")
        tabs.addTab(FocusModeTab(), "🎯 Focus Mode")
        tabs.addTab(RevisionTab(), "🔄 Revision")
        tabs.addTab(MotivationAnalyticsTab(), "📊 Motivation & Analytics")
        tabs.addTab(SettingsTab(), "⚙ Settings")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    create_template_if_not_exists()
    init_db()
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
