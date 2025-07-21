# ===================================================================================
# Course Progress Tracker v1.0
# Developed by Gemini
# A professional, modern, and feature-rich application to track video course progress.
# ===================================================================================

import tkinter
import tkinter.messagebox
from tkinter import filedialog
import customtkinter as ctk
import os
import json
import re
from PIL import Image

# --- إعدادات أساسية للبرنامج ---
APP_NAME = "متتبع الكورسات الاحترافي"
APP_WIDTH = 1100
APP_HEIGHT = 700
DATA_FILE_NAME = "course_data.json"

# --- الفرز الطبيعي لأسماء الملفات (لضمان ترتيب 1, 2, ... 10) ---
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

# --- الفئة الرئيسية للبرنامج ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- إعدادات النافذة الرئيسية ---
        self.title(APP_NAME)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(800, 600)
        
        # --- تحميل الأيقونات ---
        self.add_icon = self.load_icon("add.png", (20, 20)) # سيتم إنشاء أيقونات افتراضية لو لم توجد
        self.folder_icon = self.load_icon("folder.png", (20, 20))

        # --- إعداد تخطيط الواجهة ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- الإطار العلوي للأزرار والتحكم ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(2, weight=1)

        self.app_title_label = ctk.CTkLabel(self.header_frame, text=APP_NAME, font=ctk.CTkFont(size=20, weight="bold"))
        self.app_title_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.add_course_button = ctk.CTkButton(self.header_frame, text="إضافة كورس جديد", image=self.add_icon, command=self.add_course_dialog)
        self.add_course_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.header_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=0, column=3, padx=20, pady=10, sticky="e")
        self.appearance_mode_menu.set("Dark")

        # --- نظام التبويبات (Tabs) ---
        self.tab_view = ctk.CTkTabview(self, anchor="ne", command=self.on_tab_change)
        self.tab_view.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tab_view.grid_remove() # إخفاء التبويبات حتى يتم إضافة كورس
        
        # --- رسالة البدء ---
        self.welcome_frame = ctk.CTkFrame(self)
        self.welcome_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.welcome_label = ctk.CTkLabel(self.welcome_frame, text="لم تبدأ بعد.\n\nانقر على 'إضافة كورس جديد' لبدء رحلتك التعليمية!", font=ctk.CTkFont(size=18))
        self.welcome_label.pack(expand=True, padx=20, pady=20)
        
        # --- تهيئة البيانات ---
        self.data = self.load_data()
        self.current_course_path = None
        self.video_widgets = {} # لتخزين عناصر الواجهة لكل فيديو
        
        self.load_courses_from_data()

    # --- دالة تحميل الأيقونات (مع إنشاء أيقونة افتراضية) ---
    def load_icon(self, name, size):
        try:
            return ctk.CTkImage(Image.open(name), size=size)
        except FileNotFoundError:
            # في حال عدم وجود ملف الأيقونة، قم بإنشاء صورة بيضاء بسيطة
            print(f"Warning: Icon '{name}' not found. Using a placeholder.")
            placeholder = Image.new('RGBA', size, (255, 255, 255, 0)) # شفاف
            return ctk.CTkImage(placeholder, size=size)

    # --- دوال إدارة البيانات (حفظ وتحميل) ---
    def get_data_path(self):
        # حفظ ملف البيانات في مجلد بيانات التطبيق للمستخدم الحالي
        app_data_path = os.getenv('APPDATA')
        app_folder = os.path.join(app_data_path, APP_NAME)
        os.makedirs(app_folder, exist_ok=True)
        return os.path.join(app_folder, DATA_FILE_NAME)

    def load_data(self):
        data_path = self.get_data_path()
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {} # ملف تالف أو فارغ
        return {}

    def save_data(self):
        if not self.data: return
        data_path = self.get_data_path()
        try:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except IOError:
            tkinter.messagebox.showerror("خطأ في الحفظ", "لم يتمكن البرنامج من حفظ البيانات. تأكد من وجود صلاحيات كافية.")

    # --- دوال إدارة الكورسات ---
    def add_course_dialog(self):
        folder_path = filedialog.askdirectory(title="اختر مجلد الكورس")
        if not folder_path:
            return
        
        if folder_path in self.data:
            tkinter.messagebox.showinfo("موجود بالفعل", "هذا الكورس موجود بالفعل في قائمتك.")
            self.tab_view.set(self.get_course_display_name(folder_path))
            return
            
        course_name = os.path.basename(folder_path)
        videos = self.scan_for_videos(folder_path)

        if not videos:
            tkinter.messagebox.showwarning("لا توجد فيديوهات", "لم يتم العثور على أي ملفات فيديو مدعومة في هذا المجلد.")
            return

        self.data[folder_path] = {
            "display_name": course_name,
            "videos": {video: {"watched": False, "slider": 0, "notes": ""} for video in videos}
        }
        
        self.add_course_tab(folder_path)
        self.tab_view.set(course_name)
        self.save_data()

    def add_course_tab(self, course_path):
        if not self.tab_view.winfo_ismapped():
            self.welcome_frame.grid_remove()
            self.tab_view.grid()
        
        course_data = self.data[course_path]
        display_name = course_data["display_name"]
        
        tab = self.tab_view.add(display_name)
        
        # --- محتويات التبويب ---
        # إطار التحكم داخل التبويب (بحث، ...)
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        search_label = ctk.CTkLabel(control_frame, text="ابحث عن فيديو:")
        search_label.pack(side="right", padx=(0, 10))
        
        search_entry = ctk.CTkEntry(control_frame, placeholder_text="اكتب اسم الفيديو...")
        search_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        search_entry.bind("<KeyRelease>", lambda event, cp=course_path: self.filter_videos(event, cp))

        # إطار المحتوى القابل للتمرير
        scrollable_frame = ctk.CTkScrollableFrame(tab, label_text=f"فيديوهات الكورس: {display_name}")
        scrollable_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.video_widgets[course_path] = {
            "tab": tab,
            "search": search_entry,
            "frame": scrollable_frame,
            "rows": []
        }

        self.populate_video_list(course_path)

    def populate_video_list(self, course_path, filter_text=""):
        widgets = self.video_widgets[course_path]
        frame = widgets["frame"]
        
        # حذف الصفوف القديمة
        for row_frame in widgets["rows"]:
            row_frame.destroy()
        widgets["rows"].clear()

        course_data = self.data[course_path]
        videos = course_data["videos"]
        
        # الفرز الطبيعي
        sorted_videos = sorted(videos.keys(), key=natural_sort_key)
        
        row_index = 0
        for video_name in sorted_videos:
            if filter_text.lower() not in video_name.lower():
                continue
            
            video_info = videos[video_name]
            
            # إطار الصف لكل فيديو
            row_frame = ctk.CTkFrame(frame, border_width=1)
            row_frame.pack(fill="x", padx=5, pady=5, expand=True)
            row_frame.grid_columnconfigure(3, weight=1)

            # خانة الاختيار
            watched_var = ctk.BooleanVar(value=video_info["watched"])
            checkbox = ctk.CTkCheckBox(row_frame, text="", variable=watched_var,
                                       command=lambda vn=video_name, v=watched_var: self.update_data(course_path, vn, "watched", v.get()))
            checkbox.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

            # اسم الفيديو
            video_label = ctk.CTkLabel(row_frame, text=video_name, anchor="e", justify="right")
            video_label.grid(row=0, column=1, columnspan=2, padx=5, pady=(5,0), sticky="ew")

            # شريط التطبيق
            slider_label = ctk.CTkLabel(row_frame, text="مستوى التطبيق: 0%", anchor="e", justify="right")
            slider_label.grid(row=1, column=1, padx=5, pady=(0,5), sticky="w")
            
            slider = ctk.CTkSlider(row_frame, from_=0, to=100, number_of_steps=100,
                                   command=lambda value, vn=video_name, sl=slider_label: self.on_slider_change(value, vn, sl, course_path))
            slider.set(video_info["slider"])
            slider_label.configure(text=f"مستوى التطبيق: {int(video_info['slider'])}%")
            slider.grid(row=1, column=2, padx=5, pady=(0,5), sticky="ew")

            # خانة الملاحظات
            notes_entry = ctk.CTkTextbox(row_frame, height=60, wrap="word")
            notes_entry.insert("1.0", video_info["notes"])
            notes_entry.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="ew")
            notes_entry.bind("<KeyRelease>", lambda event, vn=video_name: self.update_data(course_path, vn, "notes", event.widget.get("1.0", "end-1c")))
            
            widgets["rows"].append(row_frame)
            row_index += 1

    def scan_for_videos(self, folder_path):
        supported_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
        videos = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) and os.path.splitext(item)[1].lower() in supported_extensions:
                videos.append(item)
        return videos

    def load_courses_from_data(self):
        for course_path in self.data.keys():
            if os.path.isdir(course_path): # التحقق من أن المجلد لا يزال موجودًا
                self.add_course_tab(course_path)
            else:
                # يمكن إضافة منطق لإعلام المستخدم بأن المجلد مفقود
                print(f"Warning: Course path not found: {course_path}")
        
        if self.data and self.tab_view.get() is not None:
             self.on_tab_change() # لتحديث المسار الحالي عند البدء

    # --- دوال التفاعل والأحداث ---
    def on_slider_change(self, value, video_name, slider_label, course_path):
        slider_label.configure(text=f"مستوى التطبيق: {int(value)}%")
        self.update_data(course_path, video_name, "slider", value)
    
    def update_data(self, course_path, video_name, key, value):
        if course_path in self.data and video_name in self.data[course_path]["videos"]:
            self.data[course_path]["videos"][video_name][key] = value
            self.save_data() # الحفظ التلقائي عند أي تغيير

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def get_course_path_from_display_name(self, display_name):
        for path, details in self.data.items():
            if details['display_name'] == display_name:
                return path
        return None

    def get_course_display_name(self, course_path):
        return self.data.get(course_path, {}).get('display_name', os.path.basename(course_path))

    def on_tab_change(self):
        current_tab_name = self.tab_view.get()
        if current_tab_name:
            self.current_course_path = self.get_course_path_from_display_name(current_tab_name)
    
    def filter_videos(self, event, course_path):
        search_term = event.widget.get()
        self.populate_video_list(course_path, filter_text=search_term)


# --- نقطة انطلاق البرنامج ---
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # الوضع الافتراضي
    ctk.set_default_color_theme("blue")  # الثيم الافتراضي
    
    app = App()
    app.mainloop()