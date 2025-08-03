import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Toplevel, Scrollbar, ttk, Canvas
from pathlib import Path
import re
import threading
from datetime import datetime
import json
import sys
from PIL import Image, ImageTk
import tempfile
import time

class VideoFrameProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("别快视频图片合并分割器v1.0")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        
        # 获取程序所在目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            self.app_dir = os.path.dirname(sys.executable)
            self.ffmpeg_dir = os.path.join(self.app_dir, "ffmpeg")
        else:
            # 如果是普通Python脚本
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
            self.ffmpeg_dir = os.path.join(self.app_dir, "ffmpeg")
        
        # 设置FFmpeg路径
        self.ffmpeg_path = os.path.join(self.ffmpeg_dir, "ffmpeg.exe")
        self.ffprobe_path = os.path.join(self.ffmpeg_dir, "ffprobe.exe")
        
        # 检查FFmpeg是否存在
        self.check_ffmpeg()

        # 配置文件路径
        self.config_file = os.path.join(self.app_dir, "路径设置.json")
        
        # Variables
        self.video_path = tk.StringVar()
        self.image_folder_path = tk.StringVar()
        self.output_video_path = tk.StringVar()
        self.output_frames_path = tk.StringVar()
        self.first_last_path = tk.StringVar()
        self.frame_number = tk.IntVar(value=1)
        self.tasks = []
        self.running_task = None
        self.stop_flag = False
        self.progress = tk.StringVar(value="就绪")

        # 转场效果列表
        self.transition_effects = {
            "淡入淡出": "fade",
            "擦除": "wipeleft",
            "滑动": "slideleft",
            "圆形擦除": "circleopen",
            "溶解": "pixelize",
            "径向擦除": "radial",
            "平滑左": "smoothleft",
            "平滑右": "smoothright",
            "平滑上": "smoothup",
            "平滑下": "smoothdown"
        }

        # 加载配置
        self.load_config()

        # Frame for Input Section
        input_frame = tk.LabelFrame(root, text="输入设置", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(input_frame, text="视频路径:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        tk.Entry(input_frame, textvariable=self.video_path, width=40).grid(row=0, column=1, padx=5, pady=2)
        tk.Button(input_frame, text="浏览", command=self.browse_video).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(input_frame, text="批量处理", command=self.batch_process).grid(row=0, column=3, padx=5, pady=2)

        tk.Label(input_frame, text="图片路径:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        tk.Entry(input_frame, textvariable=self.image_folder_path, width=40).grid(row=1, column=1, padx=5, pady=2)
        tk.Button(input_frame, text="浏览", command=self.browse_image_folder).grid(row=1, column=2, padx=5, pady=2)
        tk.Button(input_frame, text="添加任务", command=self.add_task).grid(row=1, column=3, padx=5, pady=2)

        # Frame for Output Section
        output_frame = tk.LabelFrame(root, text="输出设置", padx=10, pady=10)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        tk.Label(output_frame, text="保存视频:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.video_entry = tk.Entry(output_frame, textvariable=self.output_video_path, width=40)
        self.video_entry.grid(row=0, column=1, padx=5, pady=2)
        self.video_entry.bind('<KeyRelease>', lambda e: self.save_config())
        tk.Button(output_frame, text="浏览", command=self.browse_output_video).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(output_frame, text="合并视频", command=self.merge_frames_to_video).grid(row=0, column=3, padx=5, pady=2)

        tk.Label(output_frame, text="保存图片:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.frames_entry = tk.Entry(output_frame, textvariable=self.output_frames_path, width=40)
        self.frames_entry.grid(row=1, column=1, padx=5, pady=2)
        self.frames_entry.bind('<KeyRelease>', lambda e: self.save_config())
        tk.Button(output_frame, text="浏览", command=self.browse_output_frames).grid(row=1, column=2, padx=5, pady=2)
        tk.Button(output_frame, text="分割视频", command=self.extract_all_frames).grid(row=1, column=3, padx=5, pady=2)

        tk.Label(output_frame, text="保存首尾:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.first_last_entry = tk.Entry(output_frame, textvariable=self.first_last_path, width=40)
        self.first_last_entry.grid(row=2, column=1, padx=5, pady=2)
        self.first_last_entry.bind('<KeyRelease>', lambda e: self.save_config())
        tk.Button(output_frame, text="浏览", command=self.browse_first_last).grid(row=2, column=2, padx=5, pady=2)
        tk.Button(output_frame, text="截首尾帧", command=self.extract_first_last).grid(row=2, column=3, padx=5, pady=2)

        # Frame for Frame Extraction
        extract_frame = tk.LabelFrame(root, text="帧提取设置", padx=10, pady=10)
        extract_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        tk.Label(extract_frame, text="提取特定帧编号:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        tk.Entry(extract_frame, textvariable=self.frame_number, width=10).grid(row=0, column=1, padx=5, pady=2)
        tk.Button(extract_frame, text="提取特定帧", command=self.extract_specific_frame).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(extract_frame, text="特效合并视频", command=self.show_effect_merge_dialog).grid(row=0, column=3, padx=5, pady=2)

        # Progress Bar
        progress_frame = tk.Frame(root)
        progress_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(progress_frame, text="进度:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        tk.Label(progress_frame, textvariable=self.progress).grid(row=0, column=2, padx=5, pady=2)

        # Frame for Task Management
        task_frame = tk.LabelFrame(root, text="任务管理", padx=10, pady=10)
        task_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")

        button_frame = tk.Frame(task_frame)
        button_frame.grid(row=0, column=0, columnspan=5, pady=5, padx=5, sticky="w")
        tk.Button(button_frame, text="删除", command=self.delete_task).grid(row=0, column=0, pady=5, padx=5)
        tk.Button(button_frame, text="编辑", command=self.edit_task).grid(row=0, column=1, pady=5, padx=5)
        tk.Button(button_frame, text="开始", command=self.start_tasks).grid(row=0, column=2, pady=5, padx=5)
        tk.Button(button_frame, text="停止", command=self.stop_task).grid(row=0, column=3, pady=5, padx=5)
        tk.Button(button_frame, text="退出", command=self.on_closing).grid(row=0, column=4, pady=5, padx=5)

        listbox_frame = tk.Frame(task_frame)
        listbox_frame.grid(row=1, column=0, columnspan=5, pady=5, padx=5, sticky="nsew")

        self.task_listbox = tk.Listbox(listbox_frame, height=8, width=60)
        self.task_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        # Configure grid weights
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(0, weight=1)
        task_frame.grid_rowconfigure(1, weight=1)
        task_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_columnconfigure(1, weight=1)

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def check_ffmpeg(self):
        """检查FFmpeg是否存在"""
        if not os.path.exists(self.ffmpeg_path) or not os.path.exists(self.ffprobe_path):
            # 尝试从系统PATH中查找
            try:
                import subprocess
                result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
                if result.returncode == 0:
                    # 找到系统FFmpeg，使用系统的
                    self.ffmpeg_path = 'ffmpeg'
                    self.ffprobe_path = 'ffprobe'
                    print("使用系统中的FFmpeg")
                    return
            except:
                pass
            
            # 如果都找不到，显示警告
            messagebox.showwarning("警告", 
                f"未找到FFmpeg组件！\n"
                f"程序功能将受限。\n\n"
                f"请安装FFmpeg或将ffmpeg.exe和ffprobe.exe\n"
                f"放置到以下位置：\n"
                f"{self.ffmpeg_dir}")
            
    def get_ffmpeg_cmd(self, cmd_name):
        """获取FFmpeg命令的完整路径"""
        if cmd_name == "ffmpeg":
            if os.path.exists(self.ffmpeg_path):
                return self.ffmpeg_path
            else:
                return "ffmpeg"  # 尝试使用系统命令
        elif cmd_name == "ffprobe":
            if os.path.exists(self.ffprobe_path):
                return self.ffprobe_path
            else:
                return "ffprobe"  # 尝试使用系统命令
        return cmd_name

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "output_video_path": "C:/输出/视频",
            "output_frames_path": "C:/输出/帧",
            "first_last_path": "C:/输出/首尾帧"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有必需的键都存在
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
            else:
                config = default_config
                # 创建配置文件
                self.save_config_to_file(config)
            
            # 设置变量值
            self.output_video_path.set(config.get("output_video_path", default_config["output_video_path"]))
            self.output_frames_path.set(config.get("output_frames_path", default_config["output_frames_path"]))
            self.first_last_path.set(config.get("first_last_path", default_config["first_last_path"]))
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 使用默认配置
            self.output_video_path.set(default_config["output_video_path"])
            self.output_frames_path.set(default_config["output_frames_path"])
            self.first_last_path.set(default_config["first_last_path"])

    def save_config_to_file(self, config=None):
        """保存配置到文件"""
        if config is None:
            config = {
                "output_video_path": self.output_video_path.get(),
                "output_frames_path": self.output_frames_path.get(),
                "first_last_path": self.first_last_path.get()
            }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def save_config(self):
        """保存当前配置"""
        self.save_config_to_file()

    def on_closing(self):
        """关闭窗口前保存配置"""
        self.save_config()
        self.root.quit()

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4 *.mkv *.mov *.avi *.flv *.wmv")])
        if path:
            self.video_path.set(path)

    def browse_image_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.image_folder_path.set(path)

    def browse_output_video(self):
        path = filedialog.askdirectory()
        if path:
            self.output_video_path.set(path)
            self.save_config()

    def browse_output_frames(self):
        path = filedialog.askdirectory()
        if path:
            self.output_frames_path.set(path)
            self.save_config()

    def browse_first_last(self):
        path = filedialog.askdirectory()
        if path:
            self.first_last_path.set(path)
            self.save_config()

    def show_error_details(self, error_message):
        """显示详细的错误信息"""
        error_window = Toplevel(self.root)
        error_window.title("FFmpeg 错误详情")
        error_window.geometry("600x400")
        
        text_widget = Text(error_window, wrap='word', padx=10, pady=10)
        text_widget.insert('1.0', error_message)
        text_widget.config(state='disabled')
        
        scrollbar = Scrollbar(error_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def run_ffmpeg(self, cmd, show_progress=False):
        """运行FFmpeg命令，可选显示进度"""
        if show_progress:
            self.progress_bar.start(10)
        
        # 替换命令中的ffmpeg和ffprobe为完整路径
        if cmd[0] in ['ffmpeg', 'ffprobe']:
            cmd[0] = self.get_ffmpeg_cmd(cmd[0])
            
        try:
            # 使用CREATE_NO_WINDOW标志来隐藏控制台窗口（仅Windows）
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            # 使用encoding='utf-8'来避免编码错误
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  encoding='utf-8', errors='replace', creationflags=creationflags)
            
            if result.returncode != 0:
                error_msg = f"命令执行失败 (返回码: {result.returncode})\n命令: {' '.join(cmd)}\n\n错误输出:\n{result.stderr}"
                messagebox.showerror("FFmpeg 执行失败", "操作失败，点击'确定'查看详细错误信息。")
                self.show_error_details(error_msg)
                return False
            return True
        finally:
            if show_progress:
                self.progress_bar.stop()

    def get_video_info(self, video_path):
        """获取视频信息（帧率、总帧数、时长等）"""
        cmd = [
            self.get_ffmpeg_cmd('ffprobe'), '-v', 'error', '-select_streams', 'v:0',
            '-count_packets', '-show_entries', 
            'stream=nb_read_packets,r_frame_rate,duration,width,height',
            '-of', 'json', video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace',
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                stream = info['streams'][0] if info.get('streams') else {}
                
                # 获取帧率
                frame_rate = stream.get('r_frame_rate', '25/1')
                num, den = map(int, frame_rate.split('/'))
                fps = num / den if den != 0 else 25
                
                # 获取总帧数
                total_frames = int(stream.get('nb_read_packets', 0))
                
                # 获取时长
                duration = float(stream.get('duration', 0))
                
                # 获取分辨率
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))
                
                return {
                    'fps': fps, 
                    'total_frames': total_frames, 
                    'duration': duration,
                    'width': width,
                    'height': height
                }
        except:
            pass
        
        return {'fps': 25, 'total_frames': 0, 'duration': 0, 'width': 0, 'height': 0}

    def get_audio_duration(self, audio_path):
        """获取音频文件时长"""
        cmd = [
            self.get_ffmpeg_cmd('ffprobe'), '-v', 'error', '-show_entries', 
            'format=duration', '-of', 'json', audio_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace',
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                duration = float(info.get('format', {}).get('duration', 0))
                return duration
        except:
            pass
        
        return 0

    def format_time(self, seconds):
        """格式化时间显示"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"

    def show_effect_merge_dialog(self):
        """显示特效合并对话框"""
        frames_dir = self.image_folder_path.get()
        if not frames_dir or not os.path.exists(frames_dir):
            messagebox.showwarning("警告", "请先选择一个有效的图片文件夹。")
            return
        
        # 创建对话框
        dialog = Toplevel(self.root)
        dialog.title("特效合并视频设置")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        
        # 合并类型选择
        tk.Label(dialog, text="合并类型:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        merge_type_var = tk.StringVar(value="特效合并")
        merge_type_frame = tk.Frame(dialog)
        merge_type_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        tk.Radiobutton(merge_type_frame, text="特效合并", variable=merge_type_var, 
                      value="特效合并", command=lambda: self.toggle_effect_options(dialog, merge_type_var.get())).pack(side="left")
        tk.Radiobutton(merge_type_frame, text="简单合并", variable=merge_type_var, 
                      value="简单合并", command=lambda: self.toggle_effect_options(dialog, merge_type_var.get())).pack(side="left")
        
        # 音频文件选择
        tk.Label(dialog, text="音频文件:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        audio_path_var = tk.StringVar()
        audio_frame = tk.Frame(dialog)
        audio_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        tk.Entry(audio_frame, textvariable=audio_path_var, width=30).pack(side="left")
        tk.Button(audio_frame, text="浏览", command=lambda: self.browse_audio(audio_path_var)).pack(side="left", padx=5)
        
        # 音频模式选择
        tk.Label(dialog, text="音频模式:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        audio_mode_var = tk.StringVar(value="正常模式")
        audio_mode_frame = tk.Frame(dialog)
        audio_mode_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        tk.Radiobutton(audio_mode_frame, text="正常模式", variable=audio_mode_var, value="正常模式").pack(side="left")
        tk.Radiobutton(audio_mode_frame, text="循环模式", variable=audio_mode_var, value="循环模式").pack(side="left")
        
        # 图片显示时长（特效合并时使用）
        tk.Label(dialog, text="每张图片显示时长（秒）:", name="duration_label").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        duration_var = tk.DoubleVar(value=2.0)
        duration_scale = tk.Scale(dialog, from_=0.5, to=10.0, resolution=0.5, orient="horizontal", 
                                 variable=duration_var, length=200, name="duration_scale")
        duration_scale.grid(row=3, column=1, padx=10, pady=10)
        
        # 转场时长（特效合并时显示）
        tk.Label(dialog, text="转场效果时长（秒）:", name="transition_duration_label").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        transition_duration_var = tk.DoubleVar(value=1.0)
        transition_scale = tk.Scale(dialog, from_=0.1, to=3.0, resolution=0.1, orient="horizontal", 
                                   variable=transition_duration_var, length=200, name="transition_duration_scale")
        transition_scale.grid(row=4, column=1, padx=10, pady=10)
        
        # 转场效果选择（特效合并时显示）
        tk.Label(dialog, text="转场效果:", name="effect_label").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        effect_var = tk.StringVar(value="淡入淡出")
        effect_menu = ttk.Combobox(dialog, textvariable=effect_var, values=list(self.transition_effects.keys()), 
                                  state="readonly", width=20, name="effect_menu")
        effect_menu.grid(row=5, column=1, padx=10, pady=10)
        
        # 输出帧率
        tk.Label(dialog, text="输出视频帧率:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
        fps_var = tk.IntVar(value=30)
        tk.Scale(dialog, from_=15, to=60, resolution=5, orient="horizontal", 
                variable=fps_var, length=200).grid(row=6, column=1, padx=10, pady=10)
        
        # 时长信息显示
        info_frame = tk.LabelFrame(dialog, text="时长信息", padx=10, pady=10)
        info_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        video_duration_label = tk.Label(info_frame, text="预计视频时长: 计算中...")
        video_duration_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        audio_duration_label = tk.Label(info_frame, text="音频文件时长: 未选择")
        audio_duration_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # 更新时长信息的函数
        def update_durations(*args):
            # 计算视频时长
            try:
                image_count = len([f for f in os.listdir(frames_dir) 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'))])
                
                if merge_type_var.get() == "特效合并" and image_count > 1:
                    # 特效合并：考虑转场时间
                    video_duration = duration_var.get() * image_count - transition_duration_var.get() * (image_count - 1) / 2
                elif merge_type_var.get() == "简单合并":
                    # 简单合并：快速播放所有帧
                    video_duration = image_count / fps_var.get()
                else:
                    # 单张图片
                    video_duration = duration_var.get()
                
                video_duration_label.config(text=f"预计视频时长: {video_duration:.1f} 秒")
            except:
                video_duration_label.config(text="预计视频时长: 计算失败")
            
            # 更新音频时长
            if audio_path_var.get() and os.path.exists(audio_path_var.get()):
                audio_duration = self.get_audio_duration(audio_path_var.get())
                if audio_duration > 0:
                    audio_duration_label.config(text=f"音频文件时长: {audio_duration:.1f} 秒")
                else:
                    audio_duration_label.config(text="音频文件时长: 无法读取")
            else:
                audio_duration_label.config(text="音频文件时长: 未选择")
        
        # 绑定更新事件
        duration_var.trace('w', update_durations)
        transition_duration_var.trace('w', update_durations)
        merge_type_var.trace('w', update_durations)
        audio_path_var.trace('w', update_durations)
        fps_var.trace('w', update_durations)
        
        # 初始更新
        update_durations()
        
        # 按钮框架
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        def start_effect_merge():
            dialog.destroy()
            
            if merge_type_var.get() == "特效合并":
                self.effect_merge_frames_to_video(
                    duration=duration_var.get(),
                    transition_duration=transition_duration_var.get(),
                    effect=self.transition_effects[effect_var.get()],
                    fps=fps_var.get(),
                    audio_path=audio_path_var.get(),
                    audio_mode=audio_mode_var.get()
                )
            else:
                self.simple_merge_frames_to_video(
                    fps=fps_var.get(),
                    audio_path=audio_path_var.get(),
                    audio_mode=audio_mode_var.get()
                )
        
        tk.Button(button_frame, text="开始合并", command=start_effect_merge, width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="取消", command=dialog.destroy, width=15).pack(side="left", padx=10)
        
        # 使对话框模态
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def toggle_effect_options(self, dialog, merge_type):
        """切换特效选项的显示/隐藏"""
        if merge_type == "简单合并":
            # 隐藏特效合并特有的选项
            for widget_name in ["transition_duration_label", "transition_duration_scale", 
                              "effect_label", "effect_menu", "duration_label", "duration_scale"]:
                widget = dialog.nametowidget(widget_name)
                widget.grid_remove()
        else:
            # 显示所有选项
            dialog.nametowidget("duration_label").grid()
            dialog.nametowidget("duration_scale").grid()
            dialog.nametowidget("transition_duration_label").grid()
            dialog.nametowidget("transition_duration_scale").grid()
            dialog.nametowidget("effect_label").grid()
            dialog.nametowidget("effect_menu").grid()

    def browse_audio(self, audio_var):
        """浏览音频文件"""
        path = filedialog.askopenfilename(
            filetypes=[("音频文件", "*.mp3 *.wav *.aac *.flac *.m4a *.ogg *.wma")]
        )
        if path:
            audio_var.set(path)

    def simple_merge_frames_to_video(self, fps=30, audio_path="", audio_mode="正常模式"):
        """简单合并图片为视频（按帧率快速播放）"""
        frames_dir = self.image_folder_path.get()
        if not frames_dir or not os.path.exists(frames_dir):
            return
        
        # 生成输出文件名
        folder_name = Path(frames_dir).name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{folder_name}_简单合并_{timestamp}.mp4"
        output_path = os.path.join(self.output_video_path.get(), output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.progress.set("正在简单合并图片为视频...")
        
        try:
            # 获取图片文件
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
            image_files = sorted([f for f in os.listdir(frames_dir) 
                                if f.lower().endswith(valid_extensions) 
                                and os.path.isfile(os.path.join(frames_dir, f))],
                               key=self.natural_sort_key)
            
            if not image_files:
                messagebox.showwarning("警告", "未找到支持的图片文件。")
                return
            
            # 计算视频总时长（图片数量/帧率）
            video_duration = len(image_files) / fps
            
            # 获取音频时长
            audio_duration = 0
            if audio_path and os.path.exists(audio_path):
                audio_duration = self.get_audio_duration(audio_path)
            
            # 检查是否为序列
            is_sequence = False
            first_file = image_files[0]
            pattern_match = re.search(r'(\d+)', first_file)
            if pattern_match and len(image_files) > 1:
                is_sequence = True
                number_str = pattern_match.group(1)
                pattern = first_file.replace(number_str, f'%0{len(number_str)}d')
                input_pattern = os.path.join(frames_dir, pattern)
            
            # 构建FFmpeg命令
            if is_sequence:
                # 使用图片序列输入
                cmd = [
                    'ffmpeg', '-y',
                    '-framerate', str(fps),
                    '-i', input_pattern
                ]
            else:
                # 使用concat方式
                concat_file = os.path.join(frames_dir, "simple_concat_list.txt")
                with open(concat_file, 'w', encoding='utf-8') as f:
                    for img_file in image_files:
                        f.write(f"file '{img_file}'\n")
                        f.write(f"duration {1.0/fps}\n")
                    f.write(f"file '{image_files[-1]}'\n")
                
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file
                ]
            
            # 添加音频输入
            if audio_path and os.path.exists(audio_path):
                if audio_mode == "循环模式" and audio_duration < video_duration:
                    # 循环音频
                    cmd.extend(['-stream_loop', '-1', '-i', audio_path])
                else:
                    cmd.extend(['-i', audio_path])
            
            # 视频编码参数
            cmd.extend([
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'medium',
                '-crf', '23',
                '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2'
            ])
            
            # 音频处理
            if audio_path and os.path.exists(audio_path):
                if audio_mode == "循环模式" and audio_duration > video_duration:
                    # 音频长于视频，需要循环图片
                    repeat_count = int(audio_duration / video_duration) + 1
                    video_duration = video_duration * repeat_count
                    cmd.extend(['-t', str(audio_duration)])
                else:
                    cmd.extend(['-t', str(video_duration)])
                cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
            
            cmd.append(output_path)
            
            # 执行命令
            if self.run_ffmpeg(cmd, show_progress=True):
                self.progress.set("简单视频合并完成")
                messagebox.showinfo("成功", 
                    f"视频已成功生成！\n"
                    f"文件: {output_filename}\n"
                    f"位置: {output_path}\n"
                    f"图片数: {len(image_files)}\n"
                    f"帧率: {fps} fps\n"
                    f"音频: {'有' if audio_path else '无'}")
            else:
                self.progress.set("合并失败")
            
            # 清理临时文件
            if not is_sequence and 'concat_file' in locals() and os.path.exists(concat_file):
                os.remove(concat_file)
                
        except Exception as e:
            self.progress.set("合并失败")
            messagebox.showerror("错误", f"简单合并视频失败: {str(e)}")

    def effect_merge_frames_to_video(self, duration=2.0, transition_duration=1.0, effect="fade", 
                                   fps=30, audio_path="", audio_mode="正常模式"):
        """特效合并图片为视频（带音频）"""
        frames_dir = self.image_folder_path.get()
        if not frames_dir or not os.path.exists(frames_dir):
            return
        
        # 生成输出文件名
        folder_name = Path(frames_dir).name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{folder_name}_特效合并_{timestamp}.mp4"
        output_path = os.path.join(self.output_video_path.get(), output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.progress.set("正在特效合并图片为视频...")
        
        try:
            # 获取图片文件
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
            image_files = sorted([f for f in os.listdir(frames_dir) 
                                if f.lower().endswith(valid_extensions) 
                                and os.path.isfile(os.path.join(frames_dir, f))],
                               key=self.natural_sort_key)
            
            if not image_files:
                messagebox.showwarning("警告", "未找到支持的图片文件。")
                return
            
            # 计算视频总时长
            if len(image_files) == 1:
                video_duration = duration
            else:
                video_duration = duration * len(image_files) - transition_duration * (len(image_files) - 1) / 2
            
            # 获取音频时长
            audio_duration = 0
            if audio_path and os.path.exists(audio_path):
                audio_duration = self.get_audio_duration(audio_path)
            
            # 根据音频模式调整策略
            original_image_count = len(image_files)
            if audio_path and audio_duration > 0 and audio_mode == "循环模式" and audio_duration > video_duration:
                # 需要重复图片以匹配音频长度
                needed_duration = audio_duration
                if len(image_files) == 1:
                    repeat_count = int(needed_duration / duration) + 1
                else:
                    # 计算需要多少组图片
                    single_group_duration = video_duration
                    repeat_count = int(needed_duration / single_group_duration) + 1
                image_files = image_files * repeat_count
            
            if len(image_files) == 1:
                # 只有一张图片，简单处理
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', os.path.join(frames_dir, image_files[0]),
                    '-t', str(duration)
                ]
                
                # 添加音频
                if audio_path and os.path.exists(audio_path):
                    if audio_mode == "循环模式":
                        cmd.extend(['-stream_loop', '-1', '-i', audio_path])
                    else:
                        cmd.extend(['-i', audio_path])
                
                cmd.extend([
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps={fps}'
                ])
                
                if audio_path and os.path.exists(audio_path):
                    cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-shortest'])
                
                cmd.append(output_path)
            else:
                # 多张图片，使用转场效果
                filter_complex = []
                inputs = []
                
                # 为每张图片创建输入
                for i, img in enumerate(image_files):
                    inputs.extend(['-loop', '1', '-t', str(duration + transition_duration), 
                                  '-i', os.path.join(frames_dir, img)])
                
                # 缩放所有输入
                for i in range(len(image_files)):
                    filter_complex.append(
                        f'[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,'
                        f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}]'
                    )
                
                # 创建转场效果
                if len(image_files) == 2:
                    filter_complex.append(
                        f'[v0][v1]xfade=transition={effect}:duration={transition_duration}:'
                        f'offset={duration - transition_duration/2}[vout]'
                    )
                else:
                    prev_output = "v0"
                    for i in range(1, len(image_files)):
                        offset = duration * i - transition_duration * i / 2
                        if i == len(image_files) - 1:
                            output = "vout"
                        else:
                            output = f"vt{i}"
                        
                        filter_complex.append(
                            f'[{prev_output}][v{i}]xfade=transition={effect}:'
                            f'duration={transition_duration}:offset={offset}[{output}]'
                        )
                        prev_output = output
                
                # 构建FFmpeg命令
                cmd = ['ffmpeg', '-y']
                cmd.extend(inputs)
                
                # 添加音频输入
                if audio_path and os.path.exists(audio_path):
                    if audio_mode == "循环模式":
                        cmd.extend(['-stream_loop', '-1', '-i', audio_path])
                    else:
                        cmd.extend(['-i', audio_path])
                
                # 添加滤镜
                filter_str = ';'.join(filter_complex)
                cmd.extend(['-filter_complex', filter_str])
                
                # 映射输出
                cmd.extend(['-map', '[vout]'])
                if audio_path and os.path.exists(audio_path):
                    cmd.extend(['-map', f'{len(image_files)}:a'])
                
                # 编码参数
                cmd.extend([
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-preset', 'medium',
                    '-crf', '23'
                ])
                
                if audio_path and os.path.exists(audio_path):
                    cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
                    if audio_mode == "正常模式" or (audio_mode == "循环模式" and audio_duration >= video_duration):
                        cmd.extend(['-t', str(video_duration)])
                
                cmd.append(output_path)
            
            if self.run_ffmpeg(cmd, show_progress=True):
                self.progress.set("特效视频合并完成")
                messagebox.showinfo("成功", 
                    f"特效视频已成功生成！\n"
                    f"文件: {output_filename}\n"
                    f"位置: {output_path}\n"
                    f"原始图片数: {original_image_count}\n"
                    f"转场效果: {effect}\n"
                    f"音频: {'有' if audio_path else '无'}")
            else:
                self.progress.set("特效合并失败")
                
        except Exception as e:
            self.progress.set("特效合并失败")
            messagebox.showerror("错误", f"特效合并视频失败: {str(e)}")

    def extract_first_last(self):
        """提取首尾帧（改进版）"""
        video_path = self.video_path.get()
        if not video_path:
            messagebox.showwarning("警告", "请先选择一个视频文件。")
            return
            
        self.progress.set("正在提取首尾帧...")
        output_dir = self.first_last_path.get()
        os.makedirs(output_dir, exist_ok=True)
        name = Path(video_path).stem

        try:
            # 获取视频信息
            video_info = self.get_video_info(video_path)
            
            # 提取第一帧
            cmd_first = [
                'ffmpeg', '-y', '-i', video_path, 
                '-vf', 'select=eq(n\\,0)', '-vframes', '1',
                os.path.join(output_dir, f"{name}_首帧.png")
            ]
            if not self.run_ffmpeg(cmd_first, show_progress=True):
                return

            # 提取最后一帧 - 使用更可靠的方法
            if video_info['total_frames'] > 0:
                # 方法1：如果能获取总帧数，使用帧选择
                last_frame_index = video_info['total_frames'] - 1
                cmd_last = [
                    'ffmpeg', '-y', '-i', video_path,
                    '-vf', f'select=eq(n\\,{last_frame_index})',
                    '-vframes', '1',
                    os.path.join(output_dir, f"{name}_尾帧.png")
                ]
            else:
                # 方法2：反向读取视频的第一帧
                cmd_last = [
                    'ffmpeg', '-y', '-sseof', '-3', '-i', video_path,
                    '-update', '1', '-vframes', '1',
                    os.path.join(output_dir, f"{name}_尾帧.png")
                ]
            
            if not self.run_ffmpeg(cmd_last, show_progress=True):
                # 备用方法：使用时长定位
                if video_info['duration'] > 0:
                    timestamp = max(0, video_info['duration'] - 0.1)
                    cmd_last_backup = [
                        'ffmpeg', '-y', '-ss', str(timestamp), '-i', video_path,
                        '-vframes', '1',
                        os.path.join(output_dir, f"{name}_尾帧.png")
                    ]
                    self.run_ffmpeg(cmd_last_backup, show_progress=True)
            
            self.progress.set("首尾帧提取完成")
            messagebox.showinfo("成功", f"首尾帧已保存到: {output_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"提取首尾帧失败: {str(e)}")
        finally:
            self.progress.set("就绪")

    def extract_specific_frame(self):
        """提取特定帧"""
        video_path = self.video_path.get()
        if not video_path:
            messagebox.showwarning("警告", "请先选择一个视频文件。")
            return
            
        output_dir = self.first_last_path.get()
        os.makedirs(output_dir, exist_ok=True)
        name = Path(video_path).stem
        frame = self.frame_number.get()
        
        self.progress.set(f"正在提取第 {frame} 帧...")
        
        # 使用更精确的帧选择
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f'select=eq(n\\,{frame-1})',
            '-vframes', '1',
            os.path.join(output_dir, f"{name}_帧{frame}.png")
        ]
        
        if self.run_ffmpeg(cmd, show_progress=True):
            messagebox.showinfo("成功", f"第 {frame} 帧已保存")
        
        self.progress.set("就绪")

    def extract_all_frames(self):
        """提取所有帧（改进版）"""
        video_path = self.video_path.get()
        if not video_path:
            messagebox.showwarning("警告", "请先选择一个视频文件。")
            return
            
        output_dir = self.output_frames_path.get()
        os.makedirs(output_dir, exist_ok=True)
        name = Path(video_path).stem
        new_folder = os.path.join(output_dir, name)
        os.makedirs(new_folder, exist_ok=True)
        
        self.progress.set("正在分割视频为帧...")
        
        # 获取视频信息
        video_info = self.get_video_info(video_path)
        total_frames = video_info['total_frames']
        
        # 提取所有帧，不限制帧率
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vsync', '0',  # 保持原始时间戳
            os.path.join(new_folder, f"%06d.png")  # 使用6位数字以支持更多帧
        ]
        
        if self.run_ffmpeg(cmd, show_progress=True):
            # 统计实际提取的帧数
            extracted_frames = len([f for f in os.listdir(new_folder) if f.endswith('.png')])
            self.progress.set(f"完成：已提取 {extracted_frames} 帧")
            messagebox.showinfo("成功", f"视频已分割为 {extracted_frames} 帧\n保存位置: {new_folder}")
        else:
            self.progress.set("分割失败")

    def natural_sort_key(self, filename):
        """自然排序键函数，正确处理数字"""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', filename)]

    def merge_frames_to_video(self):
        """合并图片为视频（改进版）"""
        frames_dir = self.image_folder_path.get()
        if not frames_dir or not os.path.exists(frames_dir):
            messagebox.showwarning("警告", "请先选择一个有效的图片文件夹。")
            return
            
        # 生成输出文件名
        folder_name = Path(frames_dir).name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{folder_name}_合并_{timestamp}.mp4"
        output_path = os.path.join(self.output_video_path.get(), output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self.progress.set("正在合并图片为视频...")
        
        try:
            # 支持更多图片格式
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
            all_files = os.listdir(frames_dir)
            
            # 过滤图片文件
            image_files = [f for f in all_files 
                          if f.lower().endswith(valid_extensions) 
                          and os.path.isfile(os.path.join(frames_dir, f))]
            
            if not image_files:
                messagebox.showwarning("警告", "在指定文件夹中未找到支持的图片文件。")
                return
            
            # 自然排序文件名
            image_files.sort(key=self.natural_sort_key)
            
            # 检测图片模式（是否为序列）
            is_sequence = False
            if len(image_files) > 1:
                # 检查是否为数字序列命名
                numbers = []
                for f in image_files[:10]:  # 检查前10个文件
                    match = re.search(r'(\d+)', f)
                    if match:
                        numbers.append(int(match.group(1)))
                if numbers and all(b - a == 1 for a, b in zip(numbers[:-1], numbers[1:])):
                    is_sequence = True
            
            # 获取第一张图片的信息
            first_image_path = os.path.join(frames_dir, image_files[0])
            probe_cmd = [
                self.get_ffmpeg_cmd('ffprobe'), '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height', '-of', 'json',
                first_image_path
            ]
            
            # 设置默认参数
            fps = 30  # 默认帧率
            scale_filter = ""
            
            try:
                result = subprocess.run(probe_cmd, capture_output=True, encoding='utf-8', errors='replace')
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    if info.get('streams'):
                        width = info['streams'][0].get('width', 0)
                        height = info['streams'][0].get('height', 0)
                        # 如果尺寸过大，添加缩放
                        if width > 1920 or height > 1080:
                            scale_filter = "-vf scale=1920:-1 "
            except:
                pass
            
            if is_sequence and len(image_files) > 10:
                # 使用图片序列模式（适用于连续编号的图片）
                # 找到序列模式
                first_file = image_files[0]
                pattern_match = re.search(r'(\d+)', first_file)
                if pattern_match:
                    number_str = pattern_match.group(1)
                    pattern = first_file.replace(number_str, f'%0{len(number_str)}d')
                    
                    cmd = [
                        'ffmpeg', '-y',
                        '-framerate', str(fps),
                        '-i', os.path.join(frames_dir, pattern),
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'medium',
                        '-crf', '23'
                    ]
                    if scale_filter:
                        cmd.extend(['-vf', 'scale=1920:-1'])
                    cmd.append(output_path)
                else:
                    raise ValueError("无法识别图片序列模式")
            else:
                # 使用concat demuxer（适用于任意命名的图片）
                concat_file = os.path.join(frames_dir, "concat_list.txt")
                with open(concat_file, 'w', encoding='utf-8') as f:
                    for img_file in image_files:
                        # 使用相对路径并转换为正斜杠
                        f.write(f"file '{img_file}'\n")
                        f.write(f"duration {1.0/fps}\n")  # 设置每张图片的持续时间
                    # 最后一张图片也需要显示
                    f.write(f"file '{image_files[-1]}'\n")
                
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-vsync', 'vfr'  # 可变帧率，更好处理不同尺寸的图片
                ]
                if scale_filter:
                    cmd.extend(['-vf', 'scale=1920:-1:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2'])
                cmd.append(output_path)
                
                # 执行命令
                if self.run_ffmpeg(cmd, show_progress=True):
                    success = True
                else:
                    success = False
                
                # 清理临时文件
                if os.path.exists(concat_file):
                    os.remove(concat_file)
                    
                if not success:
                    return
            
            # 验证输出
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.progress.set("视频合并完成")
                messagebox.showinfo("成功", 
                    f"视频已成功生成！\n"
                    f"文件: {output_filename}\n"
                    f"位置: {output_path}\n"
                    f"共合并 {len(image_files)} 张图片")
            else:
                raise Exception("输出文件未生成或大小为0")
                
        except Exception as e:
            self.progress.set("合并失败")
            messagebox.showerror("错误", f"合并视频失败: {str(e)}")

    def add_task(self):
        """添加任务"""
        # 优先使用当前设置的路径
        if self.video_path.get():
            path = self.video_path.get()
            task_type = "split"
        elif self.image_folder_path.get():
            path = self.image_folder_path.get()
            task_type = "merge"
        else:
            # 如果都没有，则让用户选择
            path = filedialog.askopenfilename(
                filetypes=[("视频文件", "*.mp4 *.mkv *.mov *.avi *.flv *.wmv")]
            )
            if not path:
                path = filedialog.askdirectory()
                if not path:
                    return
            task_type = "split" if os.path.isfile(path) else "merge"
        
        task = {"path": path, "type": task_type}
        self.tasks.append(task)
        self.update_task_list()

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            del self.tasks[selected[0]]
            self.update_task_list()

    def edit_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            task = self.tasks[selected[0]]
            new_path = filedialog.askopenfilename(
                filetypes=[("视频文件", "*.mp4 *.mkv *.mov *.avi *.flv *.wmv")]
            ) or filedialog.askdirectory()
            if new_path:
                task["path"] = new_path
                task["type"] = "split" if os.path.isfile(new_path) else "merge"
                self.update_task_list()

    def start_tasks(self):
        if self.running_task and self.running_task.is_alive():
            messagebox.showwarning("警告", "已有任务正在运行。")
            return
        if not self.tasks:
            messagebox.showwarning("警告", "无任务可执行。")
            return
        self.stop_flag = False
        self.running_task = threading.Thread(target=self.process_tasks)
        self.running_task.start()

    def stop_task(self):
        self.stop_flag = True
        self.progress.set("正在停止...")

    def process_tasks(self):
        """处理任务队列"""
        total_tasks = len(self.tasks)
        for i, task in enumerate(self.tasks):
            if self.stop_flag:
                self.progress.set("任务已停止")
                break
                
            self.progress.set(f"处理任务 {i+1}/{total_tasks}")
            
            if task["type"] == "split":
                self.video_path.set(task["path"])
                self.extract_all_frames()
            else:
                self.image_folder_path.set(task["path"])
                self.merge_frames_to_video()
                
        if not self.stop_flag:
            self.progress.set("所有任务完成")
            messagebox.showinfo("完成", "所有任务已完成！")

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            task_type = '分割视频' if task['type'] == 'split' else '合并图片'
            task_name = Path(task['path']).name
            self.task_listbox.insert(tk.END, f"{i+1}. [{task_type}] {task_name}")

    def batch_process(self):
        """批量处理视频"""
        video_paths = filedialog.askopenfilenames(
            filetypes=[("视频文件", "*.mp4 *.mkv *.mov *.avi *.flv *.wmv")]
        )
        if not video_paths:
            return
            
        for video_path in video_paths:
            task = {"path": video_path, "type": "split"}
            self.tasks.append(task)
        
        self.update_task_list()
        
        if messagebox.askyesno("批量处理", f"已添加 {len(video_paths)} 个视频到任务列表。\n是否立即开始处理？"):
            self.start_tasks()


if __name__ == "__main__":
    # 尝试导入PIL，如果失败则提示用户安装
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import tkinter.messagebox as messagebox
        messagebox.showerror("缺少依赖", "需要安装Pillow库来显示视频预览。\n请运行: pip install Pillow")
        sys.exit(1)
    
    root = tk.Tk()
    app = VideoFrameProcessor(root)
    root.mainloop()