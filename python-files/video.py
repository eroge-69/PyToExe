# 导入所需的模块
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os
import platform
import threading
# 导入拖拽功能库
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    messagebox.showerror("缺少依赖", "拖拽功能需要 'tkinterdnd2' 库。\n请在终端运行: pip install tkinterdnd2")
    exit()

class VideoTrimTool:
    """
    一个使用 Tkinter 构建的图形化视频处理工具，
    可以通过调用 FFmpeg 批量删除指定视频文件的片头部分。

    v1.4 更新:
    - 优化 FFmpeg 命令，使用 '-c copy' 复制所有流。
    - 对 MP4/MOV 文件自动添加 '-movflags +faststart' 优化网络播放。
    """
    def __init__(self, root):
        """
        初始化应用程序主窗口和核心组件。
        :param root: TkinterDnD 的根窗口实例。
        """
        self.root = root
        self.root.title("视频片头删除工具 (v1.4)")
        self.root.geometry("600x450")
        self.root.minsize(500, 400)

        self.VALID_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            messagebox.showerror("错误", "未找到 FFmpeg。\n请确保已正确安装 FFmpeg 并将其添加至系统环境变量(PATH)。")
            self.root.destroy()
            return

        self.selected_files = []
        self.processing_thread = None

        self.create_widgets()
        self._setup_drag_and_drop()
        
        self.update_status("就绪 (可拖拽文件到此窗口)")

    def _get_startup_info(self):
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

    def _check_ffmpeg(self):
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=True, startupinfo=self._get_startup_info()
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def create_widgets(self):
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        files_frame = ttk.LabelFrame(main_frame, text="已选择的文件 (可拖拽文件至此)", padding=10)
        files_frame.grid(row=0, column=0, sticky=tk.NSEW)
        files_frame.columnconfigure(0, weight=1)

        self.files_text = tk.Text(files_frame, height=10, wrap=tk.WORD, font=("Arial", 10), relief=tk.FLAT)
        self.files_text.grid(row=0, column=0, sticky=tk.NSEW)
        self.files_text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(files_frame, command=self.files_text.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.files_text.config(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, pady=(10, 5), sticky=tk.E)
        
        self.clear_btn = ttk.Button(btn_frame, text="清空列表", command=self.clear_selection)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.select_file_btn = ttk.Button(btn_frame, text="添加文件...", command=self.select_files)
        self.select_file_btn.pack(side=tk.LEFT)
        
        settings_frame = ttk.LabelFrame(main_frame, text="剪辑设置", padding=10)
        settings_frame.grid(row=2, column=0, pady=10, sticky=tk.EW)
        
        vcmd = (self.root.register(self._validate_time_input), '%P')
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill=tk.X, expand=True)
        
        ttk.Label(time_frame, text="要删除的片头时长:").pack(side=tk.LEFT, padx=(5, 10))
        self.hour_var = tk.StringVar(value="00")
        ttk.Entry(time_frame, textvariable=self.hour_var, width=3, justify=tk.CENTER, validate='key', validatecommand=vcmd).pack(side=tk.LEFT)
        ttk.Label(time_frame, text="时").pack(side=tk.LEFT, padx=(2, 5))
        self.minute_var = tk.StringVar(value="00")
        ttk.Entry(time_frame, textvariable=self.minute_var, width=3, justify=tk.CENTER, validate='key', validatecommand=vcmd).pack(side=tk.LEFT)
        ttk.Label(time_frame, text="分").pack(side=tk.LEFT, padx=(2, 5))
        self.second_var = tk.StringVar(value="00")
        ttk.Entry(time_frame, textvariable=self.second_var, width=3, justify=tk.CENTER, validate='key', validatecommand=vcmd).pack(side=tk.LEFT)
        ttk.Label(time_frame, text="秒").pack(side=tk.LEFT, padx=(2, 5))

        process_control_frame = ttk.Frame(main_frame)
        process_control_frame.grid(row=3, column=0, sticky=tk.EW, pady=(10, 5))
        process_control_frame.columnconfigure(0, weight=1)

        self.process_btn = ttk.Button(process_control_frame, text="开始处理", command=self.start_processing)
        self.process_btn.grid(row=0, column=0, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=tk.EW, pady=5)

    def _setup_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._on_drop_files)

    def _on_drop_files(self, event):
        try:
            filepaths = self.root.tk.splitlist(event.data)
            added_files_count = 0
            for path in filepaths:
                if os.path.isfile(path) and os.path.splitext(path)[1].lower() in self.VALID_VIDEO_EXTENSIONS:
                    if path not in self.selected_files:
                        self.selected_files.append(path)
                        added_files_count += 1
            
            if added_files_count > 0:
                self._update_files_text()
                self.update_status(f"通过拖拽添加了 {added_files_count} 个文件。总计 {len(self.selected_files)} 个。")
                self.progress_var.set(0)
            else:
                self.update_status("拖拽的文件无效或已在列表中。")
        except Exception as e:
            messagebox.showerror("拖拽错误", f"处理拖拽文件时出错: {e}")
    
    def clear_selection(self):
        if not self.selected_files: return
        self.selected_files.clear()
        self._update_files_text()
        self.progress_var.set(0)
        self.update_status("文件列表已清空。")

    def _validate_time_input(self, value_if_allowed):
        if value_if_allowed.isdigit() and len(value_if_allowed) <= 2:
            return True
        return value_if_allowed == ""

    def update_status(self, message):
        self.status_var.set(message)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="请选择一个或多个视频文件",
            filetypes=[
                ("所有视频文件", " ".join(f"*{ext}" for ext in self.VALID_VIDEO_EXTENSIONS)),
                ("MP4 文件", "*.mp4"), ("MKV 文件", "*.mkv"), ("所有文件", "*.*")
            ]
        )
        if file_paths:
            new_files_count = 0
            for p in file_paths:
                if p not in self.selected_files:
                    self.selected_files.append(p)
                    new_files_count += 1
            if new_files_count > 0:
                self._update_files_text()
                self.update_status(f"新添加了 {new_files_count} 个文件。总计 {len(self.selected_files)} 个。")
                self.progress_var.set(0)

    def _update_files_text(self):
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        for i, file_path in enumerate(self.selected_files, 1):
            self.files_text.insert(tk.END, f"{i}. {os.path.basename(file_path)}\n")
        self.files_text.config(state=tk.DISABLED)

    def start_processing(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择至少一个视频文件。")
            return
        
        try:
            hours = int(self.hour_var.get() or 0)
            minutes = int(self.minute_var.get() or 0)
            seconds = int(self.second_var.get() or 0)
            if hours < 0 or minutes < 0 or seconds < 0: raise ValueError("时间值不能为负数")
            total_seconds = hours * 3600 + minutes * 60 + seconds
            if total_seconds == 0:
                messagebox.showwarning("警告", "要删除的时长不能为0。")
                return
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效的时间输入: {e}。\n请输入有效的整数。")
            return

        self._toggle_controls(enabled=False)
        self.processing_thread = threading.Thread(
            target=self.process_videos, 
            args=(total_seconds,),
            daemon=True
        )
        self.processing_thread.start()

    def process_videos(self, duration_seconds):
        total_files = len(self.selected_files)
        success_count = 0
        error_files = []

        for i, input_path in enumerate(self.selected_files):
            progress = ((i + 1) / total_files) * 100
            file_basename = os.path.basename(input_path)
            
            status_msg = f"处理中 ({i+1}/{total_files}): {file_basename}"
            self.root.after(0, self._update_ui_from_thread, progress, status_msg)

            try:
                dir_name = os.path.dirname(input_path)
                _, file_ext = os.path.splitext(file_basename)
                output_dir = os.path.join(dir_name, "processed")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, file_basename)
                
                # --- FFmpeg 命令构建 ---
                # 这是根据您的建议优化后的命令
                cmd = [
                    'ffmpeg',
                    '-y',  # 自动覆盖已存在的文件
                    '-ss', str(duration_seconds),  # 使用快速的输入定位
                    '-i', input_path,
                ]

                # 仅对mp4/mov文件添加 faststart 标记
                if file_ext.lower() in ['.mp4', '.mov']:
                    cmd.extend(['-movflags', '+faststart'])

                # 添加核心的复制命令和输出文件路径
                cmd.extend([
                    '-c', 'copy', # 复制所有流（视频、音频、字幕等）
                    output_path
                ])
                # --- 命令构建结束 ---
                
                subprocess.run(
                    cmd, check=True, capture_output=True, text=True, 
                    encoding='utf-8', startupinfo=self._get_startup_info()
                )
                success_count += 1
            
            except subprocess.CalledProcessError as e:
                error_detail = e.stderr.strip().split('\n')[-1]
                error_files.append(f"{file_basename}: {error_detail}")
            except Exception as e:
                error_files.append(f"{file_basename}: {str(e)}")

        self.root.after(0, self.show_final_results, success_count, error_files)

    def _update_ui_from_thread(self, progress, status_message):
        self.progress_var.set(progress)
        self.update_status(status_message)

    def show_final_results(self, success_count, error_files):
        error_count = len(error_files)
        result_msg = f"处理完成！\n\n成功: {success_count} 个\n失败: {error_count} 个"
        
        if error_count > 0:
            error_details = "\n\n失败详情:\n" + "\n".join(f"- {e}" for e in error_files)
            self._show_error_details_dialog(result_msg, error_details)
        else:
            messagebox.showinfo("处理结果", result_msg)
        
        self.clear_selection()
        self.update_status("处理完成！等待新任务 (可拖拽文件到此窗口)")
        self._toggle_controls(enabled=True)

    def _show_error_details_dialog(self, summary, details):
        dialog = tk.Toplevel(self.root)
        dialog.title("处理失败详情")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text=summary, justify=tk.LEFT, padding=10).pack(anchor=tk.W)
        
        text_frame = ttk.Frame(dialog, padding=(10, 0, 10, 10))
        text_frame.pack(fill=tk.BOTH, expand=True)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        error_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        error_text.insert(tk.END, details)
        error_text.config(state=tk.DISABLED)
        error_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(text_frame, command=error_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        error_text['yscrollcommand'] = scrollbar.set

        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def _toggle_controls(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.process_btn.config(state=state)
        self.select_file_btn.config(state=state)
        self.clear_btn.config(state=state)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoTrimTool(root)
    root.mainloop()