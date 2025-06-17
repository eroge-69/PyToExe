#!/usr/bin/env python3
"""
Python SSH Desktop Tool - A PuTTY-like SSH client
Requires: pip install paramiko
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import paramiko
import threading
import time
import json
import os
import socket
from datetime import datetime

class SSHClient:
    def __init__(self):
        self.client = None
        self.shell = None
        self.connected = False
        
    def connect(self, hostname, port, username, password=None, key_file=None, timeout=10):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connection parameters
            connect_params = {
                'hostname': hostname,
                'port': int(port),
                'username': username,
                'timeout': timeout,
                'allow_agent': False,
                'look_for_keys': False
            }
            
            if key_file and os.path.exists(key_file):
                try:
                    # Try different key types
                    key = None
                    for key_class in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
                        try:
                            key = key_class.from_private_key_file(key_file)
                            break
                        except paramiko.PasswordRequiredException:
                            # Key is encrypted, ask for passphrase
                            passphrase = simpledialog.askstring("Key Passphrase", 
                                                               "Enter passphrase for private key:", 
                                                               show='*')
                            if passphrase:
                                key = key_class.from_private_key_file(key_file, password=passphrase)
                                break
                        except Exception:
                            continue
                    
                    if key:
                        connect_params['pkey'] = key
                    else:
                        raise Exception("Could not load private key")
                        
                except Exception as e:
                    raise Exception(f"Private key error: {str(e)}")
            else:
                if password:
                    connect_params['password'] = password
                else:
                    raise Exception("No authentication method provided")
            
            # Connect to SSH server
            self.client.connect(**connect_params)
            
            # Create interactive shell
            self.shell = self.client.invoke_shell(term='xterm', width=80, height=24)
            self.shell.settimeout(0.1)  # Non-blocking reads
            
            self.connected = True
            return True
            
        except paramiko.AuthenticationException:
            raise Exception("Authentication failed. Check username/password or key file.")
        except paramiko.SSHException as e:
            raise Exception(f"SSH connection error: {str(e)}")
        except socket.timeout:
            raise Exception(f"Connection timeout to {hostname}:{port}")
        except socket.gaierror:
            raise Exception(f"Could not resolve hostname: {hostname}")
        except Exception as e:
            raise Exception(f"Connection failed: {str(e)}")
    
    def send_command(self, command):
        if self.shell and self.connected:
            try:
                self.shell.send(command + '\n')
                return True
            except Exception:
                return False
        return False
    
    def receive_data(self):
        if self.shell and self.connected:
            try:
                if self.shell.recv_ready():
                    data = self.shell.recv(4096)
                    return data.decode('utf-8', errors='ignore')
            except Exception:
                pass
        return ""
    
    def disconnect(self):
        self.connected = False
        if self.shell:
            try:
                self.shell.close()
            except:
                pass
        if self.client:
            try:
                self.client.close()
            except:
                pass

class SSHTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Python SSH Tool v1.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.ssh_client = SSHClient()
        self.sessions = {}
        self.receiving_thread = None
        
        self.create_widgets()
        self.load_sessions()
        
    def create_widgets(self):
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Connection tab
        self.create_connection_tab()
        
        # Terminal tab
        self.create_terminal_tab()
        
    def create_connection_tab(self):
        self.conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conn_frame, text="Connection")
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.conn_frame)
        scrollbar = ttk.Scrollbar(self.conn_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Session management
        session_frame = ttk.LabelFrame(scrollable_frame, text="Saved Sessions", padding=10)
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        session_container = ttk.Frame(session_frame)
        session_container.pack(fill=tk.X)
        
        self.session_listbox = tk.Listbox(session_container, height=5)
        self.session_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.session_listbox.bind('<Double-Button-1>', self.load_session)
        
        session_scroll = ttk.Scrollbar(session_container, orient="vertical", command=self.session_listbox.yview)
        session_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_listbox.configure(yscrollcommand=session_scroll.set)
        
        session_buttons = ttk.Frame(session_frame)
        session_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(session_buttons, text="Load", command=self.load_session).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_buttons, text="Save", command=self.save_session).pack(side=tk.LEFT, padx=2)
        ttk.Button(session_buttons, text="Delete", command=self.delete_session).pack(side=tk.LEFT, padx=2)
        
        # Connection settings
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Connection Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Host settings
        host_frame = ttk.Frame(settings_frame)
        host_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(host_frame, text="Host Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.host_entry = ttk.Entry(host_frame, width=25)
        self.host_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(host_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.port_entry = ttk.Entry(host_frame, width=8)
        self.port_entry.grid(row=0, column=3, sticky=tk.W)
        self.port_entry.insert(0, "22")
        
        # Username
        user_frame = ttk.Frame(settings_frame)
        user_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(user_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.username_entry = ttk.Entry(user_frame, width=25)
        self.username_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Authentication
        auth_frame = ttk.LabelFrame(settings_frame, text="Authentication", padding=10)
        auth_frame.pack(fill=tk.X, pady=5)
        
        self.auth_type = tk.StringVar(value="password")
        ttk.Radiobutton(auth_frame, text="Password Authentication", 
                       variable=self.auth_type, value="password", 
                       command=self.toggle_auth).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(auth_frame, text="Private Key Authentication", 
                       variable=self.auth_type, value="key", 
                       command=self.toggle_auth).pack(anchor=tk.W, pady=2)
        
        # Password field
        self.pass_frame = ttk.Frame(auth_frame)
        self.pass_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.pass_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.password_entry = ttk.Entry(self.pass_frame, width=30, show="*")
        self.password_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Key file field
        self.key_frame = ttk.Frame(auth_frame)
        
        ttk.Label(self.key_frame, text="Private Key File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.key_entry = ttk.Entry(self.key_frame, width=30)
        self.key_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Button(self.key_frame, text="Browse...", command=self.browse_key).grid(row=0, column=2)
        
        # Connection options
        options_frame = ttk.LabelFrame(settings_frame, text="Connection Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="Timeout (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.timeout_entry = ttk.Entry(options_frame, width=10)
        self.timeout_entry.grid(row=0, column=1, sticky=tk.W)
        self.timeout_entry.insert(0, "10")
        
        # Connection buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect_ssh)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(button_frame, text="Disconnect", 
                                       command=self.disconnect_ssh, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to connect")
        status_frame = ttk.Frame(button_frame)
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_terminal_tab(self):
        self.term_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.term_frame, text="Terminal", state=tk.DISABLED)
        
        # Terminal output with custom styling
        term_container = ttk.Frame(self.term_frame)
        term_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.terminal_text = scrolledtext.ScrolledText(
            term_container,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 11),
            wrap=tk.WORD,
            insertbackground='white',
            selectbackground='#264f78',
            relief=tk.FLAT,
            bd=2
        )
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        
        # Command input frame
        input_frame = ttk.Frame(self.term_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT)
        
        self.command_entry = ttk.Entry(input_frame, font=('Consolas', 11))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.command_entry.bind('<Return>', self.send_command)
        self.command_entry.bind('<Up>', self.command_history_up)
        self.command_entry.bind('<Down>', self.command_history_down)
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_command)
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Terminal controls
        control_frame = ttk.Frame(self.term_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(control_frame, text="Clear", command=self.clear_terminal).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Copy All", command=self.copy_terminal).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # Connection info
        self.conn_info_var = tk.StringVar(value="Not connected")
        ttk.Label(control_frame, textvariable=self.conn_info_var).pack(side=tk.RIGHT)
        
        # Command history
        self.command_history = []
        self.history_index = -1
        
    def toggle_auth(self):
        if self.auth_type.get() == "password":
            self.pass_frame.pack(fill=tk.X, pady=5)
            self.key_frame.pack_forget()
        else:
            self.key_frame.pack(fill=tk.X, pady=5)
            self.pass_frame.pack_forget()
            
    def browse_key(self):
        filename = filedialog.askopenfilename(
            title="Select Private Key File",
            filetypes=[
                ("SSH Key files", "*.pem *.key *.ppk"),
                ("PEM files", "*.pem"),
                ("Key files", "*.key"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, filename)
    
    def connect_ssh(self):
        hostname = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        timeout = int(self.timeout_entry.get().strip()) if self.timeout_entry.get().strip() else 10
        
        if not hostname:
            messagebox.showerror("Error", "Please enter a hostname")
            return
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        if not port:
            port = "22"
            
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
            
        self.status_var.set("Connecting...")
        self.connect_btn.config(state=tk.DISABLED)
        self.root.update()
        
        def connect_thread():
            try:
                if self.auth_type.get() == "password":
                    password = self.password_entry.get()
                    if not password:
                        raise Exception("Please enter a password")
                    self.ssh_client.connect(hostname, port, username, password=password, timeout=timeout)
                else:
                    key_file = self.key_entry.get().strip()
                    if not key_file:
                        raise Exception("Please select a private key file")
                    if not os.path.exists(key_file):
                        raise Exception("Private key file not found")
                    self.ssh_client.connect(hostname, port, username, key_file=key_file, timeout=timeout)
                
                # Connection successful
                self.root.after(0, self.connection_success, hostname, port, username)
                
            except Exception as e:
                self.root.after(0, self.connection_failed, str(e))
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def connection_success(self, hostname, port, username):
        self.status_var.set("Connected")
        self.conn_info_var.set(f"Connected to {username}@{hostname}:{port}")
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.notebook.tab(1, state=tk.NORMAL)
        self.notebook.select(1)
        
        # Clear terminal and show welcome message
        self.terminal_text.delete(1.0, tk.END)
        welcome_msg = f"Connected to {hostname}:{port} as {username}\n"
        welcome_msg += f"Connection established at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        welcome_msg += "=" * 60 + "\n"
        self.append_to_terminal(welcome_msg)
        
        # Focus on command entry
        self.command_entry.focus_set()
        
        # Start receiving data
        self.start_receiving_data()
        
        # Send initial command to get prompt
        time.sleep(0.5)
        self.ssh_client.send_command("")
    
    def connection_failed(self, error_msg):
        self.status_var.set("Connection failed")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("Connection Error", error_msg)
    
    def disconnect_ssh(self):
        self.ssh_client.disconnect()
        self.status_var.set("Disconnected")
        self.conn_info_var.set("Not connected")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.notebook.tab(1, state=tk.DISABLED)
        self.notebook.select(0)
        
        # Stop receiving thread
        if self.receiving_thread and self.receiving_thread.is_alive():
            self.receiving_thread = None
    
    def start_receiving_data(self):
        def receive_loop():
            while self.ssh_client.connected:
                try:
                    data = self.ssh_client.receive_data()
                    if data:
                        self.root.after(0, lambda d=data: self.append_to_terminal(d))
                    time.sleep(0.05)
                except Exception:
                    break
        
        self.receiving_thread = threading.Thread(target=receive_loop, daemon=True)
        self.receiving_thread.start()
    
    def append_to_terminal(self, text):
        self.terminal_text.insert(tk.END, text)
        self.terminal_text.see(tk.END)
        self.root.update_idletasks()
    
    def send_command(self, event=None):
        command = self.command_entry.get().strip()
        if command and self.ssh_client.connected:
            # Add to history
            if command not in self.command_history:
                self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # Send command
            success = self.ssh_client.send_command(command)
            if success:
                self.command_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to send command. Connection may be lost.")
    
    def command_history_up(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
    
    def command_history_down(self, event):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.command_entry.delete(0, tk.END)
            self.history_index = len(self.command_history)
    
    def clear_terminal(self):
        self.terminal_text.delete(1.0, tk.END)
    
    def copy_terminal(self):
        try:
            content = self.terminal_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Terminal content copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")
    
    def save_log(self):
        try:
            content = self.terminal_text.get(1.0, tk.END)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def save_session(self):
        hostname = self.host_entry.get().strip()
        if not hostname:
            messagebox.showerror("Error", "Please enter a hostname first")
            return
            
        session_name = simpledialog.askstring("Save Session", "Enter session name:", 
                                            initialvalue=f"{self.username_entry.get()}@{hostname}")
        if session_name:
            session_data = {
                'hostname': hostname,
                'port': self.port_entry.get(),
                'username': self.username_entry.get(),
                'auth_type': self.auth_type.get(),
                'key_file': self.key_entry.get() if self.auth_type.get() == 'key' else '',
                'timeout': self.timeout_entry.get()
            }
            self.sessions[session_name] = session_data
            self.update_session_list()
            self.save_sessions_to_file()
            messagebox.showinfo("Success", f"Session '{session_name}' saved")
    
    def load_session(self, event=None):
        selection = self.session_listbox.curselection()
        if selection:
            session_name = self.session_listbox.get(selection[0])
            session_data = self.sessions[session_name]
            
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, session_data['hostname'])
            
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, session_data['port'])
            
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, session_data['username'])
            
            self.timeout_entry.delete(0, tk.END)
            self.timeout_entry.insert(0, session_data.get('timeout', '10'))
            
            self.auth_type.set(session_data['auth_type'])
            self.toggle_auth()
            
            if session_data['auth_type'] == 'key':
                self.key_entry.delete(0, tk.END)
                self.key_entry.insert(0, session_data['key_file'])
    
    def delete_session(self):
        selection = self.session_listbox.curselection()
        if selection:
            session_name = self.session_listbox.get(selection[0])
            if messagebox.askyesno("Confirm Delete", f"Delete session '{session_name}'?"):
                del self.sessions[session_name]
                self.update_session_list()
                self.save_sessions_to_file()
    
    def update_session_list(self):
        self.session_listbox.delete(0, tk.END)
        for session_name in sorted(self.sessions.keys()):
            self.session_listbox.insert(tk.END, session_name)
    
    def save_sessions_to_file(self):
        try:
            with open('ssh_sessions.json', 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def load_sessions(self):
        try:
            if os.path.exists('ssh_sessions.json'):
                with open('ssh_sessions.json', 'r') as f:
                    self.sessions = json.load(f)
                self.update_session_list()
        except Exception as e:
            print(f"Error loading sessions: {e}")

def main():
    root = tk.Tk()
    app = SSHTool(root)
    
    def on_closing():
        if app.ssh_client.connected:
            app.ssh_client.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (900 // 2)
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"900x700+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()