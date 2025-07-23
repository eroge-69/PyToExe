import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import time
import json
import os
import base64
from PIL import Image, ImageTk
import io
import mss
import struct

class TeacherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MCEEA教師端廣播系統")
        self.root.geometry("800x600")
        
        # 網路設定
        self.broadcast_port = 12345
        self.file_port = 12346
        self.command_port = 12347
        self.clients = []
        self.is_broadcasting = False
        self.broadcast_thread = None
        self.server_socket = None
        
        self.setup_ui()
        self.start_discovery_server()
        
    def setup_ui(self):
        # 主要框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 連接狀態
        status_frame = ttk.LabelFrame(main_frame, text="連接狀態", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.client_listbox = tk.Listbox(status_frame, height=6)
        self.client_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.client_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.client_listbox.yview)
        
        # 廣播控制
        broadcast_frame = ttk.LabelFrame(main_frame, text="螢幕廣播", padding="5")
        broadcast_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 10))
        
        self.broadcast_btn = ttk.Button(broadcast_frame, text="開始廣播", command=self.toggle_broadcast)
        self.broadcast_btn.grid(row=0, column=0, pady=5)
        
        self.broadcast_status = ttk.Label(broadcast_frame, text="狀態: 未廣播")
        self.broadcast_status.grid(row=1, column=0, pady=5)
        
        # 檔案傳輸
        file_frame = ttk.LabelFrame(main_frame, text="檔案傳輸", padding="5")
        file_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 10))
        
        ttk.Button(file_frame, text="選擇檔案", command=self.select_file).grid(row=0, column=0, pady=5)
        self.file_label = ttk.Label(file_frame, text="未選擇檔案")
        self.file_label.grid(row=1, column=0, pady=5)
        
        ttk.Button(file_frame, text="傳送檔案", command=self.send_file).grid(row=2, column=0, pady=5)
        
        # 系統控制
        control_frame = ttk.LabelFrame(main_frame, text="系統控制", padding="5")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="關閉所有學生端", command=self.shutdown_all, 
                  style='Accent.TButton').grid(row=0, column=0, pady=5, padx=5)
        
        ttk.Button(control_frame, text="黑屏", command=self.black_screen).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(control_frame, text="解除黑屏", command=self.unblack_screen).grid(row=0, column=2, pady=5, padx=5)
        
        # 設定網格權重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
        self.selected_file = None
        
    def start_discovery_server(self):
        """啟動學生端發現服務"""
        def discovery_server():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', 12348))
                
                while True:
                    data, addr = sock.recvfrom(1024)
                    if data == b'STUDENT_DISCOVERY':
                        # 回應學生端
                        response = json.dumps({
                            'type': 'teacher_response',
                            'teacher_ip': self.get_local_ip()
                        })
                        sock.sendto(response.encode(), addr)
                        
                        # 添加到客戶端列表
                        client_info = f"{addr[0]}:{addr[1]}"
                        if client_info not in self.clients:
                            self.clients.append(client_info)
                            self.root.after(0, self.update_client_list)
                            
            except Exception as e:
                print(f"Discovery server error: {e}")
        
        threading.Thread(target=discovery_server, daemon=True).start()
        
    def get_local_ip(self):
        """獲取本機IP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
            
    def update_client_list(self):
        """更新客戶端列表顯示"""
        self.client_listbox.delete(0, tk.END)
        for client in self.clients:
            self.client_listbox.insert(tk.END, f"學生端: {client}")
            
    def toggle_broadcast(self):
        """切換廣播狀態"""
        if self.is_broadcasting:
            self.stop_broadcast()
        else:
            self.start_broadcast()
            
    def start_broadcast(self):
        """開始螢幕廣播"""
        if self.is_broadcasting:
            return
            
        self.is_broadcasting = True
        self.broadcast_btn.config(text="停止廣播")
        self.broadcast_status.config(text="狀態: 廣播中...")
        
        def broadcast_screen():
            with mss.mss() as sct:
                while self.is_broadcasting:
                    try:
                        # 截取螢幕
                        screenshot = sct.grab(sct.monitors[1])
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        
                        # 壓縮圖片
                        img = img.resize((800, 600), Image.Resampling.LANCZOS)
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=30)
                        img_data = buffer.getvalue()
                        
                        # 廣播給所有學生端
                        self.broadcast_data('screen', base64.b64encode(img_data).decode())
                        
                        time.sleep(0.1)  # 10 FPS
                        
                    except Exception as e:
                        print(f"Broadcast error: {e}")
                        break
                        
        self.broadcast_thread = threading.Thread(target=broadcast_screen, daemon=True)
        self.broadcast_thread.start()
        
    def stop_broadcast(self):
        """停止螢幕廣播"""
        self.is_broadcasting = False
        self.broadcast_btn.config(text="開始廣播")
        self.broadcast_status.config(text="狀態: 未廣播")
        
    def broadcast_data(self, data_type, data):
        """廣播數據給所有學生端"""
        message = json.dumps({
            'type': data_type,
            'data': data
        })
        
        # UDP廣播
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode(), ('<broadcast>', self.broadcast_port))
            sock.close()
        except Exception as e:
            print(f"Broadcast error: {e}")
            
    def select_file(self):
        """選擇要傳輸的檔案"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"已選擇: {filename}")
            
    def send_file(self):
        """傳送檔案給所有學生端"""
        if not self.selected_file:
            messagebox.showwarning("警告", "請先選擇檔案")
            return
            
        try:
            with open(self.selected_file, 'rb') as f:
                file_data = f.read()
                
            filename = os.path.basename(self.selected_file)
            file_info = {
                'filename': filename,
                'data': base64.b64encode(file_data).decode()
            }
            
            self.broadcast_data('file', file_info)
            messagebox.showinfo("成功", f"檔案 {filename} 已傳送")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"檔案傳送失敗: {e}")
            
    def shutdown_all(self):
        """關閉所有學生端"""
        result = messagebox.askyesno("確認", "確定要關閉所有學生端電腦嗎？")
        if result:
            self.broadcast_data('command', 'shutdown')
            messagebox.showinfo("完成", "關機指令已發送")
            
    def black_screen(self):
        """學生端黑屏"""
        self.broadcast_data('command', 'black_screen')
        
    def unblack_screen(self):
        """解除學生端黑屏"""
        self.broadcast_data('command', 'unblack_screen')
        
    def run(self):
        """運行程序"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """程序關閉時的清理工作"""
        self.is_broadcasting = False
        self.root.destroy()

if __name__ == "__main__":
    app = TeacherApp()
    app.run()