import tkinter as tk
from tkinter import messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import os
import re
import sys
import subprocess
import cv2
import threading
from PIL import Image
import concurrent.futures
from functools import partial
import time

def numerical_sort(value):
    """用于文件名自然数字排序的辅助函数。"""
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    if len(parts) > 1:
        try:
            parts[1::2] = map(int, parts[1::2])
        except (ValueError, IndexError):
            return parts
    return parts

class BatchFileToolApp:
    def __init__(self, master):
        self.master = master
        # 更新了程序标题和版本号为1.2
        master.title("Lanny的工具箱 (V1.2)")

        # --- 窗口居中与尺寸设置 ---
        initial_width, initial_height = 800, 700
        screen_width, screen_height = master.winfo_screenwidth(), master.winfo_screenheight()
        center_x = int(screen_width / 2 - initial_width / 2)
        center_y = int(screen_height / 2 - initial_height / 2)
        master.geometry(f'{initial_width}x{initial_height}+{center_x}+{center_y}')
        master.resizable(True, True)
        master.minsize(750, 600)

        # --- 顶部导航栏 ---
        nav_frame = ttk.Frame(master, padding=(10, 5))
        nav_frame.pack(side=tk.TOP, fill=tk.X)
        self.nav_buttons = {
            "image_rename": ttk.Button(nav_frame, text="批量重命名图片", command=lambda: self.show_frame("image_rename")),
            "video_modify": ttk.Button(nav_frame, text="视频批量修改", command=lambda: self.show_frame("video_modify")),
            "txt_modify": ttk.Button(nav_frame, text="批量修改TXT文件", command=lambda: self.show_frame("txt_modify"))
        }
        for btn in self.nav_buttons.values():
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- 主内容区域 ---
        content_frame = ttk.Frame(master, padding=(0, 10))
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.frames = {
            "image_rename": self._create_image_rename_frame(content_frame),
            "video_modify": self._create_video_modify_frame(content_frame),
            "txt_modify": self._create_txt_modify_frame(content_frame)
        }
        
        self.current_frame = None
        self.show_frame("image_rename")

    def show_frame(self, frame_name):
        """显示指定框架并​更新导航按钮样式。"""
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(expand=True, fill=tk.BOTH)
        for name, button in self.nav_buttons.items():
            button.config(bootstyle="primary" if name == frame_name else "outline-secondary")

    def _build_rename_panel(self, parent, file_type_name, file_extensions):
        """可复用的文件重命名面板UI与逻辑。"""
        frame = ttk.Frame(parent, padding=(10, 5))
        frame.pack(expand=True, fill=tk.BOTH)
        
        folder_label = ttk.Label(frame, text=f"{file_type_name}文件夹:")
        folder_entry = ttk.Entry(frame)

        prefix_label = ttk.Label(frame, text="新文件名前缀 (可选):")
        prefix_entry = ttk.Entry(frame)

        # 后缀输入框
        suffix_label = ttk.Label(frame, text="新文件名后缀 (可选):")
        suffix_entry = ttk.Entry(frame)

        # 标签文本，使其表示数字部分的总长度
        zeros_label = ttk.Label(frame, text="数字部分总长度 (例如: 3 -> 001, 010, 100):")
        # 默认值改为 3，更符合总长度的含义
        zeros_spinbox = ttk.Spinbox(frame, from_=0, to=10, width=8); zeros_spinbox.set("3")

        start_label = ttk.Label(frame, text="起始序号:")
        start_spinbox = ttk.Spinbox(frame, from_=0, to=99999, width=8); start_spinbox.set("1")

        def browse_folder():
            folder_selected = filedialog.askdirectory()
            if folder_selected: folder_entry.delete(0, tk.END); folder_entry.insert(0, folder_selected)
        browse_button = ttk.Button(frame, text="浏览...", command=browse_folder, bootstyle="secondary")
        
        def execute_rename():
            folder = folder_entry.get()
            if not os.path.isdir(folder): Messagebox.show_error(f"请输入一个有效的{file_type_name}文件夹路径。", "路径错误"); return
            
            prefix = prefix_entry.get()
            suffix = suffix_entry.get() # 获取后缀

            try:
                # 获取数字部分总长度，而不是前导零数量
                total_number_length = int(zeros_spinbox.get())
                if total_number_length < 0:
                    Messagebox.show_error("数字部分总长度不能为负数。", "输入错误"); return

                start_number = int(start_spinbox.get())
                if start_number < 0:
                    Messagebox.show_error("起始序号不能为负数。", "输入错误"); return
            except ValueError:
                Messagebox.show_error("数字部分总长度和起始序号必须是有效的数字。", "输入错误"); return
            
            try:
                files = sorted([f for f in os.listdir(folder) if f.lower().endswith(file_extensions)], key=numerical_sort)
            except Exception as e: Messagebox.show_error(f"读取文件列表时出错: {e}", "读取错误"); return
            if not files: Messagebox.show_info(f"在指定文件夹中未找到支持的{file_type_name}文件。", "未找到文件"); return
            
            temp_suffix_ext = ".renametemp" # 临时后缀，用于原子操作
            mappings = []
            
            for i, filename in enumerate(files):
                _, extension = os.path.splitext(filename)
                # 根据新的数字部分总长度生成数字部分
                numerical_part = str(start_number + i).zfill(total_number_length)
                # 包含前缀、数字部分、后缀和原始扩展名
                new_name = f"{prefix}{numerical_part}{suffix}{extension}"
                mappings.append({'old': os.path.join(folder, filename), 'new': os.path.join(folder, new_name)})
            
            all_old_paths = {m['old'] for m in mappings}
            for m in mappings:
                # 检查新文件名是否与现有文件（且不是本次重命名操作中的文件）冲突
                if os.path.exists(m['new']) and m['new'] not in all_old_paths:
                    Messagebox.show_error(f"操作中止：新文件名 '{os.path.basename(m['new'])}' 已存在，且不是本次操作中的文件。", "命名冲突"); return

            try:
                # 第一步：将所有待重命名的文件改名为临时名称
                for m in mappings:
                    os.rename(m['old'], m['old'] + temp_suffix_ext)
                
                # 第二步：将临时名称改回最终名称
                for m in mappings:
                    os.rename(m['old'] + temp_suffix_ext, m['new'])
            except Exception as e:
                Messagebox.show_error(f"重命名过程中出错: {e}。请检查文件夹并手动恢复带'{temp_suffix_ext}'后缀的文件。", "操作失败"); return
            Messagebox.show_info(f"成功重命名 {len(mappings)} 个{file_type_name}文件。", "操作成功")

        rename_button = ttk.Button(frame, text=f"开始重命名{file_type_name}", command=execute_rename, bootstyle="success")
        
        frame.columnconfigure(1, weight=1)
        # 布局调整以适应新增的后缀输入框
        folder_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        folder_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        browse_button.grid(row=0, column=2, sticky="e", padx=5, pady=10)

        prefix_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)
        prefix_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=10)

        suffix_label.grid(row=2, column=0, sticky="w", padx=5, pady=10) # 新增后缀行的布局
        suffix_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=10)

        zeros_label.grid(row=3, column=0, sticky="w", padx=5, pady=10) # 行数从2变为3
        zeros_spinbox.grid(row=3, column=1, sticky="w", padx=5, pady=10)

        start_label.grid(row=4, column=0, sticky="w", padx=5, pady=10) # 行数从3变为4
        start_spinbox.grid(row=4, column=1, sticky="w", padx=5, pady=10)

        rename_button.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=(20,10), ipady=5) # 行数从4变为5
        
    def _create_image_rename_frame(self, parent):
        frame = ttk.Frame(parent)
        container = ttk.LabelFrame(frame, text="图片重命名设置", padding=(10, 5))
        container.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self._build_rename_panel(container, "图片", ('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        return frame

    # 将视频重命名改为视频批量修改框架，类似TXT批量修改
    def _create_video_modify_frame(self, parent):
        frame = ttk.Frame(parent, padding=(5, 0))
        notebook = ttk.Notebook(frame)
        notebook.pack(expand=True, fill=tk.BOTH, pady=5)
        
        rename_tab = ttk.Frame(notebook)
        extract_frames_tab = ttk.Frame(notebook)
        
        notebook.add(rename_tab, text="批量重命名")
        notebook.add(extract_frames_tab, text="批量拆帧")
        
        self._build_rename_panel(rename_tab, "视频", ('.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.m4v', '.3gp'))
        self._build_extract_frames_tab(extract_frames_tab)
        
        return frame

    def _build_extract_frames_tab(self, parent_tab):
        """创建视频拆帧标签页"""
        folder_frame = ttk.Frame(parent_tab, padding=(5, 5))
        folder_frame.pack(side=tk.TOP, fill=tk.X)
        folder_label = ttk.Label(folder_frame, text="视频文件夹:")
        folder_entry = ttk.Entry(folder_frame)
        
        # 创建分割窗口
        paned_window = ttk.PanedWindow(parent_tab, orient=tk.HORIZONTAL)
        paned_window.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # 左侧视频列表
        list_frame = ttk.Frame(paned_window, padding=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        select_all_var = tk.BooleanVar()
        select_all_check = ttk.Checkbutton(list_frame, text="全选/全不选", variable=select_all_var, bootstyle="primary")
        select_all_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        # 视频文件列表
        video_tree = ttk.Treeview(list_frame, columns=("checked", "filename"), show="headings", selectmode="none")
        video_tree.heading("checked", text="")
        video_tree.heading("filename", text="视频文件名")
        video_tree.column("checked", width=40, stretch=tk.NO, anchor="center")
        video_tree.column("filename", anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=video_tree.yview)
        video_tree.configure(yscrollcommand=scrollbar.set)
        
        video_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        paned_window.add(list_frame, weight=1)
        
        # 右侧设置面板
        settings_frame = ttk.Frame(paned_window, padding=5)
        settings_frame.columnconfigure(0, weight=1)
        paned_window.add(settings_frame, weight=2)
        
        # 设置面板中的控件
        output_frame = ttk.LabelFrame(settings_frame, text="输出设置", padding=(10, 5))
        output_frame.pack(fill=tk.X, pady=5)
        
        output_folder_label = ttk.Label(output_frame, text="输出根文件夹 (可选):")
        output_folder_entry = ttk.Entry(output_frame)
        output_folder_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        output_folder_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        def browse_output_folder():
            folder = filedialog.askdirectory()
            if folder:
                output_folder_entry.delete(0, tk.END)
                output_folder_entry.insert(0, folder)
                
        output_browse_button = ttk.Button(output_frame, text="浏览...", command=browse_output_folder, bootstyle="secondary")
        output_browse_button.grid(row=0, column=2, sticky="e", padx=5, pady=10)
        
        output_frame.columnconfigure(1, weight=1)
        
        # 提取帧的命名设置
        naming_frame = ttk.LabelFrame(settings_frame, text="帧图片命名设置", padding=(10, 5))
        naming_frame.pack(fill=tk.X, pady=5)
        naming_frame.columnconfigure(1, weight=1)
        
        prefix_label = ttk.Label(naming_frame, text="图片名前缀 (可选):")
        prefix_entry = ttk.Entry(naming_frame)
        
        suffix_label = ttk.Label(naming_frame, text="图片名后缀 (可选):")
        suffix_entry = ttk.Entry(naming_frame)
        
        zeros_label = ttk.Label(naming_frame, text="数字部分总长度:")
        zeros_spinbox = ttk.Spinbox(naming_frame, from_=0, to=10, width=8)
        zeros_spinbox.set("6")  # 视频帧通常较多，默认长度设为6
        
        prefix_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        prefix_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=10)
        
        suffix_label.grid(row=1, column=0, sticky="w", padx=5, pady=10)
        suffix_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=10)
        
        zeros_label.grid(row=2, column=0, sticky="w", padx=5, pady=10)
        zeros_spinbox.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        
        # 提取间隔设置
        interval_frame = ttk.LabelFrame(settings_frame, text="提取间隔设置", padding=(10, 5))
        interval_frame.pack(fill=tk.X, pady=5)
        interval_frame.columnconfigure(1, weight=1)
        
        interval_label = ttk.Label(interval_frame, text="每隔多少帧提取一帧:")
        interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=1000, width=8)
        interval_spinbox.set("1")  # 默认提取每一帧
        
        interval_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        interval_spinbox.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        # 图片格式设置
        format_frame = ttk.LabelFrame(settings_frame, text="图片格式设置", padding=(10, 5))
        format_frame.pack(fill=tk.X, pady=5)
        
        format_var = tk.StringVar(value="jpg")
        jpg_radio = ttk.Radiobutton(format_frame, text="JPG", variable=format_var, value="jpg")
        png_radio = ttk.Radiobutton(format_frame, text="PNG", variable=format_var, value="png")
        
        jpg_radio.pack(side=tk.LEFT, padx=20, pady=10)
        png_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 添加FFmpeg加速选项
        use_ffmpeg_var = tk.BooleanVar(value=True)  # 默认启用FFmpeg
        use_ffmpeg_check = ttk.Checkbutton(
            settings_frame, 
            text="使用FFmpeg加速(如果已安装)", 
            variable=use_ffmpeg_var,
            bootstyle="info-round-toggle"
        )
        use_ffmpeg_check.pack(fill=tk.X, pady=5)
        
        # 添加并行处理选项
        parallel_processing_frame = ttk.LabelFrame(settings_frame, text="并行处理设置", padding=(10, 5))
        parallel_processing_frame.pack(fill=tk.X, pady=5)
        
        use_parallel_var = tk.BooleanVar(value=True)  # 默认启用并行处理
        use_parallel_check = ttk.Checkbutton(
            parallel_processing_frame, 
            text="启用并行处理", 
            variable=use_parallel_var,
            bootstyle="info-round-toggle"
        )
        use_parallel_check.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        
        max_workers_label = ttk.Label(parallel_processing_frame, text="最大线程数:")
        max_workers_spinbox = ttk.Spinbox(
            parallel_processing_frame, 
            from_=1, 
            to=16,  # 最多16个线程，防止系统过载
            width=4
        )
        max_workers_spinbox.set(min(os.cpu_count() or 4, 8))  # 默认使用CPU核心数，最多8个
        max_workers_label.pack(side=tk.LEFT, padx=(20, 5), pady=5)
        max_workers_spinbox.pack(side=tk.LEFT, pady=5)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(settings_frame, text="进度", padding=(10, 5))
        progress_frame.pack(fill=tk.X, pady=5)
        
        progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, 
                                      length=100, mode='determinate', 
                                      variable=progress_var)
        progress_bar.pack(fill=tk.X, padx=10, pady=10)
        
        progress_label = ttk.Label(progress_frame, text="准备就绪")
        progress_label.pack(padx=10, pady=(0, 10))
        
        # 获取选中的视频文件
        def get_checked_videos():
            checked_videos = []
            for item_id in video_tree.get_children():
                if 'checked' in video_tree.item(item_id, "tags"):
                    filename = video_tree.item(item_id, "values")[1]
                    checked_videos.append(filename)
            return checked_videos
        
        # 切换文件选中状态
        def toggle_check(event):
            item_id = video_tree.identify_row(event.y)
            if not item_id: return
            
            # 只在点击第一列(勾选框列)时切换状态
            column = video_tree.identify_column(event.x)
            if column != "#1":
                return
                
            tags = list(video_tree.item(item_id, "tags"))
            is_checked = 'checked' in tags
            
            # 切换状态
            if is_checked:
                if 'checked' in tags: tags.remove('checked')
                if 'unchecked' not in tags: tags.append('unchecked')
                new_char = "🔲"
            else:
                if 'unchecked' in tags: tags.remove('unchecked')
                if 'checked' not in tags: tags.append('checked')
                new_char = "✅"
                
            filename = video_tree.item(item_id, "values")[1]
            video_tree.item(item_id, tags=tuple(tags), values=(new_char, filename))
            
            # 更新全选框状态
            all_items = video_tree.get_children()
            if not all_items: 
                select_all_var.set(False)
            else: 
                select_all_var.set(all('checked' in video_tree.item(i, "tags") for i in all_items))
                
            update_extract_button_state()
                
        video_tree.bind("<Button-1>", toggle_check)
        
        # 全选/全不选
        def toggle_select_all():
            is_checked = select_all_var.get()
            for item_id in video_tree.get_children():
                tags = list(video_tree.item(item_id, "tags"))
                
                # 清除现有状态
                if 'checked' in tags: tags.remove('checked')
                if 'unchecked' in tags: tags.remove('unchecked')
                
                # 设置新状态
                if is_checked:
                    tags.append('checked')
                    new_char = "✅"
                else:
                    tags.append('unchecked')
                    new_char = "🔲"
                    
                filename = video_tree.item(item_id, "values")[1]
                video_tree.item(item_id, tags=tuple(tags), values=(new_char, filename))
                
            update_extract_button_state()
            
        select_all_check.config(command=toggle_select_all)
        
        # 更新按钮状态
        def update_extract_button_state():
            extract_button.config(state=tk.NORMAL if get_checked_videos() else tk.DISABLED)
        
        # 填充视频文件列表
        def populate_video_list():
            video_tree.delete(*video_tree.get_children())
            folder = folder_entry.get()
            
            if not os.path.isdir(folder): return
            
            try:
                video_extensions = ('.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.m4v', '.3gp')
                videos = sorted([f for f in os.listdir(folder) if f.lower().endswith(video_extensions)], key=numerical_sort)
                
                for video in videos:
                    video_tree.insert("", tk.END, values=("🔲", video), tags=('unchecked',))
                    
            except Exception as e:
                Messagebox.show_error(f"读取视频列表失败: {e}", "错误")
                
            select_all_var.set(False)
            update_extract_button_state()
            
        # 浏览文件夹按钮
        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                folder_entry.delete(0, tk.END)
                folder_entry.insert(0, folder)
                populate_video_list()
                
        browse_button = ttk.Button(folder_frame, text="浏览...", command=browse_folder, bootstyle="secondary")
        refresh_button = ttk.Button(folder_frame, text="刷新列表", command=populate_video_list, bootstyle="info")
        
        folder_label.pack(side=tk.LEFT, padx=(0, 5))
        folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        browse_button.pack(side=tk.LEFT, padx=5)
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 使用FFmpeg提取帧
        def extract_frames_with_ffmpeg(video_path, output_dir, prefix, suffix, total_number_length, frame_interval, img_format):
            try:
                # 检查FFmpeg是否可用
                try:
                    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                except:
                    return False, "FFmpeg未安装或不可用"
                    
                # 构建FFmpeg命令
                output_pattern = f"{output_dir}/{prefix}%0{total_number_length}d{suffix}.{img_format}"
                
                # 使用FFmpeg的fps过滤器来控制帧间隔
                fps_filter = f"fps=1/{frame_interval}"
                if frame_interval == 1:
                    fps_filter = "fps=source"  # 如果是每一帧，就使用源视频帧率
                    
                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-vf", fps_filter,
                    "-q:v", "2" if img_format.lower() == "jpg" else "0",
                    "-start_number", "0",
                    output_pattern
                ]
                    
                # 执行命令
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                    
                if process.returncode != 0:
                    return False, f"FFmpeg错误: {stderr.decode()}"
                    
                # 计算提取的帧数
                extracted_files = [f for f in os.listdir(output_dir) if f.endswith(f".{img_format}")]
                return True, len(extracted_files)
            except Exception as e:
                return False, f"FFmpeg处理出错: {str(e)}"
        
        # 使用OpenCV提取帧
        def extract_frames_with_opencv(video_path, output_dir, prefix, suffix, total_number_length, frame_interval, img_format, silent=False):
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    if not silent:
                        progress_label.config(text=f"无法打开视频")
                    return 0
                
                # 获取视频属性
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # 更新进度条范围（仅在非静默模式）
                if not silent:
                    progress_bar.config(maximum=total_frames)
                
                # 优化：直接设置帧位置而不是读取所有帧
                frame_index = 0
                frames_saved = 0
                
                while frame_index < total_frames:
                    # 直接设置到指定帧位置，跳过中间帧
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                        
                    # 生成文件名并保存
                    frame_number = str(frames_saved).zfill(total_number_length)
                    frame_name = f"{prefix}{frame_number}{suffix}.{img_format}"
                    frame_path = os.path.join(output_dir, frame_name)
                    
                    # 确保保存成功
                    if img_format.lower() == 'jpg':
                        success = cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    else:
                        success = cv2.imwrite(frame_path, frame)
                        
                    if not success:
                        # 尝试使用PIL保存
                        try:
                            # 转换BGR到RGB
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img = Image.fromarray(rgb_frame)
                            img.save(frame_path, quality=95 if img_format.lower() == 'jpg' else None)
                            success = True
                        except Exception as e:
                            if not silent:
                                print(f"无法保存帧 {frame_name}: {e}")
                            
                    if success:
                        frames_saved += 1
                    
                    # 更新进度和显示（仅在非静默模式）
                    frame_index += frame_interval
                    if not silent:
                        progress_var.set(min(frame_index, total_frames))
                        progress_label.config(text=f"正在处理: 帧 {min(frame_index, total_frames)}/{total_frames}")
                        
                        # 让UI有机会更新
                        if frames_saved % 5 == 0:
                            self.master.update_idletasks()
                
                # 关闭视频
                cap.release()
                return frames_saved
            except Exception as e:
                if not silent:
                    progress_label.config(text=f"OpenCV处理出错: {e}")
                return 0
        
        # 执行视频拆帧功能
        def extract_frames():
            videos = get_checked_videos()
            if not videos:
                return
                
            # 获取设置
            video_folder = folder_entry.get()
            output_root = output_folder_entry.get() or video_folder
            prefix = prefix_entry.get()
            suffix = suffix_entry.get()
            total_number_length = int(zeros_spinbox.get())
            frame_interval = int(interval_spinbox.get())
            img_format = format_var.get()
            use_ffmpeg = use_ffmpeg_var.get()
            use_parallel = use_parallel_var.get()
            
            # 创建输出根目录
            if not os.path.exists(output_root):
                try:
                    os.makedirs(output_root)
                except Exception as e:
                    Messagebox.show_error(f"创建输出目录失败: {e}", "错误")
                    return
            
            # 禁用按钮，防止重复操作
            extract_button.config(state=tk.DISABLED)
            
            # 在单独线程中运行，防止UI卡顿
            def run_extraction():
                total_videos = len(videos)
                total_frames_extracted = 0
                videos_processed = 0
                start_time = time.time()
                
                try:
                    # 准备视频处理函数
                    def process_video(video_name):
                        video_path = os.path.join(video_folder, video_name)
                        
                        # 创建与视频同名的目录
                        video_name_without_ext = os.path.splitext(video_name)[0]
                        output_dir = os.path.join(output_root, video_name_without_ext)
                        
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        frames_saved = 0
                        
                        # 使用FFmpeg或OpenCV处理
                        if use_ffmpeg:
                            success, result = extract_frames_with_ffmpeg(
                                video_path, output_dir, prefix, suffix, 
                                total_number_length, frame_interval, img_format
                            )
                            
                            if success:
                                frames_saved = result
                            else:
                                # FFmpeg失败则尝试OpenCV
                                frames_saved = extract_frames_with_opencv(
                                    video_path, output_dir, prefix, suffix, 
                                    total_number_length, frame_interval, img_format,
                                    silent=True  # 静默模式，不更新UI
                                )
                        else:
                            frames_saved = extract_frames_with_opencv(
                                video_path, output_dir, prefix, suffix, 
                                total_number_length, frame_interval, img_format,
                                silent=True
                            )
                        
                        return video_name, frames_saved
                    
                    # 并行处理或串行处理
                    if use_parallel:
                        try:
                            max_workers = int(max_workers_spinbox.get())
                            if max_workers < 1:
                                max_workers = 1
                        except:
                            max_workers = min(os.cpu_count() or 4, 8)
                        
                        progress_label.config(text=f"并行处理中，使用 {max_workers} 个线程...")
                        
                        # 使用线程池进行并行处理
                        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                            future_to_video = {executor.submit(process_video, video): video for video in videos}
                            
                            for i, future in enumerate(concurrent.futures.as_completed(future_to_video)):
                                video_name, frames = future.result()
                                total_frames_extracted += frames
                                videos_processed += 1
                                
                                # 更新进度
                                progress_var.set(int((videos_processed / total_videos) * 100))
                                progress_label.config(text=f"已处理: {videos_processed}/{total_videos} 视频")
                                
                                # 让UI更新
                                self.master.update_idletasks()
                    else:
                        # 串行处理
                        for video_name in videos:
                            video_path = os.path.join(video_folder, video_name)
                            
                            # 创建与视频同名的目录
                            video_name_without_ext = os.path.splitext(video_name)[0]
                            output_dir = os.path.join(output_root, video_name_without_ext)
                            
                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)
                            
                            progress_label.config(text=f"正在处理: {video_name}")
                            
                            # 使用FFmpeg或OpenCV处理
                            if use_ffmpeg:
                                success, result = extract_frames_with_ffmpeg(
                                    video_path, output_dir, prefix, suffix, 
                                    total_number_length, frame_interval, img_format
                                )
                                
                                if success:
                                    frames_saved = result
                                    total_frames_extracted += frames_saved
                                    progress_var.set(100)  # 
                                else:
                                    # FFmpeg失败则尝试OpenCV
                                    frames_saved = extract_frames_with_opencv(
                                        video_path, output_dir, prefix, suffix, 
                                        total_number_length, frame_interval, img_format,
                                        silent=False  # 非静默模式，更新UI
                                    )
                                    total_frames_extracted += frames_saved
                            else:
                                frames_saved = extract_frames_with_opencv(
                                    video_path, output_dir, prefix, suffix, 
                                    total_number_length, frame_interval, img_format,
                                    silent=False
                                )
                                total_frames_extracted += frames_saved
                            
                            videos_processed += 1
                            progress_var.set(int((videos_processed / total_videos) * 100))
                            progress_label.config(text=f"已处理: {videos_processed}/{total_videos} 视频")
                            
                            # 让UI更新
                            self.master.update_idletasks()
                    
                    elapsed_time = time.time() - start_time
                    progress_label.config(text=f"完成! 从 {videos_processed} 个视频中共提取了 {total_frames_extracted} 帧，耗时 {elapsed_time:.2f} 秒")
                    
                except Exception as e:
                    progress_label.config(text=f"处理过程中出错: {e}")
                finally:
                    # 恢复按钮状态
                    extract_button.config(state=tk.NORMAL)
            
            # 启动线程
            threading.Thread(target=run_extraction, daemon=True).start()
            
        # 开始提取按钮
        extract_button = ttk.Button(settings_frame, text="提取选中视频的帧", command=extract_frames, bootstyle="success", state=tk.DISABLED)
        extract_button.pack(fill=tk.X, ipady=8, pady=(15, 5))

    def _create_txt_modify_frame(self, parent):
        frame = ttk.Frame(parent, padding=(5, 0))
        notebook = ttk.Notebook(frame)
        notebook.pack(expand=True, fill=tk.BOTH, pady=5)
        
        create_tab = ttk.Frame(notebook)
        modify_delete_tab = ttk.Frame(notebook)
        
        notebook.add(create_tab, text="批量创建TXT")
        notebook.add(modify_delete_tab, text="批量修改/删除")
        
        self._build_create_tab(create_tab)
        self._build_modify_delete_tab(modify_delete_tab)
        
        return frame

    def _build_create_tab(self, parent_tab):
        settings_frame = ttk.LabelFrame(parent_tab, text="TXT创建设置", padding=(10, 5))
        settings_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        settings_frame.columnconfigure(1, weight=1)
        
        folder_label, folder_entry = ttk.Label(settings_frame, text="保存到文件夹:"), ttk.Entry(settings_frame)
        prefix_label, prefix_entry = ttk.Label(settings_frame, text="文件名前缀 (可选):"), ttk.Entry(settings_frame)
        suffix_label, suffix_entry = ttk.Label(settings_frame, text="文件名后缀 (可选):"), ttk.Entry(settings_frame)
        
        # 【修改】标签文本，表示数字部分的总长度
        zeros_label = ttk.Label(settings_frame, text="数字部分总长度 (例如: 3 -> 001, 010, 100):")
        zeros_spinbox = ttk.Spinbox(settings_frame, from_=0, to=10, width=8); zeros_spinbox.set("3")

        start_label, start_spinbox = ttk.Label(settings_frame, text="起始序号:"), ttk.Spinbox(settings_frame, from_=0, to=99999, width=8)
        start_spinbox.set("1")

        count_label, count_spinbox = ttk.Label(settings_frame, text="创建数量:"), ttk.Spinbox(settings_frame, from_=1, to=99999, width=8)
        count_spinbox.set("10")

        content_label = ttk.Label(settings_frame, text="文件内容 (可选, 每个文件会保存相同内容):")
        content_text = scrolledtext.ScrolledText(settings_frame, width=40, height=8, wrap=tk.WORD, undo=True)

        def browse_folder():
            folder_selected = filedialog.askdirectory()
            if folder_selected: folder_entry.delete(0, tk.END); folder_entry.insert(0, folder_selected)
        browse_button = ttk.Button(settings_frame, text="浏览...", command=browse_folder, bootstyle="secondary")

        def execute_create():
            folder_path = folder_entry.get()
            if not os.path.isdir(folder_path): Messagebox.show_error("请输入一个有效的文件夹路径。", "路径错误"); return

            prefix = prefix_entry.get()
            suffix = suffix_entry.get()  # 获取后缀
            
            try:
                total_number_length = int(zeros_spinbox.get())
                if total_number_length < 0:
                    Messagebox.show_error("数字部分总长度不能为负数。", "输入错误"); return

                start_number = int(start_spinbox.get())
                if start_number < 0:
                    Messagebox.show_error("起始序号不能为负数。", "输入错误"); return

                count = int(count_spinbox.get())
                if count <= 0:
                    Messagebox.show_error("创建数量必须大于零。", "输入错误"); return
            except ValueError:
                Messagebox.show_error("数字部分总长度、起始序号和创建数量必须是有效的数字。", "输入错误"); return

            content = content_text.get("1.0", tk.END).rstrip('\n')  # 去除内容末尾的换行符
            created_files = 0
            skipped_files = 0

            for i in range(count):
                number = start_number + i
                numerical_part = str(number).zfill(total_number_length)
                filename = f"{prefix}{numerical_part}{suffix}.txt"
                filepath = os.path.join(folder_path, filename)

                if os.path.exists(filepath):
                    skipped_files += 1
                    continue

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_files += 1
                except Exception as e:
                    Messagebox.show_error(f"创建文件 {filename} 时出错: {e}", "创建错误")
                    return

            result_message = f"成功创建了 {created_files} 个TXT文件"
            if skipped_files > 0:
                result_message += f"，跳过了 {skipped_files} 个已存在的文件"
            Messagebox.show_info(result_message + "。", "操作成功")

        create_button = ttk.Button(settings_frame, text="开始创建TXT文件", command=execute_create, bootstyle="success")

        # 使用网格布局让控件排列更整齐
        layout = [
            (folder_label, folder_entry, browse_button),
            (prefix_label, prefix_entry),
            (suffix_label, suffix_entry),
            (zeros_label, zeros_spinbox),
            (start_label, start_spinbox),
            (count_label, count_spinbox),
            (content_label,),
            (content_text,),
            (create_button,)
        ]

        for r, widgets in enumerate(layout):
            pady, ipady = (8, 0), 0
            if r == 7: pady, ipady = ((15, 5), 5) # 按钮行的行号变为7
            
            if len(widgets) == 3:
                widgets[0].grid(row=r, column=0, sticky='w', padx=5, pady=pady)
                widgets[1].grid(row=r, column=1, sticky='ew', padx=5, pady=pady)
                widgets[2].grid(row=r, column=2, sticky='e', padx=5, pady=pady)
            elif len(widgets) == 2:
                widgets[0].grid(row=r, column=0, sticky='w', padx=5, pady=pady)
                widgets[1].grid(row=r, column=1, columnspan=2, sticky='ew', padx=5, pady=pady)
            else:
                widgets[0].grid(row=r, column=0, columnspan=3, sticky='ew', padx=5, pady=pady, ipady=ipady)

    def _build_modify_delete_tab(self, parent_tab):
        folder_frame = ttk.Frame(parent_tab, padding=(5, 5)); folder_frame.pack(side=tk.TOP, fill=tk.X)
        folder_label = ttk.Label(folder_frame, text="TXT文件夹:"); folder_entry = ttk.Entry(folder_frame)
        
        paned_window = ttk.PanedWindow(parent_tab, orient=tk.HORIZONTAL)
        paned_window.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        list_frame = ttk.Frame(paned_window, padding=5)
        list_frame.columnconfigure(0, weight=1); list_frame.rowconfigure(1, weight=1)
        
        select_all_var = tk.BooleanVar()
        select_all_check = ttk.Checkbutton(list_frame, text="全选/全不选", variable=select_all_var, bootstyle="primary")
        select_all_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        file_tree = ttk.Treeview(list_frame, columns=("checked", "filename"), show="headings", selectmode="none")
        file_tree.heading("checked", text=""); file_tree.heading("filename", text="文件名")
        file_tree.column("checked", width=40, stretch=tk.NO, anchor="center"); file_tree.column("filename", anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=file_tree.yview)
        file_tree.configure(yscrollcommand=scrollbar.set)
        
        file_tree.grid(row=1, column=0, sticky="nsew"); scrollbar.grid(row=1, column=1, sticky="ns")
        paned_window.add(list_frame, weight=1)

        actions_frame = ttk.Frame(paned_window, padding=5); actions_frame.columnconfigure(0, weight=1)
        paned_window.add(actions_frame, weight=2)

        # 获取选中文件的函数
        def get_checked_files():
            checked_files = []
            for item_id in file_tree.get_children():
                if 'checked' in file_tree.item(item_id, "tags"):
                    filename = file_tree.item(item_id, "values")[1]
                    checked_files.append(filename)
            return checked_files

        def update_buttons_state():
            checked_count = len(get_checked_files())
            state = tk.NORMAL if checked_count > 0 else tk.DISABLED
            view_edit_button.config(state=tk.NORMAL if checked_count == 1 else tk.DISABLED)
            open_button.config(state=state)
            delete_button.config(state=state)
            replace_button.config(state=state)
            prepend_button.config(state=state)
            append_button.config(state=state)

        # 改进文件选择功能
        def toggle_check(event):
            item_id = file_tree.identify_row(event.y)
            if not item_id: return
            
            # 只在点击第一列(勾选框列)时切换状态
            column = file_tree.identify_column(event.x)
            if column != "#1":
                return
                
            tags = list(file_tree.item(item_id, "tags"))
            is_checked = 'checked' in tags
            
            # 切换状态
            if is_checked:
                if 'checked' in tags: tags.remove('checked')
                if 'unchecked' not in tags: tags.append('unchecked')
                new_char = "🔲"
            else:
                if 'unchecked' in tags: tags.remove('unchecked')
                if 'checked' not in tags: tags.append('checked')
                new_char = "✅"
                
            filename = file_tree.item(item_id, "values")[1]
            file_tree.item(item_id, tags=tuple(tags), values=(new_char, filename))
            
            # 更新全选框状态
            all_items = file_tree.get_children()
            if not all_items: 
                select_all_var.set(False)
            else: 
                select_all_var.set(all('checked' in file_tree.item(i, "tags") for i in all_items))
                
            update_buttons_state()

        file_tree.bind("<Button-1>", toggle_check)

        def toggle_select_all():
            is_checked = select_all_var.get()
            for item_id in file_tree.get_children():
                tags = list(file_tree.item(item_id, "tags"))
                
                # 清除现有状态
                if 'checked' in tags: tags.remove('checked')
                if 'unchecked' in tags: tags.remove('unchecked')
                
                # 设置新状态
                if is_checked:
                    tags.append('checked')
                    new_char = "✅"
                else:
                    tags.append('unchecked')
                    new_char = "🔲"
                    
                filename = file_tree.item(item_id, "values")[1]
                file_tree.item(item_id, tags=tuple(tags), values=(new_char, filename))
                
            update_buttons_state()
            
        select_all_check.config(command=toggle_select_all)
        
        def populate_file_list():
            folder = folder_entry.get()
            file_tree.delete(*file_tree.get_children())
            if not os.path.isdir(folder): return
            try:
                files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.txt')], key=numerical_sort)
                for file in files:
                    file_tree.insert("", tk.END, values=("🔲", file), tags=('unchecked',))
            except Exception as e: Messagebox.show_error(f"读取文件列表失败: {e}", "错误")
            select_all_var.set(False); update_buttons_state()

        browse_button = ttk.Button(folder_frame, text="浏览...", command=lambda: [folder_entry.delete(0, tk.END), folder_entry.insert(0, filedialog.askdirectory() or folder_entry.get()), populate_file_list()], bootstyle="secondary")
        refresh_button = ttk.Button(folder_frame, text="刷新列表", command=populate_file_list, bootstyle="info")
        folder_label.pack(side=tk.LEFT, padx=(0, 5)); folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X); browse_button.pack(side=tk.LEFT, padx=5); refresh_button.pack(side=tk.LEFT, padx=(0, 5))

        def view_edit_file():
            selected_files = get_checked_files()
            if len(selected_files) != 1: return
            filename = selected_files[0]
            filepath = os.path.join(folder_entry.get(), filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
            except Exception as e: Messagebox.show_error(f"无法读取文件 '{filename}':\n{e}", "读取失败"); return

            editor_window = tk.Toplevel(self.master)
            editor_window.title(f"查看/编辑 - {filename}"); editor_window.geometry("600x500")
            editor_window.transient(self.master); editor_window.grab_set()

            text_area = scrolledtext.ScrolledText(editor_window, wrap=tk.WORD, undo=True)
            text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            text_area.insert(tk.END, content)

            def save_changes():
                new_content = text_area.get("1.0", tk.END)
                try:
                    with open(filepath, 'w', encoding='utf-8') as f: f.write(new_content)
                    editor_window.destroy()
                    Messagebox.show_info("文件已成功保存。", "保存成功")
                except Exception as e: Messagebox.show_error(f"无法保存文件:\n{e}", "保存失败", parent=editor_window)
            
            button_frame = ttk.Frame(editor_window); button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            save_btn = ttk.Button(button_frame, text="保存修改", command=save_changes, bootstyle="success"); save_btn.pack(side=tk.RIGHT)
            close_btn = ttk.Button(button_frame, text="关闭", command=editor_window.destroy, bootstyle="secondary"); close_btn.pack(side=tk.RIGHT, padx=10)

        def open_selected_files():
            files_to_open = get_checked_files()
            if not files_to_open: return

            folder = folder_entry.get()
            errors = []
            for filename in files_to_open:
                filepath = os.path.join(folder, filename)
                try:
                    if sys.platform == "win32":
                        os.startfile(filepath)
                    elif sys.platform == "darwin": # macOS
                        subprocess.run(['open', filepath], check=True)
                    else: # Linux and other Unix-like
                        subprocess.run(['xdg-open', filepath], check=True)
                except Exception as e:
                    errors.append(f"打开 {filename} 时发生错误: {e}")
            
            if errors:
                Messagebox.show_error("打开部分或全部文件时出错：\n" + "\n".join(errors), "打开错误")

        view_edit_button = ttk.Button(actions_frame, text="查看/编辑勾选的文件 (仅1个)", command=view_edit_file, state=tk.DISABLED, bootstyle="info-outline")
        view_edit_button.pack(fill=tk.X, ipady=4, pady=(0,5))
        
        open_button = ttk.Button(actions_frame, text="用默认程序打开勾选的文件", command=open_selected_files, state=tk.DISABLED, bootstyle="info-outline")
        open_button.pack(fill=tk.X, ipady=4, pady=(0,10))

        delete_frame = ttk.LabelFrame(actions_frame, text="批量删除", padding=10); delete_frame.pack(fill=tk.X, pady=5)
        # 改进删除功能
        def delete_selected():
            files_to_delete = get_checked_files()
            if not files_to_delete: return
            
            if not Messagebox.show_question("确认删除", f"确定要永久删除这 {len(files_to_delete)} 个文件吗？", parent=self.master): return            
            deleted_count, errors = 0, []
            folder = folder_entry.get()
            for filename in files_to_delete:
                filepath = os.path.join(folder, filename)
                try: 
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e: 
                    errors.append(f"{filename}: {e}")
            
            if errors: Messagebox.show_error("删除时发生错误：\n" + "\n".join(errors), "删除失败")
            else: Messagebox.show_info(f"成功删除了 {deleted_count} 个文件。", "操作成功")
            
            # 删除完成后刷新文件列表
            populate_file_list()
            
        delete_button = ttk.Button(delete_frame, text="删除勾选的文件", command=delete_selected, bootstyle="danger", state=tk.DISABLED)
        delete_button.pack(fill=tk.X, ipady=4)

        # 改进内容修改功能
        def modify_content(mode):
            files_to_modify = get_checked_files()
            if not files_to_modify: return
            
            folder = folder_entry.get()
            modified_count = 0
            errors = []
            
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            add_text = add_text_widget.get("1.0", tk.END).rstrip('\n')
            
            try:
                for filename in files_to_modify:
                    filepath = os.path.join(folder, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            original_content = f.read()
                        
                        new_content = original_content
                        if mode == 'replace': 
                            new_content = original_content.replace(find_text, replace_text)
                        elif mode == 'prepend': 
                            new_content = add_text + '\n' + original_content
                        elif mode == 'append': 
                            new_content = original_content.rstrip('\n') + '\n' + add_text

                        if new_content != original_content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            modified_count += 1
                    except Exception as e:
                        errors.append(f"{filename}: {e}")
                        
                if errors:
                    Messagebox.show_error(f"处理部分文件时出错: \n" + "\n".join(errors), "处理错误")
                Messagebox.show_info(f"成功修改了 {modified_count} 个文件。", "操作成功")
            except Exception as e: 
                Messagebox.show_error(f"处理文件时出错: {e}", "操作失败")

        replace_frame = ttk.LabelFrame(actions_frame, text="查找与替换", padding=10); replace_frame.pack(fill=tk.X, pady=5)
        replace_frame.columnconfigure(1, weight=1)
        find_label = ttk.Label(replace_frame, text="查找:"); find_entry = ttk.Entry(replace_frame)
        replace_label = ttk.Label(replace_frame, text="替换为:"); replace_entry = ttk.Entry(replace_frame)
        replace_button = ttk.Button(replace_frame, text="对勾选的文件执行替换", command=lambda: modify_content('replace'), bootstyle="primary-outline", state=tk.DISABLED)
        find_label.grid(row=0, column=0, sticky="w", padx=5, pady=5); find_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        replace_label.grid(row=1, column=0, sticky="w", padx=5, pady=5); replace_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        replace_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(10,5), ipady=4)
        
        add_frame = ttk.LabelFrame(actions_frame, text="添加内容到文件", padding=10); add_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        add_frame.rowconfigure(0, weight=1); add_frame.columnconfigure(0, weight=1); add_frame.columnconfigure(1, weight=1)
        add_text_widget = tk.Text(add_frame, height=4, wrap=tk.WORD, undo=True)
        prepend_button = ttk.Button(add_frame, text="在文件头部添加", command=lambda: modify_content('prepend'), state=tk.DISABLED)
        append_button = ttk.Button(add_frame, text="在文件尾部添加", command=lambda: modify_content('append'), state=tk.DISABLED)
        add_text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        prepend_button.grid(row=1, column=0, sticky="ew", padx=(0,5), pady=5, ipady=4)
        append_button.grid(row=1, column=1, sticky="ew", padx=(5,0), pady=5, ipady=4)
        
        populate_file_list()

if __name__ == "__main__":
    # 使用一个现代化的 ttkbootstrap 主题
    root = ttk.Window(themename="litera")
    app = BatchFileToolApp(root)
    root.mainloop()
