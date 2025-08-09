import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time
import keyboard

# --- การตั้งค่าดีไซน์ (Design System) ---
BG_COLOR = "#2E2E2E"       # สีพื้นหลัง (เทาเข้ม)
TEXT_COLOR = "#EAEAEA"     # สีตัวอักษร (เทาอ่อน)
ACCENT_COLOR = "#007ACC"   # สีไฮไลท์ (สีน้ำเงิน)
SUCCESS_COLOR = "#28A745"  # สีสถานะทำงาน (สีเขียว)
WARNING_COLOR = "#FFC107"  # สีสถานะเตือน (สีเหลือง)
DISABLED_COLOR = "#5A5A5A" # สีของปุ่มเมื่อปิดใช้งาน

# --- คลาสหลักของโปรแกรม ---
class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("350x280")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=BG_COLOR)

        # ตัวแปรสถานะ
        self.clicking = False
        self.click_thread = None

        # ตั้งค่าสไตล์
        self.setup_styles()

        # สร้าง widgets
        self.create_widgets()
        
        # ตั้งค่า Hotkey
        self.setup_hotkey()
        
        # จัดการการปิดหน้าต่าง
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """ตั้งค่าสไตล์ของ ttk widgets ทั้งหมด"""
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # --- ตั้งค่าสไตล์ทั่วไป ---
        style.configure('.',
                        background=BG_COLOR,
                        foreground=TEXT_COLOR,
                        fieldbackground=BG_COLOR,
                        font=('Segoe UI', 10))

        # --- สไตล์ปุ่ม (TButton) ---
        style.configure('TButton',
                        font=('Segoe UI', 11, 'bold'),
                        padding=(10, 8),
                        borderwidth=0)
        style.map('TButton',
                  background=[('active', ACCENT_COLOR), ('disabled', DISABLED_COLOR)],
                  foreground=[('disabled', TEXT_COLOR)])

        # --- สไตล์ช่องกรอกข้อมูล (TEntry) & ComboBox ---
        style.configure('TEntry',
                        fieldbackground='#4A4A4A',
                        foreground=TEXT_COLOR,
                        borderwidth=0,
                        insertcolor=TEXT_COLOR)
        style.configure('TCombobox',
                        fieldbackground='#4A4A4A',
                        foreground=TEXT_COLOR,
                        arrowcolor=TEXT_COLOR,
                        borderwidth=0)
        style.map('TCombobox',
                  fieldbackground=[('readonly', '#4A4A4A')],
                  selectbackground=[('readonly', '#4A4A4A')],
                  selectforeground=[('readonly', TEXT_COLOR)])


    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=(20, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # --- ส่วนตั้งค่า ---
        # นับถอยหลัง
        ttk.Label(main_frame, text="นับถอยหลัง (วินาที):").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.interval_var = tk.StringVar(value="3")
        self.interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=10, justify='center')
        self.interval_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=(0, 10))

        # เปลี่ยนเป็น "การกระทำ" และเพิ่ม "spacebar"
        ttk.Label(main_frame, text="การกระทำ:").grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        self.action_var = tk.StringVar(value="left")
        self.action_combo = ttk.Combobox(main_frame, textvariable=self.action_var, values=["left", "right", "middle", "spacebar"], width=9, state="readonly", justify='center')
        self.action_combo.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=(0, 20))

        # --- ส่วนควบคุม ---
        self.start_button = ttk.Button(main_frame, text="Start (F6)", command=self.start_clicking, style='TButton')
        self.start_button.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))

        self.stop_button = ttk.Button(main_frame, text="Stop (F6)", command=self.stop_clicking, state=tk.DISABLED, style='TButton')
        self.stop_button.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        
        # --- ป้ายแสดงสถานะ ---
        self.status_label = ttk.Label(main_frame, text="กด F6 เพื่อเริ่ม", font=("Segoe UI", 11, "bold"), anchor=tk.CENTER)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(20, 0))

    def setup_hotkey(self):
        keyboard.add_hotkey('f6', self.toggle_clicking)

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if self.clicking: return
        try:
            self.interval = float(self.interval_var.get())
            if self.interval <= 0: raise ValueError("ค่าต้องเป็นบวก")
        except ValueError:
            self.status_label.config(foreground=WARNING_COLOR)
            self.status_label.config(text="! ใส่ค่าเป็นตัวเลขมากกว่า 0")
            return

        self.clicking = True
        self.set_controls_state(tk.DISABLED)
        self.click_thread = threading.Thread(target=self.click_worker, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        self.set_controls_state(tk.NORMAL)
        self.status_label.config(text="หยุดทำงานแล้ว", foreground=TEXT_COLOR)

    def set_controls_state(self, state):
        self.interval_entry.config(state=state)
        self.action_combo.config(state=state)
        if state == tk.DISABLED:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else: # tk.NORMAL
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def click_worker(self):
        action = self.action_var.get()
        while self.clicking:
            end_time = time.time() + self.interval
            while time.time() < end_time:
                if not self.clicking: return
                remaining = end_time - time.time()
                self.status_label.config(text=f"จะทำงานในอีก {remaining:.1f} วิ...", foreground=WARNING_COLOR)
                time.sleep(0.1)

            if not self.clicking: return

            # *** แก้ไข: เปลี่ยนไปใช้ keyboard.press_and_release ***
            if action == 'spacebar':
                self.status_label.config(text="กด Spacebar!", foreground=SUCCESS_COLOR)
                keyboard.press_and_release('space') # ใช้วิธีนี้แทน
            else: # เป็นการคลิกเมาส์
                self.status_label.config(text="คลิก!", foreground=SUCCESS_COLOR)
                pyautogui.click(button=action)
                x, y = pyautogui.position()
                self.show_click_effect(x, y)
            
            time.sleep(0.2)

    def show_click_effect(self, x, y):
        try:
            effect_window = tk.Toplevel(self.root)
            effect_window.overrideredirect(True)
            effect_window.attributes('-topmost', True)
            effect_window.attributes('-alpha', 0.6)
            effect_window.config(bg=WARNING_COLOR)
            size = 30
            effect_window.geometry(f'{size}x{size}+{x - size//2}+{y - size//2}')
            self.root.after(100, effect_window.destroy)
        except tk.TclError:
            pass
            
    def on_closing(self):
        self.clicking = False
        self.root.destroy()

# --- ส่วนเริ่มต้นการทำงานของโปรแกรม ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
# --- ส่วนจบของโปรแกรม ---
# หมายเหตุ: อย่าลืมติดตั้งไลบรารีที่จำเป็นก่อนใช้งาน:
# pip install pyautogui keyboard
# คำสั่งนี้จะติดตั้งไลบรารีที่จำเป็นสำหรับโปรแกรมนี้
# และโปรแกรมนี้ต้องรันบนระบบปฏิบัติการที่รองรับไลบรารีเหล่านี้
# เช่น Windows, macOS หรือ Linux ที่มีการติดตั้งไลบรารีเหล