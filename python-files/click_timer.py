import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui

pyautogui.FAILSAFE = True

class ClickTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("클릭 타이머")
        self.root.geometry("420x260")
        self.root.resizable(False, False)

        self.coord = None
        self.countdown_thread = None
        self.stop_flag = threading.Event()

        frm = ttk.Frame(root, padding=16)
        frm.pack(fill=tk.BOTH, expand=True)

        self.coord_label = ttk.Label(frm, text="선택된 좌표: 없음")
        self.coord_label.grid(row=0, column=0, columnspan=3, sticky="w")

        self.pick_btn = ttk.Button(frm, text="좌표 선택", command=self.pick_coordinate)
        self.pick_btn.grid(row=1, column=0, sticky="w")

        self.preview_btn = ttk.Button(frm, text="좌표로 커서 이동", command=self.preview_move, state=tk.DISABLED)
        self.preview_btn.grid(row=1, column=1, sticky="w", padx=(8,0))

        ttk.Label(frm, text="지연 시간(초) →").grid(row=2, column=0, sticky="w", pady=(12,0))
        self.delay_var = tk.StringVar(value="5")
        self.delay_entry = ttk.Entry(frm, textvariable=self.delay_var, width=10)
        self.delay_entry.grid(row=2, column=1, sticky="w", pady=(12,0))

        self.move_check_var = tk.BooleanVar(value=True)
        self.move_check = ttk.Checkbutton(frm, text="클릭 전에 커서를 좌표로 이동", variable=self.move_check_var)
        self.move_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8,0))

        self.status_var = tk.StringVar(value="대기 중")
        self.status_lbl = ttk.Label(frm, textvariable=self.status_var)
        self.status_lbl.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8,0))

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=3, sticky="w", pady=(12,0))
        self.start_btn = ttk.Button(btns, text="시작", command=self.start_countdown)
        self.start_btn.pack(side=tk.LEFT)
        self.stop_btn = ttk.Button(btns, text="정지", command=self.stop_countdown, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(8,0))

        info = (
            "사용법:\n"
            "1) '좌표 선택'을 눌러 전체 화면 오버레이에서 클릭 위치를 지정\n"
            "2) 지연 시간(초) 입력\n"
            "3) '시작'을 누르면 카운트다운 후 자동 클릭\n"
            "※ 비상중지: 마우스를 화면 좌상단(0,0)으로 이동"
        )
        ttk.Label(frm, text=info, foreground="#444").grid(row=6, column=0, columnspan=3, sticky="w", pady=(12,0))

        for c in range(3):
            frm.grid_columnconfigure(c, weight=0)

    def pick_coordinate(self):
        overlay = tk.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        try:
            overlay.attributes("-alpha", 0.25)
        except tk.TclError:
            pass
        overlay.configure(bg="black")
        overlay.attributes("-topmost", True)
        overlay.overrideredirect(True)

        msg = tk.Label(
            overlay,
            text="클릭할 지점을 마우스로 한 번 클릭하세요\n(ESC: 취소)",
            font=("Segoe UI", 18),
            fg="white", bg="black"
        )
        msg.pack(expand=True)

        def on_click(event):
            x = event.x_root
            y = event.y_root
            self.coord = (x, y)
            self.coord_label.config(text=f"선택된 좌표: x={x}, y={y}")
            self.preview_btn.config(state=tk.NORMAL)
            overlay.destroy()

        def on_key(event):
            if event.keysym == "Escape":
                overlay.destroy()

        overlay.bind("<Button-1>", on_click)
        overlay.bind("<Key>", on_key)
        overlay.focus_set()

    def preview_move(self):
        if not self.coord:
            messagebox.showwarning("안내", "먼저 좌표를 선택하세요.")
            return
        x, y = self.coord
        pyautogui.moveTo(x, y, duration=0.3)

    def start_countdown(self):
        if not self.coord:
            messagebox.showwarning("안내", "먼저 좌표를 선택하세요.")
            return
        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("안내", "지연 시간은 0 이상의 숫자여야 합니다.")
            return

        self.stop_flag.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set(f"카운트다운 시작: {delay:.1f}초")

        def worker():
            remain = delay
            while remain > 0 and not self.stop_flag.is_set():
                self.status_var.set(f"남은 시간: {remain:.1f}초")
                time.sleep(0.1)
                remain = max(0.0, remain - 0.1)
            if self.stop_flag.is_set():
                self.status_var.set("정지됨")
            else:
                x, y = self.coord
                if self.move_check_var.get():
                    pyautogui.moveTo(x, y, duration=0.3)
                self.status_var.set("클릭 실행")
                pyautogui.click(x, y)
                self.status_var.set("완료")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

        self.countdown_thread = threading.Thread(target=worker, daemon=True)
        self.countdown_thread.start()

    def stop_countdown(self):
        self.stop_flag.set()

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = ClickTimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
