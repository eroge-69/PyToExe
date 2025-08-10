#!/usr/bin/env python3
"""
macro_recorder_windows.py
Windows-only macro recorder/player focused on background input sending.

Features:
- Record mouse & keyboard with timestamps and window association.
- Save/load macros (JSON) with coords relative to a target window.
- Playback with PostMessage / SendMessage attempts and SendInput fallback.
- Looping, speed control, pause/resume, emergency stop (Esc).
- Tkinter GUI: list, delete, import/export, simple editor (remove step, insert delay, toggle shift).
- Global hotkeys via pynput GlobalHotKeys.
- Logging to macro_recorder_windows.log

Dependencies:
pip install pynput pyautogui pygetwindow psutil pillow
(Uses ctypes for Win32; pywin32 is optional and not required.)
This script runs only on Windows.
"""

import os
import sys
import time
import json
import threading
import logging
import ctypes
from ctypes import wintypes
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

# Third-party
from pynput import mouse, keyboard
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab  # optional screenshot
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# Logging
LOG_FILE = "macro_recorder_windows.log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

if not sys.platform.startswith("win"):
    raise RuntimeError("This script is Windows-only by design per user's request.")

# ---------------- Win32 setup ----------------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 message constants
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

# SendInput structures for fallback synthetic input
PUL = ctypes.POINTER(ctypes.c_ulong)

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", PUL)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", PUL)]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]

SendInput = user32.SendInput

# Basic VK mapping; extendable
VK_MAP = { 'shift':0x10, 'ctrl':0x11, 'alt':0x12, 'enter':0x0D, 'esc':0x1B,
           'tab':0x09, 'left':0x25, 'up':0x26, 'right':0x27, 'down':0x28,
           'space':0x20, 'backspace':0x08 }

def vk_from_keyname(name: str) -> Optional[int]:
    if not name:
        return None
    n = name.lower()
    if n in VK_MAP:
        return VK_MAP[n]
    if len(n) == 1:
        return ord(n.upper())
    # try single-letter like 'a'
    try:
        return ord(n.upper()[0])
    except Exception:
        return None

# ---------------- Data structures ----------------
@dataclass
class Event:
    t: float
    type: str
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    pressed: Optional[bool] = None
    dx: Optional[int] = None
    dy: Optional[int] = None
    key: Optional[str] = None
    window_title: Optional[str] = None
    window_pid: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None

@dataclass
class Macro:
    name: str
    events: List[Event]
    target_match: Dict[str,Any]
    created_at: float

# ---------------- Utilities ----------------
def now_ts():
    return time.time()

def log_exc(msg="Exception"):
    logging.exception(msg)

def find_hwnd_by_match(match: Dict[str,Any]) -> Optional[int]:
    """Find hwnd by title partial match or pid using pygetwindow enumerations."""
    try:
        if not match:
            return None
        pid = match.get('pid')
        title = match.get('title')
        partial = match.get('partial', True)
        if pid:
            EnumWindows = user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            found = []
            def _enum(hwnd, lParam):
                pid_dw = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_dw))
                if pid_dw.value == int(pid):
                    found.append(hwnd)
                return True
            EnumWindows(EnumWindowsProc(_enum), 0)
            return int(found[0]) if found else None
        if title:
            for w in gw.getAllWindows():
                if not w.title:
                    continue
                if partial and title.lower() in w.title.lower():
                    return int(w._hWnd)
                if not partial and title.lower() == w.title.lower():
                    return int(w._hWnd)
    except Exception:
        log_exc("find_hwnd_by_match")
    return None

def post_mouse_message(hwnd:int, msg:int, x:int, y:int, wheel=0):
    lParam = (y << 16) | (x & 0xFFFF)
    wParam = 0
    if msg == WM_MOUSEWHEEL:
        # wheel in high word of wParam
        wParam = (wheel & 0xFFFF) << 16
    user32.PostMessageW(hwnd, msg, wParam, lParam)

def post_key_message(hwnd:int, msg:int, vk:int, scan=0):
    # lParam: repeat count (1) | scan <<16 ...
    lParam = 1 | (scan << 16)
    user32.PostMessageW(hwnd, msg, vk, lParam)

def send_key_via_sendinput(vk:int, down:bool=True):
    # minimal SendInput wrapper for keyboard
    try:
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        ki = KEYBDINPUT(vk, 0, 0 if down else KEYEVENTF_KEYUP, 0, None)
        inp = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki))
        SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    except Exception:
        log_exc("send_key_via_sendinput")

# ---------------- Recorder ----------------
class Recorder:
    def __init__(self, screenshot=False):
        self.events: List[Event] = []
        self.start_time: Optional[float] = None
        self.screenshot = screenshot
        self._mouse_listener = None
        self._keyboard_listener = None
        self.assoc_window = None
        self._stop_flag = threading.Event()

    def _ts(self):
        return (now_ts() - self.start_time) if self.start_time else 0.0

    def start(self):
        logging.info("Recording started")
        self.start_time = now_ts()
        self.events = []
        self.assoc_window = self._active_window_info()
        self._stop_flag.clear()

        def on_move(x,y):
            try:
                rx, ry = self._abs_to_rel(x,y)
                self.events.append(Event(t=self._ts(), type='mouse_move', x=rx, y=ry,
                                         window_title=self.assoc_window.get('title'), window_pid=self.assoc_window.get('pid')))
            except Exception:
                log_exc("on_move")

        def on_click(x,y,button,pressed):
            try:
                rx, ry = self._abs_to_rel(x,y)
                self.events.append(Event(t=self._ts(), type='mouse_click', x=rx, y=ry,
                                         button=str(button), pressed=pressed,
                                         window_title=self.assoc_window.get('title'), window_pid=self.assoc_window.get('pid')))
            except Exception:
                log_exc("on_click")

        def on_scroll(x,y,dx,dy):
            try:
                rx, ry = self._abs_to_rel(x,y)
                self.events.append(Event(t=self._ts(), type='mouse_scroll', x=rx, y=ry, dx=dx, dy=dy,
                                         window_title=self.assoc_window.get('title'), window_pid=self.assoc_window.get('pid')))
            except Exception:
                log_exc("on_scroll")

        def on_press(key):
            try:
                k = self._key_to_str(key)
                self.events.append(Event(t=self._ts(), type='key_down', key=k,
                                         window_title=self.assoc_window.get('title'), window_pid=self.assoc_window.get('pid')))
            except Exception:
                log_exc("on_press")

        def on_release(key):
            try:
                k = self._key_to_str(key)
                self.events.append(Event(t=self._ts(), type='key_up', key=k,
                                         window_title=self.assoc_window.get('title'), window_pid=self.assoc_window.get('pid')))
            except Exception:
                log_exc("on_release")

        self._mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self._keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self):
        logging.info("Stopping recording")
        try:
            if self._mouse_listener:
                self._mouse_listener.stop()
        except Exception:
            pass
        try:
            if self._keyboard_listener:
                self._keyboard_listener.stop()
        except Exception:
            pass
        self.start_time = None

    def save(self, path:str, name:Optional[str]=None, target_match:Optional[Dict[str,Any]]=None):
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        macro = Macro(name=name, events=self.events,
                      target_match=target_match or {"title": self.assoc_window.get('title'), "partial":True, "pid": self.assoc_window.get('pid')},
                      created_at=now_ts())
        out = {"name":macro.name, "created_at":macro.created_at, "target_match":macro.target_match,
               "events":[asdict(e) for e in macro.events]}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        logging.info("Saved macro %s (%d events) to %s", name, len(self.events), path)

    # utility methods
    def _active_window_info(self):
        win = gw.getActiveWindow()
        if not win:
            return {"title":None, "pid":None, "bbox":None}
        title = win.title
        hwnd = getattr(win, "_hWnd", None)
        pid = None
        try:
            if hwnd:
                pid_dw = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_dw))
                pid = pid_dw.value
        except Exception:
            pass
        bbox = (win.left, win.top, win.width, win.height)
        return {"title":title, "pid":pid, "bbox":bbox}

    def _abs_to_rel(self, x:int, y:int) -> Tuple[int,int]:
        try:
            bbox = self.assoc_window.get('bbox')
            if bbox:
                left, top, w, h = bbox
                return x - left, y - top
            # fallback: best-effort find window by title
            title = self.assoc_window.get('title')
            if title:
                for w in gw.getAllWindows():
                    if title.lower() in (w.title or "").lower():
                        return x - w.left, y - w.top
        except Exception:
            log_exc("_abs_to_rel")
        return x, y

    def _key_to_str(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            return str(key).split('.')[-1].strip("'")
        except Exception:
            return str(key)

# ---------------- Player ----------------
class Player:
    def __init__(self):
        self._pause = threading.Event()
        self._stop = threading.Event()
        self.speed = 1.0
        self.loop = 1
        self._thread = None
        self.force_shift = None  # None means as-recorded, True/False to force
        # hold lock for thread-safe UI interactions
        self._lock = threading.Lock()

    def play_file(self, path:str, loop:int=1, speed:float=1.0, bring_to_foreground=False):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.play_data(data, loop, speed, bring_to_foreground)

    def play_data(self, data:Dict[str,Any], loop:int=1, speed:float=1.0, bring_to_foreground=False):
        events = data.get('events', [])
        target = data.get('target_match', {})
        self.loop = loop
        self.speed = speed
        self._stop.clear()
        self._pause.clear()
        self._thread = threading.Thread(target=self._run, args=(events, target, bring_to_foreground), daemon=True)
        self._thread.start()

    def _run(self, events:List[Dict[str,Any]], target:Dict[str,Any], bring_to_foreground=False):
        logging.info("Playback started (loop=%d speed=%s)", self.loop, self.speed)
        hwnd = find_hwnd_by_match(target)
        if not hwnd:
            logging.error("Target window not found: %s", target)
            # try asking user
            if messagebox.askyesno("Window not found", "Target window not found. Do you want to attempt to pick a window now?"):
                # user picks active window
                aw = gw.getActiveWindow()
                if aw:
                    hwnd = int(getattr(aw, "_hWnd", 0))
        # main loop
        for li in range(self.loop):
            if self._stop.is_set():
                break
            last_t = 0.0
            for ev in events:
                if self._stop.is_set():
                    break
                while self._pause.is_set():
                    time.sleep(0.05)
                # timing adjust
                delta = (ev['t'] - last_t) / self.speed
                if delta > 0:
                    time.sleep(delta)
                last_t = ev['t']
                try:
                    self._perform_event(ev, hwnd, bring_to_foreground)
                except Exception:
                    log_exc("perform_event")
            time.sleep(0.02)
        logging.info("Playback finished")

    def pause(self): self._pause.set()
    def resume(self): self._pause.clear()
    def toggle_pause(self):
        if self._pause.is_set(): self.resume()
        else: self.pause()
    def stop(self): self._stop.set(); self._pause.clear()

    def _perform_event(self, ev:Dict[str,Any], hwnd:Optional[int], bring_to_foreground=False):
        typ = ev.get('type')
        x = ev.get('x'); y = ev.get('y')
        abs_xy = None
        if x is not None and y is not None:
            if hwnd:
                try:
                    w = gw.Win32Window(hwnd)
                    left = w.left; top = w.top
                    abs_xy = (left + int(x), top + int(y))
                except Exception:
                    abs_xy = (int(x), int(y))
            else:
                abs_xy = (int(x), int(y))

        # Mouse move
        if typ == 'mouse_move':
            if hwnd:
                try:
                    post_mouse_message(hwnd, WM_MOUSEMOVE, int(x), int(y))
                    return
                except Exception:
                    pass
            if abs_xy: pyautogui.moveTo(abs_xy[0], abs_xy[1], duration=0)

        # Mouse click (press/release)
        elif typ == 'mouse_click':
            btn = ev.get('button') or ''
            pressed = ev.get('pressed', False)
            btnname = 'left' if 'left' in btn.lower() else ('right' if 'right' in btn.lower() else 'middle')
            if hwnd:
                try:
                    if 'left' in btnname:
                        msg = WM_LBUTTONDOWN if pressed else WM_LBUTTONUP
                    elif 'right' in btnname:
                        msg = WM_RBUTTONDOWN if pressed else WM_RBUTTONUP
                    else:
                        msg = WM_MBUTTONDOWN if pressed else WM_MBUTTONUP
                    post_mouse_message(hwnd, msg, int(x), int(y))
                    return
                except Exception:
                    pass
            if abs_xy:
                if pressed: pyautogui.mouseDown(abs_xy[0], abs_xy[1], button=btnname)
                else: pyautogui.mouseUp(abs_xy[0], abs_xy[1], button=btnname)

        # Scroll
        elif typ == 'mouse_scroll':
            dy = ev.get('dy', 0)
            if hwnd:
                try:
                    post_mouse_message(hwnd, WM_MOUSEWHEEL, int(x), int(y), wheel=int(dy*120))
                    return
                except Exception:
                    pass
            pyautogui.scroll(int(dy), x=abs_xy[0] if abs_xy else None, y=abs_xy[1] if abs_xy else None)

        # Key events
        elif typ in ('key_down','key_up'):
            keyname = ev.get('key')
            is_down = typ == 'key_down'
            # optional force shift behavior
            if keyname and (self.force_shift is not None) and keyname.lower() == 'shift':
                # enforce global preference by ignoring recorded shift events or injecting them
                if self.force_shift is False and is_down:
                    # skip pressing shift
                    return
            if hwnd:
                vk = vk_from_keyname(keyname)
                if vk:
                    try:
                        post_key_message(hwnd, WM_KEYDOWN if is_down else WM_KEYUP, vk)
                        return
                    except Exception:
                        pass
            # fallback to SendInput/pyautogui
            vk = vk_from_keyname(keyname)
            if vk:
                try:
                    send_key_via_sendinput(vk, down=is_down)
                    return
                except Exception:
                    pass
            # final fallback to pyautogui
            if keyname:
                try:
                    if is_down: pyautogui.keyDown(keyname)
                    else: pyautogui.keyUp(keyname)
                except Exception:
                    try:
                        if not is_down: pyautogui.press(keyname)
                    except Exception:
                        log_exc("pyautogui key fallback failed")

# ---------------- GUI Manager ----------------
class MacroManagerGUI:
    def __init__(self, root, macros_dir="macros"):
        self.root = root
        self.macros_dir = macros_dir
        os.makedirs(self.macros_dir, exist_ok=True)
        self.rec = Recorder()
        self.player = Player()
        self._setup_ui()
        self._load_list()
        self._setup_hotkeys()

    def _setup_ui(self):
        r = self.root
        r.title("Macro Recorder - Windows Only")
        frm = ttk.Frame(r, padding=8); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Saved Macros:").pack(anchor=tk.W)
        self.listbox = tk.Listbox(frm, width=80, height=12); self.listbox.pack(fill=tk.BOTH, expand=True)
        btnf = ttk.Frame(frm); btnf.pack(fill=tk.X, pady=6)
        ttk.Button(btnf, text="Record (Ctrl+Alt+R)", command=self.gui_record).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Stop Record", command=self.gui_stop_record).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Play Selected (Ctrl+Alt+P)", command=self.gui_play).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Pause/Resume (Ctrl+Alt+Space)", command=self.player.toggle_pause).pack(side=tk.LEFT)
        ttk.Button(btnf, text="Stop (ESC)", command=self.player.stop).pack(side=tk.LEFT)
        mg = ttk.Frame(frm); mg.pack(fill=tk.X)
        ttk.Button(mg, text="Import", command=self.import_macro).pack(side=tk.LEFT)
        ttk.Button(mg, text="Export", command=self.export_macro).pack(side=tk.LEFT)
        ttk.Button(mg, text="Delete", command=self.delete_macro).pack(side=tk.LEFT)
        ttk.Button(mg, text="Edit (basic)", command=self.edit_macro).pack(side=tk.LEFT)
        ttk.Button(mg, text="Toggle Topmost", command=self.toggle_topmost).pack(side=tk.LEFT)

    def _load_list(self):
        self.listbox.delete(0, tk.END)
        for f in sorted(os.listdir(self.macros_dir)):
            if f.lower().endswith('.json'):
                self.listbox.insert(tk.END, f)

    # GUI actions
    def gui_record(self):
        name = simpledialog.askstring("Macro name", "Enter name for macro:", parent=self.root)
        if not name:
            return
        path = os.path.join(self.macros_dir, f"{name}.json")
        threading.Thread(target=self._record_thread, args=(path,), daemon=True).start()

    def _record_thread(self, path):
        try:
            self.rec.start()
            messagebox.showinfo("Recording", "Recording started. Press Ctrl+Alt+R again (hotkey) to stop.")
            # wait until recorder.start_time becomes None (stop called)
            while self.rec.start_time:
                time.sleep(0.1)
            if self.rec.events:
                target = {"title": self.rec.assoc_window.get('title'), "partial": True, "pid": self.rec.assoc_window.get('pid')}
                self.rec.save(path, name=os.path.splitext(os.path.basename(path))[0], target_match=target)
                self._load_list()
                messagebox.showinfo("Saved", f"Saved macro to {path}")
        except Exception:
            log_exc("record thread")

    def gui_stop_record(self):
        try: self.rec.stop()
        except Exception: pass

    def gui_play(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Select macro", "Please select a macro.")
            return
        fname = self.listbox.get(sel[0])
        path = os.path.join(self.macros_dir, fname)
        loops = simpledialog.askinteger("Loops", "How many loops?", initialvalue=1, minvalue=1, parent=self.root)
        if loops is None: loops = 1
        speed = simpledialog.askfloat("Speed", "Playback speed (1.0 = normal)", initialvalue=1.0, minvalue=0.1, parent=self.root)
        if speed is None: speed = 1.0
        threading.Thread(target=self.player.play_file, args=(path, loops, speed, False), daemon=True).start()

    def import_macro(self):
        src = filedialog.askopenfilename(parent=self.root, title="Import macro", filetypes=[("JSON","*.json")])
        if not src: return
        dst = os.path.join(self.macros_dir, os.path.basename(src))
        try:
            with open(src,'r',encoding='utf-8') as f: data = json.load(f)
            with open(dst,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Imported", f"Imported to {dst}")
            self._load_list()
        except Exception:
            log_exc("import")

    def export_macro(self):
        sel = self.listbox.curselection()
        if not sel: return
        fname = self.listbox.get(sel[0]); path = os.path.join(self.macros_dir,fname)
        dst = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not dst: return
        try:
            with open(path,'r',encoding='utf-8') as f: data = json.load(f)
            with open(dst,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Exported", f"Exported to {dst}")
        except Exception:
            log_exc("export")

    def delete_macro(self):
        sel = self.listbox.curselection()
        if not sel: return
        fname = self.listbox.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete {fname}?"):
            try:
                os.remove(os.path.join(self.macros_dir, fname))
                self._load_list()
            except Exception:
                log_exc("delete")

    def toggle_topmost(self):
        try:
            curr = bool(self.root.attributes("-topmost"))
        except Exception:
            curr = False
        try:
            self.root.attributes("-topmost", not curr)
            messagebox.showinfo("Topmost", f"Topmost set to {not curr}")
        except Exception:
            log_exc("topmost")

    def edit_macro(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select a macro to edit")
            return
        fname = self.listbox.get(sel[0])
        path = os.path.join(self.macros_dir, fname)
        try:
            with open(path,'r',encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            messagebox.showerror("Error", "Failed to load macro")
            return
        # Simple editor: show number of events and allow deleting an event by index, inserting delay, toggling global shift behavior
        evs = data.get('events', [])
        info = f"Macro: {fname}\nEvents: {len(evs)}\n\nOptions:\n1) Delete event by index\n2) Insert delay at index\n3) Toggle global 'force shift' (player-level)\n"
        choice = simpledialog.askinteger("Edit macro", info + "\nChoose option (1/2/3):", parent=self.root, minvalue=1, maxvalue=3)
        if choice == 1:
            idx = simpledialog.askinteger("Delete", "Event index (0-based):", parent=self.root, minvalue=0, maxvalue=len(evs)-1)
            if idx is None: return
            evs.pop(idx)
            data['events'] = evs
            with open(path,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Deleted", f"Deleted event {idx}")
        elif choice == 2:
            idx = simpledialog.askinteger("Insert", "Insert at index (0-based):", parent=self.root, minvalue=0, maxvalue=len(evs))
            if idx is None: return
            delay = simpledialog.askfloat("Delay", "Delay seconds to insert:", parent=self.root, minvalue=0.0)
            if delay is None: return
            # create a pseudo-event that represents a pause
            newt = (evs[idx]['t'] if idx < len(evs) else (evs[-1]['t'] if evs else 0.0)) + delay
            # shift subsequent events' timestamps
            for j in range(idx, len(evs)):
                evs[j]['t'] = evs[j]['t'] + delay
            data['events'] = evs
            with open(path,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Inserted", f"Inserted {delay}s at {idx}")
        elif choice == 3:
            cur = self.player.force_shift
            # toggle between None -> False -> True -> None
            if cur is None: self.player.force_shift = False
            elif cur is False: self.player.force_shift = True
            else: self.player.force_shift = None
            messagebox.showinfo("Force shift", f"Player.force_shift set to {self.player.force_shift}")
        self._load_list()

    # Global hotkeys via pynput
    def _setup_hotkeys(self):
        from pynput.keyboard import GlobalHotKeys
        def hk_record():
            # toggle record start/stop via hotkey
            if self.rec.start_time:
                self.gui_stop_record()
            else:
                # prompt for name in main thread
                def askstart():
                    name = simpledialog.askstring("Macro name", "Enter macro name:", parent=self.root)
                    if not name: return
                    path = os.path.join(self.macros_dir, f"{name}.json")
                    threading.Thread(target=self._record_thread, args=(path,), daemon=True).start()
                self.root.after(0, askstart)

        def hk_play():
            self.root.after(0, self.gui_play)

        def hk_pause():
            self.player.toggle_pause()

        def hk_emergency():
            logging.warning("Emergency hotkey triggered")
            self.player.stop()
            self.rec.stop()

        hotmap = {'<ctrl>+<alt>+r':hk_record, '<ctrl>+<alt>+p':hk_play, '<ctrl>+<alt>+space':hk_pause, '<esc>':hk_emergency}
        self._gh = GlobalHotKeys(hotmap)
        self._gh.start()

# ---------------- Main ----------------
def main():
    root = tk.Tk()
    app = MacroManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    print("Running Macro Recorder (Windows-only). Logs:", LOG_FILE)
    main()
