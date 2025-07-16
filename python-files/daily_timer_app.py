import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, time, timedelta
import json, os

activities = []

def save_data():
    with open("activities.json", "w", encoding="utf-8") as f:
        json.dump([
            {**act, 'start': act['start'].strftime("%H:%M"), 'end': act['end'].strftime("%H:%M")}
            for act in activities
        ], f, ensure_ascii=False, indent=2)

def load_data():
    global activities
    if os.path.exists("activities.json"):
        with open("activities.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
            activities = [
                {
                    'topic': act['topic'],
                    'detail': act['detail'],
                    'start': time.fromisoformat(act['start']),
                    'end': time.fromisoformat(act['end'])
                } for act in raw
            ]

def is_time_conflict(start, end, ignore_index=None):
    """ตรวจสอบการทับซ้อนของเวลา โดยคำนึงถึงกรณีข้ามวัน"""
    for i, act in enumerate(activities):
        if i == ignore_index:
            continue
        
        act_start = act['start']
        act_end = act['end']
        
        # กรณีปกติ: ไม่ข้ามวัน
        if act_end > act_start:
            # กรณีกิจกรรมใหม่ไม่ข้ามวัน
            if end > start:
                conflict = not (end <= act_start or start >= act_end)
            # กรณีกิจกรรมใหม่ข้ามวัน
            else:
                conflict = True  # กิจกรรมข้ามวันจะทับกับกิจกรรมที่ไม่ข้ามวันเสมอ
        # กรณีกิจกรรมเดิมข้ามวัน
        else:
            # กรณีกิจกรรมใหม่ไม่ข้ามวัน
            if end > start:
                conflict = True  # กิจกรรมไม่ข้ามวันจะทับกับกิจกรรมข้ามวันเสมอ
            # กรณีกิจกรรมใหม่ข้ามวัน
            else:
                conflict = True  # กิจกรรมข้ามวันสองอันจะทับกันเสมอ
        
        if conflict:
            return True
    return False

def start_app():
    now = datetime.now()
    current_time = now.time()
    
    current_activity = None
    next_activity = None
    
    for act in activities:
        start = act['start']
        end = act['end']
        
        # กรณีไม่ข้ามวัน
        if end > start:
            if start <= current_time <= end:
                current_activity = act
                break
            elif current_time < start and (next_activity is None or start < next_activity['start']):
                next_activity = act
        # กรณีข้ามวัน
        else:
            if current_time >= start or current_time <= end:
                current_activity = act
                break
            elif (next_activity is None or 
                  (next_activity['end'] > next_activity['start'] and start < next_activity['start']) or
                  (next_activity['end'] <= next_activity['start'])):
                next_activity = act
    
    # สร้างหน้าต่างแสดงผล
    win = tk.Toplevel(root)
    win.title("⏳ กิจวัตรปัจจุบัน")
    win.configure(bg="#1A1D23")
    win.geometry("400x500")
    win.resizable(False, False)
    
    # สร้างเฟรมหลัก
    main_frame = tk.Frame(win, bg="#1A1D23")
    main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    
    # สไตล์และสี
    title_font = ("Segoe UI", 16, "bold")
    text_font = ("Segoe UI", 12)
    label_fg = "#D1D5DB"
    highlight_color = "#4F46E5"
    
    # สร้างตัวแปรสำหรับแสดงผล
    time_left_var = tk.StringVar()
    status_var = tk.StringVar()
    
    def update_display():
        nonlocal current_activity, next_activity
        now = datetime.now()
        current_time = now.time()
        
        # ค้นหากิจกรรมปัจจุบัน/ถัดไปใหม่
        current_activity = None
        next_activity = None
        
        for act in activities:
            start = act['start']
            end = act['end']
            
            if end > start:  # ไม่ข้ามวัน
                if start <= current_time <= end:
                    current_activity = act
                    break
                elif current_time < start and (next_activity is None or start < next_activity['start']):
                    next_activity = act
            else:  # ข้ามวัน
                if current_time >= start or current_time <= end:
                    current_activity = act
                    break
                elif (next_activity is None or 
                      (next_activity['end'] > next_activity['start'] and start < next_activity['start']) or
                      (next_activity['end'] <= next_activity['start'])):
                    next_activity = act
        
        if current_activity:
            status_var.set("กิจกรรมปัจจุบัน")
            end_time = current_activity['end']
            
            # คำนวณเวลาคงเหลือ
            if current_activity['end'] > current_activity['start']:  # ไม่ข้ามวัน
                end_datetime = datetime.combine(now.date(), end_time)
                time_left = end_datetime - now
            else:  # ข้ามวัน
                if current_time >= current_activity['start']:  # อยู่ในส่วนก่อนเที่ยงคืน
                    end_datetime = datetime.combine(now.date() + timedelta(days=1), end_time)
                else:  # อยู่ในส่วนหลังเที่ยงคืน
                    end_datetime = datetime.combine(now.date(), end_time)
                time_left = end_datetime - now
            
            if time_left.total_seconds() <= 0:
                win.after(100, update_display)
                return
            
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{hours} ชั่วโมง {minutes} นาที {seconds} วินาที"
            time_left_var.set(time_left_str)
            win.after(1000, update_display)
        
        elif next_activity:
            status_var.set("กิจกรรมถัดไป")
            start_time = next_activity['start']
            
            # คำนวณเวลาจนเริ่มกิจกรรมถัดไป
            if next_activity['end'] > next_activity['start']:  # ไม่ข้ามวัน
                start_datetime = datetime.combine(now.date(), start_time)
            else:  # ข้ามวัน
                if current_time < next_activity['start']:  # ยังไม่ถึงเวลาเริ่ม
                    start_datetime = datetime.combine(now.date(), start_time)
                else:  # ผ่านเวลาเริ่มแล้ว (อยู่ในส่วนหลังเที่ยงคืน)
                    start_datetime = datetime.combine(now.date() + timedelta(days=1), start_time)
            
            time_until = start_datetime - now
            
            if time_until.total_seconds() <= 0:
                win.after(100, update_display)
                return
            
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_left_str = f"{hours} ชั่วโมง {minutes} นาที {seconds} วินาที"
            time_left_var.set(time_left_str)
            win.after(1000, update_display)
        
        else:
            status_var.set("ไม่มีกิจกรรม")
            time_left_var.set("")
    
    update_display()
    
    # ส่วนแสดงผล
    tk.Label(main_frame, textvariable=status_var, font=title_font, 
            bg="#1A1D23", fg=highlight_color).pack(pady=(0, 15), anchor='w')
    
    if current_activity or next_activity:
        activity = current_activity if current_activity else next_activity
        
        # หัวข้อกิจกรรม
        tk.Label(main_frame, text=activity['topic'], font=("Segoe UI", 14, "bold"), 
                bg="#1A1D23", fg="white").pack(pady=(0, 10), anchor='w')
        
        # รายละเอียด
        detail_frame = tk.Frame(main_frame, bg="#2D3139", padx=10, pady=10)
        detail_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(detail_frame, text=activity['detail'], font=text_font, 
                bg="#2D3139", fg="white", wraplength=350, justify='left').pack(anchor='w')
        
        # เวลา
        time_frame = tk.Frame(main_frame, bg="#1A1D23")
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(time_frame, text=f"เวลาเริ่ม: {activity['start'].strftime('%H:%M')}", 
                font=text_font, bg="#1A1D23", fg=label_fg).pack(side=tk.LEFT)
        tk.Label(time_frame, text=f"เวลาสิ้นสุด: {activity['end'].strftime('%H:%M')}", 
                font=text_font, bg="#1A1D23", fg=label_fg).pack(side=tk.RIGHT)
        
        # แสดงเวลาคงเหลือ
        time_left_frame = tk.Frame(main_frame, bg="#1A1D23")
        time_left_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(time_left_frame, 
                text="เวลาคงเหลือ:" if current_activity else "เริ่มในอีก:", 
                font=text_font, bg="#1A1D23", fg=label_fg).pack(side=tk.LEFT)
        
        tk.Label(time_left_frame, textvariable=time_left_var, 
                font=("Segoe UI", 12, "bold"), bg="#1A1D23", fg=highlight_color).pack(side=tk.RIGHT)
        
    else:
        # ไม่มีกิจกรรมใดๆ
        tk.Label(main_frame, text="ตอนนี้ไม่มีกิจกรรมที่กำหนดไว้", 
                font=text_font, bg="#1A1D23", fg=label_fg).pack(pady=(50, 0))
    
    # ปุ่มปิด
    close_btn = tk.Button(main_frame, text="ปิด", font=("Segoe UI", 12, "bold"),
                        bg="#4F46E5", fg="white", activebackground="#4338CA",
                        relief="flat", padx=20, pady=8, command=win.destroy)
    close_btn.pack(fill=tk.X, pady=(20, 0))

def add_activity():
    win = tk.Toplevel(root)
    win.title("➕ เพิ่มกิจกรรมใหม่")
    win.configure(bg="#1A1D23")  # Darker background like ClickUp
    win.geometry("350x550")  # Adjusted size
    win.resizable(False, False)

    # Create a frame for content with padding
    content_frame = tk.Frame(win, bg="#1A1D23")
    content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    font = ("Segoe UI", 11)
    label_fg = "#D1D5DB"
    entry_bg = "#2D3139"  # Darker entry background
    entry_fg = "#FFFFFF"  # White text
    entry_border = "#3D424D"  # Border color

    # หัวข้อกิจกรรม
    ttk.Label(content_frame, text="หัวข้อ", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    topic_entry = tk.Entry(content_frame, font=font, bg=entry_bg, fg=entry_fg, 
                          insertbackground=entry_fg, highlightthickness=1, 
                          highlightbackground=entry_border, highlightcolor="#4F46E5",
                          relief=tk.FLAT)
    topic_entry.pack(fill=tk.X, pady=(0, 15))

    # รายละเอียดกิจกรรม
    ttk.Label(content_frame, text="รายละเอียด", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    detail_text = tk.Text(content_frame, font=font, height=5, width=30, wrap="word",
                         bg=entry_bg, fg=entry_fg, insertbackground=entry_fg,
                         highlightthickness=1, highlightbackground=entry_border,
                         highlightcolor="#4F46E5", relief=tk.FLAT)
    detail_text.pack(fill=tk.X, pady=(0, 15))

    # เวลาเริ่ม
    ttk.Label(content_frame, text="เวลาเริ่ม", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    start_combo = ttk.Combobox(content_frame, font=font, state="readonly",
        values=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)])
    start_combo.pack(fill=tk.X, pady=(0, 15))

    # เวลาสิ้นสุด
    ttk.Label(content_frame, text="เวลาสิ้นสุด", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    end_combo = ttk.Combobox(content_frame, font=font, state="readonly",
        values=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)])
    end_combo.pack(fill=tk.X, pady=(0, 20))

    def submit():
        topic = topic_entry.get().strip()
        detail = detail_text.get("1.0", tk.END).strip()
        start_str = start_combo.get()
        end_str = end_combo.get()

        if not topic or not detail or not start_str or not end_str:
            messagebox.showwarning("กรอกไม่ครบ", "โปรดกรอกข้อมูลให้ครบทุกช่อง")
            return

        try:
            start = time.fromisoformat(start_str)
            end = time.fromisoformat(end_str)
        except:
            messagebox.showerror("ผิดพลาด", "รูปแบบเวลาไม่ถูกต้อง")
            return

        if is_time_conflict(start, end):
            messagebox.showwarning("ทับกัน", "เวลากิจกรรมนี้ซ้ำกับกิจกรรมเดิม")
            return

        activities.append({'topic': topic, 'detail': detail, 'start': start, 'end': end})
        save_data()
        messagebox.showinfo("เพิ่มแล้ว", "กิจกรรมถูกเพิ่มเรียบร้อย")
        win.destroy()

    # ปุ่ม Submit แบบ ClickUp
    submit_btn = tk.Button(content_frame, text="บันทึกกิจกรรม", font=("Segoe UI", 12, "bold"),
                          bg="#4F46E5", fg="white", activebackground="#4338CA",
                          relief="flat", padx=20, pady=8, command=submit)
    submit_btn.pack(fill=tk.X, pady=(10, 0))

    # ปรับแต่ง Combobox ให้เข้ากับธีม
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg, 
                   foreground=entry_fg, selectbackground="#4F46E5", 
                   selectforeground="white", bordercolor=entry_border,
                   arrowsize=15)
    style.map('TCombobox', fieldbackground=[('readonly', entry_bg)],
              selectbackground=[('readonly', '#4F46E5')],
              selectforeground=[('readonly', 'white')])

def edit_activity():
    if not activities:
        messagebox.showinfo("ไม่มี", "ยังไม่มีกิจวัตรให้แก้ไข")
        return

    # ขั้นตอนที่ 1: ให้ผู้ใช้เลือกกิจกรรมที่จะแก้ไข (เหมือนเดิม)
    options = "\n".join([f"{i+1}. {act['topic']} ({act['start'].strftime('%H:%M')} - {act['end'].strftime('%H:%M')})" for i, act in enumerate(activities)])
    idx_str = simpledialog.askstring("เลือกกิจวัตร", f"กิจวัตรที่มี:\n{options}\n\nเลือกหมายเลขเพื่อแก้ไขหรือลบ")
    
    if idx_str is None: # ผู้ใช้กด Cancel
        return

    try:
        idx = int(idx_str) - 1
        if idx < 0 or idx >= len(activities):
            raise ValueError
    except ValueError:
        messagebox.showerror("ผิดพลาด", "หมายเลขไม่ถูกต้อง")
        return
    except Exception as e:
        messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}")
        return

    selected_activity = activities[idx]

    # ขั้นตอนที่ 2: เปิดหน้าต่างแก้ไขแบบใหม่
    win = tk.Toplevel(root)
    win.title(f"✏️ แก้ไขกิจกรรม: {selected_activity['topic']}")
    win.configure(bg="#1A1D23")
    win.geometry("350x600")
    win.resizable(False, False)

    # สร้างเฟรมหลักสำหรับเนื้อหา
    content_frame = tk.Frame(win, bg="#1A1D23")
    content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # หัวข้อหน้าต่างแก้ไข
    header_frame = tk.Frame(content_frame, bg="#1A1D23")
    header_frame.pack(fill=tk.X, pady=(0, 15))
    
    tk.Label(header_frame, text=f"แก้ไข: {selected_activity['topic']}", 
            font=("Segoe UI", 14, "bold"), bg="#1A1D23", fg="#FFFFFF").pack(side=tk.LEFT)

    font = ("Segoe UI", 11)
    label_fg = "#D1D5DB"
    entry_bg = "#2D3139"
    entry_fg = "#FFFFFF"
    entry_border = "#3D424D"

    # หัวข้อกิจกรรม
    ttk.Label(content_frame, text="หัวข้อ", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    topic_entry = tk.Entry(content_frame, font=font, bg=entry_bg, fg=entry_fg, 
                         insertbackground=entry_fg, highlightthickness=1, 
                         highlightbackground=entry_border, highlightcolor="#4F46E5",
                         relief=tk.FLAT)
    topic_entry.insert(0, selected_activity['topic'])
    topic_entry.pack(fill=tk.X, pady=(0, 15))

    # รายละเอียดกิจกรรม
    ttk.Label(content_frame, text="รายละเอียด", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    detail_text = tk.Text(content_frame, font=font, height=5, width=30, wrap="word",
                        bg=entry_bg, fg=entry_fg, insertbackground=entry_fg,
                        highlightthickness=1, highlightbackground=entry_border,
                        highlightcolor="#4F46E5", relief=tk.FLAT)
    detail_text.insert("1.0", selected_activity['detail'])
    detail_text.pack(fill=tk.X, pady=(0, 15))

    # เวลาเริ่ม
    ttk.Label(content_frame, text="เวลาเริ่ม", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    start_combo = ttk.Combobox(content_frame, font=font, state="readonly",
                              values=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)])
    start_combo.set(selected_activity['start'].strftime("%H:%M"))
    start_combo.pack(fill=tk.X, pady=(0, 15))

    # เวลาสิ้นสุด
    ttk.Label(content_frame, text="เวลาสิ้นสุด", background="#1A1D23", foreground=label_fg, font=font).pack(pady=(0, 5), anchor='w')
    end_combo = ttk.Combobox(content_frame, font=font, state="readonly",
                            values=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)])
    end_combo.set(selected_activity['end'].strftime("%H:%M"))
    end_combo.pack(fill=tk.X, pady=(0, 20))

    # ปุ่มดำเนินการ
    button_frame = tk.Frame(content_frame, bg="#1A1D23")
    button_frame.pack(fill=tk.X, pady=(10, 0))

    def update_activity():
        new_topic = topic_entry.get().strip()
        new_detail = detail_text.get("1.0", tk.END).strip()
        new_start_str = start_combo.get()
        new_end_str = end_combo.get()

        if not new_topic or not new_detail or not new_start_str or not new_end_str:
            messagebox.showwarning("กรอกไม่ครบ", "โปรดกรอกข้อมูลให้ครบทุกช่อง")
            return

        try:
            new_start = time.fromisoformat(new_start_str)
            new_end = time.fromisoformat(new_end_str)
        except ValueError:
            messagebox.showerror("ผิดพลาด", "รูปแบบเวลาไม่ถูกต้อง")
            return

        if is_time_conflict(new_start, new_end, ignore_index=idx):
            messagebox.showwarning("ทับกัน", "เวลาใหม่ทับกิจกรรมอื่น")
            return
        
        if new_end <= new_start:
            messagebox.showwarning("เวลาไม่ถูกต้อง", "เวลาสิ้นสุดต้องหลังเวลาเริ่มต้น")
            return

        activities[idx]['topic'] = new_topic
        activities[idx]['detail'] = new_detail
        activities[idx]['start'] = new_start
        activities[idx]['end'] = new_end
        save_data()
        messagebox.showinfo("แก้ไขแล้ว", "กิจกรรมถูกแก้ไขเรียบร้อย")
        win.destroy()

    def delete_selected_activity():
        if messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบกิจกรรม '{selected_activity['topic']}' ใช่หรือไม่?"):
            del activities[idx]
            save_data()
            messagebox.showinfo("ลบแล้ว", "กิจกรรมถูกลบเรียบร้อย")
            win.destroy()

    # ปุ่มบันทึกการแก้ไข
    update_btn = tk.Button(button_frame, text="บันทึกการแก้ไข", font=("Segoe UI", 12, "bold"),
                          bg="#4F46E5", fg="white", activebackground="#4338CA",
                          relief="flat", padx=20, pady=8, command=update_activity)
    update_btn.pack(fill=tk.X, pady=(0, 10))

    # ปุ่มลบกิจกรรม
    delete_btn = tk.Button(button_frame, text="ลบกิจกรรม", font=("Segoe UI", 12, "bold"),
                          bg="#EF4444", fg="white", activebackground="#DC2626",
                          relief="flat", padx=20, pady=8, command=delete_selected_activity)
    delete_btn.pack(fill=tk.X)

    # ปรับแต่ง Combobox ให้เข้ากับธีม
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg, 
                   foreground=entry_fg, selectbackground="#4F46E5", 
                   selectforeground="white", bordercolor=entry_border,
                   arrowsize=15)
    style.map('TCombobox', fieldbackground=[('readonly', entry_bg)],
              selectbackground=[('readonly', '#4F46E5')],
              selectforeground=[('readonly', 'white')])

def exit_app():
    root.destroy()

# --- สร้างหน้าต่างหลักแบบ ClickUp สไตล์ ---
root = tk.Tk()
root.title("🧘‍♂️ Daily Zen Timer")
w, h = 350, 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (w // 2)
y = (screen_height // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")
root.resizable(False, False)
root.configure(bg="#1A1D23")  # Dark background like ClickUp

# สร้างเฟรมหลักสำหรับเนื้อหา
main_frame = tk.Frame(root, bg="#1A1D23")
main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

# หัวแอปพลิเคชัน
header_frame = tk.Frame(main_frame, bg="#1A1D23")
header_frame.pack(fill=tk.X, pady=(0, 20))

tk.Label(header_frame, text="Daily Zen Timer", font=("Segoe UI", 18, "bold"), 
        bg="#1A1D23", fg="#FFFFFF").pack(side=tk.LEFT)
tk.Label(header_frame, text="🧘‍♂️", font=("Segoe UI", 18), 
        bg="#1A1D23", fg="#FFFFFF").pack(side=tk.RIGHT)

# สร้างสไตล์สำหรับปุ่มแบบ ClickUp
style = ttk.Style()
style.theme_use("clam")

# สไตล์ปุ่มหลัก
style.configure("ClickUp.TButton",
               font=("Segoe UI", 12),
               foreground="#FFFFFF",
               background="#2D3139",
               padding=12,
               borderwidth=0,
               focusthickness=0,
               focuscolor='none')
style.map("ClickUp.TButton",
          background=[("active", "#3D424D")],
          foreground=[("active", "white")])

# สไตล์ปุ่มพิเศษ
style.configure("ClickUp.Primary.TButton",
               font=("Segoe UI", 12, "bold"),
               foreground="#FFFFFF",
               background="#4F46E5",
               padding=12,
               borderwidth=0)
style.map("ClickUp.Primary.TButton",
          background=[("active", "#4338CA")])

# สไตล์ปุ่มอันตราย
style.configure("ClickUp.Danger.TButton",
               font=("Segoe UI", 12, "bold"),
               foreground="#FFFFFF",
               background="#EF4444",
               padding=12,
               borderwidth=0)
style.map("ClickUp.Danger.TButton",
          background=[("active", "#DC2626")])

# ปุ่มเมนูหลัก
ttk.Button(main_frame, text="เริ่มกิจวัตร", style="ClickUp.TButton", command=start_app).pack(fill=tk.X, pady=8)
ttk.Button(main_frame, text="เพิ่มกิจกรรม", style="ClickUp.Primary.TButton", command=add_activity).pack(fill=tk.X, pady=8)
ttk.Button(main_frame, text="แก้ไขกิจกรรม", style="ClickUp.TButton", command=edit_activity).pack(fill=tk.X, pady=8)
ttk.Button(main_frame, text="ปิดแอป", style="ClickUp.Danger.TButton", command=exit_app).pack(fill=tk.X, pady=8)

# Footer
footer_frame = tk.Frame(main_frame, bg="#1A1D23")
footer_frame.pack(fill=tk.X, pady=(20, 0))
tk.Label(footer_frame, text="Zen Mode © 2023", font=("Segoe UI", 9), 
        bg="#1A1D23", fg="#6B7280").pack(side=tk.RIGHT)

load_data()
root.mainloop()