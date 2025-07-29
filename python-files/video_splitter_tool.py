import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from moviepy.editor import VideoFileClip
import math

class ModernVideoSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Splitter Tool")
        self.root.geometry("600x450")
        self.root.configure(bg='#1e1e1e')
        
        # Biến lưu trữ
        self.video_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.segment_duration = tk.DoubleVar(value=4.5)  # Mặc định 4.5 giây
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Sẵn sàng")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Style cho ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cấu hình màu sắc
        style.configure('Modern.TFrame', background='#1e1e1e')
        style.configure('Modern.TLabel', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('Title.TLabel', background='#1e1e1e', foreground='#00d4aa', font=('Segoe UI', 16, 'bold'))
        style.configure('Modern.TButton', background='#00d4aa', foreground='#ffffff', font=('Segoe UI', 9, 'bold'))
        style.map('Modern.TButton', 
                 background=[('active', '#00b8a0'), ('pressed', '#009688')])
        
        # Container chính
        main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="🎬 Video Splitter Tool", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Chọn file video
        video_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        video_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(video_frame, text="📁 Chọn file video:", style='Modern.TLabel').pack(anchor=tk.W)
        
        video_input_frame = ttk.Frame(video_frame, style='Modern.TFrame')
        video_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.video_entry = tk.Entry(video_input_frame, textvariable=self.video_path, 
                                   bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 10),
                                   relief=tk.FLAT, bd=5)
        self.video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(video_input_frame, text="Duyệt", style='Modern.TButton',
                               command=self.browse_video)
        browse_btn.pack(side=tk.RIGHT)
        
        # Chọn thư mục output
        output_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        output_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(output_frame, text="📂 Thư mục xuất file:", style='Modern.TLabel').pack(anchor=tk.W)
        
        output_input_frame = ttk.Frame(output_frame, style='Modern.TFrame')
        output_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_entry = tk.Entry(output_input_frame, textvariable=self.output_folder,
                                    bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 10),
                                    relief=tk.FLAT, bd=5)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_btn = ttk.Button(output_input_frame, text="Chọn", style='Modern.TButton',
                               command=self.browse_output)
        output_btn.pack(side=tk.RIGHT)
        
        # Cài đặt thời lượng đoạn
        duration_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        duration_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(duration_frame, text="⏱️ Thời lượng mỗi đoạn (giây):", style='Modern.TLabel').pack(anchor=tk.W)
        
        duration_input = tk.Scale(duration_frame, from_=1.0, to=5.0, resolution=0.1,
                                 variable=self.segment_duration, orient=tk.HORIZONTAL,
                                 bg='#1e1e1e', fg='#ffffff', highlightthickness=0,
                                 troughcolor='#2d2d2d', activebackground='#00d4aa')
        duration_input.pack(fill=tk.X, pady=(5, 0))
        
        # Nút xử lý
        process_btn = ttk.Button(main_frame, text="🚀 Bắt đầu cắt video", 
                                style='Modern.TButton', command=self.start_processing)
        process_btn.pack(pady=20)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                     style='Modern.TLabel', font=('Segoe UI', 9))
        self.status_label.pack(pady=(5, 0))
        
        # Thông tin
        info_text = ("💡 Tool sẽ cắt video thành các đoạn và tự động xóa các file số chẵn (2, 4, 6...)\n"
                    "Chỉ giữ lại các file số lẻ (1, 3, 5, 7...)")
        info_label = ttk.Label(main_frame, text=info_text, style='Modern.TLabel',
                              font=('Segoe UI', 8), justify=tk.CENTER)
        info_label.pack(pady=(20, 0))
        
    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Chọn thư mục xuất file")
        if folder:
            self.output_folder.set(folder)
            
    def start_processing(self):
        if not self.video_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
            return
            
        if not self.output_folder.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục xuất file!")
            return
            
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(target=self.process_video)
        thread.daemon = True
        thread.start()
        
    def process_video(self):
        try:
            self.status_var.set("Đang tải video...")
            self.progress_var.set(0)
            
            # Load video
            video = VideoFileClip(self.video_path.get())
            duration = video.duration
            segment_length = self.segment_duration.get()
            
            # Tính số đoạn
            num_segments = math.ceil(duration / segment_length)
            
            self.status_var.set(f"Đang cắt video thành {num_segments} đoạn...")
            
            created_files = []
            
            # Cắt video thành các đoạn
            for i in range(num_segments):
                start_time = i * segment_length
                end_time = min((i + 1) * segment_length, duration)
                
                # Tạo tên file
                filename = f"{i + 1}.mp4"
                filepath = os.path.join(self.output_folder.get(), filename)
                
                # Cắt đoạn video
                segment = video.subclip(start_time, end_time)
                segment.write_videofile(filepath, verbose=False, logger=None)
                segment.close()
                
                created_files.append((i + 1, filepath))
                
                # Cập nhật progress
                progress = ((i + 1) / num_segments) * 80  # 80% cho việc cắt
                self.progress_var.set(progress)
                self.status_var.set(f"Đã cắt {i + 1}/{num_segments} đoạn...")
                
            video.close()
            
            # Xóa các file số chẵn
            self.status_var.set("Đang xóa các file số chẵn...")
            deleted_files = []
            
            for file_num, filepath in created_files:
                if file_num % 2 == 0:  # Số chẵn
                    try:
                        os.remove(filepath)
                        deleted_files.append(file_num)
                    except Exception as e:
                        print(f"Không thể xóa file {filepath}: {e}")
                        
            self.progress_var.set(100)
            
            # Thông báo hoàn thành
            remaining_files = [num for num, _ in created_files if num % 2 == 1]
            deleted_count = len(deleted_files)
            
            self.status_var.set("Hoàn thành!")
            
            messagebox.showinfo(
                "Hoàn thành", 
                f"✅ Đã cắt video thành công!\n\n"
                f"📁 Tổng số đoạn tạo: {num_segments}\n"
                f"🗑️ Đã xóa {deleted_count} file số chẵn\n"
                f"💾 Còn lại {len(remaining_files)} file số lẻ\n\n"
                f"File được lưu tại: {self.output_folder.get()}"
            )
            
        except Exception as e:
            self.progress_var.set(0)
            self.status_var.set("Có lỗi xảy ra!")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi xử lý video:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ModernVideoSplitter(root)
    
    # Đặt icon và tối ưu hóa window
    try:
        root.iconbitmap(default="")  # Có thể thêm icon nếu có
    except:
        pass
        
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (600 // 2)
    y = (root.winfo_screenheight() // 2) - (450 // 2)
    root.geometry(f"600x450+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()