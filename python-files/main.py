import tkinter as tk
from tkinter import messagebox
import os, threading, time, subprocess, sys, platform
from datetime import datetime, timedelta, timezone
import requests
import json
import pystray
from PIL import Image, ImageDraw

# Configuration
ADMIN_KEY = "admin123"
API_BASE_URL = "http://localhost:3000/api"  # กำหนด URL ของ API
shutdown_warning_shown = False
remaining_seconds = 0
user_key = None
user_email = None
status_window = None
status_label = None

# ========== API Functions ==========
def verify_access_key(key: str) -> dict:
    """ตรวจสอบคีย์ผ่าน API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/keys/validate",
            headers={"Content-Type": "application/json"},
            json={"key": key}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return {
                    "valid": True,
                    "email": data["key"]["email"],
                    "remaining": int(data["remainingMs"] / 1000)  # แปลง ms เป็น seconds
                }
            else:
                return {"valid": False, "reason": "คีย์ไม่พบหรือหมดอายุ"}
        elif response.status_code == 404:
            return {"valid": False, "reason": "คีย์ไม่พบในระบบ"}
        else:
            return {"valid": False, "reason": f"API error: {response.status_code}"}
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการตรวจสอบคีย์: {e}")
        return {"valid": False, "reason": str(e)}

def check_remaining_time(key: str) -> int | None:
    """เช็คเวลาที่เหลือผ่าน API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/keys/validate",
            headers={"Content-Type": "application/json"},
            json={"key": key}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return int(data["remainingMs"] / 1000)  # แปลง ms เป็น seconds
            return 0
        return None
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการเช็คเวลา: {e}")
        return None

# ========== System Functions ==========
def shutdown_system():
    """ปิดเครื่องตาม OS"""
    print("\n🔴 กำลังปิดเครื่อง...")
    system = platform.system()
    try:
        if system == "Windows":
            os.system("shutdown /s /t 10")
        elif system == "Darwin":  # macOS
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
        elif system == "Linux":
            os.system("shutdown -h now")
        else:
            print(f"⚠️ ไม่รองรับ OS: {system}")
    except Exception as e:
        print(f"❌ ไม่สามารถปิดเครื่อง: {e}")

def format_time(seconds):
    """แปลงวินาทีเป็น HH:MM"""
    hours = seconds // 3600
    mins = (seconds % 3600) // 60
    return f"{hours:02d}:{mins:02d}"

def countdown_timer_background():
    """Background timer — รีเฟรช API ทุก 5 นาทีสุดท้าย"""
    global remaining_seconds, shutdown_warning_shown, user_key

    print("⏰ เริ่มนับถอยหลัง (background)...")

    if remaining_seconds <= 0:
        print("⚠️ remaining_seconds ไม่ถูกต้องหรือเป็น 0 ตั้งแต่เริ่มต้น")
        return

    elapsed_since_refresh = 0

    while True:
        if isinstance(remaining_seconds, (int, float)) and remaining_seconds <= 300:
            DB_REFRESH_INTERVAL = 60
        else:
            DB_REFRESH_INTERVAL = float('inf')

        if elapsed_since_refresh >= DB_REFRESH_INTERVAL:
            val = check_remaining_time(user_key)
            if val is None:
                print("⚠️ ไม่สามารถเชื่อมต่อ API — ใช้ค่า Temp ต่อ")
            else:
                remaining_seconds = val
                print(f"🔄 รีเฟรชจาก API: {format_time(remaining_seconds)}")
            elapsed_since_refresh = 0

        if isinstance(remaining_seconds, (int, float)):
            if remaining_seconds <= 0:
                print("⏰ เวลาเหลือ 0 - ปิดเครื่อง")
                shutdown_system()
                break
            else:
                print(f"⏱️ เวลาเหลือ: {format_time(int(remaining_seconds))}")
        else:
            print("⚠️ เวลาไม่แน่นอน (None) — จะไม่ปิดเครื่องจนกว่าจะมีค่าแน่นอน")

        if isinstance(remaining_seconds, (int, float)) and remaining_seconds <= 300 and not shutdown_warning_shown:
            shutdown_warning_shown = True
            try:
                show_warning_dialog()
            except Exception:
                pass

        time.sleep(60)
        elapsed_since_refresh += 60
        if isinstance(remaining_seconds, (int, float)):
            remaining_seconds = max(0, int(remaining_seconds) - 60)

# ========== System Tray Functions ==========
def create_image():
    """Create a simple image for the tray icon"""
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
    return image

def show_window(icon, item):
    """Show the main window from tray"""
    icon.stop()
    status_window.deiconify()

def quit_app(icon, item):
    """Quit the application from tray"""
    icon.stop()
    try:
        status_window.destroy()
    except:
        pass
    sys.exit(0)

def run_tray():
    """Run system tray icon"""
    icon = pystray.Icon("system_lock", create_image(), "System Lock")
    icon.menu = pystray.Menu(
        pystray.MenuItem("Show", show_window),
        pystray.MenuItem("Exit", quit_app)
    )
    icon.run()

def hide_window():
    """Hide window to system tray"""
    status_window.withdraw()
    threading.Thread(target=run_tray, daemon=True).start()

def show_warning_dialog():
    """แสดง UI ที่เตือนเมื่อเหลือ 5 นาที"""
    warning_window = tk.Toplevel(status_window)
    warning_window.title("⚠️ แจ้งเตือน")
    warning_window.geometry("500x300")
    warning_window.attributes("-topmost", True)
    warning_window.configure(bg="#ff6b6b")
    
    frame = tk.Frame(warning_window, bg="#ff6b6b")
    frame.pack(expand=True, fill="both")
    
    tk.Label(frame, text="⚠️ เตือน!", bg="#ff6b6b", fg="white", font=("Arial", 28, "bold")).pack(pady=20)
    tk.Label(frame, text="เครื่องจะปิดในอีก 5 นาที", bg="#ff6b6b", fg="white", font=("Arial", 18)).pack(pady=10)
    tk.Label(frame, text="หากต้องการเพิ่มเวลา โปรดติดต่อผู้ดูแลระบบ", bg="#ff6b6b", fg="white", font=("Arial", 12)).pack(pady=15)
    
    def close_warning():
        warning_window.destroy()
    
    btn = tk.Button(frame, text="ตกลง", command=close_warning, bg="#ff4444", fg="white", font=("Arial", 14, "bold"), padx=30, pady=10, relief="flat", cursor="hand2")
    btn.pack(pady=20)

def create_status_window():
    """สร้างหน้าต่างแสดงสถานะที่รันอยู่เบื้องหลัง"""
    global status_window, status_label
    
    status_window = tk.Tk()
    status_window.title("🔒 System Lock - Active")
    status_window.geometry("400x200")
    status_window.attributes("-topmost", False)
    status_window.configure(bg="#1a1a2e")
    
    status_window.protocol("WM_DELETE_WINDOW", hide_window)
    
    frame = tk.Frame(status_window, bg="#1a1a2e")
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    tk.Label(frame, text="🔓 ระบบปลดล็อกแล้ว", bg="#1a1a2e", fg="#4CAF50", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(frame, text=f"ผู้ใช้: {user_email}", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(pady=5)
    
    status_label = tk.Label(frame, text="⏱️ เวลาเหลือ: กำลังโหลด...", bg="#1a1a2e", fg="#00d4ff", font=("Arial", 16))
    status_label.pack(pady=20)
    
    btn_admin = tk.Button(frame, text="🔐 Admin Panel", command=show_admin_panel, bg="#444", fg="white", font=("Arial", 12), padx=20, pady=8, relief="flat", cursor="hand2")
    btn_admin.pack(pady=10)
    
    update_status_display()
    
    status_window.mainloop()

def update_status_display():
    """อัปเดตการแสดงเวลาที่เหลือ"""
    global remaining_seconds, status_label, status_window
    try:
        if remaining_seconds > 0:
            status_label.config(text=f"⏱️ เวลาเหลือ: {format_time(remaining_seconds)}")
            status_window.after(5000, update_status_display)
        else:
            status_label.config(text="⏰ เวลาหมด - กำลังปิดเครื่อง...")
    except:
        pass

# ========== Loading Spinner ==========
class LoadingSpinner:
    def __init__(self, parent, size=40):
        self.canvas = tk.Canvas(parent, width=size, height=size, bg="#1a1a2e", highlightthickness=0)
        self.size = size
        self.angle = 0
        self.running = False
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def start(self):
        self.running = True
        self.animate()
        
    def stop(self):
        self.running = False
        
    def animate(self):
        if not self.running:
            return
        self.canvas.delete("all")
        center = self.size / 2
        radius = self.size / 3
        for i in range(8):
            angle = self.angle + (i * 45)
            x = center + radius * 0.7 * (1 if i % 3 == 0 else 0.6) * (1 if i < 4 else -1)
            y = center + radius * 0.7 * (1 if i % 3 == 0 else 0.6) * (1 if 1 <= i < 5 else -1)
            opacity = int(255 * (1 - i / 8))
            color = f"#{opacity:02x}{opacity:02x}{255:02x}"
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")
        self.angle = (self.angle + 45) % 360
        self.canvas.after(100, self.animate)

# ========== Main GUI ==========
def check_key(max_retries=5, retry_delay=2):
    """ตรวจสอบคีย์พร้อม loading spinner และ retry"""
    global user_key, user_email, remaining_seconds
    
    key = entry_key.get()
    if not key:
        messagebox.showwarning("ข้อมูลไม่สมบูรณ์", "กรุณากรอกคีย์!")
        return
    
    loading_frame = tk.Frame(frame, bg="#1a1a2e")
    loading_frame.place(relx=0.5, rely=0.5, anchor="center")
    spinner = LoadingSpinner(loading_frame, size=50)
    spinner.pack()
    loading_label = tk.Label(loading_frame, text="กำลังตรวจสอบ...", bg="#1a1a2e", fg="#00d4ff", font=("Arial", 14))
    loading_label.pack(pady=10)
    spinner.start()
    btn_confirm.config(state="disabled")
    entry_key.config(state="disabled")
    btn_admin.config(state="disabled")
    root.update()
    
    def verify_in_thread():
        global user_key, user_email, remaining_seconds
        time.sleep(1)
        
        # Retry mechanism
        for attempt in range(max_retries):
            result = verify_access_key(key)
            if result.get("valid") or "API error" not in result.get("reason", ""):
                break
            print(f"🔄 Retry attempt {attempt + 1}/{max_retries}: {result['reason']}")
            time.sleep(retry_delay)
        
        root.after(0, lambda: handle_verification_result(result, loading_frame, spinner))
    
    def handle_verification_result(result, loading_frame, spinner):
        global user_key, user_email, remaining_seconds
        spinner.stop()
        loading_frame.destroy()
        
        if result and result["valid"]:
            user_email = result["email"]
            user_key = key
            remaining_seconds = result["remaining"]
            if remaining_seconds <= 0:
                messagebox.showerror("❌ ผิดพลาด", "คีย์นี้หมดอายุแล้ว")
                btn_confirm.config(state="normal")
                entry_key.config(state="normal")
                btn_admin.config(state="normal")
                entry_key.delete(0, tk.END)
                entry_key.focus()
                return
            messagebox.showinfo("✅ สำเร็จ", f"ยินดีต้อนรับ {user_email}!\n\nเวลาเหลือ: {format_time(remaining_seconds)}\n(ระบบจะปิดเครื่องเมื่อเวลาหมด)")
            print(f"✅ ปลดล็อกสำเร็จ - {user_email}")
            print(f"⏰ เวลาเหลือ: {format_time(remaining_seconds)}")
            root.destroy()
            countdown_thread = threading.Thread(target=countdown_timer_background, daemon=True)
            countdown_thread.start()
            create_status_window()
        else:
            reason = result["reason"] if result else "ข้อผิดพลาดไม่ทราบสาเหตุ"
            messagebox.showerror("❌ ผิดพลาด", f"คีย์ไม่ถูกต้อง!\n\n{reason}")
            btn_confirm.config(state="normal")
            entry_key.config(state="normal")
            btn_admin.config(state="normal")
            entry_key.delete(0, tk.END)
            entry_key.focus()
    
    verify_thread = threading.Thread(target=verify_in_thread, daemon=True)
    verify_thread.start()

def show_admin_panel():
    """แสดง Admin Panel"""
    admin_window = tk.Toplevel(status_window if status_window else root)
    admin_window.title("🔐 Admin Panel")
    admin_window.geometry("450x250")
    admin_window.attributes("-topmost", True)
    admin_window.configure(bg="#1a1a2e")
    frame = tk.Frame(admin_window, bg="#1a1a2e")
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    tk.Label(frame, text="🔐 Admin Key", bg="#1a1a2e", fg="white", font=("Arial", 16, "bold")).pack(pady=10)
    entry_admin = tk.Entry(frame, show="*", font=("Arial", 16), justify="center", width=25, bg="#16213e", fg="white", insertbackground="white")
    entry_admin.pack(pady=15)
    entry_admin.focus()
    
    def verify_admin():
        if entry_admin.get() == ADMIN_KEY:
            messagebox.showinfo("✅ สำเร็จ", "ปิดโปรแกรมด้วย Admin Key")
            print("👑 ปิดโปรแกรมด้วย Admin Key")
            admin_window.destroy()
            try:
                status_window.destroy()
            except:
                pass
            sys.exit(0)
        else:
            messagebox.showerror("❌ ผิดพลาด", "Admin Key ไม่ถูกต้อง!")
            entry_admin.delete(0, tk.END)
    
    entry_admin.bind("<Return>", lambda e: verify_admin())
    btn = tk.Button(frame, text="ยืนยัน", font=("Arial", 14, "bold"), command=verify_admin, bg="#0f4c75", fg="white", activebackground="#1a6fa3", activeforeground="white", padx=25, pady=10, relief="flat", cursor="hand2")
    btn.pack(pady=10)
    
    def on_closing():
        admin_window.destroy()
    
    admin_window.protocol("WM_DELETE_WINDOW", on_closing)

# ========== Main Program ==========
if __name__ == "__main__":
    print(f"🖥️ ระบบปฏิบัติการ: {platform.system()} {platform.release()}")
    
    # ตรวจสอบการเชื่อมต่อ API
    try:
        response = requests.get(f"{API_BASE_URL}/keys")
        if response.status_code != 200:
            print(f"⚠️ ไม่สามารถเชื่อมต่อ API: Status {response.status_code}")
            sys.exit(1)
        print("✅ เชื่อมต่อ API สำเร็จ")
    except Exception as e:
        print(f"⚠️ ไม่สามารถเชื่อมต่อ API: {e}")
        sys.exit(1)
    
    root = tk.Tk()
    root.title("🔒 System Lock")
    root.geometry("550x500")
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.configure(bg="#1a1a2e")
    
    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both", padx=30, pady=30)
    
    tk.Label(frame, text="🔒", bg="#1a1a2e", fg="#0f4c75", font=("Arial", 60)).pack(pady=20)
    tk.Label(frame, text="System Lock", bg="#1a1a2e", fg="white", font=("Arial", 28, "bold")).pack(pady=10)
    tk.Label(frame, text="กรุณากรอกคีย์เพื่อเข้าใช้งานเครื่อง", bg="#1a1a2e", fg="#aaa", font=("Arial", 13)).pack(pady=15)
    
    entry_frame = tk.Frame(frame, bg="#16213e", highlightthickness=2, highlightbackground="#0f4c75")
    entry_frame.pack(pady=20, ipadx=10, ipady=12)
    
    entry_key = tk.Entry(entry_frame, show="•", font=("Arial", 20), justify="center", width=22, bg="#16213e", fg="white", insertbackground="white", border=0)
    entry_key.pack()
    entry_key.focus()
    entry_key.bind("<Return>", lambda e: check_key())
    
    button_frame = tk.Frame(frame, bg="#1a1a2e")
    button_frame.pack(pady=25)
    
    btn_confirm = tk.Button(button_frame, text="ยืนยัน", font=("Arial", 16, "bold"), command=check_key, bg="#0f4c75", fg="white", activebackground="#1a6fa3", activeforeground="white", padx=40, pady=12, relief="flat", cursor="hand2")
    btn_confirm.pack(side="left", padx=10)
    
    btn_admin = tk.Button(button_frame, text="🔐", font=("Arial", 14), command=show_admin_panel, bg="#444", fg="white", activebackground="#666", activeforeground="white", padx=12, pady=10, relief="flat", cursor="hand2")
    btn_admin.pack(side="left", padx=5)
    
    tk.Label(frame, text="💡 ใช้คีย์ที่ได้รับจากผู้ดูแลระบบ", bg="#1a1a2e", fg="#666", font=("Arial", 11)).pack(pady=15)
    tk.Label(frame, text=f"OS: {platform.system()} {platform.release()}", bg="#1a1a2e", fg="#444", font=("Arial", 9)).pack(pady=5)
    
    root.mainloop()
    print("✅ โปรแกรมจบการทำงาน")