# PocketMine Toolbox – PyQt6
# -------------------------------------------------------------
# Features:
# • Modern dark UI with soft shadows and hover animations
# • Tools:
#   - Create .phar  (requires local PHP with phar extension; we generate & run a tiny PHP pack script)
#   - Extract .phar  (same requirement)
#   - API Injector   (edit plugin.yml api field)
#   - Crashdump Parser (reads PocketMine JSON crashdumps and summarizes)
#   - Decode .pmf (simple reader for PocketMine Model/Font *.pmf metadata if present; shows hex/size)
#   - Generate Skeleton Plugin (creates plugin folder with plugin.yml + src/Main.php)
#   - Poggit Search (opens browser)
#   - MOTD Generator (helpers for § color codes; copy/save)
#   - Ping Server (Bedrock UDP status ping)
#   - Server Manager + Live Console (run PocketMine server process, view logs, send commands)
#   - Config Editor (edit/save YAML/JSON/TXT with monospaced editor)
# -------------------------------------------------------------
# Notes:
# • Tested with PyQt6. Install:  pip install PyQt6 pyyaml
# • For .phar create/extract you need: PHP in PATH and phar.readonly=0 for create.
#   The tool invokes:  php -d phar.readonly=0 <temp_builder.php>
# • This file is meant as a single-file app. Run with:  python pocketmine_toolbox.py

import os
import sys
import json
import time
import uuid
import socket
import struct
import tempfile
import threading
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QRect, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect,
    QHBoxLayout, QFileDialog, QMessageBox, QLineEdit, QTextEdit, QScrollArea, QDialog, QGridLayout,
    QComboBox, QSpinBox, QSplitter, QListWidget, QListWidgetItem, QTabWidget, QPlainTextEdit,
    QProgressBar
)

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# -----------------------------
# Helpers
# -----------------------------

def soft_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setMinimumHeight(40)
    btn.setStyleSheet(
        """
        QPushButton {
            background-color: #222428; border: 0px; border-radius: 10px; color: #eaeaea; padding: 10px;
        }
        QPushButton:hover { background-color: #2a2d32; }
        QPushButton:pressed { background-color: #5A189A; }
        """
    )
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setColor(QColor(0, 0, 0, 140))
    shadow.setOffset(0, 8)
    btn.setGraphicsEffect(shadow)
    return btn

class Animator:
    @staticmethod
    def pulse(widget, scale=1.03, duration=160):
        rect = widget.geometry()
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        new_w, new_h = int(rect.width()*scale), int(rect.height()*scale)
        anim.setStartValue(rect)
        anim.setEndValue(QRect(rect.x() - (new_w-rect.width())//2,
                               rect.y() - (new_h-rect.height())//2,
                               new_w, new_h))
        anim.start()
        widget._anim = anim  # prevent GC

# -----------------------------
# Dialogs / Tools
# -----------------------------

class PharBuilder(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create .phar (PHP required)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)

        row = QHBoxLayout()
        self.src = QLineEdit(); self.src.setPlaceholderText("Plugin folder containing plugin.yml and src/")
        b1 = soft_button("Browse…"); b1.clicked.connect(self.choose_src)
        row.addWidget(self.src); row.addWidget(b1)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        self.dest = QLineEdit(); self.dest.setPlaceholderText("Output file e.g. MyPlugin.phar")
        b2 = soft_button("Save as…"); b2.clicked.connect(self.choose_dest)
        row2.addWidget(self.dest); row2.addWidget(b2)
        lay.addLayout(row2)

        self.progress = QProgressBar(); self.progress.setRange(0,0); self.progress.hide()
        lay.addWidget(self.progress)

        go = soft_button("Create .phar")
        go.clicked.connect(self.run)
        lay.addWidget(go)

        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(160)
        self.log.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.log)

    def choose_src(self):
        d = QFileDialog.getExistingDirectory(self, "Select plugin folder")
        if d:
            self.src.setText(d)

    def choose_dest(self):
        f, _ = QFileDialog.getSaveFileName(self, "Save .phar", filter="PHAR (*.phar)")
        if f:
            if not f.lower().endswith('.phar'):
                f += '.phar'
            self.dest.setText(f)

    def run(self):
        src = self.src.text().strip(); dest = self.dest.text().strip()
        if not src or not dest:
            QMessageBox.warning(self, "Missing", "Select source folder and destination file.")
            return
        if not Path(src).exists():
            QMessageBox.critical(self, "Error", "Source folder does not exist.")
            return
        self.progress.show()
        threading.Thread(target=self._build_phar, args=(src, dest), daemon=True).start()

    def _build_phar(self, src, dest):
        php = os.environ.get("PHP", "php")
        # Create a small PHP packer script in a temp file
        script = f"""
        <?php
        error_reporting(E_ALL); ini_set('display_errors', 1);
        if (!class_exists('Phar')) {{
            fwrite(STDERR, "Phar extension not available\n");
            exit(2);
        }}
        $src = '{src}'."/";
        $dest = '{dest}';
        if (file_exists($dest)) {{ unlink($dest); }}
        $phar = new Phar($dest);
        $phar->startBuffering();
        $phar->buildFromDirectory($src);
        $stub = "<?php Phar::mapPhar(); include 'phar://" . basename($dest) . "/plugin.yml'; __HALT_COMPILER(); ?>";
        $phar->setStub($stub);
        $phar->stopBuffering();
        echo "Built $dest\n";
        ?>
        """
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.php') as tf:
            tf.write(script)
            phpfile = tf.name
        try:
            # Create process
            import subprocess
            cmd = [php, '-d', 'phar.readonly=0', phpfile]
            self._log('Running: ' + ' '.join(cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:  # type: ignore
                self._log(line.rstrip())
            rc = p.wait()
            self._log(f"Exit code: {rc}")
            self._done()
        except Exception as e:
            self._log("Error: "+str(e))
            self._done()
        finally:
            try: os.remove(phpfile)
            except Exception: pass

    def _log(self, s):
        def add():
            self.log.appendPlainText(s)
        QTimer.singleShot(0, add)

    def _done(self):
        QTimer.singleShot(0, self.progress.hide)


class PharExtractor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extract .phar (PHP required)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        row = QHBoxLayout()
        self.file = QLineEdit(); self.file.setPlaceholderText(".phar file")
        b1 = soft_button("Browse…"); b1.clicked.connect(self.choose_file)
        row.addWidget(self.file); row.addWidget(b1)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        self.dest = QLineEdit(); self.dest.setPlaceholderText("Destination folder")
        b2 = soft_button("Choose…"); b2.clicked.connect(self.choose_dest)
        row2.addWidget(self.dest); row2.addWidget(b2)
        lay.addLayout(row2)
        self.progress = QProgressBar(); self.progress.setRange(0,0); self.progress.hide()
        lay.addWidget(self.progress)
        go = soft_button("Extract")
        go.clicked.connect(self.run)
        lay.addWidget(go)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.log)

    def choose_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select .phar", filter="PHAR (*.phar)")
        if f:
            self.file.setText(f)

    def choose_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Select destination")
        if d:
            self.dest.setText(d)

    def run(self):
        file = self.file.text().strip(); dest = self.dest.text().strip()
        if not file or not dest:
            QMessageBox.warning(self, "Missing", "Choose a .phar file and destination folder.")
            return
        self.progress.show()
        threading.Thread(target=self._extract, args=(file, dest), daemon=True).start()

    def _extract(self, file, dest):
        php = os.environ.get("PHP", "php")
        script = f"""
        <?php
        error_reporting(E_ALL); ini_set('display_errors', 1);
        $file = '{file}'; $dest = '{dest}';
        $phar = new Phar($file);
        $phar->extractTo($dest, null, true);
        echo "Extracted to $dest\n";
        ?>
        """
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.php') as tf:
            tf.write(script)
            phpfile = tf.name
        try:
            import subprocess
            cmd = [php, phpfile]
            self._log('Running: ' + ' '.join(cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:  # type: ignore
                self._log(line.rstrip())
            p.wait()
            self._done()
        except Exception as e:
            self._log("Error: "+str(e)); self._done()
        finally:
            try: os.remove(phpfile)
            except Exception: pass

    def _log(self, s):
        QTimer.singleShot(0, lambda: self.log.appendPlainText(s))
    def _done(self):
        QTimer.singleShot(0, self.progress.hide)


class ApiInjector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Injector (plugin.yml)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.path = QLineEdit(); self.path.setPlaceholderText("plugin.yml path")
        b = soft_button("Browse…"); b.clicked.connect(self.choose)
        r.addWidget(self.path); r.addWidget(b)
        lay.addLayout(r)
        r2 = QHBoxLayout()
        self.api = QLineEdit(); self.api.setPlaceholderText("API version(s), e.g. 5.0.0 or 4.0.0,5.0.0")
        r2.addWidget(QLabel("api:")); r2.addWidget(self.api)
        lay.addLayout(r2)
        go = soft_button("Inject/Update")
        go.clicked.connect(self.run)
        lay.addWidget(go)
        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.out)

    def choose(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select plugin.yml", filter="YAML (*.yml)")
        if f:
            self.path.setText(f)

    def run(self):
        if yaml is None:
            QMessageBox.critical(self, "pyyaml missing", "Install pyyaml: pip install pyyaml")
            return
        path = self.path.text().strip(); apistr = self.api.text().strip()
        if not path or not apistr:
            QMessageBox.warning(self, "Missing", "Select plugin.yml and enter api version(s).")
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            versions = [v.strip() for v in apistr.split(',') if v.strip()]
            data['api'] = versions if len(versions) > 1 else versions[0]
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
            self.out.appendPlainText(f"Updated api: {data['api']}")
        except Exception as e:
            self.out.appendPlainText("Error: "+str(e))


class CrashdumpParser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crashdump Parser (PocketMine JSON)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.path = QLineEdit(); self.path.setPlaceholderText("Select crashdump .json")
        b = soft_button("Open…"); b.clicked.connect(self.choose)
        r.addWidget(self.path); r.addWidget(b)
        lay.addLayout(r)
        self.view = QPlainTextEdit(); self.view.setReadOnly(True)
        self.view.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.view)

    def choose(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open crashdump JSON", filter="JSON (*.json)")
        if f:
            self.path.setText(f)
            self.run(f)

    def run(self, f):
        try:
            data = json.load(open(f, 'r', encoding='utf-8'))
            lines = []
            err = data.get('error', {})
            lines.append("=== Error ===")
            lines.append(f"Type: {err.get('type')}  Message: {err.get('message')}")
            if 'file' in err:
                lines.append(f"File: {err.get('file')}:{err.get('line')}")
            trace = data.get('trace', [])
            lines.append("\n=== Trace ===")
            for i, t in enumerate(trace):
                lines.append(f"#{i} {t.get('file','?')}:{t.get('line','?')} -> {t.get('class','')}::{t.get('function','')}")
            sysinfo = data.get('system', {})
            lines.append("\n=== System ===")
            lines.append(f"PHP: {sysinfo.get('php')}  OS: {sysinfo.get('os')}  PMMP: {sysinfo.get('pocketmine')}")
            self.view.setPlainText('\n'.join(lines))
        except Exception as e:
            self.view.setPlainText("Error: "+str(e))


class PMFDecoder(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Decode .pmf (basic)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.path = QLineEdit(); self.path.setPlaceholderText("Select .pmf file")
        b = soft_button("Open…"); b.clicked.connect(self.choose)
        r.addWidget(self.path); r.addWidget(b)
        lay.addLayout(r)
        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.out)

    def choose(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open .pmf", filter="PMF (*.pmf)")
        if f:
            self.path.setText(f)
            self.run(f)

    def run(self, f):
        try:
            with open(f, 'rb') as fh:
                data = fh.read()
            head = data[:64]
            self.out.setPlainText(
                f"Size: {len(data)} bytes\nHead (hex): {head.hex()}\n\n(Note) This is a lightweight inspector that shows size and header bytes.\nIf you share the format spec, we can parse fields precisely.)"
            )
        except Exception as e:
            self.out.setPlainText("Error: "+str(e))


class SkeletonGenerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Skeleton Plugin")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        grid = QGridLayout()
        self.name = QLineEdit(); self.author = QLineEdit(); self.version = QLineEdit('1.0.0')
        self.api = QLineEdit('5.0.0')
        grid.addWidget(QLabel("Name"),0,0); grid.addWidget(self.name,0,1)
        grid.addWidget(QLabel("Author"),1,0); grid.addWidget(self.author,1,1)
        grid.addWidget(QLabel("Version"),2,0); grid.addWidget(self.version,2,1)
        grid.addWidget(QLabel("API"),3,0); grid.addWidget(self.api,3,1)
        lay.addLayout(grid)
        r = QHBoxLayout()
        self.dest = QLineEdit(); self.dest.setPlaceholderText("Destination folder (will create subfolder)")
        b = soft_button("Choose…"); b.clicked.connect(self.choose)
        r.addWidget(self.dest); r.addWidget(b)
        lay.addLayout(r)
        go = soft_button("Generate")
        go.clicked.connect(self.run)
        lay.addWidget(go)
        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.out)

    def choose(self):
        d = QFileDialog.getExistingDirectory(self, "Destination root")
        if d: self.dest.setText(d)

    def run(self):
        name = self.name.text().strip(); author = self.author.text().strip()
        version = self.version.text().strip(); api = self.api.text().strip()
        root = self.dest.text().strip()
        if not (name and author and version and api and root):
            QMessageBox.warning(self, "Missing", "Fill all fields and choose destination.")
            return
        plugdir = Path(root)/name
        (plugdir/"src"/name).mkdir(parents=True, exist_ok=True)
        (plugdir/"resources").mkdir(exist_ok=True)
        plugin_yml = {
            'name': name,
            'main': f"{name}\\Main",
            'version': version,
            'api': api,
            'author': author,
            'description': f"Skeleton plugin {name}"
        }
        (plugdir/"plugin.yml").write_text(yaml.safe_dump(plugin_yml, sort_keys=False) if yaml else
                                            f"name: {name}\nmain: {name}\\\\Main\nversion: {version}\napi: {api}\nauthor: {author}\n", encoding='utf-8')
        php_main = f'''<?php\n\nnamespace {name};\n\nuse pocketmine\\plugin\\PluginBase;\nuse pocketmine\\event\\Listener;\n\nclass Main extends PluginBase implements Listener {{\n    protected function onEnable() : void {{\n        $this->getLogger()->info("{name} enabled!");\n    }}\n}}\n'''
        (plugdir/"src"/name/"Main.php").write_text(php_main, encoding='utf-8')
        self.out.appendPlainText(f"Created skeleton at {plugdir}")


class PoggitSearch(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Poggit Search")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        self.q = QLineEdit(); self.q.setPlaceholderText("Search query e.g. economy")
        lay.addWidget(self.q)
        btn = soft_button("Open in browser")
        btn.clicked.connect(self.open)
        lay.addWidget(btn)

    def open(self):
        q = self.q.text().strip()
        if not q: return
        webbrowser.open(f"https://poggit.pmmp.io/p?q={q}")


class MotdGenerator(QDialog):
    COLORS = [
        '§0','§1','§2','§3','§4','§5','§6','§7','§8','§9','§a','§b','§c','§d','§e','§f',
        '§l','§o','§n','§m','§r'
    ]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MOTD Generator")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        self.text = QLineEdit(); self.text.setPlaceholderText("Enter MOTD text")
        lay.addWidget(self.text)
        grid = QGridLayout()
        for i, c in enumerate(self.COLORS):
            b = soft_button(c)
            b.setMinimumHeight(32)
            b.clicked.connect(lambda _, t=c: self.insert(t))
            grid.addWidget(b, i//7, i%7)
        lay.addLayout(grid)
        r = QHBoxLayout()
        copyb = soft_button("Copy to clipboard")
        copyb.clicked.connect(self.copy)
        r.addWidget(copyb)
        saveb = soft_button("Save to server.properties…")
        saveb.clicked.connect(self.save)
        r.addWidget(saveb)
        lay.addLayout(r)

    def insert(self, t):
        self.text.insert(t)

    def copy(self):
        QApplication.clipboard().setText(self.text.text())
        QMessageBox.information(self, "Copied", "MOTD copied to clipboard")

    def save(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open server.properties", filter="Properties (*.properties)")
        if not f: return
        lines = []
        found = False
        for line in open(f, 'r', encoding='utf-8', errors='ignore'):
            if line.startswith('server-name=') or line.startswith('motd='):
                lines.append('motd='+self.text.text()+"\n"); found = True
            else:
                lines.append(line)
        if not found:
            lines.append('motd='+self.text.text()+"\n")
        open(f, 'w', encoding='utf-8').writelines(lines)
        QMessageBox.information(self, "Saved", "Updated motd in server.properties")


class BedrockPinger(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ping Bedrock Server (UDP 19132)")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.host = QLineEdit('127.0.0.1'); self.port = QSpinBox(); self.port.setRange(1,65535); self.port.setValue(19132)
        r.addWidget(QLabel("Host")); r.addWidget(self.host); r.addWidget(QLabel("Port")); r.addWidget(self.port)
        lay.addLayout(r)
        btn = soft_button("Ping")
        btn.clicked.connect(self.ping)
        lay.addWidget(btn)
        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.out)

    def ping(self):
        host = self.host.text().strip(); port = int(self.port.value())
        try:
            MAGIC = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(3.0)
            t = int(time.time()*1000)
            pkt = b"\x01" + struct.pack(">Q", t) + MAGIC + struct.pack(">Q", uuid.getnode())
            s.sendto(pkt, (host, port))
            data, _ = s.recvfrom(4096)
            if data and data[0] == 0x1C:
                # response format contains server name string after magic
                txt = data[35:].decode('utf-8', errors='ignore')
                parts = txt.split(';')
                # Expected: MCPE;MOTD;protocol;version;online;max;serverId;level;gamemode;?;port;portv6
                info = {
                    'brand': parts[0] if len(parts)>0 else '',
                    'motd': parts[1] if len(parts)>1 else '',
                    'protocol': parts[2] if len(parts)>2 else '',
                    'version': parts[3] if len(parts)>3 else '',
                    'players': f"{parts[4]}/{parts[5]}" if len(parts)>5 else '',
                    'level': parts[7] if len(parts)>7 else '',
                }
                self.out.setPlainText("\n".join([f"{k}: {v}" for k,v in info.items()]))
            else:
                self.out.setPlainText("Unexpected reply")
        except Exception as e:
            self.out.setPlainText("Error: "+str(e))


class ConfigEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Config Editor")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.path = QLineEdit(); self.path.setPlaceholderText("Open any .yml/.json/.txt …")
        openb = soft_button("Open…"); openb.clicked.connect(self.open)
        saveb = soft_button("Save")
        saveb.clicked.connect(self.save)
        r.addWidget(self.path); r.addWidget(openb); r.addWidget(saveb)
        lay.addLayout(r)
        self.edit = QPlainTextEdit(); self.edit.setStyleSheet("background:#0e0e0f; border-radius:8px; font-family: Consolas, 'Fira Code', monospace;")
        lay.addWidget(self.edit)

    def open(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open file")
        if f:
            self.path.setText(f)
            self.edit.setPlainText(Path(f).read_text(encoding='utf-8', errors='ignore'))

    def save(self):
        f = self.path.text().strip()
        if not f:
            f, _ = QFileDialog.getSaveFileName(self, "Save as")
            if not f: return
            self.path.setText(f)
        Path(f).write_text(self.edit.toPlainText(), encoding='utf-8')
        QMessageBox.information(self, "Saved", f"Saved {f}")


class ServerManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Server Manager & Live Console")
        self.setStyleSheet("background:#121212; color:#eaeaea;")
        self.proc = None
        lay = QVBoxLayout(self)
        r = QHBoxLayout()
        self.cwd = QLineEdit(); self.cwd.setPlaceholderText("PocketMine server folder (where start.sh/cmd or bin/php exists)")
        choose = soft_button("Choose…"); choose.clicked.connect(self.choose)
        r.addWidget(self.cwd); r.addWidget(choose)
        lay.addLayout(r)
        r2 = QHBoxLayout()
        self.cmd = QLineEdit("./start.sh")
        r2.addWidget(QLabel("Start command:")); r2.addWidget(self.cmd)
        lay.addLayout(r2)
        r3 = QHBoxLayout()
        self.startb = soft_button("Start"); self.startb.clicked.connect(self.start)
        self.stopb = soft_button("Stop"); self.stopb.clicked.connect(self.stop)
        r3.addWidget(self.startb); r3.addWidget(self.stopb)
        lay.addLayout(r3)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#0e0e0f; border-radius:8px;")
        lay.addWidget(self.log)
        r4 = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("Type command and press Enter")
        self.input.returnPressed.connect(self.send)
        r4.addWidget(self.input)
        lay.addLayout(r4)

    def choose(self):
        d = QFileDialog.getExistingDirectory(self, "Select server folder")
        if d: self.cwd.setText(d)

    def start(self):
        if self.proc is not None:
            QMessageBox.information(self, "Running", "Server already running")
            return
        try:
            import subprocess
            self.log.clear()
            self.proc = subprocess.Popen(self.cmd.text(), cwd=self.cwd.text() or None,
                                         shell=True, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         text=True, bufsize=1)
            threading.Thread(target=self._reader, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.proc = None

    def _reader(self):
        assert self.proc is not None
        for line in self.proc.stdout:  # type: ignore
            QTimer.singleShot(0, lambda s=line: self.log.appendPlainText(s.rstrip()))
        rc = self.proc.wait()
        QTimer.singleShot(0, lambda: self.log.appendPlainText(f"\n[Process exited {rc}]"))
        self.proc = None

    def send(self):
        if self.proc and self.proc.stdin:
            cmd = self.input.text() + "\n"
            try:
                self.proc.stdin.write(cmd)
                self.proc.stdin.flush()
            except Exception:
                pass
            self.input.clear()

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass


# -----------------------------
# Main Window
# -----------------------------

class PocketMineToolbox(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PocketMine Toolbox – PyQt6")
        self.resize(980, 700)
        self.setStyleSheet("background-color: #0f1115; color: #eaeaea; font-family: 'Segoe UI', Roboto, sans-serif;")

        outer = QHBoxLayout(self)
        # Left nav
        nav = QVBoxLayout()
        title = QLabel("Phrqndys Toolbox")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        nav.addWidget(title)

        self.tools = [
            ("Create .phar", PharBuilder),
            ("Extract .phar", PharExtractor),
            ("API Injector", ApiInjector),
            ("Crashdump Parser", CrashdumpParser),
            ("Decode .pmf", PMFDecoder),
            ("Generate skeleton plugin", SkeletonGenerator),
            ("Poggit Search", PoggitSearch),
            ("MOTD Generator", MotdGenerator),
            ("Ping server", BedrockPinger),
            ("Config Editor", ConfigEditor),
            ("Server Manager / Live Console", ServerManager),
        ]

        nav_box = QVBoxLayout()
        for text, cls in self.tools:
            b = soft_button(text)
            b.clicked.connect(lambda _, c=cls: self.open_tool(c))
            b.installEventFilter(self)
            nav_box.addWidget(b)
        nav_box.addStretch(1)

        nav_frame = QFrame(); nav_frame.setStyleSheet("background:#121419; border-radius:16px;")
        nav_frame.setLayout(nav_box)
        nav.addWidget(nav_frame)
        outer.addLayout(nav, 1)

        # Right info panel
        self.info = QPlainTextEdit()
        self.info.setReadOnly(True)
        self.info.setPlainText(
            "Welcome! Choose a tool on the left.\n\n" \
            "Tips:\n- .phar tools require PHP installed (set PHP env var if needed).\n" \
            "- Server Manager lets you run PocketMine and send commands.\n" \
            "- Ping uses Bedrock UDP discovery to show server info.\n" \
            "- API Injector edits plugin.yml api field.\n"
        )
        self.info.setStyleSheet("background:#0b0d11; border-radius:16px;")
        outer.addWidget(self.info, 2)

    def eventFilter(self, source, event):
        if isinstance(source, QPushButton):
            if event.type() == event.Type.Enter:
                Animator.pulse(source, 1.03)
        return super().eventFilter(source, event)

    def open_tool(self, cls):
        dlg = cls(self)
        dlg.resize(700, 520)
        dlg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PocketMineToolbox()
    win.show()
    sys.exit(app.exec())
