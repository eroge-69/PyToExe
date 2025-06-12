import subprocess
import re
import time
import threading
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import queue
import os
import platform
from PIL import Image, ImageTk
import io
from bs4 import BeautifulSoup
import traceback
import logging
import csv
import json

# Thiết lập logging
logging.basicConfig(filename='error.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# Kiểm tra phụ thuộc
def check_requirements():
    try:
        import requests
        import bs4
        import PIL
    except ImportError as e:
        print(f"Missing Python library: {e.name}")
        print("Run: pip install requests beautifulsoup4 pillow")
        return False
    for cmd in ['yt-dlp', 'ffmpeg', 'ffprobe']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Missing tool: {cmd}")
            print(f"Install {cmd} and add to PATH")
            return False
    return True

class MonitorApp:
    def __init__(self, root):
        try:
            if not check_requirements():
                raise Exception("Missing requirements. Check console for details.")
            self.root = root
            self.root.title("Livestream FPS Monitor")
            self.root.resizable(True, True)
            self.configs = []  # Initialize as empty list
            self.entries = []
            self.threads = []
            self.stop_events = {}
            self.popup_queue = queue.Queue()
            self.running = False
            self.monitor_status = {}
            self.status_labels = {}
            self.stream_summary = {}
            self.log_lock = threading.Lock()
            self.blink_state = True
            self.photo_references = []
            self.is_maximized = False
            self.csv_file = "stream_configs.csv"
            self.max_log_lines = 1000  # Maximum number of log lines to keep

            # Cấu hình grid cho root
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

            # Main container
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
            self.main_frame.grid_rowconfigure(0, weight=2)
            self.main_frame.grid_rowconfigure(1, weight=1)
            self.main_frame.grid_rowconfigure(2, weight=2)
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(2, weight=0)

            # Canvas và Scrollbar cho mục nhập luồng
            self.stream_canvas = tk.Canvas(self.main_frame)
            self.stream_v_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.stream_canvas.yview)
            self.stream_h_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.stream_canvas.xview)
            self.stream_canvas.configure(yscrollcommand=self.stream_v_scrollbar.set, xscrollcommand=self.stream_h_scrollbar.set)
            self.stream_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.stream_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.stream_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

            # Frame cho mục nhập luồng
            self.frame = ttk.Frame(self.stream_canvas, padding="10")
            self.frame_id = self.stream_canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)
            for col in range(8):
                self.frame.grid_columnconfigure(col, weight=1)

            # Nhãn cho các cột
            ttk.Label(self.frame, text="Stream").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="Title").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="Thumbnail").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="YouTube URL").grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="FPS Drop %").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="Slack User ID").grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="Status").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text="Add/Remove").grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)

            # Khung cho các nút cố định
            self.button_frame = ttk.Frame(self.main_frame)
            self.button_frame.grid(row=0, column=2, sticky=(tk.N, tk.E), padx=5, pady=5)
            self.start_button = ttk.Button(self.button_frame, text="Start Monitoring", command=self.start_monitoring)
            self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
            self.stop_button = ttk.Button(self.button_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
            self.stop_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
            self.get_info_button = ttk.Button(self.button_frame, text="Get Title & Thumbnail", command=self.update_titles_thumbnails)
            self.get_info_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)

            # Khung log
            self.log_frame = ttk.Frame(self.main_frame, padding="10")
            self.log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.log_frame.grid_rowconfigure(0, weight=1)
            self.log_frame.grid_columnconfigure(0, weight=1)
            self.log_text = tk.Text(self.log_frame, height=10, state='disabled')
            self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            log_scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
            log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.log_text['yscrollcommand'] = log_scrollbar.set

            # Canvas và Scrollbar cho bảng tóm tắt
            self.summary_canvas = tk.Canvas(self.main_frame)
            self.summary_v_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.summary_canvas.yview)
            self.summary_h_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.summary_canvas.xview)
            self.summary_canvas.configure(yscrollcommand=self.summary_v_scrollbar.set, xscrollcommand=self.summary_h_scrollbar.set)
            self.summary_canvas.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.summary_v_scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
            self.summary_h_scrollbar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

            # Frame cho bảng tóm tắt
            self.summary_frame = ttk.Frame(self.summary_canvas, padding="10")
            self.summary_frame_id = self.summary_canvas.create_window((0, 0), window=self.summary_frame, anchor=tk.NW)
            for col in range(5):
                self.summary_frame.grid_columnconfigure(col, weight=1)

            # Nhãn cho bảng tóm tắt
            ttk.Label(self.summary_frame, text="Stream").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.summary_frame, text="Thumbnail").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.summary_frame, text="FPS").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.summary_frame, text="Status").grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.summary_frame, text="Indicator").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

            # Load configurations from CSV
            self.load_configs_from_csv()

            # Thêm một mục nhập mặc định nếu không có config nào được load
            if not self.entries:
                self.add_entry()

            # Bind sự kiện
            self.frame.bind("<Configure>", self.update_stream_scrollregion)
            self.summary_frame.bind("<Configure>", self.update_summary_scrollregion)
            self.root.bind("<Configure>", self.update_layout)
            self.bind_mouse_wheel()

            # Cập nhật trạng thái
            self.root.after(1000, self.update_monitor_status)
            self.root.after(500, self.blink_indicators)
            self.root.after(100, self.process_popup_queue)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Đặt kích thước ban đầu
            self.root.geometry("1200x800")
        except Exception as e:
            logging.error(f"Error in __init__: {str(e)}\n{traceback.format_exc()}")
            messagebox.showerror("Startup Error", f"Failed to start application. Check error.log for details.")
            raise

    def load_configs_from_csv(self):
        try:
            if os.path.exists(self.csv_file):
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    entries_data = []
                    self.configs = []
                    for idx, row in enumerate(reader):
                        entries_data.append((idx, row['youtube_url'], row['fps_drop_percent'], row['manager_id']))
                        self.configs.append({
                            'youtube_url': row['youtube_url'],
                            'manager_id': row['manager_id'],
                            'fps_drop_percent': float(row['fps_drop_percent']) if row['fps_drop_percent'] else 0.0,
                            'title': row.get('title', ''),
                            'thumbnail_url': row.get('thumbnail_url', ''),
                            'thumbnail': None
                        })
                    if entries_data:
                        self.refresh_ui(entries_data)
                        self.log_message(f"Đã tải {len(entries_data)} cấu hình từ {self.csv_file}")
                        # Cập nhật titles và thumbnails sau khi load
                        self.update_titles_thumbnails()
            else:
                self.log_message(f"Không tìm thấy file {self.csv_file}, bắt đầu với cấu hình mặc định")
        except Exception as e:
            self.log_message(f"Lỗi khi tải cấu hình từ CSV: {str(e)}")
            logging.error(f"Error in load_configs_from_csv: {str(e)}\n{traceback.format_exc()}")

    def save_configs_to_csv(self):
        try:
            self.update_configs()
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['youtube_url', 'fps_drop_percent', 'manager_id', 'title', 'thumbnail_url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for config in self.configs:
                    writer.writerow({
                        'youtube_url': config['youtube_url'],
                        'fps_drop_percent': config['fps_drop_percent'],
                        'manager_id': config['manager_id'],
                        'title': config['title'],
                        'thumbnail_url': config['thumbnail_url']
                    })
            self.log_message(f"Đã lưu cấu hình vào {self.csv_file}")
        except Exception as e:
            self.log_message(f"Lỗi khi lưu cấu hình vào CSV: {str(e)}")
            logging.error(f"Error in save_configs_to_csv: {str(e)}\n{traceback.format_exc()}")

    def bind_mouse_wheel(self):
        def stream_scroll_y(event):
            self.stream_canvas.yview_scroll(int(-1 * (event.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if event.num == 4 else 1, "units")
            return "break"

        def stream_scroll_x(event):
            self.stream_canvas.xview_scroll(int(-1 * (event.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if event.num == 4 else 1, "units")
            return "break"

        def summary_scroll_y(event):
            self.summary_canvas.yview_scroll(int(-1 * (event.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if event.num == 4 else 1, "units")
            return "break"

        def summary_scroll_x(event):
            self.summary_canvas.xview_scroll(int(-1 * (event.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if event.num == 4 else 1, "units")
            return "break"

        # Bind cho stream_canvas, frame và các widget con
        for widget in [self.stream_canvas, self.frame]:
            widget.bind("<MouseWheel>", stream_scroll_y)
            widget.bind("<Shift-MouseWheel>", stream_scroll_x)
            if platform.system() == "Linux":
                widget.bind("<Button-4>", stream_scroll_y)
                widget.bind("<Button-5>", stream_scroll_y)
                widget.bind("<Shift-Button-4>", stream_scroll_x)
                widget.bind("<Shift-Button-5>", stream_scroll_x)

        # Bind cho summary_canvas
        self.summary_canvas.bind("<MouseWheel>", summary_scroll_y)
        self.summary_canvas.bind("<Shift-MouseWheel>", summary_scroll_x)
        if platform.system() == "Linux":
            self.summary_canvas.bind("<Button-4>", summary_scroll_y)
            self.summary_canvas.bind("<Button-5>", summary_scroll_y)
            self.summary_canvas.bind("<Shift-Button-4>", summary_scroll_x)
            self.summary_canvas.bind("<Shift-Button-5>", summary_scroll_x)

        # Bind cho các widget con trong frame
        for i, (idx, url_entry, fps_entry, manager_entry, status_label, thumbnail_label, add_button, remove_button) in enumerate(self.entries):
            for child in [url_entry, fps_entry, manager_entry, status_label, thumbnail_label, add_button, remove_button]:
                child.bind("<MouseWheel>", stream_scroll_y)
                child.bind("<Shift-MouseWheel>", stream_scroll_x)
                if platform.system() == "Linux":
                    child.bind("<Button-4>", stream_scroll_y)
                    child.bind("<Button-5>", stream_scroll_y)
                    child.bind("<Shift-Button-4>", stream_scroll_x)
                    child.bind("<Shift-Button-5>", stream_scroll_x)

    def update_stream_scrollregion(self, event=None):
        self.stream_canvas.configure(scrollregion=self.stream_canvas.bbox("all"))

    def update_summary_scrollregion(self, event=None):
        self.summary_canvas.configure(scrollregion=self.summary_canvas.bbox("all"))

    def update_layout(self, event=None):
        if platform.system() == "Windows":
            if self.root.state() == 'zoomed' and not self.is_maximized:
                self.is_maximized = True
                self.log_message("Cửa sổ đã được phóng to toàn màn hình.")
            elif self.root.state() != 'zoomed' and self.is_maximized:
                self.is_maximized = False
                self.log_message("Cửa sổ đã được khôi phục kích thước.")
        else:  # Linux/macOS
            try:
                zoomed = self.root.attributes('-zoomed')
                if zoomed and not self.is_maximized:
                    self.is_maximized = True
                    self.log_message("Cửa sổ đã được phóng to toàn màn hình.")
                elif not zoomed and self.is_maximized:
                    self.is_maximized = False
                    self.log_message("Cửa sổ đã được khôi phục kích thước.")
            except:
                pass
        self.update_stream_scrollregion()
        self.update_summary_scrollregion()

    def log_message(self, message):
        with self.log_lock:
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            # Check and trim log if it exceeds max lines
            line_count = int(self.log_text.index('end-1c').split('.')[0]) - 1
            if line_count > self.max_log_lines:
                self.log_text.delete('1.0', f"{line_count - self.max_log_lines + 1}.0")
            self.log_text.config(state='disabled')
            self.log_text.see(tk.END)

    def get_youtube_video_info(self, video_url, thread_name):
        if not video_url.startswith(('http://', 'https://')):
            self.log_message(f"[{thread_name}] URL không hợp lệ: {video_url}")
            return {"title": "URL không hợp lệ", "thumbnail": None, "thumbnail_url": ""}
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            response = requests.get(video_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find("meta", property="og:title")
            title = title_tag["content"] if title_tag else "Không tìm thấy tiêu đề"
            thumbnail_tag = soup.find("link", rel="image_src")
            thumbnail_url = thumbnail_tag["href"] if thumbnail_tag else ""
            thumbnail = None
            if thumbnail_url:
                resp = requests.get(thumbnail_url, stream=True, timeout=10)
                resp.raise_for_status()
                img = Image.open(io.BytesIO(resp.content))
                img = img.resize((128, 72), Image.Resampling.LANCZOS)  # Changed to 128x72 (16:9)
                thumbnail = ImageTk.PhotoImage(img)
                self.photo_references.append(thumbnail)
            self.log_message(f"[{thread_name}] Đã tải: {title}, Thumbnail: {thumbnail_url}")
            return {
                "title": title,
                "thumbnail": thumbnail,
                "thumbnail_url": thumbnail_url
            }
        except requests.Timeout:
            self.log_message(f"[{thread_name}] Lỗi: Hết thời gian tải URL.")
            return {"title": "Timeout", "thumbnail": None, "thumbnail_url": ""}
        except requests.HTTPError as e:
            self.log_message(f"[{thread_name}] Lỗi HTTP: {e}")
            return {"title": "Lỗi HTTP", "thumbnail": None, "thumbnail_url": ""}
        except Exception as e:
            self.log_message(f"[{thread_name}] Lỗi không xác định: {e}")
            return {"title": "Lỗi", "thumbnail": None, "thumbnail_url": ""}

    def check_livestream_status(self, youtube_url, thread_name):
        creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        try:
            result = subprocess.run(
                ['yt-dlp', '--get-id', '--skip-download', youtube_url],
                capture_output=True, text=True, check=True, creationflags=creation_flags
            )
            self.log_message(f"[{thread_name}] Livestream đang hoạt động.")
            return True
        except subprocess.CalledProcessError:
            self.log_message(f"[{thread_name}] Livestream không hoạt động hoặc offline.")
            return False
        except Exception as e:
            self.log_message(f"[{thread_name}] Lỗi kiểm tra livestream: {e}")
            return False

    def show_video_details(self, thread_name, url):
        info = self.get_youtube_video_info(url, thread_name)
        window = tk.Toplevel(self.root)
        window.title(f"Chi tiết {thread_name}")
        ttk.Label(window, text=f"Tiêu đề: {info['title']}").pack(padx=10, pady=5)
        if info["thumbnail"]:
            ttk.Label(window, image=info["thumbnail"]).pack(padx=10, pady=5)

    def update_titles_thumbnails(self):
        try:
            self.update_configs()
            self.photo_references = []
            
            while len(self.configs) < len(self.entries):
                self.configs.append({
                    'youtube_url': '',
                    'manager_id': '',
                    'fps_drop_percent': 0.0,
                    'title': '',
                    'thumbnail_url': '',
                    'thumbnail': None
                })

            for i, (idx, url_entry, _, _, _, thumbnail_label, _, _) in enumerate(self.entries):
                thread_name = f"Stream-{i+1}"
                url = url_entry.get().strip()
                if url:
                    info = self.get_youtube_video_info(url, thread_name)
                    self.configs[i]['title'] = info['title']
                    self.configs[i]['thumbnail_url'] = info['thumbnail_url']
                    self.configs[i]['thumbnail'] = info['thumbnail']
                    title_label = self.frame.grid_slaves(row=i+1, column=1)[0]
                    title_label.config(text=info['title'])
                    thumbnail_label.config(image=info['thumbnail'])
                    thumbnail_label.image = info['thumbnail']
                    if thread_name in self.stream_summary:
                        self.stream_summary[thread_name]["thumbnail_label"].config(image=info['thumbnail'])
                        self.stream_summary[thread_name]["thumbnail_label"].image = info['thumbnail']
                    # Bind sự kiện cuộn chuột cho widget mới
                    for widget in [url_entry, thumbnail_label, title_label]:
                        widget.bind("<MouseWheel>", lambda e: self.stream_canvas.yview_scroll(int(-1 * (e.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if e.num == 4 else 1, "units"))
                        widget.bind("<Shift-MouseWheel>", lambda e: self.stream_canvas.xview_scroll(int(-1 * (e.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if e.num == 4 else 1, "units"))
                        if platform.system() == "Linux":
                            widget.bind("<Button-4>", lambda e: self.stream_canvas.yview_scroll(-1, "units"))
                            widget.bind("<Button-5>", lambda e: self.stream_canvas.yview_scroll(1, "units"))
                            widget.bind("<Shift-Button-4>", lambda e: self.stream_canvas.xview_scroll(-1, "units"))
                            widget.bind("<Shift-Button-5>", lambda e: self.stream_canvas.xview_scroll(1, "units"))
            self.log_message("Đã cập nhật tiêu đề và thumbnail cho tất cả luồng.")
            
            # Đảm bảo binding và focus
            self.bind_mouse_wheel()
            self.stream_canvas.focus_set()
            self.frame.focus_set()
            self.log_message("Đã đặt lại focus và binding cuộn chuột cho bảng nhập luồng.")
        except Exception as e:
            logging.error(f"Error in update_titles_thumbnails: {str(e)}\n{traceback.format_exc()}")
            self.log_message(f"Lỗi cập nhật tiêu đề/thumbnail: {e}")

    def get_m3u8_url(self, youtube_url, thread_name, max_retries=3, retry_delay=10):
        creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    ['yt-dlp', '-g', youtube_url],
                    capture_output=True, text=True, check=True, timeout=15,
                    creationflags=creation_flags
                )
                urls = result.stdout.strip().split('\n')
                for url in urls:
                    if '.m3u8' in url:
                        self.log_message(f"[{thread_name}] Lấy được link m3u8: {url}")
                        return url
                self.log_message(f"[{thread_name}] Không tìm thấy link m3u8 trong đầu ra.")
                return None
            except subprocess.CalledProcessError as e:
                self.log_message(f"[{thread_name}] Lỗi khi lấy link m3u8 (lần {attempt+1}/{max_retries}): {e.stderr}")
                if attempt < max_retries - 1:
                    self.log_message(f"[{thread_name}] Thử lại sau {retry_delay} giây...")
                    time.sleep(retry_delay)
            except Exception as e:
                self.log_message(f"[{thread_name}] Lỗi lấy m3u8: {e}")
                return None
        self.log_message(f"[{thread_name}] Hết số lần thử lấy link m3u8.")
        return None

    def get_fps_metadata(self, stream_url, thread_name, max_retries=3, retry_delay=10):
        creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        self.log_message(f"[{thread_name}] Đọc FPS khai báo (metadata)...")
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=r_frame_rate", "-of", "json", stream_url],
                    capture_output=True, text=True, timeout=10,
                    creationflags=creation_flags
                )
                data = json.loads(result.stdout)
                fps_expr = data["streams"][0]["r_frame_rate"]
                fps = eval(fps_expr) if "/" in fps_expr else float(fps_expr)
                self.log_message(f"[{thread_name}] FPS metadata (khai báo): {fps:.2f}")
                return fps
            except Exception as e:
                self.log_message(f"[{thread_name}] Lỗi đọc metadata (lần {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    self.log_message(f"[{thread_name}] Thử lại sau {retry_delay} giây...")
                    time.sleep(retry_delay)
        self.log_message(f"[{thread_name}] Hết số lần thử lấy FPS metadata.")
        return None

    def send_slack_alert(self, user_id, youtube_url, stop_event, thread_name):
        while not stop_event.is_set():
            now = time.strftime('%H:%M:%S')
            message = f"<@{user_id}> | STREAM LAG | {youtube_url} | {now}"
            try:
                requests.post(SLACK_WEBHOOK_URL, json={"text": message})
                self.log_message(f"[{thread_name}] Đã gửi cảnh báo Slack: {message}")
            except Exception as e:
                self.log_message(f"[{thread_name}] Lỗi gửi Slack: {e}")
            for _ in range(20):
                if stop_event.is_set():
                    break
                time.sleep(1)

    def monitor_loop(self, stream_url, ref_fps, fps_drop_percent, youtube_url, user_id, thread_name, popup_queue, stop_event, status_callback):
        creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        self.log_message(f"[{thread_name}] Bắt đầu theo dõi FPS liên tục...")
        
        while not stop_event.is_set():
            try:
                process = subprocess.Popen(
                    ["ffmpeg", "-i", stream_url, "-f", "null", "-"],
                    stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, bufsize=1,
                    creationflags=creation_flags
                )

                frame_pattern = re.compile(r"frame=\s*(\d+)")
                last_frame = 0
                last_time = time.time()
                bad_fps_counter = 0
                alert_triggered = False
                slack_stop_event = threading.Event()
                reset_event = threading.Event()
                first_measure = True
                no_signal_counter = 0

                for line in process.stderr:
                    if stop_event.is_set() or reset_event.is_set():
                        self.log_message(f"[{thread_name}] Đã dừng/reset trạng thái theo dõi.")
                        status_callback(thread_name, "", 0.0, "No Signal")
                        break

                    match = frame_pattern.search(line)
                    if match:
                        no_signal_counter = 0
                        current_frame = int(match.group(1))
                        now = time.time()
                        elapsed = now - last_time

                        if elapsed >= 5.0:
                            frames_received = current_frame - last_frame
                            current_fps = frames_received / elapsed
                            last_frame = current_frame
                            last_time = now
                            now_str = datetime.now().strftime("%H:%M:%S")

                            if first_measure:
                                self.log_message(f"[{thread_name}] [{now_str}] Đang chờ ổn định stream...")
                                first_measure = False
                                continue

                            fps_threshold = ref_fps * (1 - fps_drop_percent / 100)
                            if current_fps < fps_threshold:
                                self.log_message(f"[{thread_name}] [{now_str}] FPS giảm mạnh: {current_fps:.2f} < {fps_threshold:.2f}")
                                bad_fps_counter += 1
                                status = "Lag"
                            else:
                                self.log_message(f"[{thread_name}] [{now_str}] FPS ổn định: {current_fps:.2f}")
                                bad_fps_counter = 0
                                status = "Stable"

                            status_callback(thread_name, "", current_fps, status)

                            if bad_fps_counter >= 2 and not alert_triggered:
                                alert_triggered = True
                                slack_stop_event.clear()
                                threading.Thread(target=self.send_slack_alert, args=(user_id, youtube_url, slack_stop_event, thread_name), daemon=True).start()
                                self.log_message(f"[{thread_name}] Đã kích hoạt cảnh báo Slack và thêm yêu cầu popup vào hàng đợi...")
                                popup_queue.put((thread_name, youtube_url, current_fps, fps_threshold, reset_event))
                    else:
                        now = time.time()
                        elapsed = now - last_time
                        if elapsed >= 5.0:
                            no_signal_counter += 1
                            now_str = datetime.now().strftime("%H:%M:%S")
                            self.log_message(f"[{thread_name}] [{now_str}] Không nhận được khung hình.")
                            status_callback(thread_name, "", 0.0, "No Signal")
                            if no_signal_counter >= 2 and not alert_triggered:
                                alert_triggered = True
                                slack_stop_event.clear()
                                threading.Thread(target=self.send_slack_alert, args=(user_id, youtube_url, slack_stop_event, thread_name), daemon=True).start()
                                self.log_message(f"[{thread_name}] Đã kích hoạt cảnh báo Slack do mất tín hiệu.")
                                popup_queue.put((thread_name, youtube_url, 0.0, ref_fps, reset_event))
                            last_time = now

            except Exception as e:
                self.log_message(f"[{thread_name}] Lỗi khi theo dõi: {e}")
                status_callback(thread_name, "", 0.0, "No Signal")
            finally:
                if 'process' in locals():
                    process.kill()
                if 'reset_event' in locals() and reset_event.is_set():
                    slack_stop_event.set()
                status_callback(thread_name, "", 0.0, "No Signal")

    def start_monitor_thread(self, config, index, popup_queue, stop_event, status_callback):
        thread_name = f"Stream-{index+1}"
        youtube_url = config['youtube_url']
        manager_id = config['manager_id']
        fps_drop_percent = config['fps_drop_percent']

        if not self.check_livestream_status(youtube_url, thread_name):
            status_callback(thread_name, "", 0.0, "Offline")
            return

        m3u8_url = self.get_m3u8_url(youtube_url, thread_name)
        if not m3u8_url:
            self.log_message(f"[{thread_name}] Không lấy được link m3u8. Thoát.")
            status_callback(thread_name, "", 0.0, "No Signal")
            return

        ref_fps = self.get_fps_metadata(m3u8_url, thread_name)
        if not ref_fps:
            self.log_message(f"[{thread_name}] Không lấy được FPS metadata. Thoát.")
            status_callback(thread_name, "", 0.0, "No Signal")
            return

        self.monitor_loop(m3u8_url, ref_fps, fps_drop_percent, youtube_url, manager_id, thread_name, popup_queue, stop_event, status_callback)

    def add_entry(self, load_config=False, insert_index=None):
        self.update_configs()
        entries_data = [(i, e[1].get(), e[2].get(), e[3].get()) for i, e in enumerate(self.entries)]
        if not load_config:
            new_index = insert_index if insert_index is not None else len(self.entries)
            entries_data.insert(new_index, (new_index, '', '', ''))
            self.configs.insert(new_index, {
                'youtube_url': '',
                'manager_id': '',
                'fps_drop_percent': 0.0,
                'title': '',
                'thumbnail_url': '',
                'thumbnail': None
            })
        self.refresh_ui(entries_data)
        if self.running:
            self.start_button.config(state=tk.NORMAL)
        self.log_message(f"Đã thêm luồng tại vị trí {(insert_index if insert_index is not None else len(self.entries))+1}")

    def remove_stream(self, index):
        if len(self.entries) <= 1:
            messagebox.showwarning("Warning", "At least one stream entry is required!")
            return
        if self.running:
            messagebox.showwarning("Warning", "Cannot remove stream while monitoring!")
            return

        self.update_configs()
        entries_data = [(i, e[1].get(), e[2].get(), e[3].get()) for i, e in enumerate(self.entries) if i != index]
        if index < len(self.configs):
            self.configs.pop(index)
        self.refresh_ui(entries_data)
        self.update_configs()
        self.save_configs_to_csv()  # Save after removing stream
        self.log_message(f"Đã xóa luồng tại vị trí {index+1}")

    def refresh_ui(self, entries_data):
        # Xóa các widget liên quan đến luồng (row >= 1)
        for row in range(1, len(self.entries) + 1):
            for col in range(8):
                for widget in self.frame.grid_slaves(row=row, column=col):
                    widget.destroy()

        # Xóa bảng tóm tắt
        for row in range(1, len(self.stream_summary) + 1):
            for widget in self.summary_frame.grid_slaves(row=row):
                widget.destroy()

        self.entries = []
        self.monitor_status = {}
        self.status_labels = {}
        self.stream_summary = {}

        for idx, (index, url, fps, manager) in enumerate(entries_data):
            N = idx + 1
            row = N
            thread_name = f"Stream-{N}"
            info = next((cfg for cfg in self.configs if cfg.get('youtube_url') == url), 
                        {'title': '', 'thumbnail': None, 'thumbnail_url': ''})
            if info.get('thumbnail') and info['thumbnail'] not in self.photo_references:
                self.photo_references.append(info['thumbnail'])
            ttk.Label(self.frame, text=f"Stream {N}").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Label(self.frame, text=info.get('title', '')).grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            thumbnail_label = ttk.Label(self.frame, image=info.get('thumbnail'))
            thumbnail_label.grid(row=row, column=2, padx=5, pady=5, sticky=tk.W)
            thumbnail_label.image = info.get('thumbnail')
            if url:
                thumbnail_label.bind("<Button-1>", lambda e, tn=thread_name, u=url: self.show_video_details(tn, u))
            url_entry = ttk.Entry(self.frame)
            url_entry.grid(row=row, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
            url_entry.insert(0, url)
            fps_entry = ttk.Entry(self.frame, width=10)
            fps_entry.grid(row=row, column=4, padx=5, pady=5, sticky=tk.W)
            fps_entry.insert(0, fps)
            manager_entry = ttk.Entry(self.frame, width=20)
            manager_entry.grid(row=row, column=5, padx=5, pady=5, sticky=tk.W)
            manager_entry.insert(0, manager)
            status_label = ttk.Label(self.frame, text="", foreground="green")
            status_label.grid(row=row, column=6, padx=5, pady=5, sticky=tk.W)
            
            # Thêm cả nút "+" và "-" trong cột Add/Remove
            button_frame = ttk.Frame(self.frame)
            button_frame.grid(row=row, column=7, padx=5, pady=5, sticky=tk.W)
            add_button = ttk.Button(button_frame, text="+", command=lambda idx=index: self.add_entry(insert_index=idx+1))
            add_button.grid(row=0, column=0, padx=2)
            remove_button = ttk.Button(button_frame, text="-", command=lambda idx=index: self.remove_stream(idx), 
                                      state=tk.DISABLED if self.running else tk.NORMAL)
            remove_button.grid(row=0, column=1, padx=2)

            self.entries.append((index, url_entry, fps_entry, manager_entry, status_label, thumbnail_label, add_button, remove_button))
            self.monitor_status[thread_name] = ""
            self.status_labels[thread_name] = status_label

            # Bind sự kiện cuộn chuột cho các widget con
            for widget in [url_entry, fps_entry, manager_entry, status_label, thumbnail_label, add_button, remove_button]:
                widget.bind("<MouseWheel>", lambda e: self.stream_canvas.yview_scroll(int(-1 * (e.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if e.num == 4 else 1, "units"))
                widget.bind("<Shift-MouseWheel>", lambda e: self.stream_canvas.xview_scroll(int(-1 * (e.delta / 120)) if platform.system() in ["Windows", "Darwin"] else -1 if e.num == 4 else 1, "units"))
                if platform.system() == "Linux":
                    widget.bind("<Button-4>", lambda e: self.stream_canvas.yview_scroll(-1, "units"))
                    widget.bind("<Button-5>", lambda e: self.stream_canvas.yview_scroll(1, "units"))
                    widget.bind("<Shift-Button-4>", lambda e: self.stream_canvas.xview_scroll(-1, "units"))
                    widget.bind("<Shift-Button-5>", lambda e: self.stream_canvas.xview_scroll(1, "units"))

            summary_row = idx + 1
            ttk.Label(self.summary_frame, text=f"Stream {N}").grid(row=summary_row, column=0, padx=5, pady=5, sticky=tk.W)
            summary_thumbnail_label = ttk.Label(self.summary_frame, image=info.get('thumbnail'))
            summary_thumbnail_label.grid(row=summary_row, column=1, padx=5, pady=5, sticky=tk.W)
            summary_thumbnail_label.image = info.get('thumbnail')
            if url:
                summary_thumbnail_label.bind("<Button-1>", lambda e, tn=thread_name, u=url: self.show_video_details(tn, u))
            fps_label = ttk.Label(self.summary_frame, text="0.00")
            fps_label.grid(row=summary_row, column=2, padx=5, pady=5, sticky=tk.W)
            status_label = ttk.Label(self.summary_frame, text="No Signal")
            status_label.grid(row=summary_row, column=3, padx=5, pady=5, sticky=tk.W)
            canvas = tk.Canvas(self.summary_frame, width=20, height=20)
            canvas.grid(row=summary_row, column=4, padx=5, pady=5, sticky=tk.W)
            indicator_id = canvas.create_oval(5, 5, 15, 15, fill="red")
            self.stream_summary[thread_name] = {
                'fps_label': fps_label,
                'status_label': status_label,
                'canvas': canvas,
                'indicator_id': indicator_id,
                'thumbnail_label': summary_thumbnail_label,
                'fps': 0.0,
                'status': 'No Signal',
                'color': 'red'
            }

        self.update_stream_scrollregion()
        self.update_summary_scrollregion()
        self.bind_mouse_wheel()

    def update_configs(self):
        updated_configs = []
        for idx, url_entry, fps_entry, manager_entry, _, _, _, _ in self.entries:
            youtube_url = url_entry.get().strip()
            fps_drop_percent = fps_entry.get().strip()
            manager_id = manager_entry.get().strip()
            
            existing_config = next((cfg for cfg in self.configs if cfg.get('youtube_url') == youtube_url), None)
            
            config = {
                'youtube_url': youtube_url,
                'manager_id': manager_id,
                'fps_drop_percent': float(fps_drop_percent) if fps_drop_percent else 0.0,
                'title': existing_config.get('title', '') if existing_config else '',
                'thumbnail_url': existing_config.get('thumbnail_url', '') if existing_config else '',
                'thumbnail': existing_config.get('thumbnail', None) if existing_config else None
            }
            updated_configs.append(config)
        
        self.configs = updated_configs

    def validate_config(self):
        for idx, url_entry, fps_entry, manager_entry, _, _, _, _ in self.entries:
            youtube_url = url_entry.get().strip()
            fps_drop_percent = fps_entry.get().strip()
            manager_id = manager_entry.get().strip()
            if not (youtube_url and fps_drop_percent and manager_id):
                messagebox.showerror("Error", "Please fill in all fields!")
                return False
            try:
                fps_drop = float(fps_drop_percent)
                if not (0 <= fps_drop <= 100):
                    messagebox.showerror("Error", "FPS drop % must be between 0 and 100!")
                    return False
            except ValueError:
                messagebox.showerror("Error", "FPS drop % must be a valid number!")
                return False
        return True

    def start_monitoring(self):
        self.stop_monitoring()

        if not self.validate_config():
            return

        self.update_configs()
        self.save_configs_to_csv()  # Save configs to CSV before starting monitoring

        if not self.configs:
            messagebox.showerror("Error", "No valid configurations provided!")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.get_info_button.config(state=tk.DISABLED)
        for _, _, _, _, _, _, _, remove_button in self.entries:
            remove_button.config(state=tk.DISABLED)

        self.threads = []
        self.stop_events = {}
        for i, config in enumerate(self.configs):
            thread_name = f"Stream-{i+1}"
            stop_event = threading.Event()
            self.stop_events[thread_name] = stop_event
            t = threading.Thread(
                target=self.start_monitor_thread,
                args=(config, i, self.popup_queue, stop_event, self.update_status_callback),
                daemon=True
            )
            t.start()
            self.threads.append(t)
            self.monitor_status[thread_name] = "o"

        self.log_message(f"Đang chạy {len(self.threads)} luồng theo dõi livestream song song.")
        self.log_message("Đã vô hiệu hóa nút Get Title & Thumbnail trong lúc giám sát.")

    def stop_monitoring(self):
        if not self.running:
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to stop monitoring?"):
            return

        for thread_name, stop_event in self.stop_events.items():
            stop_event.set()
            self.monitor_status[thread_name] = ""
            if thread_name in self.status_labels:
                self.status_labels[thread_name].config(text="")
            if thread_name in self.stream_summary:
                self.stream_summary[thread_name]["fps"] = 0.0
                self.stream_summary[thread_name]["status"] = "No Signal"
                self.stream_summary[thread_name]["color"] = "red"
                self.stream_summary[thread_name]["fps_label"].config(text="0.00")
                self.stream_summary[thread_name]["status_label"].config(text="No Signal")
                self.stream_summary[thread_name]["canvas"].itemconfig(
                    self.stream_summary[thread_name]["indicator_id"], fill="red"
                )
        self.threads = []
        self.stop_events = {}
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.get_info_button.config(state=tk.NORMAL)
        for _, _, _, _, _, _, _, remove_button in self.entries:
            remove_button.config(state=tk.NORMAL)
        self.log_message("Đã dừng tất cả luồng giám sát.")
        self.log_message("Đã kích hoạt lại nút Get Title & Thumbnail.")

    def update_status_callback(self, thread_name, status, fps, stream_status):
        with self.log_lock:
            self.monitor_status[thread_name] = status
            if thread_name in self.status_labels:
                self.status_labels[thread_name].config(text=status)
            if thread_name in self.stream_summary:
                self.stream_summary[thread_name]["fps"] = fps
                self.stream_summary[thread_name]["status"] = stream_status
                self.stream_summary[thread_name]["fps_label"].config(text=f"{fps:.2f}")
                self.stream_summary[thread_name]["status_label"].config(text=stream_status)
                if stream_status == "Stable":
                    self.stream_summary[thread_name]["color"] = "green"
                elif stream_status == "Lag":
                    self.stream_summary[thread_name]["color"] = "yellow"
                elif stream_status == "Offline":
                    self.stream_summary[thread_name]["color"] = "red"
                else:
                    self.stream_summary[thread_name]["color"] = "red"

    def blink_indicators(self):
        self.blink_state = not self.blink_state
        for thread_name, summary in self.stream_summary.items():
            color = summary["color"] if self.blink_state else "gray"
            summary["canvas"].itemconfig(summary["indicator_id"], fill=color)
        self.root.after(500, self.blink_indicators)

    def update_monitor_status(self):
        if self.running:
            for thread_name in self.monitor_status:
                if thread_name in self.stop_events and not self.stop_events[thread_name].is_set():
                    current = self.monitor_status.get(thread_name, "")
                    if current == "":
                        self.monitor_status[thread_name] = "o"
                    elif current == "o":
                        self.monitor_status[thread_name] = "oo"
                    elif current == "oo":
                        self.monitor_status[thread_name] = "ooo"
                    else:
                        self.monitor_status[thread_name] = "o"
                    if thread_name in self.status_labels:
                        self.status_labels[thread_name].config(text=self.monitor_status[thread_name])
        self.root.after(1000, self.update_monitor_status)

    def process_popup_queue(self):
        try:
            while True:
                thread_name, youtube_url, current_fps, fps_threshold, reset_event = self.popup_queue.get_nowait()
                message = f"Stream: {thread_name}\nURL: {youtube_url}\nFPS hiện tại: {current_fps:.2f}\nNgưỡng FPS: {fps_threshold:.2f}"
                result = messagebox.askokcancel("Stream Lag Alert", message)
                if result:
                    self.log_message(f"[{thread_name}] Người dùng nhấn OK, reset trạng thái.")
                    reset_event.set()
        except queue.Empty:
            pass
        self.root.after(100, self.process_popup_queue)

    def on_closing(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to exit?"):
            self.stop_monitoring()
            self.update_configs()
            self.save_configs_to_csv()  # Save configs before closing
            self.root.destroy()

def main():
    try:
        root = tk.Tk()
        app = MonitorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        logging.error(f"Error in main: {str(e)}\n{traceback.format_exc()}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()