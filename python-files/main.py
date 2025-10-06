#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化登录器 - 在线编译专用版
完全兼容，无外部依赖
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import re

class LoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("登录器")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        self.center_window()
        
        # 数据
        self.users = {}
        self.current_code = ""
        self.current_email = ""
        
        self.create_ui()
    
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def create_ui(self):
        # 主容器
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 左侧
        left_frame = tk.Frame(main_frame, bg='#34495e', width=400)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 标题
        title = tk.Label(left_frame, text="🎮\n游戏登录器", 
                        bg='#34495e', fg='white',
                        font=('Arial', 20, 'bold'), justify='center')
        title.pack(pady=50)
        
        features = ["安全登录", "邮箱验证", "数据保护", "现代界面"]
        for f in features:
            lbl = tk.Label(left_frame, text=f"✓ {f}", 
                          bg='#34495e', fg='#ecf0f1',
                          font=('Arial', 12))
            lbl.pack(pady=10)
        
        # 右侧
        self.right_frame = tk.Frame(main_frame, bg='#3498db')
        self.right_frame.pack(side='right', fill='both', expand=True)
        
        self.show_login()
    
    def clear_right(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
    
    def show_login(self):
        self.clear_right()
        
        container = tk.Frame(self.right_frame, bg='#3498db')
        container.pack(expand=True, fill='both', padx=40, pady=40)
        
        tk.Label(container, text="用户登录", bg='#3498db', fg='white',
                font=('Arial', 18, 'bold')).pack(pady=(0, 30))
        
        tk.Label(container, text="用户名:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.login_user = tk.Entry(container, font=('Arial', 12))
        self.login_user.pack(fill='x', pady=(5, 15), ipady=5)
        
        tk.Label(container, text="密码:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.login_pass = tk.Entry(container, show='*', font=('Arial', 12))
        self.login_pass.pack(fill='x', pady=(5, 20), ipady=5)
        
        tk.Button(container, text="登录", command=self.do_login,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 cursor='hand2').pack(fill='x', pady=10, ipady=8)
        
        link1 = tk.Label(container, text="没有账号？点击注册", 
                        bg='#3498db', fg='#ecf0f1', cursor='hand2',
                        font=('Arial', 10))
        link1.pack(pady=(15, 5))
        link1.bind('<Button-1>', lambda e: self.show_register())
        
        self.login_pass.bind('<Return>', lambda e: self.do_login())
    
    def show_register(self):
        self.clear_right()
        
        container = tk.Frame(self.right_frame, bg='#3498db')
        container.pack(expand=True, fill='both', padx=40, pady=30)
        
        tk.Label(container, text="用户注册", bg='#3498db', fg='white',
                font=('Arial', 18, 'bold')).pack(pady=(0, 25))
        
        tk.Label(container, text="用户名:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.reg_user = tk.Entry(container, font=('Arial', 12))
        self.reg_user.pack(fill='x', pady=(5, 12), ipady=5)
        
        tk.Label(container, text="邮箱:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.reg_email = tk.Entry(container, font=('Arial', 12))
        self.reg_email.pack(fill='x', pady=(5, 12), ipady=5)
        
        tk.Label(container, text="密码:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.reg_pass = tk.Entry(container, show='*', font=('Arial', 12))
        self.reg_pass.pack(fill='x', pady=(5, 12), ipady=5)
        
        tk.Label(container, text="确认密码:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.reg_pass2 = tk.Entry(container, show='*', font=('Arial', 12))
        self.reg_pass2.pack(fill='x', pady=(5, 18), ipady=5)
        
        tk.Button(container, text="注册", command=self.do_register,
                 bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                 cursor='hand2').pack(fill='x', pady=8, ipady=8)
        
        link2 = tk.Label(container, text="已有账号？返回登录", 
                        bg='#3498db', fg='#ecf0f1', cursor='hand2',
                        font=('Arial', 10))
        link2.pack(pady=(12, 0))
        link2.bind('<Button-1>', lambda e: self.show_login())
    
    def show_verify(self):
        self.clear_right()
        
        container = tk.Frame(self.right_frame, bg='#3498db')
        container.pack(expand=True, fill='both', padx=40, pady=50)
        
        tk.Label(container, text="邮箱验证", bg='#3498db', fg='white',
                font=('Arial', 18, 'bold')).pack(pady=(0, 20))
        
        info = f"验证码已发送到:\n{self.current_email}\n\n请输入6位验证码"
        tk.Label(container, text=info, bg='#3498db', fg='white',
                font=('Arial', 12), justify='center').pack(pady=(0, 25))
        
        tk.Label(container, text="验证码:", bg='#3498db', fg='white',
                font=('Arial', 12)).pack(anchor='w')
        self.verify_code = tk.Entry(container, font=('Arial', 12))
        self.verify_code.pack(fill='x', pady=(5, 20), ipady=5)
        
        tk.Button(container, text="验证", command=self.do_verify,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 cursor='hand2').pack(fill='x', pady=8, ipady=8)
        
        link3 = tk.Label(container, text="重新发送验证码", 
                        bg='#3498db', fg='#ecf0f1', cursor='hand2',
                        font=('Arial', 10))
        link3.pack(pady=(15, 5))
        link3.bind('<Button-1>', lambda e: self.resend_code())
        
        link4 = tk.Label(container, text="返回注册", 
                        bg='#3498db', fg='#ecf0f1', cursor='hand2',
                        font=('Arial', 10))
        link4.pack(pady=5)
        link4.bind('<Button-1>', lambda e: self.show_register())
        
        self.verify_code.bind('<Return>', lambda e: self.do_verify())
    
    def show_success(self, msg):
        self.clear_right()
        
        container = tk.Frame(self.right_frame, bg='#3498db')
        container.pack(expand=True, fill='both', padx=40, pady=80)
        
        tk.Label(container, text="✅", bg='#3498db', fg='#27ae60',
                font=('Arial', 40)).pack(pady=(0, 20))
        
        tk.Label(container, text=msg, bg='#3498db', fg='white',
                font=('Arial', 16, 'bold')).pack(pady=(0, 30))
        
        tk.Button(container, text="返回登录", command=self.show_login,
                 bg='#2980b9', fg='white', font=('Arial', 12, 'bold'),
                 cursor='hand2').pack(pady=10, ipadx=20, ipady=8)
    
    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def do_login(self):
        user = self.login_user.get().strip()
        password = self.login_pass.get()
        
        if not user or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        if user in self.users:
            data = self.users[user]
            if data['password'] == password:
                if data.get('verified', False):
                    self.show_success(f"欢迎回来，{user}！")
                else:
                    messagebox.showwarning("提示", "请先验证邮箱")
                    self.current_email = data['email']
                    self.current_code = str(random.randint(100000, 999999))
                    messagebox.showinfo("提示", f"验证码: {self.current_code}")
                    self.show_verify()
            else:
                messagebox.showerror("错误", "密码错误")
        else:
            messagebox.showerror("错误", "用户不存在")
    
    def do_register(self):
        user = self.reg_user.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_pass.get()
        password2 = self.reg_pass2.get()
        
        if not all([user, email, password, password2]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if len(user) < 3:
            messagebox.showerror("错误", "用户名至少3个字符")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("错误", "邮箱格式不正确")
            return
        
        if len(password) < 6:
            messagebox.showerror("错误", "密码至少6个字符")
            return
        
        if password != password2:
            messagebox.showerror("错误", "两次密码不一致")
            return
        
        if user in self.users:
            messagebox.showerror("错误", "用户名已存在")
            return
        
        # 检查邮箱
        for data in self.users.values():
            if data.get('email') == email:
                messagebox.showerror("错误", "邮箱已被使用")
                return
        
        # 保存用户
        self.users[user] = {
            'email': email,
            'password': password,
            'verified': False
        }
        
        self.current_email = email
        self.current_code = str(random.randint(100000, 999999))
        
        messagebox.showinfo("成功", f"注册成功！\n验证码: {self.current_code}")
        self.show_verify()
    
    def do_verify(self):
        code = self.verify_code.get().strip()
        
        if not code:
            messagebox.showerror("错误", "请输入验证码")
            return
        
        if code == self.current_code:
            # 更新验证状态
            for data in self.users.values():
                if data.get('email') == self.current_email:
                    data['verified'] = True
                    break
            
            self.show_success("验证成功！")
        else:
            messagebox.showerror("错误", "验证码错误")
    
    def resend_code(self):
        self.current_code = str(random.randint(100000, 999999))
        messagebox.showinfo("提示", f"新验证码: {self.current_code}")
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = LoginApp()
    app.run()
