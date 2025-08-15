"""
28键电子琴工具（4×7 布局）

功能概览：
- 可视化 4×7 键位网格：1-7 / q-u / a-j / z-m。
- z–m 对应电子琴音阶：从左到右 z-c, x-d, c-e, v-f, b-g, n-a, m-G7。
  音色从下往上（低行到高行）逐渐清脆。
- 以 BPM 控制节奏，按谱面脚本自动弹奏并发送按键。
- 支持单音与和弦，以及休止符。
- GUI 上点击 z–m 显示音名并渐变颜色表示音高。

依赖：
- Python 3.9+
- 第三方库：pyautogui、keyboard、pyperclip
  安装：pip install pyautogui keyboard pyperclip

注意：
- 发送按键到当前前台窗口，开始播放前请切换到目标软件。
- 若游戏/软件屏蔽模拟输入，请以管理员身份运行 Python。
"""

import threading
import time
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    import keyboard
except Exception:
    keyboard = None

ROWS = [
    list("1234567"),
    list("qwertyu"),
    list("asdfghj"),
    list("zxcvbnm"),
]
VALID_KEYS = {k for row in ROWS for k in row}
Z_M_MAPPING = {
    'z': 'C', 'x': 'D', 'c': 'E', 'v': 'F', 'b': 'G', 'n': 'A', 'm': 'G7'
}

TOKEN_RE = re.compile(r"\{[^}]+\}|rest(?::[0-9]*\.?[0-9]+)?|[1-7qwertyuiopasdfghjklzxcvbnm](?::[0-9]*\.?[0-9]+)?",
                      re.IGNORECASE)
DUR_RE = re.compile(r":([0-9]*\.?[0-9]+)$")


def parse_score(text: str):
    events = []
    cleaned = []
    for line in text.splitlines():
        line = line.split('#', 1)[0]
        if line.strip():
            cleaned.append(line)
    cleaned = "\n".join(cleaned)

    for m in TOKEN_RE.finditer(cleaned):
        token = m.group(0).strip()
        if token.startswith('{'):
            body = token[1:-1].strip()
            parts = body.split()
            dur_beats = 1.0
            if ':' in parts[-1]:
                last = parts[-1]
                base = last.split(':')[0]
                parts[-1] = base
                md = DUR_RE.search(last)
                if md:
                    dur_beats = float(md.group(1))
            keys = set()
            for p in parts:
                p = p.lower()
                if p not in VALID_KEYS:
                    raise ValueError(f"非法键：{p}")
                keys.add(p)
            events.append((keys, dur_beats))
        elif token.lower().startswith('rest'):
            md = DUR_RE.search(token)
            dur_beats = float(md.group(1)) if md else 1.0
            events.append((set(), dur_beats))
        else:
            md = DUR_RE.search(token)
            dur_beats = float(md.group(1)) if md else 1.0
            key = token.split(':')[0].lower()
            if key not in VALID_KEYS:
                raise ValueError(f"非法键：{key}")
            events.append(({key}, dur_beats))
    return events


def beats_to_seconds(beats: float, bpm: float) -> float:
    return (60.0 / bpm) * beats


class Player:
    def __init__(self):
        self.thread = None
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()

    def is_playing(self):
        return self.thread is not None and self.thread.is_alive()

    def stop(self):
        self.stop_flag.set()
        self.pause_flag.clear()

    def pause(self):
        self.pause_flag.set()

    def resume(self):
        self.pause_flag.clear()

    def play(self, events, bpm, ui_highlight_cb, done_cb, pre_focus_title):
        if self.is_playing():
            return
        self.stop_flag.clear()
        self.pause_flag.clear()

        def _run():
            if pre_focus_title:
                try_focus_window(pre_focus_title)
                time.sleep(0.2)
            for idx, (keys, beats) in enumerate(events):
                if self.stop_flag.is_set():
                    break
                while self.pause_flag.is_set() and not self.stop_flag.is_set():
                    time.sleep(0.05)
                ui_highlight_cb(idx)
                duration = beats_to_seconds(beats, bpm)
                if keys:
                    press_keys(keys, duration)
                else:
                    time.sleep(duration)
            done_cb()

        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()


def press_keys(keys: set[str], hold_seconds: float):
    for k in keys:
        display_key = Z_M_MAPPING.get(k, k.upper())
        print(f"播放音：{display_key}")  # GUI 或控制台显示音名

    if keyboard is not None:
        for k in keys:
            keyboard.press(k)
        time.sleep(hold_seconds)
        for k in keys:
            keyboard.release(k)
    elif pyautogui is not None:
        for k in keys:
            pyautogui.keyDown(k)
        time.sleep(hold_seconds)
        for k in keys:
            pyautogui.keyUp(k)
    else:
        raise RuntimeError("缺少依赖：请安装 keyboard 或 pyautogui")


def try_focus_window(title_substring: str):
    try:
        import win32gui
        import win32con
    except Exception:
        return
    def _enum_handler(hwnd, result_list):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if title_substring.lower() in t.lower():
                result_list.append(hwnd)
    found = []
    try:
        win32gui.EnumWindows(_enum_handler, found)
        if found:
            hwnd = found[0]
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("28键电子琴工具 (4×7)")
        self.geometry("860x620")
        self.player = Player()
        self.events = []
        self._build_top_controls()
        self._build_grid()
        self._build_score_editor()
        self._build_statusbar()
        self._load_demo()

    def _build_top_controls(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(frm, text="BPM:").pack(side=tk.LEFT)
        self.var_bpm = tk.StringVar(value="120")
        ttk.Entry(frm, width=6, textvariable=self.var_bpm).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Label(frm, text="播放前切到窗口:").pack(side=tk.LEFT)
        self.var_win = tk.StringVar()
        ttk.Entry(frm, width=30, textvariable=self.var_win).pack(side=tk.LEFT, padx=(4, 12))
        self.btn_parse = ttk.Button(frm, text="解析谱面", command=self.on_parse)
        self.btn_parse.pack(side=tk.LEFT, padx=4)
        self.btn_play = ttk.Button(frm, text="▶ 播放", command=self.on_play)
        self.btn_play.pack(side=tk.LEFT, padx=4)
        self.btn_pause = ttk.Button(frm, text="⏸ 暂停", command=self.on_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=4)
        self.btn_resume = ttk.Button(frm, text="⏵ 继续", command=self.on_resume)
        self.btn_resume.pack(side=tk.LEFT, padx=4)
        self.btn_stop = ttk.Button(frm, text="⏹ 停止", command=self.on_stop)
        self.btn_stop.pack(side=tk.LEFT, padx=4)
        self.btn_load = ttk.Button(frm, text="打开…", command=self.on_load)
        self.btn_load.pack(side=tk.LEFT, padx=8)
        self.btn_save = ttk.Button(frm, text="保存…", command=self.on_save)
        self.btn_save.pack(side=tk.LEFT)

    def _build_grid(self):
        outer = ttk.LabelFrame(self, text="4×7 键位")
        outer.pack(fill=tk.X, padx=10, pady=6)
        self.key_buttons = []
        for r, row_keys in enumerate(ROWS):
            rowf = ttk.Frame(outer)
            rowf.pack(fill=tk.X, padx=6, pady=4)
            for c, k in enumerate(row_keys):
                btn = tk.Button(rowf, text=k.upper(), width=5,
                                command=lambda kk=k: self.tap_once(kk))
                if r == 3:  # z-m 渐变颜色显示音高
                    hue = c / 6
                    color = f"#%02x%02x%02x" % (int(255*(1-hue)), int(255*(1-hue*0.5)), int(255*hue))
                    btn.config(bg=color)
                btn.grid(row=0, column=c, padx=4, pady=2)
                self.key_buttons.append(btn)

    def _build_score_editor(self):
        frm = ttk.LabelFrame(self, text="谱面编辑区")
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.txt = tk.Text(frm, height=14, wrap=tk.WORD)
        self.txt.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.timeline = tk.Listbox(self, height=8)
        self.timeline.pack(fill=tk.BOTH, expand=False, padx=12, pady=(0, 8))

    def _build_statusbar(self):
        self.var_status = tk.StringVar(value="就绪")
        bar = ttk.Label(self, textvariable=self.var_status, anchor='w')
        bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=4)

    def tap_once(self, k: str):
        display_key = Z_M_MAPPING.get(k, k.upper())
        print(f"点击音：{display_key}")
        press_keys({k}, 0.05)

    def on_parse(self):
        try:
            events = parse_score(self.txt.get("1.0", tk.END))
            self.events = events
            self.refresh_timeline()
            self.status(f"解析成功，共 {len(events)} 个事件")
        except Exception as e:
            messagebox.showerror("解析错误", str(e))

    def on_play(self):
        if not self.events:
            self.on_parse()
            if not self.events:
                return
        try:
            bpm = float(self.var_bpm.get())
            if bpm <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("参数错误", "BPM 必须为正数")
            return
        pre_title = self.var_win.get().strip()
        self.btn_play.config(state=tk.DISABLED)
        self.player.play(
            self.events,
            bpm,
            ui_highlight_cb=self.highlight_event,
            done_cb=self.on_play_done,
            pre_focus_title=pre_title
        )
        self.status("正在播放…")

    def on_pause(self):
        self.player.pause()
        self.status("已暂停")

    def on_resume(self):
        self.player.resume()
        self.status("继续播放…")

    def on_stop(self):
        self.player.stop()
        self.btn_play.config(state=tk.NORMAL)
        self.status("已停止")

    def on_play_done(self):
        self.btn_play.config(state=tk.NORMAL)
        self.status("播放完成")

    def refresh_timeline(self):
        self.timeline.delete(0, tk.END)
        try:
            bpm = float(self.var_bpm.get())
        except Exception:
            bpm = 120.0
        total_t = 0.0
        for i, (keys, beats) in enumerate(self.events):
            dur_s = beats_to_seconds(beats, bpm)
            total_t += dur_s
            name = "休止" if not keys else "+".join(Z_M_MAPPING.get(k, k.upper()) for k in keys)
            self.timeline.insert(tk.END, f"{i+1:03d} | {name:<10} | {beats:g} 拍 ≈ {dur_s:.2f}s | t={total_t:.2f}s")

    def highlight_event(self, idx):
        if 0 <= idx < self.timeline.size():
            self.timeline.selection_clear(0, tk.END)
            self.timeline.selection_set(idx)
            self.timeline.see(idx)

    def on_load(self):
        path = filedialog.askopenfilename(title="打开谱面文件", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.txt.delete("1.0", tk.END)
                self.txt.insert("1.0", f.read())
            self.status(f"已加载：{path}")
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def on_save(self):
        path = filedialog.asksaveasfilename(title="保存谱面为…", defaultextension=".txt",
                                            filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.txt.get("1.0", tk.END))
            self.status(f"已保存：{path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _load_demo(self):
        demo = (
            "# 电子琴演示谱面\n"
            "z x c v b n m q w e a s d f g h 1 2 3 4 5 6 7\n"
        )
        self.txt.insert("1.0", demo)

    def status(self, s: str):
        self.var_status.set(s)


if __name__ == '__main__':
    try:
        app = App()
        app.mainloop()
    except Exception as exc:
        messagebox.showerror("程序错误", str(exc))
