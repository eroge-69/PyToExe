# capcut_subtitle_gui.py
# Requires: PyQt5
# Run: python capcut_subtitle_gui.py

import sys, os, json, threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QFileDialog, QTextEdit, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt

ROOT_SCAN = ["D:\\", os.path.join(os.getenv("LOCALAPPDATA") or "", "")]

def find_capcut_roots(roots, max_dirs=5000):
    found = []
    seen = 0
    for root in roots:
        if not root: 
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            seen += 1
            if seen > max_dirs: break
            name = os.path.basename(dirpath)
            if name.lower() == "capcut drafts":
                found.append(dirpath)
            # small optimization: prune obvious long branches
            if os.path.basename(dirpath).lower() in ("windows","program files","program files (x86)"):
                dirnames[:] = []
        # don't flood
    return sorted(set(found))

def find_projects_in_root(root_path):
    try:
        items = [os.path.join(root_path, d) for d in os.listdir(root_path)
                 if os.path.isdir(os.path.join(root_path, d))]
        return sorted(items)
    except Exception:
        return []

def find_draft_json(start_folder):
    for dirpath, dirnames, filenames in os.walk(start_folder):
        if "draft_content.json" in filenames:
            return os.path.join(dirpath, "draft_content.json")
    return None

def format_ts(ms):
    # ms -> "HH:MM:SS,mmm"
    try:
        ms = int(ms)
    except:
        ms = 0
    h = ms // 3600000
    ms -= h * 3600000
    m = ms // 60000
    ms -= m * 60000
    s = ms // 1000
    ms -= s * 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def extract_sentences_from_json(data):
    results = []
    # primary path: extra_info.subtitle_fragment_info_list
    candidates = []
    if isinstance(data, dict):
        if "extra_info" in data and isinstance(data["extra_info"], dict):
            candidates = data["extra_info"].get("subtitle_fragment_info_list", []) or []
        # recursive find: collect any 'subtitle_cache_info' strings
        def recurse(obj):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    if k == "subtitle_cache_info" and isinstance(v, str) and v.strip():
                        candidates.append({"subtitle_cache_info": v})
                    else:
                        recurse(v)
            elif isinstance(obj, list):
                for item in obj:
                    recurse(item)
        recurse(data)
    # parse candidates
    for frag in candidates:
        sci = frag.get("subtitle_cache_info")
        if not sci: continue
        try:
            parsed = json.loads(sci)
            sent_list = parsed.get("sentence_list") or parsed.get("sentence_list", [])
            for s in sent_list:
                text = s.get("text") or ""
                st = s.get("start_time") or s.get("start") or 0
                et = s.get("end_time") or s.get("end") or st + 1000
                # sometimes times are in seconds*1000 already; assume ms.
                results.append((int(st), int(et), text.strip()))
        except Exception:
            # ignore malformed
            continue
    # sort by start_time
    results = sorted(results, key=lambda x: x[0])
    # dedupe empty text
    filtered = [r for r in results if r[2]]
    return filtered

def to_srt(entries):
    lines = []
    idx = 1
    for st, et, text in entries:
        lines.append(str(idx))
        lines.append(f"{format_ts(st)} --> {format_ts(et)}")
        lines.append(text)
        lines.append("")  # blank line
        idx += 1
    return "\n".join(lines)

def to_vtt(entries):
    lines = ["WEBVTT\n"]
    for st, et, text in entries:
        lines.append(f"{format_ts(st).replace(',', '.')} --> {format_ts(et).replace(',', '.')}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CapCut Drafts → Subtitle (Pro-ish)")
        self.resize(1000,600)
        self.rootList = QListWidget()
        self.projectList = QListWidget()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.scanBtn = QPushButton("Scan D: + LOCALAPPDATA")
        self.browseBtn = QPushButton("Browse folder")
        self.exportSrtBtn = QPushButton("Export .srt")
        self.exportVttBtn = QPushButton("Export .vtt")
        self.statusLabel = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0,100)
        self.progress.setValue(0)

        left = QVBoxLayout()
        left.addWidget(QLabel("Found 'CapCut Drafts' roots"))
        left.addWidget(self.rootList)
        left.addWidget(self.scanBtn)
        left.addWidget(self.browseBtn)

        mid = QVBoxLayout()
        mid.addWidget(QLabel("Projects (subfolders)"))
        mid.addWidget(self.projectList)
        mid.addWidget(self.exportSrtBtn)
        mid.addWidget(self.exportVttBtn)
        mid.addWidget(self.statusLabel)
        mid.addWidget(self.progress)

        right = QVBoxLayout()
        right.addWidget(QLabel("Subtitle preview"))
        right.addWidget(self.preview)

        main = QHBoxLayout()
        main.addLayout(left,2)
        main.addLayout(mid,2)
        main.addLayout(right,4)

        central = QWidget()
        central.setLayout(main)
        self.setCentralWidget(central)

        # signals
        self.scanBtn.clicked.connect(self.scan_roots_thread)
        self.browseBtn.clicked.connect(self.browse_folder)
        self.rootList.itemClicked.connect(self.on_root_selected)
        self.projectList.itemClicked.connect(self.on_project_selected)
        self.exportSrtBtn.clicked.connect(lambda: self.export_selected("srt"))
        self.exportVttBtn.clicked.connect(lambda: self.export_selected("vtt"))

        # quick initial scan
        self.scan_roots_thread()

    def scan_roots_thread(self):
        self.statusLabel.setText("Scanning...")
        self.progress.setValue(5)
        threading.Thread(target=self._scan_roots, daemon=True).start()

    def _scan_roots(self):
        roots = find_capcut_roots(ROOT_SCAN)
        self.rootList.clear()
        for r in roots:
            self.rootList.addItem(r)
        self.progress.setValue(100)
        self.statusLabel.setText(f"Found {len(roots)} root(s)")

    def browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select CapCut Drafts folder")
        if d:
            self.rootList.addItem(d)
            self.statusLabel.setText("Added manual folder")

    def on_root_selected(self, item):
        root = item.text()
        self.projectList.clear()
        projects = find_projects_in_root(root)
        for p in projects:
            self.projectList.addItem(p)
        self.statusLabel.setText(f"{len(projects)} projects")

    def on_project_selected(self, item):
        folder = item.text()
        self.statusLabel.setText("Searching draft_content.json...")
        self.progress.setValue(10)
        threading.Thread(target=self._load_project, args=(folder,), daemon=True).start()

    def _load_project(self, folder):
        path = find_draft_json(folder)
        if not path:
            self.statusLabel.setText("draft_content.json not found in project")
            self.preview.setPlainText("")
            self.progress.setValue(0)
            return
        self.statusLabel.setText(f"Found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.preview.setPlainText(f"Failed read JSON: {e}")
            return
        entries = extract_sentences_from_json(data)
        if not entries:
            self.preview.setPlainText("No subtitle entries found.")
            return
        srt = to_srt(entries)
        # preview first 3000 chars
        self.preview.setPlainText(srt[:4000])
        self.current_entries = entries
        self.current_draft_path = path
        self.progress.setValue(100)
        self.statusLabel.setText(f"Loaded {len(entries)} subtitle lines")

    def export_selected(self, kind):
        if not hasattr(self, "current_entries") or not self.current_entries:
            self.statusLabel.setText("No subtitles to export")
            return
        fn, _ = QFileDialog.getSaveFileName(self, "Save file", f"subtitles.{kind}", f"*.{kind}")
        if not fn:
            return
        try:
            content = to_srt(self.current_entries) if kind=="srt" else to_vtt(self.current_entries)
            with open(fn, "w", encoding="utf-8") as f:
                f.write(content)
            self.statusLabel.setText(f"Saved: {fn}")
        except Exception as e:
            self.statusLabel.setText(f"Failed to save: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
