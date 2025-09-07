import sys, os, glob, json, re
import time
import win32api, win32con
import pygetwindow as gw
import pyautogui
import keyboard
from mutagen.easyid3 import EasyID3
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit, QLabel, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox, QDialog,
    QDialogButtonBox, QGridLayout
)
from PySide6.QtCore import Qt
import ctypes

CONFIG = os.path.expanduser("~/.freq_vk_config.json")
ALL_FREQS = [
    "18-21", "20-22", "21-23", "22-25", "23-26", "25-28", "26-29",
    "28-31", "29-33", "31-35", "33-37", "35-39", "37-41",
    "39-44", "41-46", "52-58"
]

RENDER_FREQS = [
    "23-26", "25-28", "26-29", "28-31", "29-33", "31-35",
    "33-37", "35-39", "37-41", "39-44", "41-46"
]

VK_CODE = {
    'SHIFT': 0x10, 'CTRL': 0x11, 'ALT': 0x12, 'ENTER': 0x0D, 'UP': 0x26, 'TAB': 0x09,
    'M': 0x4D, 'R': 0x52, 'S': 0x53, '-': 0xBD,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39
}

PUL = ctypes.POINTER(ctypes.c_ulong)
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MAPVK_VK_TO_VSC = 0

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ki", KEYBDINPUT)]

def send_key_scan(vk, down=True):
    scan = ctypes.windll.user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    flags = KEYEVENTF_SCANCODE
    if not down:
        flags |= KEYEVENTF_KEYUP
    ki = KEYBDINPUT(0, scan, flags, 0, ctypes.pointer(ctypes.c_ulong(0)))
    inp = INPUT(INPUT_KEYBOARD, ki)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

def key(vk, up=False):
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP if up else 0, 0)

def press_key(vk):
    key(vk); time.sleep(0.05); key(vk, up=True); time.sleep(0.05)

def press_hotkey(*vks):
    for vk in vks:
        key(vk)
    time.sleep(0.05)
    for vk in reversed(vks):
        key(vk, up=True)
    time.sleep(0.05)

def write_text(text):
    for ch in text:
        if ch.isdigit():
            press_key(VK_CODE[ch])
        elif ch == '-':
            press_key(VK_CODE['-'])
        elif ch.upper() in VK_CODE:
            press_key(VK_CODE[ch.upper()])
        else:
            print(f"Неизвестный символ: {ch}")

def load_cfg():
    if os.path.exists(CONFIG):
        cfg = json.load(open(CONFIG, "r", encoding="utf-8"))
    else:
        cfg = {}
    cfg.setdefault("folder", "")
    cfg.setdefault("freqs", [])
    cfg.setdefault("tag_handler", "")
    cfg.setdefault("tag_production", "")
    cfg.setdefault("brackets", "round")
    cfg.setdefault("delay", "60")
    return cfg

def save_cfg(cfg):
    json.dump(cfg, open(CONFIG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def wrap_tag(tag, brackets):
    return f"[{tag}]" if brackets == "square" else f"({tag})"

def extract_freq_from_filename(filename):
    match = re.search(r'(\d{2}-\d{2}(?:[.,]\d{2})*)', filename)
    return match.group(1) if match else None

def edit_meta(folder, _, artist, title, handler, production, brackets):
    count = 0
    files = glob.glob(os.path.join(folder, "*.mp3"))
    for fn in files:
        freq = extract_freq_from_filename(os.path.basename(fn))
        if not freq:
            print(f"❌ Частота не найдена в имени: {fn}")
            continue
        try:
            audio = EasyID3(fn)
        except:
            audio = EasyID3()
        audio["title"] = f"{title} {wrap_tag(handler, brackets)}"
        artist_full = f"({freq}Hz) {artist} {wrap_tag(production, brackets)}".strip()
        audio["artist"] = artist_full
        audio["genre"] = ", ".join([wrap_tag(handler, brackets), wrap_tag(production, brackets)])
        audio.save(fn)
        count += 1
    return count

def focus_fl_studio():
    try:
        for w in gw.getWindowsWithTitle("FL Studio"):
            if w.title and "FL Studio" in w.title:
                try:
                    w.minimize()
                    w.restore()
                    w.activate()
                except:
                    pass
                time.sleep(1)
                return True
        raise Exception("Not found")
    except:
        QMessageBox.critical(None, "Ошибка", "FL Studio не запущена или окно не найдено")
        return False

def render_via_route(freqs, delay_sec):
    if not focus_fl_studio(): 
        return
    for freq in freqs:
        press_hotkey(VK_CODE['CTRL'], VK_CODE['R'])
        time.sleep(1)
        write_text(freq)
        time.sleep(0.3)
        press_key(VK_CODE['TAB'])
        time.sleep(0.3)
        press_key(VK_CODE['M'])
        time.sleep(0.3)
        press_key(VK_CODE['ENTER'])
        time.sleep(0.5)
        press_key(VK_CODE['ENTER'])
        time.sleep(delay_sec)
        pyautogui.click(x=1280, y=300)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        keyboard.press('shift')
        keyboard.press_and_release('up')
        keyboard.release('shift')
        time.sleep(0.2)

class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_cfg()
        self.init_ui()

    def init_ui(self):
        self.folder = QLineEdit(self.cfg.get("folder", ""))
        btn_folder = QPushButton("Папка")
        btn_folder.clicked.connect(self.choose_folder)

        self.freq_lbl = QLabel(f"Частот выбрано: {len(self.cfg.get('freqs', []))}")
        btn_freq = QPushButton("Выбрать частоты")
        btn_freq.clicked.connect(self.choose_freq)

        self.delay_input = QLineEdit(self.cfg.get("delay", "60"))
        delay_lbl = QLabel("Задержка после рендера (сек):")

        self.artist = QLineEdit()
        self.title = QLineEdit()

        btn_tags = QPushButton("Изменить теги")
        btn_tags.clicked.connect(self.edit_tags)

        btn_meta = QPushButton("Старт")
        btn_meta.clicked.connect(self.run_meta)

        btn_render = QPushButton("Рендер FL (разработка)")
        btn_render.clicked.connect(self.run_render_manual)

        lay = QVBoxLayout()
        lay.addLayout(self.row(self.folder, btn_folder))
        lay.addLayout(self.row(self.freq_lbl, btn_freq))
        lay.addLayout(self.row(delay_lbl, self.delay_input))
        lay.addLayout(self.row(QLabel("Исполнитель:"), self.artist))
        lay.addLayout(self.row(QLabel("Название:"), self.title))
        lay.addWidget(btn_tags)
        lay.addWidget(btn_meta)
        lay.addWidget(btn_render)
        self.setLayout(lay)
        self.setWindowTitle("Track Renamer by #DeadRazer")
        self.resize(400, 400)

    def row(self, *widgets):
        h = QHBoxLayout()
        for w in widgets:
            h.addWidget(w)
        return h

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбрать папку", self.folder.text())
        if folder:
            self.folder.setText(folder)
            self.cfg["folder"] = folder
            save_cfg(self.cfg)

    def choose_freq(self):
        dlg = FrequencyDialog(self, self.cfg.get("freqs", []))
        if dlg.exec():
            self.cfg["freqs"] = dlg.get_selected()
            self.freq_lbl.setText(f"Частот выбрано: {len(self.cfg['freqs'])}")
            save_cfg(self.cfg)

    def edit_tags(self):
        dlg = TagDialog(self, self.cfg.get("tag_handler", ""), self.cfg.get("tag_production", ""), self.cfg.get("brackets", "round"))
        if dlg.exec():
            h, p, b = dlg.get_values()
            self.cfg.update({"tag_handler": h, "tag_production": p, "brackets": b})
            save_cfg(self.cfg)

    def run_meta(self):
        cnt = edit_meta(
            self.folder.text(),
            self.cfg.get("freqs", []),
            self.artist.text(),
            self.title.text(),
            self.cfg.get("tag_handler", ""),
            self.cfg.get("tag_production", ""),
            self.cfg.get("brackets", "round")
        )
        QMessageBox.information(self, "Готово", f"Обработано файлов: {cnt}")

    def run_render_manual(self):
        try:
            delay = int(self.delay_input.text())
        except:
            delay = 60
        self.cfg["delay"] = str(delay)
        save_cfg(self.cfg)
        render_via_route(RENDER_FREQS, delay)

class FrequencyDialog(QDialog):
    def __init__(self, parent, selected):
        super().__init__(parent)
        self.setWindowTitle("Выбрать частоты")
        grid = QGridLayout()
        self.boxes = []
        for idx, f in enumerate(ALL_FREQS):
            cb = QCheckBox(f)
            cb.setChecked(f in selected)
            grid.addWidget(cb, idx//4, idx%4)
            self.boxes.append(cb)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_selected(self):
        return [cb.text() for cb in self.boxes if cb.isChecked()]

class TagDialog(QDialog):
    def __init__(self, parent, handler, prod, brackets):
        super().__init__(parent)
        self.setWindowTitle("Редактировать теги")
        self.hi = QLineEdit(handler)
        self.pi = QLineEdit(prod)
        self.rb = QCheckBox("Круглые скобки")
        self.sb = QCheckBox("Квадратные")
        self.rb.setChecked(brackets == "round")
        self.sb.setChecked(brackets == "square")
        self.rb.stateChanged.connect(self.sync)
        self.sb.stateChanged.connect(self.sync)
        grid = QVBoxLayout()
        grid.addWidget(QLabel("Тег обработчика:"))
        grid.addWidget(self.hi)
        grid.addWidget(QLabel("Продакшн:"))
        grid.addWidget(self.pi)
        grid.addWidget(self.rb)
        grid.addWidget(self.sb)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        grid.addWidget(btns)
        self.setLayout(grid)

    def sync(self):
        if self.sender() == self.rb and self.rb.isChecked():
            self.sb.setChecked(False)
        if self.sender() == self.sb and self.sb.isChecked():
            self.rb.setChecked(False)

    def get_values(self):
        return self.hi.text(), self.pi.text(), "round" if self.rb.isChecked() else "square"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWin()
    w.show()
    sys.exit(app.exec())
