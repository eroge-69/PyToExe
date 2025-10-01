# totp_gui_complete.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import time
import pyotp
import base64
import urllib.parse
import json
import os
from PIL import Image
from pyzbar import pyzbar
import sys

try:
    import pyperclip

    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


class DarkTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_style()

    def configure_style(self):
        style = ttk.Style()
        style.configure("Dark.Treeview",
                        background="#2d2d2d",
                        foreground="#ffffff",
                        fieldbackground="#2d2d2d",
                        rowheight=25)
        style.configure("Dark.Treeview.Heading",
                        background="#404040",
                        foreground="#ffffff",
                        relief="flat")
        style.map("Dark.Treeview.Heading",
                  background=[("active", "#505050")])


class TOTPExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TOTP Extractor - Google Authenticator")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 750)

        # Dark Mode Farben
        self.bg_color = '#2d2d2d'
        self.fg_color = '#ffffff'
        self.entry_bg = '#3a3a3a'  # Graue Eingabefelder
        self.select_bg = '#404040'
        self.button_bg = '#4a4a4a'
        self.button_hover = '#5a5a5a'

        # Root Window Hintergrund
        self.root.configure(bg=self.bg_color)

        # Daten
        self.accounts = []
        self.raw_secrets = []  # Für manuelle Namenszuweisung
        self.totp_threads = []
        self.running = True  # Automatisch aktiv
        self.config_file = "totp_accounts.json"

        self.setup_ui()

        # Lade gespeicherte Konten NACH der UI-Erstellung
        self.load_accounts()
        self.refresh_accounts()

        if self.accounts:
            self.start_btn.config(state=tk.NORMAL)
            self.status_var.set(f"{len(self.accounts)} Konten geladen")

        # Starte TOTP automatisch
        if self.accounts:
            self.start_totp_automatic()

    def setup_ui(self):
        # Hauptframe
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Titel
        title_label = tk.Label(main_frame, text="🔐 TOTP Extractor", font=("Arial", 18, "bold"),
                               bg=self.bg_color, fg=self.fg_color)
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(main_frame, text="Google Authenticator QR-Code Importer",
                                  font=("Arial", 10), bg=self.bg_color, fg=self.fg_color)
        subtitle_label.pack(pady=(0, 20))

        # Live TOTP Anzeige
        live_frame = tk.LabelFrame(main_frame, text="📱 Live TOTP Codes", font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        live_frame.pack(fill=tk.X, pady=(0, 15))

        # Suchleiste für Live TOTP
        search_frame = tk.Frame(live_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT,
                                                                                                      padx=(0, 10))
        self.live_search_var = tk.StringVar()
        self.live_search_entry = tk.Entry(search_frame, textvariable=self.live_search_var, width=30,
                                          bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color,
                                          relief=tk.FLAT)
        self.live_search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        self.live_search_var.trace('w', self.search_live_totp)

        tk.Button(search_frame, text="Suchen", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.search_live_totp).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(search_frame, text="❌", bg=self.button_bg, fg=self.fg_color, width=3, relief=tk.FLAT,
                  command=self.clear_live_search).pack(side=tk.LEFT)

        # Treeview für Live-Codes
        tree_frame = tk.Frame(live_frame, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Nr", "Code", "Name", "Countdown")
        self.live_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.live_tree["style"] = "Dark.Treeview"

        self.live_tree.heading("Nr", text="#")
        self.live_tree.heading("Code", text="🔐 Code")
        self.live_tree.heading("Name", text="🏷️ Name")
        self.live_tree.heading("Countdown", text="⏱️ Countdown")

        self.live_tree.column("Nr", width=50, anchor=tk.CENTER)
        self.live_tree.column("Code", width=100, anchor=tk.CENTER)
        self.live_tree.column("Name", width=300)
        self.live_tree.column("Countdown", width=100, anchor=tk.CENTER)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.live_tree.yview)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.live_tree.xview)
        self.live_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.live_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Event-Binding für Klick auf Codes
        self.live_tree.bind("<Button-1>", self.on_live_code_click)
        self.live_tree.bind("<Double-Button-1>", self.on_live_code_double_click)

        # Dateiauswahl
        file_frame = tk.LabelFrame(main_frame, text="📁 QR-Code Import", font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 15))

        file_row = tk.Frame(file_frame, bg=self.bg_color)
        file_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(file_row, text="📄 Datei:", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_row, textvariable=self.file_path_var, width=50,
                                   bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color, relief=tk.FLAT)
        self.file_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)

        tk.Button(file_row, text="📂 Durchsuchen...", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.browse_file).pack(side=tk.LEFT)

        # Buttons
        button_frame = tk.Frame(file_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(button_frame, text="📤 Konten extrahieren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.extract_accounts).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(button_frame, text="✏️ Manuelle Zuweisung", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.manual_name_assignment).pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(button_frame, text="📥 Importieren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.import_accounts).pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(button_frame, text="💾 Exportieren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.export_accounts).pack(side=tk.LEFT, padx=(5, 0))

        # Status
        self.status_var = tk.StringVar(value="✅ Bereit")
        status_label = tk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10),
                                bg=self.bg_color, fg='#4CAF50')
        status_label.pack(pady=(0, 15))

        # Notebook für Tabs
        notebook_frame = tk.Frame(main_frame, bg=self.bg_color)
        notebook_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Kontenliste
        self.accounts_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.accounts_frame, text="📋 Konten")
        self.setup_accounts_tab()

        # Tab 2: Vollbild Live TOTP
        self.totp_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.totp_frame, text="🖥️ Vollbild TOTP")
        self.setup_totp_tab()

        # Tab 3: Debug Log
        self.log_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.log_frame, text="📝 Debug Log")
        self.setup_log_tab()

        # Steuerbuttons
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = tk.Button(control_frame, text="▶️ Start TOTP", bg=self.button_bg, fg=self.fg_color,
                                   relief=tk.FLAT,
                                   state=tk.DISABLED, command=self.start_totp)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop TOTP", bg=self.button_bg, fg=self.fg_color,
                                  relief=tk.FLAT,
                                  command=self.stop_totp)
        self.stop_btn.pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(control_frame, text="🔄 Aktualisieren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.refresh_accounts).pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(control_frame, text="💾 Speichern", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.save_accounts).pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(control_frame, text="🗑️ Liste leeren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.clear_accounts).pack(side=tk.LEFT, padx=(5, 5))

        tk.Button(control_frame, text="🚪 Beenden", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.root.quit).pack(side=tk.LEFT, padx=(5, 0))

    def setup_accounts_tab(self):
        # Suchleiste für Konten
        search_frame = tk.Frame(self.accounts_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(10, 10))

        tk.Label(search_frame, text="🔍 Suche:", font=("Arial", 10), bg=self.bg_color, fg=self.fg_color).pack(
            side=tk.LEFT)
        self.account_search_var = tk.StringVar()
        self.account_search_entry = tk.Entry(search_frame, textvariable=self.account_search_var, width=30,
                                             bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color,
                                             relief=tk.FLAT)
        self.account_search_entry.pack(side=tk.LEFT, padx=(10, 10))
        self.account_search_var.trace('w', self.search_accounts)

        tk.Button(search_frame, text="Suchen", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.search_accounts).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(search_frame, text="❌", bg=self.button_bg, fg=self.fg_color, width=3, relief=tk.FLAT,
                  command=self.clear_account_search).pack(side=tk.LEFT)

        # Treeview für Konten
        tree_frame = tk.Frame(self.accounts_frame, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("Nr", "Name", "Issuer", "Secret")
        self.accounts_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.accounts_tree["style"] = "Dark.Treeview"

        self.accounts_tree.heading("Nr", text="#")
        self.accounts_tree.heading("Name", text="🏷️ Name")
        self.accounts_tree.heading("Issuer", text="🏢 Issuer")
        self.accounts_tree.heading("Secret", text="🔑 Secret")

        self.accounts_tree.column("Nr", width=50, anchor=tk.CENTER)
        self.accounts_tree.column("Name", width=200)
        self.accounts_tree.column("Issuer", width=150)
        self.accounts_tree.column("Secret", width=250)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.accounts_tree.yview)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.accounts_tree.xview)
        self.accounts_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.accounts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Kontextmenü
        self.accounts_tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.select_bg, fg=self.fg_color)
        self.context_menu.add_command(label="✏️ Namen bearbeiten", command=self.edit_account_name)
        self.context_menu.add_command(label="📋 Secret kopieren", command=self.copy_secret)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Konto löschen", command=self.delete_account)
        self.context_menu.add_command(label="🧨 Alle löschen", command=self.clear_accounts)

    def setup_totp_tab(self):
        # Treeview für Live-Codes
        tree_frame = tk.Frame(self.totp_frame, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Nr", "Code", "Name", "Countdown")
        self.totp_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.totp_tree["style"] = "Dark.Treeview"

        self.totp_tree.heading("Nr", text="#")
        self.totp_tree.heading("Code", text="🔐 Code")
        self.totp_tree.heading("Name", text="🏷️ Name")
        self.totp_tree.heading("Countdown", text="⏱️ Countdown")

        self.totp_tree.column("Nr", width=50, anchor=tk.CENTER)
        self.totp_tree.column("Code", width=100, anchor=tk.CENTER)
        self.totp_tree.column("Name", width=300)
        self.totp_tree.column("Countdown", width=100, anchor=tk.CENTER)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.totp_tree.yview)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.totp_tree.xview)
        self.totp_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.totp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Event-Binding für Klick auf Codes
        self.totp_tree.bind("<Button-1>", self.on_fullscreen_code_click)
        self.totp_tree.bind("<Double-Button-1>", self.on_fullscreen_code_double_click)

    def setup_log_tab(self):
        # ScrolledText für Log
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, height=20,
                                                  bg=self.entry_bg, fg=self.fg_color,
                                                  insertbackground=self.fg_color, relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button-Leiste
        button_frame = tk.Frame(self.log_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(button_frame, text="🗑️ Log leeren", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(button_frame, text="💾 Log speichern", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))

    def on_live_code_click(self, event):
        """Behandelt Klick auf TOTP-Code in der Live-Anzeige"""
        self.copy_code_to_clipboard(self.live_tree, event)

    def on_live_code_double_click(self, event):
        """Behandelt Doppelklick auf TOTP-Code in der Live-Anzeige"""
        self.copy_code_to_clipboard(self.live_tree, event)
        if hasattr(self, 'status_var'):
            original_status = self.status_var.get()
            self.status_var.set("✅ Code in Zwischenablage kopiert!")
            self.live_tree.after(2000, lambda: self.status_var.set(original_status))

    def on_fullscreen_code_click(self, event):
        """Behandelt Klick auf TOTP-Code in der Vollbild-Anzeige"""
        self.copy_code_to_clipboard(self.totp_tree, event)

    def on_fullscreen_code_double_click(self, event):
        """Behandelt Doppelklick auf TOTP-Code in der Vollbild-Anzeige"""
        self.copy_code_to_clipboard(self.totp_tree, event)
        if hasattr(self, 'status_var'):
            original_status = self.status_var.get()
            self.status_var.set("✅ Code in Zwischenablage kopiert!")
            self.totp_tree.after(2000, lambda: self.status_var.set(original_status))

    def copy_code_to_clipboard(self, treeview, event):
        """Kopiert den TOTP-Code in die Zwischenablage"""
        if not HAS_PYPERCLIP:
            return

        # Hole das angeklickte Item
        item = treeview.identify_row(event.y)
        if not item:
            return

        # Hole die Werte des Items
        try:
            values = treeview.item(item, 'values')
            if len(values) >= 2:
                code = values[1]  # Code ist in Spalte 2 (Index 1)

                # Prüfe ob es ein gültiger Code ist (nur Zahlen)
                if code.isdigit() and len(code) == 6:
                    pyperclip.copy(code)
                    # Einfaches visuelles Feedback
                    treeview.tag_configure('copied', background='#2a6f4a')
                    treeview.item(item, tags=('copied',))
                    treeview.after(300, lambda: self.clear_item_highlight(treeview, item))
        except Exception:
            pass  # Ignoriere Fehler beim Klicken

    def clear_item_highlight(self, treeview, item):
        """Entfernt die Hervorhebung vom Item"""
        try:
            # Prüfe ob das Item noch existiert
            treeview.item(item, tags=())
        except Exception:
            pass  # Item existiert nicht mehr, das ist OK

    def search_live_totp(self, *args):
        """Sucht in der Live TOTP Anzeige"""
        search_term = self.live_search_var.get().lower().strip()

        if not hasattr(self, 'live_tree') or not self.live_tree:
            return

        # Lösche aktuelle Anzeige
        for item in self.live_tree.get_children():
            self.live_tree.delete(item)

        # Zeige nur passende Konten an
        for i, account in enumerate(self.accounts, 1):
            name = account.get('name', f'Konto {i}').lower()
            if not search_term or search_term in name:
                try:
                    totp = pyotp.TOTP(account['secret'])
                    code = totp.now()
                    display_name = account.get('name', f'Konto {i}')
                    if len(display_name) > 40:
                        display_name = display_name[:37] + "..."

                    current_time = int(time.time())
                    seconds_remaining = 30 - (current_time % 30)

                    self.live_tree.insert("", tk.END, values=(i, code, display_name, f"{seconds_remaining}s"))
                except:
                    display_name = account.get('name', f'Konto {i}')
                    if len(display_name) > 40:
                        display_name = display_name[:37] + "..."
                    self.live_tree.insert("", tk.END, values=(i, "❌ FEHLER", display_name, "0"))

    def clear_live_search(self):
        """Löscht die Live-Suche"""
        self.live_search_var.set("")
        self.search_live_totp()

    def search_accounts(self, *args):
        """Sucht in der Kontenliste"""
        search_term = self.account_search_var.get().lower().strip()

        if not hasattr(self, 'accounts_tree') or not self.accounts_tree:
            return

        # Lösche aktuelle Anzeige
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)

        # Zeige nur passende Konten an
        count = 0
        for i, account in enumerate(self.accounts, 1):
            name = account.get('name', f'Konto {i}').lower()
            issuer = account.get('issuer', '').lower()

            if not search_term or search_term in name or search_term in issuer:
                count += 1
                secret_display = account.get('secret', '')
                if len(secret_display) > 25:
                    secret_display = secret_display[:22] + "..."

                self.accounts_tree.insert("", tk.END, values=(
                    i,
                    account.get('name', 'Unbekannt'),
                    account.get('issuer', 'Unbekannt'),
                    secret_display
                ))

        self.status_var.set(f"✅ {count} Konten gefunden")

    def clear_account_search(self):
        """Löscht die Konto-Suche"""
        self.account_search_var.set("")
        self.search_accounts()

    def show_context_menu(self, event):
        item = self.accounts_tree.identify_row(event.y)
        if item:
            self.accounts_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_account_name(self):
        selection = self.accounts_tree.selection()
        if not selection:
            return

        item = selection[0]
        account_index = self.accounts_tree.index(item)
        if 0 <= account_index < len(self.accounts):
            old_name = self.accounts[account_index].get('name', '')
            new_name = simpledialog.askstring("Name bearbeiten", "Neuer Name:", initialvalue=old_name)
            if new_name and new_name != old_name:
                self.accounts[account_index]['name'] = new_name
                self.refresh_accounts()
                self.log(f"✏️ Name geändert: {old_name} -> {new_name}")

    def copy_secret(self):
        selection = self.accounts_tree.selection()
        if not selection:
            return

        item = selection[0]
        account_index = self.accounts_tree.index(item)
        if 0 <= account_index < len(self.accounts):
            secret = self.accounts[account_index].get('secret', '')
            if HAS_PYPERCLIP:
                try:
                    pyperclip.copy(secret)
                    messagebox.showinfo("✅ Erfolg", "Secret in Zwischenablage kopiert!")
                except Exception as e:
                    messagebox.showerror("❌ Fehler", f"Fehler beim Kopieren: {e}")
            else:
                messagebox.showinfo("ℹ️ Info", f"Secret:\n{secret}")

    def delete_account(self):
        selection = self.accounts_tree.selection()
        if not selection:
            return

        if messagebox.askyesno("🗑️ Bestätigung", "Möchtest du dieses Konto wirklich löschen?"):
            item = selection[0]
            account_index = self.accounts_tree.index(item)
            if 0 <= account_index < len(self.accounts):
                deleted_account = self.accounts.pop(account_index)
                self.refresh_accounts()
                self.save_accounts()
                self.log(f"🗑️ Konto gelöscht: {deleted_account.get('name', 'Unbekannt')}")

    def clear_accounts(self):
        if not self.accounts:
            return

        if messagebox.askyesno("🧨 Bestätigung", "Möchtest du wirklich alle Konten löschen?"):
            self.accounts.clear()
            self.refresh_accounts()
            self.save_accounts()
            self.start_btn.config(state=tk.DISABLED)
            self.log("🧨 Alle Konten gelöscht")
            self.status_var.set("🧨 Alle Konten gelöscht")

    def log(self, message):
        # Sicherstellen, dass log_text existiert
        if hasattr(self, 'log_text') and self.log_text:
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)

    def clear_log(self):
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.delete(1.0, tk.END)

    def save_log(self):
        if not hasattr(self, 'log_text') or not self.log_text:
            return

        log_content = self.log_text.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
            title="📝 Log speichern"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("✅ Erfolg", "Log gespeichert!")
            except Exception as e:
                messagebox.showerror("❌ Fehler", f"Fehler beim Speichern: {e}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="📂 QR-Code Bild auswählen",
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("Alle Dateien", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def extract_accounts(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("❌ Fehler", "Bitte wähle eine Bilddatei aus!")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("❌ Fehler", "Datei nicht gefunden!")
            return

        # Starte Extraktion in separatem Thread
        self.status_var.set("📤 Extrahiere Konten...")
        threading.Thread(target=self._extract_accounts_thread, args=(file_path,), daemon=True).start()

    def _extract_accounts_thread(self, file_path):
        try:
            self.log(f"📄 Lese Bild: {file_path}")

            # Bild öffnen
            image = Image.open(file_path)
            self.log("✅ Bild erfolgreich geöffnet")

            # QR-Codes dekodieren
            decoded_objects = pyzbar.decode(image)
            self.log(f"✅ {len(decoded_objects)} QR-Code(s) gefunden")

            if not decoded_objects:
                self.log("❌ Keine QR-Codes im Bild gefunden")
                self.root.after(0, lambda: self.status_var.set("❌ Keine QR-Codes gefunden"))
                return

            url = decoded_objects[0].data.decode('utf-8')
            self.log(f"🔗 Gefundene URL: {url[:100]}...")

            # Konten extrahieren
            new_accounts = self.extract_accounts_from_url(url)

            if new_accounts:
                # Füge neue Konten zur bestehenden Liste hinzu
                existing_count = len(self.accounts)
                for new_account in new_accounts:
                    # Prüfe auf Duplikate
                    is_duplicate = False
                    for existing_account in self.accounts:
                        if existing_account['secret'] == new_account['secret']:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        self.accounts.append(new_account)

                added_count = len(self.accounts) - existing_count

                self.root.after(0, self.refresh_accounts)
                self.log(f"✅ {added_count} neue Konto(e) hinzugefügt")
                self.root.after(0, lambda: self.status_var.set(f"✅ {added_count} neue Konten hinzugefügt"))
                self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

                # Speichere aktualisierte Liste
                self.root.after(0, self.save_accounts)

                # Starte TOTP automatisch wenn neue Konten hinzugefügt wurden
                if added_count > 0:
                    self.root.after(0, self.start_totp_automatic)

            else:
                self.log("❌ Keine neuen Konten gefunden")
                self.root.after(0, lambda: self.status_var.set("❌ Keine neuen Konten gefunden"))

        except Exception as e:
            error_msg = f"❌ Fehler bei der Extraktion: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("❌ Fehler", error_msg))
            self.root.after(0, lambda: self.status_var.set("❌ Fehler bei Extraktion"))

    def extract_accounts_from_url(self, url):
        """Extrahiert Konten aus URL"""
        try:
            if url.startswith("otpauth://"):
                parsed = urllib.parse.urlparse(url)
                query = urllib.parse.parse_qs(parsed.query)
                secret = query.get('secret', [None])[0]
                issuer = query.get('issuer', [None])[0]
                name = parsed.path.lstrip('/')
                if not secret:
                    return []

                secret_b32 = self.decode_secret(secret.encode('ascii'))
                if secret_b32:
                    return [{
                        'secret': secret_b32,
                        'issuer': issuer or 'Unbekannt',
                        'name': name or 'Importiert'
                    }]
                else:
                    return []

            elif url.startswith("otpauth-migration://"):
                parsed = urllib.parse.urlparse(url)
                query = urllib.parse.parse_qs(parsed.query)
                data_b64 = query.get('data', [None])[0]
                if not data_b64:
                    return []

                decoded_data = urllib.parse.unquote(data_b64)
                data_bytes = base64.b64decode(decoded_data)

                # Finde alle Secrets für manuelle Zuweisung
                self.raw_secrets = self.find_all_secrets_with_info(data_bytes)

                # Erstelle Konten mit Standardnamen
                accounts = []
                for i, secret_info in enumerate(self.raw_secrets):
                    secret_b32 = secret_info['secret']
                    if secret_b32:
                        accounts.append({
                            'secret': secret_b32,
                            'name': f'Konto {i + 1}',
                            'issuer': 'Google Auth'
                        })

                return accounts[:9]  # Maximal 9 Konten

        except Exception as e:
            self.log(f"❌ Fehler bei URL-Verarbeitung: {e}")
            return []

    def find_all_secrets_with_info(self, data_bytes):
        """Findet alle Secrets mit zusätzlichen Informationen"""
        secrets = []
        i = 0
        counter = 1

        while i < len(data_bytes) - 10:
            if data_bytes[i] == 0x0A:  # Secret-Marker
                try:
                    length = data_bytes[i + 1]
                    if 8 < length < 60 and i + 2 + length <= len(data_bytes):
                        secret_data = data_bytes[i + 2:i + 2 + length]

                        secret_b32 = self.decode_secret(secret_data)
                        if secret_b32 and self.test_secret_validity(secret_b32):
                            # Finde nahegelegene Strings
                            nearby_strings = self.find_nearby_strings(data_bytes, i)

                            secrets.append({
                                'secret': secret_b32,
                                'position': i,
                                'length': length,
                                'nearby_strings': nearby_strings,
                                'counter': counter
                            })
                            counter += 1

                        i += length + 2
                        continue
                except:
                    pass
            i += 1

        return secrets

    def find_nearby_strings(self, data_bytes, position):
        """Findet Strings in der Nähe einer Position"""
        search_start = max(0, position - 100)
        search_end = min(len(data_bytes), position + 150)
        search_data = data_bytes[search_start:search_end]

        strings = self.extract_all_strings(search_data)

        # Kategorisiere Strings
        colon_strings = [s for s in strings if ':' in s and len(s) > 3 and len(s) < 50]
        email_strings = [s for s in strings if '@' in s and '.' in s and len(s) > 5]
        service_strings = [s for s in strings if
                           len(s) > 3 and not s.replace('@', '').replace('.', '').replace('-', '').isdigit()]

        return {
            'colon_format': colon_strings[:3],
            'emails': email_strings[:3],
            'services': service_strings[:5]
        }

    def extract_all_strings(self, data_bytes):
        """Extrahiert alle lesbaren Strings"""
        strings = []
        current_string = ""

        for byte in data_bytes:
            if 32 <= byte <= 126 or byte in [195, 196, 197, 228, 246, 252, 223]:
                current_string += chr(byte)
            else:
                if len(current_string) >= 2:
                    cleaned = ''.join(c for c in current_string if 32 <= ord(c) <= 126 or c in 'äöüÄÖÜß@.+-_=')
                    if len(cleaned) >= 2:
                        strings.append(cleaned.strip())
                current_string = ""

        if len(current_string) >= 2:
            cleaned = ''.join(c for c in current_string if 32 <= ord(c) <= 126 or c in 'äöüÄÖÜß@.+-_=')
            if len(cleaned) >= 2:
                strings.append(cleaned.strip())

        return strings

    def manual_name_assignment(self):
        """Öffnet Dialog für manuelle Namenszuweisung"""
        if not self.raw_secrets:
            messagebox.showinfo("ℹ️ Info", "Bitte extrahiere zuerst die Konten aus einem QR-Code!")
            return

        self.manual_assignment_dialog()

    def manual_assignment_dialog(self):
        """Dialog für manuelle Namenszuweisung"""
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Manuelle Namenszuweisung")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.bg_color)

        # Canvas mit Scrollbar
        canvas = tk.Canvas(dialog, bg=self.bg_color)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Widgets für jedes Secret
        entries = []
        for i, secret_info in enumerate(self.raw_secrets):
            frame = tk.LabelFrame(scrollable_frame, text=f"🔐 Konto {i + 1}", font=("Arial", 10, "bold"),
                                  bg=self.bg_color, fg=self.fg_color, padx=10, pady=10)
            frame.pack(fill="x", padx=10, pady=5)

            # Nahegelegene Strings anzeigen
            nearby = secret_info['nearby_strings']

            if nearby['colon_format']:
                label1 = tk.Label(frame, text="🏷️ Dein Format (Service:Benutzer):", font=("Arial", 9, "bold"),
                                  bg=self.bg_color, fg=self.fg_color)
                label1.pack(anchor="w")
                for j, name in enumerate(nearby['colon_format']):
                    btn = tk.Button(frame, text=name, width=50, bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT)
                    btn.pack(anchor="w", pady=2)
                    btn.bind("<Button-1>",
                             lambda e, idx=len(entries), n=name: entries[idx].delete(0, tk.END) or entries[idx].insert(
                                 0, n))

            if nearby['emails']:
                label2 = tk.Label(frame, text="📧 E-Mail-Adressen:", font=("Arial", 9, "bold"),
                                  bg=self.bg_color, fg=self.fg_color)
                label2.pack(anchor="w", pady=(10, 0))
                for j, email in enumerate(nearby['emails']):
                    btn = tk.Button(frame, text=email, width=50, bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT)
                    btn.pack(anchor="w", pady=2)
                    btn.bind("<Button-1>",
                             lambda e, idx=len(entries), n=email: entries[idx].delete(0, tk.END) or entries[idx].insert(
                                 0, n))

            # Eingabefeld für Namen
            label3 = tk.Label(frame, text="✍️ Eigenen Namen eingeben:", font=("Arial", 9, "bold"),
                              bg=self.bg_color, fg=self.fg_color)
            label3.pack(anchor="w", pady=(10, 0))
            name_var = tk.StringVar(value=f"Konto {i + 1}")
            entry = tk.Entry(frame, textvariable=name_var, width=50,
                             bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color, relief=tk.FLAT)
            entry.pack(fill="x", pady=5)
            entries.append(entry)

        # Scrollbare Elemente
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(fill="x", padx=10, pady=10)

        def apply_names():
            new_accounts = []
            for i, entry in enumerate(entries):
                if i < len(self.raw_secrets):
                    name = entry.get().strip()
                    if not name:
                        name = f"Konto {i + 1}"
                    new_accounts.append({
                        'secret': self.raw_secrets[i]['secret'],
                        'name': name,
                        'issuer': 'Manuell'
                    })

            # Füge neue Konten zur bestehenden Liste hinzu
            existing_count = len(self.accounts)
            for new_account in new_accounts:
                # Prüfe auf Duplikate
                is_duplicate = False
                for existing_account in self.accounts:
                    if existing_account['secret'] == new_account['secret']:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    self.accounts.append(new_account)

            added_count = len(self.accounts) - existing_count
            self.refresh_accounts()
            self.save_accounts()
            self.log(f"✏️ Manuelle Namenszuweisung: {added_count} Konten hinzugefügt")
            self.status_var.set(f"✅ {added_count} Konten hinzugefügt")
            if self.accounts:
                self.start_btn.config(state=tk.NORMAL)
            dialog.destroy()

            # Starte TOTP automatisch
            self.start_totp_automatic()

        tk.Button(button_frame, text="✅ Namen übernehmen", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=apply_names).pack(side="left", padx=(0, 10))
        tk.Button(button_frame, text="❌ Abbrechen", bg=self.button_bg, fg=self.fg_color, relief=tk.FLAT,
                  command=dialog.destroy).pack(side="left")

    def decode_secret(self, secret_bytes):
        """Dekodiert das Secret"""
        if not secret_bytes:
            return ''

        try:
            if isinstance(secret_bytes, str):
                secret_bytes = secret_bytes.encode('ascii')

            decoded = base64.b64decode(secret_bytes, validate=False)
            secret_b32 = base64.b32encode(decoded).decode('ascii').rstrip('=')
            if len(secret_b32) > 10 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret_b32):
                return secret_b32
        except:
            pass

        try:
            secret_b32 = base64.b32encode(secret_bytes).decode('ascii').rstrip('=')
            if len(secret_b32) > 10:
                return secret_b32
        except:
            pass

        return ''

    def test_secret_validity(self, secret_b32):
        """Testet ob ein Secret gültig ist"""
        try:
            totp = pyotp.TOTP(secret_b32)
            code = totp.now()
            return len(code) == 6 and code.isdigit()
        except:
            return False

    def import_accounts(self):
        """Importiert Konten aus JSON-Datei"""
        file_path = filedialog.askopenfilename(
            title="📥 Konten importieren",
            filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_accounts = json.load(f)

                if isinstance(imported_accounts, list):
                    # Füge importierte Konten hinzu (ohne Duplikate)
                    added_count = 0
                    for account in imported_accounts:
                        if 'secret' in account and 'name' in account:
                            # Prüfe auf Duplikate
                            is_duplicate = False
                            for existing_account in self.accounts:
                                if existing_account['secret'] == account['secret']:
                                    is_duplicate = True
                                    break

                            if not is_duplicate:
                                self.accounts.append(account)
                                added_count += 1

                    self.refresh_accounts()
                    self.save_accounts()
                    self.log(f"📥 {added_count} Konten importiert")
                    self.status_var.set(f"✅ {added_count} Konten importiert")
                    if self.accounts:
                        self.start_btn.config(state=tk.NORMAL)
                    messagebox.showinfo("✅ Erfolg", f"{added_count} Konten erfolgreich importiert!")

                    # Starte TOTP automatisch wenn neue Konten hinzugefügt wurden
                    if added_count > 0:
                        self.start_totp_automatic()

                else:
                    messagebox.showerror("❌ Fehler", "Ungültiges Dateiformat!")

            except Exception as e:
                messagebox.showerror("❌ Fehler", f"Fehler beim Importieren: {e}")

    def export_accounts(self):
        """Exportiert Konten in JSON-Datei"""
        if not self.accounts:
            messagebox.showinfo("ℹ️ Info", "Keine Konten zum Exportieren!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
            title="💾 Konten exportieren"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.accounts, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("✅ Erfolg", "Konten erfolgreich exportiert!")
                self.log(f"💾 Konten exportiert nach: {file_path}")
            except Exception as e:
                messagebox.showerror("❌ Fehler", f"Fehler beim Exportieren: {e}")

    def save_accounts(self):
        """Speichert Konten in Konfigurationsdatei"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
            self.log("💾 Konten gespeichert")
        except Exception as e:
            self.log(f"❌ Fehler beim Speichern: {e}")

    def load_accounts(self):
        """Lädt Konten aus Konfigurationsdatei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
                # Nur loggen wenn log_text bereits existiert
                if hasattr(self, 'log_text') and self.log_text:
                    self.log(f"📂 {len(self.accounts)} Konten geladen")
            else:
                self.accounts = []
        except Exception as e:
            # Nur loggen wenn log_text bereits existiert
            if hasattr(self, 'log_text') and self.log_text:
                self.log(f"❌ Fehler beim Laden: {e}")
            self.accounts = []

    def refresh_accounts(self):
        # Sicherstellen, dass accounts_tree existiert
        if hasattr(self, 'accounts_tree') and self.accounts_tree:
            # Leere Treeview
            for item in self.accounts_tree.get_children():
                self.accounts_tree.delete(item)

            # Füge Konten hinzu
            for i, account in enumerate(self.accounts, 1):
                secret_display = account.get('secret', '')
                if len(secret_display) > 25:
                    secret_display = secret_display[:22] + "..."

                self.accounts_tree.insert("", tk.END, values=(
                    i,
                    account.get('name', 'Unbekannt'),
                    account.get('issuer', 'Unbekannt'),
                    secret_display
                ))

        # Aktualisiere auch die Live-Anzeige
        self.search_live_totp()

    def start_totp_automatic(self):
        """Startet TOTP automatisch (ohne Button)"""
        if not self.accounts:
            return

        self.running = True
        self.stop_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("▶️ Live TOTP Codes aktiv")

        # Starte Update-Thread
        thread = threading.Thread(target=self._update_totp_codes, daemon=True)
        self.totp_threads.append(thread)
        thread.start()

    def start_totp(self):
        """Startet TOTP manuell"""
        self.start_totp_automatic()

    def stop_totp(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("⏹️ Bereit")

    def _update_totp_codes(self):
        """Aktualisiert die TOTP-Codes alle Sekunde"""
        while self.running:
            try:
                # Sicherstellen, dass benötigte Elemente existieren
                current_time = int(time.time())
                seconds_remaining = 30 - (current_time % 30)

                # Update alle Anzeigen
                self.root.after(0, self._update_all_displays, seconds_remaining)

            except Exception as e:
                if hasattr(self, 'log_text') and self.log_text:
                    self.log(f"❌ Fehler bei TOTP-Update: {e}")

            time.sleep(1)

    def _update_all_displays(self, seconds_remaining):
        """Aktualisiert alle TOTP-Anzeigen"""
        # Wenn eine Suche aktiv ist, verwende die Suchfunktion
        if hasattr(self, 'live_search_var') and self.live_search_var.get().strip():
            self.search_live_totp()
            return

        # Leere alle Treeviews
        if hasattr(self, 'live_tree') and self.live_tree:
            for item in self.live_tree.get_children():
                self.live_tree.delete(item)

        if hasattr(self, 'totp_tree') and self.totp_tree:
            for item in self.totp_tree.get_children():
                self.totp_tree.delete(item)

        # Füge aktuelle Codes hinzu
        for i, account in enumerate(self.accounts, 1):
            try:
                totp = pyotp.TOTP(account['secret'])
                code = totp.now()
                name = account.get('name', f'Konto {i}')

                # Kürze lange Namen
                if len(name) > 40:
                    display_name = name[:37] + "..."
                else:
                    display_name = name

                # Füge zu allen Anzeigen hinzu
                if hasattr(self, 'live_tree') and self.live_tree:
                    self.live_tree.insert("", tk.END, values=(i, code, display_name, f"{seconds_remaining}s"))

                if hasattr(self, 'totp_tree') and self.totp_tree:
                    self.totp_tree.insert("", tk.END, values=(i, code, display_name, f"{seconds_remaining}s"))

                # Kopiere ersten Code in Zwischenablage
                if i == 1 and HAS_PYPERCLIP and seconds_remaining == 29:
                    try:
                        pyperclip.copy(code)
                    except:
                        pass

            except Exception as e:
                error_display = "❌ FEHLER"
                if hasattr(self, 'live_tree') and self.live_tree:
                    self.live_tree.insert("", tk.END, values=(i, error_display, account.get('name', f'Konto {i}'), "0"))
                if hasattr(self, 'totp_tree') and self.totp_tree:
                    self.totp_tree.insert("", tk.END, values=(i, error_display, account.get('name', f'Konto {i}'), "0"))

    def on_closing(self):
        self.running = False
        self.save_accounts()  # Speichere beim Beenden
        self.root.quit()


def main():
    root = tk.Tk()
    app = TOTPExtractorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()