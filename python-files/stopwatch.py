import tkinter as tk
import time

class StopwatchApp:
    def __init__(self, root):
        self.root = root
        root.title("高精度秒錶")
        root.geometry("400x200")
        root.resizable(False, False)
        
        # 狀態變數
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0.0
        
        # 創建時間顯示標籤
        self.time_label = tk.Label(
            root, text="0.00", 
            font=("Arial", 48, "bold"),
            fg="#333333"
        )
        self.time_label.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 創建大按鈕 (佔據右側空間)
        self.button = tk.Button(
            root, text="開始", 
            command=self.toggle_start_stop,
            font=("Arial", 24, "bold"),
            bg="#4CAF50",  # 綠色
            fg="white",
            activebackground="#45a049",
            height=5,
            width=8,
            relief=tk.FLAT
        )
        self.button.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH)
        
        # 綁定Enter鍵
        root.bind('<Return>', lambda event: self.toggle_start_stop())
        
        # 綁定Escape鍵用於退出
        root.bind('<Escape>', lambda event: root.destroy())
        
        # 用於更新時間的變數
        self.last_update = 0

    def toggle_start_stop(self):
        if not self.running:
            self.start()
        else:
            self.stop()
    
    def start(self):
        if not self.running:
            self.running = True
            self.button.config(text="停止", bg="#f44336")  # 紅色
            
            # 記錄開始時間（減去已過時間以實現暫停/繼續功能）
            self.start_time = time.time() - self.elapsed_time
            self.update_time()
    
    def stop(self):
        if self.running:
            self.running = False
            self.button.config(text="開始", bg="#4CAF50")  # 綠色
    
    def reset(self):
        self.running = False
        self.elapsed_time = 0.0
        self.time_label.config(text="0.00")
        self.button.config(text="開始", bg="#4CAF50")
    
    def update_time(self):
        if self.running:
            # 計算經過時間（精確到毫秒）
            self.elapsed_time = time.time() - self.start_time
            
            # 更新顯示（格式：秒.百分秒）
            display_time = "{:.2f}".format(self.elapsed_time)
            self.time_label.config(text=display_time)
            
            # 每10毫秒更新一次（0.01秒精度）
            self.root.after(10, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchApp(root)
    
    # 添加右鍵菜單用於重置
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="重置", command=app.reset)
    
    def show_menu(event):
        menu.post(event.x_root, event.y_root)
    
    root.bind("<Button-3>", show_menu)  # 綁定右鍵菜單
    
    root.mainloop()