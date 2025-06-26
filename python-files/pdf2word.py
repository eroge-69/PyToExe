import os
import sys
from pdf2docx import Converter
import tkinter as tk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
import time

class PDFToWordConverter:
    def __init__(self):
        self.input_folder = ""
        self.output_folder = ""
        
    def select_input_folder(self):
        """选择输入文件夹（包含PDF文件）"""
        folder = filedialog.askdirectory(title="选择包含PDF文件的文件夹")
        if folder:
            self.input_folder = folder
            self.input_path_var.set(folder)
            
    def select_output_folder(self):
        """选择输出文件夹（存储转换后的Word文件）"""
        folder = filedialog.askdirectory(title="选择Word文件输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_path_var.set(folder)
    
    def convert_pdf_to_word(self, pdf_file, output_file):
        """转换单个PDF文件为Word文件"""
        try:
            # 更新状态
            self.status_var.set(f"正在转换: {os.path.basename(pdf_file)}")
            self.root.update()
            
            # 执行转换
            cv = Converter(pdf_file)
            cv.convert(output_file)
            cv.close()
            return True
        except Exception as e:
            print(f"转换 {pdf_file} 时出错: {str(e)}")
            return False
    
    def start_conversion(self):
        """开始批量转换过程"""
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("错误", "请先选择输入和输出文件夹！")
            return
            
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            messagebox.showinfo("提示", "输入文件夹中没有找到PDF文件！")
            return
            
        total_files = len(pdf_files)
        self.progress_var.set(f"0/{total_files}")
        
        # 更新状态
        self.status_var.set("开始转换...")
        self.root.update()
        
        # 记录开始时间
        start_time = time.time()
        
        # 转换计数器
        success_count = 0
        
        # 使用线程池进行并行转换
        with ThreadPoolExecutor(max_workers=min(os.cpu_count(), 4)) as executor:
            futures = []
            
            for i, pdf_file in enumerate(pdf_files):
                pdf_path = os.path.join(self.input_folder, pdf_file)
                # 将输出文件名更改为.docx后缀
                output_filename = os.path.splitext(pdf_file)[0] + ".docx"
                output_path = os.path.join(self.output_folder, output_filename)
                
                # 提交转换任务到线程池
                future = executor.submit(self.convert_pdf_to_word, pdf_path, output_path)
                futures.append((future, pdf_file))
            
            # 处理转换结果
            for i, (future, pdf_file) in enumerate(futures):
                result = future.result()
                if result:
                    success_count += 1
                
                # 更新进度
                self.progress_var.set(f"{i+1}/{total_files}")
                self.root.update()
        
        # 计算总耗时
        elapsed_time = time.time() - start_time
        
        # 显示完成消息
        completion_msg = (f"转换完成！\n"
                         f"成功转换: {success_count}/{total_files} 文件\n"
                         f"耗时: {elapsed_time:.2f} 秒")
        
        self.status_var.set("转换完成!")
        messagebox.showinfo("完成", completion_msg)
    
    def create_gui(self):
        """创建图形用户界面"""
        self.root = tk.Tk()
        self.root.title("PDF批量转Word工具")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        # 输入路径变量
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪")
        self.progress_var = tk.StringVar(value="0/0")
        
        # 创建布局
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入文件夹选择
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="PDF文件夹:").pack(side=tk.LEFT)
        tk.Entry(input_frame, textvariable=self.input_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(input_frame, text="浏览", command=self.select_input_folder).pack(side=tk.RIGHT)
        
        # 输出文件夹选择
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="输出文件夹:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(output_frame, text="浏览", command=self.select_output_folder).pack(side=tk.RIGHT)
        
        # 开始转换按钮
        tk.Button(main_frame, text="开始转换", command=self.start_conversion, 
                 bg="#4CAF50", fg="white", font=("Arial", 12), padx=10, pady=5).pack(pady=20)
        
        # 状态框架
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        tk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        tk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        tk.Label(status_frame, text="进度:").pack(side=tk.LEFT, padx=(20, 0))
        tk.Label(status_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=5)
        
        # 底部提示
        tk.Label(self.root, text="提示：请确保已安装必要的库 (pdf2docx)", 
                fg="gray").pack(side=tk.BOTTOM, pady=5)
        
        self.root.mainloop()
        
    def run(self):
        """运行应用程序"""
        # 检查必要的库是否已安装
        try:
            import pdf2docx
        except ImportError:
            print("缺少必要的库。正在尝试安装...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2docx"])
            print("安装完成！")
            
        self.create_gui()

if __name__ == "__main__":
    app = PDFToWordConverter()
    app.run()
