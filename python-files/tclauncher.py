# TC_Launcher_Rebuild.pyw
# TC Launcher — Ultimate rebuild (splash, cache, settings, notepad, python runner, app launcher, music, etc.)
# Save as TC_Launcher_Rebuild.pyw and double-click to run
# Note: Requires PyQt6. Music uses pygame if available, otherwise system default playback.

import sys, os, json, time, subprocess, threading, io
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget, QScrollArea,
    QTextEdit, QFileDialog, QLineEdit, QProgressBar, QColorDialog, QSlider,
    QMessageBox, QInputDialog, QFrame
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QSize

# ---------- Constants & Cache ----------
CACHE_PATH = Path(__file__).with_name("tc_cache.json")
DEFAULT_CACHE = {
    "recent_files": [],
    "recent_apps": [],
    "app_favorites": [],
    "ai_history": [],
    "python_snippets": [],
    "music_playlist": [],
    "settings": {
        "bg_color": "#1f1f1f",
        "btn_color": "#2F9E44",
        "btn_text": "#ffffff",
        "top_bar": "#114b5f",
        "corner_radius": 10,
        "opacity": 1.0,
        "fps_counter": False,
        "vsync": True
    }
}

def load_cache():
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # merge defaults
            for k, v in DEFAULT_CACHE.items():
                if k not in data:
                    data[k] = v
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        if kk not in data[k]:
                            data[k][kk] = vv
            return data
        except Exception:
            return DEFAULT_CACHE.copy()
    else:
        return DEFAULT_CACHE.copy()

def save_cache(cache):
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print("Failed saving cache:", e)

cache = load_cache()

# try optional pygame for music
try:
    import pygame
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

# ---------- Utility helpers ----------
def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def make_icon_pixmap(text="TC", size=64, bg="#114b5f", fg="#fff"):
    """Create a simple pixmap icon programmatically."""
    pix = QPixmap(size, size)
    pix.fill(QColor(bg))
    p = QPainter(pix)
    p.setPen(QColor(fg))
    f = QFont("Segoe UI", int(size/2), QFont.Weight.Bold)
    p.setFont(f)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, text)
    p.end()
    return pix

# ---------- Splash Screen (QTimer-based) ----------
class Splash(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(640, 320)
        self.center_on_screen()
        self.setStyleSheet("background-color:#0f0f0f; color:#fff; border-radius:8px;")
        # central
        w = QWidget()
        self.setCentralWidget(w)
        v = QVBoxLayout(w)
        # top bar (simulated)
        self.logo = QLabel("TC LAUNCHER ULTIMATE")
        self.logo.setFont(QFont("Segoe UI", 20))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.logo)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        v.addWidget(self.progress)
        self.msg = QLabel("Preparing...")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.msg)
        self.show()
        self.messages = [
            "Checking cache...",
            "Loading UI modules...",
            "Initializing editors...",
            "Preparing Python runtime...",
            "Setting up music player...",
            "Applying settings...",
            "Finalizing..."
        ]
        self.idx = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(700)  # 0.7s per message
        self.fake_progress = 0

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.setGeometry(x, y, self.width(), self.height())

    def step(self):
        if self.idx < len(self.messages):
            self.msg.setText(self.messages[self.idx])
            self.fake_progress += int(80/len(self.messages))
            self.progress.setValue(min(95, self.fake_progress))
            self.idx += 1
        else:
            self.timer.stop()
            self.progress.setValue(100)
            QTimer.singleShot(450, self.finish)

    def finish(self):
        self.close()
        # open main window on the GUI thread
        self.main = TCHub()
        self.main.show()

# ---------- Main Launcher Window ----------
class TCHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TC Launcher Ultimate")
        # set programmatically generated icon
        icon_pix = make_icon_pixmap("TC", 128, bg=cache['settings']['settings']['top_bar'] if 'settings' in cache and 'top_bar' in cache['settings'] else cache['settings']['top_bar'])
        self.setWindowIcon(QIcon(icon_pix))
        # window geometry
        self.resize(1400, 820)
        # main container and layout
        root = QWidget()
        self.setCentralWidget(root)
        main_h = QHBoxLayout(root)
        main_h.setContentsMargins(0,0,0,0)
        main_v = QVBoxLayout()
        # Top bar (custom border color)
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(36)
        top_color = cache['settings']['top_bar'] if 'top_bar' in cache['settings'] else "#114b5f"
        self.top_bar.setStyleSheet(f"background-color: {top_color};")
        top_layout = QHBoxLayout(self.top_bar)
        title = QLabel("  TC Launcher Ultimate")
        title.setStyleSheet("color: white; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        # quick FPS label
        self.fps_label = QLabel("")
        self.fps_label.setStyleSheet("color: white; margin-right:8px;")
        top_layout.addWidget(self.fps_label)
        main_v.addWidget(self.top_bar)
        # below top bar: content layout
        content_h = QHBoxLayout()
        # left sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        categories = [
            "Home", "Notepad", "Python Runner", "AI Chat", "App Launcher",
            "Music Player", "File Tools (16)", "Internet Tools (placeholders)",
            "System Tools (placeholders)", "Creative (placeholders)",
            "Games (placeholders)", "Experimental (placeholders)",
            "Settings", "Exit"
        ]
        for c in categories:
            self.sidebar.addItem(QListWidgetItem(c))
        self.sidebar.currentRowChanged.connect(self.switch_page)
        content_h.addWidget(self.sidebar)
        # center stack
        self.stack = QStackedWidget()
        content_h.addWidget(self.stack, 1)
        # right log panel
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedWidth(360)
        content_h.addWidget(self.log)
        main_v.addLayout(content_h)
        main_h.addLayout(main_v)
        self.add_log("Launcher initialized.")
        # create pages
        self.pages = {}
        self.create_pages()
        self.sidebar.setCurrentRow(0)
        # timers for fps etc
        self._frame_count = 0
        self._last_time = time.time()
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self._fps_tick)
        self.fps_timer.start(1000//30)  # 30Hz wound-down tick; not heavy

    def add_log(self, text):
        self.log.append(f"[{timestamp()}] {text}")

    def _fps_tick(self):
        # simple estimate increment
        if cache['settings'].get('fps_counter'):
            now = time.time()
            self._frame_count += 1
            dt = now - self._last_time
            if dt >= 1.0:
                fps = self._frame_count / dt
                self.fps_label.setText(f"{fps:.0f} FPS")
                self._frame_count = 0
                self._last_time = now
        else:
            self.fps_label.setText("")

    def create_pages(self):
        # Home page
        home = QWidget()
        hv = QVBoxLayout(home)
        lbl = QLabel("Welcome to TC Launcher Ultimate")
        lbl.setFont(QFont("Segoe UI", 20))
        hv.addWidget(lbl)
        hv.addStretch()
        self.stack.addWidget(home)
        self.pages["Home"] = home

        # Notepad page
        self.notepad_editor = QTextEdit()
        np_page = QWidget()
        np_layout = QVBoxLayout(np_page)
        np_controls = QHBoxLayout()
        open_btn = QPushButton("Open File")
        save_btn = QPushButton("Save File")
        clear_btn = QPushButton("Clear")
        open_btn.clicked.connect(self.notepad_open)
        save_btn.clicked.connect(self.notepad_save)
        clear_btn.clicked.connect(lambda: self.notepad_editor.clear())
        np_controls.addWidget(open_btn); np_controls.addWidget(save_btn); np_controls.addWidget(clear_btn)
        np_layout.addLayout(np_controls)
        np_layout.addWidget(self.notepad_editor)
        self.stack.addWidget(np_page)
        self.pages["Notepad"] = np_page

        # Python Runner page
        py_page = QWidget()
        py_layout = QVBoxLayout(py_page)
        self.py_editor = QTextEdit()
        self.py_output = QTextEdit(); self.py_output.setReadOnly(True)
        run_btn = QPushButton("Run (capture output)")
        run_btn.clicked.connect(self.run_python_code)
        py_layout.addWidget(self.py_editor)
        py_layout.addWidget(run_btn)
        py_layout.addWidget(QLabel("Output:"))
        py_layout.addWidget(self.py_output)
        self.stack.addWidget(py_page)
        self.pages["Python Runner"] = py_page

        # AI Chat
        ai_page = QWidget(); ai_layout = QVBoxLayout(ai_page)
        self.ai_log = QTextEdit(); self.ai_log.setReadOnly(True)
        ai_input_h = QHBoxLayout()
        self.ai_input = QLineEdit()
        ai_send = QPushButton("Send")
        ai_send.clicked.connect(self.ai_send)
        ai_input_h.addWidget(self.ai_input); ai_input_h.addWidget(ai_send)
        ai_layout.addWidget(self.ai_log); ai_layout.addLayout(ai_input_h)
        self.stack.addWidget(ai_page); self.pages["AI Chat"] = ai_page
        # replay existing history
        for msg in cache.get("ai_history", []):
            self.ai_log.append(f"User: {msg.get('user')}\nAI: {msg.get('ai')}\n")

        # App Launcher
        app_page = QWidget(); app_layout = QVBoxLayout(app_page)
        self.app_list = QListWidget()
        add_app_btn = QPushButton("Add App (browse executable)")
        add_app_btn.clicked.connect(self.add_app)
        run_app_btn = QPushButton("Run Selected App")
        run_app_btn.clicked.connect(self.run_selected_app)
        save_fav_btn = QPushButton("Save Selected to Favorites")
        save_fav_btn.clicked.connect(self.save_selected_fav)
        app_layout.addWidget(add_app_btn); app_layout.addWidget(run_app_btn); app_layout.addWidget(save_fav_btn); app_layout.addWidget(self.app_list)
        # populate from cache
        for a in cache.get("recent_apps", []):
            self.app_list.addItem(a)
        app_page.setLayout(app_layout)
        self.stack.addWidget(app_page); self.pages["App Launcher"] = app_page

        # Music Player
        music_page = QWidget(); music_layout = QVBoxLayout(music_page)
        self.playlist_list = QListWidget()
        music_btns = QHBoxLayout()
        add_song = QPushButton("Add Song")
        add_song.clicked.connect(self.add_song)
        play_btn = QPushButton("Play")
        stop_btn = QPushButton("Stop")
        play_btn.clicked.connect(self.play_selected_song)
        stop_btn.clicked.connect(self.stop_music)
        music_btns.addWidget(add_song); music_btns.addWidget(play_btn); music_btns.addWidget(stop_btn)
        music_layout.addLayout(music_btns); music_layout.addWidget(self.playlist_list)
        for s in cache.get("music_playlist", []):
            self.playlist_list.addItem(s)
        self.stack.addWidget(music_page); self.pages["Music Player"] = music_page

        # File Tools (16 implemented basic)
        ft_page = QWidget(); ft_layout = QVBoxLayout(ft_page)
        # create 16 buttons and connect to implemented functions
        ft_buttons = [
            ("Batch Rename", self.ft_batch_rename),
            ("Duplicate Finder", self.ft_duplicate_finder),
            ("Folder Size Analyzer", self.ft_folder_size),
            ("Archive Manager (zip)", self.ft_archive_zip),
            ("Secure Delete (overwrite)", self.ft_secure_delete),
            ("File Hash (MD5/SHA256)", self.ft_file_hash),
            ("Quick Text Editor (open)", self.ft_quick_text_edit),
            ("Markdown Preview (placeholder)", lambda: self.add_log("Markdown preview placeholder")),
            ("Recent Files (from cache)", self.ft_recent_files),
            ("File Sorter (by ext)", self.ft_file_sorter),
            ("Image Batch Convert (placeholder)", lambda: self.add_log("Image convert placeholder")),
            ("CSV Preview (placeholder)", lambda: self.add_log("CSV preview placeholder")),
            ("Log Viewer (open file)", self.ft_log_viewer),
            ("File Backup (copy)", self.ft_file_backup),
            ("Shortcut Creator (windows .lnk placeholder)", lambda: self.add_log("Shortcut creator placeholder")),
            ("Empty Folder Cleaner", self.ft_empty_folder_cleaner)
        ]
        for name, fn in ft_buttons:
            b = QPushButton(name)
            b.clicked.connect(fn)
            ft_layout.addWidget(b)
        ft_layout.addStretch()
        self.stack.addWidget(ft_page); self.pages["File Tools (16)"] = ft_page

        # placeholders for others
        for p in ["Internet Tools (placeholders)", "System Tools (placeholders)",
                  "Creative (placeholders)", "Games (placeholders)", "Experimental (placeholders)"]:
            page = QWidget(); layout = QVBoxLayout(page)
            layout.addWidget(QLabel(f"{p} — placeholders ready for implementation"))
            layout.addStretch()
            self.stack.addWidget(page); self.pages[p] = page

        # Settings page
        settings_page = QWidget(); s_layout = QVBoxLayout(settings_page)
        btn_bg = QPushButton("Change Background Color")
        btn_bg.clicked.connect(lambda: self.pick_color("bg"))
        btn_btn = QPushButton("Change Button Color")
        btn_btn.clicked.connect(lambda: self.pick_color("btn"))
        btn_txt = QPushButton("Change Button Text Color")
        btn_txt.clicked.connect(lambda: self.pick_color("txt"))
        btn_top = QPushButton("Change Top Bar Color")
        btn_top.clicked.connect(lambda: self.pick_color("top"))
        radius_slider = QSlider(Qt.Orientation.Horizontal); radius_slider.setMinimum(0); radius_slider.setMaximum(40)
        radius_slider.setValue(cache['settings'].get('corner_radius', 10))
        radius_slider.valueChanged.connect(lambda v: self.set_corner_radius(v))
        opacity_slider = QSlider(Qt.Orientation.Horizontal); opacity_slider.setMinimum(50); opacity_slider.setMaximum(100)
        opacity_slider.setValue(int(cache['settings'].get('opacity', 1.0)*100))
        opacity_slider.valueChanged.connect(lambda v: self.set_opacity(v/100.0))
        fps_checkbox = QPushButton("Toggle FPS Counter")
        fps_checkbox.clicked.connect(self.toggle_fps)
        vsync_checkbox = QPushButton("Toggle VSync Setting (placeholder)")
        vsync_checkbox.clicked.connect(self.toggle_vsync)
        s_layout.addWidget(btn_bg); s_layout.addWidget(btn_btn); s_layout.addWidget(btn_txt); s_layout.addWidget(btn_top)
        s_layout.addWidget(QLabel("Corner Radius")); s_layout.addWidget(radius_slider)
        s_layout.addWidget(QLabel("Window Opacity")); s_layout.addWidget(opacity_slider)
        s_layout.addWidget(fps_checkbox); s_layout.addWidget(vsync_checkbox)
        s_layout.addStretch()
        self.stack.addWidget(settings_page); self.pages["Settings"] = settings_page

        # Exit page (confirm)
        exit_page = QWidget(); ex_layout = QVBoxLayout(exit_page)
        ex_layout.addWidget(QLabel("Exit TC Launcher — click Confirm to save and exit"))
        confirm = QPushButton("Confirm Exit")
        confirm.clicked.connect(self.exit_confirm)
        ex_layout.addWidget(confirm); ex_layout.addStretch()
        self.stack.addWidget(exit_page); self.pages["Exit"] = exit_page

        # Apply styling to stack buttons (live update)
        self.apply_styles()

    # ---------- Page switching ----------
    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        cat = self.sidebar.item(idx).text()
        self.add_log(f"Switched to: {cat}")

    # ---------- Notepad ----------
    def notepad_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open text file", "", "Text Files (*.txt *.md *.py *.log);;All Files (*)")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            self.notepad_editor.setPlainText(txt)
            # add to recent
            if path not in cache['recent_files']:
                cache['recent_files'].insert(0, path)
                cache['recent_files'] = cache['recent_files'][:50]
            self.add_log(f"Opened file: {path}")
        except Exception as e:
            self.add_log(f"Failed opening file: {e}")

    def notepad_save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save text file", "", "Text Files (*.txt *.md *.py);;All Files (*)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.notepad_editor.toPlainText())
            if path not in cache['recent_files']:
                cache['recent_files'].insert(0, path)
                cache['recent_files'] = cache['recent_files'][:50]
            self.add_log(f"Saved file: {path}")
        except Exception as e:
            self.add_log(f"Failed saving file: {e}")

    # ---------- Python Runner (exec capture) ----------
    def run_python_code(self):
        code = self.py_editor.toPlainText()
        if not code.strip():
            self.add_log("Python Runner: no code to run.")
            return
        self.add_log("Python Runner: starting execution...")
        # run in thread
        def worker(code_text):
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            buff = io.StringIO()
            sys.stdout = buff; sys.stderr = buff
            try:
                exec(compile(code_text, "<tc_python_runner>", "exec"), {})
            except Exception as e:
                buff.write(f"\nError: {e}\n")
            finally:
                out = buff.getvalue()
                sys.stdout = old_stdout; sys.stderr = old_stderr
            # send output to UI thread
            def finish():
                self.py_output.append(out)
                # save snippet
                cache['python_snippets'].insert(0, code_text)
                cache['python_snippets'] = cache['python_snippets'][:50]
                self.add_log("Python Runner: finished.")
            QApplication.instance().postEvent(self, FunctionEvent(finish))
        threading.Thread(target=worker, args=(code,), daemon=True).start()

    # ---------- AI Chat placeholder ----------
    def ai_send(self):
        text = self.ai_input.text().strip()
        if not text: return
        self.ai_log.append(f"User: {text}")
        reply = f"Echo: {text}"  # placeholder for smarter AI
        self.ai_log.append(f"AI: {reply}\n")
        cache['ai_history'].append({"user": text, "ai": reply})
        cache['ai_history'] = cache['ai_history'][-200:]
        self.ai_input.clear()
        self.add_log("AI Chat: message exchanged.")

    # ---------- App Launcher ----------
    def add_app(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select executable or script")
        if not path: return
        self.app_list.addItem(path)
        if path not in cache['recent_apps']:
            cache['recent_apps'].insert(0, path)
            cache['recent_apps'] = cache['recent_apps'][:60]
        self.add_log(f"Added app: {path}")

    def run_selected_app(self):
        it = self.app_list.currentItem()
        if not it: self.add_log("No app selected."); return
        path = it.text()
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            else:
                subprocess.Popen([path])
            self.add_log(f"Launched: {path}")
        except Exception as e:
            self.add_log(f"Failed launch: {e}")

    def save_selected_fav(self):
        it = self.app_list.currentItem()
        if not it: self.add_log("No app selected."); return
        path = it.text()
        if path not in cache['app_favorites']:
            cache['app_favorites'].append(path)
            cache['app_favorites'] = cache['app_favorites'][:100]
            self.add_log(f"Saved to favorites: {path}")

    # ---------- Music Player ----------
    def add_song(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select audio file", "", "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)")
        if not path: return
        self.playlist_list.addItem(path)
        if path not in cache['music_playlist']:
            cache['music_playlist'].append(path)
            cache['music_playlist'] = cache['music_playlist'][:200]
        self.add_log(f"Added song: {path}")

    def play_selected_song(self):
        it = self.playlist_list.currentItem()
        if not it: self.add_log("No song selected."); return
        path = it.text()
        self.add_log(f"Playing: {path}")
        if PYGAME_OK:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            except Exception as e:
                self.add_log(f"pygame play error: {e}; trying system default")
                open_with_system(path)
        else:
            open_with_system(path)

    def stop_music(self):
        if PYGAME_OK:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        self.add_log("Music stopped (best-effort).")

    # ---------- File Tools implemented ----------
    def ft_batch_rename(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder with files to rename")
        if not folder: return
        pattern, ok = QInputDialog.getText(self, "Rename Pattern", "Enter pattern with {} for numbering (e.g. file_{}):")
        if not ok: return
        files = sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        for i,fn in enumerate(files, 1):
            ext = os.path.splitext(fn)[1]
            src = os.path.join(folder, fn)
            dst = os.path.join(folder, pattern.format(i) + ext)
            try:
                os.rename(src, dst)
            except Exception as e:
                self.add_log(f"Rename failed: {e}")
        self.add_log(f"Batch renamed {len(files)} files in {folder}.")

    def ft_duplicate_finder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to scan for duplicates")
        if not folder: return
        self.add_log("Duplicate scan started (may take a while)...")
        def worker(folder):
            seen = {}
            dups = []
            for root,_,files in os.walk(folder):
                for f in files:
                    p = os.path.join(root,f)
                    try:
                        h = hashlib.md5(open(p,"rb").read()).hexdigest()
                    except Exception:
                        continue
                    if h in seen:
                        dups.append((seen[h], p))
                    else:
                        seen[h] = p
            def finish():
                self.add_log(f"Duplicate scan complete. Found {len(dups)} duplicate pairs.")
            QApplication.instance().postEvent(self, FunctionEvent(finish))
        threading.Thread(target=worker, args=(folder,), daemon=True).start()

    def ft_folder_size(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to compute size")
        if not folder: return
        total = 0
        for root,_,files in os.walk(folder):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root,f))
                except:
                    pass
        self.add_log(f"Folder {folder} size: {total/1024/1024:.2f} MB")

    def ft_archive_zip(self):
        from zipfile import ZipFile
        folder = QFileDialog.getExistingDirectory(self, "Select folder to zip")
        if not folder: return
        target, _ = QFileDialog.getSaveFileName(self, "Save Zip As", "", "Zip Files (*.zip)")
        if not target: return
        with ZipFile(target, "w") as z:
            for root,_,files in os.walk(folder):
                for f in files:
                    z.write(os.path.join(root,f), arcname=os.path.relpath(os.path.join(root,f), folder))
        self.add_log(f"Folder {folder} zipped to {target}")

    def ft_secure_delete(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select file to securely overwrite and delete")
        if not p: return
        try:
            length = os.path.getsize(p)
            with open(p,"br+") as f:
                f.seek(0)
                f.write(b"\x00"*length)
            os.remove(p)
            self.add_log(f"Securely deleted {p}")
        except Exception as e:
            self.add_log(f"Secure delete failed: {e}")

    def ft_file_hash(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select file to hash")
        if not p: return
        try:
            with open(p,"rb") as f:
                data = f.read()
            md5 = hashlib.md5(data).hexdigest()
            sha = hashlib.sha256(data).hexdigest()
            self.add_log(f"{p} MD5: {md5} | SHA256: {sha}")
        except Exception as e:
            self.add_log(f"Hashing failed: {e}")

    def ft_quick_text_edit(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open text file")
        if not p: return
        try:
            with open(p,"r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            win = QMainWindow()
            te = QTextEdit(); te.setPlainText(txt)
            save_btn = QPushButton("Save")
            def do_save():
                try:
                    with open(p,"w", encoding="utf-8") as f:
                        f.write(te.toPlainText())
                    self.add_log(f"Saved quick edit to {p}")
                    win.close()
                except Exception as e:
                    self.add_log(f"Save failed: {e}")
            top = QWidget(); top_layout = QVBoxLayout(top)
            top_layout.addWidget(te); top_layout.addWidget(save_btn)
            save_btn.clicked.connect(do_save)
            win.setCentralWidget(top); win.setWindowTitle(f"Quick Edit - {os.path.basename(p)}"); win.resize(600,500); win.show()
        except Exception as e:
            self.add_log(f"Open failed: {e}")

    def ft_recent_files(self):
        r = cache.get("recent_files", [])
        dlg = QInputDialog(self); dlg.setWindowTitle("Recent Files"); dlg.setLabelText("Select index to open (0 is newest) or -1 to cancel")
        if not r:
            self.add_log("No recent files in cache.")
            return
        # quick display in message
        txt = "\n".join([f"{i}: {p}" for i, p in enumerate(r[:30])])
        QMessageBox.information(self, "Recent files (top 30)", txt)

    def ft_file_sorter(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to sort by extension")
        if not folder: return
        for f in os.listdir(folder):
            src = os.path.join(folder, f)
            if not os.path.isfile(src): continue
            ext = os.path.splitext(f)[1].lstrip(".").lower() or "noext"
            dest_dir = os.path.join(folder, ext)
            os.makedirs(dest_dir, exist_ok=True)
            try:
                shutil.move(src, os.path.join(dest_dir, f))
            except Exception as e:
                self.add_log(f"Move failed: {e}")
        self.add_log(f"Sorted files in {folder} by extension.")

    def ft_log_viewer(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open log file")
        if not p: return
        try:
            with open(p,"r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            win = QMainWindow(); te = QTextEdit(); te.setReadOnly(True); te.setPlainText(txt)
            win.setCentralWidget(te); win.setWindowTitle(os.path.basename(p)); win.resize(800,600); win.show()
            self.add_log(f"Opened log viewer for {p}")
        except Exception as e:
            self.add_log(f"Failed to open log: {e}")

    def ft_file_backup(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select file to backup")
        if not p: return
        target = QFileDialog.getExistingDirectory(self, "Select backup folder")
        if not target: return
        try:
            shutil.copy2(p, target)
            self.add_log(f"Backed up {p} to {target}")
        except Exception as e:
            self.add_log(f"Backup failed: {e}")

    def ft_empty_folder_cleaner(self):
        folder = QFileDialog.getExistingDirectory(self, "Select root folder to remove empty folders")
        if not folder: return
        removed = 0
        for root, dirs, files in os.walk(folder, topdown=False):
            if not dirs and not files:
                try:
                    os.rmdir(root)
                    removed += 1
                except:
                    pass
        self.add_log(f"Removed {removed} empty folders in {folder}")

    # ---------- Settings helpers ----------
    def pick_color(self, target):
        col = QColorDialog.getColor()
        if not col.isValid():
            return
        hexc = col.name()
        if target == "bg":
            cache['settings']['bg_color'] = hexc
            self.setStyleSheet(f"background-color:{hexc};")
        elif target == "btn":
            cache['settings']['btn_color'] = hexc
            self.apply_styles()
        elif target == "txt":
            cache['settings']['btn_text'] = hexc
            self.apply_styles()
        elif target == "top":
            cache['settings']['top_bar'] = hexc
            self.top_bar.setStyleSheet(f"background-color:{hexc};")
            # fallback if not present
            self.top_bar.setStyleSheet(f"background-color:{hexc};")
        self.add_log(f"Set {target} color to {hexc}")

    def set_corner_radius(self, v):
        cache['settings']['corner_radius'] = v
        self.apply_styles()

    def set_opacity(self, v):
        self.setWindowOpacity(v)
        cache['settings']['opacity'] = v

    def apply_styles(self):
        r = cache['settings'].get('corner_radius', 10)
        btn_color = cache['settings'].get('btn_color', "#2F9E44")
        txt_color = cache['settings'].get('btn_text', "#ffffff")
        style = f"""
            QPushButton {{
                border-radius: {r}px;
                background-color: {btn_color};
                color: {txt_color};
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """
        self.setStyleSheet(f"background-color: {cache['settings'].get('bg_color', '#1f1f1f')};")
        # apply to all buttons in stack
        for page in self.pages.values():
            for btn in page.findChildren(QPushButton):
                btn.setStyleSheet(style)

    def toggle_fps(self):
        cache['settings']['fps_counter'] = not cache['settings'].get('fps_counter', False)
        self.add_log(f"FPS counter {'enabled' if cache['settings']['fps_counter'] else 'disabled'}")

    def toggle_vsync(self):
        cache['settings']['vsync'] = not cache['settings'].get('vsync', True)
        self.add_log(f"VSync setting toggled (placeholder) -> {cache['settings']['vsync']}")

    # ---------- Exit / save ----------
    def exit_confirm(self):
        save_cache(cache)
        self.add_log("Saved cache and exiting.")
        QApplication.quit()

    def closeEvent(self, event):
        save_cache(cache)
        event.accept()

# ---------- Helper to post function calls to main Qt loop ----------
from PyQt6.QtCore import QEvent
class FunctionEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, func):
        super().__init__(FunctionEvent.EVENT_TYPE)
        self.func = func

def custom_event_filter(obj, event):
    if isinstance(event, FunctionEvent):
        try:
            event.func()
        except Exception as e:
            print("FunctionEvent error:", e)
        return True
    return False

# install the event filter
app = QApplication.instance() or QApplication(sys.argv)
app.installEventFilter(app)
# patching eventFilter: PyQt's default app has .eventFilter method; use setEventFilter by subclassing not trivial here
# so we use application.postEvent with QCoreApplication.instance().postEvent in the worker to add events.
# But above we used QApplication.instance().postEvent(...) where needed.

# ---------- Helper to open file with system default ----------
def open_with_system(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print("open_with_system error:", e)

# ---------- Run the app ----------
if __name__ == "__main__":
    # ensure the QApplication exists
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    # Create and show splash which will launch main
    splash = Splash()
    sys.exit(app.exec())
