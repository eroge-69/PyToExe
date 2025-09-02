import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk
import pyautogui
import io
import base64
import zlib

class RemoteDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Desktop")
        self.root.geometry("800x600")
        
        self.is_server = False
        self.client_socket = None
        self.server_socket = None
        self.connection_active = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connection section
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W)
        self.ip_entry = ttk.Entry(conn_frame, width=20)
        self.ip_entry.grid(row=0, column=1, padx=5)
        self.ip_entry.insert(0, "127.0.0.1")
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, padx=(20, 0))
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.grid(row=0, column=3, padx=5)
        self.port_entry.insert(0, "12345")
        
        # Buttons
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.start_server_btn = ttk.Button(btn_frame, text="Start Server", 
                                         command=self.start_server)
        self.start_server_btn.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="Connect", 
                                    command=self.connect_to_server)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", 
                                       command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Remote screen display
        screen_frame = ttk.LabelFrame(main_frame, text="Remote Screen", padding="10")
        screen_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.screen_label = ttk.Label(screen_frame, text="Not connected", 
                                    background="black", foreground="white")
        self.screen_label.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        screen_frame.columnconfigure(0, weight=1)
        screen_frame.rowconfigure(0, weight=1)
    
    def start_server(self):
        try:
            port = int(self.port_entry.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            
            self.is_server = True
            self.status_var.set(f"Server started on port {port}. Waiting for connection...")
            
            # Start accepting connections in a separate thread
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            self.start_server_btn.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def accept_connections(self):
        try:
            self.client_socket, addr = self.server_socket.accept()
            self.connection_active = True
            self.status_var.set(f"Connected to {addr[0]}:{addr[1]}")
            
            # Start screen sharing
            threading.Thread(target=self.send_screen, daemon=True).start()
            
        except Exception as e:
            self.status_var.set(f"Connection error: {str(e)}")
    
    def connect_to_server(self):
        try:
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.connection_active = True
            
            self.status_var.set(f"Connected to {ip}:{port}")
            
            # Start receiving screen
            threading.Thread(target=self.receive_screen, daemon=True).start()
            
            self.start_server_btn.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def send_screen(self):
        try:
            while self.connection_active:
                # Capture screen
                screenshot = pyautogui.screenshot()
                
                # Compress image
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format='JPEG', quality=50)
                compressed_data = zlib.compress(img_bytes.getvalue())
                
                # Send data
                data_len = len(compressed_data)
                self.client_socket.sendall(data_len.to_bytes(4, 'big'))
                self.client_socket.sendall(compressed_data)
                
                # Throttle sending rate
                threading.Event().wait(0.1)
                
        except Exception as e:
            self.status_var.set(f"Send error: {str(e)}")
            self.disconnect()
    
    def receive_screen(self):
        try:
            while self.connection_active:
                # Receive data length
                data_len_bytes = self.client_socket.recv(4)
                if not data_len_bytes:
                    break
                
                data_len = int.from_bytes(data_len_bytes, 'big')
                
                # Receive compressed data
                received_data = b''
                while len(received_data) < data_len:
                    chunk = self.client_socket.recv(min(4096, data_len - len(received_data)))
                    if not chunk:
                        break
                    received_data += chunk
                
                if len(received_data) != data_len:
                    break
                
                # Decompress and display
                try:
                    decompressed_data = zlib.decompress(received_data)
                    image = Image.open(io.BytesIO(decompressed_data))
                    
                    # Resize for display
                    display_width = 600
                    display_height = 400
                    image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_screen, photo)
                    
                except Exception as e:
                    print(f"Image processing error: {e}")
                    
        except Exception as e:
            self.status_var.set(f"Receive error: {str(e)}")
            self.disconnect()
    
    def update_screen(self, photo):
        self.screen_label.configure(image=photo)
        self.screen_label.image = photo
    
    def disconnect(self):
        self.connection_active = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.status_var.set("Disconnected")
        self.screen_label.configure(image='', text="Not connected")
        
        self.start_server_btn.config(state=tk.NORMAL)
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = RemoteDesktopApp(root)
    
    # Handle window close
    def on_closing():
        app.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()