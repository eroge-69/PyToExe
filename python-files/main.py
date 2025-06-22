import json
import requests
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import keyboard
import webbrowser
import urllib3
import random
import math
import time
import uuid
import hashlib
from typing import List, Dict, Tuple, Optional
from functools import partial

# ปิดคำเตือนความปลอดภัยของ HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ตั้งค่าสีธีม
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ค่าคงที่
CONFIG_FILE = "config.json"
FLAGS_URL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/refs/heads/roblox/FVariables.txt"
HWID_PASTEBIN_URL = "https://pastebin.com/raw/ufsTQSUu"

# สีธีม Cyberpunk
CYBER_BLUE = "#00f0ff"
CYBER_PINK = "#ff00a0"
CYBER_PURPLE = "#a000ff"
CYBER_GREEN = "#00ff80"
CYBER_DARK = "#0a0a20"
CYBER_DARKER = "#050510"
CYBER_LIGHT = "#e0e0ff"
CYBER_YELLOW = "#ffff00"

class HWIDManager:
    @staticmethod
    def get_hwid():
        """สร้างรหัสฮาร์ดแวร์เฉพาะเครื่อง"""
        hwid = str(uuid.getnode())  # MAC address
        hwid += os.environ.get("COMPUTERNAME", "")
        hwid += os.environ.get("PROCESSOR_IDENTIFIER", "")
        return hashlib.sha256(hwid.encode()).hexdigest()

    @staticmethod
    def verify_hwid_from_pastebin():
        """ตรวจสอบ HWID จาก Pastebin"""
        try:
            response = requests.get(HWID_PASTEBIN_URL, verify=False, timeout=10)
            if response.status_code == 200:
                authorized_hwids = [line.strip() for line in response.text.splitlines() if line.strip()]
                current_hwid = HWIDManager.get_hwid()
                return current_hwid in authorized_hwids
        except Exception as e:
            print(f"HWID verification error: {e}")
        return False

class HWIDVerificationWindow(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.title("HWID Verification")
        self.geometry("500x350")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        """จัดหน้าต่างให้อยู่กลางจอ"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color=CYBER_DARK)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(main_frame, 
                    text="HWID VERIFICATION",
                    font=("Courier New", 18, "bold"),
                    text_color=CYBER_BLUE).pack(pady=(20, 10))
        
        # HWID display
        hwid_frame = ctk.CTkFrame(main_frame, fg_color="#0a0a30")
        hwid_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(hwid_frame, 
                    text="Your HWID:",
                    font=("Courier New", 12),
                    text_color=CYBER_LIGHT).pack(side="left", padx=5)
        
        self.hwid_entry = ctk.CTkEntry(hwid_frame, 
                                     font=("Courier New", 10),
                                     fg_color="#0a0a30",
                                     text_color=CYBER_LIGHT,
                                     border_color=CYBER_BLUE)
        self.hwid_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.hwid_entry.insert(0, HWIDManager.get_hwid())
        self.hwid_entry.configure(state="readonly")
        
        # Copy button
        copy_button = ctk.CTkButton(hwid_frame,
                                  text="COPY",
                                  command=self.copy_hwid,
                                  width=60,
                                  fg_color=CYBER_DARK,
                                  hover_color=CYBER_PURPLE)
        copy_button.pack(side="right", padx=5)
        
        # Verify button
        verify_button = ctk.CTkButton(main_frame,
                                    text="VERIFY HWID",
                                    command=self.verify_hwid,
                                    font=("Courier New", 12, "bold"),
                                    fg_color=CYBER_DARK,
                                    hover_color=CYBER_PURPLE,
                                    border_color=CYBER_BLUE,
                                    border_width=2)
        verify_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame,
                                       text="",
                                       font=("Courier New", 12),
                                       text_color=CYBER_PINK)
        self.status_label.pack(pady=10)
        
        # Support section
        support_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        support_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(support_frame,
                    text="If your HWID is not authorized:",
                    font=("Courier New", 10),
                    text_color=CYBER_LIGHT).pack(side="left")
        
        contact_button = ctk.CTkButton(support_frame,
                                     text="CONTACT SUPPORT",
                                     command=lambda: webbrowser.open("https://discord.gg/H6RzcDeDJu"),
                                     width=120,
                                     fg_color=CYBER_DARK,
                                     hover_color=CYBER_PURPLE)
        contact_button.pack(side="right")
    
    def copy_hwid(self):
        """คัดลอก HWID ไปยังคลิปบอร์ด"""
        self.clipboard_clear()
        self.clipboard_append(HWIDManager.get_hwid())
        self.status_label.configure(text="HWID copied to clipboard!", text_color=CYBER_GREEN)
    
    def verify_hwid(self):
        """ตรวจสอบ HWID"""
        self.status_label.configure(text="Verifying HWID...", text_color=CYBER_YELLOW)
        self.update()
        
        try:
            if HWIDManager.verify_hwid_from_pastebin():
                self.status_label.configure(text="VERIFICATION SUCCESSFUL", text_color=CYBER_GREEN)
                self.after(1500, self.on_verification_success)
            else:
                self.status_label.configure(text="HWID NOT AUTHORIZED", text_color=CYBER_PINK)
        except Exception as e:
            self.status_label.configure(text=f"Verification failed: {str(e)}", text_color=CYBER_PINK)
    
    def on_verification_success(self):
        self.destroy()
        self.callback(True)
    
    def on_close(self):
        self.callback(False)
        self.destroy()

class CyberpunkBackground(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=CYBER_DARKER, corner_radius=0)
        
        self.canvas = tk.Canvas(self, bg=CYBER_DARKER, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # สร้างองค์ประกอบพื้นหลัง
        self.grid_lines = []
        self.particles = []
        self.hexagons = []
        self.circuit_paths = []
        
        self.draw_grid()
        self.create_particles(15)
        self.create_hex_grid()
        self.create_circuit_paths(5)
        
        self.animate()

    def draw_grid(self):
        """วาดเส้นกริด"""
        width = self.winfo_width() if self.winfo_width() > 0 else 800
        height = self.winfo_height() if self.winfo_height() > 0 else 600
        
        # เส้นแนวตั้ง
        for x in range(0, width, 40):
            line = self.canvas.create_line(x, 0, x, height, 
                                         fill="#202050", width=1)
            self.grid_lines.append(line)
        
        # เส้นแนวนอน
        for y in range(0, height, 40):
            line = self.canvas.create_line(0, y, width, y, 
                                         fill="#202050", width=1)
            self.grid_lines.append(line)

    def create_particles(self, count):
        """สร้างอนุภาคเคลื่อนที่"""
        colors = [CYBER_BLUE, CYBER_PINK, CYBER_PURPLE, CYBER_GREEN]
        
        for _ in range(count):
            x = random.randint(0, self.winfo_width() if self.winfo_width() > 0 else 800)
            y = random.randint(0, self.winfo_height() if self.winfo_height() > 0 else 600)
            size = random.randint(2, 6)
            speed = random.uniform(0.5, 2)
            direction = random.uniform(0, 2 * math.pi)
            color = random.choice(colors)
            
            self.particles.append({
                'id': self.canvas.create_oval(x, y, x+size, y+size, 
                                            fill=color, outline=""),
                'x': x, 'y': y, 'size': size, 
                'speed': speed, 'direction': direction,
                'color': color
            })

    def create_hex_grid(self):
        """สร้างกริดหกเหลี่ยม"""
        hex_size = 30
        rows = int((self.winfo_height() if self.winfo_height() > 0 else 600) / (hex_size * 0.75)) + 2
        cols = int((self.winfo_width() if self.winfo_width() > 0 else 800) / (hex_size * math.sqrt(3)/2)) + 2
        
        for row in range(rows):
            for col in range(cols):
                x = col * hex_size * math.sqrt(3)/2
                y = row * hex_size * 0.75
                if col % 2:
                    y += hex_size * 0.375
                
                hex_id = self.canvas.create_polygon(
                    self.get_hex_points(x, y, hex_size), 
                    fill="", outline="#303080", width=1
                )
                self.hexagons.append({
                    'id': hex_id,
                    'x': x, 'y': y,
                    'size': hex_size,
                    'glow_counter': 0
                })

    def get_hex_points(self, x, y, size):
        """คำนวณจุดหกเหลี่ยม"""
        points = []
        for i in range(6):
            angle = math.pi/3 * i
            points.append(x + size * math.sin(angle))
            points.append(y + size * math.cos(angle))
        return points

    def create_circuit_paths(self, count):
        """สร้างเส้นวงจร"""
        width = self.winfo_width() if self.winfo_width() > 0 else 800
        height = self.winfo_height() if self.winfo_height() > 0 else 600
        
        for _ in range(count):
            path = []
            segments = random.randint(3, 6)
            start_x = random.randint(0, width)
            start_y = random.randint(0, height)
            
            for _ in range(segments):
                end_x = random.randint(0, width)
                end_y = random.randint(0, height)
                ctrl1_x = random.randint(0, width)
                ctrl1_y = random.randint(0, height)
                ctrl2_x = random.randint(0, width)
                ctrl2_y = random.randint(0, height)
                
                path_segment = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    smooth=True, splinesteps=12,
                    fill="#303080", width=1
                )
                path.append({
                    'id': path_segment,
                    'points': [start_x, start_y, end_x, end_y],
                    'glow_pos': 0,
                    'direction': 1
                })
                
                start_x, start_y = end_x, end_y
            
            self.circuit_paths.append(path)

    def animate(self):
        """แอนิเมชันพื้นหลัง"""
        width = self.winfo_width() if self.winfo_width() > 0 else 800
        height = self.winfo_height() if self.winfo_height() > 0 else 600
        
        # อนุภาคเคลื่อนที่
        for particle in self.particles:
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            
            if particle['x'] > width:
                particle['x'] = 0
            elif particle['x'] < 0:
                particle['x'] = width
            if particle['y'] > height:
                particle['y'] = 0
            elif particle['y'] < 0:
                particle['y'] = height
                
            self.canvas.coords(particle['id'], 
                             particle['x'], particle['y'], 
                             particle['x']+particle['size'], particle['y']+particle['size'])
            
            if random.random() < 0.05:
                particle['direction'] += random.uniform(-0.5, 0.5)
        
        # กริดหกเหลี่ยมส่องสว่าง
        for hexagon in self.hexagons:
            if random.random() < 0.01:
                self.canvas.itemconfig(hexagon['id'], fill=CYBER_BLUE)
                hexagon['glow_counter'] = 10
            elif hexagon['glow_counter'] > 0:
                hexagon['glow_counter'] -= 1
                if hexagon['glow_counter'] == 0:
                    self.canvas.itemconfig(hexagon['id'], fill="")
        
        # เส้นวงจรเคลื่อนที่
        for path in self.circuit_paths:
            for segment in path:
                segment['glow_pos'] += 0.05 * segment['direction']
                if segment['glow_pos'] >= 1 or segment['glow_pos'] <= 0:
                    segment['direction'] *= -1
                
                points = segment['points']
                x = points[0] + (points[2] - points[0]) * segment['glow_pos']
                y = points[1] + (points[3] - points[1]) * segment['glow_pos']
                
                if 'glow_id' in segment:
                    self.canvas.coords(segment['glow_id'], x-3, y-3, x+3, y+3)
                else:
                    segment['glow_id'] = self.canvas.create_oval(
                        x-3, y-3, x+3, y+3,
                        fill=CYBER_PINK, outline=""
                    )
        
        self.after(40, self.animate)

class CyberpunkButton(ctk.CTkButton):
    """ปุ่มสไตล์ Cyberpunk"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            border_width=2,
            border_color=CYBER_BLUE,
            fg_color=CYBER_DARK,
            hover_color=CYBER_PURPLE,
            text_color=CYBER_LIGHT,
            font=("Courier New", 12, "bold"),
            corner_radius=5
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(border_color=CYBER_PINK)

    def on_leave(self, event):
        self.configure(border_color=CYBER_BLUE)

class CyberpunkEntry(ctk.CTkEntry):
    """ช่องป้อนข้อมูลสไตล์ Cyberpunk"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=("Courier New", 12),
            fg_color="#0a0a30",
            text_color=CYBER_LIGHT,
            border_color=CYBER_BLUE,
            corner_radius=5
        )

class FFlagManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # ซ่อนหน้าต่างหลักจนกว่าจะตรวจสอบ HWID
        self.verify_hwid()
    
    def verify_hwid(self):
        """แสดงหน้าต่างตรวจสอบ HWID"""
        self.hwid_window = HWIDVerificationWindow(self, self.on_hwid_verified)
        self.hwid_window.grab_set()
    
    def on_hwid_verified(self, success):
        """Callback หลังตรวจสอบ HWID"""
        if success:
            self.after(100, self.initialize_app)
        else:
            self.destroy()
    
    def initialize_app(self):
        """ตั้งค่าแอปพลิเคชันหลัก"""
        self.deiconify()
        self.title("ROBLOX FFLAG MANAGER v2.0 - Mx Shop")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        self._set_cyberpunk_theme()
        self.load_config()
        self.setup_ui()
        self.setup_keybind_system()  # ระบบ keybind ใหม่
        self.setup_main_ui()
    
    def _set_cyberpunk_theme(self):
        """ตั้งค่าธีม Cyberpunk"""
        ctk.ThemeManager.theme["CTk"]["fg_color"] = CYBER_DARK
        ctk.ThemeManager.theme["CTk"]["text_color"] = CYBER_LIGHT
        ctk.ThemeManager.theme["CTk"]["button_color"] = CYBER_DARK
        ctk.ThemeManager.theme["CTk"]["button_hover_color"] = CYBER_PURPLE
        ctk.ThemeManager.theme["CTk"]["border_color"] = CYBER_BLUE
        ctk.ThemeManager.theme["CTk"]["border_width"] = 2
        
        ctk.ThemeManager.theme["CTkEntry"]["border_color"] = CYBER_BLUE
        ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = "#0a0a30"
        ctk.ThemeManager.theme["CTkEntry"]["text_color"] = CYBER_LIGHT
        
        ctk.ThemeManager.theme["CTkScrollbar"]["button_color"] = CYBER_DARK
        ctk.ThemeManager.theme["CTkScrollbar"]["button_hover_color"] = CYBER_PURPLE
        
        ctk.ThemeManager.theme["CTkCheckBox"]["border_color"] = CYBER_BLUE
        ctk.ThemeManager.theme["CTkCheckBox"]["fg_color"] = CYBER_PINK
        ctk.ThemeManager.theme["CTkCheckBox"]["hover_color"] = CYBER_PURPLE
        ctk.ThemeManager.theme["CTkCheckBox"]["text_color"] = CYBER_LIGHT

    def load_config(self):
        """โหลดการตั้งค่าจากไฟล์"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.json_path = config.get("json_path", "")
                self.always_on_top = config.get("always_on_top", False)
        else:
            self.json_path = ""
            self.always_on_top = False
            self.save_config()
        
        self.load_flags_data()
    
    def save_config(self):
        """บันทึกการตั้งค่าไปยังไฟล์"""
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "json_path": self.json_path,
                "always_on_top": self.always_on_top
            }, f)
    
    def load_flags_data(self):
        """โหลดข้อมูล FFlags"""
        try:
            with open(self.json_path, "r") as file:
                self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {
                "applicationSettings": {},
                "disabledFlags": {},
                "flagOrder": [],
                "keybinds": {}
            }
        
        self.keybinds = self.settings.get("keybinds", {})
        
        try:
            response = requests.get(FLAGS_URL, verify=False)
            lines = response.text.split("\n")
            allowed_prefixes = ("DFInt", "DFFlag", "DFString")
            self.flags_list = []
            for line in lines:
                if line.startswith(("[C++]", "[Lua]")) and " " in line:
                    flag_name = line.split(" ", 1)[1].strip()
                    if flag_name.startswith(allowed_prefixes):
                        self.flags_list.append(flag_name)
            self.flags_list.sort()
        except Exception as e:
            print(f"Error loading flags: {e}")
            self.flags_list = []
    
    def save_flags_data(self):
        """บันทึกข้อมูล FFlags"""
        self.settings["flagOrder"] = [
            flag for flag in self.settings["flagOrder"] 
            if flag in self.settings["applicationSettings"] or flag in self.settings["disabledFlags"]
        ]
        self.settings["keybinds"] = self.keybinds
        with open(self.json_path, "w") as file:
            json.dump(self.settings, file, indent=4)
    
    def setup_ui(self):
        """ตั้งค่า UI เบื้องต้น"""
        self.animated_bg = CyberpunkBackground(self)
        self.animated_bg.pack(fill="both", expand=True)
    
    def setup_main_ui(self):
        """ตั้งค่า UI หลัก"""
        self.animated_bg.destroy()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # แถบด้านข้าง
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=CYBER_DARK)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        ctk.CTkLabel(self.sidebar_frame, 
                    text="FFLAG MANAGER", 
                    font=("Courier New", 18, "bold"),
                    text_color=CYBER_BLUE).pack(pady=(20, 10))
        
        # เมนูตัวเลือก
        menu_options = [
            ("FLAG BROWSER", self.show_flag_browser),
            ("ACTIVE FLAGS", self.show_active_flags),
            ("KEYBINDS", self.show_keybinds),
            ("SETTINGS", self.show_settings),
            ("Owner Credit", self.show_documentation)
        ]
        
        for text, command in menu_options:
            btn = CyberpunkButton(self.sidebar_frame, 
                             text=text, 
                             command=command,
                             height=40)
            btn.pack(fill="x", padx=10, pady=5)
        
        # พื้นที่เนื้อหาหลัก
        self.main_content = ctk.CTkFrame(self, fg_color=CYBER_DARK)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.show_flag_browser()
    
    def setup_keybind_system(self):
        """ตั้งค่าระบบ keybind ใหม่ที่เสถียรกว่า"""
        self.keybind_thread_running = True
        self.keybind_thread = threading.Thread(target=self.keybind_listener, daemon=True)
        self.keybind_thread.start()
    
    def keybind_listener(self):
        """ฟังก์ชันตรวจจับการกดปุ่มใหม่"""
        while self.keybind_thread_running:
            try:
                for flag, key in self.keybinds.items():
                    if keyboard.is_pressed(key):
                        self.after(0, lambda f=flag: self.toggle_flag(f))
                        time.sleep(0.3)  # Debounce
            except Exception as e:
                print(f"Keybind error: {e}")
            time.sleep(0.01)
    
    def show_flag_browser(self):
        """แสดงหน้าต่างค้นหา Flag"""
        self.clear_main_content()
        
        self.browser_canvas = CyberpunkBackground(self.main_content)
        self.browser_canvas.pack(fill="both", expand=True)
        
        content_frame = ctk.CTkFrame(self.browser_canvas, fg_color=CYBER_DARK)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        
        # ส่วนค้นหา
        search_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, 
                    text="SEARCH FLAGS:", 
                    font=("Courier New", 12),
                    text_color=CYBER_GREEN).pack(side="left", padx=5)
        
        self.search_entry = CyberpunkEntry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_search)
        
        # รายการ Flag
        list_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.available_flags_list = tk.Listbox(list_frame, 
                                             bg="#0a0a30", 
                                             fg=CYBER_LIGHT,
                                             selectbackground=CYBER_PURPLE, 
                                             selectforeground=CYBER_LIGHT,
                                             font=("Courier New", 12),
                                             highlightthickness=0,
                                             borderwidth=0)
        self.available_flags_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ctk.CTkScrollbar(self.available_flags_list)
        scrollbar.pack(side="right", fill="y")
        self.available_flags_list.config(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.available_flags_list.yview)
        
        self.update_flag_list()
        
        # ส่วนควบคุม
        controls_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        self.selected_flag_label = ctk.CTkLabel(controls_frame, 
                                              text="NO FLAG SELECTED",
                                              font=("Courier New", 12),
                                              text_color=CYBER_GREEN)
        self.selected_flag_label.pack(side="left", padx=5)
        
        self.flag_value_entry = CyberpunkEntry(controls_frame, placeholder_text="ENTER VALUE...")
        self.flag_value_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        add_button = CyberpunkButton(controls_frame, 
                                text="ADD FLAG", 
                                command=self.add_flag)
        add_button.pack(side="left", padx=5)
        
        self.available_flags_list.bind("<<ListboxSelect>>", self.on_flag_select)
    
    def show_active_flags(self):
        """แสดง Flag ที่ใช้งานอยู่"""
        self.clear_main_content()
        
        self.active_flags_canvas = CyberpunkBackground(self.main_content)
        self.active_flags_canvas.pack(fill="both", expand=True)
        
        content_frame = ctk.CTkFrame(self.active_flags_canvas, fg_color=CYBER_DARK)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        
        # ปุ่มล้างทั้งหมด
        clear_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        clear_frame.pack(fill="x", padx=10, pady=5)
        
        clear_button = CyberpunkButton(clear_frame,
                                    text="CLEAR ALL FLAGS",
                                    command=self.clear_current_flags,
                                    fg_color="#300030",
                                    hover_color="#500050",
                                    text_color=CYBER_PINK,
                                    border_color=CYBER_PINK)
        clear_button.pack(side="right", padx=5)
        
        # แสดงรายการ Flag
        scroll_canvas = ctk.CTkCanvas(content_frame, 
                                     bg=CYBER_DARK, 
                                     highlightthickness=0)
        scroll_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ctk.CTkScrollbar(scroll_canvas, orientation="vertical")
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=scroll_canvas.yview)
        
        self.active_flags_frame = ctk.CTkFrame(scroll_canvas, fg_color=CYBER_DARK)
        scroll_canvas.create_window((0, 0), window=self.active_flags_frame, anchor="nw")
        
        self.active_flags_frame.bind("<Configure>", 
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        
        scroll_canvas.bind_all("<MouseWheel>", 
            lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.update_active_flags_list()
    
    def show_keybinds(self):
        """แสดงการตั้งค่า Keybind"""
        self.clear_main_content()
        
        self.keybinds_canvas = CyberpunkBackground(self.main_content)
        self.keybinds_canvas.pack(fill="both", expand=True)
        
        content_frame = ctk.CTkFrame(self.keybinds_canvas, fg_color=CYBER_DARK)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        
        # หัวข้อ
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(title_frame, 
                    text="KEYBIND MANAGER", 
                    font=("Courier New", 16, "bold"),
                    text_color=CYBER_BLUE).pack(side="left")
        
        # รายการ Keybind
        scroll_canvas = ctk.CTkCanvas(content_frame, 
                                     bg=CYBER_DARK, 
                                     highlightthickness=0)
        scroll_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ctk.CTkScrollbar(scroll_canvas, orientation="vertical")
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=scroll_canvas.yview)
        
        self.keybinds_frame = ctk.CTkFrame(scroll_canvas, fg_color=CYBER_DARK)
        scroll_canvas.create_window((0, 0), window=self.keybinds_frame, anchor="nw")
        
        self.keybinds_frame.bind("<Configure>", 
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        
        scroll_canvas.bind_all("<MouseWheel>", 
            lambda e: scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # เพิ่มการควบคุม Keybind สำหรับแต่ละ Flag
        for flag in self.settings["flagOrder"]:
            if flag in self.settings["applicationSettings"] or flag in self.settings["disabledFlags"]:
                self.create_keybind_control(flag)
    
    def create_keybind_control(self, flag):
        """สร้างส่วนควบคุม Keybind สำหรับ Flag"""
        current_keybind = self.keybinds.get(flag, "")
        
        frame = ctk.CTkFrame(self.keybinds_frame, 
                            border_width=2, 
                            border_color=CYBER_BLUE,
                            fg_color="#0a0a30")
        frame.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)
        
        label = ctk.CTkLabel(frame, 
                           text=flag,
                           font=("Courier New", 12),
                           text_color=CYBER_LIGHT)
        label.pack(side="left", padx=5)
        
        keybind_entry = CyberpunkEntry(frame, width=150)
        keybind_entry.insert(0, current_keybind)
        keybind_entry.pack(side="left", padx=5)
        
        set_button = CyberpunkButton(frame, 
                                  text="SET KEYBIND",
                                  command=lambda f=flag, e=keybind_entry: self.set_keybind(f, e))
        set_button.pack(side="left", padx=5)
        
        clear_button = CyberpunkButton(frame, 
                                     text="CLEAR",
                                     command=lambda f=flag: self.clear_keybind(f),
                                     fg_color="#300010",
                                     hover_color="#500020",
                                     text_color=CYBER_PINK,
                                     border_color=CYBER_PINK)
        clear_button.pack(side="right", padx=5)
    
    def set_keybind(self, flag, entry_widget):
        """ตั้งค่า Keybind"""
        keybind = entry_widget.get().strip().upper()
        if keybind:
            self.keybinds[flag] = keybind
            self.save_flags_data()
            messagebox.showinfo("Success", f"Keybind for {flag} set to {keybind}")
    
    def clear_keybind(self, flag):
        """ลบ Keybind"""
        if flag in self.keybinds:
            del self.keybinds[flag]
            self.save_flags_data()
            messagebox.showinfo("Success", f"Keybind for {flag} cleared")
    
    def show_settings(self):
        """แสดงหน้าต่างการตั้งค่า"""
        self.clear_main_content()
        
        self.settings_canvas = CyberpunkBackground(self.main_content)
        self.settings_canvas.pack(fill="both", expand=True)
        
        content_frame = ctk.CTkFrame(self.settings_canvas, fg_color=CYBER_DARK)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        
        # ส่วนการตั้งค่าไฟล์
        config_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        config_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(config_frame, 
                    text="CONFIGURATION FILE:", 
                    font=("Courier New", 12),
                    text_color=CYBER_GREEN).pack(anchor="w", padx=5, pady=5)
        
        file_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=5, pady=5)
        
        self.json_path_entry = CyberpunkEntry(file_frame)
        self.json_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.json_path_entry.insert(0, self.json_path)
        
        browse_button = CyberpunkButton(file_frame, 
                                   text="BROWSE", 
                                   command=self.select_json_file)
        browse_button.pack(side="left", padx=5)
        
        # ส่วนนำเข้า FFlag
        import_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        import_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(import_frame, 
                    text="IMPORT FFLAGS:", 
                    font=("Courier New", 12),
                    text_color=CYBER_GREEN).pack(anchor="w", padx=5, pady=5)
        
        import_controls = ctk.CTkFrame(import_frame, fg_color="transparent")
        import_controls.pack(fill="x", padx=5, pady=5)
        
        self.import_path_entry = CyberpunkEntry(import_controls)
        self.import_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        import_browse_button = CyberpunkButton(import_controls, 
                                          text="BROWSE", 
                                          command=self.select_import_file)
        import_browse_button.pack(side="left", padx=5)
        
        import_button = CyberpunkButton(import_controls,
                                     text="IMPORT JSON",
                                     command=self.import_json_flags)
        import_button.pack(side="right", padx=5)
        
        # การตั้งค่าแอปพลิเคชัน
        app_frame = ctk.CTkFrame(content_frame, fg_color="#0a0a30")
        app_frame.pack(fill="x", padx=10, pady=10)
        
        self.always_on_top_var = ctk.BooleanVar(value=self.always_on_top)
        always_on_top_check = ctk.CTkCheckBox(app_frame, 
                                            text="ALWAYS ON TOP", 
                                            variable=self.always_on_top_var,
                                            command=self.toggle_always_on_top,
                                            text_color=CYBER_LIGHT,
                                            font=("Courier New", 12))
        always_on_top_check.pack(anchor="w", padx=5, pady=5)

    def select_import_file(self):
        """เลือกไฟล์ที่จะนำเข้า"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.import_path_entry.delete(0, tk.END)
            self.import_path_entry.insert(0, file_path)

    def import_json_flags(self):
        """นำเข้า FFlag จากไฟล์ JSON"""
        import_path = self.import_path_entry.get()
        if not import_path:
            messagebox.showerror("Error", "Please select a file to import")
            return
        
        try:
            with open(import_path, "r") as f:
                imported_flags = json.load(f)
                
                if not isinstance(imported_flags, dict):
                    messagebox.showerror("Error", "Invalid format: Expected a JSON object with key-value pairs")
                    return
                    
                # เพิ่ม Flag ที่นำเข้าโดยไม่ลบของเดิม
                for flag, value in imported_flags.items():
                    if flag not in self.settings["flagOrder"]:
                        self.settings["flagOrder"].append(flag)
                    self.settings["applicationSettings"][flag] = str(value)
                    
                self.save_flags_data()
                self.update_active_flags_list()
                messagebox.showinfo("Success", f"Successfully imported {len(imported_flags)} FFlags")
                
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import FFlags: {str(e)}")
    
    def show_documentation(self):
        """เปิดลิงก์เอกสาร"""
        webbrowser.open("https://discord.gg/H6RzcDeDJu")
    
    def clear_main_content(self):
        """ล้างเนื้อหาหลัก"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def update_search(self, event=None):
        """อัปเดตผลการค้นหา"""
        search_query = self.search_entry.get().lower()
        self.available_flags_list.delete(0, tk.END)
        
        for flag in self.flags_list:
            if search_query in flag.lower():
                self.available_flags_list.insert(tk.END, flag)
    
    def update_flag_list(self, event=None):
        """อัปเดตรายการ Flag"""
        self.available_flags_list.delete(0, tk.END)
        for flag in self.flags_list:
            self.available_flags_list.insert(tk.END, flag)
    
    def on_flag_select(self, event):
        """เมื่อเลือก Flag"""
        selection = self.available_flags_list.curselection()
        if selection:
            self.selected_flag = self.available_flags_list.get(selection[0])
            self.selected_flag_label.configure(text=f"SELECTED: {self.selected_flag}")
    
    def add_flag(self):
        """เพิ่ม Flag"""
        if hasattr(self, 'selected_flag') and self.selected_flag:
            value = self.flag_value_entry.get()
            if value:
                self.save_flag(self.selected_flag, value)
                self.flag_value_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Flag {self.selected_flag} added with value {value}")
                self.selected_flag = None
                self.selected_flag_label.configure(text="NO FLAG SELECTED")
    
    def clear_current_flags(self):
        """ล้าง Flag ทั้งหมด"""
        if messagebox.askyesno("Confirm", "Clear all currently active FFlags?"):
            self.settings["applicationSettings"] = {}
            self.settings["disabledFlags"] = {}
            self.settings["flagOrder"] = []
            self.keybinds = {}
            self.save_flags_data()
            self.update_active_flags_list()
            messagebox.showinfo("Success", "All FFlags have been cleared")
    
    def save_flag(self, name, value):
        """บันทึก Flag"""
        if name not in self.settings["flagOrder"]:
            self.settings["flagOrder"].append(name)
        
        if name in self.settings["disabledFlags"]:
            self.settings["disabledFlags"][name] = value
        else:
            self.settings["applicationSettings"][name] = value
        
        self.save_flags_data()
        self.update_active_flags_list()
    
    def update_active_flags_list(self):
        """อัปเดตรายการ Flag ที่ใช้งานอยู่"""
        if not hasattr(self, 'active_flags_frame'):
            return
            
        for widget in self.active_flags_frame.winfo_children():
            widget.destroy()
        
        for flag in self.settings["flagOrder"]:
            if flag in self.settings["applicationSettings"] or flag in self.settings["disabledFlags"]:
                self.create_flag_card(flag)
    
    def create_flag_card(self, flag):
        """สร้างการ์ดแสดง Flag"""
        is_enabled = flag in self.settings["applicationSettings"]
        current_value = self.settings["applicationSettings"].get(flag, 
                              self.settings["disabledFlags"].get(flag, ""))
        keybind = self.keybinds.get(flag, "NOT SET")
        
        card_frame = ctk.CTkFrame(self.active_flags_frame, 
                                 border_width=2, 
                                 border_color=CYBER_BLUE,
                                 fg_color="#0a0a30")
        card_frame.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)
        
        # ส่วนหัวการ์ด
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        status_color = CYBER_GREEN if is_enabled else CYBER_PINK
        status_text = "ENABLED" if is_enabled else "DISABLED"
        status_label = ctk.CTkLabel(header_frame, 
                                  text=f"● {status_text}", 
                                  text_color=status_color,
                                  font=("Courier New", 12, "bold"))
        status_label.pack(side="left", padx=5)
        
        flag_label = ctk.CTkLabel(header_frame, 
                                 text=flag, 
                                 font=("Courier New", 12, "bold"),
                                 text_color=CYBER_LIGHT)
        flag_label.pack(side="left", padx=5)
        
        keybind_label = ctk.CTkLabel(header_frame,
                                   text=f"Keybind: {keybind}",
                                   font=("Courier New", 10),
                                   text_color=CYBER_YELLOW)
        keybind_label.pack(side="right", padx=5)
        
        # ส่วนค่า
        value_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        value_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(value_frame, 
                    text=f"VALUE: {current_value}",
                    font=("Courier New", 12),
                    text_color=CYBER_LIGHT).pack(side="left")
        
        # ส่วนควบคุม
        controls_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        toggle_button = CyberpunkButton(controls_frame, 
                                   text="DISABLE" if is_enabled else "ENABLE",
                                   command=lambda f=flag: self.toggle_flag(f))
        toggle_button.pack(side="left", padx=5)
        
        edit_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        edit_frame.pack(side="left", padx=5)
        
        edit_entry = CyberpunkEntry(edit_frame, width=200)
        edit_entry.pack(side="left", padx=5)
        
        update_button = CyberpunkButton(edit_frame, 
                                   text="UPDATE",
                                   command=lambda f=flag, e=edit_entry: self.update_flag_value(f, e))
        update_button.pack(side="left", padx=5)
        
        remove_button = CyberpunkButton(controls_frame, 
                                   text="REMOVE",
                                   command=lambda f=flag: self.remove_flag(f),
                                   fg_color="#300010",
                                   hover_color="#500020",
                                   text_color=CYBER_PINK,
                                   border_color=CYBER_PINK)
        remove_button.pack(side="right", padx=5)
    
    def toggle_flag(self, flag):
        """สลับสถานะ Flag"""
        if flag in self.settings["applicationSettings"]:
            self.settings["disabledFlags"][flag] = self.settings["applicationSettings"].pop(flag)
        else:
            self.settings["applicationSettings"][flag] = self.settings["disabledFlags"].pop(flag)
        
        self.save_flags_data()
        self.update_active_flags_list()
    
    def update_flag_value(self, flag, entry_widget):
        """อัปเดตค่า Flag"""
        new_value = entry_widget.get()
        if new_value:
            if flag in self.settings["applicationSettings"]:
                self.settings["applicationSettings"][flag] = new_value
            elif flag in self.settings["disabledFlags"]:
                self.settings["disabledFlags"][flag] = new_value
            
            self.save_flags_data()
            entry_widget.delete(0, tk.END)
            self.update_active_flags_list()
    
    def remove_flag(self, flag):
        """ลบ Flag"""
        if flag in self.settings["applicationSettings"]:
            del self.settings["applicationSettings"][flag]
        if flag in self.settings["disabledFlags"]:
            del self.settings["disabledFlags"][flag]
        if flag in self.settings["flagOrder"]:
            self.settings["flagOrder"].remove(flag)
        if flag in self.keybinds:
            del self.keybinds[flag]
        
        self.save_flags_data()
        self.update_active_flags_list()
    
    def select_json_file(self):
        """เลือกไฟล์ JSON"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.json_path = file_path
            self.json_path_entry.delete(0, tk.END)
            self.json_path_entry.insert(0, self.json_path)
            self.save_config()
            self.load_flags_data()
            self.update_active_flags_list()
    
    def toggle_always_on_top(self):
        """สลับโหมด Always on Top"""
        self.always_on_top = self.always_on_top_var.get()
        self.attributes("-topmost", self.always_on_top)
        self.save_config()
    
    def on_close(self):
        """เมื่อปิดแอปพลิเคชัน"""
        self.keybind_thread_running = False
        if hasattr(self, 'keybind_thread'):
            self.keybind_thread.join(timeout=1)
        self.destroy()

if __name__ == "__main__":
    app = FFlagManager()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()