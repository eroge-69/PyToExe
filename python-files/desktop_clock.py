import tkinter as tk
from tkinter import ttk, colorchooser, font, messagebox
import time
import datetime
import threading
import winsound
import json
import os
from math import pi, cos, sin

class DesktopClock:
    def __init__(self, root):
        self.root = root
        self.root.title("多功能桌面时钟")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        
        # 加载设置
        self.settings = {
            "font_family": "Arial",
            "font_size": 24,
            "text_color": "#000000",
            "bg_color": "#FFFFFF",
            "clock_type": "digital",
            "always_on_top": False,
            "locked": False,
            "alarm_time": "",
            "alarm_active": False
        }
        self.load_settings()
        
        # 创建菜单
        self.create_menu()
        
        # 创建主界面
        self.create_main_frame()
        
        # 创建设置对话框
        self.settings_dialog = None
        
        # 创建闹钟对话框
        self.alarm_dialog = None
        
        # 创建倒计时对话框
        self.countdown_dialog = None
        self.countdown_active = False
        self.countdown_end_time = None
        self.countdown_mode = "seconds"
        
        # 创建日期推算对话框
        self.date_calc_dialog = None
        
        # 更新时钟
        self.update_clock()
        
        # 设置窗口属性
        self.update_window_properties()
        
        # 检查闹钟
        self.check_alarm()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="设置", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 功能菜单
        feature_menu = tk.Menu(menubar, tearoff=0)
        feature_menu.add_command(label="闹钟", command=self.open_alarm)
        feature_menu.add_command(label="倒计时", command=self.open_countdown)
        feature_menu.add_command(label="日期推算", command=self.open_date_calculator)
        menubar.add_cascade(label="功能", menu=feature_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_frame(self):
        # 主框架
        self.main_frame = tk.Frame(self.root, bg=self.settings["bg_color"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 时钟显示区域
        self.clock_label = tk.Label(
            self.main_frame, 
            text="", 
            font=(self.settings["font_family"], self.settings["font_size"]), 
            fg=self.settings["text_color"], 
            bg=self.settings["bg_color"]
        )
        self.clock_label.pack(expand=True)
        
        # 如果是模拟时钟，使用Canvas
        self.clock_canvas = None
        if self.settings["clock_type"] != "digital":
            self.create_analog_clock()
    
    def create_analog_clock(self):
        if self.clock_canvas:
            self.clock_canvas.destroy()
            
        size = min(self.main_frame.winfo_width(), self.main_frame.winfo_height()) - 20
        if size < 100:
            size = 300  # 默认大小
            
        self.clock_canvas = tk.Canvas(
            self.main_frame, 
            width=size, 
            height=size, 
            bg=self.settings["bg_color"], 
            highlightthickness=0
        )
        self.clock_canvas.pack(expand=True)
        
        # 绘制时钟
        self.draw_analog_clock()
    
    def draw_analog_clock(self):
        if not self.clock_canvas:
            return
            
        canvas = self.clock_canvas
        canvas.delete("all")
        
        size = min(canvas.winfo_width(), canvas.winfo_height())
        center = size // 2
        radius = size // 2 - 10
        
        # 绘制时钟外框
        canvas.create_oval(
            center - radius, center - radius, 
            center + radius, center + radius, 
            outline=self.settings["text_color"], 
            width=2
        )
        
        # 获取当前时间
        now = datetime.datetime.now()
        hour, minute, second = now.hour, now.minute, now.second
        
        # 绘制时钟刻度
        for i in range(60):
            angle = pi / 30 * i
            length = radius - 15 if i % 5 == 0 else radius - 8
            x1 = center + (radius - length) * sin(angle)
            y1 = center - (radius - length) * cos(angle)
            x2 = center + radius * sin(angle)
            y2 = center - radius * cos(angle)
            width = 3 if i % 5 == 0 else 1
            canvas.create_line(x1, y1, x2, y2, fill=self.settings["text_color"], width=width)
        
        # 绘制时针
        hour_angle = pi / 6 * hour + pi / 360 * minute
        hour_length = radius * 0.5
        x_hour = center + hour_length * sin(hour_angle)
        y_hour = center - hour_length * cos(hour_angle)
        canvas.create_line(center, center, x_hour, y_hour, fill=self.settings["text_color"], width=4)
        
        # 绘制分针
        minute_angle = pi / 30 * minute
        minute_length = radius * 0.7
        x_minute = center + minute_length * sin(minute_angle)
        y_minute = center - minute_length * cos(minute_angle)
        canvas.create_line(center, center, x_minute, y_minute, fill=self.settings["text_color"], width=3)
        
        # 绘制秒针
        second_angle = pi / 30 * second
        second_length = radius * 0.9
        x_second = center + second_length * sin(second_angle)
        y_second = center - second_length * cos(second_angle)
        canvas.create_line(center, center, x_second, y_second, fill="red", width=1)
        
        # 中心点
        canvas.create_oval(center - 5, center - 5, center + 5, center + 5, fill=self.settings["text_color"])
    
    def update_clock(self):
        now = datetime.datetime.now()
        
        if self.settings["clock_type"] == "digital":
            # 数字时钟
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")
            
            if hasattr(self, 'show_date') and self.show_date:
                display_text = f"{time_str}\n{date_str}"
            else:
                display_text = time_str
                
            self.clock_label.config(text=display_text)
        else:
            # 模拟时钟
            self.draw_analog_clock()
        
        # 检查倒计时
        if self.countdown_active and self.countdown_end_time:
            remaining = self.countdown_end_time - datetime.datetime.now()
            if remaining.total_seconds() <= 0:
                self.countdown_active = False
                self.play_alarm_sound()
                messagebox.showinfo("倒计时结束", "倒计时已结束！")
            else:
                self.update_countdown_display(remaining)
        
        # 每100毫秒更新一次（模拟时钟需要更频繁的更新）
        self.root.after(100, self.update_clock)
    
    def update_countdown_display(self, remaining):
        if self.settings["clock_type"] == "digital":
            total_seconds = remaining.total_seconds()
            
            if self.countdown_mode == "seconds":
                text = f"倒计时: {int(total_seconds)}秒"
            elif self.countdown_mode == "minutes":
                minutes = total_seconds // 60
                text = f"倒计时: {int(minutes)}分钟"
            elif self.countdown_mode == "hours":
                hours = total_seconds // 3600
                text = f"倒计时: {int(hours)}小时"
            elif self.countdown_mode == "days":
                days = total_seconds // 86400
                text = f"倒计时: {int(days)}天"
            elif self.countdown_mode == "months":
                months = total_seconds // (86400 * 30)
                text = f"倒计时: {int(months)}月"
            elif self.countdown_mode == "years":
                years = total_seconds // (86400 * 365)
                text = f"倒计时: {int(years)}年"
            
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text=text)
            else:
                self.countdown_label = tk.Label(
                    self.main_frame, 
                    text=text, 
                    font=(self.settings["font_family"], self.settings["font_size"] // 2), 
                    fg=self.settings["text_color"], 
                    bg=self.settings["bg_color"]
                )
                self.countdown_label.pack()
    
    def update_window_properties(self):
        # 置顶窗口
        self.root.attributes('-topmost', self.settings["always_on_top"])
        
        # 锁定窗口（禁用调整大小）
        if self.settings["locked"]:
            self.root.resizable(False, False)
        else:
            self.root.resizable(True, True)
    
    def open_settings(self):
        if self.settings_dialog:
            self.settings_dialog.lift()
            return
            
        self.settings_dialog = tk.Toplevel(self.root)
        self.settings_dialog.title("时钟设置")
        self.settings_dialog.geometry("400x500")
        
        # 字体设置
        font_frame = tk.LabelFrame(self.settings_dialog, text="字体设置")
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(font_frame, text="字体:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        font_family = ttk.Combobox(font_frame, values=list(font.families()), state="readonly")
        font_family.set(self.settings["font_family"])
        font_family.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(font_frame, text="大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        font_size = tk.Spinbox(font_frame, from_=8, to=72, width=5)
        font_size.delete(0, tk.END)
        font_size.insert(0, str(self.settings["font_size"]))
        font_size.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 颜色设置
        color_frame = tk.LabelFrame(self.settings_dialog, text="颜色设置")
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(color_frame, text="文字颜色:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        text_color_btn = tk.Button(
            color_frame, 
            bg=self.settings["text_color"], 
            command=lambda: self.choose_color("text_color", text_color_btn)
        )
        text_color_btn.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        tk.Label(color_frame, text="背景颜色:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        bg_color_btn = tk.Button(
            color_frame, 
            bg=self.settings["bg_color"], 
            command=lambda: self.choose_color("bg_color", bg_color_btn)
        )
        bg_color_btn.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时钟类型
        clock_frame = tk.LabelFrame(self.settings_dialog, text="时钟类型")
        clock_frame.pack(fill=tk.X, padx=10, pady=5)
        
        clock_type = tk.StringVar(value=self.settings["clock_type"])
        tk.Radiobutton(clock_frame, text="数字时钟", variable=clock_type, value="digital").grid(row=0, column=0, sticky=tk.W)
        tk.Radiobutton(clock_frame, text="模拟时钟", variable=clock_type, value="analog").grid(row=1, column=0, sticky=tk.W)
        
        # 窗口属性
        window_frame = tk.LabelFrame(self.settings_dialog, text="窗口属性")
        window_frame.pack(fill=tk.X, padx=10, pady=5)
        
        always_on_top = tk.BooleanVar(value=self.settings["always_on_top"])
        tk.Checkbutton(window_frame, text="窗口置顶", variable=always_on_top).grid(row=0, column=0, sticky=tk.W)
        
        locked = tk.BooleanVar(value=self.settings["locked"])
        tk.Checkbutton(window_frame, text="锁定窗口(禁止调整大小)", variable=locked).grid(row=1, column=0, sticky=tk.W)
        
        # 保存按钮
        def save_settings():
            self.settings["font_family"] = font_family.get()
            self.settings["font_size"] = int(font_size.get())
            self.settings["clock_type"] = clock_type.get()
            self.settings["always_on_top"] = always_on_top.get()
            self.settings["locked"] = locked.get()
            
            # 更新字体和颜色
            self.clock_label.config(
                font=(self.settings["font_family"], self.settings["font_size"]),
                fg=self.settings["text_color"],
                bg=self.settings["bg_color"]
            )
            
            # 更新主框架背景
            self.main_frame.config(bg=self.settings["bg_color"])
            
            # 如果是模拟时钟，重新创建
            if self.settings["clock_type"] != "digital":
                self.create_analog_clock()
            
            # 更新窗口属性
            self.update_window_properties()
            
            # 保存设置到文件
            self.save_settings()
            
            self.settings_dialog.destroy()
            self.settings_dialog = None
        
        save_btn = tk.Button(self.settings_dialog, text="保存", command=save_settings)
        save_btn.pack(pady=10)
        
        self.settings_dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(self, 'settings_dialog', None))
    
    def choose_color(self, key, button):
        color = colorchooser.askcolor(title=f"选择{key}")[1]
        if color:
            self.settings[key] = color
            button.config(bg=color)
            self.clock_label.config(fg=self.settings["text_color"], bg=self.settings["bg_color"])
            if self.clock_canvas:
                self.clock_canvas.config(bg=self.settings["bg_color"])
                self.main_frame.config(bg=self.settings["bg_color"])
    
    def open_alarm(self):
        if self.alarm_dialog:
            self.alarm_dialog.lift()
            return
            
        self.alarm_dialog = tk.Toplevel(self.root)
        self.alarm_dialog.title("闹钟设置")
        self.alarm_dialog.geometry("300x200")
        
        # 闹钟时间
        tk.Label(self.alarm_dialog, text="闹钟时间 (HH:MM):").pack(pady=5)
        alarm_time = tk.Entry(self.alarm_dialog)
        alarm_time.insert(0, self.settings["alarm_time"])
        alarm_time.pack(pady=5)
        
        # 激活开关
        alarm_active = tk.BooleanVar(value=self.settings["alarm_active"])
        tk.Checkbutton(self.alarm_dialog, text="激活闹钟", variable=alarm_active).pack(pady=5)
        
        # 保存按钮
        def save_alarm():
            self.settings["alarm_time"] = alarm_time.get()
            self.settings["alarm_active"] = alarm_active.get()
            self.save_settings()
            self.alarm_dialog.destroy()
            self.alarm_dialog = None
        
        save_btn = tk.Button(self.alarm_dialog, text="保存", command=save_alarm)
        save_btn.pack(pady=10)
        
        self.alarm_dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(self, 'alarm_dialog', None))
    
    def check_alarm(self):
        if self.settings["alarm_active"] and self.settings["alarm_time"]:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            
            if current_time == self.settings["alarm_time"]:
                self.play_alarm_sound()
                messagebox.showinfo("闹钟", "时间到了！")
                # 禁用闹钟，避免重复提醒
                self.settings["alarm_active"] = False
                self.save_settings()
        
        # 每分钟检查一次
        self.root.after(60000, self.check_alarm)
    
    def play_alarm_sound(self):
        try:
            # 播放声音（Windows）
            for _ in range(3):
                winsound.Beep(1000, 500)
                time.sleep(0.5)
        except:
            # 如果beep不可用，使用系统声音
            try:
                import winsound
                winsound.MessageBeep()
            except:
                pass
    
    def open_countdown(self):
        if self.countdown_dialog:
            self.countdown_dialog.lift()
            return
            
        self.countdown_dialog = tk.Toplevel(self.root)
        self.countdown_dialog.title("倒计时设置")
        self.countdown_dialog.geometry("300x300")
        
        # 时间设置
        tk.Label(self.countdown_dialog, text="倒计时时间:").pack(pady=5)
        
        time_frame = tk.Frame(self.countdown_dialog)
        time_frame.pack(pady=5)
        
        tk.Label(time_frame, text="小时:").grid(row=0, column=0)
        hours = tk.Spinbox(time_frame, from_=0, to=23, width=5)
        hours.grid(row=0, column=1)
        
        tk.Label(time_frame, text="分钟:").grid(row=0, column=2)
        minutes = tk.Spinbox(time_frame, from_=0, to=59, width=5)
        minutes.grid(row=0, column=3)
        
        tk.Label(time_frame, text="秒:").grid(row=0, column=4)
        seconds = tk.Spinbox(time_frame, from_=0, to=59, width=5)
        seconds.grid(row=0, column=5)
        
        # 模式选择
        tk.Label(self.countdown_dialog, text="显示模式:").pack(pady=5)
        mode = tk.StringVar(value="seconds")
        modes = [("秒", "seconds"), ("分钟", "minutes"), ("小时", "hours"), 
                 ("天", "days"), ("月", "months"), ("年", "years")]
        
        for i, (text, val) in enumerate(modes):
            tk.Radiobutton(self.countdown_dialog, text=text, variable=mode, value=val).pack(anchor=tk.W)
        
        # 开始按钮
        def start_countdown():
            h = int(hours.get())
            m = int(minutes.get())
            s = int(seconds.get())
            
            total_seconds = h * 3600 + m * 60 + s
            if total_seconds <= 0:
                messagebox.showwarning("警告", "请设置有效的倒计时时间")
                return
                
            self.countdown_mode = mode.get()
            self.countdown_end_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
            self.countdown_active = True
            
            # 如果有倒计时标签，先删除
            if hasattr(self, 'countdown_label'):
                self.countdown_label.destroy()
                delattr(self, 'countdown_label')
            
            self.countdown_dialog.destroy()
            self.countdown_dialog = None
        
        start_btn = tk.Button(self.countdown_dialog, text="开始倒计时", command=start_countdown)
        start_btn.pack(pady=10)
        
        # 停止按钮
        def stop_countdown():
            self.countdown_active = False
            self.countdown_end_time = None
            if hasattr(self, 'countdown_label'):
                self.countdown_label.destroy()
                delattr(self, 'countdown_label')
            self.countdown_dialog.destroy()
            self.countdown_dialog = None
        
        stop_btn = tk.Button(self.countdown_dialog, text="停止倒计时", command=stop_countdown)
        stop_btn.pack(pady=5)
        
        self.countdown_dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(self, 'countdown_dialog', None))
    
    def open_date_calculator(self):
        if self.date_calc_dialog:
            self.date_calc_dialog.lift()
            return
            
        self.date_calc_dialog = tk.Toplevel(self.root)
        self.date_calc_dialog.title("日期推算")
        self.date_calc_dialog.geometry("400x300")
        
        # 开始日期
        tk.Label(self.date_calc_dialog, text="开始日期:").pack(pady=5)
        start_date = tk.Entry(self.date_calc_dialog)
        start_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        start_date.pack(pady=5)
        
        # 操作类型
        tk.Label(self.date_calc_dialog, text="操作:").pack(pady=5)
        operation = tk.StringVar(value="add")
        tk.Radiobutton(self.date_calc_dialog, text="增加天数", variable=operation, value="add").pack(anchor=tk.W)
        tk.Radiobutton(self.date_calc_dialog, text="减少天数", variable=operation, value="subtract").pack(anchor=tk.W)
        
        # 天数
        tk.Label(self.date_calc_dialog, text="天数:").pack(pady=5)
        days = tk.Spinbox(self.date_calc_dialog, from_=0, to=9999, width=5)
        days.pack(pady=5)
        
        # 结果
        result_frame = tk.Frame(self.date_calc_dialog)
        result_frame.pack(pady=10)
        
        tk.Label(result_frame, text="结果日期:").grid(row=0, column=0)
        result_label = tk.Label(result_frame, text="", relief=tk.SUNKEN, width=20)
        result_label.grid(row=0, column=1)
        
        # 计算按钮
        def calculate():
            try:
                date_obj = datetime.datetime.strptime(start_date.get(), "%Y-%m-%d").date()
                day_count = int(days.get())
                
                if operation.get() == "add":
                    new_date = date_obj + datetime.timedelta(days=day_count)
                else:
                    new_date = date_obj - datetime.timedelta(days=day_count)
                
                result_label.config(text=new_date.strftime("%Y-%m-%d"))
            except ValueError:
                messagebox.showwarning("警告", "请输入有效的日期格式 (YYYY-MM-DD)")
        
        calc_btn = tk.Button(self.date_calc_dialog, text="计算", command=calculate)
        calc_btn.pack(pady=5)
        
        self.date_calc_dialog.protocol("WM_DELETE_WINDOW", lambda: setattr(self, 'date_calc_dialog', None))
    
    def load_settings(self):
        if os.path.exists("clock_settings.json"):
            try:
                with open("clock_settings.json", "r") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except:
                pass
    
    def save_settings(self):
        try:
            with open("clock_settings.json", "w") as f:
                json.dump(self.settings, f)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopClock(root)
    root.mainloop()