import customtkinter as ctk
import requests
import threading
from tkinter import scrolledtext
import tkinter as tk
from PIL import Image, ImageDraw
import os
import json
import time
import math

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# API URL
API_URL = "http://45.134.39.193:6391"

class AnimatedLabel(ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._animation_running = False
        self._animation_phase = 0
        
    def start_animation(self):
        self._animation_running = True
        self._animate()
        
    def stop_animation(self):
        self._animation_running = False
        
    def _animate(self):
        if not self._animation_running:
            return
            
        self._animation_phase += 0.05
        if self._animation_phase > 2 * math.pi:
            self._animation_phase = 0
            
        r = int(255 * (0.5 + 0.5 * math.sin(self._animation_phase)))
        g = int(255 * (0.5 + 0.5 * math.sin(self._animation_phase + 2)))
        b = int(255 * (0.5 + 0.5 * math.sin(self._animation_phase + 4)))
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.configure(text_color=color)
        
        self.after(50, self._animate)

class ModernApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Code Manager Pro X")
        self.root.geometry("1024x768")
        
        self.center_window()
        
        self.username = ""
        self.password = ""
        self.current_category = "luaCodes"
        self.notifications = []
        
        self.create_login_frame()
        
    def center_window(self):
        self.root.update_idletasks()
        width = 1024
        height = 768
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.login_frame.pack(fill="both", expand=True, padx=150, pady=150)
        
        bg_frame = ctk.CTkFrame(self.login_frame, corner_radius=25, fg_color="#252526", border_width=2, border_color="#4e8cff")
        bg_frame.pack(fill="both", expand=True)
        
        content_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_label = AnimatedLabel(
            content_frame, 
            text="CODE MANAGER PRO X",
            font=ctk.CTkFont(family="Roboto", size=32, weight="bold"),
            text_color="red"
        )
        self.title_label.pack(pady=(0, 50))
        self.title_label.start_animation()
        
        subtitle_label = ctk.CTkLabel(
            content_frame, 
            text="Secure Access to Your Resources",
            font=ctk.CTkFont(family="Roboto", size=18),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 40))
        
        self.username_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Username",
            width=400,
            height=50,
            font=ctk.CTkFont(family="Roboto", size=18),
            corner_radius=12,
            justify="center"
        )
        self.username_entry.pack(pady=(0, 25))
        
        self.password_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Password",
            width=400,
            height=50,
            show="*",
            font=ctk.CTkFont(family="Roboto", size=18),
            corner_radius=12,
            justify="center"
        )
        self.password_entry.pack(pady=(0, 40))
        
        self.login_button = ctk.CTkButton(
            content_frame,
            text="Login",
            command=self.login,
            width=400,
            height=50,
            font=ctk.CTkFont(family="Roboto", size=18, weight="bold"),
            corner_radius=12,
            fg_color="#4e8cff",
            hover_color="#3a70cc"
        )
        self.login_button.pack(pady=(0, 25))
        
        self.notification_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=50)
        self.notification_frame.pack(fill="x", pady=(0, 10))
        
        footer_label = ctk.CTkLabel(
            content_frame,
            text="Code Manager Pro X Tool - @2025",
            font=ctk.CTkFont(family="Roboto", size=14),
            text_color="gray"
        )
        footer_label.pack(pady=(20, 0))
        
        self.password_entry.bind("<Return>", lambda event: self.login())
        
    def show_login_notification(self, message, is_success=False):
        for widget in self.notification_frame.winfo_children():
            widget.destroy()
        
        bg_color = "#2e7d32" if is_success else "#d32f2f"
        icon = "✓" if is_success else "✗"
        
        notification_container = ctk.CTkFrame(
            self.notification_frame, 
            fg_color=bg_color,
            corner_radius=10,
            height=40
        )
        notification_container.pack(fill="x", pady=5)
        notification_container.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            notification_container,
            text=icon,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        icon_label.pack(side="left", padx=(15, 10))
        
        message_label = ctk.CTkLabel(
            notification_container,
            text=message,
            font=ctk.CTkFont(family="Noto Kufi Arabic", size=16),
            text_color="white"
        )
        message_label.pack(side="left", padx=10)
        
        self.animate_notification_entrance(notification_container)
        
        if is_success:
            self.root.after(3000, lambda: self.animate_notification_exit(notification_container))
        
    def show_top_notification(self, message, is_success=True):
        notification = ctk.CTkFrame(
            self.root, 
            corner_radius=10, 
            fg_color="#2e7d32" if is_success else "#d32f2f",
            height=50,
            width=300
        )
        
        notification.place(relx=1.0, rely=0.02, anchor="ne", x=-20)
        
        icon = "✓" if is_success else "✗"
        icon_label = ctk.CTkLabel(
            notification,
            text=icon,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        icon_label.place(relx=0.1, rely=0.5, anchor="w")
        
        message_label = ctk.CTkLabel(
            notification,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        message_label.place(relx=0.3, rely=0.5, anchor="w")
        
        self.notifications.append(notification)
        
        self.animate_top_notification_entrance(notification)
        
        self.root.after(3000, lambda: self.animate_top_notification_exit(notification))
    
    def animate_notification_entrance(self, widget):
        alpha = 0
        def fade_in():
            nonlocal alpha
            alpha += 0.1
            if alpha <= 1.0:
                widget.configure(fg_color=self.blend_colors("#00000000", widget.cget("fg_color"), alpha))
                self.root.after(30, fade_in)
        
        fade_in()
    
    def animate_notification_exit(self, widget):
        original_color = widget.cget("fg_color")
        alpha = 1.0
        def fade_out():
            nonlocal alpha
            alpha -= 0.1
            if alpha >= 0:
                widget.configure(fg_color=self.blend_colors("#00000000", original_color, alpha))
                self.root.after(30, fade_out)
            else:
                widget.destroy()
        
        fade_out()
    
    def animate_top_notification_entrance(self, widget):
        start_x = 20
        current_x = start_x
        
        def slide_in():
            nonlocal current_x
            current_x -= 1
            widget.place(relx=1.0, rely=0.02, anchor="ne", x=-current_x)
            
            if current_x > 0:
                self.root.after(5, slide_in)
        
        slide_in()
    
    def animate_top_notification_exit(self, widget):
        current_x = 0
        
        def slide_out():
            nonlocal current_x
            current_x += 1
            widget.place(relx=1.0, rely=0.02, anchor="ne", x=-current_x)
            
            if current_x < 20:
                self.root.after(5, slide_out)
            else:
                if widget in self.notifications:
                    self.notifications.remove(widget)
                widget.destroy()
        
        slide_out()
    
    def blend_colors(self, color1, color2, alpha):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb
        
        if color1 == "#00000000":
            r1, g1, b1 = 0, 0, 0
        else:
            r1, g1, b1 = hex_to_rgb(color1)
            
        r2, g2, b2 = hex_to_rgb(color2)
        
        r = int(r1 + (r2 - r1) * alpha)
        g = int(g1 + (g2 - g1) * alpha)
        b = int(b1 + (b2 - b1) * alpha)
        
        return rgb_to_hex((r, g, b))
    
    def create_main_interface(self):
        self.login_frame.pack_forget()
        self.title_label.stop_animation()
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_header()
        self.create_content_area()
        self.load_data()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, height=80, fg_color="#252526", corner_radius=15, border_width=2, border_color="#4e8cff")
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        inner_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        inner_frame.pack(expand=True, fill="x", padx=20)
        
        tabs = [("📜 Lua Codes", "luaCodes"), ("🔑 Serials", "serials"), ("👤 Accounts", "accounts"), ("🛠️ Tools", "tools")]
        self.tab_buttons = []
        
        for tab_text, tab_id in tabs:
            button = ctk.CTkButton(
                inner_frame,
                text=tab_text,
                command=lambda t=tab_id: self.switch_tab(t),
                width=140,
                height=40,
                font=ctk.CTkFont(family="Roboto", size=16),
                fg_color="transparent",
                border_width=2,
                border_color="#4e8cff",
                text_color=("gray", "white"),
                hover_color="#3a3a3a"
            )
            button.pack(side="left", padx=8)
            self.tab_buttons.append(button)
        
        welcome_label = ctk.CTkLabel(
            inner_frame, 
            text=f"Welcome, {self.username}",
            font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
            text_color="#4e8cff"
        )
        welcome_label.pack(side="right", padx=15)
        
        logout_button = ctk.CTkButton(
            inner_frame,
            text="Logout",
            command=self.logout,
            width=100,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray", "white"),
            hover_color="#3a3a3a",
            font=ctk.CTkFont(family="Roboto", size=14)
        )
        logout_button.pack(side="right", padx=15)
        
        if self.current_category == "luaCodes":
            self.search_entry = ctk.CTkEntry(
                inner_frame,
                placeholder_text="Search Lua Codes",
                width=200,
                height=40,
                font=ctk.CTkFont(family="Roboto", size=14),
                corner_radius=10
            )
            self.search_entry.pack(side="left", padx=8)
            self.search_entry.bind("<KeyRelease>", self.search_lua_codes)
        
        self.highlight_tab("luaCodes")
    
    def create_content_area(self):
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
    def switch_tab(self, tab):
        self.current_category = tab
        self.highlight_tab(tab)
        self.load_data()
        
    def highlight_tab(self, tab):
        for button in self.tab_buttons:
            button.configure(fg_color="transparent", text_color=("gray", "white"))
        
        for button in self.tab_buttons:
            if tab.lower() in button.cget("command").__code__.co_consts:
                button.configure(fg_color="#4e8cff", text_color="white")
                break
    
    def search_lua_codes(self, event=None):
        search_query = self.search_entry.get().lower()
        thread = threading.Thread(target=self.load_data_thread, args=(search_query,))
        thread.daemon = True
        thread.start()
    
    def load_data(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="Loading data...",
            font=ctk.CTkFont(family="Roboto", size=18),
            text_color="gray"
        )
        loading_label.pack(pady=50)
        
        thread = threading.Thread(target=self.load_data_thread)
        thread.daemon = True
        thread.start()
    
    def load_data_thread(self, search_query=None):
        try:
            params = {
                "username": self.username,
                "password": self.password,
                "category": self.current_category
            }
            if search_query:
                params["search"] = search_query
                
            response = requests.get(f"{API_URL}/data", params=params, timeout=10)
            
            data = response.json()
            
            if data.get("success"):
                self.root.after(0, self.display_data, data.get('data', []))
            else:
                self.root.after(0, self.display_error, data.get('error', 'Unknown error'))
                
        except requests.exceptions.ConnectionError:
            self.root.after(0, self.display_error, "لا يمكن الاتصال بالخادم")
        except Exception as e:
            self.root.after(0, self.display_error, f"خطأ غير متوقع: {str(e)}")
    
    def display_data(self, data):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not data:
            no_data_label = ctk.CTkLabel(
                self.scroll_frame, 
                text="No data available",
                font=ctk.CTkFont(family="Roboto", size=18),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return
        
        if self.current_category == "luaCodes":
            self.display_lua_codes(data)
        elif self.current_category == "serials":
            self.display_serials(data)
        elif self.current_category == "accounts":
            self.display_accounts(data)
        elif self.current_category == "tools":
            self.display_tools(data)
    
    def display_lua_codes(self, codes):
        for code in codes:
            code_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#252526", border_width=2, border_color="#4e8cff")
            code_frame.pack(fill="x", pady=10, padx=5)
            
            title_frame = ctk.CTkFrame(code_frame, fg_color="transparent")
            title_frame.pack(fill="x", padx=15, pady=(15, 10))
            
            title_label = ctk.CTkLabel(
                title_frame, 
                text=code['title'],
                font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
                text_color="#4e8cff"
            )
            title_label.pack(side="left")
            
            view_button = ctk.CTkButton(
                title_frame,
                text="View Code" if not code.get('visible', False) else "Hide Code",
                command=lambda c=code: self.toggle_code_visibility(c),
                width=120,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#4e8cff",
                hover_color="#3a70cc"
            )
            view_button.pack(side="right", padx=(10, 0))
            
            copy_button = ctk.CTkButton(
                title_frame,
                text="Copy Code",
                command=lambda c=code['code']: self.copy_to_clipboard(c),
                width=120,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#2b5b84",
                hover_color="#1e4060"
            )
            copy_button.pack(side="right")
            
            if code.get('visible', False):
                code_text = scrolledtext.ScrolledText(
                    code_frame,
                    width=80,
                    height=12,
                    font=("Consolas", 12),
                    bg="#1e1e1e",
                    fg="#ffffff",
                    insertbackground="white",
                    selectbackground="#3b3b3b",
                    relief="flat",
                    borderwidth=0
                )
                code_text.pack(fill="x", padx=15, pady=(0, 15))
                code_text.insert("1.0", code['code'])
                code_text.configure(state="disabled")
    
    def toggle_code_visibility(self, code):
        thread = threading.Thread(target=self.toggle_code_visibility_thread, args=(code,))
        thread.daemon = True
        thread.start()
    
    def toggle_code_visibility_thread(self, code):
        try:
            response = requests.post(f"{API_URL}/toggle-code", json={
                "username": self.username,
                "password": self.password,
                "category": self.current_category,
                "codeId": code['id']
            }, timeout=10)
            
            data = response.json()
            
            if data.get("success"):
                self.root.after(0, self.load_data)
                
        except Exception as e:
            self.root.after(0, self.show_top_notification, f"Error: {str(e)}", False)
    
    def display_serials(self, serials):
        for serial in serials:
            serial_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#252526", border_width=2, border_color="#4e8cff")
            serial_frame.pack(fill="x", pady=10, padx=5)
            
            info_frame = ctk.CTkFrame(serial_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=15)
            
            ctk.CTkLabel(
                info_frame, 
                text=f"Serial: {serial['serial']}",
                font=ctk.CTkFont(family="Roboto", size=18, weight="bold"),
                text_color="#4e8cff"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame, 
                text=f"Status: {serial['status']}",
                font=ctk.CTkFont(family="Roboto", size=16),
                text_color="green" if serial['status'].lower() == "unbanned" else "red"
            ).pack(anchor="w", pady=(5, 0))
            
            serial_frame2 = ctk.CTkFrame(serial_frame, fg_color="transparent")
            serial_frame2.pack(fill="x", padx=15, pady=(0, 15))
            
            copy_button = ctk.CTkButton(
                serial_frame2,
                text="Copy",
                command=lambda s=serial['serial']: self.copy_to_clipboard(s),
                width=80,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#4e8cff",
                hover_color="#3a70cc"
            )
            copy_button.pack(side="right", padx=(10, 0))
            
            toggle_status_button = ctk.CTkButton(
                serial_frame2,
                text="Toggle Status",
                command=lambda s=serial: self.toggle_serial_status(s),
                width=120,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#2b5b84",
                hover_color="#1e4060"
            )
            toggle_status_button.pack(side="right")
    
    def toggle_serial_status(self, serial):
        thread = threading.Thread(target=self.toggle_serial_status_thread, args=(serial,))
        thread.daemon = True
        thread.start()
    
    def toggle_serial_status_thread(self, serial):
        try:
            new_status = "Unbanned" if serial['status'].lower() == "banned" else "Banned"
            response = requests.post(f"{API_URL}/update-serial-status", json={
                "username": self.username,
                "password": self.password,
                "category": "serials",
                "serialId": serial['id'],
                "newStatus": new_status
            }, timeout=10)
            
            data = response.json()
            
            if data.get("success"):
                self.root.after(0, self.load_data)
                self.root.after(0, self.show_top_notification, f"Serial status updated to {new_status}!")
            else:
                self.root.after(0, self.show_top_notification, f"Error: {data.get('error', 'Unknown error')}", False)
                
        except Exception as e:
            self.root.after(0, self.show_top_notification, f"Error: {str(e)}", False)
    
    def display_accounts(self, accounts):
        for account in accounts:
            account_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#252526", border_width=2, border_color="#4e8cff")
            account_frame.pack(fill="x", pady=10, padx=5)
            
            info_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=15)
            
            ctk.CTkLabel(
                info_frame, 
                text=f"Account Name: {account['accountName']}",
                font=ctk.CTkFont(family="Roboto", size=18, weight="bold"),
                text_color="#4e8cff"
            ).pack(anchor="w")
            
            pass_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
            pass_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            ctk.CTkLabel(
                pass_frame, 
                text=f"Password: {account['password']}",
                font=ctk.CTkFont(family="Consolas", size=16),
                text_color="white"
            ).pack(side="left")
            
            copy_name_button = ctk.CTkButton(
                pass_frame,
                text="Copy Name",
                command=lambda n=account['accountName']: self.copy_to_clipboard(n),
                width=80,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#4e8cff",
                hover_color="#3a70cc"
            )
            copy_name_button.pack(side="right", padx=(10, 0))
            
            copy_pass_button = ctk.CTkButton(
                pass_frame,
                text="Copy Password",
                command=lambda p=account['password']: self.copy_to_clipboard(p),
                width=80,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#4e8cff",
                hover_color="#3a70cc"
            )
            copy_pass_button.pack(side="right")
    
    def display_tools(self, tools):
        for tool in tools:
            tool_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#252526", border_width=2, border_color="#4e8cff")
            tool_frame.pack(fill="x", pady=10, padx=5)
            
            info_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=15)
            
            ctk.CTkLabel(
                info_frame, 
                text=tool['name'],
                font=ctk.CTkFont(family="Roboto", size=20, weight="bold"),
                text_color="#4e8cff"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame, 
                text=f"Download URL: {tool['downloadUrl']}",
                font=ctk.CTkFont(family="Roboto", size=16),
                text_color="white"
            ).pack(anchor="w", pady=(5, 0))
            
            copy_button = ctk.CTkButton(
                info_frame,
                text="Copy URL",
                command=lambda u=tool['downloadUrl']: self.copy_to_clipboard(u),
                width=80,
                height=35,
                font=ctk.CTkFont(family="Roboto", size=14),
                fg_color="#4e8cff",
                hover_color="#3a70cc"
            )
            copy_button.pack(anchor="w", pady=(5, 0))
    
    def display_error(self, error_message):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.scroll_frame, 
            text=f"Error: {error_message}",
            font=ctk.CTkFont(family="Noto Kufi Arabic", size=16),
            text_color="red"
        )
        error_label.pack(pady=50)
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_top_notification("Copied to clipboard!")
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_login_notification("الرجاء إدخال اسم المستخدم وكلمة المرور", False)
            return
        
        self.username = username
        self.password = password
        
        self.login_button.configure(state="disabled", text="Logging in...")
        self.show_login_notification("جاري التحقق من بيانات الدخول...", False)
        
        thread = threading.Thread(target=self.login_thread)
        thread.daemon = True
        thread.start()
    
    def login_thread(self):
        try:
            response = requests.post(f"{API_URL}/login", json={
                "username": self.username,
                "password": self.password
            }, timeout=10)
            
            data = response.json()
            
            if data.get("success"):
                self.root.after(0, self.login_success)
            else:
                self.root.after(0, self.login_failed, data.get('error', 'Unknown error'))
                
        except requests.exceptions.ConnectionError:
            self.root.after(0, self.login_failed, "لا يمكن الاتصال بالخادم")
        except Exception as e:
            self.root.after(0, self.login_failed, f"خطأ غير متوقع: {str(e)}")
    
    def login_success(self):
        self.show_login_notification("تم تسجيل الدخول بنجاح!", True)
        self.root.after(1000, self.create_main_interface)
    
    def login_failed(self, error_message):
        self.login_button.configure(state="normal", text="Login")
        self.show_login_notification(f"فشل تسجيل الدخول: {error_message}", False)
    
    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True, padx=150, pady=150)
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.login_button.configure(state="normal", text="Login")
        
        for widget in self.notification_frame.winfo_children():
            widget.destroy()
        
        self.title_label.start_animation()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernApp()
    app.run()