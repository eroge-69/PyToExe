import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import webbrowser


class FileBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("W Simple BackUp Data")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.setup_ui()
        
        # 设置默认路径
        self.source_dir = os.path.expanduser("~/Documents")
        self.backup_dir = os.path.expanduser("~/Backups")
        self.source_var.set(self.source_dir)
        self.backup_var.set(self.backup_dir)
        
        # 设置文件类型
        self.file_types = {'.doc', '.xls', '.pdf', '.docx', '.xlsx', '.ppt', '.pptx', '.jpg', 'jpeg'}
    
        self.file_type_vars = {
            '.doc': tk.BooleanVar(value=True),
            '.xls': tk.BooleanVar(value=True),
            '.pdf': tk.BooleanVar(value=True),
            '.docx': tk.BooleanVar(value=True),
            '.xlsx': tk.BooleanVar(value=True),
            '.ppt': tk.BooleanVar(value=True),
            '.pptx': tk.BooleanVar(value=True),
            '.jpg': tk.BooleanVar(value=True),
            '.jpeg': tk.BooleanVar(value=True)
        }
        
        # 备份历史
        self.backup_history = []
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        # 标题
        title_label = ttk.Label(main_frame, text="Simple BackUp Data", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)
        
        # 源目录选择
        source_frame = ttk.LabelFrame(main_frame, text="Save From 选择备份源目录", padding=10)
        source_frame.pack(fill=tk.X, padx=5, pady=5)

        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=50)
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        source_btn = ttk.Button(source_frame, text="Browse浏览...", command=self.select_source)
        source_btn.pack(side=tk.RIGHT)
        
          # 新添加的提示文字行 (仅此部分是新加的)
        ttk.Label(source_frame, 
                 text="if don't know where the original file saved, just enter C:\\ ",
                 font=('Arial', 8), 
                 foreground='gray').pack(side=tk.TOP, fill=tk.X, pady=(5,0))
        
      
        # 备份目录选择
        backup_frame = ttk.LabelFrame(main_frame, text="Save To选择备份目标目录", padding=10)
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.backup_var = tk.StringVar()
        backup_entry = ttk.Entry(backup_frame, textvariable=self.backup_var, width=50)
        backup_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        backup_btn = ttk.Button(backup_frame, text="Browse浏览...", command=self.select_backup)
        backup_btn.pack(side=tk.RIGHT)
        
        # 文件类型选择
        filetype_frame = ttk.LabelFrame(main_frame, text="Select File Type选择要备份的文件类型", padding=10)
        filetype_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建文件类型复选框
        check_frame = ttk.Frame(filetype_frame)
        check_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(check_frame, text="Word文档 (.doc)", variable=tk.BooleanVar(value=True),
                        command=lambda: self.toggle_file_type('.doc')).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="Excel表格 (.xls)", variable=tk.BooleanVar(value=True), 
                        command=lambda: self.toggle_file_type('.xls')).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="PDF文件 (.pdf)", variable=tk.BooleanVar(value=True),
                        command=lambda: self.toggle_file_type('.pdf')).grid(row=0 , column=4, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="Word文档 (.docx)", variable=tk.BooleanVar(value=True), 
                        command=lambda: self.toggle_file_type('.docx')).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="Excel表格 (.xlsx)", variable=tk.BooleanVar(value=True), 
                        command=lambda: self.toggle_file_type('.xlsx')).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="PPT演示文稿 (.ppt)", variable=tk.BooleanVar(value=True),
                        command=lambda: self.toggle_file_type('.ppt')).grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="PPT演示文稿 (.pptx)", variable=tk.BooleanVar(value=True),
                        command=lambda: self.toggle_file_type('.pptx')).grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="JPG照片 (.jpg)", variable=tk.BooleanVar(value=True),
                        command=lambda: self.toggle_file_type('.jpg')).grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        ttk.Checkbutton(check_frame, text="JPG照片 (.jpeg)", variable=tk.BooleanVar(value=True),
                       command=lambda: self.toggle_file_type('.jpeg')).grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)


        # 备份按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        self.backup_btn = ttk.Button(btn_frame, text="BackUp开始备份", command=self.start_backup, style='Accent.TButton')
        self.backup_btn.pack(side=tk.LEFT, padx=10)
        
        self.open_btn = ttk.Button(btn_frame, text="Open BackUp Folder打开备份目录", command=self.open_backup_folder, state=tk.DISABLED)
        self.open_btn.pack(side=tk.LEFT, padx=10)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(anchor=tk.W, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="备份日志", padding=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=5, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 底部信息栏
        footer = ttk.Frame(main_frame)
        footer.pack(fill=tk.X, pady=5)
        
        ttk.Label(footer, text="© 2889 File BackUp Tool").pack(side=tk.LEFT)
        ttk.Button(footer, text="帮助", command=self.show_help).pack(side=tk.RIGHT)
        
        # 自定义样式
        self.root.style = ttk.Style()
        self.root.style.configure('Accent.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#4CAF50')
        
    def select_source(self):
        directory = filedialog.askdirectory(title="选择备份源目录", initialdir=self.source_dir)
        if directory:
            self.source_var.set(directory)
            
    def select_backup(self):
        directory = filedialog.askdirectory(title="选择备份目标目录", initialdir=self.backup_dir)
        if directory:
            self.backup_var.set(directory)
            
    def toggle_file_type(self, ext):
        current = self.file_types.copy()
        if ext in current:
            current.remove(ext)
        else:
            current.add(ext)
        self.file_types = current
        
    def start_backup(self):
        source_dir = self.source_var.get()
        backup_root = self.backup_var.get()
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", f"源目录不存在: {source_dir}")
            return
            
        if not os.path.exists(backup_root):
            try:
                os.makedirs(backup_root)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建备份目录: {e}")
                return
        
        # 创建带时间戳的备份文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(backup_root, f"Backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # 禁用按钮，开始备份
        self.backup_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_var.set("正在扫描文件...")
        self.log_message(f"开始备份: {source_dir} → {backup_dir}")
        
        # 在新线程中执行备份
        threading.Thread(target=self.perform_backup, args=(source_dir, backup_dir), daemon=True).start()
        
    def perform_backup(self, source_dir, backup_dir):
        try:
            # 扫描所有符合条件的文件
            valid_files = []
            total_size = 0
            for foldername, _, filenames in os.walk(source_dir):
                for filename in filenames:
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in self.file_types:
                        file_path = os.path.join(foldername, filename)
                        valid_files.append(file_path)
                        total_size += os.path.getsize(file_path)
                        
            if not valid_files:
                self.log_message("未找到符合条件的文件")
                self.status_var.set("未找到文件")
                self.backup_btn.config(state=tk.NORMAL)
                return
                
            self.log_message(f"找到 {len(valid_files)} 个文件需要备份，总大小: {self.format_size(total_size)}")
            self.status_var.set(f"正在备份 0/{len(valid_files)} 文件...")
            
            # 备份文件
            backed_up = 0
            backed_up_size = 0
            for i, file_path in enumerate(valid_files):
                try:
                    # 创建相对路径
                    relative_path = os.path.relpath(os.path.dirname(file_path), source_dir)
                    dest_folder = os.path.join(backup_dir, relative_path)
                    os.makedirs(dest_folder, exist_ok=True)
                    
                    # 复制文件
                    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
                    shutil.copy2(file_path, dest_path)
                    
                    backed_up += 1
                    backed_up_size += os.path.getsize(file_path)
                    
                    # 更新进度
                    progress = int((i + 1) / len(valid_files) * 100)
                    self.progress['value'] = progress
                    self.status_var.set(f"正在备份 {i+1}/{len(valid_files)} 文件 ({progress}%)")
                    
                    if (i + 1) % 10 == 0 or i == len(valid_files) - 1:
                        self.log_message(f"已备份 {i+1}/{len(valid_files)} 文件")
                        
                except Exception as e:
                    self.log_message(f"备份失败: {file_path} - {str(e)}")
            
            # 完成备份
            self.log_message(f"\n备份完成! 共备份 {backed_up} 个文件 ({self.format_size(backed_up_size)})")
            self.log_message(f"备份位置: {backup_dir}")
            self.status_var.set(f"备份完成! {backed_up} 个文件已备份")
            self.progress['value'] = 100
            
            # 保存备份历史
            self.backup_history.append({
                'timestamp': datetime.now(),
                'source': source_dir,
                'backup_dir': backup_dir,
                'file_count': backed_up,
                'total_size': backed_up_size
            })
            
            # 启用按钮
            self.backup_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log_message(f"备份过程中发生错误: {str(e)}")
            self.status_var.set("备份失败")
            self.backup_btn.config(state=tk.NORMAL)
            
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def open_backup_folder(self):
        if self.backup_history:
            last_backup = self.backup_history[-1]['backup_dir']
            if os.path.exists(last_backup):
                os.startfile(last_backup)
            else:
                messagebox.showwarning("警告", "备份目录不存在或已被移动")
        else:
            messagebox.showinfo("信息", "尚未进行任何备份")
            
    def show_help(self):
        help_text = """
        **使用指南User Manual**
          
        
        1. 选择源目录 - 包含要备份文件的文件夹
           copy from - select what folder you want backup
           If dont know where the original file saved, just enter " c:\ " ..
        2. 选择备份目录 - 备份文件将保存的位置
           copy to - save to where you want to save
        3. 选择要备份的文件类型（默认全选）
           Select what file type you want save - default is select all
        4. 点击"开始备份"按钮执行备份
           Click "Backup" to start backup
        
        功能特点：
        - 自动创建带时间戳的备份文件夹
        - 保留原始目录结构
        - 实时显示备份进度
        - 备份完成后可立即打开备份目录
        
        支持的文件格式：
        - Word文档 (.doc, .docx)
        - Excel表格 (.xls, .xlsx)
        - PDF文件 (.pdf)
        """
        messagebox.showinfo("帮助", help_text)
        
    @staticmethod
    def format_size(size_bytes):
        """将字节数转换为易读的大小表示"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    root = tk.Tk()
    app = FileBackupApp(root)
    root.mainloop()