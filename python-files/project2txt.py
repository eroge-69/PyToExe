import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

HISTORY_FILE = "path_history.txt"
OUTPUT_NAMES = ["myfiles.txt", "task.txt"]

# لیست اکستنشن‌های غیر متنی برای فیلتر کردن
NON_TEXT_EXTENSIONS = [
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", # تصاویر
    ".mp3", ".wav", ".aac", ".flac", ".ogg", # صدا
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", # ویدئو
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", # اسناد
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", # آرشیو
    ".exe", ".dll", ".so", ".obj", ".bin", # باینری/اجرایی
    ".ttf", ".otf", ".woff", ".woff2", # فونت
    ".db", ".sqlite", ".mdb", # دیتابیس
    ".iso", ".img", # ایمیج دیسک
]

folder_names = {}  # مسیر نسبی فولدر -> BooleanVar
ext_names = {}     # اکستنشن -> BooleanVar (فقط برای اکستنشن‌های مجاز و متنی)
file_names = {}    # مسیر نسبی فایل (غیر از جاوا و فقط متنی) -> BooleanVar
all_scanned_files = {} # مسیر نسبی فایل -> اکستنشن (شامل تمام فایل‌های متنی برای فیلتر کردن)
root_path = ""


def load_history():
    return open(HISTORY_FILE, "r", encoding="utf-8").read().splitlines() if os.path.exists(HISTORY_FILE) else []


def save_history(path):
    history = load_history()
    if path in history:
        history.remove(path)
    history.insert(0, path)
    history = history[:5]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(history))


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        combo_path.set(folder)
        save_history(folder)
        combo_path["values"] = load_history()


def is_text_file(ext):
    """بررسی می‌کند که آیا یک اکستنشن متنی است یا خیر."""
    return ext.lower() not in NON_TEXT_EXTENSIONS


def scan_folder():
    global root_path
    folder = combo_path.get().strip()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("خطا", "لطفاً مسیر معتبر انتخاب کنید")
        return

    root_path = folder
    folder_names.clear()
    ext_names.clear()
    file_names.clear()
    all_scanned_files.clear() # پاک کردن لیست جامع فایل‌ها

    for dirpath, dirnames, filenames in os.walk(folder):
        rel_folder = os.path.relpath(dirpath, folder)
        folder_names[rel_folder] = tk.BooleanVar(value=True) # همه فولدرها در ابتدا تیک خورده

        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            rel_file = os.path.relpath(os.path.join(dirpath, file), root_path)

            if not is_text_file(ext): # اگر فایل غیر متنی بود، کلاً نادیده بگیر
                continue

            # اگر فایل متنی بود، آن را به لیست جامع فایل‌های اسکن شده اضافه کن
            all_scanned_files[rel_file] = ext 

            if ext: # اگر اکستنشن داشت و متنی بود
                if ext not in ext_names:
                    # .java به صورت پیشفرض تیک خورده باشد، سایر اکستنشن‌های متنی خیر
                    ext_names[ext] = tk.BooleanVar(value=(ext == ".java"))

            # فایل‌های غیر جاوا و متنی به لیست file_names اضافه می‌شوند با وضعیت تیک‌نخورده
            if ext != ".java":
                file_names[rel_file] = tk.BooleanVar(value=False)


    refresh_lists()


def toggle_extension(ext):
    # این تابع فقط نیاز به فراخوانی refresh_lists دارد تا UI بروزرسانی شود
    refresh_lists()


def toggle_folder(folder_name):
    is_checked = folder_names[folder_name].get()

    if not is_checked: # اگر تیک برداشته شده
        to_remove_folders = [f for f in list(folder_names) if f != folder_name and f.startswith(folder_name + os.sep)]
        for f in to_remove_folders:
            if f in folder_names: # اطمینان از وجود در دیکشنری قبل از دسترسی
                folder_names[f].set(False)
        folder_names[folder_name].set(False)
    else: # اگر تیک خورده
        abs_folder = os.path.join(root_path, folder_name)
        for dirpath, dirnames, _ in os.walk(abs_folder):
            rel_sub_folder = os.path.relpath(dirpath, root_path)
            if rel_sub_folder not in folder_names: # اگر فولدر جدیدی پیدا شد
                folder_names[rel_sub_folder] = tk.BooleanVar(value=True)
            else:
                folder_names[rel_sub_folder].set(True)
        folder_names[folder_name].set(True)

    refresh_lists()


def refresh_lists():
    # پاک کردن UI
    for widget in scroll_frame_folders.winfo_children():
        widget.destroy()
    for widget in frame_exts.winfo_children():
        widget.destroy()

    # فولدرها
    ttk.Label(scroll_frame_folders, text="Folders:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    sorted_folder_names_items = sorted(folder_names.items(), key=lambda item: (item[0] != ".", item[0]))
    for name, var in sorted_folder_names_items:
        display_name = name if name != "." else os.path.basename(root_path) + " (root)"
        ttk.Checkbutton(scroll_frame_folders, text=display_name, variable=var,
                        command=lambda n=name: toggle_folder(n)).pack(anchor="w")


    # فایل‌های غیر جاوا
    # فقط در صورتی عنوان "Files (excluding .java):" را نمایش بده که حداقل یک اکستنشن غیر جاوا و متنی تیک خورده باشد
    show_files_label = False
    for ext, var in ext_names.items():
        if ext != ".java" and var.get():
            show_files_label = True
            break
    
    if show_files_label:
        ttk.Label(scroll_frame_folders, text="Files (excluding .java):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,0))

    # نمایش فایل‌های غیر جاوا و متنی که اکستنشنشان تیک خورده و فولدر والدشان هم تیک خورده است
    for name, var in sorted(file_names.items()):
        file_ext = all_scanned_files.get(name) # اکستنشن واقعی فایل از لیست جامع
        
        # اطمینان حاصل شود که اکستنشن فایل موجود است و تیک خورده است
        if file_ext and ext_names.get(file_ext, tk.BooleanVar(value=False)).get(): 
            folder_of_file = os.path.dirname(name)
            
            # بررسی تیک فولدر والد
            folder_is_checked = False
            if folder_of_file == "" and folder_names.get(".", tk.BooleanVar(value=False)).get():
                folder_is_checked = True
            elif folder_of_file != "" and folder_names.get(folder_of_file, tk.BooleanVar(value=False)).get():
                folder_is_checked = True

            if folder_is_checked:
                ttk.Checkbutton(scroll_frame_folders, text=name, variable=var).pack(anchor="w")


    # اکستنشن‌ها (فقط متنی‌ها)
    ttk.Label(frame_exts, text="Extensions (Text Files Only):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    for name, var in sorted(ext_names.items()):
        # ext_names از قبل فقط شامل اکستنشن‌های متنی است، پس نیازی به is_text_file اینجا نیست
        ttk.Checkbutton(frame_exts, text=name, variable=var,
                        command=lambda n=name: toggle_extension(n)).pack(anchor="w")


def merge_files():
    if not root_path:
        messagebox.showerror("خطا", "ابتدا مسیر را اسکن کنید")
        return

    selected_files_to_merge = []

    # 1. افزودن فایل‌های غیر جاوا و متنی که دستی تیک خورده‌اند و فولدر والدشان هم تیک خورده است
    for file_rel, var in file_names.items():
        file_ext = all_scanned_files.get(file_rel) # اکستنشن واقعی فایل

        # فقط فایل‌هایی که اکستنشنشان متنی است و جاوا نیست
        if file_ext and file_ext != ".java":
            if var.get(): # اگر فایل دستی تیک خورده است
                folder_of_file = os.path.dirname(file_rel)
                # چک کن که فولدر والد تیک خورده باشد
                if (folder_of_file == "" and folder_names.get(".", tk.BooleanVar(value=False)).get()) or \
                   (folder_of_file != "" and folder_names.get(folder_of_file, tk.BooleanVar(value=False)).get()):
                    selected_files_to_merge.append(file_rel)

    # 2. افزودن فایل‌های جاوا (متنی) اگر اکستنشن .java تیک خورده باشد و فولدر والدشان هم تیک خورده باشد
    if ext_names.get(".java", tk.BooleanVar(value=False)).get():
        for file_rel, ext in all_scanned_files.items():
            if ext == ".java":
                folder_of_file = os.path.dirname(file_rel)
                if (folder_of_file == "" and folder_names.get(".", tk.BooleanVar(value=False)).get()) or \
                   (folder_of_file != "" and folder_names.get(folder_of_file, tk.BooleanVar(value=False)).get()):
                    selected_files_to_merge.append(file_rel)


    output_name = combo_output.get().strip() or "myfiles.txt"
    output_file = os.path.join(os.path.dirname(__file__), output_name)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_rel in sorted(list(set(selected_files_to_merge))):
            file_path = os.path.join(root_path, file_rel)
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write("// =========================================================================================\n")
                    outfile.write(f"// FILE: {file_rel}\n")
                    outfile.write("// =========================================================================================\n")
                    outfile.write(infile.read() + '\n\n')
            except Exception as e:
                outfile.write(f"// ERROR reading {file_rel}: {e}\n\n")

    messagebox.showinfo("انجام شد", f"فایل '{output_file}' ساخته شد")


# GUI (بدون تغییر)
root = tk.Tk()
root.title("Merge Files Tool")
root.geometry("900x600")

# مسیر ورودی
ttk.Label(root, text="مسیر ورودی:").pack(anchor="w", padx=5, pady=(5, 0))
path_frame = ttk.Frame(root)
path_frame.pack(fill="x", padx=5)
combo_path = ttk.Combobox(path_frame, values=load_history(), width=80)
combo_path.pack(side="left", fill="x", expand=True)
btn_browse = ttk.Button(path_frame, text="انتخاب پوشه", command=browse_folder)
btn_browse.pack(side="left", padx=5)

# خروجی
ttk.Label(root, text="نام فایل خروجی:").pack(anchor="w", padx=5, pady=(5, 0))
combo_output = ttk.Combobox(root, values=OUTPUT_NAMES)
combo_output.set("myfiles.txt")
combo_output.pack(fill="x", padx=5, pady=5)

# دکمه‌ها کنار هم
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)
ttk.Button(btn_frame, text="Scan", width=15, command=scan_folder).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Extract", width=15, command=merge_files).pack(side="left", padx=5)

# قاب اصلی با دو بخش
frame_lists = ttk.Frame(root)
frame_lists.pack(fill="both", expand=True)

# قاب فولدرها با اسکرول
frame_folders = ttk.LabelFrame(frame_lists, text="فایل‌ها و فولدرها")
frame_folders.pack(side="left", fill="both", expand=True, padx=5, pady=5)
canvas_folders = tk.Canvas(frame_folders)
scroll_frame_folders = ttk.Frame(canvas_folders)
scroll_y = ttk.Scrollbar(frame_folders, orient="vertical", command=canvas_folders.yview)
canvas_folders.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
canvas_folders.pack(side="left", fill="both", expand=True)
canvas_folders.create_window((0, 0), window=scroll_frame_folders, anchor="nw")
scroll_frame_folders.bind("<Configure>", lambda e: canvas_folders.configure(scrollregion=canvas_folders.bbox("all")))

# قاب اکستنشن‌ها
frame_exts = ttk.LabelFrame(frame_lists, text="اکستنشن‌ها")
frame_exts.pack(side="right", fill="both", expand=True, padx=5, pady=5)

root.mainloop()

