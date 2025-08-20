import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import struct
import hashlib
from datetime import datetime

class ModernIMMODisabler:
    def __init__(self, root):
        self.root = root
        self.root.title("IMMO Disabler Pro v2.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#2b2b2b")
        
        # ตัวแปรสำหรับเก็บข้อมูล
        self.file_path = tk.StringVar()
        self.offset_var = tk.StringVar()
        self.file_size = tk.StringVar(value="ขนาดไฟล์: -")
        self.file_hash = tk.StringVar(value="Hash: -")
        self.current_value = tk.StringVar(value="ค่าปัจจุบัน: -")
        
        # ธีมสี
        self.colors = {
            "dark_bg": "#2b2b2b",
            "darker_bg": "#1e1e1e",
            "card_bg": "#3c3c3c",
            "accent": "#ff6b35",
            "accent_dark": "#e55a2b",
            "text": "#ffffff",
            "text_secondary": "#cccccc",
            "success": "#4caf50",
            "warning": "#ff9800",
            "danger": "#f44336",
            "info": "#2196f3"
        }
        
        # สร้าง GUI
        self.setup_styles()
        self.create_widgets()
        
        # ตั้งค่า grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("TFrame", background=self.colors["dark_bg"])
        style.configure("TLabel", background=self.colors["dark_bg"], foreground=self.colors["text"])
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.colors["accent"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Card.TFrame", background=self.colors["card_bg"])
        style.configure("Card.TLabel", background=self.colors["card_bg"], foreground=self.colors["text"])
        
        # Button styles
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), 
                       background=self.colors["accent"], foreground="white")
        style.map("Primary.TButton", 
                 background=[('active', self.colors["accent_dark"])])
        
        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), 
                       background=self.colors["danger"], foreground="white")
        style.map("Danger.TButton", 
                 background=[('active', "#d32f2f")])
        
        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), 
                       background=self.colors["success"], foreground="white")
        style.map("Success.TButton", 
                 background=[('active', "#388e3c")])
        
        style.configure("Info.TButton", font=("Segoe UI", 10, "bold"), 
                       background=self.colors["info"], foreground="white")
        style.map("Info.TButton", 
                 background=[('active', "#1976d2")])
        
        # Entry style
        style.configure("Modern.TEntry", fieldbackground=self.colors["darker_bg"], 
                       foreground=self.colors["text"], borderwidth=1)
    
    def create_widgets(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        
        # Header section
        header_frame = ttk.Frame(main_container, style="Card.TFrame", padding="15")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Title and subtitle
        ttk.Label(header_frame, text="IMMO DISABLER PRO", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(header_frame, text="เครื่องมือปิดระบบ IMMO แบบมืออาชีพ", 
                 font=("Segoe UI", 10), foreground=self.colors["text_secondary"]).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # File selection card
        file_card = ttk.LabelFrame(main_container, text=" การจัดการไฟล์ ", padding="15", style="Card.TFrame")
        file_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_card.columnconfigure(1, weight=1)
        
        ttk.Label(file_card, text="ไฟล์ BIN:", style="Subtitle.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(file_card)
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50, style="Modern.TEntry")
        file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="เลือกไฟล์", command=self.browse_file, style="Primary.TButton")
        browse_btn.grid(row=0, column=1, sticky=tk.E)
        
        # File info
        info_frame = ttk.Frame(file_card)
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(info_frame, textvariable=self.file_size, style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(info_frame, textvariable=self.file_hash, style="Card.TLabel").grid(row=0, column=1, sticky=tk.W)
        
        # Offset card
        offset_card = ttk.LabelFrame(main_container, text=" การตั้งค่า ", padding="15", style="Card.TFrame")
        offset_card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        offset_card.columnconfigure(1, weight=1)
        
        ttk.Label(offset_card, text="ตำแหน่ง Offset (Hex):", style="Subtitle.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        offset_frame = ttk.Frame(offset_card)
        offset_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(offset_frame, text="0x", style="Card.TLabel", font=("Consolas", 11)).grid(row=0, column=0, sticky=tk.W)
        offset_entry = ttk.Entry(offset_frame, textvariable=self.offset_var, width=15, style="Modern.TEntry", font=("Consolas", 11))
        offset_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(offset_frame, text="(ตัวอย่าง: 1A3F หรือ 0x1A3F)", 
                 style="Card.TLabel", foreground=self.colors["text_secondary"]).grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(offset_frame, textvariable=self.current_value, 
                 style="Card.TLabel", foreground=self.colors["info"]).grid(row=0, column=3, sticky=tk.E, padx=(20, 0))
        
        # Action buttons card
        action_card = ttk.LabelFrame(main_container, text=" การดำเนินการ ", padding="15", style="Card.TFrame")
        action_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        button_frame = ttk.Frame(action_card)
        button_frame.grid(row=0, column=0, columnspan=4)
        
        read_btn = ttk.Button(button_frame, text="อ่านค่าปัจจุบัน", command=self.read_current_value, style="Info.TButton", width=18)
        read_btn.grid(row=0, column=0, padx=5)
        
        disable_btn = ttk.Button(button_frame, text="ปิด IMMO โดยใส่ 0", command=self.disable_immo, style="Danger.TButton", width=18)
        disable_btn.grid(row=0, column=1, padx=5)
        
        restore_btn = ttk.Button(button_frame, text="กู้คืนจาก Backup", command=self.restore_backup, style="Success.TButton", width=18)
        restore_btn.grid(row=0, column=2, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="ล้างข้อมูล", command=self.clear_data, style="Primary.TButton", width=18)
        clear_btn.grid(row=0, column=3, padx=5)
        
        # Hex dump card
        hex_card = ttk.LabelFrame(main_container, text=" ข้อมูล Hex Dump ", padding="15", style="Card.TFrame")
        hex_card.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        hex_card.columnconfigure(0, weight=1)
        hex_card.rowconfigure(0, weight=1)
        
        # Custom text widget with dark theme
        self.hex_dump = scrolledtext.ScrolledText(
            hex_card, 
            width=80, 
            height=15, 
            font=("Consolas", 10),
            bg=self.colors["darker_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            selectbackground=self.colors["accent"],
            relief="flat",
            padx=10,
            pady=10
        )
        self.hex_dump.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        status_frame = ttk.Frame(main_container, style="Card.TFrame", padding="10")
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="พร้อมทำงาน - เลือกไฟล์ BIN เพื่อเริ่มต้น")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, style="Card.TLabel", 
                             font=("Segoe UI", 9), foreground=self.colors["text_secondary"])
        status_bar.grid(row=0, column=0, sticky=tk.W)
        
        # Configure grid weights for main container
        main_container.rowconfigure(4, weight=1)
        
        # Bind events
        file_entry.bind("<FocusIn>", lambda e: file_entry.configure(style="Modern.TEntry"))
        offset_entry.bind("<FocusIn>", lambda e: offset_entry.configure(style="Modern.TEntry"))
        
        # Set focus to file entry
        file_entry.focus()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="เลือกไฟล์ BIN",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.update_file_info()
            self.status_var.set("โหลดไฟล์สำเร็จ - พร้อมทำงาน")
    
    def update_file_info(self):
        file_path = self.file_path.get()
        if file_path and os.path.exists(file_path):
            # อ่านขนาดไฟล์
            file_size = os.path.getsize(file_path)
            self.file_size.set(f"ขนาดไฟล์: {file_size} bytes (0x{file_size:X})")
            
            # คำนวณ hash
            file_hash = self.calculate_file_hash(file_path)
            self.file_hash.set(f"SHA-256 Hash: {file_hash}")
        else:
            self.file_size.set("ขนาดไฟล์: -")
            self.file_hash.set("Hash: -")
    
    def calculate_file_hash(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            return hashlib.sha256(file_data).hexdigest()[:16] + "..."
        except:
            return "การคำนวณล้มเหลว"
    
    def read_current_value(self):
        if not self.validate_inputs():
            return
        
        file_path = self.file_path.get()
        offset = self.parse_offset(self.offset_var.get())
        
        if offset is None:
            messagebox.showerror("ข้อผิดพลาด", "รูปแบบ Offset ไม่ถูกต้อง")
            return
        
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                current_value = f.read(1)[0]
            
            self.current_value.set(f"ค่าปัจจุบัน: 0x{current_value:02X}")
            self.show_hex_dump(offset)
            
            self.status_var.set(f"อ่านค่าสำเร็จ - ที่ offset 0x{offset:X} มีค่า: 0x{current_value:02X}")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถอ่านค่าได้: {str(e)}")
            self.status_var.set("การอ่านค่าล้มเหลว")
    
    def disable_immo(self):
        if not self.validate_inputs():
            return
        
        file_path = self.file_path.get()
        offset = self.parse_offset(self.offset_var.get())
        
        if offset is None:
            messagebox.showerror("ข้อผิดพลาด", "รูปแบบ Offset ไม่ถูกต้อง")
            return
        
        # ยืนยันการดำเนินการ
        confirm = messagebox.askyesno(
            "ยืนยันการปิด IMMO", 
            f"คุณแน่ใจต้องการปิด IMMO โดยเขียน 0 ที่ตำแหน่ง 0x{offset:X}?\n\n"
            f"ไฟล์: {os.path.basename(file_path)}\n\n"
            f"โปรแกรมจะสร้างไฟล์ backup อัตโนมัติก่อนดำเนินการ"
        )
        
        if not confirm:
            return
        
        try:
            # อ่านไฟล์
            with open(file_path, 'rb') as f:
                data = bytearray(f.read())
            
            # ตรวจสอบว่า offset อยู่ในช่วงที่ถูกต้อง
            if offset >= len(data):
                messagebox.showerror("ข้อผิดพลาด", f"Offset 0x{offset:X} เกินขนาดไฟล์")
                return
            
            # สร้างไฟล์ backup
            backup_path = self.create_backup(file_path)
            
            # บันทึกค่าเดิม
            old_value = data[offset]
            
            # เขียน 0 ที่ offset ที่กำหนด
            data[offset] = 0
            
            # เขียนไฟล์ที่แก้ไข
            with open(file_path, 'wb') as f:
                f.write(data)
            
            # อัพเดทข้อมูลไฟล์
            self.update_file_info()
            self.current_value.set(f"ค่าใหม่: 0x00")
            
            # แสดง hex dump
            self.show_hex_dump(offset)
            
            # แจ้งเตือนสำเร็จ
            messagebox.showinfo("สำเร็จ", 
                               f"ปิด IMMO สำเร็จ!\n\n"
                               f"รายละเอียด:\n"
                               f"• ตำแหน่ง: 0x{offset:X}\n"
                               f"• ค่าเดิม: 0x{old_value:02X}\n"
                               f"• ค่าใหม่: 0x00\n\n"
                               f"ไฟล์ backup ถูกสร้างที่:\n{backup_path}")
            
            self.status_var.set("ปิด IMMO สำเร็จ - ไฟล์ถูกบันทึกแล้ว")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
            self.status_var.set("การดำเนินการล้มเหลว")
    
    def restore_backup(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์ก่อน")
            return
        
        backup_path = file_path + '.backup'
        if not os.path.exists(backup_path):
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์ backup")
            return
        
        confirm = messagebox.askyesno(
            "ยืนยันการกู้คืน", 
            "คุณแน่ใจต้องการกู้คืนไฟล์จาก backup?\n\nการดำเนินการนี้จะแทนที่ไฟล์ปัจจุบันด้วยไฟล์ backup"
        )
        
        if not confirm:
            return
        
        try:
            with open(backup_path, 'rb') as f:
                backup_data = f.read()
            
            with open(file_path, 'wb') as f:
                f.write(backup_data)
            
            self.update_file_info()
            self.current_value.set("ค่าปัจจุบัน: -")
            self.hex_dump.delete(1.0, tk.END)
            
            messagebox.showinfo("สำเร็จ", "กู้คืนไฟล์จาก backup สำเร็จ")
            self.status_var.set("กู้คืนไฟล์สำเร็จ")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถกู้คืนไฟล์ได้: {str(e)}")
    
    def clear_data(self):
        self.file_path.set("")
        self.offset_var.set("")
        self.file_size.set("ขนาดไฟล์: -")
        self.file_hash.set("Hash: -")
        self.current_value.set("ค่าปัจจุบัน: -")
        self.hex_dump.delete(1.0, tk.END)
        self.status_var.set("ข้อมูลถูกล้างแล้ว - พร้อมสำหรับไฟล์ใหม่")
    
    def create_backup(self, file_path):
        backup_path = file_path + '.backup'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        numbered_backup = f"{file_path}.backup_{timestamp}"
        
        with open(file_path, 'rb') as f:
            original_data = f.read()
        
        with open(numbered_backup, 'wb') as f:
            f.write(original_data)
        
        return numbered_backup
    
    def show_hex_dump(self, offset):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if offset >= len(data):
                return
            
            # แสดงข้อมูล 32 bytes ก่อนและหลัง offset
            start = max(0, offset - 16)
            end = min(len(data), offset + 16)
            
            hex_dump_text = ""
            ascii_text = ""
            result_text = ""
            
            for i in range(start, end):
                if i % 16 == 0:
                    if hex_dump_text:
                        result_text += f"{start:08X}  {hex_dump_text}  {ascii_text}\n"
                    hex_dump_text = ""
                    ascii_text = ""
                    start_line = i
                
                byte_val = data[i]
                
                # Highlight offset ที่เลือก
                if i == offset:
                    hex_dump_text += f"[{byte_val:02X}] "
                else:
                    hex_dump_text += f"{byte_val:02X} "
                
                if 32 <= byte_val <= 126:
                    ascii_text += chr(byte_val)
                else:
                    ascii_text += "."
            
            # เพิ่มบรรทัดสุดท้าย
            if hex_dump_text:
                result_text += f"{start_line:08X}  {hex_dump_text}  {ascii_text}\n"
            
            self.hex_dump.delete(1.0, tk.END)
            self.hex_dump.insert(1.0, f"แสดงข้อมูลรอบๆ offset 0x{offset:X}:\n\n")
            self.hex_dump.insert(tk.END, result_text)
            
            # Highlight the offset line
            self.hex_dump.tag_configure("highlight", background=self.colors["accent_dark"], foreground="white")
            
            # Find and highlight the offset value
            start_idx = f"3.0+{offset-start+2} chars"  # Approximate position
            self.hex_dump.tag_add("highlight", start_idx, f"{start_idx}+2 chars")
            
        except Exception as e:
            self.hex_dump.delete(1.0, tk.END)
            self.hex_dump.insert(1.0, f"ข้อผิดพลาดในการอ่านข้อมูล: {str(e)}")
    
    def parse_offset(self, offset_str):
        try:
            offset_str = offset_str.strip().upper()
            if offset_str.startswith("0X"):
                offset_str = offset_str[2:]
            
            return int(offset_str, 16)
        except:
            return None
    
    def validate_inputs(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์ BIN ที่ถูกต้อง")
            return False
        
        if not self.offset_var.get().strip():
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกตำแหน่ง Offset")
            return False
        
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernIMMODisabler(root)
    root.mainloop()
