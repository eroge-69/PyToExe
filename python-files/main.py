import sys, os, csv, pyautogui, datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint

# --- CONFIG ---
ROWS = 6
COLS = 4
SLOT_W, SLOT_H = 16.25, 16.25
SCAN_INTERVAL_MS = 200
CSV_FILE = "patterns_next.csv"
LOG_FILE = "pattern_log.csv"

# --- Ensure log file exists ---
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Row", "Pattern", "Predict", "Real", "Result"])

# ------------------------ DATA ------------------------
def load_patterns():
    patterns = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["Pattern"], row["Next"])
                patterns[key] = {"correct": int(row["ถูก"]), "wrong": int(row["ผิด"])}
    return patterns

def save_patterns(patterns):
    with open(CSV_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Pattern", "Next", "ถูก", "ผิด"])
        for (p, n), stat in patterns.items():
            writer.writerow([p, n, stat["correct"], stat["wrong"]])

def log_result(row, pattern, predict, real):
    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), row, pattern, predict, real, "✔" if predict == real else "✘"])

# ------------------------ TOP PATTERN WINDOW ------------------------
class TopPatternWindow(QWidget):
    def __init__(self, patterns):
        super().__init__()
        self.setGeometry(1100, 300, 400, 300)
        self.setWindowTitle("Top Patterns")
        self.setStyleSheet("background-color: #222; color: white;")
        self.setFont(QFont("Consolas", 10))
        self.text = QTextEdit(self)
        self.text.setGeometry(10, 10, 380, 280)
        self.text.setReadOnly(True)
        self.update_top(patterns)

    def update_top(self, patterns):
        result_lines = []
        for (pattern, next_res), stat in patterns.items():
            total = stat["correct"] + stat["wrong"]
            if total >= 10:
                winrate = stat["correct"] / total
                if winrate >= 0.80:
                    result_lines.append((winrate, total, pattern, next_res))

        result_lines.sort(reverse=True)
        if not result_lines:
            self.text.setText("ยังไม่พบสูตรที่มีความแม่น ≥ 80% และจำนวนครั้ง ≥ 10")
        else:
            lines = [f"{i+1}. {p} → {n} ({int(w*100)}% | {t} ครั้ง)" for i, (w, t, p, n) in enumerate(result_lines[:10])]
            self.text.setText("\n".join(lines))

# ------------------------ RESULT WINDOW ------------------------
class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 300, 400, 250)
        self.setWindowTitle("ผลลัพธ์ Pattern")
        self.setStyleSheet("background-color: #111; color: white;")
        self.setFont(QFont("Consolas", 10))
        self.patterns = load_patterns()
        self.pattern_list = [""] * ROWS
        self.labels = []
        self.last_predict = ["-"] * ROWS
        self.error_counts = [0] * ROWS

        for i in range(ROWS):
            label = QLabel("-", self)
            label.setGeometry(10, i * 30, 270, 30)
            self.labels.append(label)

            btn_ok = QPushButton("✔", self)
            btn_no = QPushButton("✘", self)
            btn_ok.setGeometry(280, i * 30 + 5, 30, 20)
            btn_no.setGeometry(315, i * 30 + 5, 30, 20)
            btn_ok.clicked.connect(lambda checked, r=i: self.mark(r, True))
            btn_no.clicked.connect(lambda checked, r=i: self.mark(r, False))

        self.top_btn = QPushButton("ดูสูตรแม่นสุด", self)
        self.top_btn.setGeometry(10, 190, 150, 25)
        self.top_btn.clicked.connect(self.open_top)

    def update_row(self, row_idx, pattern):
        if len(pattern) != 4 or "T" in pattern or "-" in pattern:
            return
        self.pattern_list[row_idx] = pattern
        next_counts = {}
        for (p, n), stat in self.patterns.items():
            if p == pattern:
                total = stat["correct"] + stat["wrong"]
                if total > 0:
                    winrate = stat["correct"] / total
                    next_counts[n] = (winrate, total)

        if not next_counts:
            self.labels[row_idx].setText(f"แถว {row_idx+1}: {pattern} | ยังไม่มีข้อมูล")
            self.last_predict[row_idx] = "-"
        else:
            best = max(next_counts.items(), key=lambda x: x[1][0])
            predict = best[0]
            self.labels[row_idx].setText(f"แถว {row_idx+1}: {pattern} → {predict} ({int(best[1][0]*100)}%)")
            self.last_predict[row_idx] = predict
            # ปิดปุ่ม ✔ ✘ โดยอัตโนมัติเมื่อจับสีแล้ว
            self.mark(row_idx, True)

    def mark(self, row_idx, is_correct):
        pattern = self.pattern_list[row_idx]
        predict = self.last_predict[row_idx]
        if not pattern or predict == "-": return

        key = (pattern, predict)
        stat = self.patterns.get(key, {"correct": 0, "wrong": 0})
        if is_correct:
            stat["correct"] += 1
            self.error_counts[row_idx] = 0
        else:
            stat["wrong"] += 1
            self.error_counts[row_idx] += 1
        self.patterns[key] = stat
        save_patterns(self.patterns)
        log_result(row_idx + 1, pattern, predict, "✔" if is_correct else "✘", predict)
        self.update_row(row_idx, pattern)

        if self.error_counts[row_idx] >= 3:
            self.labels[row_idx].setText(f"แถว {row_idx+1}: {pattern} ❌ พักสูตรนี้")

    def open_top(self):
        self.top_window = TopPatternWindow(self.patterns)
        self.top_window.show()

# ------------------------ SCAN WINDOW ------------------------
class ScanWindow(QWidget):
    def __init__(self, result_window):
        super().__init__()
        self.resize(int(COLS * SLOT_W) + 150, int(ROWS * SLOT_H) + 40)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.OpenHandCursor)
        self.old_pos = self.pos()
        self.results = [["-"] * COLS for _ in range(ROWS)]
        self.result_window = result_window

        self.start_btn = QPushButton("เริ่มจับสี", self)
        self.start_btn.setGeometry(int(COLS * SLOT_W) + 10, 10, 120, 30)
        self.start_btn.clicked.connect(self.start_scanning)

        self.timer = QTimer()
        self.timer.timeout.connect(self.scan)

    def start_scanning(self):
        self.timer.start(SCAN_INTERVAL_MS)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.old_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            delta = e.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = e.globalPos()

    def scan(self):
        for r in range(ROWS):
            row_result = []
            for c in range(COLS):
                gx = self.mapToGlobal(QPoint(int(c * SLOT_W + SLOT_W / 2), int(r * SLOT_H + SLOT_H / 2))).x()
                gy = self.mapToGlobal(QPoint(int(c * SLOT_W + SLOT_W / 2), int(r * SLOT_H + SLOT_H / 2))).y()
                r_, g_, b_ = pyautogui.screenshot().getpixel((gx, gy))
                if b_ - r_ > 30 and b_ > 100:
                    row_result.append("P")
                elif r_ - b_ > 30 and r_ > 100:
                    row_result.append("B")
                elif abs(r_ - g_) < 20 and abs(b_ - g_) < 20 and r_ > 150:
                    row_result.append("T")
                else:
                    row_result.append("-")
            self.results[r] = row_result
            pattern = "".join(row_result)
            if "T" not in pattern and "-" not in pattern:
                self.result_window.update_row(r, pattern)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setPen(QPen(Qt.black, 1))
        for r in range(ROWS):
            for c in range(COLS):
                x, y = int(c * SLOT_W), int(r * SLOT_H)
                p.setBrush(Qt.NoBrush)
                p.drawRect(x, y, int(SLOT_W), int(SLOT_H))
                p.setBrush(Qt.black)
                p.drawEllipse(x + int(SLOT_W / 2) - 2, y + int(SLOT_H / 2) - 2, 4, 4)

# ------------------------ MAIN ------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    result = ResultWindow()
    scan = ScanWindow(result)
    scan.show()
    result.show()
    sys.exit(app.exec_())
