#!/usr/bin/env python3
"""
Simple Crosshair overlay + settings GUI.

Requirements:
    pip install pyqt5

Build to exe:
    pyinstaller --onefile --noconsole simple_crosshair.py
"""

import sys, os, ctypes, configparser, threading
from ctypes import wintypes
from PyQt5 import QtWidgets, QtGui, QtCore

CONFIG_FILE = "config.ini"
DEFAULT_HOTKEY = "ctrl+numpad_add"
DEFAULT_TYPE = "dot"
DEFAULT_COLOR = "green"
DEFAULT_SIZE = 4
CLICK_THROUGH = True

# Win32 constants
user32 = ctypes.windll.user32
MOD_NONE=0x0; MOD_ALT=0x1; MOD_CONTROL=0x2; MOD_SHIFT=0x4; MOD_WIN=0x8
WM_HOTKEY=0x0312
VK_MAP={chr(c):c for c in range(0x41,0x5B)}
VK_MAP.update({str(d):ord(str(d)) for d in range(10)})
VK_MAP.update({"numpad_add":0x6B,"add":0x6B,"plus":0xBB,"space":0x20})

# Color map
COLOR_MAP={
    "green":QtGui.QColor(0,255,0),
    "red":QtGui.QColor(255,0,0),
    "yellow":QtGui.QColor(255,255,0),
    "purple":QtGui.QColor(128,0,128),
}

# ---------- Config ----------
def read_config():
    cfg=configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        cfg["hotkey"]={"toggle":DEFAULT_HOTKEY}
        cfg["crosshair"]={"type":DEFAULT_TYPE,"color":DEFAULT_COLOR,"size":str(DEFAULT_SIZE)}
        with open(CONFIG_FILE,"w") as f: cfg.write(f)
    else:
        cfg.read(CONFIG_FILE)
        if "hotkey" not in cfg: cfg["hotkey"]={"toggle":DEFAULT_HOTKEY}
        if "crosshair" not in cfg: cfg["crosshair"]={"type":DEFAULT_TYPE,"color":DEFAULT_COLOR,"size":str(DEFAULT_SIZE)}
    return cfg

def write_config(cfg):
    with open(CONFIG_FILE,"w") as f: cfg.write(f)

# ---------- Parse hotkey ----------
def normalize_token(tok:str)->str: return tok.strip().lower().replace(" ","_")
def parse_hotkey_string(s:str):
    if not s: return None,None
    parts=[normalize_token(p) for p in s.split("+")]
    mods,key_tok=0,None
    for p in parts:
        if p in ("ctrl","control"): mods|=MOD_CONTROL
        elif p=="alt": mods|=MOD_ALT
        elif p=="shift": mods|=MOD_SHIFT
        elif p in ("win","lwin","rwin"): mods|=MOD_WIN
        else: key_tok=p
    if key_tok is None: return None,None
    vk=VK_MAP.get(key_tok)
    if vk is None and len(key_tok)==1: vk=ord(key_tok.upper())
    return (mods,vk) if vk is not None else (None,None)

# ---------- Overlay ----------
class SimpleCrosshair(QtWidgets.QWidget):
    def __init__(self,cfg):
        super().__init__(None,QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
        self.cfg=cfg
        self.setObjectName("Simple_Crosshair")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(self.get_window_size(),self.get_window_size())
        self.setWindowFlag(QtCore.Qt.Tool)
        self.center_on_screen()
    def get_dot_size(self): return int(self.cfg["crosshair"].get("size",DEFAULT_SIZE))
    def get_window_size(self):
        t=self.cfg["crosshair"].get("type","dot")
        s=self.get_dot_size()
        if t=="dot": return s+2
        else: return min(s,10)+2  # cross max 10px
    def get_color(self): return COLOR_MAP.get(self.cfg["crosshair"].get("color","green"),QtGui.QColor(0,255,0))
    def get_type(self): return self.cfg["crosshair"].get("type","dot")
    def center_on_screen(self):
        screen=QtWidgets.QApplication.primaryScreen().geometry()
        x=(screen.width()-self.width())//2
        y=(screen.height()-self.height())//2
        self.move(x,y)
    def showEvent(self,event):
        hwnd=int(self.winId());self._make_topmost(hwnd)
        if CLICK_THROUGH:self._make_click_through(hwnd)
        super().showEvent(event)
    def _make_click_through(self,hwnd):
        GWL_EXSTYLE=-20;WS_EX_LAYERED=0x00080000;WS_EX_TRANSPARENT=0x00000020;WS_EX_NOACTIVATE=0x08000000
        cur=user32.GetWindowLongW(hwnd,GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd,GWL_EXSTYLE,cur|WS_EX_LAYERED|WS_EX_TRANSPARENT|WS_EX_NOACTIVATE)
    def _make_topmost(self,hwnd):
        HWND_TOPMOST=-1;SWP_NOMOVE=0x2;SWP_NOSIZE=0x1;SWP_SHOWWINDOW=0x40
        user32.SetWindowPos(hwnd,HWND_TOPMOST,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_SHOWWINDOW)
    def paintEvent(self,event):
        p=QtGui.QPainter(self);p.setRenderHint(QtGui.QPainter.Antialiasing)
        pen=QtGui.QPen(QtGui.QColor(0,0,0));pen.setWidth(1);p.setPen(pen)
        p.setBrush(self.get_color())
        t=self.get_type();s=self.get_dot_size();win=self.width();h=self.height()
        cx=win//2;cy=h//2
        if t=="dot":
            w=s+1;h=s+1;x=cx-w//2;y=cy-h//2;p.drawEllipse(int(x),int(y),int(w),int(h))
        elif t=="cross":
            l=min(s,10)
            # horizontal
            p.drawLine(cx-l//2,cy,cx+l//2,cy)
            # vertical
            p.drawLine(cx,cy-l//2,cx,cy+l//2)
    def update_overlay(self):
        self.setFixedSize(self.get_window_size(),self.get_window_size())
        self.center_on_screen()
        self.update()

# ---------- Hotkey listener ----------
class HotkeyListener(threading.Thread):
    def __init__(self,hotkey_string,callback):
        super().__init__(daemon=True);self.hotkey_string=hotkey_string;self.callback=callback;self._hotkey_id=1
    def run(self):
        mods,vk=parse_hotkey_string(self.hotkey_string)
        if mods is None or vk is None:return
        if not user32.RegisterHotKey(None,self._hotkey_id,mods,vk):print("Hotkey registration failed");return
        msg=wintypes.MSG()
        while True:
            b=user32.GetMessageW(ctypes.byref(msg),None,0,0)
            if b==0: break
            if msg.message==WM_HOTKEY:
                try:self.callback()
                except: pass
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        user32.UnregisterHotKey(None,self._hotkey_id)

# ---------- Settings GUI ----------
class SettingsWindow(QtWidgets.QWidget):
    def __init__(self,overlay,cfg):
        super().__init__()
        self.overlay=overlay;self.cfg=cfg
        self.setWindowTitle("Simple Crosshair Settings")
        self.setFixedSize(300,300)
        self.setStyleSheet("background-color:#B0B0B0;")
        layout=QtWidgets.QVBoxLayout()
        # Type
        self.type_group=QtWidgets.QButtonGroup()
        layout.addWidget(QtWidgets.QLabel("Crosshair Type:"))
        for t in ["dot","cross"]:
            rb=QtWidgets.QRadioButton(t.capitalize())
            if self.cfg["crosshair"].get("type",DEFAULT_TYPE)==t: rb.setChecked(True)
            self.type_group.addButton(rb);rb.setObjectName(t)
            layout.addWidget(rb)
        # Color
        self.color_group=QtWidgets.QButtonGroup()
        layout.addWidget(QtWidgets.QLabel("Color:"))
        for color in ["green","red","yellow","purple"]:
            rb=QtWidgets.QRadioButton(color.capitalize())
            if self.cfg["crosshair"].get("color",DEFAULT_COLOR)==color: rb.setChecked(True)
            self.color_group.addButton(rb);rb.setObjectName(color)
            layout.addWidget(rb)
        # Size
        self.size_group=QtWidgets.QButtonGroup()
        layout.addWidget(QtWidgets.QLabel("Size:"))
        for s in [2,4,6,8,10]:
            rb=QtWidgets.QRadioButton(str(s))
            if int(self.cfg["crosshair"].get("size",DEFAULT_SIZE))==s: rb.setChecked(True)
            self.size_group.addButton(rb);rb.setObjectName(str(s))
            layout.addWidget(rb)
        # Hotkey
        layout.addWidget(QtWidgets.QLabel("Hotkey (e.g., ctrl+numpad_add):"))
        self.hotkey_input=QtWidgets.QLineEdit(self.cfg["hotkey"].get("toggle",DEFAULT_HOTKEY))
        layout.addWidget(self.hotkey_input)
        # Save button
        save_btn=QtWidgets.QPushButton("Save & Apply")
        save_btn.clicked.connect(self.apply_settings)
        layout.addWidget(save_btn)
        self.setLayout(layout)
    def apply_settings(self):
        # Type
        for rb in self.type_group.buttons():
            if rb.isChecked(): self.cfg["crosshair"]["type"]=rb.objectName()
        # Color
        for rb in self.color_group.buttons():
            if rb.isChecked(): self.cfg["crosshair"]["color"]=rb.objectName()
        # Size
        for rb in self.size_group.buttons():
            if rb.isChecked(): self.cfg["crosshair"]["size"]=rb.objectName()
        # Hotkey
        self.cfg["hotkey"]["toggle"]=self.hotkey_input.text().strip()
        write_config(self.cfg)
        self.overlay.update_overlay()
        QtWidgets.QMessageBox.information(self,"Saved","Settings applied!")

# ---------- Main ----------
def main():
    if sys.platform!="win32": return
    app=QtWidgets.QApplication(sys.argv)
    cfg=read_config()
    overlay=SimpleCrosshair(cfg)
    overlay.show()
    # Hotkey
    class ToggleObj(QtCore.QObject):
        toggle_signal=QtCore.pyqtSignal()
    toggler=ToggleObj()
    toggler.toggle_signal.connect(lambda: overlay.setVisible(not overlay.isVisible()))
    def on_hotkey(): toggler.toggle_signal.emit()
    listener=HotkeyListener(cfg["hotkey"].get("toggle",DEFAULT_HOTKEY),on_hotkey)
    listener.start()
    # Settings GUI
    settings=SettingsWindow(overlay,cfg)
    settings.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
