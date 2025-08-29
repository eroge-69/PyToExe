import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import segyio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
import pandas as pd


class SEGYProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SEGY文件处理器 - Seismic Data Trimmer")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # 变量
        self.input_directory = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.target_position = tk.IntVar(value=1000)
        self.show_plots = tk.BooleanVar(value=True)
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="SEGY文件批量处理工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入目录选择
        ttk.Label(main_frame, text="输入目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_directory, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", 
                  command=self.select_input_directory).grid(row=1, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_directory, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", 
                  command=self.select_output_directory).grid(row=2, column=2, pady=5)
        
        # 参数设置框架
        param_frame = ttk.LabelFrame(main_frame, text="处理参数", padding="10")
        param_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        param_frame.columnconfigure(1, weight=1)
        
        # 目标位置设置
        ttk.Label(param_frame, text="目标触发位置:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(param_frame, from_=100, to=5000, textvariable=self.target_position, 
                   width=20).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        ttk.Label(param_frame, text="采样点").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 显示选项
        ttk.Checkbutton(param_frame, text="显示对比图表", 
                       variable=self.show_plots).grid(row=1, column=0, columnspan=2, 
                                                     sticky=tk.W, pady=5)
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        # 处理按钮
        self.process_button = ttk.Button(control_frame, text="开始处理", 
                                        command=self.start_processing,
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(control_frame, text="停止处理", 
                                     command=self.stop_processing,
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清除日志按钮
        ttk.Button(control_frame, text="清除日志", 
                  command=self.clear_log).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=(10, 5))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def select_input_directory(self):
        """选择输入目录"""
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_directory.set(directory)
            self.log_message(f"已选择输入目录: {directory}")
            
    def select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_directory.set(directory)
            self.log_message(f"已选择输出目录: {directory}")
            
    def log_message(self, message):
        """在日志窗口显示消息"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
        
    def clear_log(self):
        """清除日志"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
        
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_directory.get():
            messagebox.showerror("错误", "请选择输入目录")
            return False
            
        if not self.output_directory.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False
            
        if not os.path.exists(self.input_directory.get()):
            messagebox.showerror("错误", "输入目录不存在")
            return False
            
        # 检查输入目录中是否有SEGY文件
        input_dir = self.input_directory.get()
        segy_files = [f for f in os.listdir(input_dir) if f.endswith('.sgy')]
        if not segy_files:
            messagebox.showerror("错误", "输入目录中没有找到SEGY文件(.sgy)")
            return False
            
        return True
        
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
            
        self.processing = True
        self.process_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # 在新线程中运行处理过程
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
        
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.process_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status("处理已停止")
        self.log_message("处理已被用户停止")
        
    def process_files(self):
        """处理SEGY文件的主函数"""
        try:
            input_dir = self.input_directory.get()
            output_dir = self.output_directory.get()
            target_pos = self.target_position.get()
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取所有SEGY文件
            segy_files = [f for f in os.listdir(input_dir) if f.endswith('.sgy')]
            total_files = len(segy_files)
            
            self.log_message(f"找到 {total_files} 个SEGY文件")
            self.log_message(f"目标触发位置: {target_pos}")
            self.log_message("开始处理...")
            
            for i, file_name in enumerate(segy_files):
                if not self.processing:
                    break
                    
                self.update_status(f"正在处理: {file_name} ({i+1}/{total_files})")
                progress = (i / total_files) * 100
                self.update_progress(progress)
                
                try:
                    self.process_single_file(file_name, input_dir, output_dir, target_pos)
                    self.log_message(f"✓ 已完成: {file_name}")
                except Exception as e:
                    self.log_message(f"✗ 处理失败 {file_name}: {str(e)}")
                    
            if self.processing:
                self.update_progress(100)
                self.update_status("处理完成")
                self.log_message(f"所有文件处理完成! 输出目录: {output_dir}")
                messagebox.showinfo("完成", f"成功处理了 {total_files} 个文件!")
                
        except Exception as e:
            self.log_message(f"处理过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
        finally:
            self.processing = False
            self.process_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def process_single_file(self, file_name, input_dir, output_dir, target_position):
        """处理单个SEGY文件"""
        file_path = os.path.join(input_dir, file_name)
        new_file_path = os.path.join(output_dir, f"Trimmed_{file_name}")
        
        with segyio.open(file_path, "r", ignore_geometry=True) as f:
            num_traces = f.tracecount
            sample_rate = segyio.tools.dt(f) / 1000
            num_samples = f.samples.size
            
            self.log_message(f"  道数: {num_traces}, 采样点数: {num_samples}, 采样率: {sample_rate} ms")
            
            # 获取触发道数据
            trigger_trace = f.trace[0]
            pick_position = np.argmax(np.abs(trigger_trace))
            pick_time = pick_position * sample_rate
            
            self.log_message(f"  触发位置: 采样点 {pick_position}, 时间 {pick_time:.2f} ms")
            
            # 计算偏移量
            offset = target_position - pick_position
            if offset <= 0:
                raise ValueError(f"目标位置 {target_position} 小于等于触发位置 {pick_position}")
                
            # 读取和裁剪所有道
            trace_data = []
            for i in range(num_traces):
                trace = f.trace[i]
                trimmed_trace = trace[-offset:] if offset < len(trace) else trace
                trace_data.append(trimmed_trace)
                
            # 创建新的SEGY文件
            spec = segyio.spec()
            spec.tracecount = num_traces
            spec.samplecount = len(trace_data[0])
            spec.format = f.format
            spec.ext_headers = f.ext_headers
            spec.samples = f.samples[-offset:].tolist()
            
            with segyio.create(new_file_path, spec) as new_file:
                new_file.header[:] = f.header[:]
                for i in range(num_traces):
                    new_file.trace[i] = trace_data[i]
                    
            # 如果启用了图表显示，显示对比图
            if self.show_plots.get():
                self.show_comparison_plot(file_name, f.trace[:], trace_data, f)
                
    def show_comparison_plot(self, file_name, original_traces, trimmed_traces, segy_file):
        """显示原始和裁剪后的对比图"""
        try:
            num_traces = min(4, len(original_traces))  # 最多显示4道
            
            fig, axs = plt.subplots(num_traces, 2, figsize=(12, 2 * num_traces))
            fig.suptitle(f"原始 vs 裁剪后对比 - {file_name}", fontsize=14)
            
            if num_traces == 1:
                axs = axs.reshape(1, -1)
                
            for i in range(num_traces):
                # 获取深度信息
                try:
                    elevation = segy_file.header[i].get(segyio.TraceField.ReceiverGroupElevation, 0)
                    depth_info = f"道 {i}: {elevation/100.0:.2f}m" if elevation != 0 else f"道 {i}"
                except:
                    depth_info = f"道 {i}"
                
                # 原始道
                axs[i, 0].plot(original_traces[i])
                axs[i, 0].set_title(f"原始 - {depth_info}")
                axs[i, 0].set_ylabel("振幅")
                
                # 裁剪后的道
                axs[i, 1].plot(trimmed_traces[i])
                axs[i, 1].set_title(f"裁剪后 - {depth_info}")
                
            plt.xlabel("采样点索引")
            plt.tight_layout()
            plt.show(block=False)  # 非阻塞显示
            
        except Exception as e:
            self.log_message(f"显示图表时出错: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置应用程序图标和样式
    try:
        # 使用现代化的ttk样式
        style = ttk.Style()
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        elif 'clam' in style.theme_names():
            style.theme_use('clam')
    except:
        pass
        
    app = SEGYProcessorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("退出", "正在处理文件，确定要退出吗？"):
                app.processing = False
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()