import socket
import threading
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode, b64encode
import netifaces

class FileTransfer:
    def __init__(self, file_port=5001):
        self.file_port = file_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.file_port))
        self.sock.listen(5)
        threading.Thread(target=self.listen, daemon=True).start()
    
    def listen(self):
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self.handle_transfer, args=(client,), daemon=True).start()
    
    def handle_transfer(self, client):
        try:
            # Receive encrypted header
            data = client.recv(1024)
            key = b64decode(self.key)
            cipher = AES.new(key, AES.MODE_CBC, iv=data[:16])
            header = json.loads(unpad(cipher.decrypt(data[16:]), AES.block_size).decode())
            
            filename = header['filename']
            filesize = header['size']
            
            # Receive file
            with open(filename, 'wb') as f:
                received = 0
                while received < filesize:
                    chunk = client.recv(4096)
                    if not chunk: break
                    f.write(chunk)
                    received += len(chunk)
                    self.update_progress(received, filesize)
            
            self.app.add_message(f"Received: {filename}", "system")
        except Exception as e:
            print(f"Transfer error: {e}")
        finally:
            client.close()
    
    def send_file(self, ip, filename):
        try:
            filesize = os.path.getsize(filename)
            key = b64decode(self.key)
            iv = os.urandom(16)
            
            # Encrypt header
            header = json.dumps({
                'filename': os.path.basename(filename),
                'size': filesize
            }).encode()
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            enc_header = iv + cipher.encrypt(pad(header, AES.block_size))
            
            # Connect and send header
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.file_port))
                s.send(enc_header)
                
                # Send file
                with open(filename, 'rb') as f:
                    while chunk := f.read(4096):
                        s.send(chunk)
                        self.update_progress(f.tell(), filesize)
            
            self.app.add_message(f"Sent: {os.path.basename(filename)}", "system")
        except Exception as e:
            messagebox.showerror("Transfer Error", str(e))
    
    def update_progress(self, current, total):
        if self.app and hasattr(self.app, 'progress'):
            self.app.progress['value'] = (current / total) * 100
            self.app.root.update_idletasks()

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("LAN Chat & File Transfer")
        self.root.geometry("800x600")
        
        # Login frame
        self.login_frame = ttk.Frame(root)
        ttk.Label(self.login_frame, text="Server IP:").grid(row=0, column=0, padx=5, pady=5)
        self.server_ip = ttk.Entry(self.login_frame, width=15)
        self.server_ip.insert(0, self.get_default_server())
        self.server_ip.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        self.username = ttk.Entry(self.login_frame, width=20)
        self.username.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="Encryption Key:").grid(row=2, column=0, padx=5, pady=5)
        self.enc_key = ttk.Entry(self.login_frame, width=40)
        self.enc_key.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.login_frame, text="Connect", command=self.connect).grid(
            row=3, column=0, columnspan=2, pady=10
        )
        self.login_frame.pack(pady=50)
    
    def get_default_server(self):
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if '192.168' in addr['addr']:
                        return addr['addr'].rsplit('.', 1)[0] + '.1'  # Common gateway
        return ""
    
    def connect(self):
        if not self.username.get() or not self.enc_key.get():
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            self.key = self.enc_key.get()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip.get(), 5000))
            
            # Get encryption key from server
            server_key = b64decode(self.sock.recv(1024))
            if server_key != b64decode(self.key):
                raise ValueError("Key mismatch")
            
            # Register
            reg_data = json.dumps({
                'username': self.username.get(),
                'file_port': 5001
            }).encode()
            self.sock.send(reg_data)
            
            # Start listeners
            self.file_transfer = FileTransfer()
            self.file_transfer.key = self.key
            self.file_transfer.app = self
            
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.setup_main_ui()
            
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def setup_main_ui(self):
        self.login_frame.destroy()
        
        # Main layout
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (users/groups)
        left_panel = ttk.Frame(self.main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        ttk.Label(left_panel, text="Online Users:").pack(anchor=tk.W)
        self.user_list = tk.Listbox(left_panel, height=15)
        self.user_list.pack(fill=tk.X, pady=5)
        
        ttk.Button(left_panel, text="New Group", command=self.create_group).pack(fill=tk.X, pady=2)
        
        # Chat area
        chat_frame = ttk.Frame(self.main_frame)
        chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.chat_area = tk.Text(chat_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        self.msg_entry = ttk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", self.send_message)
        
        ttk.Button(input_frame, text="Send", command=self.send_message).pack(side=tk.RIGHT)
        ttk.Button(input_frame, text="Send File", command=self.send_file).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(chat_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
    
    def create_group(self):
        group_name = tk.simpledialog.askstring("New Group", "Group Name:")
        if group_name:
            self.sock.send(json.dumps({
                'type': 'CREATE_GROUP',
                'group': group_name
            }).encode())
    
    def send_message(self, event=None):
        content = self.msg_entry.get().strip()
        if content:
            self.add_message(f"You: {content}", "user")
            self.sock.send(json.dumps({
                'type': 'MSG',
                'to': self.selected_user,
                'content': content,
                'is_group': isinstance(self.selected_user, tuple)
            }).encode())
            self.msg_entry.delete(0, tk.END)
    
    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if hasattr(self, 'selected_user') and self.selected_user:
                target = self.selected_user[0] if isinstance(self.selected_user, tuple) else self.selected_user
                user_data = next((u for u in self.clients if u[0] == target), None)
                if user_
                    threading.Thread(
                        target=self.file_transfer.send_file,
                        args=(user_data[1], file_path),
                        daemon=True
                    ).start()
    
    def add_message(self, message, msg_type):
        self.chat_area.config(state=tk.NORMAL)
        if msg_type == "user":
            self.chat_area.insert(tk.END, message + "\n", "user")
        elif msg_type == "system":
            self.chat_area.insert(tk.END, f"[SYSTEM] {message}\n", "system")
        else:
            self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.tag_config("user", foreground="blue")
        self.chat_area.tag_config("system", foreground="green")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not  break
                
                # Decrypt message
                key = b64decode(self.key)
                nonce = data[:16]
                cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
                msg = json.loads(cipher.decrypt(data[16:]).decode())
                
                if msg['type'] == 'USERS':
                    self.clients = msg['users']  # [(username, ip), ...]
                    self.update_user_list()
                
                elif msg['type'] == 'MSG':
                    sender = msg['from']
                    content = msg['content']
                    self.add_message(f"{sender}: {content}", "received")
                
                elif msg['type'] == 'USER_LEFT':
                    self.update_user_list()
            
            except Exception as e:
                print(f"Receive error: {e}")
                break
    
    def update_user_list(self):
        self.user_list.delete(0, tk.END)
        for user in self.clients:
            self.user_list.insert(tk.END, user[0])
        self.user_list.bind('<<ListboxSelect>>', self.on_user_select)
    
    def on_user_select(self, event):
        selection = self.user_list.curselection()
        if selection:
            idx = selection[0]
            self.selected_user = self.clients[idx][0]

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()