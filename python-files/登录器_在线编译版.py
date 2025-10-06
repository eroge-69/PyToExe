#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化登录器 - 简化版（适合在线编译）
3:2比例布局，左侧海报，右侧功能区域
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import re
import webbrowser
from urllib.request import urlopen
import io
import base64

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ModernLoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_data()
        self.setup_styles()
        self.create_main_layout()
        self.current_view = "login"
        self.verification_code = ""
        self.user_email = ""
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("登录器")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(bg='#1e3c72')
        
        # 居中显示
        self.center_window()
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def setup_data(self):
        """设置数据文件"""
        self.data_file = "user_data.json"
        self.load_users()
        
    def load_users(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except:
            self.users = {}
            
    def save_users(self):
        """保存用户数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {str(e)}")
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 配置样式
        style.configure('Title.TLabel', 
                       background='#2a5298', 
                       foreground='#ffffff',
                       font=('Microsoft YaHei UI', 24, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#2a5298',
                       foreground='#e0e0e0',
                       font=('Microsoft YaHei UI', 12))
        
        style.configure('Modern.TEntry',
                       font=('Microsoft YaHei UI', 11),
                       fieldbackground='rgba(255, 255, 255, 0.9)')
        
        style.configure('Modern.TButton',
                       font=('Microsoft YaHei UI', 11, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
    def create_poster_image(self):
        """创建或加载海报图片"""
        if PIL_AVAILABLE:
            try:
                # 尝试加载本地图片
                if os.path.exists("assets/poster.jpg"):
                    img = Image.open("assets/poster.jpg")
                    img = img.resize((480, 800), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
            except:
                pass
        
        # 如果无法加载图片，返回None使用默认背景
        return None
    
    def create_main_layout(self):
        """创建主布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg='#1e3c72')
        main_container.pack(fill='both', expand=True)
        
        # 左侧海报区域
        self.poster_frame = tk.Frame(main_container, bg='#1e3c72', width=480)
        self.poster_frame.pack(side='left', fill='y', padx=10, pady=10)
        self.poster_frame.pack_propagate(False)
        
        # 加载海报图片
        poster_image = self.create_poster_image()
        if poster_image:
            poster_label = tk.Label(self.poster_frame, image=poster_image, bg='#1e3c72')
            poster_label.image = poster_image  # 保持引用
            poster_label.pack(fill='both', expand=True)
        else:
            # 默认海报区域
            default_poster = tk.Label(self.poster_frame, 
                                    text="🎮\n欢迎使用\n登录器", 
                                    bg='#2a5298', 
                                    fg='white',
                                    font=('Microsoft YaHei UI', 20, 'bold'),
                                    justify='center')
            default_poster.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 右侧功能区域
        self.function_frame = tk.Frame(main_container, bg='#2a5298')
        self.function_frame.pack(side='right', fill='both', expand=True, padx=(0, 10), pady=10)
        
        # 创建内容容器
        self.content_container = tk.Frame(self.function_frame, bg='#2a5298')
        self.content_container.pack(fill='both', expand=True, padx=40, pady=50)
        
        # 显示登录界面
        self.show_login_view()
    
    def clear_content(self):
        """清空内容区域"""
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def show_login_view(self):
        """显示登录界面"""
        self.clear_content()
        self.current_view = "login"
        
        # 标题
        title = ttk.Label(self.content_container, text="用户登录", style='Title.TLabel')
        title.pack(pady=(0, 30))
        
        # 登录表单
        login_frame = tk.Frame(self.content_container, bg='#2a5298')
        login_frame.pack(fill='x', pady=20)
        
        # 用户名
        tk.Label(login_frame, text="用户名:", bg='#2a5298', fg='white', 
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(login_frame, font=('Microsoft YaHei UI', 11),
                                     bg='white', relief='flat', bd=10)
        self.username_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # 密码
        tk.Label(login_frame, text="密码:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(login_frame, show="*", font=('Microsoft YaHei UI', 11),
                                     bg='white', relief='flat', bd=10)
        self.password_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # 按钮区域
        button_frame = tk.Frame(login_frame, bg='#2a5298')
        button_frame.pack(fill='x', pady=10)
        
        # 登录按钮
        login_btn = tk.Button(button_frame, text="登录", 
                            command=self.handle_login,
                            bg='#4CAF50', fg='white', 
                            font=('Microsoft YaHei UI', 12, 'bold'),
                            relief='flat', bd=0, cursor='hand2')
        login_btn.pack(fill='x', ipady=10, pady=(0, 10))
        
        # 功能链接
        link_frame = tk.Frame(login_frame, bg='#2a5298')
        link_frame.pack(fill='x', pady=20)
        
        register_link = tk.Label(link_frame, text="还没有账号？立即注册", 
                               bg='#2a5298', fg='#87CEEB', 
                               font=('Microsoft YaHei UI', 10),
                               cursor='hand2')
        register_link.pack(anchor='w')
        register_link.bind("<Button-1>", lambda e: self.show_register_view())
        
        forgot_link = tk.Label(link_frame, text="忘记密码？", 
                             bg='#2a5298', fg='#87CEEB',
                             font=('Microsoft YaHei UI', 10),
                             cursor='hand2')
        forgot_link.pack(anchor='w', pady=(5, 0))
        forgot_link.bind("<Button-1>", lambda e: self.show_forgot_password())
        
        # 绑定回车键
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
    
    def show_register_view(self):
        """显示注册界面"""
        self.clear_content()
        self.current_view = "register"
        
        # 标题
        title = ttk.Label(self.content_container, text="用户注册", style='Title.TLabel')
        title.pack(pady=(0, 30))
        
        # 注册表单
        register_frame = tk.Frame(self.content_container, bg='#2a5298')
        register_frame.pack(fill='x', pady=20)
        
        # 用户名
        tk.Label(register_frame, text="用户名:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.reg_username_entry = tk.Entry(register_frame, font=('Microsoft YaHei UI', 11),
                                         bg='white', relief='flat', bd=10)
        self.reg_username_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # 邮箱
        tk.Label(register_frame, text="邮箱:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.reg_email_entry = tk.Entry(register_frame, font=('Microsoft YaHei UI', 11),
                                       bg='white', relief='flat', bd=10)
        self.reg_email_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # 密码
        tk.Label(register_frame, text="密码:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.reg_password_entry = tk.Entry(register_frame, show="*", font=('Microsoft YaHei UI', 11),
                                         bg='white', relief='flat', bd=10)
        self.reg_password_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # 确认密码
        tk.Label(register_frame, text="确认密码:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.reg_confirm_entry = tk.Entry(register_frame, show="*", font=('Microsoft YaHei UI', 11),
                                        bg='white', relief='flat', bd=10)
        self.reg_confirm_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # 按钮区域
        button_frame = tk.Frame(register_frame, bg='#2a5298')
        button_frame.pack(fill='x', pady=10)
        
        # 注册按钮
        register_btn = tk.Button(button_frame, text="注册", 
                               command=self.handle_register,
                               bg='#2196F3', fg='white',
                               font=('Microsoft YaHei UI', 12, 'bold'),
                               relief='flat', bd=0, cursor='hand2')
        register_btn.pack(fill='x', ipady=10, pady=(0, 10))
        
        # 返回登录
        back_link = tk.Label(register_frame, text="已有账号？返回登录", 
                           bg='#2a5298', fg='#87CEEB',
                           font=('Microsoft YaHei UI', 10),
                           cursor='hand2')
        back_link.pack(anchor='w', pady=(10, 0))
        back_link.bind("<Button-1>", lambda e: self.show_login_view())
    
    def show_verification_view(self):
        """显示验证码界面"""
        self.clear_content()
        self.current_view = "verification"
        
        # 标题
        title = ttk.Label(self.content_container, text="邮箱验证", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # 说明文字
        info_text = f"验证码已发送到 {self.user_email}\n请查收邮件并输入验证码"
        info_label = tk.Label(self.content_container, text=info_text,
                            bg='#2a5298', fg='#e0e0e0',
                            font=('Microsoft YaHei UI', 12),
                            justify='center')
        info_label.pack(pady=(0, 30))
        
        # 验证码输入
        verify_frame = tk.Frame(self.content_container, bg='#2a5298')
        verify_frame.pack(fill='x', pady=20)
        
        tk.Label(verify_frame, text="验证码:", bg='#2a5298', fg='white',
                font=('Microsoft YaHei UI', 12)).pack(anchor='w', pady=(0, 5))
        self.verify_code_entry = tk.Entry(verify_frame, font=('Microsoft YaHei UI', 14),
                                        bg='white', relief='flat', bd=10,
                                        justify='center')
        self.verify_code_entry.pack(fill='x', ipady=12, pady=(0, 20))
        
        # 按钮区域
        button_frame = tk.Frame(verify_frame, bg='#2a5298')
        button_frame.pack(fill='x', pady=10)
        
        # 验证按钮
        verify_btn = tk.Button(button_frame, text="验证", 
                             command=self.handle_verification,
                             bg='#4CAF50', fg='white',
                             font=('Microsoft YaHei UI', 12, 'bold'),
                             relief='flat', bd=0, cursor='hand2')
        verify_btn.pack(fill='x', ipady=10, pady=(0, 10))
        
        # 重新发送
        resend_link = tk.Label(verify_frame, text="没收到验证码？重新发送", 
                             bg='#2a5298', fg='#87CEEB',
                             font=('Microsoft YaHei UI', 10),
                             cursor='hand2')
        resend_link.pack(anchor='w', pady=(10, 0))
        resend_link.bind("<Button-1>", lambda e: self.resend_verification())
        
        # 返回
        back_link = tk.Label(verify_frame, text="返回注册", 
                           bg='#2a5298', fg='#87CEEB',
                           font=('Microsoft YaHei UI', 10),
                           cursor='hand2')
        back_link.pack(anchor='w', pady=(5, 0))
        back_link.bind("<Button-1>", lambda e: self.show_register_view())
        
        # 绑定回车键
        self.verify_code_entry.bind('<Return>', lambda e: self.handle_verification())
        self.verify_code_entry.focus()
    
    def validate_email(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """验证密码强度"""
        if len(password) < 6:
            return False, "密码长度至少6位"
        if len(password) > 20:
            return False, "密码长度不能超过20位"
        return True, "密码符合要求"
    
    def generate_verification_code(self):
        """生成验证码"""
        return str(random.randint(100000, 999999))
    
    def send_verification_email(self, email, code):
        """发送验证邮件（模拟）"""
        # 这里应该是真实的邮件发送逻辑
        print(f"发送验证码 {code} 到邮箱 {email}")
        return True
    
    def handle_login(self):
        """处理登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            messagebox.showerror("错误", "请输入用户名")
            return
        
        if not password:
            messagebox.showerror("错误", "请输入密码")
            return
        
        # 验证用户
        if username in self.users:
            user_data = self.users[username]
            if user_data['password'] == password:
                if user_data.get('verified', False):
                    messagebox.showinfo("成功", f"登录成功！欢迎 {username}")
                    self.show_main_app()
                else:
                    messagebox.showwarning("提示", "账号未验证，请先完成邮箱验证")
                    self.user_email = user_data['email']
                    self.send_verification_code()
                    self.show_verification_view()
            else:
                messagebox.showerror("错误", "密码错误")
        else:
            messagebox.showerror("错误", "用户不存在")
    
    def handle_register(self):
        """处理注册"""
        username = self.reg_username_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        
        # 验证输入
        if not username:
            messagebox.showerror("错误", "请输入用户名")
            return
        
        if len(username) < 3:
            messagebox.showerror("错误", "用户名至少3位")
            return
        
        if not email:
            messagebox.showerror("错误", "请输入邮箱")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("错误", "邮箱格式不正确")
            return
        
        if not password:
            messagebox.showerror("错误", "请输入密码")
            return
        
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            messagebox.showerror("错误", msg)
            return
        
        if password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        # 检查用户是否已存在
        if username in self.users:
            messagebox.showerror("错误", "用户名已存在")
            return
        
        # 检查邮箱是否已被使用
        for user_data in self.users.values():
            if user_data['email'] == email:
                messagebox.showerror("错误", "邮箱已被使用")
                return
        
        # 注册用户
        self.users[username] = {
            'email': email,
            'password': password,
            'verified': False,
            'created_at': str(random.randint(1000000000, 9999999999))
        }
        
        self.save_users()
        self.user_email = email
        self.send_verification_code()
        
        messagebox.showinfo("成功", "注册成功！请查收验证邮件")
        self.show_verification_view()
    
    def send_verification_code(self):
        """发送验证码"""
        self.verification_code = self.generate_verification_code()
        success = self.send_verification_email(self.user_email, self.verification_code)
        
        if not success:
            messagebox.showerror("错误", "验证码发送失败，请稍后重试")
    
    def handle_verification(self):
        """处理验证"""
        entered_code = self.verify_code_entry.get().strip()
        
        if not entered_code:
            messagebox.showerror("错误", "请输入验证码")
            return
        
        if entered_code == self.verification_code:
            # 验证成功，更新用户状态
            for username, user_data in self.users.items():
                if user_data['email'] == self.user_email:
                    user_data['verified'] = True
                    self.save_users()
                    break
            
            messagebox.showinfo("成功", "邮箱验证成功！")
            self.show_login_view()
        else:
            messagebox.showerror("错误", "验证码错误，请重新输入")
    
    def resend_verification(self):
        """重新发送验证码"""
        self.send_verification_code()
        messagebox.showinfo("提示", "验证码已重新发送，请查收邮件")
    
    def show_forgot_password(self):
        """显示忘记密码"""
        messagebox.showinfo("提示", "忘记密码功能开发中...")
    
    def show_main_app(self):
        """显示主应用界面"""
        self.clear_content()
        
        # 欢迎界面
        welcome_label = ttk.Label(self.content_container, 
                                text="🎉 登录成功！", 
                                style='Title.TLabel')
        welcome_label.pack(pady=(50, 30))
        
        # 功能按钮
        features_frame = tk.Frame(self.content_container, bg='#2a5298')
        features_frame.pack(fill='x', pady=20)
        
        # 示例功能按钮
        features = [
            ("🎮 游戏中心", self.open_game_center),
            ("👤 个人资料", self.open_profile),
            ("⚙️ 设置", self.open_settings),
            ("🚪 退出登录", self.logout)
        ]
        
        for i, (text, command) in enumerate(features):
            btn = tk.Button(features_frame, text=text,
                          command=command,
                          bg='#3f51b5', fg='white',
                          font=('Microsoft YaHei UI', 12),
                          relief='flat', bd=0, cursor='hand2')
            btn.pack(fill='x', ipady=15, pady=10)
    
    def open_game_center(self):
        """打开游戏中心"""
        messagebox.showinfo("游戏中心", "游戏中心功能开发中...")
    
    def open_profile(self):
        """打开个人资料"""
        messagebox.showinfo("个人资料", "个人资料功能开发中...")
    
    def open_settings(self):
        """打开设置"""
        messagebox.showinfo("设置", "设置功能开发中...")
    
    def logout(self):
        """退出登录"""
        result = messagebox.askyesno("确认", "确定要退出登录吗？")
        if result:
            self.show_login_view()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ModernLoginApp()
        app.run()
    except Exception as e:
        import sys
        print(f"应用启动失败: {e}")
        sys.exit(1)
