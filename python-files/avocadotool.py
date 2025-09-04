import tkinter
import customtkinter
import pydirectinput
import time
import threading
import keyboard
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- CÀI ĐẶT CƠ BẢN CỦA TOOL ---
KEY_PRESS_INTERVAL = 0.5
CYCLE_WAIT_TIME = 20
KEYS_TO_PRESS = ['w', 'a', 's', 'd']
START_HOTKEY = 'f6'
STOP_HOTKEY = 'f7'

# --- Biến toàn cục ---
afk_running = False
afk_thread = None
afk_seconds_counter = 0

# --- Lớp Overlay (giữ nguyên, không thay đổi) ---
class OverlayWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("280x80+100+100")
        self.title("AFK Status")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.config(bg='#2b2b2b')
        self.wm_attributes("-transparentcolor", '#2b2b2b')
        self.timer_label = customtkinter.CTkLabel(self, text="Thời gian AFK: 00:00:00", font=customtkinter.CTkFont(size=18, weight="bold"), text_color="#00FF00", bg_color='#2b2b2b')
        self.timer_label.pack(pady=(5,0))
        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng...", font=customtkinter.CTkFont(size=14), text_color="lightblue", bg_color='#2b2b2b')
        self.status_label.pack(pady=(0,5))
        self.bind_drag_events(self.timer_label)
        self.bind_drag_events(self.status_label)
    def bind_drag_events(self, widget):
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.do_drag)
    def update_timer_display(self, time_str): self.timer_label.configure(text=f"Thời gian AFK: {time_str}")
    def update_status_display(self, status_text, color): self.status_label.configure(text=status_text, text_color=color)
    def start_drag(self, event): self._drag_start_x, self._drag_start_y = event.x, event.y
    def do_drag(self, event): self.geometry(f"+{self.winfo_pointerx() - self._drag_start_x}+{self.winfo_pointery() - self._drag_start_y}")

# --- Lớp ứng dụng chính ---
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # ... (Phần khởi tạo giữ nguyên) ...
        self.title("Avocado AFK Tool PRO (DirectInput)")
        self.geometry("400x320")
        self.resizable(False, False)
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("green")
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.title_label = customtkinter.CTkLabel(self.main_frame, text="🥑 Avocado AFK Tool 🥑", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=12)
        self.hotkey_info = customtkinter.CTkLabel(self.main_frame, text=f"Start: {START_HOTKEY.upper()} | Stop: {STOP_HOTKEY.upper()}", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="yellow")
        self.hotkey_info.pack(pady=(0, 10))
        self.status_label = customtkinter.CTkLabel(self.main_frame, text="Sẵn sàng để bắt đầu!", font=customtkinter.CTkFont(size=14), text_color="#90EE90")
        self.status_label.pack(pady=10)
        self.start_button = customtkinter.CTkButton(self.main_frame, text="Bắt đầu AFK", command=self.start_afk, width=200, height=40)
        self.start_button.pack(pady=10)
        self.stop_button = customtkinter.CTkButton(self.main_frame, text="Dừng AFK", command=self.stop_afk, fg_color="#D22B2B", hover_color="#B31B1B", width=200, height=40, state="disabled")
        self.stop_button.pack(pady=10)
        self.overlay = OverlayWindow(self)
        self.setup_hotkeys()
        self.update_afk_timer()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        self.overlay.update_status_display(message, color)

    def afk_logic(self):
        global afk_running
        self.update_status("Bắt đầu sau 5 giây...", "#FFA500")
        for i in range(5, 0, -1):
            if not afk_running: return
            self.update_status(f"Bắt đầu sau... {i}", "#FFA500")
            time.sleep(1)
        while afk_running:
            for key in KEYS_TO_PRESS:
                if not afk_running: return
                self.update_status(f"Đang nhấn phím '{key.upper()}'", "#FFFFFF")
                
                # <<< SỬA ĐỔI QUAN TRỌNG TẠI ĐÂY >>>
                # Thay vì press(), ta nhấn giữ 0.1 giây rồi thả ra
                pydirectinput.keyDown(key)
                time.sleep(0.1)
                pydirectinput.keyUp(key)
                # <<< KẾT THÚC SỬA ĐỔI >>>

                time.sleep(KEY_PRESS_INTERVAL)
            if afk_running:
                for i in range(CYCLE_WAIT_TIME, 0, -1):
                    if not afk_running: return
                    self.update_status(f"Đang chờ... {i} giây", "lightblue")
                    time.sleep(1)
        self.update_status("Đã dừng!", "#D22B2B")

    def start_afk(self):
        global afk_running, afk_thread
        if not afk_running:
            afk_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.afk_thread = threading.Thread(target=self.afk_logic, daemon=True)
            self.afk_thread.start()

    def stop_afk(self):
        global afk_running
        if afk_running:
            afk_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.update_status("Đang dừng...", "#D22B2B") # Thêm thông báo khi dừng

    # ... (Các hàm còn lại giữ nguyên) ...
    def update_afk_timer(self):
        global afk_seconds_counter
        if afk_running: afk_seconds_counter += 1
        hours, rem = divmod(afk_seconds_counter, 3600)
        minutes, seconds = divmod(rem, 60)
        self.overlay.update_timer_display(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self.update_afk_timer)

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(START_HOTKEY, self.start_afk)
            keyboard.add_hotkey(STOP_HOTKEY, self.stop_afk)
        except Exception: self.update_status("Lỗi phím nóng! Chạy bằng quyền Admin.", "red")

    def on_closing(self):
        global afk_running
        afk_running = False
        keyboard.unhook_all()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()