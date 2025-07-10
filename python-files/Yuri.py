import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import shutil
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import fitz
import threading

class AppSettings:
    SETTINGS_FILE = "user_settings.txt"
    DEFAULT_SETTINGS = {
        "language": "ar",
        "theme": "light"
    }

    @staticmethod
    def save_settings(data):
        try:
            with open(AppSettings.SETTINGS_FILE, "w", encoding="utf-8") as f:
                for k, v in data.items():
                    f.write(f"{k}={v}\n")
        except IOError as e:
            messagebox.showerror("خطأ", f"فشل حفظ الإعدادات: {e}")

    @staticmethod
    def load_settings():
        settings = AppSettings.DEFAULT_SETTINGS.copy()
        if not os.path.exists(AppSettings.SETTINGS_FILE):
            return settings
        try:
            with open(AppSettings.SETTINGS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        settings[k] = v
            return settings
        except IOError as e:
            messagebox.showerror("خطأ", f"فشل تحميل الإعدادات: {e}")
            return AppSettings.DEFAULT_SETTINGS.copy()

class FileUtils:
    @staticmethod
    def sort_numerically(files):
        def get_numeric_key(filename):
            base_name = os.path.splitext(filename)[0]
            numbers = ''.join(filter(str.isdigit, base_name))
            return int(numbers) if numbers else 0
        return sorted(files, key=get_numeric_key)

    @staticmethod
    def open_folder(path):
        if os.path.exists(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}")')
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل فتح المجلد: {e}")

    @staticmethod
    def get_valid_images(folder):
        return [f for f in os.listdir(folder)
               if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

class WindowUtils:
    @staticmethod
    def center_window(parent, child):
        child.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        child_width = child.winfo_width()
        child_height = child.winfo_height()
        x = parent_x + (parent_width // 2) - (child_width // 2)
        y = parent_y + (parent_height // 2) - (child_height // 2)
        child.geometry(f'+{x}+{y}')

    @staticmethod
    def create_option_window(parent, title, options):
        win = tk.Toplevel(parent)
        win.title(title)
        win.geometry("350x200")
        WindowUtils.center_window(parent, win)
        win.transient(parent)
        win.grab_set()
        for text, cmd in options:
            btn = ttk.Button(win, text=text, width=30, command=lambda c=cmd: [c(), win.destroy()])
            btn.pack(pady=5, padx=10, fill=tk.X)
        return win

class Localization:
    MESSAGES = {
        "ar": {
            "app_title": "أداة Cherry - إدارة الصور و PDF",
            "tab_conversions": "🔁 تحويل الصور وPDF",
            "tab_processing": "🖼️ معالجة الصور",
            "tab_organization": "📝 تنظيم الملفات",
            "tab_settings": "⚙️ إعدادات التطبيق",
            "status_ready": "جاهز",
            "btn_convert_folder_to_pdf": "تحويل مجلد إلى PDF",
            "btn_convert_multi_folder_to_pdf": "تحويل عدة مجلدات إلى PDF",
            "btn_pdf_to_images": "PDF إلى صور",
            "btn_change_image_format": "تغيير صيغة الصور",
            "btn_merge_images": "دمج الصور",
            "btn_split_long_images": "قص الصور الطويلة",
            "btn_merge_vertically": "دمج في صورة واحدة (طولياً)",
            "btn_rename_custom_pattern": "إعادة تسمية الصور بنمط مخصص",
            "btn_rename_sequentially": "ترقيم الصور تلقائيًا",
            "dialog_select_image_folder": "اختر مجلد الصور",
            "dialog_select_root_folder": "اختر المجلد الرئيسي",
            "dialog_select_pdf_file": "اختر ملف PDF",
            "dialog_select_rename_folder": "اختر مجلد لإعادة التسمية",
            "dialog_select_merge_files": "اختر الصور لدمجها",
            "dialog_select_merge_folder": "اختر مجلد صور",
            "dialog_save_merged_image": "احفظ الصورة المدموجة باسم:",
            "dialog_select_split_files": "اختر الصور لقصها",
            "dialog_select_split_folder": "اختر مجلد صور لقصها",
            "info_no_valid_images": "لا توجد صور صالحة في المجلد.",
            "info_pdf_created": "تم إنشاء PDF بنجاح: {}",
            "info_folder_processed": "تم معالجة {} مجلد من أصل {}.",
            "info_no_subfolders": "لم يتم العثور على مجلدات فرعية.",
            "info_no_images_found": "لم يتم العثور على صور.",
            "info_images_merged_success": "تم دمج الصور بنجاح.",
            "info_pdf_pages_extracted": "تم استخراج الصفحات إلى صور بنجاح!\n{}",
            "info_no_pattern_entered": "لم يتم إدخال نمط للاسم. تم الإلغاء.",
            "info_no_start_number": "لم يتم إدخال رقم البداية. تم الإلغاء.",
            "info_images_renamed_success": "تمت إعادة تسمية {} صورة بنجاح!",
            "info_no_images_renamed": "لم يتم إعادة تسمية أي صور.",
            "info_images_sequentially_renamed": "تمت إعادة ترقيم الصور بنجاح!",
            "info_pdf_no_pages": "ملف PDF لا يحتوي على صفحات.",
            "info_coming_soon": "هذه الميزة قيد التطوير وسيتم دعمها قريباً.",
            "info_images_splitted_success": "تم قص الصور الطويلة بنجاح!",
            "error_save_settings_failed": "فشل حفظ الإعدادات: {}",
            "error_load_settings_failed": "فشل تحميل الإعدادات: {}",
            "error_open_folder_failed": "فشل فتح المجلد: {}",
            "error_conversion_failed": "حدث خطأ أثناء التحويل: {}",
            "error_folder_conversion_failed": "خطأ في مجلد {}: {}",
            "error_merge_failed": "حدث خطأ أثناء الدمج:\n{}",
            "error_image_split_failed": "فشل قص الصورة {}: {}",
            "error_pdf_extraction_failed": "حدث خطأ أثناء استخراج PDF: {}",
            "error_rename_failed": "فشل إعادة التسمية: {}\n{}",
            "prompt_pages_per_image": "كم صورة تدمج في كل صفحة؟",
            "prompt_num_splits": "كم عدد القصات لكل صورة؟ (1 - 100)",
            "prompt_rename_pattern": "أدخل النمط (مثلاً: Scan_ أو Page). استخدم {} للرقم المتسلسل.",
            "prompt_rename_pattern_default": "أدخل النمط (مثلاً: Scan_ أو Page_). استخدم {} للرقم المتسلسل.\nاتركه فارغًا للنمط الافتراضي 'page_'",
            "prompt_start_number": "من أي رقم تبدأ؟",
            "prompt_num_digits": "أدخل عدد الخانات للأرقام (1-5).\nمثال: 4 خانات تعطي 0001",
            "option_select_files": "📂 اختر صور",
            "option_select_folder": "📁 اختر مجلد",
            "option_back": "🔙 رجوع",
            "window_select_image_source": "اختيار مصدر الصور",
            "settings_language": "اللغة:",
            "settings_theme": "الوضع:",
            "theme_light": "فاتح",
            "theme_dark": "داكن",
            "app_version": "الإصدار: {}",
            "restart_required_message": "لتطبيق هذه التغييرات، برجاء إعادة تشغيل التطبيق.",
            "restart_required_title": "إعادة تشغيل مطلوبة",
            "save_settings_btn": "حفظ الإعدادات",
            "dialog_select_images_to_convert": "اختر الصور للتحويل",
            "dialog_select_folder_to_convert": "اختر مجلد للتحويل",
            "prompt_select_output_format": "اختر صيغة الإخراج:",
            "format_png": "PNG",
            "format_jpg": "JPG",
            "format_webp": "WEBP",
            "prompt_jpg_quality": "جودة JPG:",
            "info_image_format_converted": "تم تحويل {} صورة إلى صيغة {} بنجاح.",
            "error_image_format_conversion_failed": "فشل تحويل الصورة {}: {}",
            "info_no_images_selected_for_conversion": "لم يتم اختيار أي صور للتحويل.",
            "progress_converting_images": "جاري تحويل الصور...",
            "progress_converting_pdf": "جاري تحويل PDF...",
            "progress_processing_folders": "جاري معالجة المجلدات...",
            "progress_extracting_pages": "جاري استخراج الصفحات...",
            "progress_renaming_images": "جاري إعادة تسمية الصور...",
            "progress_merging_images": "جاري دمج الصور...",
            "progress_splitting_images": "جاري قص الصور..."
        },
        "en": {
            "app_title": "Cherry Tool - Image & PDF Management",
            "tab_conversions": "🔁 Image & PDF Conversions",
            "tab_processing": "🖼️ Image Processing",
            "tab_organization": "📝 File Organization",
            "tab_settings": "⚙️ App Settings",
            "status_ready": "Ready",
            "btn_convert_folder_to_pdf": "Convert Folder to PDF",
            "btn_convert_multi_folder_to_pdf": "Convert Multiple Folders to PDF",
            "btn_pdf_to_images": "PDF to Images",
            "btn_change_image_format": "Change Image Format",
            "btn_merge_images": "Merge Images",
            "btn_split_long_images": "Split Long Images",
            "btn_merge_vertically": "Merge into one image (Vertically)",
            "btn_rename_custom_pattern": "Rename Images with Custom Pattern",
            "btn_rename_sequentially": "Auto-Number Images",
            "dialog_select_image_folder": "Select Image Folder",
            "dialog_select_root_folder": "Select Root Folder",
            "dialog_select_pdf_file": "Select PDF File",
            "dialog_select_rename_folder": "Select Folder to Rename",
            "dialog_select_merge_files": "Select Images to Merge",
            "dialog_select_merge_folder": "Select Image Folder",
            "dialog_save_merged_image": "Save Merged Image As:",
            "dialog_select_split_files": "Select Images to Split",
            "dialog_select_split_folder": "Select Image Folder to Split",
            "info_no_valid_images": "No valid images found in folder.",
            "info_pdf_created": "PDF created successfully: {}",
            "info_folder_processed": "Processed {} out of {} folders.",
            "info_no_subfolders": "No subfolders found.",
            "info_no_images_found": "No images found.",
            "info_images_merged_success": "Images merged successfully.",
            "info_pdf_pages_extracted": "PDF pages extracted successfully!\n{}",
            "info_no_pattern_entered": "No pattern entered. Canceled.",
            "info_no_start_number": "No start number entered. Canceled.",
            "info_images_renamed_success": "Successfully renamed {} images!",
            "info_no_images_renamed": "No images renamed.",
            "info_images_sequentially_renamed": "Images renumbered successfully!",
            "info_pdf_no_pages": "PDF file contains no pages.",
            "info_coming_soon": "This feature is under development and will be supported soon.",
            "info_images_splitted_success": "Long images split successfully!",
            "error_save_settings_failed": "Failed to save settings: {}",
            "error_load_settings_failed": "Failed to load settings: {}",
            "error_open_folder_failed": "Failed to open folder: {}",
            "error_conversion_failed": "An error occurred during conversion: {}",
            "error_folder_conversion_failed": "Error in folder {}: {}",
            "error_merge_failed": "An error occurred during merging:\n{}",
            "error_image_split_failed": "Failed to crop image {}: {}",
            "error_pdf_extraction_failed": "An error occurred during PDF extraction: {}",
            "error_rename_failed": "Rename failed: {}\n{}",
            "prompt_pages_per_image": "How many images per page?",
            "prompt_num_splits": "How many splits per image? (1 - 100)",
            "prompt_rename_pattern": "Enter pattern (e.g., Scan_ or Page). Use {} for sequence number.",
            "prompt_rename_pattern_default": "Enter pattern (e.g., Scan_ or Page_). Use {} for sequence number.\nLeave empty for default pattern 'page_'",
            "prompt_start_number": "Start from which number?",
            "prompt_num_digits": "Enter number of digits for numbering (1-5).\nExample: 4 digits gives 0001",
            "option_select_files": "📂 Select Files",
            "option_select_folder": "📁 Select Folder",
            "option_back": "🔙 Back",
            "window_select_image_source": "Select Image Source",
            "settings_language": "Language:",
            "settings_theme": "Theme:",
            "theme_light": "Light",
            "theme_dark": "Dark",
            "app_version": "Version: {}",
            "restart_required_message": "To apply these changes, please restart the application.",
            "restart_required_title": "Restart Required",
            "save_settings_btn": "Save Settings",
            "dialog_select_images_to_convert": "Select images to convert",
            "dialog_select_folder_to_convert": "Select folder to convert",
            "prompt_select_output_format": "Select output format:",
            "format_png": "PNG",
            "format_jpg": "JPG",
            "format_webp": "WEBP",
            "prompt_jpg_quality": "JPG Quality:",
            "info_image_format_converted": "Successfully converted {} images to {} format.",
            "error_image_format_conversion_failed": "Failed to convert image {}: {}",
            "info_no_images_selected_for_conversion": "No images selected for conversion.",
            "progress_converting_images": "Converting images...",
            "progress_converting_pdf": "Converting PDF...",
            "progress_processing_folders": "Processing folders...",
            "progress_extracting_pages": "Extracting pages...",
            "progress_renaming_images": "Renaming images...",
            "progress_merging_images": "Merging images...",
            "progress_splitting_images": "Splitting images..."
        }
    }

    @staticmethod
    def get_message(key, lang="ar"):
        return Localization.MESSAGES.get(lang, Localization.MESSAGES["ar"]).get(key, key)

class PDFConverter:
    pass

class ImageProcessor:
    @staticmethod
    def merge_images(files, pages_per_image, app_instance):
        if not files:
            app_instance.root.after(0, lambda: messagebox.showinfo("خطأ", Localization.get_message("info_no_images_found", app_instance.current_language)))
            return
        output_dir = os.path.dirname(files[0]) or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("progress_merging_images", app_instance.current_language)))
        app_instance.root.after(0, lambda: app_instance.progress_bar.configure(maximum=len(files)))
        app_instance.root.after(0, lambda: app_instance.progress_bar.configure(value=0))
        imgs = []
        try:
            for i, f in enumerate(files):
                img_obj = Image.open(f).convert("RGB")
                imgs.append(img_obj)
                app_instance.root.after(0, lambda i_val=i+1: app_instance.progress_bar.configure(value=i_val))
            groups = [imgs[i:i+pages_per_image]
                     for i in range(0, len(imgs), pages_per_image)]
            for idx, group in enumerate(groups):
                if not group:
                    continue
                max_width_in_group = max(img.width for img in group)
                resized_group = []
                for img in group:
                    if img.width != max_width_in_group:
                        aspect_ratio = img.height / img.width
                        new_height = int(max_width_in_group * aspect_ratio)
                        resized_group.append(img.resize((max_width_in_group, new_height), Image.Resampling.LANCZOS))
                    else:
                        resized_group.append(img)
                total_height_in_group = sum(im.height for im in resized_group)
                merged_img = Image.new("RGB", (max_width_in_group, total_height_in_group), (255, 255, 255))
                y_offset = 0
                for im in resized_group:
                    merged_img.paste(im, (0, y_offset))
                    y_offset += im.height
                merged_img.save(os.path.join(output_dir, f"merged_{idx+1:03}.jpg"))
                merged_img.close()
                for img in resized_group:
                    img.close()
            app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("status_ready", app_instance.current_language)))
            app_instance.root.after(0, lambda: messagebox.showinfo("تم", Localization.get_message("info_images_merged_success", app_instance.current_language)))
            app_instance.root.after(0, lambda: FileUtils.open_folder(output_dir))
        except Exception as e:
            app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("status_ready", app_instance.current_language)))
            app_instance.root.after(0, lambda: messagebox.showerror("خطأ", Localization.get_message("error_merge_failed", app_instance.current_language).format(e)))
        finally:
            for img_obj in imgs:
                try:
                    img_obj.close()
                except Exception:
                    pass
            app_instance.root.after(0, lambda: app_instance.progress_bar.configure(value=0))

    @staticmethod
    def split_image(image_path, num_splits, output_dir, app_instance):
        img = None
        try:
            img = Image.open(image_path).convert("RGB")
            w, h = img.size
            split_h = h // num_splits
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            for i in range(num_splits):
                box = (0, i * split_h, w,
                      (i + 1) * split_h if i < num_splits - 1 else h)
                cropped_img = img.crop(box)
                cropped_img.save(os.path.join(output_dir, f"{base_name}_part{i+1:03}.webp"), quality=100)
                cropped_img.close()
        except Exception as e:
            app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("status_ready", app_instance.current_language)))
            app_instance.root.after(0, lambda: messagebox.showerror("خطأ", app_instance.get_text("error_image_split_failed").format(os.path.basename(image_path), e)))
            raise
        finally:
            if img:
                img.close()

    @staticmethod
    def change_image_format_logic(files, output_format, jpg_quality, app_instance):
        if not files:
            app_instance.root.after(0, lambda: messagebox.showinfo(app_instance.get_text("app_title"), app_instance.get_text("info_no_images_selected_for_conversion")))
            return
        first_file_dir = os.path.dirname(files[0])
        output_subfolder = os.path.join(first_file_dir, f"converted_{output_format.upper()}")
        os.makedirs(output_subfolder, exist_ok=True)
        app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("progress_converting_images", app_instance.current_language)))
        app_instance.root.after(0, lambda: app_instance.progress_bar.configure(maximum=len(files)))
        app_instance.root.after(0, lambda: app_instance.progress_bar.configure(value=0))
        converted_count = 0
        errors = []
        for i, file_path in enumerate(files):
            img = None
            try:
                img = Image.open(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_subfolder, f"{base_name}.{output_format.lower()}")
                if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img.save(output_path, quality=jpg_quality, optimize=True)
                else:
                    img.save(output_path)
                converted_count += 1
            except Exception as e:
                errors.append(app_instance.get_text("error_image_format_conversion_failed").format(os.path.basename(file_path), e))
            finally:
                if img:
                    img.close()
                app_instance.root.after(0, lambda i_val=i+1: app_instance.progress_bar.configure(value=i_val))
        app_instance.root.after(0, lambda: app_instance.update_status(Localization.get_message("status_ready", app_instance.current_language)))
        if errors:
            app_instance.root.after(0, lambda: messagebox.showwarning(app_instance.get_text("app_title"), "\n".join(errors[:5])))
        app_instance.root.after(0, lambda: messagebox.showinfo(app_instance.get_text("app_title"), app_instance.get_text("info_image_format_converted").format(converted_count, output_format.upper())))
        app_instance.root.after(0, lambda: FileUtils.open_folder(output_subfolder))
        app_instance.root.after(0, lambda: app_instance.progress_bar.configure(value=0))

class CherryApp:
    APP_VERSION = "1.0"

    def __init__(self, root):
        self.root = root
        self.settings = AppSettings.load_settings()
        self.current_language = self.settings.get("language", "ar")
        self.current_theme = self.settings.get("theme", "light")
        self.setup_ui()
        self.apply_theme()
        self.update_ui_texts()

    def get_text(self, key):
        return Localization.get_message(key, self.current_language)

    def setup_ui(self):
        self.root.title(self.get_text("app_title"))
        self.root.geometry("700x550")
        self.center_window()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.conversion_frame = ttk.Frame(self.notebook)
        self.processing_frame = ttk.Frame(self.notebook)
        self.organization_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conversion_frame, text="")
        self.notebook.add(self.processing_frame, text="")
        self.notebook.add(self.organization_frame, text="")
        self.notebook.add(self.settings_frame, text="")
        self.create_status_bar()

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def apply_theme(self):
        if self.current_theme == "dark":
            bg_color = '#2e2e2e'
            fg_color = 'white'
            btn_bg = '#4a7a8c'
            btn_fg = 'white'
            active_btn_bg = '#3a6a7c'
            pressed_btn_bg = '#2a5a6c'
        else:
            bg_color = 'white'
            fg_color = 'black'
            btn_bg = '#007bff'
            btn_fg = 'white'
            active_btn_bg = '#0056b3'
            pressed_btn_bg = '#004085'
        self.root.configure(bg=bg_color)
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton',
                             padding=6,
                             relief=tk.FLAT,
                             background=btn_bg,
                             foreground=btn_fg,
                             font=('Arial', 10))
        self.style.map('TButton',
                       background=[('active', active_btn_bg), ('pressed', pressed_btn_bg)])
        self.style.configure('TNotebook', background=bg_color, borderwidth=0)
        self.style.map('TNotebook.Tab',
                       background=[('selected', btn_bg), ('!selected', bg_color)],
                       foreground=[('selected', 'white'), ('!selected', fg_color)])
        self.style.configure('TRadiobutton',
                             background=bg_color,
                             foreground=fg_color,
                             font=('Arial', 9))
        self.style.map('TRadiobutton',
                       background=[('active', bg_color), ('selected', bg_color)],
                       foreground=[('active', fg_color), ('selected', fg_color)])
        self.style.configure('TProgressbar', background=btn_bg, troughcolor=bg_color)

    def create_conversion_tab(self):
        for widget in self.conversion_frame.winfo_children():
            widget.destroy()
        buttons = [
            (self.get_text("btn_convert_folder_to_pdf"), self.convert_images_to_pdf),
            (self.get_text("btn_convert_multi_folder_to_pdf"), self.multi_folder_to_pdf),
            (self.get_text("btn_pdf_to_images"), self.pdf_to_images),
            (self.get_text("btn_change_image_format"), self.show_image_format_conversion_options)
        ]
        for text, cmd in buttons:
            btn = ttk.Button(self.conversion_frame, text=text, command=cmd)
            btn.pack(pady=8, padx=20, fill=tk.X)

    def create_processing_tab(self):
        for widget in self.processing_frame.winfo_children():
            widget.destroy()
        button_frame = ttk.Frame(self.processing_frame)
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        buttons = [
            (self.get_text("btn_merge_images"), self.show_merge_options),
            (self.get_text("btn_split_long_images"), self.show_split_options),
            (self.get_text("btn_merge_vertically"), self.merge_images_vertically),
        ]
        for text, cmd in buttons:
            btn = ttk.Button(button_frame, text=text, command=cmd)
            btn.pack(pady=8, padx=20, fill=tk.X)

    def create_organization_tab(self):
        for widget in self.organization_frame.winfo_children():
            widget.destroy()
        btn_rename_custom = ttk.Button(self.organization_frame,
                                       text=self.get_text("btn_rename_custom_pattern"),
                                       command=self.rename_images)
        btn_rename_custom.pack(pady=15, padx=20, fill=tk.X)
        btn_rename_seq = ttk.Button(self.organization_frame,
                                    text=self.get_text("btn_rename_sequentially"),
                                    command=self.rename_images_sequentially)
        btn_rename_seq.pack(pady=5, padx=20, fill=tk.X)

    def create_settings_tab(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        lang_label = ttk.Label(self.settings_frame, text=self.get_text("settings_language"))
        lang_label.pack(pady=10, padx=20, anchor=tk.W)
        self.lang_var = tk.StringVar(value=self.current_language)
        lang_options = [("ar", "العربية"), ("en", "English")]
        for val, text in lang_options:
            ttk.Radiobutton(self.settings_frame, text=text, variable=self.lang_var,
                            value=val, command=self.on_settings_change).pack(padx=30, anchor=tk.W)
        theme_label = ttk.Label(self.settings_frame, text=self.get_text("settings_theme"))
        theme_label.pack(pady=10, padx=20, anchor=tk.W)
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_options = [("light", self.get_text("theme_light")), ("dark", self.get_text("theme_dark"))]
        for val, text in theme_options:
            ttk.Radiobutton(self.settings_frame, text=text, variable=self.theme_var,
                            value=val, command=self.on_settings_change).pack(padx=30, anchor=tk.W)
        save_btn = ttk.Button(self.settings_frame, text=self.get_text("save_settings_btn"), command=self.save_and_apply_settings)
        save_btn.pack(pady=20, padx=20)
        self.version_label = ttk.Label(self.settings_frame, text=self.get_text("app_version").format(self.APP_VERSION))
        self.version_label.pack(side=tk.BOTTOM, pady=10)

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.status_var = tk.StringVar()
        self.status_var.set(self.get_text("status_ready"))
        self.status_label = ttk.Label(status_frame,
                              textvariable=self.status_var,
                              anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        self.progress_bar["value"] = 0

    def update_status(self, message):
        self.status_var.set(message)

    def update_ui_texts(self):
        self.root.title(self.get_text("app_title"))
        self.notebook.tab(0, text=self.get_text("tab_conversions"))
        self.notebook.tab(1, text=self.get_text("tab_processing"))
        self.notebook.tab(2, text=self.get_text("tab_organization"))
        self.notebook.tab(3, text=self.get_text("tab_settings"))
        self.status_var.set(self.get_text("status_ready"))
        self.create_conversion_tab()
        self.create_processing_tab()
        self.create_organization_tab()
        self.create_settings_tab()
        self.apply_theme()

    def on_settings_change(self):
        pass

    def save_and_apply_settings(self):
        old_language = self.current_language
        old_theme = self.current_theme
        new_language = self.lang_var.get()
        new_theme = self.theme_var.get()
        self.current_language = new_language
        self.current_theme = new_theme
        self.settings["language"] = new_language
        self.settings["theme"] = new_theme
        AppSettings.save_settings(self.settings)
        if old_theme != new_theme:
            self.apply_theme()
        if old_language != new_language:
            self.update_ui_texts()
            messagebox.showinfo(self.get_text("restart_required_title"),
                                self.get_text("restart_required_message"))
        else:
            messagebox.showinfo(self.get_text("app_title"), self.get_text("save_settings_btn").replace("حفظ ", "تم حفظ "))

    def show_merge_options(self):
        options = [
            (self.get_text("option_select_files"), self.merge_from_files),
            (self.get_text("option_select_folder"), self.merge_from_folder),
            (self.get_text("option_back"), lambda: None)
        ]
        win = WindowUtils.create_option_window(
            self.root,
            self.get_text("window_select_image_source"),
            options
        )
        self.root.wait_window(win)

    def show_split_options(self):
        options = [
            (self.get_text("option_select_files"), self.split_from_files),
            (self.get_text("option_select_folder"), self.split_from_folder),
            (self.get_text("option_back"), lambda: None)
        ]
        win = WindowUtils.create_option_window(
            self.root,
            self.get_text("window_select_image_source"),
            options
        )
        self.root.wait_window(win)

    def show_image_format_conversion_options(self):
        options = [
            (self.get_text("option_select_files"), self.change_image_format_from_files),
            (self.get_text("option_select_folder"), self.change_image_format_from_folder),
            (self.get_text("option_back"), lambda: None)
        ]
        win = WindowUtils.create_option_window(
            self.root,
            self.get_text("window_select_image_source"),
            options
        )
        self.root.wait_window(win)

    def change_image_format_from_files(self):
        file_paths = filedialog.askopenfilenames(
            title=self.get_text("dialog_select_images_to_convert"),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
        )
        if file_paths:
            self.prompt_and_convert_image_format(list(file_paths))

    def change_image_format_from_folder(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_folder_to_convert"))
        if folder:
            files = [os.path.join(folder, f) for f in FileUtils.get_valid_images(folder)]
            if files:
                self.prompt_and_convert_image_format(files)
            else:
                messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_valid_images"))

    def prompt_and_convert_image_format(self, files):
        if not files:
            return
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text("prompt_select_output_format"))
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        output_format_var = tk.StringVar(value="png")
        formats_frame = ttk.LabelFrame(dialog, text=self.get_text("prompt_select_output_format"))
        formats_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Radiobutton(formats_frame, text=self.get_text("format_png"), variable=output_format_var, value="png").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Radiobutton(formats_frame, text=self.get_text("format_jpg"), variable=output_format_var, value="jpg").pack(anchor=tk.W, padx=10, pady=2)
        ttk.Radiobutton(formats_frame, text=self.get_text("format_webp"), variable=output_format_var, value="webp").pack(anchor=tk.W, padx=10, pady=2)
        quality_frame = ttk.Frame(dialog)
        quality_frame.pack(pady=5, padx=20, fill=tk.X)
        ttk.Label(quality_frame, text=self.get_text("prompt_jpg_quality")).pack(side=tk.LEFT)
        quality_percentage_var = tk.StringVar(value="90%")
        quality_percentage_label = ttk.Label(quality_frame, textvariable=quality_percentage_var)
        quality_percentage_label.pack(side=tk.RIGHT, padx=5)
        jpg_quality_scale = ttk.Scale(
            quality_frame,
            from_=5,
            to=100,
            orient=tk.HORIZONTAL,
            length=150,
        )
        jpg_quality_scale.set(90)
        def update_quality_label(event=None):
            current_value = jpg_quality_scale.get()
            if event and (event.num == 4 or event.delta > 0):
                current_value = min(100, current_value + 5)
            elif event and (event.num == 5 or event.delta < 0):
                current_value = max(5, current_value - 5)
            rounded_value = round(current_value / 5) * 5
            rounded_value = max(5, min(100, rounded_value))
            jpg_quality_scale.set(rounded_value)
            quality_percentage_var.set(f"{int(rounded_value)}%")
        jpg_quality_scale.bind("<Motion>", update_quality_label)
        jpg_quality_scale.bind("<ButtonRelease-1>", update_quality_label)
        jpg_quality_scale.bind("<MouseWheel>", update_quality_label)
        jpg_quality_scale.bind("<Button-4>", update_quality_label)
        jpg_quality_scale.bind("<Button-5>", update_quality_label)
        update_quality_label()
        dialog.update_idletasks()
        WindowUtils.center_window(self.root, dialog)
        def start_conversion():
            selected_format = output_format_var.get()
            quality = int(jpg_quality_scale.get()) if selected_format in ["jpg", "jpeg"] else None
            dialog.destroy()
            threading.Thread(target=self._change_image_format_logic_task, args=(files, selected_format, quality)).start()
        ttk.Button(dialog, text=self.get_text("save_settings_btn").replace("حفظ ", "بدء "), command=start_conversion).pack(pady=10)
        self.root.wait_window(dialog)

    def _change_image_format_logic_task(self, files, output_format, jpg_quality):
        ImageProcessor.change_image_format_logic(files, output_format, jpg_quality, self)

    def merge_images_vertically(self):
        file_paths = filedialog.askopenfilenames(
            title=self.get_text("dialog_select_merge_files"),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if file_paths:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png")],
                title=self.get_text("dialog_save_merged_image")
            )
            if output_path:
                threading.Thread(target=self._merge_images_vertically_task, args=(file_paths, output_path)).start()

    def _merge_images_vertically_task(self, file_paths, output_path):
        try:
            self.root.after(0, lambda: self.update_status(self.get_text("progress_merging_images")))
            self.root.after(0, lambda: self.progress_bar.configure(mode="indeterminate"))
            self.root.after(0, lambda: self.progress_bar.start())
            images_to_close = []
            try:
                images = [Image.open(img).convert("RGBA") for img in file_paths]
                images_to_close.extend(images)
                if not images:
                    self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_images_found")))
                    return
                width = max(img.width for img in images)
                resized_images = [img.resize((width, int(img.height * (width / img.width))), Image.Resampling.LANCZOS) for img in images]
                total_height = sum(img.height for img in resized_images)
                merged_image = Image.new('RGBA', (width, total_height))
                y_offset = 0
                for img in resized_images:
                    merged_image.paste(img, (0, y_offset))
                    y_offset += img.height
                merged_image.save(output_path)
                merged_image.close()
                self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_images_merged_success")))
                self.root.after(0, lambda: FileUtils.open_folder(os.path.dirname(output_path)))
            finally:
                for img_obj in images_to_close:
                    try:
                        img_obj.close()
                    except Exception:
                        pass
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.get_text("app_title"), self.get_text("error_merge_failed").format(e)))
        finally:
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.progress_bar.configure(mode="determinate"))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))

    def merge_from_files(self):
        files = filedialog.askopenfilenames(
            title=self.get_text("dialog_select_merge_files"),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
        )
        if files:
            pages = simpledialog.askinteger(
                self.get_text("app_title"),
                self.get_text("prompt_pages_per_image"),
                minvalue=1,
                maxvalue=100
            )
            if pages:
                threading.Thread(target=self._merge_images_task, args=(list(files), pages)).start()

    def merge_from_folder(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_merge_folder"))
        if folder:
            files = [os.path.join(folder, f)
                    for f in FileUtils.get_valid_images(folder)]
            files = FileUtils.sort_numerically(files)
            if files:
                pages = simpledialog.askinteger(
                    self.get_text("app_title"),
                    self.get_text("prompt_pages_per_image"),
                    minvalue=1,
                    maxvalue=100
                )
                if pages:
                    threading.Thread(target=self._merge_images_task, args=(files, pages)).start()

    def _merge_images_task(self, files, pages_per_image):
        ImageProcessor.merge_images(files, pages_per_image, self)

    def split_from_files(self):
        files = filedialog.askopenfilenames(
            title=self.get_text("dialog_select_split_files"),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
        )
        if files:
            self.process_split_images(list(files))

    def split_from_folder(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_split_folder"))
        if folder:
            files = [os.path.join(folder, f)
                    for f in FileUtils.get_valid_images(folder)]
            files = FileUtils.sort_numerically(files)
            if files:
                self.process_split_images(files)

    def process_split_images(self, files):
        num_splits = simpledialog.askinteger(
            self.get_text("app_title"),
            self.get_text("prompt_num_splits"),
            minvalue=1,
            maxvalue=100
        )
        if not num_splits:
            return
        threading.Thread(target=self._process_split_images_task, args=(files, num_splits)).start()

    def _process_split_images_task(self, files, num_splits):
        if not files:
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_valid_images")))
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            return
        output_dir = os.path.join(os.path.dirname(files[0]), "splitted_images")
        os.makedirs(output_dir, exist_ok=True)
        self.root.after(0, lambda: self.update_status(self.get_text("progress_splitting_images")))
        self.root.after(0, lambda: self.progress_bar.configure(maximum=len(files)))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))
        errors = []
        for i, path in enumerate(files):
            try:
                ImageProcessor.split_image(path, num_splits, output_dir, self)
            except Exception as e:
                errors.append(str(e))
            finally:
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
        self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
        if errors:
            self.root.after(0, lambda: messagebox.showwarning(self.get_text("app_title"), "\n".join(errors[:3])))
        self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_images_splitted_success")))
        self.root.after(0, lambda: FileUtils.open_folder(output_dir))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def convert_images_to_pdf(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_image_folder"))
        if folder:
            threading.Thread(target=self._convert_images_to_pdf_task, args=(folder,)).start()

    def _convert_images_to_pdf_task(self, folder):
        images = FileUtils.get_valid_images(folder)
        if not images:
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_valid_images")))
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            return
        images = FileUtils.sort_numerically(images)
        pdf_path = os.path.join(folder, "output.pdf")
        self.root.after(0, lambda: self.update_status(self.get_text("progress_converting_pdf")))
        self.root.after(0, lambda: self.progress_bar.configure(maximum=len(images)))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))
        image_list = []
        try:
            for i, img_name in enumerate(images):
                img_full_path = os.path.join(folder, img_name)
                img_obj = Image.open(img_full_path).convert("RGB")
                image_list.append(img_obj)
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
            if image_list:
                image_list[0].save(
                    pdf_path,
                    save_all=True,
                    append_images=image_list[1:],
                    optimize=True
                )
                self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_pdf_created").format(pdf_path)))
                self.root.after(0, lambda: FileUtils.open_folder(folder))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(self.get_text("app_title"), self.get_text("error_conversion_failed").format(e)))
        finally:
            for img_obj in image_list:
                try:
                    img_obj.close()
                except Exception:
                    pass
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def multi_folder_to_pdf(self):
        root_dir = filedialog.askdirectory(title=self.get_text("dialog_select_root_folder"))
        if not root_dir:
            return
        threading.Thread(target=self._multi_folder_to_pdf_task, args=(root_dir,)).start()

    def _multi_folder_to_pdf_task(self, root_dir):
        subfolders = [os.path.join(root_dir, f)
                      for f in os.listdir(root_dir)
                      if os.path.isdir(os.path.join(root_dir, f))]
        if not subfolders:
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_subfolders")))
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            return
        self.root.after(0, lambda: self.update_status(self.get_text("progress_processing_folders")))
        self.root.after(0, lambda: self.progress_bar.configure(maximum=len(subfolders)))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))
        processed = 0
        pdf_output_dir = os.path.join(root_dir, "PDF")
        os.makedirs(pdf_output_dir, exist_ok=True)
        for i, folder in enumerate(subfolders):
            images = FileUtils.get_valid_images(folder)
            if not images:
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
                continue
            images = FileUtils.sort_numerically(images)
            image_list = []
            try:
                for img_name in images:
                    img_obj = Image.open(os.path.join(folder, img_name)).convert("RGB")
                    image_list.append(img_obj)
                folder_name = os.path.basename(folder)
                pdf_name = f"{folder_name}.pdf"
                pdf_path = os.path.join(folder, pdf_name)
                if image_list:
                    image_list[0].save(
                        pdf_path,
                        save_all=True,
                        append_images=image_list[1:],
                        optimize=True
                    )
                    shutil.copy(pdf_path, os.path.join(pdf_output_dir, pdf_name))
                    processed += 1
            except Exception as e:
                self.root.after(0, lambda f=folder, err=e: messagebox.showerror(self.get_text("app_title"), self.get_text("error_folder_conversion_failed").format(f, err)))
                continue
            finally:
                for img_obj in image_list:
                    try:
                        img_obj.close()
                    except Exception:
                        pass
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
        self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
        self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_folder_processed").format(processed, len(subfolders))))
        self.root.after(0, lambda: FileUtils.open_folder(pdf_output_dir))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def pdf_to_images(self):
        pdf_file = filedialog.askopenfilename(title=self.get_text("dialog_select_pdf_file"), filetypes=[("PDF Files", "*.pdf")])
        if not pdf_file:
            return
        threading.Thread(target=self._pdf_to_images_task, args=(pdf_file,)).start()

    def _pdf_to_images_task(self, pdf_file):
        save_dir = os.path.splitext(pdf_file)[0] + "_images"
        os.makedirs(save_dir, exist_ok=True)
        self.root.after(0, lambda: self.update_status(self.get_text("progress_extracting_pages")))
        self.root.after(0, lambda: self.progress_bar.configure(mode="indeterminate"))
        self.root.after(0, lambda: self.progress_bar.start())
        doc = None
        try:
            doc = fitz.open(pdf_file)
            if not doc.page_count:
                self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_pdf_no_pages")))
                return
            self.root.after(0, lambda count=doc.page_count: self.progress_bar.configure(maximum=count))
            self.root.after(0, lambda: self.progress_bar.configure(mode="determinate"))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                output = os.path.join(save_dir, f"page_{i+1:03}.png")
                pix.save(output)
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_pdf_pages_extracted").format(save_dir)))
            self.root.after(0, lambda: FileUtils.open_folder(save_dir))
        except Exception as e:
            self.root.after(0, lambda err=e: messagebox.showerror(self.get_text("app_title"), self.get_text("error_pdf_extraction_failed").format(err)))
        finally:
            if doc:
                doc.close()
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.progress_bar.configure(mode="determinate"))
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))

    def rename_images(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_rename_folder"))
        if not folder:
            return
        images = FileUtils.sort_numerically(FileUtils.get_valid_images(folder))
        if not images:
            messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_valid_images"))
            return
        pattern = simpledialog.askstring(
            self.get_text("app_title"),
            self.get_text("prompt_rename_pattern_default")
        )
        if pattern is None:
            return
        if pattern == "":
            pattern = "page_"
        start = 1
        threading.Thread(target=self._rename_images_task, args=(folder, images, pattern, start)).start()

    def _rename_images_task(self, folder, images, pattern, start):
        self.root.after(0, lambda: self.update_status(self.get_text("progress_renaming_images")))
        self.root.after(0, lambda: self.progress_bar.configure(maximum=len(images)))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))
        renamed = 0
        errors = []
        for i, old_name in enumerate(images):
            try:
                ext = os.path.splitext(old_name)[1]
                calculated_num_digits = len(str(len(images) + start - 1)) if len(images) > 0 else 1
                num_digits_for_format = max(2, calculated_num_digits)
                if "{}" in pattern:
                    new_name = pattern.format(start + i) + ext
                else:
                    new_name = f"{pattern}{start + i:0{num_digits_for_format}d}{ext}"
                old_path = os.path.join(folder, old_name)
                new_path = os.path.join(folder, new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    renamed += 1
            except Exception as e:
                errors.append(self.get_text("error_rename_failed").format(old_name, e))
                continue
            finally:
                self.root.after(0, lambda i_val=i+1: self.progress_bar.configure(value=i_val))
        self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
        if errors:
            self.root.after(0, lambda: messagebox.showwarning(self.get_text("app_title"), "\n".join(errors[:3])))
        if renamed > 0:
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_images_renamed_success").format(renamed)))
            self.root.after(0, lambda: FileUtils.open_folder(folder))
        else:
            self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_images_renamed")))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def rename_images_sequentially(self):
        folder = filedialog.askdirectory(title=self.get_text("dialog_select_rename_folder"))
        if not folder:
            return
        images = FileUtils.sort_numerically(FileUtils.get_valid_images(folder))
        if not images:
            messagebox.showinfo(self.get_text("app_title"), self.get_text("info_no_valid_images"))
            return
        num_digits = simpledialog.askinteger(
            self.get_text("app_title"),
            self.get_text("prompt_num_digits"),
            minvalue=1,
            maxvalue=5
        )
        if num_digits is None:
            return
        threading.Thread(target=self._rename_images_sequentially_task, args=(folder, images, num_digits)).start()

    def _rename_images_sequentially_task(self, folder, images, num_digits):
        self.root.after(0, lambda: self.update_status(self.get_text("progress_renaming_images")))
        self.root.after(0, lambda: self.progress_bar.configure(maximum=len(images)))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))
        for i, old_name in enumerate(images, start=1):
            try:
                ext = os.path.splitext(old_name)[1]
                new_name = f"{i:0{num_digits}d}{ext}"
                old_path = os.path.join(folder, old_name)
                new_path = os.path.join(folder, new_name)
                if old_path != new_path:
                    os.rename(old_path, new_path)
            except Exception as e:
                self.root.after(0, lambda old_n=old_name, err=e: messagebox.showerror(self.get_text("app_title"), self.get_text("error_rename_failed").format(old_n, err)))
                self.root.after(0, lambda: self.progress_bar.configure(value=0))
                self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
                return
            finally:
                self.root.after(0, lambda i_val=i: self.progress_bar.configure(value=i_val))
        self.root.after(0, lambda: self.update_status(self.get_text("status_ready")))
        self.root.after(0, lambda: messagebox.showinfo(self.get_text("app_title"), self.get_text("info_images_sequentially_renamed")))
        self.root.after(0, lambda: FileUtils.open_folder(folder))
        self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def show_coming_soon(self):
        messagebox.showinfo(self.get_text("app_title"), self.get_text("info_coming_soon"))

if __name__ == "__main__":
    root = tk.Tk()
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "cherry_icon.ico-2.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
        else:
            print(f"Warning: Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Warning: Could not load icon: {e}")
    app = CherryApp(root)
    root.mainloop()