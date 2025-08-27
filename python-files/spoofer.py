import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import winreg as reg
import random
import string
import os
import sys
import ctypes
import shutil
import logging
import threading
from datetime import datetime
import re


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("spoofer.log"),
    ]
)
logger = logging.getLogger("spoofer")


class ModernSpoofer:
    def __init__(self, root):
        self.root = root
        self.root.title("TEMIC SPOOFER")
        self.root.geometry("900x600")
        self.root.configure(bg="#0d0d0d")
        self.root.minsize(800, 550)

        # Center window
        self.center_window()

        # Theme variables
        self.dark_mode = True
        self.colors = {
            "dark": {
                "bg": "#0d0d0d",
                "header_bg": "#0a0a0a",
                "card_bg": "#151515",
                "accent": "#4d88ff",
                "accent_hover": "#5d98ff",
                "text": "#e6e6e6",
                "text_secondary": "#a0a0a0",
                "border": "#2a2a2a",
                "success": "#00cc66",
                "warning": "#ff9900",
                "error": "#ff3333",
                "tab_bg": "#151515",
                "tab_selected": "#4d88ff"
            },
            "light": {
                "bg": "#f2f2f2",
                "header_bg": "#e6e6e6",
                "card_bg": "#ffffff",
                "accent": "#4d88ff",
                "accent_hover": "#3d78ef",
                "text": "#1a1a1a",
                "text_secondary": "#666666",
                "border": "#d9d9d9",
                "success": "#00aa55",
                "warning": "#e68a00",
                "error": "#dd2222",
                "tab_bg": "#ffffff",
                "tab_selected": "#4d88ff"
            }
        }

        # Current theme
        self.theme = self.colors["dark"]

        # Store original values for comparison
        self.original_values = {}

        # Create main container
        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create content area
        self.create_content()

        # Create settings menu (initially hidden)
        self.create_settings_menu()

        # Apply theme
        self.apply_theme()

        # Capture original values
        self.capture_original_values()

    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg=self.theme["header_bg"], relief='flat', bd=0, height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # Title
        title = tk.Label(title_bar, text="TEMIC SPOOFER v1.0.0", font=("Segoe UI", 10),
                         bg=self.theme["header_bg"], fg=self.theme["text_secondary"])
        title.pack(side=tk.LEFT, padx=10)

        # Buttons
        buttons = tk.Frame(title_bar, bg=self.theme["header_bg"])
        buttons.pack(side=tk.RIGHT)

        # Minimize button
        min_btn = tk.Label(buttons, text="─", font=("Segoe UI", 12),
                           bg=self.theme["header_bg"], fg=self.theme["text"],
                           cursor="hand2")
        min_btn.pack(side=tk.LEFT, padx=5)
        min_btn.bind("<Button-1>", lambda e: self.root.iconify())

        # Close button
        close_btn = tk.Label(buttons, text="×", font=("Segoe UI", 16),
                             bg=self.theme["header_bg"], fg=self.theme["text"],
                             cursor="hand2")
        close_btn.pack(side=tk.LEFT, padx=5)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # Bind dragging functionality
        title_bar.bind('<Button-1>', self.start_move)
        title_bar.bind('<ButtonRelease-1>', self.stop_move)
        title_bar.bind('<B1-Motion>', self.on_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_content(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Style the notebook
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.theme["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab",
                             background=self.theme["tab_bg"],
                             foreground=self.theme["text"],
                             padding=[20, 5],
                             font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.theme["tab_selected"])],
                       foreground=[("selected", "#ffffff")])

        # Create tabs
        self.create_main_tab()
        self.create_changes_tab()
        self.create_credits_tab()

    def create_main_tab(self):
        main_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(main_tab, text="Main")

        # Create card for spoofing options
        options_card = tk.Frame(main_tab, bg=self.theme["card_bg"], relief=tk.FLAT, bd=0)
        options_card.pack(fill=tk.X, padx=10, pady=10)

        # Card title
        title = tk.Label(options_card, text="Spoofing Options", font=("Segoe UI", 14, "bold"),
                         bg=self.theme["card_bg"], fg=self.theme["text"])
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))

        # Options frame
        options_frame = tk.Frame(options_card, bg=self.theme["card_bg"])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.hwid_var = tk.BooleanVar(value=True)
        self.mac_var = tk.BooleanVar(value=True)
        self.wmi_var = tk.BooleanVar(value=True)
        self.logs_var = tk.BooleanVar(value=True)

        # Create stylish checkboxes
        self.create_checkbox(options_frame, "Spoof HWID", self.hwid_var).pack(anchor=tk.W, pady=5)
        self.create_checkbox(options_frame, "Spoof MAC Address", self.mac_var).pack(anchor=tk.W, pady=5)
        self.create_checkbox(options_frame, "Spoof WMI Data", self.wmi_var).pack(anchor=tk.W, pady=5)
        self.create_checkbox(options_frame, "Clear System Logs", self.logs_var).pack(anchor=tk.W, pady=5)

        # Action buttons
        button_frame = tk.Frame(main_tab, bg=self.theme["bg"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Spoof button
        spoof_btn = tk.Button(button_frame, text="START SPOOFING", font=("Segoe UI", 12, "bold"),
                              bg=self.theme["accent"], fg="#ffffff", relief=tk.FLAT,
                              cursor="hand2", bd=0, padx=30, pady=12,
                              command=self.start_spoofing_thread)
        spoof_btn.pack(side=tk.LEFT, padx=(0, 10))
        spoof_btn.bind("<Enter>", lambda e: spoof_btn.config(bg=self.theme["accent_hover"]))
        spoof_btn.bind("<Leave>", lambda e: spoof_btn.config(bg=self.theme["accent"]))

        # Reboot button
        reboot_btn = tk.Button(button_frame, text="REBOOT SYSTEM", font=("Segoe UI", 10, "bold"),
                               bg=self.theme["card_bg"], fg=self.theme["text"], relief=tk.FLAT,
                               cursor="hand2", bd=1, padx=20, pady=10,
                               command=self.reboot_system)
        reboot_btn.pack(side=tk.LEFT)
        reboot_btn.config(highlightbackground=self.theme["border"], highlightcolor=self.theme["border"],
                          highlightthickness=1)
        reboot_btn.bind("<Enter>", lambda e: reboot_btn.config(bg=self.theme["accent"], fg="#ffffff"))
        reboot_btn.bind("<Leave>", lambda e: reboot_btn.config(bg=self.theme["card_bg"], fg=self.theme["text"]))

        # Status area
        status_card = tk.Frame(main_tab, bg=self.theme["card_bg"], relief=tk.FLAT, bd=0)
        status_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status title
        status_title = tk.Label(status_card, text="Logs", font=("Segoe UI", 14, "bold"),
                                bg=self.theme["card_bg"], fg=self.theme["text"])
        status_title.pack(anchor=tk.W, padx=15, pady=(15, 10))

        # Status text - now shows all logs
        self.status_text = scrolledtext.ScrolledText(
            status_card,
            wrap=tk.WORD,
            width=70,
            height=10,
            bg="#1a1a1a",
            fg=self.theme["text"],
            font=("Consolas", 9),
            relief=tk.FLAT,
            bd=0
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.status_text.config(state=tk.DISABLED)

        # Add log handler to display logs in the text widget
        self.log_handler = TextHandler(self.status_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(self.log_handler)

        # Initial status
        logger.info("TEMIC SPOOFER v1.0.0 started successfully")

    def create_changes_tab(self):
        changes_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(changes_tab, text="Changes")

        # Changes content
        changes_card = tk.Frame(changes_tab, bg=self.theme["card_bg"], relief=tk.FLAT, bd=0)
        changes_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title = tk.Label(changes_card, text="Changes Detection", font=("Segoe UI", 14, "bold"),
                         bg=self.theme["card_bg"], fg=self.theme["text"])
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))

        # Button to check changes
        check_btn = tk.Button(changes_card, text="CHECK CHANGES", font=("Segoe UI", 10, "bold"),
                              bg=self.theme["accent"], fg="#ffffff", relief=tk.FLAT,
                              cursor="hand2", bd=0, padx=20, pady=8,
                              command=self.check_changes)
        check_btn.pack(anchor=tk.W, padx=15, pady=(0, 15))
        check_btn.bind("<Enter>", lambda e: check_btn.config(bg=self.theme["accent_hover"]))
        check_btn.bind("<Leave>", lambda e: check_btn.config(bg=self.theme["accent"]))

        # Changes text area
        self.changes_text = scrolledtext.ScrolledText(
            changes_card,
            wrap=tk.WORD,
            width=70,
            height=15,
            bg="#1a1a1a",
            fg=self.theme["text"],
            font=("Consolas", 9),
            relief=tk.FLAT,
            bd=0
        )
        self.changes_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.changes_text.config(state=tk.DISABLED)

        # Initial message
        self.changes_text.config(state=tk.NORMAL)
        self.changes_text.insert(tk.END, "Click 'CHECK CHANGES' to see what has been modified\n")
        self.changes_text.config(state=tk.DISABLED)

    def create_credits_tab(self):
        credits_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(credits_tab, text="Credits")

        # Credits content
        credits_card = tk.Frame(credits_tab, bg=self.theme["card_bg"], relief=tk.FLAT, bd=0)
        credits_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title = tk.Label(credits_card, text="Credits", font=("Segoe UI", 16, "bold"),
                         bg=self.theme["card_bg"], fg=self.theme["text"])
        title.pack(pady=(30, 20))

        # Developer credit
        dev_frame = tk.Frame(credits_card, bg=self.theme["card_bg"])
        dev_frame.pack(pady=20)

        dev_label = tk.Label(dev_frame, text="Developer", font=("Segoe UI", 12, "bold"),
                             bg=self.theme["card_bg"], fg=self.theme["text_secondary"])
        dev_label.pack()

        dev_name = tk.Label(dev_frame, text="Dainstro", font=("Segoe UI", 18, "bold"),
                            bg=self.theme["card_bg"], fg=self.theme["accent"])
        dev_name.pack(pady=(5, 0))

        # Info text
        info_frame = tk.Frame(credits_card, bg=self.theme["card_bg"])
        info_frame.pack(fill=tk.X, padx=50, pady=30)

        info_text = tk.Label(info_frame,
                             text="TEMIC SPOOFER is a powerful privacy tool designed to protect your identity\nby spoofing hardware identifiers and clearing system traces.",
                             font=("Segoe UI", 10), bg=self.theme["card_bg"], fg=self.theme["text_secondary"],
                             justify=tk.CENTER)
        info_text.pack()

        # Warning text
        warning_frame = tk.Frame(credits_card, bg=self.theme["card_bg"])
        warning_frame.pack(fill=tk.X, padx=50, pady=(0, 30))

        warning_text = tk.Label(warning_frame,
                                text="⚠️ Use at your own risk. Some applications may detect spoofing\nand take action against your account.",
                                font=("Segoe UI", 9), bg=self.theme["card_bg"], fg=self.theme["warning"],
                                justify=tk.CENTER)
        warning_text.pack()

    def create_checkbox(self, parent, text, variable):
        frame = tk.Frame(parent, bg=self.theme["card_bg"])

        def toggle():
            variable.set(not variable.get())
            update_appearance()

        def update_appearance():
            if variable.get():
                check_canvas.itemconfig(check_bg, fill=self.theme["accent"])
                check_canvas.itemconfig(check_mark, state=tk.NORMAL)
            else:
                check_canvas.itemconfig(check_bg, fill=self.theme["card_bg"])
                check_canvas.itemconfig(check_mark, state=tk.HIDDEN)

        # Checkbox canvas
        check_canvas = tk.Canvas(frame, width=20, height=20, bg=self.theme["card_bg"],
                                 highlightthickness=0, bd=0)
        check_canvas.pack(side=tk.LEFT)

        # Checkbox background
        check_bg = check_canvas.create_rectangle(2, 2, 18, 18, fill=self.theme["card_bg"],
                                                 outline=self.theme["border"], width=1)

        # Checkmark
        check_mark = check_canvas.create_text(10, 10, text="✓", fill="#ffffff",
                                              font=("Segoe UI", 10, "bold"), state=tk.HIDDEN)

        # Label
        label = tk.Label(frame, text=text, bg=self.theme["card_bg"], fg=self.theme["text"],
                         font=("Segoe UI", 10), cursor="hand2")
        label.pack(side=tk.LEFT, padx=(10, 0))

        # Bind events
        check_canvas.bind("<Button-1>", lambda e: toggle())
        label.bind("<Button-1>", lambda e: toggle())

        # Set initial state
        update_appearance()

        return frame

    def create_settings_menu(self):
        self.settings_frame = tk.Frame(self.main_container, bg=self.theme["card_bg"],
                                       relief=tk.FLAT, bd=1, highlightbackground=self.theme["border"],
                                       highlightcolor=self.theme["border"], highlightthickness=1)
        self.settings_frame.place(x=10, y=60, width=250, height=0)
        self.settings_visible = False

        # Theme settings
        theme_label = tk.Label(self.settings_frame, text="Theme", font=("Segoe UI", 11, "bold"),
                               bg=self.theme["card_bg"], fg=self.theme["text"])
        theme_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

        theme_frame = tk.Frame(self.settings_frame, bg=self.theme["card_bg"])
        theme_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        dark_btn = tk.Button(theme_frame, text="Dark Mode", font=("Segoe UI", 9),
                             bg=self.theme["accent"] if self.dark_mode else self.theme["card_bg"],
                             fg="#ffffff" if self.dark_mode else self.theme["text"],
                             relief=tk.FLAT, bd=1, cursor="hand2",
                             command=lambda: self.toggle_theme(True))
        dark_btn.pack(side=tk.LEFT, padx=(0, 5))
        dark_btn.config(highlightbackground=self.theme["border"], highlightcolor=self.theme["border"],
                        highlightthickness=1)

        light_btn = tk.Button(theme_frame, text="Light Mode", font=("Segoe UI", 9),
                              bg=self.theme["card_bg"] if self.dark_mode else self.theme["accent"],
                              fg=self.theme["text"] if self.dark_mode else "#ffffff",
                              relief=tk.FLAT, bd=1, cursor="hand2",
                              command=lambda: self.toggle_theme(False))
        light_btn.pack(side=tk.LEFT)
        light_btn.config(highlightbackground=self.theme["border"], highlightcolor=self.theme["border"],
                         highlightthickness=1)

        # Other settings would go here
        other_label = tk.Label(self.settings_frame, text="Other Settings", font=("Segoe UI", 11, "bold"),
                               bg=self.theme["card_bg"], fg=self.theme["text"])
        other_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

        # Placeholder for other settings
        placeholder = tk.Label(self.settings_frame, text="More settings coming soon...",
                               font=("Segoe UI", 9), bg=self.theme["card_bg"], fg=self.theme["text_secondary"])
        placeholder.pack(anchor=tk.W, padx=15, pady=(0, 15))

    def toggle_settings(self):
        if self.settings_visible:
            self.settings_frame.place_forget()
            self.settings_visible = False
        else:
            self.settings_frame.place(x=10, y=60, width=250, height=150)
            self.settings_visible = True

    def toggle_theme(self, dark_mode):
        self.dark_mode = dark_mode
        self.theme = self.colors["dark" if dark_mode else "light"]
        self.apply_theme()

    def apply_theme(self):
        # Update all widgets with new theme colors
        self.root.configure(bg=self.theme["bg"])
        self.main_container.configure(bg=self.theme["bg"])

        # Update notebook style
        self.style.configure("TNotebook", background=self.theme["bg"])
        self.style.configure("TNotebook.Tab",
                             background=self.theme["tab_bg"],
                             foreground=self.theme["text"])
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.theme["tab_selected"])],
                       foreground=[("selected", "#ffffff")])

        # Update all children recursively
        self.update_widget_colors(self.main_container)

    def update_widget_colors(self, widget):
        # Recursively update widget colors based on current theme
        try:
            if isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame):
                if "card_bg" in str(widget.cget("bg")):
                    widget.configure(bg=self.theme["card_bg"])
                elif "header_bg" in str(widget.cget("bg")):
                    widget.configure(bg=self.theme["header_bg"])
                else:
                    widget.configure(bg=self.theme["bg"])
            elif isinstance(widget, tk.Label):
                if "card_bg" in str(widget.cget("bg")):
                    widget.configure(bg=self.theme["card_bg"])
                elif "header_bg" in str(widget.cget("bg")):
                    widget.configure(bg=self.theme["header_bg"])
                else:
                    widget.configure(bg=self.theme["bg"])

                if "text_secondary" in str(widget.cget("fg")):
                    widget.configure(fg=self.theme["text_secondary"])
                elif "warning" in str(widget.cget("fg")):
                    widget.configure(fg=self.theme["warning"])
                elif "accent" in str(widget.cget("fg")):
                    widget.configure(fg=self.theme["accent"])
                else:
                    widget.configure(fg=self.theme["text"])
            elif isinstance(widget, tk.Button):
                if widget.cget("text") in ["START SPOOFING", "REBOOT SYSTEM", "CHECK CHANGES"]:
                    # These are special buttons, don't change their colors
                    pass
                else:
                    widget.configure(bg=self.theme["card_bg"], fg=self.theme["text"])
        except:
            pass

        for child in widget.winfo_children():
            self.update_widget_colors(child)

    def capture_original_values(self):
        """Capture original values before spoofing for comparison"""
        try:
            # HWID values
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            machine_guid = reg.QueryValueEx(key, "MachineGuid")[0]
            reg.CloseKey(key)

            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            product_id = reg.QueryValueEx(key, "ProductId")[0]
            reg.CloseKey(key)

            # MAC addresses
            ps_command = 'Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and ($_.InterfaceType -eq "Ethernet" -or $_.InterfaceType -like "*Wireless*")} | Select-Object Name, MacAddress'
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)
            mac_addresses = result.stdout

            self.original_values = {
                "hwid": {
                    "MachineGuid": machine_guid,
                    "ProductId": product_id
                },
                "mac": mac_addresses
            }

        except Exception as e:
            logger.error(f"Error capturing original values: {e}")

    def check_changes(self):
        """Check and display changes after spoofing"""
        try:
            self.changes_text.config(state=tk.NORMAL)
            self.changes_text.delete(1.0, tk.END)

            # Check HWID changes
            self.changes_text.insert(tk.END, "HWID CHANGES:\n")
            self.changes_text.insert(tk.END, "=" * 50 + "\n")

            try:
                key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                current_machine_guid = reg.QueryValueEx(key, "MachineGuid")[0]
                reg.CloseKey(key)

                key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_product_id = reg.QueryValueEx(key, "ProductId")[0]
                reg.CloseKey(key)

                # Compare MachineGuid
                if "MachineGuid" in self.original_values["hwid"]:
                    original = self.original_values["hwid"]["MachineGuid"]
                    if original != current_machine_guid:
                        self.changes_text.insert(tk.END, f"MachineGuid:\n{original} → {current_machine_guid}\n\n")
                    else:
                        self.changes_text.insert(tk.END, "MachineGuid: No change detected\n\n")

                # Compare ProductId
                if "ProductId" in self.original_values["hwid"]:
                    original = self.original_values["hwid"]["ProductId"]
                    if original != current_product_id:
                        self.changes_text.insert(tk.END, f"ProductId:\n{original} → {current_product_id}\n\n")
                    else:
                        self.changes_text.insert(tk.END, "ProductId: No change detected\n\n")

            except Exception as e:
                self.changes_text.insert(tk.END, f"Error checking HWID: {e}\n\n")

            # Check MAC changes
            self.changes_text.insert(tk.END, "\nMAC ADDRESS CHANGES:\n")
            self.changes_text.insert(tk.END, "=" * 50 + "\n")

            try:
                ps_command = 'Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and ($_.InterfaceType -eq "Ethernet" -or $_.InterfaceType -like "*Wireless*")} | Select-Object Name, MacAddress'
                result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)
                current_mac = result.stdout

                if self.original_values["mac"] != current_mac:
                    self.changes_text.insert(tk.END, "MAC addresses changed:\n")
                    self.changes_text.insert(tk.END, f"Before:\n{self.original_values['mac']}\n")
                    self.changes_text.insert(tk.END, f"After:\n{current_mac}\n")
                else:
                    self.changes_text.insert(tk.END, "MAC addresses: No changes detected\n")

            except Exception as e:
                self.changes_text.insert(tk.END, f"Error checking MAC: {e}\n")

            self.changes_text.config(state=tk.DISABLED)

        except Exception as e:
            logger.error(f"Error checking changes: {e}")
            self.changes_text.config(state=tk.NORMAL)
            self.changes_text.insert(tk.END, f"Error checking changes: {e}")
            self.changes_text.config(state=tk.DISABLED)

    def start_spoofing_thread(self):
        logger.info("Starting spoofing process...")
        thread = threading.Thread(target=self.perform_spoofing)
        thread.daemon = True
        thread.start()

    def perform_spoofing(self):
        try:
            if self.hwid_var.get():
                logger.info("Spoofing HWID...")
                self.spoof_hwid()

            if self.mac_var.get():
                logger.info("Spoofing MAC address...")
                self.spoof_mac()

            if self.wmi_var.get():
                logger.info("Spoofing WMI data...")
                self.change_wmi_registry()

            if self.logs_var.get():
                logger.info("Clearing system logs...")
                self.clear_logs()

            logger.info("Spoofing completed successfully! Reboot recommended.")
            messagebox.showinfo("Success", "Spoofing completed successfully! Reboot for full effect.")

        except Exception as e:
            logger.error(f"Error during spoofing: {str(e)}")
            messagebox.showerror("Error", f"Spoofing failed: {e}")

    def reboot_system(self):
        if messagebox.askyesno("Reboot", "Are you sure you want to reboot your system?"):
            os.system("shutdown /r /t 0")

    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def spoof_hwid(self):
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "MachineGuid", 0, reg.REG_SZ, self.generate_random_string(36))
            reg.CloseKey(key)

            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0,
                              reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "ProductId", 0, reg.REG_SZ, self.generate_random_string(20))
            reg.SetValueEx(key, "DigitalProductId", 0, reg.REG_BINARY,
                           bytes([random.randint(0, 255) for _ in range(164)]))
            reg.CloseKey(key)

            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                              r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001", 0,
                              reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "HwProfileGuid", 0, reg.REG_SZ,
                           "{" + self.generate_random_string(8) + "-" + self.generate_random_string(
                               4) + "-" + self.generate_random_string(4) + "-" + self.generate_random_string(
                               4) + "-" + self.generate_random_string(12) + "}")
            reg.CloseKey(key)

            logger.info("HWID spoofed successfully.")
        except Exception as e:
            logger.error(f"HWID spoof error: {e}")
            raise

    def spoof_mac(self):
        try:
            # Get network adapters using PowerShell
            ps_command = 'Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and ($_.InterfaceType -eq "Ethernet" -or $_.InterfaceType -like "*Wireless*")} | Select-Object Name, InterfaceDescription'
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, check=True)

            lines = result.stdout.strip().split('\n')
            if len(lines) > 2:
                for line in lines[2:]:
                    if not line.strip():
                        continue

                    parts = line.split('|')
                    if len(parts) >= 2:
                        adapter_name = parts[0].strip()

                        # Generate random MAC
                        new_mac = f"{random.randint(0x00, 0xff):02X}-{random.randint(0x00, 0xff):02X}-{random.randint(0x00, 0xff):02X}-{random.randint(0x00, 0xff):02X}-{random.randint(0x00, 0xff):02X}-{random.randint(0x00, 0xff):02X}"

                        # Disable adapter
                        subprocess.run(
                            ['netsh', 'interface', 'set', 'interface', f'"{adapter_name}"', 'admin=disabled'],
                            capture_output=True)

                        # Set new MAC using registry
                        try:
                            class_guid = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
                            for i in range(1000):
                                try:
                                    key_path = f"{class_guid}\\{i:04d}"
                                    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path) as key:
                                        try:
                                            driver_desc = reg.QueryValueEx(key, "DriverDesc")[0]
                                            if driver_desc == adapter_name:
                                                with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path, 0,
                                                                 reg.KEY_SET_VALUE) as set_key:
                                                    reg.SetValueEx(set_key, "NetworkAddress", 0, reg.REG_SZ,
                                                                   new_mac.replace('-', ''))
                                                break
                                        except FileNotFoundError:
                                            continue
                                except FileNotFoundError:
                                    continue
                        except Exception as e:
                            logger.error(f"Registry MAC change failed: {e}")

                        # Enable adapter
                        subprocess.run(['netsh', 'interface', 'set', 'interface', f'"{adapter_name}"', 'admin=enabled'],
                                       capture_output=True)

            # Release and renew IP
            subprocess.run(['ipconfig', '/release'], capture_output=True)
            subprocess.run(['ipconfig', '/renew'], capture_output=True)

            logger.info("MAC spoofed successfully.")
        except Exception as e:
            logger.error(f"MAC spoof error: {e}")
            raise

    def clear_logs(self):
        try:
            subprocess.run(['wevtutil', 'cl', 'System'], capture_output=True, check=True)
            subprocess.run(['wevtutil', 'cl', 'Application'], capture_output=True, check=True)
            subprocess.run(['wevtutil', 'cl', 'Security'], capture_output=True, check=True)

            temp_path = os.environ.get('TEMP')
            if temp_path and os.path.exists(temp_path):
                for filename in os.listdir(temp_path):
                    file_path = os.path.join(temp_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.error(f"Error clearing temp file {file_path}: {e}")

            prefetch_path = r"C:\Windows\Prefetch"
            if os.path.exists(prefetch_path):
                for filename in os.listdir(prefetch_path):
                    file_path = os.path.join(prefetch_path, filename)
                    try:
                        os.unlink(file_path)
                    except Exception as e:
                        logger.error(f"Error clearing prefetch file {file_path}: {e}")

            subprocess.run(['ipconfig', '/flushdns'], capture_output=True, check=True)
            subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, check=True)

            logger.info("Logs cleared successfully.")
        except Exception as e:
            logger.error(f"Logs clear error: {e}")
            raise

    def change_wmi_registry(self):
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0,
                              reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "BuildLab", 0, reg.REG_SZ, self.generate_random_string(20))
            reg.SetValueEx(key, "BuildLabEx", 0, reg.REG_SZ, self.generate_random_string(30))
            reg.SetValueEx(key, "InstallDate", 0, reg.REG_DWORD, random.randint(1000000000, 2000000000))
            reg.SetValueEx(key, "InstallTime", 0, reg.REG_QWORD,
                           random.randint(1000000000000000000, 2000000000000000000))
            reg.CloseKey(key)

            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                              reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "Hostname", 0, reg.REG_SZ, self.generate_random_string(15))
            reg.SetValueEx(key, "Domain", 0, reg.REG_SZ, self.generate_random_string(10) + ".com")
            reg.CloseKey(key)

            logger.info("WMI spoofed successfully.")
        except Exception as e:
            logger.error(f"WMI spoof error: {e}")
            raise


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)

        self.text_widget.after(0, append)


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernSpoofer(root)
    logger.info("TEMIC SPOOFER v1.0.0 started successfully")
    root.mainloop()