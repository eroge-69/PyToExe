#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件名: 打包.py
作者: xl1222, wusheng233
日期: 2025-8-10
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import platform
import threading
import logging

class PharPackager:
    def __init__(self, root):
        self.root = root
        self.root.title("Phar打包解包")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        # self.root.configure(bg="#f0f0f0") 无效

        # 初始化变量 - 添加 include_hidden 定义
        self.source_dir = ""
        self.output_file = ""
        self.stub = "<?php __HALT_COMPILER(); ?>"
        self.compression = "None"
        self.php_executable = self.get_php_executable()
        # self.include_hidden = tk.BooleanVar(value=False)  # 添加这行

        # 应用样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))

        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建顶部标题
        self.header = ttk.Label(
            self.main_frame,
            text="Phar文件打包和解包工具",
            style="Header.TLabel",
            foreground="#000000"
        )
        self.header.pack(pady=(0, 10))

        # 创建配置区域
        self.create_config_section()

        # 创建日志区域
        self.create_log_section()

        # 底部按钮
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(fill=tk.X, pady=7)

        self.pack_btn = ttk.Button(
            self.btn_frame,
            text="开始打包",
            command=self.start_packing,
            style="Accent.TButton"
        )
        self.pack_btn.pack(side=tk.RIGHT, padx=5)

        self.unpack_btn = ttk.Button(
            self.btn_frame,
            text="开始解包",
            command=self.start_unpacking,
            style="Accent.TButton"
        )
        self.unpack_btn.pack(side=tk.RIGHT, padx=5)

        # 自定义按钮样式
        # 白底白字看不见！！！
        # self.style.configure("Accent.TButton", background="#3498db", foreground="white")

    def create_config_section(self):
        config_frame = ttk.LabelFrame(
            self.main_frame,
            text="打包配置",
            padding=5
        )
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # 源目录选择
        source_frame = ttk.Frame(config_frame)
        source_frame.pack(fill=tk.X, pady=2)

        ttk.Label(source_frame, text="源代码目录:").pack(side=tk.LEFT, padx=(0, 10))

        self.source_entry = ttk.Entry(source_frame, width=5)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.browse_btn = ttk.Button(
            source_frame,
            text="浏览...",
            command=self.browse_source
        )
        self.browse_btn.pack(side=tk.RIGHT)

        # 输出文件
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, pady=2)

        ttk.Label(output_frame, text="输出文件:").pack(side=tk.LEFT, padx=(0, 10))

        self.output_entry = ttk.Entry(output_frame, width=5)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.output_browse_btn = ttk.Button(
            output_frame,
            text="浏览...",
            command=self.browse_output
        )
        self.output_browse_btn.pack(side=tk.RIGHT)

        # 入口文件
        entry_frame = ttk.Frame(config_frame)
        entry_frame.pack(fill=tk.X, pady=2)

        ttk.Label(entry_frame, text="Stub:").pack(side=tk.LEFT, padx=(0, 10))

        self.stub_entry = ttk.Entry(entry_frame, width=5)
        self.stub_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.stub_entry.insert(0, self.stub)

        # PHP可执行文件
        executable_frame = ttk.Frame(config_frame)
        executable_frame.pack(fill=tk.X, pady=2)

        ttk.Label(executable_frame, text="PHP可执行文件:").pack(side=tk.LEFT, padx=(0, 10))

        self.executable_entry = ttk.Entry(executable_frame, width=5)
        self.executable_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.executable_entry.insert(0, self.php_executable)

        # 压缩选项
        compression_frame = ttk.Frame(config_frame)
        compression_frame.pack(fill=tk.X, pady=2)

        ttk.Label(compression_frame, text="压缩:").pack(side=tk.LEFT, padx=(0, 10))

        self.compression_var = tk.StringVar(value="None")
        compressions = ["None", "GZ", "BZ2"]
        for comp in compressions:
            ttk.Radiobutton(
                compression_frame,
                text=comp,
                variable=self.compression_var,
                value=comp
            ).pack(side=tk.LEFT, padx=(0, 15))

        # 包含隐藏文件
        #hidden_frame = ttk.Frame(config_frame)
        #hidden_frame.pack(fill=tk.X, pady=5)

        #ttk.Checkbutton(
        #    hidden_frame,
        #    text="包含隐藏文件",
        #    variable=self.include_hidden  # 现在这里可以正常访问了
        #).pack(side=tk.LEFT)

    def create_log_section(self):
        log_frame = ttk.LabelFrame(
            self.main_frame,
            text="打包日志",
            padding=5
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=3,
            bg="white",
            fg="#333333",
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条 占空间，用不了
        #scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        #self.log_text.config(yscrollcommand=scrollbar.set)

        # 初始日志
        self.log_text.insert(tk.END, "准备打包...\n")
        self.log_text.insert(tk.END, "请选择源代码目录并设置打包参数\n")
        self.log_text.config(state=tk.DISABLED)

    def browse_source(self):
        directory = filedialog.askdirectory(title="选择源代码目录")
        if directory:
            self.source_dir = directory
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, directory)

            # 自动设置输出文件名
            if not self.output_entry.get():
                dir_name = os.path.basename(directory)
                output_path = os.path.join(directory, f"{dir_name}.phar")
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, output_path)

    def browse_output(self):
        file = filedialog.askopenfilename(
            title="选择PHAR文件",
            defaultextension=".phar",
            filetypes=[("PHAR Files", "*.phar"), ("All Files", "*.*")]
        )
        if file:
            self.output_file = file
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file)

            # 自动设置输出文件夹
            if not self.source_entry.get():
                self.source_entry.delete(0, tk.END)
                self.source_entry.insert(0, os.path.join(os.path.dirname(file), os.path.splitext(os.path.basename(file))[0]))

    def verify_input(self):
        # 验证输入
        if not self.php_executable:
            messagebox.showerror("错误", "请指定PHP可执行文件")
            return False

        if not self.source_dir:
            messagebox.showerror("错误", "请选择源代码目录")
            return False

        if not self.output_file:
            messagebox.showerror("错误", "请指定输出文件")
            return False
        return True

    def disable_action_bar(self):
        self.pack_btn.config(state=tk.DISABLED)
        self.unpack_btn.config(state=tk.DISABLED)

    def enable_action_bar(self):
        self.root.after(100, lambda: self.pack_btn.config(state=tk.NORMAL))
        self.root.after(100, lambda: self.unpack_btn.config(state=tk.NORMAL))

    def update_input_value(self):
        self.source_dir = self.source_entry.get()
        self.output_file = self.output_entry.get()
        self.stub = self.stub_entry.get()
        self.compression = self.compression_var.get()
        self.php_executable = self.executable_entry.get()

    def start_packing(self):
        # 获取输入值
        self.update_input_value()

        if not self.verify_input():
            return
        if not os.path.isdir(self.source_dir):
            messagebox.showerror("错误", "选择的源目录不存在")
            return False
        if not self.stub:
            messagebox.showerror("错误", "请指定Stub")
            return

        # 禁用按钮
        self.disable_action_bar()

        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "开始打包...\n") # TODO: metadata
        self.log_text.insert(tk.END, f"源目录: {self.source_dir}\n")
        self.log_text.insert(tk.END, f"输出文件: {self.output_file}\n")
        self.log_text.insert(tk.END, f"Stub: {self.stub}\n")
        self.log_text.insert(tk.END, f"压缩: {self.compression}\n")
        self.log_text.insert(tk.END, "-" * 50 + "\n")
        self.log_text.config(state=tk.DISABLED)

        # 在新线程中运行打包过程
        threading.Thread(target=self.pack_phar, daemon=True).start()

    def start_unpacking(self):
        self.update_input_value()
        if not self.verify_input():
            return
        # 不需要验证输出目录
        self.disable_action_bar()

        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "开始解包...\n") # TODO: metadata
        self.log_text.insert(tk.END, f"输出目录: {self.source_dir}\n")
        self.log_text.insert(tk.END, f"源文件: {self.output_file}\n")
        self.log_text.insert(tk.END, "-" * 50 + "\n")
        self.log_text.config(state=tk.DISABLED)

        threading.Thread(target=self.unpack_phar, daemon=True).start()

    def pack_phar(self):
        try:
            # 生成打包命令并运行
            return_code = self.run_command(self.generate_pack_command())
            if return_code == 0:
                self.log_text_insert("\n打包成功!\n")
                messagebox.showinfo("成功", "PHAR文件打包成功!")
            else:
                self.log_text_insert(f"\n打包失败，状态码: {return_code}\n")
                messagebox.showerror("错误", f"打包失败，请查看日志")

        except Exception as e:
            self.log_text_insert(f"发生错误: {str(e)}\n")
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            logging.exception(e)
        finally:
            # 重新启用按钮
            self.enable_action_bar()

    def unpack_phar(self): # XXX
        try:
            source_dir = os.path.abspath(self.source_dir)
            output_file = os.path.abspath(self.output_file)

            return_code = self.run_command([
                self.php_executable,
                "-r",
                'function recurse_copy($src,$dst){$dir=opendir($src);if($dir===false){echo "无法打开文件夹$dir";exit(1);}@mkdir($dst);while(($f=readdir($dir))!==false){if($f!="."&&$f!=".."){if(is_dir("$src/$f")){recurse_copy("$src/$f","$dst/$f");}else{copy("$src/$f","$dst/$f");}}}closedir($dir);}' + # XXX
                f"recurse_copy('phar://{output_file}','{source_dir}');" # FIXME: 注入
            ])
            if return_code == 0:
                self.log_text_insert("\n解包成功!\n")
                messagebox.showinfo("成功", "PHAR文件解包成功!")
            else:
                self.log_text_insert(f"\n解包失败，状态码: {return_code}\n")
                messagebox.showerror("错误", f"解包失败，请查看日志")

        except Exception as e:
            self.log_text_insert(f"发生错误: {str(e)}\n")
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            logging.exception(e)
        finally:
            self.enable_action_bar()

    def log_text_insert(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_command(self, cmd):
        # 更新日志
        self.log_text_insert(f"执行命令: {cmd}\n")

        # 执行命令
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='GBK'
        )

        # 实时读取输出
        while True:
            output = process.stdout.readline()
            error = process.stderr.read()

            exitCode = process.poll()
            if exitCode is not None:
                return exitCode
            if output:
                self.log_text_insert(output)
            if error:
                self.log_text_insert(error)

    def get_php_executable(self):
        # 确定PHP可执行文件路径
        if platform.system() == "Windows":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 在Windows上尝试查找PHP
            possible_paths = [ # TODO: 查找PATH，工作目录
                "C:\\php\\php.exe",
                "C:\\Program Files\\php\\php.exe",
                os.path.join(current_dir, "bin\\php\\php.exe"),
                "C:\\xampp\\php\\php.exe"
            ]
            for path in possible_paths:
                if os.path.isfile(path):
                    return path
        return "php"

    def generate_pack_command(self):
        # 获取绝对路径
        source_dir = os.path.abspath(self.source_dir)
        output_file = os.path.abspath(self.output_file)
        stub = self.stub

        # 创建打包命令
        cmd = [
            self.php_executable,
            "-d",
            "phar.readonly=0",
            "-r",
            f"$phar = new Phar('{output_file}');" + # FIXME: 注入
            "$phar->startBuffering();" +
            f"$phar->buildFromDirectory('{source_dir}', '');" +
            f"$phar->setStub('{stub}');"
        ]

        # 添加压缩选项
        if self.compression == "GZ":
            cmd[-1] += "$phar->compressFiles(Phar::GZ);"
        elif self.compression == "BZ2":
            cmd[-1] += "$phar->compressFiles(Phar::BZ2);"

        # 保存并添加结束符
        cmd[-1] += '$phar->stopBuffering();'

        return cmd

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharPackager(root)
    app.run()
