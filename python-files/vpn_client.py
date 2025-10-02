#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini OpenVPN Client (GUI)
Fields: Server (host:port), Username, Password
Buttons: Connect, Disconnect
Requires: openvpn.exe (Windows) or openvpn in PATH (Linux/macOS)
Windows: run as Administrator; Linux: root/sudo typically required for TUN.
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import subprocess, threading, tempfile, os, signal, sys, time, shutil

# Try to discover OpenVPN binary
DEFAULT_WIN_PATH = r"C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
OPENVPN_PATH = shutil.which("openvpn") or (DEFAULT_WIN_PATH if os.path.exists(DEFAULT_WIN_PATH) else None)
DEFAULT_PORT = "1194"

class MiniVPNClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini OpenVPN Client")
        self.geometry("720x520")
        self.proc = None
        self.auth_file = None
        self.ovpn_file = None

        top = tk.Frame(self)
        top.pack(padx=10, pady=10, fill="x")

        # Server
        tk.Label(top, text="Server (host:port):").grid(row=0, column=0, sticky="w")
        self.server_entry = tk.Entry(top)
        self.server_entry.grid(row=0, column=1, sticky="we", padx=6)
        self.server_entry.insert(0, "vpn.example.com:" + DEFAULT_PORT)

        # Username
        tk.Label(top, text="Username:").grid(row=1, column=0, sticky="w")
        self.user_entry = tk.Entry(top)
        self.user_entry.grid(row=1, column=1, sticky="we", padx=6)

        # Password
        tk.Label(top, text="Password:").grid(row=2, column=0, sticky="w")
        self.pass_entry = tk.Entry(top, show="*")
        self.pass_entry.grid(row=2, column=1, sticky="we", padx=6)

        # Buttons
        btnf = tk.Frame(top)
        btnf.grid(row=3, column=0, columnspan=2, pady=8, sticky="w")
        self.connect_btn = tk.Button(btnf, text="Connect", width=14, command=self.connect_clicked)
        self.connect_btn.pack(side="left", padx=6)
        self.disconnect_btn = tk.Button(btnf, text="Disconnect", width=14, command=self.disconnect_clicked, state="disabled")
        self.disconnect_btn.pack(side="left", padx=6)
        tk.Button(btnf, text="Load .ovpn", command=self.load_ovpn).pack(side="left", padx=6)
        tk.Button(btnf, text="Save log", command=self.save_log).pack(side="left", padx=6)

        # OpenVPN path field (visible so user can override)
        pathf = tk.Frame(top)
        pathf.grid(row=4, column=0, columnspan=2, sticky="we", pady=(4,0))
        tk.Label(pathf, text="OpenVPN binary:").pack(side="left")
        self.ovpn_path_entry = tk.Entry(pathf)
        self.ovpn_path_entry.pack(side="left", fill="x", expand=True, padx=6)
        if OPENVPN_PATH:
            self.ovpn_path_entry.insert(0, OPENVPN_PATH)
        else:
            self.ovpn_path_entry.insert(0, DEFAULT_WIN_PATH)

        # Log box
        self.logbox = scrolledtext.ScrolledText(self, state="disabled", height=18)
        self.logbox.pack(padx=10, pady=(0,10), fill="both", expand=True)

        top.columnconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def append_log(self, text):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", text + "\\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")

    def load_ovpn(self):
        path = filedialog.askopenfilename(filetypes=[("OVPN files","*.ovpn"),("All files","*.*")])
        if path:
            self.ovpn_file = path
            self.append_log(f"Loaded .ovpn: {path}")

    def save_log(self):
        path = filedialog.asksaveasfilename(defaultextension=".log")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.logbox.get("1.0", "end"))
            messagebox.showinfo("Saved", f"Log saved to {path}")

    def connect_clicked(self):
        if self.proc:
            messagebox.showwarning("Already running", "OpenVPN process already running")
            return

        server = self.server_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not server or not username or not password:
            messagebox.showerror("Missing", "Server, username and password are required")
            return

        # Prepare auth file (two lines: user\\npass\\n)
        self.auth_file = tempfile.NamedTemporaryFile(delete=False)
        self.auth_file.write((username + "\\n" + password + "\\n").encode())
        self.auth_file.flush()
        try:
            os.fchmod(self.auth_file.fileno(), 0o600)
        except Exception:
            pass
        self.auth_file.close()

        # Create minimal ovpn if not loaded
        if self.ovpn_file:
            ovpn_path = self.ovpn_file
            self.append_log(f"Using provided .ovpn: {ovpn_path}")
        else:
            host, sep, port = server.partition(":")
            if not sep:
                port = DEFAULT_PORT
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ovpn", mode="w", encoding="utf-8")
            tmp.write(f"""client
dev tun
proto udp
remote {host} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-128-CBC
auth SHA256
auth-user-pass {self.auth_file.name}
redirect-gateway def1
dhcp-option DNS 1.1.1.1
verb 3
""")
            tmp.flush()
            tmp.close()
            ovpn_path = tmp.name
            self.ovpn_file = ovpn_path
            self.append_log(f"Created temp .ovpn {ovpn_path}")

        openvpn_path = self.ovpn_path_entry.get().strip()
        if not openvpn_path or not os.path.exists(openvpn_path):
            messagebox.showerror("OpenVPN not found", f"OpenVPN binary not found at:\\n{openvpn_path}\\nPlease install OpenVPN or set the correct path.")
            return

        cmd = [openvpn_path, "--config", ovpn_path]
        self.append_log("Starting OpenVPN...")
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception as e:
            self.append_log(f"Failed to start OpenVPN: {e}")
            self.cleanup_temp_files()
            self.proc = None
            return

        self.connect_btn.configure(state="disabled")
        self.disconnect_btn.configure(state="normal")
        t = threading.Thread(target=self._reader_thread, daemon=True)
        t.start()

    def _reader_thread(self):
        assert self.proc
        for line in self.proc.stdout:
            self.append_log(line.rstrip())
        self.append_log("OpenVPN process ended")
        try:
            self.proc.wait(timeout=2)
        except Exception:
            pass
        self.proc = None
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.cleanup_temp_files()

    def disconnect_clicked(self):
        if not self.proc:
            self.append_log("No running OpenVPN process")
            return
        self.append_log("Stopping OpenVPN...")
        try:
            if os.name == "nt":
                # Graceful stop for Windows: try CTRL_BREAK, else terminate
                self.proc.send_signal(signal.CTRL_BREAK_EVENT)
                time.sleep(1.5)
                if self.proc.poll() is None:
                    self.proc.terminate()
            else:
                self.proc.terminate()
        except Exception as e:
            self.append_log(f"Error terminating: {e}")

    def cleanup_temp_files(self):
        try:
            if self.auth_file and os.path.exists(self.auth_file.name):
                os.remove(self.auth_file.name)
                self.append_log("Removed auth file")
        except Exception:
            pass
        try:
            if self.ovpn_file and self.ovpn_file.startswith(tempfile.gettempdir()):
                if os.path.exists(self.ovpn_file):
                    os.remove(self.ovpn_file)
                    self.append_log("Removed temp ovpn")
        except Exception:
            pass

    def on_close(self):
        if self.proc:
            if not messagebox.askyesno("Exit", "OpenVPN is running. Kill and exit?"):
                return
            try:
                if os.name == "nt":
                    self.proc.send_signal(signal.CTRL_BREAK_EVENT)
                    time.sleep(1.0)
                    if self.proc.poll() is None:
                        self.proc.terminate()
                else:
                    self.proc.terminate()
            except Exception:
                pass
        self.destroy()

if __name__ == "__main__":
    app = MiniVPNClient()
    app.mainloop()
