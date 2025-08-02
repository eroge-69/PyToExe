#!/usr/bin/env python3
# sidxide.py

import sys, os, json
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QFileDialog,
    QComboBox, QToolBar, QLabel, QCheckBox, QWidget,
    QListWidget, QSplitter, QLineEdit, QListWidgetItem,
    QDockWidget, QTextEdit, QMessageBox, QVBoxLayout,
)
from PySide6.QtGui import (
    QFont, QColor, QTextCursor, QPainter, QPalette,
    QSyntaxHighlighter, QTextCharFormat, QKeySequence,
    QCursor, QPixmap, QAction, QShortcut,
)
from PySide6.QtCore import Qt, QTimer, QEvent

# Optional embedded browser
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename, TextLexer
from pygments.styles import get_style_by_name
from pygments.token import Token

from astral import LocationInfo
from astral.sun import sun

from fuzzywuzzy import process as fuzz_process

# Paths
SETTINGS_PATH = Path.home() / ".sidx1_ide_settings.json"
PLUGINS_DIR   = Path.home() / ".sidx1_ide_plugins"
SCENES_DIR    = Path.home() / ".sidx1_ide_scenes"


def load_settings():
    default = {
        "last_opened": None, "language": "python", "theme": "monokai",
        "crt": False, "sunlight": False,
        "font_family": "Fira Code", "font_size": 11,
        "project_root": None, "scene": None
    }
    try:
        cfg = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        default.update(cfg)
    except:
        pass
    return default

def save_settings(s):
    try:
        SETTINGS_PATH.write_text(json.dumps(s, indent=2), encoding="utf-8")
    except:
        pass


class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, lexer_name="python", style_name="monokai"):
        super().__init__(parent.document())
        self.current_word = ""
        self.glow_alpha = 0
        self.glow_increasing = True
        self.set_style(style_name)
        self.set_language(lexer_name)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulse)
        self._timer.start(60)

    def set_language(self, name):
        try:
            if name == "plain text":
                self.lexer = TextLexer()
            elif name.lower() in ("react", "jsx"):
                self.lexer = get_lexer_by_name("jsx")
            else:
                self.lexer = get_lexer_by_name(name)
        except:
            self.lexer = TextLexer()
        self.rehighlight()

    def set_style(self, name):
        try:
            style = get_style_by_name(name)
        except:
            style = get_style_by_name("monokai")
        self.token_formats = {}
        for tok, st in style.styles.items():
            fmt = QTextCharFormat()
            for part in st.split():
                if part.startswith("bg:"):
                    fmt.setBackground(QColor("#"+part[3:]))
                elif part.startswith("fg:"):
                    fmt.setForeground(QColor("#"+part[3:]))
                elif part == "bold":
                    fmt.setFontWeight(QFont.Bold)
                elif part == "italic":
                    fmt.setFontItalic(True)
                elif part == "underline":
                    fmt.setFontUnderline(True)
            self.token_formats[tok] = fmt
        self.rehighlight()

    def _pulse(self):
        self.glow_alpha += 8 if self.glow_increasing else -8
        if self.glow_alpha >= 120: self.glow_increasing = False
        if self.glow_alpha <= 30:  self.glow_increasing = True
        self.rehighlight()

    def highlightBlock(self, text):
        try:
            tokens = lex(text, self.lexer)
        except:
            tokens = [(Token.Text, text)]
        idx = 0
        for ttype, chunk in tokens:
            length = len(chunk)
            fmt = self.token_formats.get(
                ttype, self.token_formats.get(ttype.parent, QTextCharFormat())
            )
            if fmt:
                self.setFormat(idx, length, fmt)
            idx += length

        if self.current_word:
            pos = text.find(self.current_word)
            if pos != -1:
                glow = QTextCharFormat()
                glow.setBackground(QColor(255,255,255,self.glow_alpha))
                glow.setFontWeight(QFont.Bold)
                self.setFormat(pos, len(self.current_word), glow)

    def update_current_word(self, w):
        self.current_word = w
        self.rehighlight()


class CRTEffectOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.hide()

    def paintEvent(self, event):
        from PySide6.QtGui import QRadialGradient
        p = QPainter(self)
        w, h = self.width(), self.height()
        g = QRadialGradient(w/2, h/2, max(w,h)/1.2)
        g.setColorAt(0, QColor(0,0,0,0))
        g.setColorAt(1, QColor(0,0,0,80))
        p.fillRect(self.rect(), g)
        for y in range(0, h, 6):
            p.fillRect(0, y, w, 3, QColor(0,0,0,25))
        p.setOpacity(0.03)
        for _ in range(120):
            x = os.urandom(1)[0]/255 * w
            y = os.urandom(1)[0]/255 * h
            p.drawPoint(int(x), int(y))
        p.setOpacity(1.0)


class SunlightOverlay(QWidget):
    def __init__(self, parent, loc=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.loc = loc or LocationInfo("Denver","USA","America/Denver",39.7392,-104.9903)
        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(60000)
        self.setAttribute(Qt.WA_NoSystemBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        now = datetime.now(self.loc.tzinfo)
        s = sun(self.loc.observer, date=now.date(), tzinfo=self.loc.tzinfo)
        ratio = max(0, min(1, (now - s["sunrise"]) / (s["sunset"] - s["sunrise"])))
        if ratio > 0:
            alpha = int(100*ratio)
            p.fillRect(self.rect(), QColor(255,250,220,alpha))
            w, h = self.width(), self.height()
            sx, sy = int(w*0.8), int(h*(1-ratio*0.6))
            r = 120 + int(80*ratio)
            glow = QColor(255,245,200,int(180*ratio))
            p.setBrush(glow); p.setPen(Qt.NoPen)
            p.drawEllipse(sx-r//2, sy-r//2, r, r)


class PluginManager:
    def __init__(self, ide):
        self.ide = ide
        PLUGINS_DIR.mkdir(exist_ok=True)
        self.plugins = []
        self.load_plugins()
    def load_plugins(self):
        for py in PLUGINS_DIR.glob("*.py"):
            try:
                ns = {}
                exec(py.read_text(encoding="utf-8"), {"ide":self.ide}, ns)
                self.plugins.append((py.name, ns))
            except Exception as e:
                print("Plugin load error", py, e)
    def trigger(self, hook, *args, **kw):
        for _, ns in self.plugins:
            if hook in ns:
                try: ns[hook](*args, **kw)
                except: pass


class RuleAssistant:
    def __init__(self, main_window):
        self.main = main_window
        self.last = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.evaluate)
        self.timer.start(1500)
    def evaluate(self):
        code = self.main.editor.toPlainText()
        sug = self._rules(code)
        if sug and sug!=self.last:
            self.last=sug
            self._popup(sug)
            if hasattr(self.main,"assistant_log"):
                self.main.assistant_log.append(sug)
    def _rules(self, txt):
        for i, line in enumerate(txt.splitlines()):
            s=line.strip()
            if s.startswith("def ") and not s.endswith(":"):
                return f"Line {i+1}: missing ':' on def"
            if s.startswith("if ") and "==" in s and not s.endswith(":"):
                return f"Line {i+1}: missing ':' on if"
            if line.endswith(" "):
                return f"Line {i+1}: trailing space"
            if "except:" in s:
                return f"Line {i+1}: bare except risky"
            if len(line)>120:
                return f"Line {i+1}: over 120 chars"
        return ""
    def _popup(self, t):
        msg=QMessageBox(self.main)
        msg.setWindowTitle("sidxide Assistant")
        msg.setText(t)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        r=self.main.editor.cursorRect()
        gp=self.main.editor.viewport().mapToGlobal(r.bottomRight())
        msg.move(gp.x()-200, gp.y()+10)
        msg.show()


def make_sidx1_cursor(sz=64):
    base=os.path.dirname(__file__)
    logo=os.path.join(base,"sidx1_logo.png")
    pix=QPixmap(sz,sz); pix.fill(Qt.transparent)
    p=QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
    if os.path.exists(logo):
        img=QPixmap(logo).scaled(sz,sz,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        p.drawPixmap(0,0,img)
    else:
        f=QFont("Fira Code",int(sz*0.25)); f.setBold(True)
        p.setFont(f); p.setPen(QColor(180,220,255))
        p.drawText(pix.rect(),Qt.AlignCenter,"sidxide")
    p.end(); return QCursor(pix,hotX=sz//2,hotY=sz//2)
def install_sidx1_cursor(app): app.setOverrideCursor(make_sidx1_cursor())


class SceneManager:
    def __init__(self, ide):
        self.ide=ide
        SCENES_DIR.mkdir(exist_ok=True); self.current=None
    def save_scene(self,name):
        sc={"show_browser":self.ide.browser_dock.isVisible(),
            "show_ai":self.ide.ai_dock.isVisible()}
        p=SCENES_DIR/f"{name}.json"; p.write_text(json.dumps(sc,indent=2),encoding="utf-8")
        self.current=name
    def load_scene(self,name):
        p=SCENES_DIR/f"{name}.json"
        if not p.exists(): return False
        sc=json.loads(p.read_text(encoding="utf-8"))
        self.ide.browser_dock.setVisible(sc.get("show_browser",False))
        self.ide.ai_dock.setVisible(sc.get("show_ai",False))
        self.current=name; return True


class IDEMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sidxide")
        self.resize(1400,900)
        self.settings=load_settings(); self.current_file=None
        self.plugin_mgr=PluginManager(self)
        self.scene_mgr=SceneManager(self)
        self.assistant=RuleAssistant(self)
        self._build_ui()
        self._load_state()
        self._apply_theme_and_language()

    def _build_ui(self):
        # Project list
        self.file_list=QListWidget(); self.file_list.setMaximumWidth(260)
        self.file_list.itemDoubleClicked.connect(self._open_from_project)
        # Editor
        self.editor=QPlainTextEdit(); self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        f=QFont(self.settings["font_family"],self.settings["font_size"])
        f.setStyleStrategy(QFont.PreferAntialias); self.editor.setFont(f)
        self.highlighter=PygmentsHighlighter(self.editor,
                                             lexer_name=self.settings["language"],
                                             style_name=self.settings["theme"])
        self.editor.cursorPositionChanged.connect(self._on_cursor_move)
        self.editor.textChanged.connect(self._on_text_changed)
        # Splitter
        sp=QSplitter(); left=QWidget(); lv=QVBoxLayout(left); lv.setContentsMargins(0,0,0,0)
        lv.addWidget(QLabel("Project")); lv.addWidget(self.file_list)
        sp.addWidget(left); sp.addWidget(self.editor); sp.setStretchFactor(1,3)
        self.setCentralWidget(sp)
        # Overlays
        self.crt_overlay=CRTEffectOverlay(self.editor.viewport())
        self.sun_overlay=SunlightOverlay(self.editor.viewport())
        self.editor.viewport().installEventFilter(self)
        if self.settings["crt"]: self.crt_overlay.show()
        if self.settings["sunlight"]: self.sun_overlay.show()
        # Toolbar
        tb=QToolBar(); tb.setMovable(False); self.addToolBar(tb)
        oa=QAction("Open",self); oa.triggered.connect(self.open_file); tb.addAction(oa)
        sa=QAction("Save",self); sa.triggered.connect(self.save_file); tb.addAction(sa)
        # Language
        self.lang_combo=QComboBox(); langs=["plain text","python","javascript","java","css","html","react","bash","json","lua","c","cpp"]
        self.lang_combo.addItems(langs); cur=self.settings["language"]
        if cur=="jsx": cur="react"
        if cur not in langs: cur="python"
        self.lang_combo.setCurrentText(cur)
        self.lang_combo.currentTextChanged.connect(self._change_language)
        tb.addWidget(QLabel("Language:")); tb.addWidget(self.lang_combo)
        # Theme
        self.theme_combo=QComboBox(); self.theme_combo.addItems(["monokai","dracula","native","vs","friendly"])
        self.theme_combo.setCurrentText(self.settings["theme"])
        self.theme_combo.currentTextChanged.connect(self._change_theme)
        tb.addWidget(QLabel(" Theme:")); tb.addWidget(self.theme_combo)
        # CRT / Sunlight
        self.crt_cb=QCheckBox("CRT"); self.crt_cb.setChecked(self.settings["crt"])
        self.crt_cb.stateChanged.connect(self._toggle_crt); tb.addWidget(self.crt_cb)
        self.sun_cb=QCheckBox("Sunlight"); self.sun_cb.setChecked(self.settings["sunlight"])
        self.sun_cb.stateChanged.connect(self._toggle_sunlight); tb.addWidget(self.sun_cb)
        # Fuzzy palette
        self.cmd=QLineEdit(); self.cmd.setPlaceholderText("Ctrl+P fuzzy open")
        self.cmd.returnPressed.connect(self._run_palette); self.cmd.setMaximumWidth(300)
        tb.addWidget(self.cmd)
        # Scenes
        la=QAction("Load Scene",self); la.triggered.connect(self._prompt_load_scene); tb.addAction(la)
        ss=QAction("Save Scene",self); ss.triggered.connect(self._prompt_save_scene); tb.addAction(ss)
        # Status
        self.status=QLabel(""); tb.addSeparator(); tb.addWidget(self.status)
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+S"),self,activated=self.save_file)
        QShortcut(QKeySequence("Ctrl+O"),self,activated=self.open_file)
        QShortcut(QKeySequence("Ctrl+P"),self,activated=lambda:self.cmd.setFocus())
        # Assistant log
        self.assistant_log=QTextEdit(); self.assistant_log.setReadOnly(True)
        ad=QDockWidget("Assistant Log",self); ad.setWidget(self.assistant_log); self.addDockWidget(Qt.RightDockWidgetArea,ad)
        self.ai_dock=ad
        # Browser
        if BROWSER_AVAILABLE:
            br=QWebEngineView(); br.setUrl("https://duckduckgo.com")
            bd=QDockWidget("Browser",self); bd.setWidget(br); self.addDockWidget(Qt.RightDockWidgetArea,bd)
            self.browser_dock=bd
        else:
            bd=QDockWidget("Browser Missing",self); bd.setWidget(QLabel("Qt WebEngine not installed"))
            self.addDockWidget(Qt.RightDockWidgetArea,bd); self.browser_dock=bd
        # Palette & cursor
        self._apply_palette()
        install_sidx1_cursor(QApplication.instance())

    def _apply_palette(self):
        pal=QPalette()
        pal.setColor(QPalette.Window,QColor(25,25,25))
        pal.setColor(QPalette.WindowText,QColor(230,230,230))
        pal.setColor(QPalette.Base,QColor(18,18,18))
        pal.setColor(QPalette.AlternateBase,QColor(30,30,30))
        pal.setColor(QPalette.Text,QColor(220,220,220))
        pal.setColor(QPalette.Button,QColor(40,40,40))
        pal.setColor(QPalette.ButtonText,QColor(220,220,220))
        pal.setColor(QPalette.Highlight,QColor(100,100,180))
        pal.setColor(QPalette.HighlightedText,QColor(255,255,255))
        self.setPalette(pal)

    def _load_state(self):
        if self.settings["project_root"]:
            self._refresh_project_list()
        lo=self.settings["last_opened"]
        if lo and Path(lo).exists():
            self._load_file_at_path(lo)
        sc=self.settings["scene"]
        if sc:
            self.scene_mgr.load_scene(sc)

    def open_file(self):
        p,_=QFileDialog.getOpenFileName(self,"Open File","","All Files (*.*)")
        if p: self._load_file_at_path(p)

    def _load_file_at_path(self,p):
        try:
            txt=Path(p).read_text(encoding="utf-8",errors="ignore")
            self.editor.setPlainText(txt)
            self.current_file=p
            self.settings["last_opened"]=p; save_settings(self.settings)
            try:
                lexr=guess_lexer_for_filename(p,txt); nm=lexr.aliases[0] if lexr.aliases else "plain text"
                if nm=="jsx": nm="react"
                self.lang_combo.setCurrentText(nm)
            except: pass
            self.status.setText(f"Opened {os.path.basename(p)}")
            if self.settings["project_root"]:
                self._refresh_project_list()
        except Exception as e:
            self.status.setText(f"Open failed: {e}")

    def save_file(self):
        if not self.current_file:
            p,_=QFileDialog.getSaveFileName(self,"Save File As","","All Files (*.*)")
            if not p: return
            self.current_file=p
        try:
            Path(self.current_file).write_text(self.editor.toPlainText(),encoding="utf-8")
            self.status.setText(f"Saved {os.path.basename(self.current_file)}")
            self.settings["last_opened"]=self.current_file; save_settings(self.settings)
        except Exception as e:
            self.status.setText(f"Save failed: {e}")

    def _refresh_project_list(self):
        self.file_list.clear()
        root=self.settings["project_root"]
        if root:
            for f in Path(root).rglob("*"):
                if f.is_file():
                    itm=QListWidgetItem(str(f.relative_to(root)))
                    itm.setData(Qt.UserRole,str(f))
                    self.file_list.addItem(itm)

    def _open_from_project(self,itm):
        p=itm.data(Qt.UserRole)
        if p: self._load_file_at_path(p)

    def _run_palette(self):
        q=self.cmd.text().strip(); r=self.settings["project_root"]
        if not q or not r: return
        cand=[str(f.relative_to(r)) for f in Path(r).rglob("*") if f.is_file()]
        best=fuzz_process.extract(q,cand,limit=5)
        if best:
            top=best[0][0]
            m=self.file_list.findItems(top,Qt.MatchContains)
            if m: self._open_from_project(m[0])

    def _on_cursor_move(self):
        c=self.editor.textCursor(); c.select(QTextCursor.WordUnderCursor)
        w=c.selectedText(); self.highlighter.update_current_word(w)

    def _on_text_changed(self):
        self.plugin_mgr.trigger("on_text_changed",self.editor.toPlainText())

    def eventFilter(self,obj,event):
        if obj is self.editor.viewport() and event.type() in (QEvent.Resize,QEvent.Paint):
            self._update_overlays()
        return super().eventFilter(obj,event)

    def _update_overlays(self):
        rect=self.editor.viewport().rect()
        self.crt_overlay.setGeometry(rect)
        self.sun_overlay.setGeometry(rect)

    def _apply_theme_and_language(self):
        self.highlighter.set_language(self.settings["language"])
        self.highlighter.set_style(self.settings["theme"])

    def _change_language(self,l):
        self.settings["language"]=l; save_settings(self.settings)
        self.highlighter.set_language(l); self.status.setText(f"Language → {l}")

    def _change_theme(self,t):
        self.settings["theme"]=t; save_settings(self.settings)
        self.highlighter.set_style(t); self.status.setText(f"Theme → {t}")

    def _toggle_crt(self,state):
        on = (state==Qt.Checked); self.settings["crt"]=on; save_settings(self.settings)
        self.crt_overlay.setVisible(on)

    def _toggle_sunlight(self,state):
        on = (state==Qt.Checked); self.settings["sunlight"]=on; save_settings(self.settings)
        self.sun_overlay.setVisible(on)

    def _prompt_save_scene(self):
        n,_=QFileDialog.getSaveFileName(self,"Save Scene As",str(SCENES_DIR),"JSON Files (*.json)")
        if n:
            b=Path(n).stem; self.scene_mgr.save_scene(b)
            self.settings["scene"]=b; save_settings(self.settings)
            self.status.setText(f"Saved scene {b}")

    def _prompt_load_scene(self):
        n,_=QFileDialog.getOpenFileName(self,"Load Scene",str(SCENES_DIR),"JSON Files (*.json)")
        if n:
            b=Path(n).stem
            if self.scene_mgr.load_scene(b):
                self.settings["scene"]=b; save_settings(self.settings)
                self.status.setText(f"Loaded scene {b}")
            else:
                self.status.setText("Scene load failed")


def main():
    app = QApplication(sys.argv)
    # HighDPI attribute deprecated in Qt6; omit or update as needed.
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
