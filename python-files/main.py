import tkinter as tk
from tkinter import ttk
import webbrowser
import threading
import random
import time
import pyttsx3
import ctypes
import os
import math
import winsound
import sys

# 标题、消息、网址，用于随机效果
titles = [
    "你废了 - 系统崩溃警告",
    "你完了.exe - 严重错误",
    "警告！病毒已启动 by wdxbd_520_qwq",
    "🐛 系统异常！你废了.exe",
    "你被 wd 入侵了？！",
    "致命错误 - 系统即将崩溃",
    "病毒活动警报 - 你废了.exe"
]

websites = [
    "https://www.bilibili.com/",
    "https://www.baidu.com/",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://cn.bing.com/search?q=电脑被黑了怎么办",
    "https://zh.wikipedia.org/wiki/计算机病毒",
    "https://www.taobao.com/",
    "https://www.jd.com/"
]

messages = [
    "系统遭到破坏，10 秒内将启动自毁程序。",
    "错误代码：0xFAKE_VIRUS，作者：wdxbd_520_qwq",
    "你完了！你的数据已上传到火星",
    "CPU 已被熔毁，正在降温处理……",
    "警告：你废了.exe 正在运行中",
    "检测到关键系统文件损坏！",
    "硬盘扇区正在被擦除...",
    "内存溢出！系统资源耗尽"
]

# 系统音效
def play_sound_effects():
    try:
        # 播放系统警告音
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        time.sleep(1)
        # 播放错误音
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
    except:
        # 如果音效不可用，使用蜂鸣器
        for i in range(3):
            winsound.Beep(800, 200)
            time.sleep(0.1)

# 中文语音提示
def speak_chinese():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    for voice in engine.getProperty('voices'):
        if 'zh' in voice.id or 'chinese' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say("警告！你的电脑已被我控制！别担心，这只是个玩笑~")
    engine.runAndWait()

# 打开彩蛋网页
def open_webs():
    for site in random.sample(websites, 3):
        webbrowser.open(site)
        time.sleep(1)

# 弹窗提示
def spam_message_boxes(count=5):
    for i in range(count):
        title = random.choice(titles)
        msg = random.choice(messages)
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0)

# 控制台刷屏"日志"
def terminal_fake_warnings():
    for _ in range(30):
        print(random.choice([
            "[警告] 系统错误：代码 0x0000dead",
            "[病毒] 已感染：你废了.exe",
            "[提示] 正在连接控制服务器...",
            "[INFO] Uploading data to 127.0.0.1:6666",
            "[错误] 无法访问系统注册表",
            "[严重] 防火墙已被绕过",
            "[警报] 检测到键盘记录器活动",
            "[崩溃] 核心进程意外终止"
        ]))
        time.sleep(0.15)

# 屏幕闪烁（Windows 控制台窗口闪烁）
def flicker_screen():
    try:
        for _ in range(15):
            ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
            time.sleep(0.08)
    except:
        pass

# 假蓝屏窗口（模拟系统崩溃）
def fake_bluescreen():
    top = tk.Toplevel()
    top.attributes('-fullscreen', True)
    top.configure(bg='blue')
    
    # 添加蓝屏表情
    emoji_label = tk.Label(top, text="☹️", font=("Arial", 72), fg="white", bg="blue")
    emoji_label.pack(pady=20)
    
    msg = tk.Label(top, text="你的电脑遇到问题，需要重启。\n\n错误代码：FAKE_VIRUS_WDXBD520\n\n请稍后，我们正在收集错误信息", 
                  font=("微软雅黑", 24), fg="white", bg="blue")
    msg.pack(pady=10)
    
    # 添加进度条
    progress = ttk.Progressbar(top, mode='determinate', length=600)
    progress.pack(pady=20)
    progress.start(10)
    
    # 添加二维码彩蛋
    qr_label = tk.Label(top, text="扫描二维码获取帮助\n⬇️⬇️⬇️", font=("微软雅黑", 14), fg="white", bg="blue")
    qr_label.pack(pady=10)
    
    # 伪二维码（实际是ASCII艺术）
    qr_code = tk.Label(top, text="█████████████████\n█ 假 二 维 码 █\n█████████████████", 
                      font=("Courier New", 12), fg="white", bg="blue")
    qr_code.pack()
    
    top.after(6000, top.destroy)

# 小病毒窗口"跳舞"
def dancing_window():
    top = tk.Toplevel()
    top.geometry("200x80+100+100")
    top.title("你抓不到我~")
    top.overrideredirect(True)  # 移除窗口边框
    
    # 使用表情符号作为内容
    emojis = ["🦠", "💻", "🔥", "💣", "☠️", "👾", "🐛", "🤖", "👻", "🤯"]
    label = tk.Label(top, text=random.choice(emojis), font=("Arial", 36), bg="black", fg="green")
    label.pack(expand=True, fill=tk.BOTH)
    
    # 添加关闭按钮
    close_btn = tk.Button(top, text="X", command=top.destroy, 
                         font=("Arial", 8), bg="red", fg="white", bd=0)
    close_btn.place(x=180, y=0, width=20, height=20)

    def move():
        try:
            for _ in range(50):
                x = random.randint(0, ctypes.windll.user32.GetSystemMetrics(0)-200)
                y = random.randint(0, ctypes.windll.user32.GetSystemMetrics(1)-80)
                top.geometry(f"200x80+{x}+{y}")
                
                # 改变表情
                label.config(text=random.choice(emojis))
                
                time.sleep(0.25)
        finally:
            top.destroy()

    threading.Thread(target=move, daemon=True).start()

# 创建矩阵数字雨效果
def matrix_rain():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg='black')
    
    # 创建Canvas用于绘制
    canvas = tk.Canvas(root, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # 获取屏幕尺寸
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    
    # 初始化雨滴
    font_size = 16
    columns = width // font_size
    drops = [1] * columns
    
    # 添加标题
    title = canvas.create_text(width//2, height//4, text="系统被黑客入侵", 
                             fill="#00ff00", font=('微软雅黑', 36))
    
    def draw():
        canvas.delete("matrix")
        
        for i in range(columns):
            # 随机字符
            text = chr(random.randint(0x30A0, 0x30FF))
            
            # 绘制字符
            x = i * font_size
            y = drops[i] * font_size
            
            canvas.create_text(x, y, text=text, fill="#00ff00", font=('Arial', font_size), tags="matrix")
            
            # 重置雨滴位置
            if y > height and random.random() > 0.975:
                drops[i] = 0
            
            # 增加雨滴位置
            drops[i] += 1
        
        root.after(30, draw)
    
    draw()
    
    # 设置10秒后自动关闭
    root.after(10000, root.destroy)
    root.mainloop()

# 创建粒子系统效果
def particle_effect():
    root = tk.Tk()
    root.title("系统恢复中...")
    root.attributes("-fullscreen", True)
    
    canvas = tk.Canvas(root, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # 创建粒子
    particles = []
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    for _ in range(300):
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        size = random.randint(1, 4)
        speed = random.uniform(0.5, 3)
        color = random.choice(colors)
        particles.append([x, y, size, speed, color])
    
    def update_particles():
        canvas.delete("particles")
        
        # 添加恢复进度文本
        canvas.create_text(root.winfo_screenwidth()//2, root.winfo_screenheight()//3, 
                          text="系统恢复中...", fill="white", font=("微软雅黑", 36), tags="text")
        
        for p in particles:
            x, y, size, speed, color = p
            canvas.create_oval(x, y, x+size, y+size, fill=color, outline=color, tags="particles")
            
            # 更新位置
            p[1] += speed
            
            # 如果粒子超出屏幕，重置到顶部
            if p[1] > root.winfo_screenheight():
                p[1] = 0
                p[0] = random.randint(0, root.winfo_screenwidth())
        
        root.after(20, update_particles)
    
    update_particles()
    
    # 设置进度条
    progress = ttk.Progressbar(root, mode='determinate', length=root.winfo_screenwidth()//2)
    progress.place(x=root.winfo_screenwidth()//4, y=root.winfo_screenheight()*2//3)
    progress.start(10)
    
    # 添加进度百分比
    percent_label = tk.Label(root, text="0%", font=("微软雅黑", 24), fg="white", bg="black")
    percent_label.place(x=root.winfo_screenwidth()//2 - 30, y=root.winfo_screenheight()*2//3 + 50)
    
    # 更新百分比
    def update_percent(p=0):
        if p <= 100:
            percent_label.config(text=f"{p}%")
            root.after(50, update_percent, p+1)
    
    update_percent()
    
    # 设置8秒后自动关闭
    root.after(8000, root.destroy)
    root.mainloop()

# 文件删除动画
def fake_file_deletion():
    root = tk.Tk()
    root.title("文件删除中...")
    root.geometry("600x400")
    root.configure(bg='black')
    
    # 创建文件列表
    file_list = [
        "重要文件.docx",
        "家庭照片.jpg",
        "财务数据.xlsx",
        "个人简历.pdf",
        "项目备份.zip",
        "系统配置.ini",
        "密码.txt"
    ]
    
    # 随机选择要"删除"的文件
    selected_files = random.sample(file_list, 5)
    
    listbox = tk.Listbox(root, bg='black', fg='red', font=("Courier New", 14), 
                        selectbackground='red', selectforeground='black')
    listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 添加文件到列表
    for file in selected_files:
        listbox.insert(tk.END, f"[ ] {file}")
    
    # 删除动画
    def delete_files():
        for i in range(len(selected_files)):
            time.sleep(0.5)
            listbox.delete(i)
            listbox.insert(i, f"[✓] {selected_files[i]} 已删除")
            listbox.itemconfig(i, {'fg': '#888888'})
            root.update()
        
        # 添加完成消息
        time.sleep(1)
        listbox.insert(tk.END, "")
        listbox.insert(tk.END, "删除完成！已删除 5 个文件")
        listbox.itemconfig(len(selected_files)+1, {'fg': 'red'})
        
        root.after(3000, root.destroy)
    
    threading.Thread(target=delete_files, daemon=True).start()
    root.mainloop()

# 系统扫描动画
def system_scan():
    root = tk.Tk()
    root.title("系统扫描中...")
    root.geometry("600x400")
    
    # 创建扫描界面
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 扫描标题
    title = tk.Label(frame, text="正在扫描系统威胁", font=("微软雅黑", 18))
    title.pack(pady=10)
    
    # 扫描进度
    progress = ttk.Progressbar(frame, mode='determinate', length=500)
    progress.pack(pady=10)
    
    # 扫描结果列表
    scan_list = tk.Listbox(frame, height=15, font=("微软雅黑", 10))
    scan_list.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 威胁数据
    threats = [
        ("Trojan.Win32.FakeVirus", "高", "你废了.exe"),
        ("HackTool.Win32.PrankScript", "中", "prank.py"),
        ("PUP.Optional.FakeAV", "低", "fake_antivirus.exe"),
        ("Exploit.Script.FakeError", "严重", "error_generator.js")
    ]
    
    # 更新扫描进度
    def update_scan():
        for i in range(101):
            progress['value'] = i
            root.update()
            time.sleep(0.05)
            
            # 在特定进度添加威胁
            if i == 25:
                scan_list.insert(tk.END, "检测到威胁: Trojan.Win32.FakeVirus (高)")
            elif i == 50:
                scan_list.insert(tk.END, "检测到威胁: HackTool.Win32.PrankScript (中)")
            elif i == 70:
                scan_list.insert(tk.END, "检测到威胁: PUP.Optional.FakeAV (低)")
            elif i == 90:
                scan_list.insert(tk.END, "检测到威胁: Exploit.Script.FakeError (严重)")
        
        scan_list.insert(tk.END, "扫描完成! 检测到 4 个威胁")
        scan_list.itemconfig(4, {'fg': 'red'})
        
        root.after(3000, root.destroy)
    
    threading.Thread(target=update_scan, daemon=True).start()
    root.mainloop()

# 主窗口
def show_fake_virus():
    root = tk.Tk()
    root.title(random.choice(titles))
    root.geometry("600x400")
    root.resizable(False, False)
    
    # 添加图标
    try:
        root.iconbitmap("virus_icon.ico")
    except:
        pass

    # 创建动态背景
    bg_canvas = tk.Canvas(root, width=600, height=400, bg='black')
    bg_canvas.pack(fill=tk.BOTH, expand=True)
    
    # 绘制动态背景 - 科技感网格
    grid_lines = []
    for i in range(0, 600, 25):
        line = bg_canvas.create_line(i, 0, i, 400, fill="#113311", width=1, tags="grid")
        grid_lines.append(line)
    for i in range(0, 400, 25):
        line = bg_canvas.create_line(0, i, 600, i, fill="#113311", width=1, tags="grid")
        grid_lines.append(line)
    
    # 动态点
    dots = []
    for _ in range(50):
        x = random.randint(0, 600)
        y = random.randint(0, 400)
        dot = bg_canvas.create_oval(x, y, x+3, y+3, fill="#00ff00", outline="", tags="dot")
        dots.append(dot)
    
    # 动画函数
    def animate_background():
        # 移动点
        for dot in dots:
            coords = bg_canvas.coords(dot)
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            bg_canvas.move(dot, dx, dy)
            
            # 确保点在画布内
            x0, y0, x1, y1 = bg_canvas.coords(dot)
            if x0 < 0 or x1 > 600:
                bg_canvas.move(dot, -dx, 0)
            if y0 < 0 or y1 > 400:
                bg_canvas.move(dot, 0, -dy)
        
        # 改变网格颜色
        for line in grid_lines:
            color = "#" + format(random.randint(10, 30), '02x') + format(random.randint(40, 80), '02x') + format(random.randint(10, 30), '02x')
            bg_canvas.itemconfig(line, fill=color)
        
        root.after(100, animate_background)
    
    animate_background()

    # 主警告标签
    label = tk.Label(root, text=random.choice(messages), font=("微软雅黑", 16), 
                    fg="red", bg="#000000", wraplength=500)
    label.place(x=300, y=80, anchor=tk.CENTER)
    
    # 添加倒计时标签
    countdown_label = tk.Label(root, text="自毁倒计时: 10 秒", font=("微软雅黑", 14), 
                             fg="yellow", bg="#000000")
    countdown_label.place(x=300, y=120, anchor=tk.CENTER)
    
    # 更新倒计时
    def update_countdown(count=10):
        if count > 0:
            countdown_label.config(text=f"自毁倒计时: {count} 秒")
            root.after(1000, update_countdown, count-1)
        else:
            countdown_label.config(text="自毁已取消！")
    
    # 进度条
    progress = ttk.Progressbar(root, mode='indeterminate', length=400)
    progress.place(x=100, y=160, width=400)
    progress.start(8)
    
    # 状态图标
    status_frame = tk.Frame(root, bg="#000000")
    status_frame.place(x=300, y=220, anchor=tk.CENTER)
    
    status_icons = [
        ("CPU", "🔥", "red"),
        ("内存", "💾", "orange"),
        ("磁盘", "💽", "yellow"),
        ("网络", "📡", "green"),
        ("安全", "🛡️", "cyan")
    ]
    
    for i, (name, icon, color) in enumerate(status_icons):
        frame = tk.Frame(status_frame, bg="#000000")
        frame.grid(row=0, column=i, padx=10)
        
        icon_label = tk.Label(frame, text=icon, font=("Arial", 24), bg="#000000", fg=color)
        icon_label.pack()
        
        name_label = tk.Label(frame, text=name, font=("微软雅黑", 10), bg="#000000", fg="white")
        name_label.pack()
    
    # 添加一个关闭按钮（彩蛋）
    close_btn = tk.Button(root, text="点此停止病毒", command=root.destroy, 
                         font=("微软雅黑", 12), bg="#004400", fg="#00ff00", 
                         activebackground="#006600", activeforeground="#00ff00",
                         relief=tk.RAISED, bd=3)
    close_btn.place(x=250, y=280, width=100, height=40)

    # 作者信息
    credit = tk.Label(root, text="病毒模拟器 v2.0 - 作者：wdxbd_520_qwq", 
                     font=("微软雅黑", 9), fg="#888888", bg="#000000")
    credit.place(x=300, y=380, anchor=tk.CENTER)
    
    # 子线程运行特效
    threading.Thread(target=play_sound_effects, daemon=True).start()
    threading.Thread(target=open_webs, daemon=True).start()
    threading.Thread(target=speak_chinese, daemon=True).start()
    threading.Thread(target=flicker_screen, daemon=True).start()
    threading.Thread(target=lambda: spam_message_boxes(4), daemon=True).start()
    threading.Thread(target=terminal_fake_warnings, daemon=True).start()
    
    # 启动倒计时
    update_countdown()

    # 定时恶搞特效
    root.after(3000, fake_file_deletion)
    root.after(6000, system_scan)
    root.after(9000, fake_bluescreen)
    root.after(12000, dancing_window)
    root.after(15000, dancing_window)
    root.after(18000, matrix_rain)
    root.after(25000, particle_effect)

    # 标题每 2 秒切换
    def change_title():
        while True:
            time.sleep(2)
            root.title(random.choice(titles))

    threading.Thread(target=change_title, daemon=True).start()

    root.mainloop()

# 最后提示"整蛊完成"
def final_message():
    # 播放完成音效
    try:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    except:
        winsound.Beep(1000, 300)
    
    # 创建感谢窗口
    thanks = tk.Tk()
    thanks.title("整蛊完成")
    thanks.geometry("500x300")
    thanks.configure(bg='#000033')
    
    # 创建画布背景
    canvas = tk.Canvas(thanks, bg='#000033', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # 添加星星背景
    stars = []
    for _ in range(100):
        x = random.randint(0, 500)
        y = random.randint(0, 300)
        size = random.randint(1, 3)
        star = canvas.create_oval(x, y, x+size, y+size, fill="white", outline="")
        stars.append(star)
    
    # 动画星星
    def twinkle_stars():
        for star in stars:
            if random.random() > 0.7:
                canvas.itemconfig(star, fill=random.choice(["white", "#ffff00", "#00ffff"]))
        thanks.after(500, twinkle_stars)
    
    twinkle_stars()
    
    # 添加主消息
    msg = tk.Label(thanks, text="整蛊完成！", font=("微软雅黑", 24), 
                  fg="#ffff00", bg="#000033")
    msg.place(x=250, y=80, anchor=tk.CENTER)
    
    # 添加说明
    info = tk.Label(thanks, text="你的电脑安全无恙\n这只是一个无害的玩笑程序\n\n感谢你的体验！", 
                   font=("微软雅黑", 14), fg="white", bg="#000033", justify=tk.CENTER)
    info.place(x=250, y=150, anchor=tk.CENTER)
    
    # 添加按钮
    def close_all():
        thanks.destroy()
        # 尝试关闭所有Tkinter窗口
        for window in tk._default_root.tk.call('winfo', 'children', '.'):
            if window.startswith('.'):
                tk._default_root.tk.call('destroy', window)
    
    btn = tk.Button(thanks, text="确定", command=close_all, 
                   font=("微软雅黑", 14), bg="#004400", fg="#00ff00", 
                   width=15, height=2, relief=tk.RAISED, bd=3)
    btn.place(x=250, y=250, anchor=tk.CENTER)
    
    # 添加作者信息
    author = tk.Label(thanks, text="制作: wdxbd_520_qwq", 
                     font=("微软雅黑", 10), fg="#8888ff", bg="#000033")
    author.place(x=250, y=290, anchor=tk.CENTER)
    
    thanks.mainloop()

# 启动主程序
if __name__ == "__main__":
    show_fake_virus()
    final_message()