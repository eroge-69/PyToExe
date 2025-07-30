# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import requests
import os
import sys
import ctypes
import json
import webbrowser
from datetime import datetime
import platform

# --- Cấu hình và Dữ liệu Ngôn ngữ ---

LANGUAGES = {
    "vi": {
        "title": "NMHRUBY - Giao diện Tiện ích",
        "current_time": "Thời gian hiện tại:",
        "file": "Tệp",
        "exit": "Thoát",
        "options": "Tùy chọn",
        "language": "Ngôn ngữ",
        "help": "Trợ giúp",
        "about": "Giới thiệu",
        "confirm": "Thực thi",
        "status_enabled": "Trạng thái: Đã bật",
        "status_disabled": "Trạng thái: Đã tắt",
        "status_checking": "Đang kiểm tra...",
        "group1_title": "Tối ưu Windows (Windows Optimize)",
        "win_update": "Tắt/Bật Windows Update",
        "del_bloatware": "Gỡ bỏ Bloatware (Ứng dụng rác)",
        "prevent_bloatware": "Ngăn chặn Bloatware tự cài lại",
        "del_edge": "Gỡ bỏ Microsoft Edge",
        "win_security": "Tắt/Bật Windows Security",
        "group2_title": "Cài đặt Phần mềm (Installer Software)",
        "install_coccoc": "Cài đặt Cốc Cốc",
        "install_chrome": "Cài đặt Google Chrome",
        "install_winrar": "Cài đặt WinRAR (Đã kích hoạt)",
        "install_7zip": "Cài đặt 7-Zip",
        "install_ultraviewer": "Cài đặt UltraViewer",
        "install_teamviewer": "Cài đặt TeamViewer",
        "install_anydesk": "Cài đặt AnyDesk",
        "install_revo": "Cài đặt Revo Uninstaller (Đã kích hoạt)",
        "group3_title": "Kích hoạt Windows & Office",
        "win_office_active": "Chạy công cụ Kích hoạt Windows & Office",
        "password_msg_title": "Mật khẩu yêu cầu",
        "password_msg_content": "Password Login Tools: nmhruby",
        "about_title": "Giới thiệu về NMHRUBY",
        "about_message": """Xin chào các bạn! Tools được Code và phát triển bởi Nguyễn Mạnh Hùng.
Mình xin tự giới thiệu qua bản thân:
Mình là Nguyễn Mạnh Hùng, sinh năm 2006 tại Hà Nội.
Mình có niềm đam mê lập trình từ lớp 5.

Nếu có thắc mắc hay lỗi chỗ nào xin đóng góp vào:""",
        "about_button": "Facebook của Hùng",
        "about_footer": "Cảm ơn bạn đã tin chọn :3. Sẽ còn cập nhật nhiều tính năng hơn.",
        "app_info": "Phần mềm: NMHRUBY - Tiện ích hoàn thiện Windows\nTác giả: Nguyễn Mạnh Hùng\nPhiên bản: v1.3.5\nTrang chủ: https://hungthichcode.github.io/nmhruby/",
        "task_running_title": "Đang thực thi",
        "task_running_msg": "Đang thực hiện các tác vụ. Vui lòng không tắt ứng dụng.",
        "task_done_title": "Hoàn thành",
        "task_done_msg": "Tất cả các tác vụ đã chọn đã được thực hiện xong!",
        "admin_required_title": "Yêu cầu quyền Admin",
        "admin_required_msg": "Ứng dụng này cần quyền Administrator để hoạt động. Vui lòng chạy lại với quyền Administrator.",
        "select_bloatware_title": "Chọn Bloatware để gỡ bỏ",
        "select_all": "Chọn tất cả",
        "deselect_all": "Bỏ chọn tất cả",
        "uninstall": "Gỡ cài đặt",
        "installation_success": "{} đã được cài đặt thành công!",
        "downloading": "Đang tải {}...",
        "installing": "Đang cài đặt {}...",
        "deleting": "Đang xóa tệp tạm...",
        "running_tool": "Đang chạy công cụ...",
        "error_download": "Lỗi khi tải {}: {}",
        "error_install": "Lỗi khi cài đặt {}: {}",
        "error_general_title": "Đã có lỗi xảy ra",
        "error_general_msg": "Đã có lỗi xảy ra: {}"
    },
    "en": {
        "title": "NMHRUBY - Utility Interface",
        "current_time": "Current Time:",
        "file": "File",
        "exit": "Exit",
        "options": "Options",
        "language": "Language",
        "help": "Help",
        "about": "About",
        "confirm": "Confirm",
        "status_enabled": "Status: Enabled",
        "status_disabled": "Status: Disabled",
        "status_checking": "Checking...",
        "group1_title": "Windows Optimize",
        "win_update": "Disable/Enable Windows Update",
        "del_bloatware": "Delete Bloatware",
        "prevent_bloatware": "Prevent Bloatware Re-install",
        "del_edge": "Delete Microsoft Edge",
        "win_security": "Disable/Enable Windows Security",
        "group2_title": "Installer Software",
        "install_coccoc": "Install Coc Coc",
        "install_chrome": "Install Google Chrome",
        "install_winrar": "Install WinRAR (Activated)",
        "install_7zip": "Install 7-Zip",
        "install_ultraviewer": "Install UltraViewer",
        "install_teamviewer": "Install TeamViewer",
        "install_anydesk": "Install AnyDesk",
        "install_revo": "Install Revo Uninstaller (Activated)",
        "group3_title": "Windows & Office Activation",
        "win_office_active": "Run Windows & Office Activation Tool",
        "password_msg_title": "Password Required",
        "password_msg_content": "Password Login Tools: nmhruby",
        "about_title": "About NMHRUBY",
        "about_message": """Hello! This tool is coded and developed by Nguyen Manh Hung.
Let me introduce myself:
I'm Nguyen Manh Hung, born in 2006 in Hanoi.
I've had a passion for programming since 5th grade.

If you have any questions or find any bugs, please contribute at:""",
        "about_button": "Hung's Facebook",
        "about_footer": "Thank you for your trust :3. More features will be updated. Follow me.",
        "app_info": "Software: NMHRUBY - Windows Finishing Utility\nAuthor: Nguyen Manh Hung\nVersion: v1.3.5\nHomepage: https://hungthichcode.github.io/nmhruby/",
        "task_running_title": "Executing",
        "task_running_msg": "Executing tasks. Please do not close the application.",
        "task_done_title": "Completed",
        "task_done_msg": "All selected tasks have been completed!",
        "admin_required_title": "Admin Rights Required",
        "admin_required_msg": "This application requires administrator privileges to function. Please restart as an administrator.",
        "select_bloatware_title": "Select Bloatware to Remove",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "uninstall": "Uninstall",
        "installation_success": "{} has been installed successfully!",
        "downloading": "Downloading {}...",
        "installing": "Installing {}...",
        "deleting": "Deleting temporary file...",
        "running_tool": "Running tool...",
        "error_download": "Error downloading {}: {}",
        "error_install": "Error installing {}: {}",
        "error_general_title": "An Error Occurred",
        "error_general_msg": "An error occurred: {}"
    }
}

# --- Lớp Ứng dụng chính ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "vi"
        self.lang_data = LANGUAGES[self.current_lang]

        # Cấu hình cửa sổ chính
        self.title(self.lang_data["title"])
        self.geometry("700x800") # Tăng chiều cao để chứa group 3
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Biến lưu trạng thái checkbox
        self.vars = {
            "win_update": ctk.BooleanVar(),
            "del_bloatware": ctk.BooleanVar(),
            "prevent_bloatware": ctk.BooleanVar(),
            "del_edge": ctk.BooleanVar(),
            "win_security": ctk.BooleanVar(),
            "install_coccoc": ctk.BooleanVar(),
            "install_chrome": ctk.BooleanVar(),
            "install_winrar": ctk.BooleanVar(),
            "install_7zip": ctk.BooleanVar(),
            "install_ultraviewer": ctk.BooleanVar(),
            "install_teamviewer": ctk.BooleanVar(),
            "install_anydesk": ctk.BooleanVar(),
            "install_revo": ctk.BooleanVar(),
            "win_office_active": ctk.BooleanVar(),
        }

        # Tạo các thành phần giao diện
        self.create_widgets()
        self.update_language()
        self.update_time()

    def get_string(self, key):
        return self.lang_data.get(key, key)

    def create_widgets(self):
        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.get_string("file"), menu=self.file_menu)
        self.file_menu.add_command(label=self.get_string("exit"), command=self.quit)

        # Options Menu
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.get_string("options"), menu=self.options_menu)
        self.lang_menu = tk.Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label=self.get_string("language"), menu=self.lang_menu)
        self.lang_menu.add_command(label="Tiếng Việt", command=lambda: self.change_language("vi"))
        self.lang_menu.add_command(label="English", command=lambda: self.change_language("en"))
        
        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.get_string("help"), menu=self.help_menu)
        self.help_menu.add_command(label=self.get_string("about"), command=self.show_about)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.pack(fill="x", pady=5, padx=5)
        self.time_label = ctk.CTkLabel(header_frame, text=self.get_string("current_time"), font=ctk.CTkFont(size=14, weight="bold"))
        self.time_label.pack(pady=10)

        # --- Main Frame for scrolling ---
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Group 1: Windows Optimize ---
        self.group1 = CollapsibleFrame(main_frame, title=self.get_string("group1_title"))
        self.group1.pack(fill="x", pady=5)
        
        self.win_update_check = self.create_checkbox(self.group1.content_frame, "win_update", self.get_string("win_update"))
        self.win_update_status = ctk.CTkLabel(self.group1.content_frame, text=self.get_string("status_checking"), text_color="yellow")
        self.win_update_status.pack(anchor="w", padx=40)
        
        self.create_checkbox(self.group1.content_frame, "del_bloatware", self.get_string("del_bloatware"))
        self.create_checkbox(self.group1.content_frame, "prevent_bloatware", self.get_string("prevent_bloatware"))
        self.create_checkbox(self.group1.content_frame, "del_edge", self.get_string("del_edge"))
        
        self.win_security_check = self.create_checkbox(self.group1.content_frame, "win_security", self.get_string("win_security"))
        self.win_security_status = ctk.CTkLabel(self.group1.content_frame, text=self.get_string("status_checking"), text_color="yellow")
        self.win_security_status.pack(anchor="w", padx=40)

        self.confirm_button1 = ctk.CTkButton(self.group1.content_frame, text=self.get_string("confirm"), command=lambda: self.start_tasks(1))
        self.confirm_button1.pack(pady=10)
        
        # --- Group 2: Installer Software ---
        self.group2 = CollapsibleFrame(main_frame, title=self.get_string("group2_title"))
        self.group2.pack(fill="x", pady=5)

        self.create_checkbox(self.group2.content_frame, "install_coccoc", self.get_string("install_coccoc"))
        self.create_checkbox(self.group2.content_frame, "install_chrome", self.get_string("install_chrome"))
        self.create_checkbox(self.group2.content_frame, "install_winrar", self.get_string("install_winrar"))
        self.create_checkbox(self.group2.content_frame, "install_7zip", self.get_string("install_7zip"))
        self.create_checkbox(self.group2.content_frame, "install_ultraviewer", self.get_string("install_ultraviewer"))
        self.create_checkbox(self.group2.content_frame, "install_teamviewer", self.get_string("install_teamviewer"))
        self.create_checkbox(self.group2.content_frame, "install_anydesk", self.get_string("install_anydesk"))
        self.create_checkbox(self.group2.content_frame, "install_revo", self.get_string("install_revo"))

        self.confirm_button2 = ctk.CTkButton(self.group2.content_frame, text=self.get_string("confirm"), command=lambda: self.start_tasks(2))
        self.confirm_button2.pack(pady=10)

        # --- Group 3: Windows Active & Office ---
        self.group3 = CollapsibleFrame(main_frame, title=self.get_string("group3_title"))
        self.group3.pack(fill="x", pady=5)
        self.win_office_check = self.create_checkbox(self.group3.content_frame, "win_office_active", self.get_string("win_office_active"))
        self.confirm_button3 = ctk.CTkButton(self.group3.content_frame, text=self.get_string("confirm"), command=lambda: self.start_tasks(3))
        self.confirm_button3.pack(pady=10)

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", font=ctk.CTkFont(size=12))
        self.status_bar.pack(side="bottom", fill="x", padx=5)

        # Check initial status
        self.check_initial_status()

    def create_checkbox(self, parent, var_name, text):
        checkbox = ctk.CTkCheckBox(parent, text=text, variable=self.vars[var_name])
        checkbox.pack(anchor="w", padx=20, pady=5)
        return checkbox

    def update_language(self):
        self.lang_data = LANGUAGES[self.current_lang]
        self.title(self.get_string("title"))
        
        # Update Menu
        self.menu_bar.entryconfigure(1, label=self.get_string("file"))
        self.menu_bar.entryconfigure(2, label=self.get_string("options"))
        self.menu_bar.entryconfigure(3, label=self.get_string("help"))
        self.file_menu.entryconfigure(1, label=self.get_string("exit"))
        self.options_menu.entryconfigure(1, label=self.get_string("language"))
        self.help_menu.entryconfigure(1, label=self.get_string("about"))
        
        # Update widgets
        self.time_label.configure(text=self.get_string("current_time") + " " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.group1.title_label.configure(text=self.get_string("group1_title"))
        self.group2.title_label.configure(text=self.get_string("group2_title"))
        self.group3.title_label.configure(text=self.get_string("group3_title"))
        
        self.win_update_check.configure(text=self.get_string("win_update"))
        self.win_security_check.configure(text=self.get_string("win_security"))
        self.win_office_check.configure(text=self.get_string("win_office_active"))
        
        self.confirm_button1.configure(text=self.get_string("confirm"))
        self.confirm_button2.configure(text=self.get_string("confirm"))
        self.confirm_button3.configure(text=self.get_string("confirm"))

        # ... (cần cập nhật các checkbox khác nếu muốn)
        
    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.update_language()

    def update_time(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.configure(text=f"{self.get_string('current_time')} {now}")
        self.after(1000, self.update_time)

    def show_about(self):
        about_win = ctk.CTkToplevel(self)
        about_win.title(self.get_string("about_title"))
        about_win.geometry("500x350")
        about_win.transient(self)
        about_win.grab_set()

        text_frame = ctk.CTkFrame(about_win)
        text_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(text_frame, text=self.get_string("app_info"), justify="left").pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(text_frame, text="-"*50).pack(fill="x", padx=10)
        ctk.CTkLabel(text_frame, text=self.get_string("about_message"), wraplength=450, justify="left").pack(anchor="w", padx=10, pady=5)
        
        fb_button = ctk.CTkButton(text_frame, text=self.get_string("about_button"), 
                                  command=lambda: webbrowser.open("https://www.facebook.com/NMHRUBY"))
        fb_button.pack(pady=10)
        
        ctk.CTkLabel(text_frame, text=self.get_string("about_footer")).pack(pady=5)
        
    def check_initial_status(self):
        threading.Thread(target=self._check_status_thread, daemon=True).start()

    def _check_status_thread(self):
        try:
            result = subprocess.run(['sc', 'query', 'wuauserv'], capture_output=True, text=True, startupinfo=startup_info())
            if "RUNNING" in result.stdout:
                self.win_update_status.configure(text=self.get_string("status_enabled"), text_color="lightgreen")
            else:
                self.win_update_status.configure(text=self.get_string("status_disabled"), text_color="orange")
        except Exception:
            self.win_update_status.configure(text="Status Unknown", text_color="red")
            
        try:
            result = subprocess.run(['reg', 'query', r'HKLM\SOFTWARE\Policies\Microsoft\Windows Defender', '/v', 'DisableAntiSpyware'], capture_output=True, text=True, startupinfo=startup_info())
            if "0x1" in result.stdout:
                self.win_security_status.configure(text=self.get_string("status_disabled"), text_color="orange")
            else:
                self.win_security_status.configure(text=self.get_string("status_enabled"), text_color="lightgreen")
        except Exception:
             self.win_security_status.configure(text=self.get_string("status_enabled"), text_color="lightgreen")

    def start_tasks(self, group_num):
        threading.Thread(target=self.run_tasks, args=(group_num,), daemon=True).start()

    def run_tasks(self, group_num):
        messagebox.showinfo(self.get_string("task_running_title"), self.get_string("task_running_msg"))
        
        if group_num == 1:
            if self.vars["win_update"].get():
                self.status_bar.configure(text="Disabling Windows Update...")
                run_command(r'sc config wuauserv start=disabled & sc stop wuauserv & reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f')
            if self.vars["del_bloatware"].get():
                self.status_bar.configure(text="Removing Bloatware...")
                self.select_and_remove_bloatware()
            if self.vars["prevent_bloatware"].get():
                self.status_bar.configure(text="Preventing Bloatware...")
                run_command(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsConsumerFeatures /t REG_DWORD /d 1 /f')
            if self.vars["del_edge"].get():
                self.status_bar.configure(text="Removing Microsoft Edge...")
                self.remove_edge()
            if self.vars["win_security"].get():
                self.status_bar.configure(text="Disabling Windows Security...")
                run_command(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f')
        
        elif group_num == 2:
            installers = {
                "install_coccoc": ("Cốc Cốc", "https://files.coccoc.com/browser/installer/coccoc_vi.exe", "/S"),
                "install_chrome": ("Google Chrome", "https://dl.google.com/chrome/install/375.122/chrome_installer.exe", "/silent /install"),
                "install_winrar": ("WinRAR", f"https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x{get_bitness()}/winrar-x{get_bitness()}-624vi.exe", "/S"),
                "install_7zip": ("7-Zip", f"https://www.7-zip.org/a/7z2406-x{get_bitness()}.exe", "/S"),
                "install_ultraviewer": ("UltraViewer", "https://ultraviewer.net/vi/UltraViewer_setup_6.6_vi.exe", "/VERYSILENT /SUPPRESSMSGBOXES"),
                "install_teamviewer": ("TeamViewer", "https://download.teamviewer.com/download/TeamViewer_Setup_x64.exe", "/S"),
                "install_anydesk": ("AnyDesk", "https://download.anydesk.com/AnyDesk.exe", "--install \"C:\\Program Files (x86)\\AnyDesk\" --start-with-win --silent --create-desktop-icon"),
                "install_revo": ("Revo Uninstaller", "https://www.revouninstaller.com/download/revosetup.exe", "/VERYSILENT /SUPPRESSMSGBOXES"),
            }
            for key, (name, url, args) in installers.items():
                if self.vars[key].get():
                    self.install_software(name, url, args)
                    if key == "install_winrar":
                        self.activate_winrar()
                    if key == "install_revo":
                        self.activate_revo()
        
        elif group_num == 3:
            if self.vars["win_office_active"].get():
                self.run_activation_tool()

        self.status_bar.configure(text="Ready")
        messagebox.showinfo(self.get_string("task_done_title"), self.get_string("task_done_msg"))
        self.check_initial_status()

    def run_activation_tool(self):
        messagebox.showinfo(self.get_string("password_msg_title"), self.get_string("password_msg_content"))
        
        # URL trỏ đến file thô, không phải trang hiển thị của Github
        tool_url = "https://raw.githubusercontent.com/hungthichcode/nmhruby-tools-windows/master/Windows%20Office%20Tools%20v3.2.3%20by%20NMHRUBY%20Repack.exe"
        
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_name = os.path.basename(tool_url)
        dest_path = os.path.join(desktop_path, file_name)

        try:
            # Tải file
            self.status_bar.configure(text=self.get_string("downloading").format(file_name))
            with requests.get(tool_url, stream=True) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Chạy file và đợi nó kết thúc
            self.status_bar.configure(text=self.get_string("running_tool"))
            process = subprocess.Popen(f'"{dest_path}"')
            process.wait() # Đợi cho đến khi người dùng đóng chương trình
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror(self.get_string("error_download").format(file_name, e))
        except Exception as e:
            messagebox.showerror(self.get_string("error_general_title"), self.get_string("error_general_msg").format(e))
        finally:
            # Dọn dẹp: Xóa file đã tải về sau khi chạy xong
            if os.path.exists(dest_path):
                self.status_bar.configure(text=self.get_string("deleting"))
                os.remove(dest_path)

    def remove_edge(self):
        try:
            edge_path = ""
            for root, dirs, files in os.walk(r"C:\Program Files (x86)\Microsoft\Edge\Application"):
                if "setup.exe" in files:
                    edge_path = os.path.join(root, "setup.exe")
                    break
            if edge_path:
                command = f'"{edge_path}" --uninstall --system-level --verbose-logging --force-uninstall'
                run_command(command)
            else:
                messagebox.showerror("Error", "Could not find Microsoft Edge setup.exe.")
        except Exception as e:
            messagebox.showerror(self.get_string("error_general_title"), self.get_string("error_general_msg").format(e))

    def select_and_remove_bloatware(self):
        self.after(0, self._create_bloatware_window)

    def _create_bloatware_window(self):
        try:
            ps_command = "Get-AppxPackage | Select Name, PackageFullName | ConvertTo-Json"
            result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, startupinfo=startup_info())
            apps = json.loads(result.stdout)
            
            if not apps:
                messagebox.showinfo("Info", "No bloatware found or PowerShell error.")
                return

            win = ctk.CTkToplevel(self)
            win.title(self.get_string("select_bloatware_title"))
            win.geometry("500x600")
            win.transient(self)
            win.grab_set()

            scroll_frame = ctk.CTkScrollableFrame(win)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            app_vars = {}
            for app in apps:
                if isinstance(app, dict) and 'Name' in app:
                    var = ctk.BooleanVar()
                    name = app['Name']
                    pkg_full_name = app['PackageFullName']
                    app_vars[pkg_full_name] = var
                    ctk.CTkCheckBox(scroll_frame, text=name, variable=var).pack(anchor="w", padx=5)

            def select_all(value):
                for var in app_vars.values():
                    var.set(value)

            def do_uninstall():
                win.destroy()
                uninstall_list = [pkg for pkg, var in app_vars.items() if var.get()]
                if uninstall_list:
                    threading.Thread(target=self._uninstall_thread, args=(uninstall_list,), daemon=True).start()

            button_frame = ctk.CTkFrame(win)
            button_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(button_frame, text=self.get_string("select_all"), command=lambda: select_all(True)).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text=self.get_string("deselect_all"), command=lambda: select_all(False)).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text=self.get_string("uninstall"), command=do_uninstall).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror(self.get_string("error_general_title"), f"Failed to get app list: {e}")

    def _uninstall_thread(self, packages_to_remove):
        for pkg in packages_to_remove:
            self.status_bar.configure(text=f"Removing {pkg[:30]}...")
            ps_command = f"Remove-AppxPackage -Package '{pkg}' -AllUsers"
            run_command(f'powershell -Command "{ps_command}"')
        self.status_bar.configure(text="Bloatware removal complete.")

    def install_software(self, name, url, args):
        temp_dir = os.path.join(os.environ["TEMP"], "NMHRUBY_Downloads")
        os.makedirs(temp_dir, exist_ok=True)
        installer_path = os.path.join(temp_dir, os.path.basename(url))

        try:
            self.status_bar.configure(text=self.get_string("downloading").format(name))
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(installer_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            self.status_bar.configure(text=self.get_string("installing").format(name))
            run_command(f'"{installer_path}" {args}')
            
            self.status_bar.configure(text=self.get_string("installation_success").format(name))
        
        except requests.exceptions.RequestException as e:
            messagebox.showerror(self.get_string("error_download").format(name, e))
        except Exception as e:
            messagebox.showerror(self.get_string("error_install").format(name, e))
        finally:
            if os.path.exists(installer_path):
                os.remove(installer_path)

    def activate_winrar(self):
        self.status_bar.configure(text="Activating WinRAR...")
        key_url = "https://raw.githubusercontent.com/hungthichcode/nmhruby-tools-windows/master/rarreg.key"
        dest_path = r"C:\Program Files\WinRAR\rarreg.key"
        try:
            r = requests.get(key_url)
            r.raise_for_status()
            with open(dest_path, 'w') as f:
                f.write(r.text)
            self.status_bar.configure(text="WinRAR activated.")
        except Exception as e:
            self.status_bar.configure(text=f"WinRAR activation failed: {e}")

    def activate_revo(self):
        self.status_bar.configure(text="Activating Revo Uninstaller...")
        lic_url = "https://raw.githubusercontent.com/hungthichcode/nmhruby-tools-windows/master/revouninstallerpro5.lic"
        dest_dir = r"C:\ProgramData\VS Revo Group\Revo Uninstaller Pro"
        dest_path = os.path.join(dest_dir, "revouninstallerpro5.lic")
        try:
            os.makedirs(dest_dir, exist_ok=True)
            r = requests.get(lic_url)
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                f.write(r.content)
            self.status_bar.configure(text="Revo Uninstaller activated.")
        except Exception as e:
            self.status_bar.configure(text=f"Revo activation failed: {e}")

# --- Lớp tùy chỉnh cho Group có thể thu gọn ---

class CollapsibleFrame(ctk.CTkFrame):
    def __init__(self, parent, title=""):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.is_collapsed = True

        self.title_frame = ctk.CTkFrame(self, corner_radius=8)
        self.title_frame.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.title_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.pack(side="left", padx=10)
        
        self.toggle_button = ctk.CTkButton(self.title_frame, text="+", width=30, command=self.toggle)
        self.toggle_button.pack(side="right")

        self.content_frame = ctk.CTkFrame(self)

    def toggle(self):
        if self.is_collapsed:
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.toggle_button.configure(text="-")
        else:
            self.content_frame.grid_forget()
            self.toggle_button.configure(text="+")
        self.is_collapsed = not self.is_collapsed

# --- Các hàm tiện ích ---

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def startup_info():
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
    return info

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, startupinfo=startup_info())
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr.decode(errors='ignore')}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_bitness():
    return '64' if platform.machine().endswith('64') else '32'

# --- Điểm khởi chạy ứng dụng ---

if __name__ == "__main__":
    if is_admin():
        app = App()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

"""
--- HƯỚNG DẪN ĐÓNG GÓI THÀNH FILE .EXE ---

Để biến file script Python này thành một file .exe duy nhất có thể chạy trên mọi máy Windows
mà không cần cài Python, bạn hãy làm theo các bước sau:

1. Mở Command Prompt (CMD) hoặc PowerShell trên Windows.

2. Cài đặt các thư viện cần thiết:
   Bạn cần cài đặt các thư viện mà script này sử dụng, cộng thêm `pyinstaller` để đóng gói.
   Chạy các lệnh sau:
   pip install customtkinter
   pip install requests
   pip install pyinstaller

3. Điều hướng đến thư mục chứa file script:
   Sử dụng lệnh `cd` để di chuyển đến nơi bạn đã lưu file `nmhruby_utility.py`.
   Ví dụ: cd C:\\Users\\YourUser\\Desktop

4. Chạy lệnh PyInstaller để đóng gói:
   Sao chép và dán lệnh dưới đây vào CMD/PowerShell rồi nhấn Enter. Lệnh này sẽ gom tất cả
   lại thành một file .exe duy nhất, không hiện cửa sổ console màu đen khi chạy.

   pyinstaller --name="NMHRUBY Utility" --onefile --windowed --icon=NONE "nmhruby_utility.py"

   - `--name`: Đặt tên cho file .exe của bạn.
   - `--onefile`: Tạo ra một file .exe duy nhất.
   - `--windowed`: Ẩn cửa sổ dòng lệnh màu đen khi ứng dụng chạy.
   - `--icon=NONE`: Không sử dụng icon. Bạn có thể thay `NONE` bằng đường dẫn tới một file icon `.ico` nếu có (ví dụ: `--icon="my_icon.ico"`)

5. Tìm file .exe:
   Sau khi PyInstaller chạy xong, nó sẽ tạo ra một vài thư mục. File .exe của bạn sẽ nằm
   trong thư mục con có tên là `dist`.

   Ví dụ: C:\\Users\\YourUser\\Desktop\\dist\\NMHRUBY Utility.exe

Bây giờ bạn có thể chia sẻ file .exe này cho người khác sử dụng.
"""
