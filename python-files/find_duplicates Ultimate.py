import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, filedialog
from collections import defaultdict
import hashlib
import time
import shutil
import threading
import queue
import sqlite3
import csv
from datetime import datetime

def check_and_install_dependencies():
    required_packages = {
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "send2trash": "send2trash",
        "imagehash": "imagehash",
        "exifread": "exifread"
    }
    missing_packages = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if not missing_packages:
        return True

    temp_root = tk.Tk()
    temp_root.withdraw()
    install_confirm = messagebox.askyesno(
        "نصب پیش‌نیازها",
        f"برای اجرای کامل برنامه به پکیج(های) زیر نیاز است:\n\n{', '.join(missing_packages)}\n\nآیا مایل به نصب خودکار آن‌ها هستید؟ (نیاز به اینترنت)"
    )
    if install_confirm:
        try:
            command = [sys.executable, '-m', 'pip', 'install'] + missing_packages
            subprocess.check_call(command)
            messagebox.showinfo("نصب موفق", "پیش‌نیازها با موفقیت نصب شدند.\nلطفاً برنامه را دوباره اجرا کنید.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا در نصب", f"نصب با خطا مواجه شد: {e}\n\nلطفاً به صورت دستی نصب کنید.")
        finally:
            temp_root.destroy()
            sys.exit(1)
    else:
        messagebox.showwarning("ادامه با امکانات محدود", "بسیاری از قابلیت‌های اصلی غیرفعال خواهند بود.")
        temp_root.destroy()
        return False

try:
    from PIL import Image, ImageTk, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    
try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass

class CacheManager:
    def __init__(self, db_path='file_cache.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    path TEXT PRIMARY KEY,
                    mod_time REAL NOT NULL,
                    size INTEGER NOT NULL,
                    hash_sha1 TEXT,
                    hash_phash TEXT
                )
            ''')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_path ON file_cache(path)')

    def get_hash(self, path, mod_time, size, hash_type='sha1'):
        with self.conn:
            cursor = self.conn.execute(
                f'SELECT {hash_type} FROM file_cache WHERE path=? AND mod_time=? AND size=?',
                (path, mod_time, size)
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] else None

    def set_hash(self, path, mod_time, size, hash_value, hash_type='sha1'):
        with self.conn:
            self.conn.execute(
                f'''
                INSERT OR REPLACE INTO file_cache (path, mod_time, size, {hash_type})
                VALUES (?, ?, ?, ?)
                ''',
                (path, mod_time, size, hash_value)
            )
    
    def clear(self):
        try:
            self.conn.close()
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self.conn = sqlite3.connect(self.db_path)
            self.create_table()
            return True
        except Exception:
            return False

class AdvancedScanOptionsDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("گزینه‌های پیشرفته اسکن")
        self.transient(parent)
        self.geometry("400x250")
        self.result = None

        self.min_size_var = tk.DoubleVar(value=0)
        self.max_size_var = tk.DoubleVar(value=0)
        self.min_date_var = tk.StringVar()
        self.max_date_var = tk.StringVar()
        self.exclude_folders_var = tk.StringVar(value=".git,node_modules,venv,__pycache__")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="حجم فایل (مگابایت):").pack(anchor='w')
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="حداقل:").pack(side=tk.LEFT)
        ttk.Entry(size_frame, textvariable=self.min_size_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="حداکثر:").pack(side=tk.LEFT, padx=10)
        ttk.Entry(size_frame, textvariable=self.max_size_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="(0 برای نادیده گرفتن)").pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="تاریخ ویرایش (YYYY-MM-DD):").pack(anchor='w', pady=(10,0))
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="از:").pack(side=tk.LEFT)
        ttk.Entry(date_frame, textvariable=self.min_date_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="تا:").pack(side=tk.LEFT, padx=10)
        ttk.Entry(date_frame, textvariable=self.max_date_var, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="نادیده گرفتن پوشه‌ها (جدا با کاما):").pack(anchor='w', pady=(10,0))
        ttk.Entry(main_frame, textvariable=self.exclude_folders_var).pack(fill=tk.X, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        ttk.Button(btn_frame, text="تایید", command=self.on_ok).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="انصراف", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.wait_window(self)

    def on_ok(self):
        try:
            min_date = datetime.strptime(self.min_date_var.get(), '%Y-%m-%d').timestamp() if self.min_date_var.get() else None
            max_date = datetime.strptime(self.max_date_var.get(), '%Y-%m-%d').timestamp() if self.max_date_var.get() else None
        except ValueError:
            messagebox.showerror("خطا", "فرمت تاریخ نامعتبر است. لطفاً از YYYY-MM-DD استفاده کنید.", parent=self)
            return

        self.result = {
            "min_size_mb": self.min_size_var.get(),
            "max_size_mb": self.max_size_var.get(),
            "min_date_ts": min_date,
            "max_date_ts": max_date,
            "exclude_folders": [f.strip() for f in self.exclude_folders_var.get().split(',') if f.strip()]
        }
        self.destroy()

class SmartOrganizeDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("سازماندهی هوشمند")
        self.transient(parent)
        self.result = None
        self.destination_path = tk.StringVar(value=os.path.join(parent.root_dir, "Organized_Files"))

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="روش سازماندهی:").pack(anchor='w')
        self.mode_var = tk.StringVar(value="by_type")
        ttk.Radiobutton(main_frame, text="بر اساس نوع فایل (پوشه‌های Images, Videos, ...)", variable=self.mode_var, value="by_type").pack(anchor='w')
        ttk.Radiobutton(main_frame, text="بر اساس تاریخ ویرایش (پوشه‌های YYYY/MM)", variable=self.mode_var, value="by_date").pack(anchor='w')
        
        ttk.Label(main_frame, text="پوشه مقصد:", pady=(10,0)).pack(anchor='w')
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X)
        ttk.Entry(dest_frame, textvariable=self.destination_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dest_frame, text="...", width=3, command=self.browse_dest).pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        ttk.Button(btn_frame, text="شروع", command=self.on_ok).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="انصراف", command=self.destroy).pack(side=tk.RIGHT, padx=5)

        self.wait_window(self)
        
    def browse_dest(self):
        path = filedialog.askdirectory(title="انتخاب پوشه مقصد", initialdir=self.destination_path.get())
        if path:
            self.destination_path.set(path)

    def on_ok(self):
        if not self.destination_path.get():
            messagebox.showerror("خطا", "لطفاً پوشه مقصد را مشخص کنید.", parent=self)
            return
        self.result = {
            "mode": self.mode_var.get(),
            "destination": self.destination_path.get()
        }
        self.destroy()

class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("جعبه ابزار مدیریت فایل")
        master.geometry("1400x800")
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache = CacheManager()
        self.is_scanning = False
        self.scan_thread = None
        self.result_queue = queue.Queue()
        self.advanced_scan_options = {}
        self.drag_select_anchor = None
        self.drag_items_cache = None
        self.dup_formats_var = tk.StringVar(value=".package,.jpg,.png,.mp4,.mkv,.zip")

        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25, font=('Tahoma', 9))
        self.style.configure("Treeview.Heading", font=('Tahoma', 10, 'bold'))

        self.create_widgets()
        self.master.after(100, self.process_queue)

    def create_widgets(self):
        top_frame = ttk.Frame(self.master, padding="10")
        top_frame.pack(fill=tk.X)

        self.scan_button = ttk.Button(top_frame, text="شروع اسکن", command=self.toggle_scan)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.adv_scan_button = ttk.Button(top_frame, text="گزینه‌های پیشرفته...", command=self.open_advanced_options)
        self.adv_scan_button.pack(side=tk.LEFT, padx=(0, 10))

        self.delete_button = ttk.Button(top_frame, text="حذف انتخاب‌ها", command=self.delete_selected_items, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))

        self.smart_organize_button = ttk.Button(top_frame, text="سازماندهی هوشمند", command=self.smart_organize_selected, state=tk.DISABLED)
        self.smart_organize_button.pack(side=tk.LEFT, padx=(0, 10))

        status_frame = ttk.Frame(self.master, padding="0 0 10 10", relief="sunken", borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="برای شروع، یک حالت را از تب‌ها انتخاب و روی 'شروع اسکن' کلیک کنید.")
        self.status_label.pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        
        main_pane = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        left_pane = ttk.Frame(main_pane)
        main_pane.add(left_pane, weight=3)
        
        self.notebook = ttk.Notebook(left_pane)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.create_duplicate_finder_tab()
        self.create_similar_images_tab()
        self.create_large_files_tab()
        self.create_empty_folders_tab()

        preview_pane = ttk.Frame(main_pane)
        main_pane.add(preview_pane, weight=2)
        self.create_preview_pane(preview_pane)

    def create_preview_pane(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=4) 
        parent.rowconfigure(1, weight=0)
        parent.rowconfigure(2, weight=2)
        parent.rowconfigure(3, weight=3)

        self.media_container = ttk.Frame(parent)
        self.media_container.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.media_container.columnconfigure(0, weight=1); self.media_container.rowconfigure(0, weight=1)
        self.image_label = ttk.Label(self.media_container, text="برای پیش‌نمایش یک فایل را انتخاب کنید", anchor="center", wraplength=350)
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.video_controls_frame = ttk.Frame(parent); self.video_controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.video_controls_frame.columnconfigure(1, weight=1)
        self.play_pause_button = ttk.Button(self.video_controls_frame, text="▶", command=self.toggle_play_pause, width=3); self.play_pause_button.grid(row=0, column=0, padx=(0, 5))
        self.time_slider = ttk.Scale(self.video_controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_slider_move); self.time_slider.grid(row=0, column=1, sticky="ew")
        self.time_slider.bind("<ButtonPress-1>", self.on_slider_press); self.time_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.time_label = ttk.Label(self.video_controls_frame, text="00:00 / 00:00"); self.time_label.grid(row=0, column=2, padx=(5, 0))
        self.video_controls_frame.grid_remove()
        
        self.preview_tree = ttk.Treeview(parent, show="tree", style="preview.Treeview", selectmode="extended")
        self.preview_tree.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        self.preview_tree.tag_configure('selected_file', font=('Tahoma', 9, 'bold'))

        self.preview_context_menu = tk.Menu(self.preview_tree, tearoff=0)
        self.preview_context_menu.add_command(label="انتقال به سطل زباله", command=self.delete_from_preview_tree)
        self.preview_tree.bind("<Button-3>", self.show_preview_context_menu)
        self.preview_tree.bind("<<TreeviewSelect>>", self.on_preview_item_select)

        self.metadata_frame = ttk.LabelFrame(parent, text="اطلاعات فایل", padding=5)
        self.metadata_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        self.metadata_text = tk.Text(self.metadata_frame, wrap="word", height=6, font=('Tahoma', 8), borderwidth=0, relief="flat", state="disabled")
        self.metadata_text.pack(fill="both", expand=True)

    def create_tab_frame(self, tab_name):
        frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(frame, text=tab_name)
        
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="جستجو:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(tree_frame, show="headings", selectmode="extended")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        search_var.trace_add("write", lambda *args, sv=search_var, t=tree: self.schedule_search(sv, t))
        tree.bind("<<TreeviewSelect>>", self.on_item_select)
        tree.bind("<Double-1>", self.on_item_double_click)
        tree.bind("<Button-3>", self.show_main_tree_context_menu)
        tree.bind("<ButtonPress-1>", self.on_tree_b1_press, add='+')
        tree.bind("<B1-Motion>", self.on_tree_b1_motion)
        tree.bind("<ButtonRelease-1>", self.on_tree_b1_release, add='+')

        return frame, controls_frame, tree

    def create_duplicate_finder_tab(self):
        frame, controls, tree = self.create_tab_frame("فایل‌های تکراری")
        self.dup_tree = tree
        self.dup_tree.scan_results = []
        self.dup_tree.all_items_cache = []

        self.dup_mode_var = tk.StringVar(value="by_name")
        ttk.Label(controls, text="حالت:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(controls, text="بر اساس نام", variable=self.dup_mode_var, value="by_name").pack(side=tk.LEFT)
        ttk.Radiobutton(controls, text="بر اساس حجم", variable=self.dup_mode_var, value="by_size").pack(side=tk.LEFT, padx=5)
        self.dup_verify_content = tk.BooleanVar(value=False)
        self.dup_verify_check = ttk.Checkbutton(controls, text="مقایسه محتوا (هش SHA1)", variable=self.dup_verify_content)
        self.dup_verify_check.pack(side=tk.LEFT, padx=(10, 0))
        formats_frame = ttk.Frame(controls)
        formats_frame.pack(fill=tk.X, side=tk.TOP, pady=(5,0), expand=True)
        ttk.Label(formats_frame, text="فرمت‌ها (خالی=همه):").pack(side=tk.LEFT, padx=(0,5))
        ttk.Entry(formats_frame, textvariable=self.dup_formats_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dup_tree["columns"] = ("icon", "name", "size", "status", "relative_path", "full_path", "mod_time")
        self.setup_tree_columns(self.dup_tree)

    def create_similar_images_tab(self):
        frame, controls, tree = self.create_tab_frame("تصاویر مشابه")
        self.sim_img_tree = tree
        self.sim_img_tree.scan_results = []
        self.sim_img_tree.all_items_cache = []

        ttk.Label(controls, text="آستانه شباهت (کمتر=مشابه‌تر):").pack(side=tk.LEFT)
        self.sim_threshold = tk.IntVar(value=5)
        ttk.Scale(controls, from_=0, to=20, variable=self.sim_threshold, orient=tk.HORIZONTAL).pack(side=tk.LEFT, padx=5)
        ttk.Label(controls, textvariable=self.sim_threshold).pack(side=tk.LEFT)
        
        self.sim_img_tree["columns"] = ("icon", "name", "size", "distance", "relative_path", "full_path", "mod_time")
        self.setup_tree_columns(self.sim_img_tree, is_similar_img=True)

    def create_large_files_tab(self):
        frame, controls, tree = self.create_tab_frame("فایل‌های حجیم")
        self.large_tree = tree
        self.large_tree.scan_results = []
        self.large_tree.all_items_cache = []
        
        ttk.Label(controls, text="تعداد نتایج:").pack(side=tk.LEFT)
        self.large_file_count = tk.IntVar(value=100)
        ttk.Entry(controls, textvariable=self.large_file_count, width=10).pack(side=tk.LEFT, padx=5)
        
        self.large_tree["columns"] = ("icon", "name", "size", "mod_date", "relative_path", "full_path", "mod_time")
        self.setup_tree_columns(self.large_tree, is_large_file=True)

    def create_empty_folders_tab(self):
        frame, controls, tree = self.create_tab_frame("پوشه‌های خالی")
        self.empty_tree = tree
        self.empty_tree.scan_results = []
        self.empty_tree.all_items_cache = []
        
        self.empty_tree["columns"] = ("icon", "name", "relative_path", "full_path")
        self.empty_tree.heading("icon", text=""); self.empty_tree.column("icon", width=40, stretch=tk.NO, anchor='center')
        self.empty_tree.heading("name", text="نام پوشه"); self.empty_tree.column("name", width=250)
        self.empty_tree.heading("relative_path", text="مسیر"); self.empty_tree.column("relative_path", width=350)
        self.empty_tree.heading("full_path", text=""); self.empty_tree.column("full_path", width=0, stretch=tk.NO)

    def setup_tree_columns(self, tree, is_similar_img=False, is_large_file=False):
        tree.heading("icon", text=""); tree.column("icon", width=40, stretch=tk.NO, anchor='center')
        tree.heading("name", text="نام فایل"); tree.column("name", width=250)
        tree.heading("size", text="حجم (مگابایت)"); tree.column("size", width=120, anchor='center')
        if is_similar_img:
            tree.heading("distance", text="فاصله"); tree.column("distance", width=100, anchor='center')
        elif is_large_file:
            tree.heading("mod_date", text="تاریخ ویرایش"); tree.column("mod_date", width=150, anchor='center')
        else: # Duplicate finder
            tree.heading("status", text="توضیح"); tree.column("status", width=180, anchor='center')
        tree.heading("relative_path", text="مسیر"); tree.column("relative_path", width=350)
        tree.heading("full_path", text=""); tree.column("full_path", width=0, stretch=tk.NO)
        tree.heading("mod_time", text=""); tree.column("mod_time", width=0, stretch=tk.NO)
        tree.tag_configure('conflict', background='#FFEBEB')
        tree.tag_configure('duplicate', background='#E6F3FF')
        tree.tag_configure('separator', background='#FFFFFF')

    def get_current_tree(self):
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0: return self.dup_tree
        elif tab_index == 1: return self.sim_img_tree
        elif tab_index == 2: return self.large_tree
        elif tab_index == 3: return self.empty_tree
        return None

    def on_tab_change(self, event):
        tree = self.get_current_tree()
        if tree:
            has_results = bool(tree.scan_results)
            self.update_button_states(has_results)

    def update_button_states(self, has_results):
        delete_state = tk.NORMAL if has_results and SEND2TRASH_AVAILABLE else tk.DISABLED
        organize_state = tk.NORMAL if has_results else tk.DISABLED
        self.delete_button.config(state=delete_state)
        self.smart_organize_button.config(state=organize_state)

    def open_advanced_options(self):
        dialog = AdvancedScanOptionsDialog(self.master)
        if dialog.result:
            self.advanced_scan_options = dialog.result
            messagebox.showinfo("اعمال شد", "گزینه‌های پیشرفته برای اسکن بعدی اعمال خواهند شد.", parent=self.master)
            
    def smart_organize_selected(self):
        tree = self.get_current_tree()
        selected_ids = tree.selection()
        if not selected_ids:
            messagebox.showwarning("انتخاب نشده", "هیچ موردی برای سازماندهی انتخاب نشده است.", parent=self.master)
            return
            
        dialog = SmartOrganizeDialog(self.master)
        if not dialog.result:
            return
            
        paths_to_organize = [tree.item(item_id, 'values')[5] for item_id in selected_ids if 'separator' not in tree.item(item_id, 'tags')]
        
        self.status_label.config(text=f"در حال سازماندهی {len(paths_to_organize)} آیتم...")
        self.progress_bar.start(10)

        threading.Thread(target=self.run_organize_logic, args=(paths_to_organize, dialog.result), daemon=True).start()

    def run_organize_logic(self, paths, options):
        moved_count = 0
        errors = []
        dest_base = options['destination']
        mode = options['mode']

        file_types = {
            'Images': ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'),
            'Videos': ('.mp4', '.mkv', '.avi', '.mov', '.wmv'),
            'Documents': ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'),
            'Archives': ('.zip', '.rar', '.7z', '.tar', '.gz'),
            'Packages': ('.package',)
        }

        for path in paths:
            if not os.path.exists(path): continue
            
            dest_dir = ""
            if mode == 'by_type':
                ext = os.path.splitext(path)[1].lower()
                folder_name = 'Others'
                for type_name, extensions in file_types.items():
                    if ext in extensions:
                        folder_name = type_name
                        break
                dest_dir = os.path.join(dest_base, folder_name)
            
            elif mode == 'by_date':
                try:
                    mtime = os.path.getmtime(path)
                    dt_object = datetime.fromtimestamp(mtime)
                    dest_dir = os.path.join(dest_base, dt_object.strftime('%Y'), dt_object.strftime('%m'))
                except Exception as e:
                    errors.append(f"خطا در خواندن تاریخ {os.path.basename(path)}: {e}")
                    continue

            try:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(path, dest_dir)
                moved_count += 1
            except Exception as e:
                errors.append(f"خطا در انتقال {os.path.basename(path)}: {e}")

        self.result_queue.put({'type': 'organize_complete', 'moved': moved_count, 'errors': errors})

    def toggle_scan(self):
        if self.is_scanning:
            self.is_scanning = False
            self.scan_button.config(text="شروع اسکن")
            self.status_label.config(text="در حال متوقف کردن اسکن...")
        else:
            tree = self.get_current_tree()
            tree.delete(*tree.get_children())
            tree.scan_results = []
            tree.all_items_cache = []
            
            self.is_scanning = True
            self.scan_button.config(text="توقف اسکن")
            self.status_label.config(text="در حال آماده‌سازی برای اسکن...")
            self.progress_bar.start(10)
            self.update_button_states(False)

            tab_index = self.notebook.index(self.notebook.select())
            self.scan_thread = threading.Thread(target=self.run_scan_worker, args=(tab_index,), daemon=True)
            self.scan_thread.start()

    def run_scan_worker(self, tab_index):
        if tab_index == 0: self.scan_duplicates()
        elif tab_index == 1: self.scan_similar_images()
        elif tab_index == 2: self.scan_large_files()
        elif tab_index == 3: self.scan_empty_folders()

    def check_file_filters(self, path):
        opts = self.advanced_scan_options
        if not opts: return True
        try:
            stat = os.stat(path)
            size_mb = stat.st_size / (1024*1024)
            mod_time = stat.st_mtime

            if opts.get("min_size_mb") and size_mb < opts["min_size_mb"]: return False
            if opts.get("max_size_mb") and size_mb > opts["max_size_mb"]: return False
            if opts.get("min_date_ts") and mod_time < opts["min_date_ts"]: return False
            if opts.get("max_date_ts") and mod_time > opts["max_date_ts"]: return False
        except OSError:
            return False
        return True

    def walk_path(self):
        exclude = self.advanced_scan_options.get("exclude_folders", [])
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if not self.is_scanning:
                raise InterruptedError("Scan stopped by user.")
            
            dirnames[:] = [d for d in dirnames if d not in exclude]
            
            self.result_queue.put({'type': 'status_update', 'path': dirpath})
            yield dirpath, filenames

    def scan_duplicates(self):
        try:
            formats_str = self.dup_formats_var.get().strip()
            target_formats = tuple()
            if formats_str:
                target_formats = tuple([f.strip().lower() for f in formats_str.split(',') if f.strip()])

            files_by_size = defaultdict(list)
            for dirpath, filenames in self.walk_path():
                for filename in filenames:
                    if target_formats and not filename.lower().endswith(target_formats):
                        continue

                    full_path = os.path.join(dirpath, filename)
                    if not self.check_file_filters(full_path): continue
                    try:
                        stat_res = os.stat(full_path)
                        files_by_size[stat_res.st_size].append({'path': full_path, 'size': stat_res.st_size, 'name': filename, 'mtime': stat_res.st_mtime})
                    except OSError: continue
            
            final_groups = []
            if self.dup_mode_var.get() == 'by_name':
                files_by_name = defaultdict(list)
                for size_group in files_by_size.values():
                    for file_info in size_group:
                        files_by_name[file_info['name']].append(file_info)
                final_groups = [g for g in files_by_name.values() if len(g) > 1]
            else: # by_size
                potential_groups = [g for g in files_by_size.values() if len(g) > 1]
                if not self.dup_verify_content.get():
                    final_groups = [g for g in potential_groups if len(set(f['name'] for f in g)) > 1]
                else:
                    self.result_queue.put({'type': 'status_update', 'text': "مقایسه محتوای فایل‌ها (هش)..."})
                    for i, group in enumerate(potential_groups):
                        if not self.is_scanning: raise InterruptedError()
                        self.result_queue.put({'type': 'status_update', 'path': f"درحال هش کردن گروه {i+1} از {len(potential_groups)}"})
                        hashes = defaultdict(list)
                        for file_info in group:
                            fhash = self.calculate_hash(file_info['path'], 'sha1')
                            if fhash: hashes[fhash].append(file_info)
                        for hash_group in hashes.values():
                            if len(hash_group) > 1: final_groups.append(hash_group)

            for group in final_groups: group.sort(key=lambda x: -x['size'])
            final_groups.sort(key=lambda group: -group[0]['size'])
            self.result_queue.put({'type': 'scan_complete', 'results': final_groups, 'tab_index': 0})
        except InterruptedError:
            self.result_queue.put({'type': 'scan_stopped'})
        except Exception as e:
            self.result_queue.put({'type': 'scan_error', 'error': str(e)})

    def scan_similar_images(self):
        if not IMAGEHASH_AVAILABLE:
            self.result_queue.put({'type': 'scan_error', 'error': "کتابخانه imagehash نصب نیست."})
            return
        try:
            hashes = {}
            img_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
            
            all_images = []
            for dirpath, filenames in self.walk_path():
                for filename in filenames:
                    if filename.lower().endswith(img_exts):
                        full_path = os.path.join(dirpath, filename)
                        if self.check_file_filters(full_path):
                            all_images.append(full_path)

            total_images = len(all_images)
            for i, path in enumerate(all_images):
                if not self.is_scanning: raise InterruptedError()
                self.result_queue.put({'type': 'status_update', 'path': f"درحال پردازش تصویر {i+1} از {total_images}"})
                try:
                    fhash = self.calculate_hash(path, 'phash')
                    if fhash:
                        hashes[path] = fhash
                except Exception:
                    continue
            
            groups = []
            used = set()
            for path1 in hashes:
                if path1 in used: continue
                group = [(path1, 0)]
                used.add(path1)
                for path2 in hashes:
                    if path2 in used: continue
                    distance = hashes[path1] - hashes[path2]
                    if distance <= self.sim_threshold.get():
                        group.append((path2, distance))
                        used.add(path2)
                if len(group) > 1:
                    groups.append(group)
            
            self.result_queue.put({'type': 'scan_complete', 'results': groups, 'tab_index': 1})
        except InterruptedError:
            self.result_queue.put({'type': 'scan_stopped'})
        except Exception as e:
            self.result_queue.put({'type': 'scan_error', 'error': str(e)})

    def scan_large_files(self):
        try:
            files = []
            for dirpath, filenames in self.walk_path():
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    if not self.check_file_filters(full_path): continue
                    try:
                        stat = os.stat(full_path)
                        files.append({'path': full_path, 'size': stat.st_size, 'mtime': stat.st_mtime, 'name': filename})
                    except OSError:
                        continue
            
            files.sort(key=lambda x: -x['size'])
            limit = self.large_file_count.get()
            self.result_queue.put({'type': 'scan_complete', 'results': files[:limit], 'tab_index': 2})
        except InterruptedError:
            self.result_queue.put({'type': 'scan_stopped'})
        except Exception as e:
            self.result_queue.put({'type': 'scan_error', 'error': str(e)})

    def scan_empty_folders(self):
        try:
            empty_folders = []
            for dirpath, dirnames, filenames in os.walk(self.root_dir, topdown=False):
                if not self.is_scanning: raise InterruptedError()
                self.result_queue.put({'type': 'status_update', 'path': dirpath})
                if not dirnames and not filenames:
                    empty_folders.append(dirpath)
            
            self.result_queue.put({'type': 'scan_complete', 'results': sorted(empty_folders), 'tab_index': 3})
        except InterruptedError:
            self.result_queue.put({'type': 'scan_stopped'})
        except Exception as e:
            self.result_queue.put({'type': 'scan_error', 'error': str(e)})

    def process_queue(self):
        try:
            while not self.result_queue.empty():
                msg = self.result_queue.get_nowait()
                msg_type = msg.get('type')

                if msg_type == 'status_update':
                    if 'text' in msg:
                        self.status_label.config(text=msg['text'])
                    if 'path' in msg:
                        path = msg['path']
                        if len(path) > 80: path = "..." + path[-77:]
                        self.status_label.config(text=path)

                elif msg_type == 'scan_complete':
                    self.is_scanning = False
                    self.scan_button.config(text="شروع اسکن")
                    self.progress_bar.stop()
                    self.status_label.config(text="اسکن کامل شد.")
                    self.populate_tree(msg['results'], msg['tab_index'])
                    self.update_button_states(bool(msg['results']))
                    if not msg['results']:
                        messagebox.showinfo("نتیجه", "موردی یافت نشد.")

                elif msg_type == 'scan_stopped':
                    self.is_scanning = False
                    self.scan_button.config(text="شروع اسکن")
                    self.progress_bar.stop()
                    self.status_label.config(text="اسکن توسط کاربر متوقف شد.")

                elif msg_type == 'scan_error':
                    self.is_scanning = False
                    self.scan_button.config(text="شروع اسکن")
                    self.progress_bar.stop()
                    self.status_label.config(text=f"اسکن با خطا متوقف شد.")
                    messagebox.showerror("خطا در اسکن", msg['error'])
                    
                elif msg_type == 'organize_complete':
                    self.progress_bar.stop()
                    summary = f"{msg['moved']} آیتم با موفقیت منتقل شد."
                    if msg['errors']:
                        summary += f"\n\nخطاها:\n" + "\n".join(msg['errors'])
                        messagebox.showerror("گزارش سازماندهی", summary)
                    else:
                        messagebox.showinfo("گزارش سازماندهی", summary)
                    self.status_label.config(text="سازماندهی کامل شد. برای دیدن تغییرات دوباره اسکن کنید.")
                    self.toggle_scan() # Rescan to reflect changes

        finally:
            self.master.after(100, self.process_queue)

    def populate_tree(self, results, tab_index):
        if tab_index == 0: tree, is_dup = self.dup_tree, True
        elif tab_index == 1: tree, is_sim = self.sim_img_tree, True
        elif tab_index == 2: tree, is_large = self.large_tree, True
        elif tab_index == 3: tree, is_empty = self.empty_tree, True
        else: return
        
        tree.scan_results = results
        tree.delete(*tree.get_children())
        
        if tab_index == 0: # Duplicates
            for i, group in enumerate(results):
                if i > 0: tree.insert('', 'end', values=(), tags=('separator',))
                for j, item in enumerate(group):
                    size_mb = f"{item['size'] / (1024*1024):.2f}"
                    status, tag = self.get_duplicate_status(j, item, group)
                    tree.insert('', 'end', values=("📂", item['name'], size_mb, status, os.path.relpath(item['path'], self.root_dir), item['path'], item['mtime']), tags=(tag,))

        elif tab_index == 1: # Similar Images
            for i, group in enumerate(results):
                if i > 0: tree.insert('', 'end', values=(), tags=('separator',))
                for path, dist in group:
                    stat = os.stat(path)
                    size_mb = f"{stat.st_size / (1024*1024):.2f}"
                    tree.insert('', 'end', values=("🖼️", os.path.basename(path), size_mb, dist, os.path.relpath(path, self.root_dir), path, stat.st_mtime), tags=('duplicate',))
                    
        elif tab_index == 2: # Large Files
            for item in results:
                size_mb = f"{item['size'] / (1024*1024):.2f}"
                mod_date = datetime.fromtimestamp(item['mtime']).strftime('%Y-%m-%d %H:%M:%S')
                tree.insert('', 'end', values=("💾", item['name'], size_mb, mod_date, os.path.relpath(item['path'], self.root_dir), item['path'], item['mtime']))

        elif tab_index == 3: # Empty Folders
            for path in results:
                tree.insert('', 'end', values=("📁", os.path.basename(path), os.path.relpath(path, self.root_dir), path))
        
        tree.all_items_cache = tree.get_children('')
    
    def get_duplicate_status(self, index, item, group):
        mode = self.dup_mode_var.get()
        if mode == 'by_name':
            if index == 0: return "فایل اصلی (بزرگترین)", 'duplicate'
            if item['size'] == group[0]['size']: return "کپی دقیق", 'duplicate'
            return "نسخه با حجم کمتر", 'conflict'
        elif mode == 'by_size':
            if self.dup_verify_content.get(): return "کپی دقیق (محتوای یکسان)", 'duplicate'
            return "هم‌حجم با نام متفاوت", 'conflict'
        return "", ""

    def calculate_hash(self, filepath, hash_type='sha1'):
        try:
            if hash_type == 'sha1':
                sha1 = hashlib.sha1()
                with open(filepath, 'rb') as f:
                    while True:
                        data = f.read(65536)
                        if not data: break
                        sha1.update(data)
                return sha1.hexdigest()

            stat = os.stat(filepath)
            cached_hash = self.cache.get_hash(filepath, stat.st_mtime, stat.st_size, f'hash_{hash_type}')
            if cached_hash: return cached_hash

            if hash_type == 'phash':
                fhash = str(imagehash.phash(Image.open(filepath)))
            else:
                return None
            
            self.cache.set_hash(filepath, stat.st_mtime, stat.st_size, fhash, f'hash_{hash_type}')
            return fhash
        except Exception:
            return None

    def on_item_select(self, event):
        tree = event.widget
        selection = tree.selection()
        if not selection:
            self.clear_preview()
            return
        
        self.update_button_states(True)
        
        item_id = selection[0]
        item = tree.item(item_id)
        if 'separator' in item.get('tags', []): return
        
        try:
            full_path_index = tree["columns"].index('full_path')
            original_file_path = item['values'][full_path_index]
        except (ValueError, IndexError):
            self.clear_preview()
            return

        if not original_file_path or not os.path.exists(original_file_path):
            self.clear_preview()
            return

        self.clear_preview()
        
        if os.path.isfile(original_file_path):
            self.update_preview_tree(original_file_path)
            self.show_metadata(original_file_path)

            image_exts = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
            video_exts = ('.mp4', '.mkv', '.avi', '.mov')
            
            preview_target = None
            if original_file_path.lower().endswith(image_exts + video_exts):
                preview_target = original_file_path
            else:
                preview_target = self.find_associated_preview(original_file_path)
            
            if preview_target:
                self.show_media_preview(preview_target)
            else:
                self.clear_media_preview()
                self.image_label.config(text="پیش‌نمایش برای این نوع فایل پشتیبانی نمی‌شود")

    def show_metadata(self, file_path):
        self.metadata_text.config(state="normal")
        self.metadata_text.delete(1.0, tk.END)
        info = []
        try:
            stat = os.stat(file_path)
            info.append(f"نام: {os.path.basename(file_path)}")
            info.append(f"حجم: {stat.st_size / (1024*1024):.2f} مگابایت")
            info.append(f"تاریخ ویرایش: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            info.append("-" * 20)

            ext = os.path.splitext(file_path)[1].lower()
            if ext in ('.jpg', '.jpeg', '.tiff') and EXIFREAD_AVAILABLE:
                with open(file_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    for tag, value in tags.items():
                        if tag not in ('JPEGThumbnail', 'TIFFThumbnail'):
                            info.append(f"{tag}: {value}")
            elif ext in ('.mp4', '.mkv', '.avi') and CV2_AVAILABLE:
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    info.append(f"ابعاد: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                    info.append(f"فریم در ثانیه: {cap.get(cv2.CAP_PROP_FPS):.2f}")
                    cap.release()
        except Exception:
            info.append("خطا در خواندن اطلاعات.")
        
        self.metadata_text.insert(tk.END, "\n".join(info))
        self.metadata_text.config(state="disabled")

    def show_media_preview(self, file_path):
        image_exts = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        video_exts = ('.mp4', '.mkv', '.avi', '.mov')
        if file_path.lower().endswith(image_exts):
            self.show_image_preview(file_path)
        elif file_path.lower().endswith(video_exts):
            self.setup_video_preview(file_path)
        else:
            self.image_label.config(text="پیش‌نمایش برای این نوع فایل پشتیبانی نمی‌شود")

    def show_image_preview(self, file_path):
        if not PIL_AVAILABLE: self.image_label.config(image='', text="کتابخانه Pillow نصب نیست"); return
        try:
            self.media_container.update_idletasks()
            w, h = self.media_container.winfo_width(), self.media_container.winfo_height()
            if w < 2 or h < 2: return
            img = Image.open(file_path)
            img.thumbnail((w, h), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo_image, text="")
        except Exception as e: self.image_label.config(text=f"خطا در بارگذاری تصویر:\n{e}")

    def setup_video_preview(self, file_path):
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            self.clear_media_preview()
            self.image_label.config(text="پیش‌نیازهای ویدیو (OpenCV, Pillow) نصب نیست")
            return
        self.current_video_path = file_path
        self.video_capture = cv2.VideoCapture(file_path)
        if not self.video_capture.isOpened():
            self.clear_media_preview()
            self.image_label.config(text="امکان باز کردن فایل ویدیو وجود ندارد")
            self.video_capture = None
            return
        
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_duration_sec = frame_count / fps if fps > 0 else 0
        self.time_slider.config(to=self.video_duration_sec)
        self.time_slider.set(0)

        self.video_controls_frame.grid()
        self.show_video_frame()
        self.update_time_label()

    def play_video(self):
        if self.video_capture: self.is_playing = True; self.play_pause_button.config(text="❚❚"); self.update_video_frame()

    def update_video_frame(self):
        if not self.is_playing or not self.video_capture: return
        ret = self.show_video_frame()
        if ret:
            self.update_time_label()
            self.video_update_job = self.master.after(33, self.update_video_frame)
        else:
            self.pause_video()
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.show_video_frame()
            self.update_time_label()
    
    def on_item_double_click(self, event):
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if not item_id or 'separator' in tree.item(item_id, 'tags'): return
        
        try:
            full_path_index = tree["columns"].index('full_path')
            file_path = tree.item(item_id, 'values')[full_path_index]
        except (ValueError, IndexError):
            return

        if not file_path: return
        try:
            if sys.platform == "win32": subprocess.Popen(f'explorer /select,"{file_path}"')
            elif sys.platform == "darwin": subprocess.Popen(["open", "-R", file_path])
            else: subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
        except Exception as e: messagebox.showerror("خطا", f"امکان باز کردن پوشه وجود ندارد:\n{e}")

    def delete_selected_items(self):
        if not SEND2TRASH_AVAILABLE:
            messagebox.showerror("خطا", "کتابخانه send2trash نصب نیست.", parent=self.master)
            return

        tree = self.get_current_tree()
        selected_ids = tree.selection()
        if not selected_ids:
            messagebox.showwarning("انتخاب نشده", "هیچ موردی برای حذف انتخاب نشده است.", parent=self.master)
            return
            
        full_path_index = tree["columns"].index('full_path')
        paths_to_delete = [tree.item(item_id, 'values')[full_path_index] for item_id in selected_ids if 'separator' not in tree.item(item_id, 'tags')]
        
        if not messagebox.askyesno("تایید حذف", f"آیا از انتقال {len(paths_to_delete)} مورد به سطل زباله مطمئن هستید؟", parent=self.master):
            return

        self.clear_preview()
        deleted_count = 0
        errors = []
        deleted_paths_set = set()

        for path in paths_to_delete:
            try:
                send2trash.send2trash(path)
                deleted_count += 1
                deleted_paths_set.add(path)
            except Exception as e:
                errors.append(f"خطا در انتقال به سطل زباله {os.path.basename(path)}: {e}")

        for item_id in selected_ids:
            if tree.exists(item_id):
                tree.delete(item_id)
        
        if isinstance(tree.scan_results, list) and tree.scan_results and isinstance(tree.scan_results[0], dict):
             tree.scan_results = [item for item in tree.scan_results if item['path'] not in deleted_paths_set]
        elif isinstance(tree.scan_results, list) and tree.scan_results and isinstance(tree.scan_results[0], list):
            new_groups = []
            for group in tree.scan_results:
                new_group = [item for item in group if item['path'] not in deleted_paths_set]
                if len(new_group) > 1:
                    new_groups.append(new_group)
            tree.scan_results = new_groups
            self.populate_tree(new_groups, self.notebook.index(self.notebook.select()))


        summary = f"{deleted_count} مورد با موفقیت به سطل زباله منتقل شد."
        if errors:
            summary += "\n\nخطاها:\n" + "\n".join(errors)
            messagebox.showerror("گزارش حذف", summary)
        else:
            messagebox.showinfo("گزارش حذف", summary)
        
        self.status_label.config(text=f"{deleted_count} مورد حذف شد. لیست بروزرسانی شد.")
        self.update_button_states(bool(tree.scan_results))

    def on_slider_press(self, event): self.is_slider_dragging = True
    def on_slider_release(self, event): self.is_slider_dragging = False; self.on_slider_move(self.time_slider.get())
    def on_slider_move(self, value):
        if self.video_capture and self.is_slider_dragging:
            self.video_capture.set(cv2.CAP_PROP_POS_MSEC, float(value) * 1000)
            self.show_video_frame()
            self.update_time_label()
    def toggle_play_pause(self):
        if self.is_playing: self.pause_video()
        else: self.play_video()
    def pause_video(self): self.is_playing = False; self.play_pause_button.config(text="▶")
    def stop_video(self):
        self.pause_video()
        if hasattr(self, 'video_update_job') and self.video_update_job: self.master.after_cancel(self.video_update_job)
        self.video_update_job = None
        if hasattr(self, 'video_capture') and self.video_capture: self.video_capture.release()
        self.video_capture = None; self.current_video_path = None
    def show_video_frame(self, seek_msec=None):
        if not self.video_capture or not self.video_capture.isOpened(): return False
        if seek_msec is not None: self.video_capture.set(cv2.CAP_PROP_POS_MSEC, seek_msec)
        ret, frame = self.video_capture.read()
        if ret:
            self.media_container.update_idletasks()
            w, h = self.media_container.winfo_width(), self.media_container.winfo_height()
            if w < 2 or h < 2: return False
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.thumbnail((w-4, h-4), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo_image, text="")
        return ret
    def update_time_label(self):
        if self.video_capture and self.video_capture.isOpened() and self.video_duration_sec > 0:
            current_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
            current_sec = current_msec / 1000
            if not self.is_slider_dragging: self.time_slider.set(current_sec)
            current_time_str = time.strftime('%M:%S', time.gmtime(current_sec))
            total_time_str = time.strftime('%M:%S', time.gmtime(self.video_duration_sec))
            self.time_label.config(text=f"{current_time_str} / {total_time_str}")
    def clear_media_preview(self):
        self.stop_video()
        self.image_label.config(image='', text="برای پیش‌نمایش یک فایل را انتخاب کنید")
        self.photo_image = None
        self.video_controls_frame.grid_remove()
    def clear_preview(self):
        self.clear_media_preview()
        for item in self.preview_tree.get_children(): self.preview_tree.delete(item)
        self.current_preview_directory = None
        self.metadata_text.config(state="normal"); self.metadata_text.delete(1.0, tk.END); self.metadata_text.config(state="disabled")
    def update_preview_tree(self, selected_file_path):
        for item in self.preview_tree.get_children(): self.preview_tree.delete(item)
        try:
            directory = os.path.dirname(selected_file_path)
            if not os.path.isdir(directory): return
            self.current_preview_directory = directory
            selected_filename = os.path.basename(selected_file_path)
            parent_node_text = f"📁 {os.path.basename(directory)}"; parent_id = self.preview_tree.insert("", "end", text=parent_node_text, open=True)
            items = sorted(os.listdir(directory), key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
            highlighted_item_id = None
            for item_name in items:
                full_path = os.path.join(directory, item_name)
                prefix = "📁" if os.path.isdir(full_path) else "📄"
                text = f"{prefix} {item_name}"
                tags = ()
                if item_name == selected_filename:
                    tags = ('selected_file',)
                    highlighted_item_id = self.preview_tree.insert(parent_id, "end", text=text, tags=tags)
                else:
                    self.preview_tree.insert(parent_id, "end", text=text)
            if highlighted_item_id: self.preview_tree.see(highlighted_item_id)
        except Exception as e: self.preview_tree.insert("", "end", text=f"خطا در دسترسی به پوشه: {e}")
    def schedule_search(self, search_var, tree):
        if hasattr(self, 'search_after_id'): self.master.after_cancel(self.search_after_id)
        self.search_after_id = self.master.after(300, lambda sv=search_var, t=tree: self.perform_search(sv, t))
    def perform_search(self, search_var, tree):
        search_term = search_var.get().lower()
        tree.detach(*tree.get_children())
        for item_id in tree.all_items_cache:
            if not tree.exists(item_id): continue
            if 'separator' in tree.item(item_id, 'tags'):
                if not search_term: tree.move(item_id, '', 'end')
                continue
            values = tree.item(item_id, 'values')
            if any(search_term in str(v).lower() for v in values):
                tree.move(item_id, '', 'end')
    def show_main_tree_context_menu(self, event):
        tree = event.widget
        menu = tk.Menu(tree, tearoff=0)
        
        selection = tree.selection()
        if not selection: return
        
        is_separator = 'separator' in tree.item(selection[0], 'tags')
        
        def add_cmd(label, cmd, state='normal'):
            menu.add_command(label=label, command=cmd, state=state)

        delete_state = 'disabled' if is_separator or not SEND2TRASH_AVAILABLE else 'normal'
        add_cmd("حذف موارد انتخاب شده", self.delete_selected_items, delete_state)
        
        is_single_selection = len(selection) == 1 and not is_separator
        add_cmd("باز کردن محل آیتم", lambda: self.on_item_double_click(event), 'normal' if is_single_selection else 'disabled')
        add_cmd("کپی مسیر کامل", lambda: self.copy_selected_path(tree), 'normal' if is_single_selection else 'disabled')
        menu.add_separator()
        add_cmd("سازماندهی هوشمند موارد انتخاب شده", self.smart_organize_selected, 'normal' if not is_separator else 'disabled')
        menu.add_separator()
        add_cmd("انتخاب همه موارد", lambda: tree.selection_set(tree.get_children()))
        add_cmd("لغو انتخاب همه", lambda: tree.selection_set())
        menu.add_separator()
        add_cmd("خروجی CSV...", lambda: self.export_to_csv(tree))
        menu.add_separator()
        add_cmd("پاک کردن کش هش‌ها", self.clear_cache)

        if self.notebook.index(self.notebook.select()) <= 1: # Duplicate or Similar
             self.add_smart_select_menu(menu, tree)
        
        menu.post(event.x_root, event.y_root)

    def add_smart_select_menu(self, menu, tree):
        smart_select_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="انتخاب هوشمند در گروه‌ها...", menu=smart_select_menu)
        smart_select_menu.add_command(label="انتخاب همه بجز جدیدترین", command=lambda: self.smart_select('newest', tree))
        smart_select_menu.add_command(label="انتخاب همه بجز قدیمی‌ترین", command=lambda: self.smart_select('oldest', tree))
        smart_select_menu.add_command(label="انتخاب همه بجز بزرگترین", command=lambda: self.smart_select('largest', tree))
        smart_select_menu.add_command(label="انتخاب همه بجز کوچکترین", command=lambda: self.smart_select('smallest', tree))
        smart_select_menu.add_command(label="انتخاب همه بجز مسیر کوتاه‌تر", command=lambda: self.smart_select('shortest_path', tree))
    
    def smart_select(self, criteria, tree):
        if not tree.scan_results or not isinstance(tree.scan_results[0], list): return

        to_select = []
        path_idx = tree['columns'].index('full_path')
        mtime_idx = tree['columns'].index('mod_time')
        size_idx = tree['columns'].index('size')

        item_map = {tree.item(item_id, 'values')[path_idx]: item_id for item_id in tree.get_children('') if 'separator' not in tree.item(item_id, 'tags')}

        for group in tree.scan_results:
            group_items = [
                {'id': item_map.get(info.get('path') or info[0]),
                 'path': info.get('path') or info[0],
                 'size': os.stat(info.get('path') or info[0]).st_size,
                 'mtime': os.stat(info.get('path') or info[0]).st_mtime}
                for info in group if item_map.get(info.get('path') or info[0])
            ]
            if not group_items: continue

            if criteria == 'newest': item_to_keep = max(group_items, key=lambda x: x['mtime'])
            elif criteria == 'oldest': item_to_keep = min(group_items, key=lambda x: x['mtime'])
            elif criteria == 'largest': item_to_keep = max(group_items, key=lambda x: x['size'])
            elif criteria == 'smallest': item_to_keep = min(group_items, key=lambda x: x['size'])
            elif criteria == 'shortest_path': item_to_keep = min(group_items, key=lambda x: len(x['path']))
            else: continue
            
            to_select.extend([item['id'] for item in group_items if item['id'] != item_to_keep['id']])

        tree.selection_set(to_select)

    def copy_selected_path(self, tree):
        selection = tree.selection()
        if not selection: return
        file_path = tree.item(selection[0], 'values')[tree['columns'].index('full_path')]
        self.master.clipboard_clear(); self.master.clipboard_append(file_path); self.master.update()
        self.status_label.config(text=f"مسیر کپی شد: {os.path.basename(file_path)}")

    def export_to_csv(self, tree):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(tree['columns'])
                for item_id in tree.get_children(''):
                    writer.writerow(tree.item(item_id, 'values'))
            messagebox.showinfo("موفقیت", f"داده‌ها با موفقیت در {filepath} ذخیره شد.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل: {e}")
            
    def clear_cache(self):
        if messagebox.askyesno("تایید", "آیا از پاک کردن کامل کش هش‌های فایل مطمئن هستید؟ اسکن بعدی ممکن است طولانی‌تر شود."):
            if self.cache.clear():
                messagebox.showinfo("موفقیت", "کش با موفقیت پاک شد.")
            else:
                messagebox.showerror("خطا", "خطا در پاک کردن کش.")

    def on_tree_b1_press(self, event):
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            self.drag_select_anchor = tree.identify_row(event.y)
            self.drag_items_cache = tree.all_items_cache
        else:
            self.drag_select_anchor = None
            self.drag_items_cache = None

    def on_tree_b1_motion(self, event):
        tree = event.widget
        if not self.drag_select_anchor or not self.drag_items_cache: return
        current_item = tree.identify_row(event.y)
        if not current_item: return
        try:
            anchor_index = self.drag_items_cache.index(self.drag_select_anchor)
            current_index = self.drag_items_cache.index(current_item)
        except ValueError:
            return
        start, end = min(anchor_index, current_index), max(anchor_index, current_index)
        valid_items_to_select = [
            item for item in self.drag_items_cache[start : end + 1]
            if 'separator' not in tree.item(item, 'tags')
        ]
        if valid_items_to_select:
            tree.selection_set(valid_items_to_select)
            tree.see(current_item)

    def on_tree_b1_release(self, event):
        self.drag_select_anchor = None
        self.drag_items_cache = None
        
    def find_associated_preview(self, file_path):
        image_exts = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff')
        directory = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        try:
            for ext in image_exts:
                potential_preview = os.path.join(directory, base_name + ext)
                if os.path.exists(potential_preview):
                    return potential_preview
            
            for item in sorted(os.listdir(directory)):
                if item.lower().endswith(image_exts):
                    return os.path.join(directory, item)
        except (OSError, FileNotFoundError):
            return None
        return None

    def show_preview_context_menu(self, event):
        item_id = self.preview_tree.identify_row(event.y)
        if item_id and item_id not in self.preview_tree.selection():
            self.preview_tree.selection_set(item_id)
        if self.preview_tree.selection():
            self.preview_context_menu.post(event.x_root, event.y_root)

    def delete_from_preview_tree(self):
        selected_items = self.preview_tree.selection()
        if not selected_items: return

        paths_to_delete = []
        preview_dir_path = self.current_preview_directory
        if not preview_dir_path: return

        for item_id in selected_items:
            full_path = ""
            if not self.preview_tree.parent(item_id):
                if os.path.exists(preview_dir_path): full_path = preview_dir_path
            else:
                item_text = self.preview_tree.item(item_id, 'text')
                if " " in item_text:
                    parsed_name = item_text.split(" ", 1)[1]
                    potential_path = os.path.join(preview_dir_path, parsed_name)
                    if os.path.exists(potential_path): full_path = potential_path
            if full_path and full_path not in paths_to_delete: paths_to_delete.append(full_path)

        unique_paths = []; paths_to_delete.sort(key=len) 
        for path in paths_to_delete:
            if not any(path.startswith(p + os.sep) for p in unique_paths): unique_paths.append(path)
        
        if not unique_paths: return

        item_names = [os.path.basename(p) for p in unique_paths]
        confirm_msg = f"آیا از انتقال {len(unique_paths)} مورد به سطل زباله مطمئن هستید؟\n\n{', '.join(item_names)}"
        if not messagebox.askyesno("تأیید", confirm_msg, parent=self.master): return
        
        self.clear_preview()
        errors = []
        for path in unique_paths:
            try:
                send2trash.send2trash(path)
            except Exception as e:
                errors.append(f"خطا در انتقال {os.path.basename(path)} به سطل زباله: {e}")
        
        if errors: messagebox.showerror("خطا در حذف", "\n".join(errors))
        messagebox.showinfo("عملیات کامل شد", "موارد به سطل زباله منتقل شدند.\nبرای بروزرسانی لیست اصلی، لطفاً دوباره اسکن کنید.", parent=self.master)
        
    def on_preview_item_select(self, event):
        selection = self.preview_tree.selection()
        if not selection or not self.current_preview_directory: return
        
        item_id = selection[0]
        if not self.preview_tree.parent(item_id): return
            
        item_text = self.preview_tree.item(item_id, 'text')
        if not item_text.startswith("📄"): self.clear_media_preview(); return
            
        file_name = item_text.split(" ", 1)[1]
        file_path = os.path.join(self.current_preview_directory, file_name)

        if os.path.isfile(file_path):
            self.show_media_preview(file_path)
        else:
            self.clear_media_preview()

if __name__ == "__main__":
    if check_and_install_dependencies():
        root = tk.Tk()
        app = MainApp(root)
        root.mainloop()