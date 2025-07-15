import os
import time
import random
import sys
import webbrowser
from tkinter import Tk, Label, Button, Entry, messagebox, Toplevel, ttk, PhotoImage

def show_fake_install():
    root = Tk()
    root.title("RoPro Premium 安裝程式 v3.1.4")
    root.geometry("650x550")
    
    try:
        logo = PhotoImage(file="ropro_logo.png")
        Label(root, image=logo).pack(pady=10)
    except:
        Label(root, text="RoPro Premium", font=('Arial', 16, 'bold'), fg='#4285F4').pack(pady=10)
    
    Label(root, text="解鎖 Roblox 高級功能", font=('Arial', 12)).pack(pady=5)
    
    # 安裝選項
    options_frame = ttk.LabelFrame(root, text="安裝選項")
    options_frame.pack(pady=10, padx=20, fill="x")
    
    ttk.Checkbutton(options_frame, text="安裝 RoPro 瀏覽器擴展 (必選)").pack(anchor="w", pady=5, padx=10)
    ttk.Checkbutton(options_frame, text="啟用自動腳本更新").pack(anchor="w", pady=5, padx=10)
    ttk.Checkbutton(options_frame, text="安裝 FPS 提升模組").pack(anchor="w", pady=5, padx=10)
    
    # 安裝進度
    progress = ttk.Progressbar(root, orient="horizontal", length=450, mode="determinate")
    progress.pack(pady=20)
    
    status_label = Label(root, text="準備安裝 RoPro Premium...", font=('Arial', 10))
    status_label.pack(pady=5)
    
    # 安裝按鈕
    def start_installation():
        install_button.config(state="disabled")
        
        # 第一階段安裝 (0-50%)
        for i in range(1, 51):
            progress['value'] = i
            root.update_idletasks()
            
            if i % 5 == 0:
                messages = [
                    "正在下載 RoPro 核心文件...",
                    "驗證 Roblox 安裝路徑...",
                    "準備注入腳本引擎...",
                    "檢查系統相容性...",
                    "初始化高級功能模組..."
                ]
                status_label.config(text=random.choice(messages))
            
            time.sleep(0.03)
        
        # 暫停安裝，要求解鎖碼
        root.destroy()
        ask_for_key()
    
    install_button = Button(root, text="開始安裝 RoPro Premium", command=start_installation, 
                          bg='#4285F4', fg='white', font=('Arial', 12))
    install_button.pack(pady=15)
    
    # 官方連結
    def open_website():
        webbrowser.open("https://ropro.io")
    
    Label(root, text="官方網站: https://ropro.io", font=('Arial', 9), fg='blue', cursor="hand2").pack(pady=5)
    root.mainloop()

def ask_for_key():
    key_win = Tk()
    key_win.title("RoPro Premium 驗證")
    key_win.geometry("500x350")
    
    Label(key_win, text="🔒 RoPro Premium 解鎖", font=('Arial', 14, 'bold')).pack(pady=15)
    Label(key_win, text="需要驗證您的解鎖碼以繼續安裝", font=('Arial', 11)).pack(pady=10)
    
    Label(key_win, text="請輸入您購買獲得的解鎖碼:", font=('Arial', 10)).pack(pady=5)
    
    key_entry = Entry(key_win, font=('Arial', 12), justify='center')
    key_entry.pack(pady=10)
    
    Label(key_win, text="沒有解鎖碼？前往官方商店購買", font=('Arial', 9), fg='blue', cursor="hand2").pack(pady=5)
    
    def verify_key():
        key = key_entry.get()
        if len(key) < 8:
            messagebox.showerror("錯誤", "解鎖碼格式不正確！")
            return
        
        key_win.destroy()
        continue_installation(key)
    
    Button(key_win, text="驗證並繼續安裝", command=verify_key, bg='#34A853', fg='white').pack(pady=15)
    key_win.mainloop()

def continue_installation(key):
    install_win = Tk()
    install_win.title("RoPro Premium 安裝中...")
    install_win.geometry("600x400")
    
    Label(install_win, text="正在完成 RoPro Premium 安裝", font=('Arial', 14)).pack(pady=20)
    
    progress = ttk.Progressbar(install_win, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=10)
    
    status_label = Label(install_win, text="正在驗證解鎖碼...", font=('Arial', 10))
    status_label.pack(pady=5)
    
    # 假裝在驗證解鎖碼
    def do_installation():
        progress['value'] = 50
        install_win.update()
        time.sleep(1.5)
        
        # 假裝驗證成功
        status_label.config(text="解鎖碼驗證成功！")
        progress['value'] = 60
        install_win.update()
        time.sleep(1)
        
        # 繼續安裝進度
        for i in range(61, 101):
            progress['value'] = i
            install_win.update_idletasks()
            
            if i % 5 == 0:
                messages = [
                    "正在注入高級腳本...",
                    "配置自動更新服務...",
                    "安裝反檢測模組...",
                    "解鎖獨家遊戲功能...",
                    "優化 Roblox 內存使用..."
                ]
                status_label.config(text=random.choice(messages))
            
            time.sleep(0.05)
        
        time.sleep(1)
        install_win.destroy()
        show_final_error()
    
    install_win.after(1000, do_installation)
    install_win.mainloop()

def show_final_error():
    error_win = Tk()
    error_win.title("RoPro 安全警報")
    error_win.geometry("550x400")
    
    Label(error_win, text="⚠️ 嚴重安全警告 ⚠️", font=('Arial', 16, 'bold'), fg='red').pack(pady=15)
    Label(error_win, text="偵測到您的 Roblox 帳號憑證可能已外洩", font=('Arial', 12)).pack(pady=10)
    
    ttk.Separator(error_win, orient='horizontal').pack(fill='x', padx=50, pady=10)
    
    Label(error_win, text="錯誤代碼: RPX_SECURITY_ALERT_0x7E3F", font=('Arial', 10)).pack(pady=5)
    Label(error_win, text="可能原因:", font=('Arial', 11, 'bold')).pack(pady=5)
    Label(error_win, text="• 使用了未授權的 RoPro 版本\n• 解鎖碼來源不可信\n• 系統存在安全漏洞", 
          font=('Arial', 10), justify='left').pack(pady=5)
    
    def show_solution():
        messagebox.showwarning("立即行動", 
            "為保護您的帳號安全，請立即:\n\n"
            "1. 變更 Roblox 密碼\n"
            "2. 啟用兩步驟驗證\n"
            "3. 從官方商店重新安裝 RoPro\n\n"
            "官方網站: https://ropro.io")
    
    Button(error_win, text="如何解決？", command=show_solution, bg='#EA4335', fg='white').pack(pady=20)
    error_win.mainloop()

if __name__ == "__main__":
    # 假裝需要管理員權限
    if os.name == 'nt':
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
                sys.exit()
        except:
            pass
    
    show_fake_install()