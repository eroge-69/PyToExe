#!/usr/bin/env python3
"""
Bin File Merger Tool
合併兩個 bin 檔案的工具

功能:
1. 選擇 BOOT 檔案
2. 選擇 APP 檔案  
3. 選擇輸出檔案位置
4. 從 0x0000 開始填寫 BOOT 檔案
5. 從 0x8000 開始填寫 APP 檔案
6. 在 0x3F800 位置填寫 4 bytes: 0xAA 0x55 0xAA 0x55
7. 生成合併後的 bin 檔案
8. 輸出檔案大小為 260100 bytes
9. 未使用的 bytes 填入 0xFF
10. 記憶上次選擇的檔案路徑
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import json

class BinMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bin 檔案合併工具 v2.0")
        self.root.geometry("650x450")
        self.root.resizable(True, True)
        
        # 設定檔案路徑
        self.config_file = "bin_merger_config.json"
        
        # 檔案路徑變數
        self.boot_file_path = tk.StringVar()
        self.app_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        
        # 載入上次的設定
        self.load_config()
        
        self.setup_ui()
        
        # 註冊關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config(self):
        """載入上次的設定"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.boot_file_path.set(config.get('boot_file', ''))
                    self.app_file_path.set(config.get('app_file', ''))
                    self.output_file_path.set(config.get('output_file', ''))
        except Exception as e:
            print(f"載入設定檔失敗: {e}")
            
    def save_config(self):
        """儲存當前設定"""
        try:
            config = {
                'boot_file': self.boot_file_path.get(),
                'app_file': self.app_file_path.get(),
                'output_file': self.output_file_path.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定檔失敗: {e}")
            
    def on_closing(self):
        """程式關閉時的處理"""
        self.save_config()
        self.root.destroy()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="Bin 檔案合併工具 v2.0", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # BOOT 檔案選擇
        ttk.Label(main_frame, text="BOOT 檔案:").grid(row=1, column=0, sticky=tk.W, pady=5)
        boot_entry = ttk.Entry(main_frame, textvariable=self.boot_file_path, width=60)
        boot_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="瀏覽", 
                  command=self.select_boot_file).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # APP 檔案選擇
        ttk.Label(main_frame, text="APP 檔案:").grid(row=2, column=0, sticky=tk.W, pady=5)
        app_entry = ttk.Entry(main_frame, textvariable=self.app_file_path, width=60)
        app_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="瀏覽", 
                  command=self.select_app_file).grid(row=2, column=2, padx=(5, 0), pady=5)
        
        # 輸出檔案選擇
        ttk.Label(main_frame, text="輸出檔案:").grid(row=3, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file_path, width=60)
        output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="瀏覽", 
                  command=self.select_output_file).grid(row=3, column=2, padx=(5, 0), pady=5)
        
        # 分隔線
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # 合併設定說明
        settings_frame = ttk.LabelFrame(main_frame, text="合併設定 (v2.0)", padding="10")
        settings_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(0, weight=1)
        
        ttk.Label(settings_frame, text=" BOOT 檔案從 0x0000 開始").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(settings_frame, text=" APP 檔案從 0x8000 開始").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(settings_frame, text=" 在 0x3F800 位置填入: 0xAA 0x55 0xAA 0x55").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(settings_frame, text=" 輸出檔案大小: 260100 bytes (0x3F804)", 
                 foreground="blue").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(settings_frame, text=" 未使用區域填入: 0xFF", 
                 foreground="blue").grid(row=4, column=0, sticky=tk.W)
        ttk.Label(settings_frame, text=" 自動記憶上次選擇的檔案路徑", 
                 foreground="green").grid(row=5, column=0, sticky=tk.W)
        
        # 操作按鈕
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="開始合併", 
                  command=self.merge_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="關於", 
                  command=self.show_about).pack(side=tk.LEFT, padx=5)
        
        # 進度條
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 狀態標籤
        self.status_label = ttk.Label(main_frame, text="準備就緒 - 已載入上次設定")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
    def select_boot_file(self):
        initial_dir = os.path.dirname(self.boot_file_path.get()) if self.boot_file_path.get() else ""
        filename = filedialog.askopenfilename(
            title="選擇 BOOT 檔案",
            initialdir=initial_dir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.boot_file_path.set(filename)
            
    def select_app_file(self):
        initial_dir = os.path.dirname(self.app_file_path.get()) if self.app_file_path.get() else ""
        filename = filedialog.askopenfilename(
            title="選擇 APP 檔案",
            initialdir=initial_dir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.app_file_path.set(filename)
            
    def select_output_file(self):
        initial_dir = os.path.dirname(self.output_file_path.get()) if self.output_file_path.get() else ""
        filename = filedialog.asksaveasfilename(
            title="選擇輸出檔案位置",
            initialdir=initial_dir,
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_path.set(filename)
            
    def clear_fields(self):
        self.boot_file_path.set("")
        self.app_file_path.set("")
        self.output_file_path.set("")
        self.progress['value'] = 0
        self.status_label.config(text="準備就緒")
        
    def show_about(self):
        about_text = """Bin 檔案合併工具 v2.0

新功能:
 輸出檔案大小: 260100 bytes (0x3F864)
 未使用區域填入 0xFF
 自動記憶檔案路徑

原有功能:
 合併兩個 bin 檔案
 BOOT 檔案從 0x0000 開始
 APP 檔案從 0x8000 開始  
 在 0x3F800 位置填入標識碼

作者: AI Assistant
版本: 2.0
"""
        messagebox.showinfo("關於", about_text)
        
    def merge_files(self):
        # 檢查檔案路徑
        if not self.boot_file_path.get():
            messagebox.showerror("錯誤", "請選擇 BOOT 檔案")
            return
            
        if not self.app_file_path.get():
            messagebox.showerror("錯誤", "請選擇 APP 檔案")
            return
            
        if not self.output_file_path.get():
            messagebox.showerror("錯誤", "請選擇輸出檔案位置")
            return
            
        # 檢查檔案是否存在
        if not os.path.exists(self.boot_file_path.get()):
            messagebox.showerror("錯誤", "BOOT 檔案不存在")
            return
            
        if not os.path.exists(self.app_file_path.get()):
            messagebox.showerror("錯誤", "APP 檔案不存在")
            return
            
        try:
            self.status_label.config(text="開始合併...")
            self.progress['value'] = 10
            self.root.update()
            
            # 創建輸出緩衝區 (260100 bytes = 0x3F864)
            output_size = 260100  # 新的檔案大小
            output_buffer = bytearray([0xFF] * output_size)  # 使用 0xFF 填充
            
            self.progress['value'] = 20
            self.root.update()
            
            # 讀取 BOOT 檔案並寫入 0x0000
            self.status_label.config(text="處理 BOOT 檔案...")
            with open(self.boot_file_path.get(), 'rb') as f:
                boot_data = f.read()
                
            if len(boot_data) > 0x8000:
                messagebox.showerror("錯誤", f"BOOT 檔案太大 ({len(boot_data)} bytes)，最大允許 32KB")
                return
                
            # 將 BOOT 數據寫入從 0x0000 開始
            output_buffer[0:len(boot_data)] = boot_data
            
            self.progress['value'] = 40
            self.root.update()
            
            # 讀取 APP 檔案並寫入 0x8000
            self.status_label.config(text="處理 APP 檔案...")
            with open(self.app_file_path.get(), 'rb') as f:
                app_data = f.read()
                
            app_start = 0x8000
            app_max_size = 0x3F800 - app_start  # 到標識碼位置之前
            
            if len(app_data) > app_max_size:
                messagebox.showerror("錯誤", f"APP 檔案太大 ({len(app_data)} bytes)，最大允許 {app_max_size} bytes")
                return
                
            # 將 APP 數據寫入從 0x8000 開始
            output_buffer[app_start:app_start + len(app_data)] = app_data
            
            self.progress['value'] = 60
            self.root.update()
            
            # 在 0x3F800 位置寫入標識碼
            self.status_label.config(text="寫入標識碼...")
            marker_position = 0x3F800
            marker_bytes = [0xAA, 0x55, 0xAA, 0x55]
            output_buffer[marker_position:marker_position + 4] = marker_bytes
            
            self.progress['value'] = 80
            self.root.update()
            
            # 寫入輸出檔案
            self.status_label.config(text="寫入輸出檔案...")
            with open(self.output_file_path.get(), 'wb') as f:
                f.write(output_buffer)
                
            self.progress['value'] = 100
            self.status_label.config(text="合併完成！")
            
            # 自動儲存設定
            self.save_config()
            
            # 顯示成功訊息
            success_msg = f"""合併完成！

檔案資訊:
 BOOT 檔案大小: {len(boot_data)} bytes (0x{len(boot_data):X})
 APP 檔案大小: {len(app_data)} bytes (0x{len(app_data):X})
 輸出檔案大小: {len(output_buffer)} bytes (0x{len(output_buffer):X})
 輸出檔案位置: {self.output_file_path.get()}

合併配置:
 BOOT: 0x0000 - 0x{len(boot_data)-1:X}
 APP: 0x8000 - 0x{0x8000 + len(app_data)-1:X}
 標識碼: 0x3F800 (AA 55 AA 55)
 未使用區域: 填入 0xFF
 檔案路徑已自動儲存"""

            messagebox.showinfo("成功", success_msg)
            
        except Exception as e:
            self.progress['value'] = 0
            self.status_label.config(text="合併失敗")
            messagebox.showerror("錯誤", f"合併過程中發生錯誤:\n{str(e)}")

def main():
    root = tk.Tk()
    app = BinMergerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
