import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import imaplib
import email
from email.header import decode_header
import threading
import time
import random
import math
import re
import os
import json as jsond
import binascii
import platform
import subprocess
import qrcode
from datetime import datetime, timezone, timedelta
from PIL import Image
import requests

# Try to import Windows-specific modules
_0xwin32_available = False
try:
    if os.name == 'nt':
        import win32security
        _0xwin32_available = True
except ModuleNotFoundError:
    print("Some modules might be missing. Please install required packages.")
    time.sleep(1.5)

class _0x1a2b3c:
    def __init__(self, _0x4d5e6f, _0x7g8h9i, _0x0j1k2l, _0x3m4n5o):
        if len(_0x7g8h9i) != 10:
            exec(compile(base64.b64decode("cHJpbnQoIkludmFsaWQgb3duZXIgSUQgZm9ybWF0Iik=").decode(), '<string>', 'exec'))
            time.sleep(3)
            os._exit(1)
    
        self._0xp1q2r3 = _0x4d5e6f
        self._0xs4t5u6 = _0x7g8h9i
        self._0xv7w8x9 = _0x0j1k2l
        self._0xy0z1a2 = _0x3m4n5o
        self._0xb3c4d5 = ""
        self._0xe6f7g8 = ""
        self._0xh9i0j1 = False
        self._0xk2l3m4()

    def _0xk2l3m4(self):
        if self._0xb3c4d5 != "":
            print("You've already initialized!")
            time.sleep(3)
            os._exit(1)
        
        _0xn5o6p7 = {
            "type": "init",
            "ver": self._0xv7w8x9,
            "hash": self._0xy0z1a2,
            "name": self._0xp1q2r3,
            "ownerid": self._0xs4t5u6
        }

        _0xq8r9s0 = self._0xt1u2v3(_0xn5o6p7)

        if _0xq8r9s0 == "KeyAuth_Invalid":
            print("The application doesn't exist")
            time.sleep(3)
            os._exit(1)

        _0xw4x5y6 = jsond.loads(_0xq8r9s0)

        if _0xw4x5y6["message"] == "invalidver":
            if _0xw4x5y6["download"] != "":
                print("New Version Available")
                _0xz7a8b9 = _0xw4x5y6["download"]
                os.system(f"start {_0xz7a8b9}")
                time.sleep(3)
                os._exit(1)
            else:
                print("Invalid Version, Contact owner to add download link to latest app version")
                time.sleep(3)
                os._exit(1)

        if not _0xw4x5y6["success"]:
            print(_0xw4x5y6["message"])
            time.sleep(3)
            os._exit(1)

        self._0xb3c4d5 = _0xw4x5y6["sessionid"]
        self._0xh9i0j1 = True
        return True

    def _0xc0d1e2(self, _0xf3g4h5, _0xi6j7k8, _0xl9m0n1=None, _0xo2p3q4=None):
        self._0xr5s6t7()
        if _0xo2p3q4 is None:
            _0xo2p3q4 = self._0xu8v9w0()

        _0xx1y2z3 = {
            "type": "login",
            "username": _0xf3g4h5,
            "pass": _0xi6j7k8,
            "hwid": _0xo2p3q4,
            "sessionid": self._0xb3c4d5,
            "name": self._0xp1q2r3,
            "ownerid": self._0xs4t5u6,
        }
        
        if _0xl9m0n1 is not None:
            _0xx1y2z3["code"] = _0xl9m0n1

        _0xa4b5c6 = self._0xt1u2v3(_0xx1y2z3)

        _0xd7e8f9 = jsond.loads(_0xa4b5c6)

        if _0xd7e8f9["success"]:
            self._0xg0h1i2(_0xd7e8f9["info"])
            return True, _0xd7e8f9["message"]
        else:
            return False, _0xd7e8f9["message"]

    def _0xj3k4l5(self, _0xm6n7o8, _0xp9q0r1=None, _0xs2t3u4=None):
        self._0xr5s6t7()
        if _0xs2t3u4 is None:
            _0xs2t3u4 = self._0xu8v9w0()

        _0xv5w6x7 = {
            "type": "license",
            "key": _0xm6n7o8,
            "hwid": _0xs2t3u4,
            "sessionid": self._0xb3c4d5,
            "name": self._0xp1q2r3,
            "ownerid": self._0xs4t5u6
        }
        
        if _0xp9q0r1 is not None:
            _0xv5w6x7["code"] = _0xp9q0r1

        _0xy8z9a0 = self._0xt1u2v3(_0xv5w6x7)

        _0xb1c2d3 = jsond.loads(_0xy8z9a0)

        if _0xb1c2d3["success"]:
            self._0xg0h1i2(_0xb1c2d3["info"])
            return True, _0xb1c2d3["message"]
        else:
            return False, _0xb1c2d3["message"]

    def _0xr5s6t7(self):
        if not self._0xh9i0j1:
            print("Initialize first, in order to use the functions")
            time.sleep(3)
            os._exit(1)

    def _0xu8v9w0(self):
        if platform.system() == "Linux":
            with open("/etc/machine-id") as f:
                _0xe4f5g6 = f.read()
                return _0xe4f5g6
        elif platform.system() == 'Windows':
            try:
                if _0xwin32_available:
                    _0xh7i8j9 = os.getlogin()
                    _0xk0l1m2 = win32security.LookupAccountName(None, _0xh7i8j9)[0]
                    _0xe4f5g6 = win32security.ConvertSidToStringSid(_0xk0l1m2)
                    return _0xe4f5g6
                else:
                    return str(random.randint(100000, 999999))
            except:
                # Fallback method if win32security fails
                return str(random.randint(100000, 999999))
        elif platform.system() == 'Darwin':
            _0xn3o4p5 = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", 
                                     stdout=subprocess.PIPE, shell=True).communicate()[0]
            _0xq6r7s8 = _0xn3o4p5.decode().split('=', 1)[1].replace(' ', '')
            _0xe4f5g6 = _0xq6r7s8[1:-2]
            return _0xe4f5g6
        else:
            return str(random.randint(100000, 999999))

    def _0xt1u2v3(self, _0xw9x0y1):
        try:
            _0xz2a3b4 = requests.post(
                "https://keyauth.win/api/1.3/", data=_0xw9x0y1, timeout=10
            )
            return _0xz2a3b4.text
        except requests.exceptions.Timeout: 
            return '{"success":false,"message":"Request timed out"}'
        except:
            return '{"success":false,"message":"Unknown error"}'

    class _0xc5d6e7:
        username = ip = hwid = expires = createdate = lastlogin = subscription = subscriptions = ""

    _0xf8g9h0 = _0xc5d6e7()

    def _0xg0h1i2(self, _0xi1j2k3):
        self._0xf8g9h0.username = _0xi1j2k3["username"]
        self._0xf8g9h0.ip = _0xi1j2k3["ip"]
        self._0xf8g9h0.hwid = _0xi1j2k3["hwid"] or "N/A"
        self._0xf8g9h0.expires = _0xi1j2k3["subscriptions"][0]["expiry"]
        self._0xf8g9h0.createdate = _0xi1j2k3["createdate"]
        self._0xf8g9h0.lastlogin = _0xi1j2k3["lastlogin"]
        self._0xf8g9h0.subscription = _0xi1j2k3["subscriptions"][0]["subscription"]
        self._0xf8g9h0.subscriptions = _0xi1j2k3["subscriptions"]


import base64
exec(base64.b64decode("Y2xhc3MgXzB4bDRtNW42OiAjIEdtYWlsQ2xlYW5lckFwcA==").decode())
class _0xl4m5n6:
    def __init__(self, _0xo7p8q9):
        self._0xr0s1t2 = _0xo7p8q9
        self._0xr0s1t2.title("HATE'S GMAIL DELETER TOOL")
        self._0xr0s1t2.geometry("800x700")
        self._0xr0s1t2.configure(bg='#000000')
        
        self._0xr0s1t2.resizable(True, True)
        self._0xu3v4w5 = False
        
        self._0xx6y7z8 = ttk.Style()
        self._0xx6y7z8.theme_use('clam')
        
        self._0xx6y7z8.configure('TFrame', background='#000000')
        self._0xx6y7z8.configure('TLabel', background='#000000', foreground='#ff00ff', font=('Arial', 10))
        self._0xx6y7z8.configure('Header.TLabel', font=('Arial', 18, 'bold'), foreground='#ff00ff')
        self._0xx6y7z8.configure('Red.TButton', background='#ff00ff', foreground='#000000')
        self._0xx6y7z8.map('Red.TButton', background=[('active', '#ff44ff')])
        self._0xx6y7z8.configure('TEntry', fieldbackground='#222222', foreground='#ffffff')
        self._0xx6y7z8.configure('Vertical.TScrollbar', background='#333333', darkcolor='#222222', 
                            lightcolor='#444444', troughcolor='#111111')
        
        self._0xa9b0c1 = []
        self._0xd2e3f4()
        
        self._0xg5h6i7 = None
        self._0xj8k9l0 = False
        
        self._0xm1n2o3()
        self._0xp4q5r6()
        self._0xs7t8u9()
        
    def _0xd2e3f4(self):
        for _ in range(30):
            _0xv0w1x2 = random.randint(0, 800)
            _0xy3z4a5 = random.randint(0, 700)
            _0xb6c7d8 = random.randint(1, 4)
            _0xe9f0g1 = random.uniform(0.5, 2.0)
            self._0xa9b0c1.append({
                'x': _0xv0w1x2, 'y': _0xy3z4a5, 'size': _0xb6c7d8, 'speed': _0xe9f0g1,
                'direction': random.uniform(0, 2 * math.pi)
            })
    
    def _0xs7t8u9(self):
        for _0xh2i3j4 in self._0xa9b0c1:
            _0xh2i3j4['x'] += math.cos(_0xh2i3j4['direction']) * _0xh2i3j4['speed']
            _0xh2i3j4['y'] += math.sin(_0xh2i3j4['direction']) * _0xh2i3j4['speed']
            
            if _0xh2i3j4['x'] > self._0xr0s1t2.winfo_width(): _0xh2i3j4['x'] = 0
            if _0xh2i3j4['x'] < 0: _0xh2i3j4['x'] = self._0xr0s1t2.winfo_width()
            if _0xh2i3j4['y'] > self._0xr0s1t2.winfo_height(): _0xh2i3j4['y'] = 0
            if _0xh2i3j4['y'] < 0: _0xh2i3j4['y'] = self._0xr0s1t2.winfo_height()
        
        self._0xr0s1t2.after(50, self._0xs7t8u9)
        
    def _0xk5l6m7(self, event=None):
        self._0xu3v4w5 = not self._0xu3v4w5
        self._0xr0s1t2.attributes("-fullscreen", self._0xu3v4w5)
        return "break"
        
    def _0xn8o9p0(self, event=None):
        self._0xu3v4w5 = False
        self._0xr0s1t2.attributes("-fullscreen", False)
        return "break"
        
    def _0xm1n2o3(self):
        self._0xq1r2s3 = tk.Canvas(self._0xr0s1t2, bg='#000000', highlightthickness=0)
        self._0xq1r2s3.pack(fill=tk.BOTH, expand=True)
        
        def _0xt4u5v6():
            self._0xq1r2s3.delete("particles")
            for _0xh2i3j4 in self._0xa9b0c1:
                self._0xq1r2s3.create_oval(
                    _0xh2i3j4['x'], _0xh2i3j4['y'], _0xh2i3j4['x'] + _0xh2i3j4['size'], _0xh2i3j4['y'] + _0xh2i3j4['size'],
                    fill='#ff00ff', outline='', tags="particles"
                )
            self._0xr0s1t2.after(50, _0xt4u5v6)
        
        _0xt4u5v6()
        
        self._0xw7x8y9 = ttk.Frame(self._0xq1r2s3, padding=20)
        self._0xz0a1b2 = self._0xq1r2s3.create_window(
            self._0xr0s1t2.winfo_width()/2, 20, anchor=tk.N, window=self._0xw7x8y9
        )
        
        def _0xc3d4e5(event):
            self._0xq1r2s3.coords(self._0xz0a1b2, event.width/2, 20)
        
        self._0xq1r2s3.bind('<Configure>', _0xc3d4e5)
        
        self._0xf6g7h8 = ttk.Label(self._0xw7x8y9, text="Press F11 for fullscreen | ESC to exit", 
                                    foreground='#ff88ff', background='#000000')
        
        self._0xr0s1t2.bind("<F11>", self._0xk5l6m7)
        self._0xr0s1t2.bind("<Escape>", self._0xn8o9p0)
        
        self._0xi9j0k1 = ttk.Frame(self._0xw7x8y9)
        
        ttk.Label(self._0xi9j0k1, text="KeyAuth Login", font=('Arial', 16, 'bold'), 
                 foreground='#ff00ff').pack(pady=10)
        
        ttk.Label(self._0xi9j0k1, text="Username:", foreground='#ff00ff').pack(anchor=tk.W, pady=5)
        self._0xl2m3n4 = ttk.Entry(self._0xi9j0k1, width=30, style='TEntry')
        self._0xl2m3n4.pack(pady=5, fill=tk.X)
        
        ttk.Label(self._0xi9j0k1, text="Password:", foreground='#ff00ff').pack(anchor=tk.W, pady=5)
        self._0xo5p6q7 = ttk.Entry(self._0xi9j0k1, width=30, show="*", style='TEntry')
        self._0xo5p6q7.pack(pady=5, fill=tk.X)
        
        ttk.Label(self._0xi9j0k1, text="License Key (alternative):", foreground='#ff00ff').pack(anchor=tk.W, pady=5)
        self._0xr8s9t0 = ttk.Entry(self._0xi9j0k1, width=30, style='TEntry')
        self._0xr8s9t0.pack(pady=5, fill=tk.X)
        
        self._0xu1v2w3 = tk.Canvas(self._0xi9j0k1, width=120, height=35, bg='#000000', highlightthickness=0)
        self._0xu1v2w3.pack(pady=10)
        self._0xx4y5z6 = self._0xu1v2w3.create_rectangle(0, 0, 120, 35, fill='#ff00ff', outline='')
        self._0xa7b8c9 = self._0xu1v2w3.create_text(60, 17, text="Login", 
                                                             fill='#000000', font=('Arial', 10, 'bold'))
        self._0xu1v2w3.bind("<Button-1>", lambda e: self._0xd0e1f2())
        self._0xu1v2w3.bind("<Enter>", lambda e: self._0xu1v2w3.itemconfig(self._0xx4y5z6, fill='#ff44ff'))
        self._0xu1v2w3.bind("<Leave>", lambda e: self._0xu1v2w3.itemconfig(self._0xx4y5z6, fill='#ff00ff'))
        
        self._0xg3h4i5 = ttk.Label(self._0xi9j0k1, text="", foreground='#ff00ff')
        self._0xg3h4i5.pack(pady=5)
        
        self._0xj6k7l8 = ttk.Frame(self._0xw7x8y9)
        
        self._0xm9n0o1 = ttk.Label(self._0xj6k7l8, text="HATE'S GMAIL DELETER TOOL", 
                                font=('Arial', 20, 'bold'), foreground='#ff00ff', 
                                background='#000000')
        self._0xm9n0o1.pack(pady=10)
        
        self._0xp2q3r4 = ttk.Frame(self._0xj6k7l8)
        self._0xp2q3r4.pack(fill=tk.X, pady=10)
        
        _0xs5t6u7 = """
        ⚠️ WARNING: This tool will PERMANENTLY DELETE ALL EMAILS from your Gmail account.
        
        This tool is designed for use when selling an account and the buyer requests 
        a completely empty inbox. 
        
        PLEASE NOTE: Change all accounts that use this Gmail address before proceeding.
        You will lose access to any services linked to this email after account transfer.
        
        By using this tool, you acknowledge that you understand these risks and that
        all deletions are PERMANENT and IRREVERSIBLE.
        """
        
        self._0xv8w9x0 = ttk.Label(self._0xp2q3r4, text=_0xs5t6u7, wraplength=650, 
                                 justify=tk.LEFT, foreground='#ff00ff', background='#000000')
        self._0xv8w9x0.pack()
        
        self._0xy1z2a3 = ttk.Frame(self._0xj6k7l8)
        self._0xy1z2a3.pack(fill=tk.X, pady=20)
        
        self._0xb4c5d6 = ttk.Label(self._0xy1z2a3, text="Gmail Address:", foreground='#ff00ff')
        self._0xb4c5d6.grid(row=0, column=0, sticky=tk.W, pady=5)
        self._0xe7f8g9 = ttk.Entry(self._0xy1z2a3, width=40, style='TEntry')
        self._0xe7f8g9.grid(row=0, column=1, padx=10, pady=5)
        
        self._0xh0i1j2 = ttk.Label(self._0xy1z2a3, text="App Password:", foreground='#ff00ff')
        self._0xh0i1j2.grid(row=1, column=0, sticky=tk.W, pady=5)
        self._0xk3l4m5 = ttk.Entry(self._0xy1z2a3, width=40, show="*", style='TEntry')
        self._0xk3l4m5.grid(row=1, column=1, padx=10, pady=5)
        
        self._0xn6o7p8 = ttk.Label(self._0xy1z2a3, 
                                 text="Note: You need to generate an App Password from Google Account settings.\nRegular password won't work.", 
                                 foreground='#ff88ff', font=('Arial', 9), background='#000000')
        self._0xn6o7p8.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        self._0xq9r0s1 = ttk.Frame(self._0xj6k7l8)
        self._0xq9r0s1.pack(fill=tk.X, pady=10)
        
        self._0xt2u3v4 = tk.Canvas(self._0xq9r0s1, height=20, bg='#000000', highlightthickness=0)
        self._0xt2u3v4.pack(fill=tk.X, pady=5)
        self._0xw5x6y7 = self._0xt2u3v4.create_rectangle(0, 0, 0, 20, fill='#ff00ff', outline='')
        
        self._0xz8a9b0 = ttk.Label(self._0xq9r0s1, text="Enter credentials and click Start Deletion", foreground='#ff00ff')
        self._0xz8a9b0.pack()
        
        self._0xc1d2e3 = ttk.Frame(self._0xj6k7l8)
        self._0xc1d2e3.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self._0xf4g5h6 = ttk.Label(self._0xc1d2e3, text="Deletion Log:", foreground='#ff00ff')
        self._0xf4g5h6.pack(anchor=tk.W)
        
        self._0xi7j8k9 = scrolledtext.ScrolledText(self._0xc1d2e3, width=80, height=15, 
                                                 bg='#111111', fg='#ff00ff',
                                                 insertbackground='#ff00ff',
                                                 selectbackground='#ff44ff',
                                                 font=('Courier New', 10))
        self._0xi7j8k9.pack(fill=tk.BOTH, expand=True)
        self._0xi7j8k9.config(state=tk.DISABLED)
        
        self._0xl0m1n2 = ttk.Frame(self._0xj6k7l8)
        self._0xl0m1n2.pack(pady=10)
        
        self._0xo3p4q5 = tk.Canvas(self._0xl0m1n2, width=150, height=40, bg='#000000', highlightthickness=0)
        self._0xo3p4q5.pack(side=tk.LEFT, padx=5)
        self._0xr6s7t8 = self._0xo3p4q5.create_rectangle(0, 0, 150, 40, fill='#ff00ff', outline='')
        self._0xu9v0w1 = self._0xo3p4q5.create_text(75, 20, text="Start Deletion", 
                                                             fill='#000000', font=('Arial', 12, 'bold'))
        self._0xo3p4q5.bind("<Button-1>", lambda e: self._0xx2y3z4())
        self._0xo3p4q5.bind("<Enter>", self._0xa5b6c7)
        self._0xo3p4q5.bind("<Leave>", self._0xd8e9f0)
        
        self._0xg1h2i3 = tk.Canvas(self._0xl0m1n2, width=100, height=40, bg='#000000', highlightthickness=0)
        self._0xg1h2i3.pack(side=tk.LEFT, padx=5)
        self._0xj4k5l6 = self._0xg1h2i3.create_rectangle(0, 0, 100, 40, fill='#333333', outline='')
        self._0xm7n8o9 = self._0xg1h2i3.create_text(50, 20, text="Clear Log", 
                                                             fill='#ff00ff', font=('Arial', 12, 'bold'))
        self._0xg1h2i3.bind("<Button-1>", lambda e: self._0xp0q1r2())
        self._0xg1h2i3.bind("<Enter>", self._0xs3t4u5)
        self._0xg1h2i3.bind("<Leave>", self._0xv6w7x8)
        
        self._0xy9z0a1 = tk.Canvas(self._0xl0m1n2, width=100, height=40, bg='#000000', highlightthickness=0)
        self._0xy9z0a1.pack(side=tk.LEFT, padx=5)
        self._0xb2c3d4 = self._0xy9z0a1.create_rectangle(0, 0, 100, 40, fill='#333333', outline='')
        self._0xe5f6g7 = self._0xy9z0a1.create_text(50, 20, text="Logout", 
                                                             fill='#ff00ff', font=('Arial', 12, 'bold'))
        self._0xy9z0a1.bind("<Button-1>", lambda e: self._0xh8i9j0())
        self._0xy9z0a1.bind("<Enter>", lambda e: self._0xy9z0a1.itemconfig(self._0xb2c3d4, fill='#444444'))
        self._0xy9z0a1.bind("<Leave>", lambda e: self._0xy9z0a1.itemconfig(self._0xb2c3d4, fill='#333333'))
        
        self._0xk1l2m3 = ttk.Label(self._0xj6k7l8, text="Thank you for using HATE'S GMAIL DELETER TOOL", 
                                font=('Arial', 12, 'italic'), foreground='#ff00ff', background='#000000')
        self._0xk1l2m3.pack(pady=10)
        
    def _0xp4q5r6(self):
        self._0xj6k7l8.pack_forget()
        self._0xi9j0k1.pack(fill=tk.BOTH, expand=True, pady=20)
        self._0xf6g7h8.pack(pady=5)
        
    def _0xn4o5p6(self):
        self._0xi9j0k1.pack_forget()
        self._0xj6k7l8.pack(fill=tk.BOTH, expand=True)
        self._0xf6g7h8.pack(pady=5)
        
    def _0xd0e1f2(self):
        _0xq7r8s9 = self._0xl2m3n4.get().strip()
        _0xt0u1v2 = self._0xo5p6q7.get().strip()
        _0xw3x4y5 = self._0xr8s9t0.get().strip()
        
        if not _0xq7r8s9:
            self._0xg3h4i5.config(text="Username is required")
            return
            
        try:
            self._0xg5h6i7 = _0x1a2b3c(
                "H8tec0in's Application",
                "VscAGSWDnE",
                "1.0",
                "getchecksum()"
            )
        except:
            self._0xg3h4i5.config(text="Failed to initialize authentication")
            return
            
        if _0xt0u1v2:
            _0xz6a7b8, _0xc9d0e1 = self._0xg5h6i7._0xc0d1e2(_0xq7r8s9, _0xt0u1v2)
            if _0xz6a7b8:
                self._0xj8k9l0 = True
                self._0xg3h4i5.config(text="Login successful!")
                self._0xr0s1t2.after(1000, self._0xn4o5p6)
            else:
                self._0xg3h4i5.config(text=f"Login failed: {_0xc9d0e1}")
        elif _0xw3x4y5:
            _0xz6a7b8, _0xc9d0e1 = self._0xg5h6i7._0xj3k4l5(_0xw3x4y5)
            if _0xz6a7b8:
                self._0xj8k9l0 = True
                self._0xg3h4i5.config(text="License accepted!")
                self._0xr0s1t2.after(1000, self._0xn4o5p6)
            else:
                self._0xg3h4i5.config(text=f"License invalid: {_0xc9d0e1}")
        else:
            self._0xg3h4i5.config(text="Please enter either password or license key")
            
    def _0xh8i9j0(self):
        self._0xj8k9l0 = False
        self._0xg5h6i7 = None
        self._0xp4q5r6()
        self._0xl2m3n4.delete(0, tk.END)
        self._0xo5p6q7.delete(0, tk.END)
        self._0xr8s9t0.delete(0, tk.END)
        self._0xg3h4i5.config(text="Logged out successfully")
        
    def _0xa5b6c7(self, event):
        self._0xo3p4q5.itemconfig(self._0xr6s7t8, fill='#ff44ff')
        
    def _0xd8e9f0(self, event):
        self._0xo3p4q5.itemconfig(self._0xr6s7t8, fill='#ff00ff')
        
    def _0xs3t4u5(self, event):
        self._0xg1h2i3.itemconfig(self._0xj4k5l6, fill='#444444')
        
    def _0xv6w7x8(self, event):
        self._0xg1h2i3.itemconfig(self._0xj4k5l6, fill='#333333')
        
    def _0xf2g3h4(self, _0xi5j6k7):
        _0xl8m9n0 = self._0xt2u3v4.winfo_width()
        self._0xt2u3v4.coords(self._0xw5x6y7, 0, 0, _0xl8m9n0 * (_0xi5j6k7/100), 20)
        
    def _0xo1p2q3(self, _0xr4s5t6):
        self._0xi7j8k9.config(state=tk.NORMAL)
        self._0xi7j8k9.insert(tk.END, _0xr4s5t6 + "\n")
        self._0xi7j8k9.see(tk.END)
        self._0xi7j8k9.config(state=tk.DISABLED)
        
    def _0xp0q1r2(self):
        self._0xi7j8k9.config(state=tk.NORMAL)
        self._0xi7j8k9.delete(1.0, tk.END)
        self._0xi7j8k9.config(state=tk.DISABLED)
        self._0xz8a9b0.config(text="Log cleared")
        
    def _0xu7v8w9(self, _0xx0y1z2, _0xa3b4c5):
        try:
            self._0xo1p2q3("Connecting to Gmail server...")
            _0xd6e7f8 = imaplib.IMAP4_SSL("imap.gmail.com")
            
            self._0xo1p2q3("Authenticating...")
            _0xd6e7f8.login(_0xx0y1z2, _0xa3b4c5)
            
            self._0xo1p2q3("Connected successfully!")
            return _0xd6e7f8
        except Exception as e:
            self._0xo1p2q3(f"Connection failed: {str(e)}")
            return None
        
    def _0xg9h0i1(self, _0xj2k3l4, _0xm5n6o7="inbox"):
        try:
            _0xj2k3l4.select(_0xm5n6o7)
            _0xp8q9r0, _0xs1t2u3 = _0xj2k3l4.search(None, "ALL")
            if _0xp8q9r0 == "OK":
                return len(_0xs1t2u3[0].split())
            return 0
        except Exception as e:
            self._0xo1p2q3(f"Error getting email count: {str(e)}")
            return 0
            
    def _0xv4w5x6(self, _0xy7z8a9, _0xb0c1d2="inbox"):
        try:
            _0xy7z8a9.select(_0xb0c1d2)
            _0xe3f4g5, _0xh6i7j8 = _0xy7z8a9.search(None, "ALL")
            
            if _0xe3f4g5 != "OK":
                self._0xo1p2q3(f"Failed to search emails in {_0xb0c1d2}")
                return 0
                
            _0xk9l0m1 = _0xh6i7j8[0].split()
            _0xn2o3p4 = len(_0xk9l0m1)
            
            if _0xn2o3p4 == 0:
                self._0xo1p2q3(f"No emails found in {_0xb0c1d2}")
                return 0
                
            self._0xo1p2q3(f"Found {_0xn2o3p4} emails in {_0xb0c1d2}")
            
            _0xq5r6s7 = 50
            _0xt8u9v0 = 0
            
            for _0xw1x2y3 in range(0, _0xn2o3p4, _0xq5r6s7):
                _0xz4a5b6 = _0xk9l0m1[_0xw1x2y3:_0xw1x2y3+_0xq5r6s7]
                
                for _0xc7d8e9 in _0xz4a5b6:
                    _0xy7z8a9.store(_0xc7d8e9, '+FLAGS', '\\Deleted')
                
                _0xy7z8a9.expunge()
                _0xt8u9v0 += len(_0xz4a5b6)
                
                _0xf0g1h2 = min(100, int((_0xw1x2y3 + len(_0xz4a5b6)) / _0xn2o3p4 * 100))
                self._0xf2g3h4(_0xf0g1h2)
                self._0xo1p2q3(f"Deleted {_0xt8u9v0}/{_0xn2o3p4} emails from {_0xb0c1d2}")
                
                time.sleep(0.5)
                
            return _0xt8u9v0
            
        except Exception as e:
            self._0xo1p2q3(f"Error deleting emails from {_0xb0c1d2}: {str(e)}")
            return 0
        
    def _0xx2y3z4(self):
        if not self._0xj8k9l0:
            messagebox.showerror("Error", "You must be logged in to use this feature")
            return
            
        _0xi3j4k5 = self._0xe7f8g9.get().strip()
        _0xl6m7n8 = self._0xk3l4m5.get().strip()
        
        if not _0xi3j4k5 or not _0xl6m7n8:
            messagebox.showerror("Error", "Please enter both email and password")
            return
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", _0xi3j4k5):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
            
        _0xo9p0q1 = messagebox.askyesno("Confirm Deletion", 
                                     "Are you ABSOLUTELY SURE you want to delete ALL emails?\n\nThis action cannot be undone!")
        if not _0xo9p0q1:
            self._0xo1p2q3("Deletion cancelled by user")
            return
            
        self._0xo3p4q5.unbind("<Button-1>")
        self._0xo3p4q5.itemconfig(self._0xr6s7t8, fill='#888888')
        self._0xo3p4q5.itemconfig(self._0xu9v0w1, fill='#444444')
        
        _0xr2s3t4 = threading.Thread(target=self._0xu5v6w7, args=(_0xi3j4k5, _0xl6m7n8))
        _0xr2s3t4.daemon = True
        _0xr2s3t4.start()
        
    def _0xu5v6w7(self, _0xx8y9z0, _0xa1b2c3):
        try:
            _0xd4e5f6 = self._0xu7v8w9(_0xx8y9z0, _0xa1b2c3)
            if not _0xd4e5f6:
                return
                
            _0xg7h8i9 = ["inbox", "sent", "[Gmail]/All Mail", "[Gmail]/Trash", "[Gmail]/Spam"]
            _0xj0k1l2 = 0
            
            for _0xm3n4o5 in _0xg7h8i9:
                self._0xo1p2q3(f"Processing {_0xm3n4o5}...")
                _0xp6q7r8 = self._0xg9h0i1(_0xd4e5f6, _0xm3n4o5)
                
                if _0xp6q7r8 > 0:
                    self._0xo1p2q3(f"Found {_0xp6q7r8} emails in {_0xm3n4o5}")
                    _0xs9t0u1 = self._0xv4w5x6(_0xd4e5f6, _0xm3n4o5)
                    _0xj0k1l2 += _0xs9t0u1
                    self._0xo1p2q3(f"Deleted {_0xs9t0u1} emails from {_0xm3n4o5}")
                else:
                    self._0xo1p2q3(f"No emails found in {_0xm3n4o5}")
            
            self._0xf2g3h4(100)
            self._0xo1p2q3(f"Process completed! Total emails deleted: {_0xj0k1l2}")
            self._0xo1p2q3("PLEASE NOTE: Change all accounts that use this Gmail address")
            self._0xo1p2q3("Thank you for using HATE'S GMAIL DELETER TOOL")
            self._0xz8a9b0.config(text="Deletion completed")
            
            _0xd4e5f6.close()
            _0xd4e5f6.logout()
            
        except Exception as e:
            self._0xo1p2q3(f"Error occurred: {str(e)}")
        finally:
            self._0xr0s1t2.after(0, self._0xv2w3x4)
            
    def _0xv2w3x4(self):
        self._0xo3p4q5.bind("<Button-1>", lambda e: self._0xx2y3z4())
        self._0xo3p4q5.itemconfig(self._0xr6s7t8, fill='#ff00ff')
        self._0xo3p4q5.itemconfig(self._0xu9v0w1, fill='#000000')

if __name__ == "__main__":
    _0xy5z6a7 = tk.Tk()
    _0xb8c9d0 = _0xl4m5n6(_0xy5z6a7)
    _0xy5z6a7.mainloop()