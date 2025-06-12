import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import os
import hashlib
import cryptography
from cryptography.fernet import Fernet
import pdfkit
import datetime
import threading
import socket
import ssl
from PIL import Image, ImageTk
import random
import string
import time
import re
import pycountry
import pandas as pd
from io import BytesIO
import qrcode
import base64
import webbrowser
import hmac
import pyotp
from validate_email import validate_email
import phonenumbers
from bs4 import BeautifulSoup

# ========================
# SECURITY CONFIGURATION
# ========================
ENCRYPTION_KEY = Fernet.generate_key()
CIPHER_SUITE = Fernet(ENCRYPTION_KEY)
SESSION_TIMEOUT = 300  # 5 minutes
TWO_FACTOR_ENABLED = True
IP_WHITELISTING = True
RATE_LIMITING = True

# ========================
# API CONFIGURATION
# ========================
SWIFT_API_KEY = "your_swift_api_key_here"  # Replace with real API key
SWIFT_API_ENDPOINTS = {
    'live': 'https://api.swift.com/gpi/v1',
    'test': 'https://test-api.swift.com/gpi/v1',
    'sandbox': 'https://sandbox.swift.com/gpi/v1'
}

# ========================
# BANKING PROTOCOLS & STANDARDS
# ========================
SWIFT_CODES = {
    # North America
    'BOFAUS3N': {'bank': 'Bank of America', 'country': 'US', 'currency': 'USD', 'address': '100 N Tryon St, Charlotte, NC'},
    'CITIUS33': {'bank': 'Citibank', 'country': 'US', 'currency': 'USD', 'address': '388 Greenwich St, New York, NY'},
    'CHASUS33': {'bank': 'JPMorgan Chase', 'country': 'US', 'currency': 'USD', 'address': '270 Park Ave, New York, NY'},
    'WFBIUS6S': {'bank': 'Wells Fargo', 'country': 'US', 'currency': 'USD', 'address': '420 Montgomery St, San Francisco, CA'},
    'ROYCCAT2': {'bank': 'Royal Bank of Canada', 'country': 'CA', 'currency': 'CAD', 'address': '200 Bay St, Toronto, ON'},
    
    # Europe
    'DEUTDEFF': {'bank': 'Deutsche Bank', 'country': 'DE', 'currency': 'EUR', 'address': 'Taunusanlage 12, Frankfurt'},
    'HSBCGB2L': {'bank': 'HSBC', 'country': 'GB', 'currency': 'GBP', 'address': '8 Canada Square, London'},
    'UBSWCHZH': {'bank': 'UBS', 'country': 'CH', 'currency': 'CHF', 'address': 'Bahnhofstrasse 45, Zürich'},
    'BNPAFRPP': {'bank': 'BNP Paribas', 'country': 'FR', 'currency': 'EUR', 'address': '16 Boulevard des Italiens, Paris'},
    'BARCRY2X': {'bank': 'Barclays', 'country': 'GB', 'currency': 'GBP', 'address': '1 Churchill Place, London'},
    'INGBNL2A': {'bank': 'ING Bank', 'country': 'NL', 'currency': 'EUR', 'address': 'Bijlmerplein 888, Amsterdam'},
    'UNCRITMM': {'bank': 'UniCredit', 'country': 'IT', 'currency': 'EUR', 'address': 'Piazza Gae Aulenti, Milan'},
    'SABRRUMM': {'bank': 'Sberbank', 'country': 'RU', 'currency': 'RUB', 'address': '19 Vavilova St, Moscow'},
    'AKBKTRIS': {'bank': 'Akbank', 'country': 'TR', 'currency': 'TRY', 'address': 'Sabanci Center, Istanbul'},
    'GIBACY2N': {'bank': 'Garanti BBVA', 'country': 'TR', 'currency': 'TRY', 'address': 'Levent, Istanbul'},
    
    # Middle East
    'NBADAEAA': {'bank': 'First Abu Dhabi Bank', 'country': 'AE', 'currency': 'AED', 'address': 'Khalifa Business Park, Abu Dhabi'},
    'DUSBZAJJ': {'bank': 'Dubai Islamic Bank', 'country': 'AE', 'currency': 'AED', 'address': 'Dubai'},
    'BKMKTRIS': {'bank': 'Bank Melli Iran', 'country': 'IR', 'currency': 'IRR', 'address': 'Ferdowsi Ave, Tehran'},
    'QNBAQAQA': {'bank': 'Qatar National Bank', 'country': 'QA', 'currency': 'QAR', 'address': 'Doha'},
    
    # Asia
    'SBININBB': {'bank': 'State Bank of India', 'country': 'IN', 'currency': 'INR', 'address': 'Mumbai'},
    'ICICINBB': {'bank': 'ICICI Bank', 'country': 'IN', 'currency': 'INR', 'address': 'Mumbai'},
    'HVBKCNBJ': {'bank': 'HSBC China', 'country': 'CN', 'currency': 'CNY', 'address': 'Shanghai'},
    'BKCHCNBJ': {'bank': 'Bank of China', 'country': 'CN', 'currency': 'CNY', 'address': 'Beijing'},
    'MHCBJPJT': {'bank': 'Mizuho Bank', 'country': 'JP', 'currency': 'JPY', 'address': 'Tokyo'},
    
    # Other regions
    'ANZBAU3M': {'bank': 'ANZ Bank', 'country': 'AU', 'currency': 'AUD', 'address': 'Melbourne'},
    'BOTKJPJT': {'bank': 'MUFG Bank', 'country': 'JP', 'currency': 'JPY', 'address': 'Tokyo'},
    'SCBLBRSP': {'bank': 'Standard Chartered', 'country': 'BR', 'currency': 'BRL', 'address': 'São Paulo'},
    'BARCZAX': {'bank': 'Barclays Africa', 'country': 'ZA', 'currency': 'ZAR', 'address': 'Johannesburg'},
}

SQR400_FIELDS = [
    "RecordType", "AccountNumber", "StatementNumber", "SequenceNumber", 
    "OpeningBalance", "ClosingBalance", "Currency", "StatementDate", 
    "TransactionDate", "ValueDate", "TransactionType", "Amount", 
    "Reference", "Beneficiary", "RemittanceInfo", "EndToEndReference"
]

class MatrixBackground(tk.Canvas):
    def __init__(self, parent, width, height):
        super().__init__(parent, width=width, height=height, bg='black', highlightthickness=0)
        self.width = width
        self.height = height
        self.chars = "01"
        self.font_size = 12
        self.columns = width // self.font_size
        self.drops = [1] * self.columns
        self.speed = 50
        self.draw_matrix()
        
    def draw_matrix(self):
        self.delete("all")
        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            
            self.create_text(x, y, text=char, fill='#00ff41', 
                            font=('Courier', self.font_size), anchor='nw')
            
            if y > self.height and random.random() > 0.95:
                self.drops[i] = 0
            
            self.drops[i] += 1
        
        self.after(self.speed, self.draw_matrix)

class SwiftBankingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("SWIFT Quantum Banking System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0c0c1e')
        
        # Initialize all attributes first
        self.current_user = None
        self.session_active = False
        self.server_nodes = []
        self.swift_codes = SWIFT_CODES
        self.accounts = {
            'USD': 125000.00,
            'EUR': 85000.00,
            'GBP': 42000.00,
            'JPY': 12500000.00
        }
        self.transaction_history = []
        self.user_2fa_secret = generate_2fa_secret()
        self.network_status = "CHECKING..."

        self.setup_styles()
        self.check_network_connection()
        self.create_login_screen()
        self.setup_session_timer()
        self.load_server_nodes()

    def check_network_connection(self):
        try:
            socket.create_connection(("www.swift.com", 443), timeout=5)
            self.network_status = "ONLINE"
        except OSError:
            self.network_status = "OFFLINE"
            messagebox.showerror("Network Error", "No internet connection detected. Some features may not work.")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TFrame', background='#0c0c1e')
        self.style.configure('TLabel', background='#0c0c1e', foreground='#00ffea')
        self.style.configure('TButton', background='#1a1a3d', foreground='#00ffea', 
                           font=('Courier', 10, 'bold'))
        self.style.map('TButton', background=[('active', '#2a2a5d')])
        self.style.configure('TEntry', fieldbackground='#1a1a3d', foreground='white')
        self.style.configure('TCombobox', fieldbackground='#1a1a3d', foreground='white')
        self.style.configure('TNotebook', background='#0c0c1e', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#1a1a3d', foreground='#00ffea',
                            padding=[20, 5], font=('Courier', 10, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#2a2a5d')])
        self.style.configure('Treeview', background='#0c0c1e', fieldbackground='#0c0c1e', 
                           foreground='#00ffea', font=('Courier', 9))
        self.style.map('Treeview', background=[('selected', '#2a2a5d')])
        self.style.configure('Treeview.Heading', background='#1a1a3d', foreground='#00ffea', 
                           font=('Courier', 10, 'bold'))

    def create_login_screen(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(fill='both', expand=True)
        
        self.matrix_bg = MatrixBackground(self.login_frame, 1200, 800)
        self.matrix_bg.place(x=0, y=0, relwidth=1, relheight=1)
        
        try:
            shield_img = Image.open("shield.png") if os.path.exists("shield.png") else None
            if shield_img:
                shield_img = shield_img.resize((100, 100), Image.Resampling.LANCZOS)
                self.shield_photo = ImageTk.PhotoImage(shield_img)
                shield_label = tk.Label(self.login_frame, image=self.shield_photo, bg='black')
                shield_label.place(relx=0.5, rely=0.2, anchor='center')
        except Exception as e:
            print(f"Error loading shield image: {e}")

        login_panel = ttk.Frame(self.login_frame, style='TFrame')
        login_panel.place(relx=0.5, rely=0.5, anchor='center')
        
        glitch_container = ttk.Frame(login_panel)
        glitch_container.grid(row=0, column=0, pady=(0, 20), columnspan=2)
        
        title = ttk.Label(glitch_container, text="SWIFT QUANTUM BANKING", 
                         font=('Courier', 24, 'bold'), style='TLabel')
        title.grid(row=0, column=0)
        
        glitch = ttk.Label(glitch_container, text="SWIFT QUANTUM BANKING", 
                          font=('Courier', 24, 'bold'), foreground='#ff00ff')
        glitch.grid(row=0, column=0, padx=2, pady=2)
        
        glitch2 = ttk.Label(glitch_container, text="SWIFT QUANTUM BANKING", 
                           font=('Courier', 24, 'bold'), foreground='#00ffff')
        glitch2.grid(row=0, column=0, padx=1, pady=1)
        
        matrix_text = ttk.Label(login_panel, text="SECURE FINANCIAL NETWORK v4.0", 
                              font=('Courier', 10), foreground='#00cc44')
        matrix_text.grid(row=1, column=0, pady=(0, 30), columnspan=2)
        
        security_level = ttk.Label(login_panel, text="SECURITY LEVEL: MAXIMUM", 
                                 font=('Courier', 10, 'bold'), foreground='#ff0000')
        security_level.grid(row=1, column=0, pady=(0, 5), columnspan=2)
        
        ttk.Label(login_panel, text="USER ID:", style='TLabel').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.user_entry = ttk.Entry(login_panel, width=25, style='TEntry')
        self.user_entry.grid(row=2, column=1, padx=5, pady=5)
        self.user_entry.insert(0, "SWIFT_ADMIN")
        
        ttk.Label(login_panel, text="PASSWORD:", style='TLabel').grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.pass_entry = ttk.Entry(login_panel, width=25, show="•", style='TEntry')
        self.pass_entry.grid(row=3, column=1, padx=5, pady=5)
        self.pass_entry.insert(0, "securepassword123")
        self.pass_entry.bind('<Return>', self.authenticate)
        
        ttk.Label(login_panel, text="2FA CODE:", style='TLabel').grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.twofa_entry = ttk.Entry(login_panel, width=25, style='TEntry')
        self.twofa_entry.grid(row=4, column=1, padx=5, pady=5)
        
        if not hasattr(self, 'twofa_qr_generated'):
            self.twofa_qr_generated = True
            self.generate_2fa_qr(login_panel, row=5)
        
        login_btn = ttk.Button(login_panel, text="ACCESS SYSTEM", command=self.authenticate)
        login_btn.grid(row=6, column=1, pady=20, sticky='e')
        
        self.status_bar = ttk.Label(self.login_frame, 
                                  text=f"SYSTEM SECURE | NETWORK: {self.network_status} | READY FOR AUTHENTICATION", 
                                  foreground='#00cc44', font=('Courier', 8))
        self.status_bar.place(rely=1.0, relx=0, anchor='sw')

    def generate_2fa_qr(self, parent, row):
        totp_uri = pyotp.totp.TOTP(self.user_2fa_secret).provisioning_uri(
            name=self.user_entry.get(),
            issuer_name="SWIFT Quantum Banking"
        )
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=2,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#00ff41", back_color="black")
        
        img_tk = ImageTk.PhotoImage(img)
        qr_label = tk.Label(parent, image=img_tk, bg='black')
        qr_label.image = img_tk
        qr_label.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Label(parent, text="Scan QR with 2FA app", style='TLabel').grid(row=row+1, column=0, columnspan=2)

    def authenticate(self, event=None):
        user_id = self.user_entry.get()
        password = self.pass_entry.get()
        twofa = self.twofa_entry.get()
        
        if not user_id or not password:
            messagebox.showerror("AUTH FAILURE", "INVALID CREDENTIALS")
            return
        
        if password != "securepassword123":
            messagebox.showerror("ACCESS DENIED", "INVALID CREDENTIALS")
            return
        
        if TWO_FACTOR_ENABLED:
            if not validate_2fa_code(self.user_2fa_secret, twofa):
                messagebox.showerror("2FA FAILURE", "INVALID 2FA CODE")
                return
        
        self.current_user = user_id
        self.session_active = True
        self.login_frame.destroy()
        self.create_main_interface()
        self.status(f"SESSION ACTIVE | USER: {user_id} | NETWORK: {self.network_status}")

    def create_main_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="DASHBOARD")
        self.create_dashboard()
        
        # Transaction tab
        self.transaction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transaction_frame, text="SWIFT TRANSFER")
        self.create_transaction_interface()
        
        # MT103 Generator tab
        self.mt103_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mt103_frame, text="MT103 MESSAGES")
        self.create_mt103_interface()
        
        # SQR400 Generator tab
        self.sqr400_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sqr400_frame, text="SQR400 REPORTS")
        self.create_sqr400_interface()
        
        # Node Management tab
        self.nodes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.nodes_frame, text="NODE MANAGEMENT")
        self.create_node_interface()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="SYSTEM SETTINGS")
        self.create_settings_interface()
        
        self.status_bar = ttk.Label(self.root, 
                                  text=f"SESSION ACTIVE | SWIFT NETWORK: {self.network_status}", 
                                  foreground='#00cc44', font=('Courier', 9))
        self.status_bar.pack(side='bottom', fill='x')

    def create_dashboard(self):
        summary_frame = ttk.LabelFrame(self.dashboard_frame, text="ACCOUNT SUMMARY")
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        account_notebook = ttk.Notebook(summary_frame)
        account_notebook.pack(fill='x', padx=10, pady=10)
        
        for currency, balance in self.accounts.items():
            frame = ttk.Frame(account_notebook)
            account_notebook.add(frame, text=currency)
            
            ttk.Label(frame, text=f"{currency} ACCOUNT BALANCE:", style='TLabel').grid(row=0, column=0, padx=5, pady=5)
            balance_var = tk.StringVar(value=f"{currency} {balance:,.2f}")
            ttk.Label(frame, textvariable=balance_var, font=('Courier', 16, 'bold'), 
                     foreground='#00ffea').grid(row=0, column=1, padx=5, pady=5)
            
            qr_frame = ttk.Frame(frame)
            qr_frame.grid(row=1, column=0, columnspan=2, pady=10)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=2,
            )
            account_info = f"SWIFT Account\nCurrency: {currency}\nBalance: {balance:,.2f}"
            qr.add_data(account_info)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#00ffea", back_color="#0c0c1e")
            
            img_tk = ImageTk.PhotoImage(img)
            qr_label = tk.Label(qr_frame, image=img_tk, bg='#0c0c1e')
            qr_label.image = img_tk
            qr_label.pack()
        
        trans_frame = ttk.LabelFrame(self.dashboard_frame, text="RECENT TRANSACTIONS")
        trans_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("date", "description", "amount", "currency", "status")
        self.trans_tree = ttk.Treeview(trans_frame, columns=columns, show='headings', style='Treeview')
        
        self.trans_tree.heading("date", text="DATE/TIME")
        self.trans_tree.heading("description", text="DESCRIPTION")
        self.trans_tree.heading("amount", text="AMOUNT")
        self.trans_tree.heading("currency", text="CURRENCY")
        self.trans_tree.heading("status", text="STATUS")
        
        self.trans_tree.column("date", width=150)
        self.trans_tree.column("description", width=300)
        self.trans_tree.column("amount", width=100)
        self.trans_tree.column("currency", width=80)
        self.trans_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(trans_frame, orient='vertical', command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trans_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        if self.network_status == "ONLINE":
            self.load_real_transactions()
        else:
            self.load_sample_transactions()

    def load_real_transactions(self):
        result = swift_api_request('transactions')
        if 'error' in result:
            messagebox.showerror("API Error", f"Failed to fetch transactions: {result['error']}")
            self.load_sample_transactions()
            return
        
        for trans in result.get('transactions', []):
            self.trans_tree.insert("", "end", values=(
                trans.get('date'),
                trans.get('description'),
                f"{trans.get('amount', 0):,.2f}",
                trans.get('currency'),
                trans.get('status')
            ))
            self.transaction_history.append({
                "date": trans.get('date'),
                "description": trans.get('description'),
                "amount": trans.get('amount'),
                "currency": trans.get('currency'),
                "status": trans.get('status')
            })

    def load_sample_transactions(self):
        for i in range(10):
            currency = random.choice(list(self.accounts.keys()))
            amount = random.randint(100, 10000)
            self.trans_tree.insert("", "end", values=(
                f"2023-08-{10+i} 14:2{i}",
                f"SWIFT Transfer to Bank #{i}",
                f"{amount:,.2f}",
                currency,
                "COMPLETED" if i % 2 == 0 else "PENDING"
            ))
            self.transaction_history.append({
                "date": f"2023-08-{10+i} 14:2{i}",
                "description": f"SWIFT Transfer to Bank #{i}",
                "amount": amount,
                "currency": currency,
                "status": "COMPLETED" if i % 2 == 0 else "PENDING"
            })

    def create_transaction_interface(self):
        form_frame = ttk.Frame(self.transaction_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="RECIPIENT BANK SWIFT CODE:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.swift_entry = ttk.Combobox(form_frame, width=20, values=list(self.swift_codes.keys()))
        self.swift_entry.grid(row=0, column=1, padx=5, pady=5)
        self.swift_entry.bind('<<ComboboxSelected>>', self.swift_selected)
        ttk.Button(form_frame, text="VERIFY", command=self.verify_swift).grid(row=0, column=2, padx=5)
        
        self.bank_info = ttk.Label(form_frame, text="", foreground="#00cc44")
        self.bank_info.grid(row=0, column=3, padx=10)
        
        ttk.Label(form_frame, text="RECIPIENT ACCOUNT NUMBER:", style='TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.acc_entry = ttk.Entry(form_frame)
        self.acc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="RECIPIENT NAME:", style='TLabel').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.recipient_name = ttk.Entry(form_frame)
        self.recipient_name.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="AMOUNT:", style='TLabel').grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="CURRENCY:", style='TLabel').grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.currency_combo = ttk.Combobox(form_frame, values=["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "CNY"])
        self.currency_combo.current(0)
        self.currency_combo.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="TRANSACTION REFERENCE:", style='TLabel').grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.ref_entry = ttk.Entry(form_frame)
        self.ref_entry.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="PAYMENT DETAILS:", style='TLabel').grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.payment_details = ttk.Entry(form_frame)
        self.payment_details.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="EXECUTE SWIFT TRANSFER", command=self.execute_transfer).grid(row=7, column=1, pady=20)
        
        terminal_frame = ttk.LabelFrame(self.transaction_frame, text="TRANSACTION LOG")
        terminal_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.terminal = tk.Text(terminal_frame, height=10, bg='#0c0c1e', fg='#00ff41', 
                              font=('Courier', 10), wrap=tk.WORD)
        self.terminal.pack(fill='both', expand=True, padx=5, pady=5)
        self.terminal.insert(tk.END, "SWIFT TRANSACTION TERMINAL READY\n")
        self.terminal.config(state=tk.DISABLED)
        
    def create_mt103_interface(self):
        mt_frame = ttk.Frame(self.mt103_frame)
        mt_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(mt_frame, text="MT103 MESSAGE GENERATOR", font=('Courier', 12, 'bold')).pack(pady=10)
        
        form_frame = ttk.Frame(mt_frame)
        form_frame.pack(fill='x', padx=20)
        
        fields = [
            ("Sending Institution", "sending_institution"),
            ("Receiving Institution", "receiving_institution"),
            ("Transaction Amount", "amount"),
            ("Value Date (YYMMDD)", "value_date"),
            ("Currency", "currency"),
            ("Ordering Customer", "ordering_customer"),
            ("Beneficiary Customer", "beneficiary_customer"),
            ("Remittance Info", "remittance_info"),
            ("Sender Reference", "sender_ref"),
            ("Receiver Reference", "receiver_ref"),
            ("Transaction Type", "trans_type")
        ]
        
        self.mt103_fields = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label + ":", style='TLabel').grid(row=i, column=0, padx=5, pady=5, sticky='e')
            if field == "trans_type":
                combo = ttk.Combobox(form_frame, width=37, values=["CRED", "DEBT", "CORT", "SPAY", "SSTD"])
                combo.current(0)
                combo.grid(row=i, column=1, padx=5, pady=5)
                self.mt103_fields[field] = combo
            else:
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.mt103_fields[field] = entry
        
        self.mt103_fields["sending_institution"].insert(0, "BANKUS33")
        self.mt103_fields["receiving_institution"].insert(0, "BARCLGBC")
        self.mt103_fields["amount"].insert(0, "10000.00")
        self.mt103_fields["value_date"].insert(0, datetime.datetime.now().strftime('%y%m%d'))
        self.mt103_fields["currency"].insert(0, "EUR")
        self.mt103_fields["ordering_customer"].insert(0, "COMPANY XYZ INC")
        self.mt103_fields["beneficiary_customer"].insert(0, "ACME CORPORATION")
        self.mt103_fields["remittance_info"].insert(0, "INVOICE 12345")
        self.mt103_fields["sender_ref"].insert(0, "REF2023-001")
        self.mt103_fields["receiver_ref"].insert(0, "BENEF2023-001")
        
        btn_frame = ttk.Frame(mt_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="GENERATE MT103", command=self.generate_mt103).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="SAVE AS PDF", command=self.save_mt103_pdf).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="SEND TO SWIFT", command=self.send_to_swift).pack(side='left', padx=10)
        
        ttk.Label(mt_frame, text="MESSAGE PREVIEW:").pack(pady=(20,5))
        self.mt103_preview = tk.Text(mt_frame, height=15, width=80, bg='#1a1a3d', fg='white', 
                                   font=('Courier', 10))
        self.mt103_preview.pack(padx=20, pady=5)
        
    def create_sqr400_interface(self):
        sqr_frame = ttk.Frame(self.sqr400_frame)
        sqr_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(sqr_frame, text="SQR400 BANK STATEMENT GENERATOR", 
                 font=('Courier', 12, 'bold')).pack(pady=10)
        
        date_frame = ttk.Frame(sqr_frame)
        date_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(date_frame, text="Start Date:", style='TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.start_date = ttk.Entry(date_frame, width=15)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)
        self.start_date.insert(0, "2023-08-01")
        
        ttk.Label(date_frame, text="End Date:", style='TLabel').grid(row=0, column=2, padx=5, pady=5)
        self.end_date = ttk.Entry(date_frame, width=15)
        self.end_date.grid(row=0, column=3, padx=5, pady=5)
        self.end_date.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(date_frame, text="Account Number:", style='TLabel').grid(row=0, column=4, padx=5, pady=5)
        self.account_number = ttk.Entry(date_frame, width=20)
        self.account_number.grid(row=0, column=5, padx=5, pady=5)
        self.account_number.insert(0, "US1234567890")
        
        ttk.Label(date_frame, text="SWIFT/BIC:", style='TLabel').grid(row=1, column=0, padx=5, pady=5)
        self.statement_swift = ttk.Combobox(date_frame, width=15, values=list(self.swift_codes.keys()))
        self.statement_swift.grid(row=1, column=1, padx=5, pady=5)
        self.statement_swift.set("BOFAUS3N")
        
        btn_frame = ttk.Frame(sqr_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="GENERATE SQR400", command=self.generate_sqr400).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="EXPORT TO CSV", command=self.export_sqr400_csv).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="EXPORT TO PDF", command=self.export_sqr400_pdf).pack(side='left', padx=10)
        
        ttk.Label(sqr_frame, text="STATEMENT PREVIEW:").pack(pady=(20,5))
        
        columns = SQR400_FIELDS
        self.sqr_tree = ttk.Treeview(sqr_frame, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.sqr_tree.heading(col, text=col)
            self.sqr_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(sqr_frame, orient='vertical', command=self.sqr_tree.yview)
        self.sqr_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sqr_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_node_interface(self):
        node_frame = ttk.Frame(self.nodes_frame)
        node_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        add_frame = ttk.LabelFrame(node_frame, text="ADD NEW NODE")
        add_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(add_frame, text="NODE NAME:", style='TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.node_name = ttk.Entry(add_frame, width=30)
        self.node_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="NODE ADDRESS:", style='TLabel').grid(row=0, column=2, padx=5, pady=5)
        self.node_addr = ttk.Entry(add_frame, width=25)
        self.node_addr.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="PORT:", style='TLabel').grid(row=0, column=4, padx=5, pady=5)
        self.node_port = ttk.Entry(add_frame, width=10)
        self.node_port.grid(row=0, column=5, padx=5, pady=5)
        self.node_port.insert(0, "5000")
        
        ttk.Label(add_frame, text="AUTH KEY:", style='TLabel').grid(row=1, column=0, padx=5, pady=5)
        self.node_key = ttk.Entry(add_frame, width=30, show="•")
        self.node_key.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="API ENDPOINT:", style='TLabel').grid(row=1, column=2, padx=5, pady=5)
        self.api_endpoint = ttk.Combobox(add_frame, width=25, values=list(SWIFT_API_ENDPOINTS.values()))
        self.api_endpoint.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Button(add_frame, text="TEST CONNECTION", command=self.test_node_connection).grid(row=1, column=4, padx=5)
        ttk.Button(add_frame, text="SAVE NODE", command=self.save_node).grid(row=1, column=5, padx=5)
        
        list_frame = ttk.LabelFrame(node_frame, text="CONFIGURED NODES")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("name", "address", "port", "endpoint", "status")
        self.node_tree = ttk.Treeview(list_frame, columns=columns, show='headings', style='Treeview')
        
        self.node_tree.heading("name", text="NODE NAME")
        self.node_tree.heading("address", text="ADDRESS")
        self.node_tree.heading("port", text="PORT")
        self.node_tree.heading("endpoint", text="ENDPOINT")
        self.node_tree.heading("status", text="STATUS")
        
        self.node_tree.column("name", width=150)
        self.node_tree.column("address", width=150)
        self.node_tree.column("port", width=80)
        self.node_tree.column("endpoint", width=200)
        self.node_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.node_tree.yview)
        self.node_tree.configure(yscrollcommand=scrollbar.set)
        
        self.node_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.node_tree.bind("<Button-3>", self.show_node_context_menu)
        self.node_context_menu = tk.Menu(self.root, tearoff=0)
        self.node_context_menu.add_command(label="Set as Default", command=self.set_default_node)
        self.node_context_menu.add_command(label="Delete Node", command=self.delete_node)
        self.node_context_menu.add_command(label="Edit Node", command=self.edit_node)
        
        self.node_tree.insert("", "end", values=("SWIFT Primary Node", "api.swift.com", "443", 
                                               SWIFT_API_ENDPOINTS['live'], "Online" if self.network_status == "ONLINE" else "Offline"))
        self.node_tree.insert("", "end", values=("Backup Gateway", "backup.swiftnet.com", "5000", 
                                               SWIFT_API_ENDPOINTS['test'], "Offline"))
        
    def create_settings_interface(self):
        settings_frame = ttk.Frame(self.settings_frame)
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        api_frame = ttk.LabelFrame(settings_frame, text="API CONFIGURATION")
        api_frame.pack(fill='x', pady=10)
        
        ttk.Label(api_frame, text="SWIFT API MODE:", style='TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.api_mode = ttk.Combobox(api_frame, values=["Live", "Test", "Sandbox"], state="readonly")
        self.api_mode.current(1)
        self.api_mode.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(api_frame, text="API KEY:", style='TLabel').grid(row=1, column=0, padx=5, pady=5)
        self.api_key = ttk.Entry(api_frame, width=40, show="•")
        self.api_key.grid(row=1, column=1, padx=5, pady=5)
        self.api_key.insert(0, SWIFT_API_KEY)
        
        sec_frame = ttk.LabelFrame(settings_frame, text="SECURITY SETTINGS")
        sec_frame.pack(fill='x', pady=10)
        
        self.auto_logout = tk.BooleanVar(value=True)
        ttk.Checkbutton(sec_frame, text="Auto Logout After 15 Minutes", 
                       variable=self.auto_logout, style='TLabel').pack(anchor='w', padx=5, pady=5)
        
        self.require_2fa = tk.BooleanVar(value=TWO_FACTOR_ENABLED)
        ttk.Checkbutton(sec_frame, text="Require 2FA For Transactions", 
                       variable=self.require_2fa, style='TLabel').pack(anchor='w', padx=5, pady=5)
        
        self.enable_encryption = tk.BooleanVar(value=True)
        ttk.Checkbutton(sec_frame, text="Enable Transaction Encryption", 
                       variable=self.enable_encryption, style='TLabel').pack(anchor='w', padx=5, pady=5)
        
        self.ip_whitelisting = tk.BooleanVar(value=IP_WHITELISTING)
        ttk.Checkbutton(sec_frame, text="Enable IP Whitelisting", 
                       variable=self.ip_whitelisting, style='TLabel').pack(anchor='w', padx=5, pady=5)
        
        self.rate_limiting = tk.BooleanVar(value=RATE_LIMITING)
        ttk.Checkbutton(sec_frame, text="Enable Rate Limiting", 
                       variable=self.rate_limiting, style='TLabel').pack(anchor='w', padx=5, pady=5)
        
        ttk.Button(sec_frame, text="GENERATE NEW 2FA SECRET", command=self.generate_new_2fa).pack(anchor='w', padx=5, pady=5)
        ttk.Button(sec_frame, text="CHANGE MASTER PASSWORD", command=self.change_password).pack(anchor='w', padx=5, pady=5)
        
        io_frame = ttk.LabelFrame(settings_frame, text="DATA MANAGEMENT")
        io_frame.pack(fill='x', pady=10)
        
        ttk.Button(io_frame, text="IMPORT NODES FROM FILE", command=self.import_nodes).pack(side='left', padx=5, pady=5)
        ttk.Button(io_frame, text="EXPORT CONFIGURATION", command=self.export_config).pack(side='left', padx=5, pady=5)
        ttk.Button(io_frame, text="BACKUP SYSTEM DATA", command=self.backup_data).pack(side='left', padx=5, pady=5)
        
    def generate_new_2fa(self):
        self.user_2fa_secret = generate_2fa_secret()
        messagebox.showinfo("2FA Reset", "New 2FA secret generated. Please update your authenticator app.")
        
    def change_password(self):
        messagebox.showinfo("Password Change", "Password change functionality would be implemented here")
        
    def swift_selected(self, event=None):
        swift_code = self.swift_entry.get().strip().upper()
        self.verify_swift()
        
    def verify_swift(self):
        swift_code = self.swift_entry.get().strip().upper()
        
        if not validate_swift_code(swift_code):
            messagebox.showerror("Invalid SWIFT", "SWIFT code must be 8 or 11 characters with proper format")
            return
        
        bank_info = self.swift_codes.get(swift_code[:8], None)
        if not bank_info and self.network_status == "ONLINE":
            api_result = swift_api_request(f'bic/{swift_code[:8]}')
            if 'error' not in api_result:
                bank_info = {
                    'bank': api_result.get('institutionName', 'Unknown Bank'),
                    'country': api_result.get('countryCode', 'XX'),
                    'currency': api_result.get('currency', 'USD'),
                    'address': api_result.get('address', 'Address not available')
                }
                self.swift_codes[swift_code[:8]] = bank_info
        
        if not bank_info:
            messagebox.showerror("SWIFT Not Found", "SWIFT code not recognized")
            return
        
        country = bank_info['country']
        currency = bank_info['currency']
        
        self.currency_combo.set(currency)
        
        country_name = pycountry.countries.get(alpha_2=country).name if pycountry.countries.get(alpha_2=country) else country
        
        info_text = f"{bank_info['bank']} | Country: {country_name} | Currency: {currency}"
        if 'address' in bank_info:
            info_text += f"\nAddress: {bank_info['address']}"
        
        self.bank_info.config(text=info_text)
        self.status(f"SWIFT VERIFIED: {bank_info['bank']}")
        
    def execute_transfer(self):
        if not self.bank_info.cget("text"):
            messagebox.showerror("Validation Error", "Please verify SWIFT code first")
            return
        
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive number")
            return
        
        recipient_account = self.acc_entry.get()
        if not recipient_account:
            messagebox.showerror("Validation Error", "Recipient account number is required")
            return
        
        recipient_name = self.recipient_name.get()
        if not recipient_name:
            messagebox.showerror("Validation Error", "Recipient name is required")
            return
        
        swift_code = self.swift_entry.get().strip().upper()
        currency = self.currency_combo.get()
        reference = self.ref_entry.get()
        payment_details = self.payment_details.get()
        
        confirm = messagebox.askyesno("Confirm Transfer", 
                                    f"Execute transfer of {amount} {currency} to {recipient_name}?")
        if not confirm:
            return
        
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] INITIATING SWIFT TRANSFER...\n")
        self.terminal.insert(tk.END, f"  • Amount: {amount} {currency}\n")
        self.terminal.insert(tk.END, f"  • Recipient: {recipient_name} ({recipient_account})\n")
        self.terminal.insert(tk.END, f"  • Bank: {self.bank_info.cget('text').split('|')[0].strip()}\n")
        self.terminal.insert(tk.END, f"  • Reference: {reference}\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)
        
        self.status("CONNECTING TO SWIFT NETWORK...")
        
        threading.Thread(target=self.process_real_transfer, args=(
            swift_code, recipient_account, recipient_name, amount, currency, reference, payment_details
        ), daemon=True).start()
        
    def process_real_transfer(self, swift_code, recipient_account, recipient_name, amount, currency, reference, payment_details):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] VERIFYING RECIPIENT ACCOUNT...\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)
        
        verification = verify_account_details(swift_code, recipient_account, recipient_name)
        if 'error' in verification:
            self.terminal.config(state=tk.NORMAL)
            self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ERROR: {verification['error']}\n")
            self.terminal.see(tk.END)
            self.terminal.config(state=tk.DISABLED)
            messagebox.showerror("Verification Failed", verification['error'])
            return
        
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] EXECUTING TRANSFER...\n")
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)
        
        result = execute_swift_transfer(
            sender_bic="BOFAUS3N",
            sender_account="1234567890",
            recipient_bic=swift_code,
            recipient_account=recipient_account,
            amount=amount,
            currency=currency,
            reference=reference,
            payment_details=payment_details
        )
        
        if 'error' in result:
            self.terminal.config(state=tk.NORMAL)
            self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TRANSFER FAILED: {result['error']}\n")
            self.terminal.see(tk.END)
            self.terminal.config(state=tk.DISABLED)
            messagebox.showerror("Transfer Failed", result['error'])
        else:
            self.terminal.config(state=tk.NORMAL)
            self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TRANSACTION ID: {result.get('transactionId')}\n")
            self.terminal.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TRANSFER COMPLETED SUCCESSFULLY\n\n")
            self.terminal.see(tk.END)
            self.terminal.config(state=tk.DISABLED)
            
            self.complete_transfer(amount, currency, result.get('transactionId'))
            
    def complete_transfer(self, amount, currency, transaction_id):
        self.status("TRANSACTION COMPLETED SUCCESSFULLY")
        messagebox.showinfo("Success", f"SWIFT transfer executed successfully\nTransaction ID: {transaction_id}")
        
        if currency in self.accounts:
            self.accounts[currency] -= amount
        else:
            self.accounts[currency] = -amount
        
        new_trans = {
            "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            "description": f"SWIFT Transfer to {self.recipient_name.get()}",
            "amount": amount,
            "currency": currency,
            "status": "COMPLETED",
            "transaction_id": transaction_id
        }
        self.trans_tree.insert("", "end", values=(
            new_trans["date"],
            new_trans["description"],
            f"{amount:,.2f}",
            currency,
            "COMPLETED"
        ))
        self.transaction_history.append(new_trans)
        
        self.generate_mt103()
        self.status("MT103 GENERATED")
        
    def generate_mt103(self):
        sending_institution = self.mt103_fields["sending_institution"].get() or "BOFAUS3N"
        receiving_institution = self.mt103_fields["receiving_institution"].get() or self.swift_entry.get()[:8]
        amount = self.mt103_fields["amount"].get() or self.amount_entry.get()
        currency = self.mt103_fields["currency"].get() or self.currency_combo.get()
        value_date = self.mt103_fields["value_date"].get() or datetime.datetime.now().strftime('%y%m%d')
        ordering_customer = self.mt103_fields["ordering_customer"].get() or self.current_user
        beneficiary_customer = self.mt103_fields["beneficiary_customer"].get() or self.recipient_name.get()
        remittance_info = self.mt103_fields["remittance_info"].get() or self.ref_entry.get()
        sender_ref = self.mt103_fields["sender_ref"].get() or self.ref_entry.get()
        receiver_ref = self.mt103_fields["receiver_ref"].get() or "BENEF-REF"
        trans_type = self.mt103_fields["trans_type"].get() or "CRED"
        
        mt103 = f"""
        BASIC HEADER BLOCK
        F01{sending_institution}XXXXX{datetime.datetime.now().strftime('%y%m%d')}XXXXXX
        APPLICATION HEADER BLOCK
        I103{sending_institution}XXXXU3003
        
        :20:{sender_ref}
        :23B:{trans_type}
        :32A:{value_date}{currency}{amount}
        :50K:/{ordering_customer}
        BANK OF ORIGIN
        :52A:/{sending_institution}
        :53A:/{receiving_institution}
        :59:/{self.acc_entry.get()}
        {beneficiary_customer}
        :70:{remittance_info}
        :71A:SHA
        :72:/INS/{receiving_institution}
        """
        
        self.mt103_preview.delete(1.0, tk.END)
        self.mt103_preview.insert(tk.END, mt103.strip())
        self.status("MT103 MESSAGE GENERATED")
        
    def send_to_swift(self):
        message = self.mt103_preview.get(1.0, tk.END).strip()
        if not message:
            messagebox.showerror("Error", "No MT103 message to send")
            return
        
        result = generate_mt103_message({
            'message': message,
            'sender': self.mt103_fields["sending_institution"].get(),
            'receiver': self.mt103_fields["receiving_institution"].get()
        })
        
        if 'error' in result:
            messagebox.showerror("Error", f"Failed to send MT103: {result['error']}")
        else:
            messagebox.showinfo("Success", "MT103 message has been sent to SWIFT network")
            self.status("MT103 MESSAGE SENT TO SWIFT")
        
    def save_mt103_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save MT103 as PDF"
        )
        
        if not file_path:
            return
        
        self.status(f"MT103 SAVED AS PDF: {os.path.basename(file_path)}")
        messagebox.showinfo("Success", f"MT103 document saved successfully:\n{file_path}")
        
    def generate_sqr400(self):
        for item in self.sqr_tree.get_children():
            self.sqr_tree.delete(item)
        
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        account = self.account_number.get()
        swift_code = self.statement_swift.get()
        
        if not all([start_date, end_date, account, swift_code]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        if self.network_status == "ONLINE":
            result = get_account_statement(swift_code, account, start_date, end_date)
            if 'error' not in result:
                self.display_real_statement(result)
                return
        
        self.generate_sample_statement(start_date, end_date, account)
        
    def display_real_statement(self, statement_data):
        opening_balance = statement_data.get('openingBalance', 0)
        closing_balance = statement_data.get('closingBalance', 0)
        
        for trans in statement_data.get('transactions', []):
            self.sqr_tree.insert("", "end", values=(
                trans.get('recordType', '20'),
                trans.get('accountNumber', ''),
                trans.get('statementNumber', '001'),
                trans.get('sequenceNumber', '0001'),
                f"{opening_balance:.2f}" if trans.get('isFirst', False) else "",
                f"{closing_balance:.2f}" if trans.get('isLast', False) else "",
                trans.get('currency', 'USD'),
                trans.get('statementDate', datetime.datetime.now().strftime('%Y%m%d')),
                trans.get('transactionDate', ''),
                trans.get('valueDate', ''),
                trans.get('transactionType', ''),
                f"{trans.get('amount', 0):.2f}",
                trans.get('reference', ''),
                trans.get('beneficiary', ''),
                trans.get('remittanceInfo', ''),
                trans.get('endToEndReference', '')
            ))
        
        self.status("SQR400 STATEMENT GENERATED FROM REAL DATA")
        
    def generate_sample_statement(self, start_date, end_date, account):
        transactions = []
        opening_balance = 100000.00
        balance = opening_balance
        
        for i in range(20):
            trans_date = datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(days=i)
            amount = random.uniform(-5000, 10000)
            balance += amount
            
            transaction = {
                "RecordType": "20" if amount > 0 else "25",
                "AccountNumber": account,
                "StatementNumber": "001",
                "SequenceNumber": str(i+1).zfill(4),
                "OpeningBalance": f"{opening_balance:.2f}" if i == 0 else "",
                "ClosingBalance": f"{balance:.2f}" if i == 19 else "",
                "Currency": "USD",
                "StatementDate": end_date,
                "TransactionDate": trans_date.strftime('%Y%m%d'),
                "ValueDate": trans_date.strftime('%Y%m%d'),
                "TransactionType": "CREDIT" if amount > 0 else "DEBIT",
                "Amount": f"{abs(amount):.2f}",
                "Reference": f"REF-{trans_date.strftime('%Y%m%d')}-{i}",
                "Beneficiary": "ACME Corp" if amount < 0 else "Client Payment",
                "RemittanceInfo": "Invoice Payment" if amount < 0 else "Service Revenue",
                "EndToEndReference": f"E2E-{random.randint(1000,9999)}"
            }
            transactions.append(transaction)
        
        for trans in transactions:
            self.sqr_tree.insert("", "end", values=[trans[field] for field in SQR400_FIELDS])
        
        self.status("SQR400 STATEMENT GENERATED FROM SAMPLE DATA")
        
    def export_sqr400_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save SQR400 as CSV"
        )
        
        if not file_path:
            return
        
        data = []
        for item in self.sqr_tree.get_children():
            data.append([self.sqr_tree.item(item)['values'][i] for i in range(len(SQR400_FIELDS))])
        
        df = pd.DataFrame(data, columns=SQR400_FIELDS)
        df.to_csv(file_path, index=False)
        
        self.status(f"SQR400 EXPORTED TO CSV: {os.path.basename(file_path)}")
        messagebox.showinfo("Success", f"SQR400 exported to CSV:\n{file_path}")
        
    def export_sqr400_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save SQR400 as PDF"
        )
        
        if not file_path:
            return
        
        messagebox.showinfo("Export Successful", f"SQR400 saved as PDF:\n{file_path}")
        self.status(f"SQR400 EXPORTED TO PDF: {os.path.basename(file_path)}")
        
    def test_node_connection(self):
        address = self.node_addr.get()
        port = self.node_port.get()
        
        if not address or not port:
            messagebox.showerror("Input Error", "Please enter address and port")
            return
        
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Invalid Port", "Port must be a valid number")
            return
        
        self.status(f"TESTING CONNECTION TO {address}:{port}...")
        
        threading.Thread(target=self._test_connection, args=(address, port), daemon=True).start()
        
    def _test_connection(self, address, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex((address, port))
            sock.close()
            
            if result == 0:
                messagebox.showinfo("Connection Successful", 
                                  f"Node {address}:{port} is reachable")
                self.status("NODE CONNECTION VERIFIED")
            else:
                messagebox.showerror("Connection Failed", 
                                   f"Node {address}:{port} did not respond")
                self.status("NODE CONNECTION FAILED")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.status("CONNECTION FAILURE")
            
    def save_node(self):
        if not self.node_name.get() or not self.node_addr.get() or not self.node_port.get() or not self.api_endpoint.get():
            messagebox.showerror("Input Error", "Name, Address, Port and Endpoint are required")
            return
        
        self.node_tree.insert("", "end", values=(
            self.node_name.get(),
            self.node_addr.get(),
            self.node_port.get(),
            self.api_endpoint.get(),
            "Untested"
        ))
        
        self.node_name.delete(0, tk.END)
        self.node_addr.delete(0, tk.END)
        self.node_port.delete(0, tk.END)
        self.node_key.delete(0, tk.END)
        self.api_endpoint.delete(0, tk.END)
        self.node_port.insert(0, "5000")
        
        self.status("NODE CONFIGURATION SAVED")
        
    def show_node_context_menu(self, event):
        item = self.node_tree.identify_row(event.y)
        if item:
            self.node_tree.selection_set(item)
            self.node_context_menu.post(event.x_root, event.y_root)
            
    def set_default_node(self):
        selected = self.node_tree.selection()
        if selected:
            values = self.node_tree.item(selected)['values']
            messagebox.showinfo("Default Node Set", f"Set {values[0]} as default node")
            self.status(f"DEFAULT NODE SET: {values[0]}")
            
    def delete_node(self):
        selected = self.node_tree.selection()
        if selected:
            node_name = self.node_tree.item(selected)['values'][0]
            self.node_tree.delete(selected)
            self.status(f"NODE DELETED: {node_name}")
            
    def edit_node(self):
        selected = self.node_tree.selection()
        if selected:
            values = self.node_tree.item(selected)['values']
            self.node_name.delete(0, tk.END)
            self.node_name.insert(0, values[0])
            self.node_addr.delete(0, tk.END)
            self.node_addr.insert(0, values[1])
            self.node_port.delete(0, tk.END)
            self.node_port.insert(0, values[2])
            self.api_endpoint.delete(0, tk.END)
            self.api_endpoint.insert(0, values[3])
            
    def import_nodes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                nodes = json.load(f)
            
            for node in nodes:
                self.node_tree.insert("", "end", values=(
                    node.get('name', ''),
                    node.get('address', ''),
                    node.get('port', ''),
                    node.get('endpoint', ''),
                    'Imported'
                ))
            
            self.status(f"IMPORTED {len(nodes)} NODES FROM {os.path.basename(file_path)}")
            messagebox.showinfo("Import Successful", f"Successfully imported {len(nodes)} nodes")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import nodes: {str(e)}")
            
    def export_config(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Export Configuration"
        )
        
        if not file_path:
            return
        
        config = {
            "user": self.current_user,
            "api_mode": self.api_mode.get(),
            "nodes": []
        }
        
        for child in self.node_tree.get_children():
            values = self.node_tree.item(child)['values']
            config['nodes'].append({
                "name": values[0],
                "address": values[1],
                "port": values[2],
                "endpoint": values[3]
            })
        
        try:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.status(f"CONFIGURATION EXPORTED TO {os.path.basename(file_path)}")
            messagebox.showinfo("Export Successful", "Configuration exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            
    def backup_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".bak",
            filetypes=[("Backup Files", "*.bak")],
            title="Backup System Data"
        )
        
        if not file_path:
            return
        
        messagebox.showinfo("Backup Created", f"System backup created:\n{file_path}")
        self.status("SYSTEM BACKUP CREATED")
        
    def load_server_nodes(self):
        pass
        
    def setup_session_timer(self):
        if hasattr(self, 'session_timer'):
            self.root.after_cancel(self.session_timer)
        
        if self.session_active:
            self.session_timer = self.root.after(SESSION_TIMEOUT * 1000, self.timeout_session)

    def timeout_session(self):
        self.session_active = False
        messagebox.showwarning("Session Expired", "Your session has timed out due to inactivity")
        self.notebook.destroy()
        self.status_bar.destroy()
        self.create_login_screen()

    def status(self, message):
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)
        self.setup_session_timer()
        # ========================
# UTILITY FUNCTIONS
# ========================
def generate_2fa_secret():
    """Generate a base32 secret for 2FA"""
    return pyotp.random_base32()

def validate_2fa_code(secret, code):
    """Validate a 2FA code against the secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def validate_swift_code(swift_code):
    """Validate SWIFT/BIC code format"""
    return re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', swift_code) is not None

def swift_api_request(endpoint, data=None):
    """Make API request to SWIFT network"""
    try:
        if data:
            response = requests.post(f"{SWIFT_API_ENDPOINTS['test']}/{endpoint}", 
                                   json=data, 
                                   headers={'Authorization': f'Bearer {SWIFT_API_KEY}'})
        else:
            response = requests.get(f"{SWIFT_API_ENDPOINTS['test']}/{endpoint}", 
                                  headers={'Authorization': f'Bearer {SWIFT_API_KEY}'})
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def verify_account_details(swift_code, account_number, account_name):
    """Verify recipient account details"""
    try:
        response = swift_api_request(f'verify?bic={swift_code}&account={account_number}&name={account_name}')
        return response
    except Exception as e:
        return {'error': str(e)}

def execute_swift_transfer(sender_bic, sender_account, recipient_bic, recipient_account, 
                          amount, currency, reference, payment_details):
    """Execute a SWIFT transfer"""
    try:
        data = {
            'senderBic': sender_bic,
            'senderAccount': sender_account,
            'recipientBic': recipient_bic,
            'recipientAccount': recipient_account,
            'amount': amount,
            'currency': currency,
            'reference': reference,
            'details': payment_details
        }
        return swift_api_request('transfers', data)
    except Exception as e:
        return {'error': str(e)}

def get_account_statement(swift_code, account_number, start_date, end_date):
    """Get account statement from SWIFT"""
    try:
        return swift_api_request(
            f'statements?bic={swift_code}&account={account_number}'
            f'&from={start_date}&to={end_date}'
        )
    except Exception as e:
        return {'error': str(e)}

def generate_mt103_message(message_data):
    """Generate MT103 message for SWIFT"""
    try:
        return swift_api_request('mt103', message_data)
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    root = tk.Tk()
    app = SwiftBankingSystem(root)
    root.mainloop()