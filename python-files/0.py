import shutil
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import json
import winsound
from tkinterdnd2 import DND_FILES, TkinterDnD

# ----- إعدادات المجلدات الفرعية -----
SUB_FOLDERS_FILE = "sub_folders.txt"
SETTINGS_FILE = "settings.json"

def load_settings():
    """تحميل الإعدادات المحفوظة"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """حفظ الإعدادات"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_sub_folders():
    if os.path.exists(SUB_FOLDERS_FILE):
        with open(SUB_FOLDERS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return ["شهادات", "أوامر إدارية", "لجان", "شكر وتقدير", "خاص بالتدريس", "نشاطات", "أخرى"]

def save_sub_folders(folders):
    with open(SUB_FOLDERS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(folders))

def play_notification_sound():
    """تشغيل صوت إشعار عند الانتهاء"""
    try:
        # تشغيل صوت النظام الافتراضي
        winsound.MessageBeep(winsound.MB_OK)
    except:
        # في حالة عدم توفر الصوت، استخدام الصوت الافتراضي
        print('\a')  # صوت الجرس

sub_folders = load_sub_folders()
settings = load_settings()

# ----- واجهة المستخدم -----
root = TkinterDnD.Tk()  # استخدام TkinterDnD بدلاً من tk.Tk العادي
root.title("\U0001F4C2 نقل الملفات إلى مجلدات التدريسيين")
root.geometry("480x720")
root.configure(bg="#f3fce8")

selected_file = ""
main_folder = ""
employee_folders = {}
all_employees = []  # قائمة جميع الموظفين
filtered_employees = []  # قائمة الموظفين المفلترة
checkboxes = {}
delete_original_var = tk.BooleanVar()
search_var = tk.StringVar()
letter_filter_var = tk.StringVar()

selected_count_label = tk.Label(root, text="عدد الاسماء المحددة: 0", fg="black", bg="#f3fce8", font=("Arial", 12))

def update_selected_count():
    selected_count = sum(var.get() for var in checkboxes.values())
    selected_count_label.config(text=f"عدد الاسماء المحددة: {selected_count}")

def filter_employees():
    """فلترة الموظفين حسب البحث والحرف المحدد"""
    global filtered_employees
    search_text = search_var.get().strip().lower()
    letter_filter = letter_filter_var.get()
    
    filtered_employees = []
    for emp in all_employees:
        # فلترة حسب النص
        if search_text and search_text not in emp.lower():
            continue
        # فلترة حسب الحرف الأول
        if letter_filter and letter_filter != "الكل" and not emp.startswith(letter_filter):
            continue
        filtered_employees.append(emp)
    
    update_employee_checkboxes()

def update_employee_checkboxes():
    """تحديث قائمة الموظفين المعروضة"""
    # حذف جميع العناصر السابقة
    for widget in checkboxes_frame.winfo_children():
        widget.destroy()
    
    # إنشاء العناصر الجديدة
    global checkboxes
    checkboxes = {}
    for emp in sorted(filtered_employees):
        var = tk.BooleanVar()
        chk = tk.Checkbutton(checkboxes_frame, text=emp, variable=var, bg="#f0f4f8", 
                           font=("Arial", 12), anchor="w", command=update_selected_count)
        chk.pack(fill="x", padx=5, pady=2, anchor="w")
        checkboxes[emp] = var
    
    checkboxes_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)
    update_selected_count()

def get_unique_letters():
    """الحصول على قائمة الأحرف الأولى الفريدة"""
    letters = set()
    for emp in all_employees:
        if emp:
            letters.add(emp[0])
    return sorted(list(letters))

def select_main_folder():
    global main_folder, employee_folders, all_employees, filtered_employees
    
    # تحميل آخر مجلد محفوظ إذا كان موجوداً
    if "last_main_folder" in settings and os.path.exists(settings["last_main_folder"]):
        folder_path = settings["last_main_folder"]
    else:
        folder_path = filedialog.askdirectory()
    
    if not folder_path:
        folder_path = filedialog.askdirectory()
    
    if folder_path:
        main_folder = folder_path
        main_folder_label.config(text="\U0001F4C1 المجلد المحدد: " + os.path.basename(folder_path), fg="blue")
        
        # حفظ المجلد في الإعدادات
        settings["last_main_folder"] = folder_path
        save_settings(settings)
        
        employee_folders = {name: os.path.join(main_folder, name) 
                          for name in os.listdir(main_folder) 
                          if os.path.isdir(os.path.join(main_folder, name))}
        
        all_employees = list(employee_folders.keys())
        filtered_employees = all_employees.copy()
        
        # تحديث قائمة الأحرف
        unique_letters = get_unique_letters()
        letter_filter_combo["values"] = ["الكل"] + unique_letters
        letter_filter_var.set("الكل")
        
        # تحديث قائمة الموظفين
        update_employee_checkboxes()

def select_all():
    for var in checkboxes.values():
        var.set(True)
    update_selected_count()

def deselect_all():
    for var in checkboxes.values():
        var.set(False)
    update_selected_count()

def drop_files(event):
    """معالجة الملفات المسحوبة والملقاة"""
    global selected_file
    files = root.tk.splitlist(event.data)
    # فلترة الملفات المسموحة فقط
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    valid_files = [f for f in files if any(f.lower().endswith(ext) for ext in allowed_extensions)]
    
    if valid_files:
        selected_file = valid_files
        file_names = [os.path.basename(f) for f in selected_file]
        file_label.config(text="\U0001F4C4 ملفات محددة: " + ", ".join(file_names), fg="green")
        
        # حفظ آخر مجلد تم اختيار الملفات منه
        if selected_file:
            last_source_folder = os.path.dirname(selected_file[0])
            settings["last_source_folder"] = last_source_folder
            save_settings(settings)
    else:
        messagebox.showwarning("تحذير", "يرجى سحب ملفات PDF أو صور فقط (PDF, JPG, PNG)")

def select_file():
    global selected_file
    
    # البدء من آخر مجلد تم اختيار الملفات منه
    initial_dir = settings.get("last_source_folder", "")
    if not initial_dir or not os.path.exists(initial_dir):
        initial_dir = ""
    
    file_paths = filedialog.askopenfilenames(
        initialdir=initial_dir,
        filetypes=[("PDF & Image Files", "*.pdf;*.jpg;*.jpeg;*.png")]
    )
    
    if file_paths:
        selected_file = file_paths
        file_names = [os.path.basename(fp) for fp in selected_file]
        file_label.config(text="\U0001F4C4 ملفات محددة: " + ", ".join(file_names), fg="green")
        
        # حفظ آخر مجلد تم اختيار الملفات منه
        last_source_folder = os.path.dirname(selected_file[0])
        settings["last_source_folder"] = last_source_folder
        save_settings(settings)

def handle_file_conflict(destination, file_name):
    existing_file_path = os.path.join(destination, file_name)
    if os.path.exists(existing_file_path):
        response = messagebox.askyesno("تأكيد", f"يوجد ملف بنفس الاسم: {file_name} في:\n{existing_file_path}.\nهل تريد استبداله؟")
        return response
    return True

def copy_file():
    if not main_folder:
        messagebox.showerror("❌ خطأ", "يرجى تحديد مجلد الأسماء أولاً!")
        return
    if not selected_file:
        messagebox.showerror("❌ خطأ", "يرجى اختيار ملف أولاً!")
        return
    selected_employees = [emp for emp, var in checkboxes.items() if var.get()]
    if not selected_employees:
        messagebox.showerror("❌ خطأ", "يرجى تحديد موظف واحد على الأقل!")
        return
    selected_sub_folder = sub_folder_var.get()
    if not selected_sub_folder:
        messagebox.showerror("❌ خطأ", "يرجى اختيار المجلد الفرعي!")
        return

    threading.Thread(target=perform_copy, args=(selected_employees, selected_sub_folder)).start()

def perform_copy(selected_employees, selected_sub_folder):
    try:
        for emp in selected_employees:
            emp_folder = employee_folders[emp]
            sub_folder = os.path.join(emp_folder, selected_sub_folder)
            if not os.path.exists(sub_folder):
                os.makedirs(sub_folder)
            for file in selected_file:
                file_name = os.path.basename(file)
                if handle_file_conflict(sub_folder, file_name):
                    try:
                        shutil.copy(file, sub_folder)
                    except Exception as e:
                        messagebox.showerror("❌ خطأ", f"فشل نقل الملف: {file_name}\nالخطأ: {str(e)}")
                        return

        if delete_original_var.get():
            for file in selected_file:
                try:
                    os.remove(file)
                except Exception as e:
                    messagebox.showerror("❌ خطأ", f"فشل حذف الملف: {os.path.basename(file)}\nالخطأ: {str(e)}")
                    return

        # تشغيل صوت الإشعار
        play_notification_sound()
        
        messagebox.showinfo("✅ نجاح", f"تم نقل الملفات بنجاح إلى المجلد ({selected_sub_folder}) لدى التدريسيين المحددين!")
        
    except Exception as e:
        messagebox.showerror("❌ خطأ", f"حدث خطأ أثناء النقل: {str(e)}")

def show_instructions():
    instructions = tk.Toplevel(root)
    instructions.title("تعليمات الاستخدام")
    instructions.geometry("500x400")
    instructions.configure(bg="#f0f4f8")

    instruction_text = (
        "كيفية استخدام التطبيق:\n\n"
        "1. اختر مجلد الأسماء الخاص بالتدريسيين.\n"
        "2. استخدم البحث أو الفلترة حسب الحرف للعثور على الموظفين.\n"
        "3. اختر الملفات بالضغط على زر 'اختر الملف' أو بسحبها وإفلاتها.\n"
        "4. قم بتحديد الموظفين الذين ترغب في نقل الملفات إليهم.\n"
        "5. اختر المجلد الفرعي أو أضف مجلد جديد.\n"
        "6. اضغط على زر 'نقل الملف' لإتمام العملية.\n"
        "7. يمكنك اختيار حذف الملفات الأصلية بعد النقل.\n"
        "8. سيتم تشغيل صوت إشعار عند الانتهاء من النقل.\n\n"
        "الميزات الجديدة:\n"
        "• تذكر آخر مجلد للأسماء ومجلد الملفات\n"
        "• البحث عن الأسماء والفلترة حسب الحرف الأول\n"
        "• السحب والإفلات للملفات\n"
        "• الإشعار الصوتي عند الانتهاء"
    )

    label = tk.Label(instructions, text=instruction_text, bg="#f0f4f8", font=("Arial", 11), justify="right")
    label.pack(pady=20, padx=20)
    tk.Button(instructions, text="إغلاق", command=instructions.destroy, bg="#DC3545", fg="white", font=("Arial", 12)).pack(pady=10)

def add_sub_folder():
    global sub_folders
    new_name = simpledialog.askstring("إضافة مجلد فرعي", "أدخل اسم المجلد الفرعي الجديد:")
    if new_name and new_name not in sub_folders:
        sub_folders.append(new_name)
        save_sub_folders(sub_folders)
        sub_folder_menu["values"] = sub_folders
        sub_folder_var.set(new_name)

def remove_sub_folder():
    global sub_folders
    current = sub_folder_var.get()
    if current in sub_folders:
        if messagebox.askyesno("تأكيد", f"هل تريد حذف المجلد الفرعي '{current}'؟"):
            sub_folders.remove(current)
            save_sub_folders(sub_folders)
            sub_folder_menu["values"] = sub_folders
            sub_folder_var.set(sub_folders[0] if sub_folders else "")

# --- إعداد واجهة المستخدم ---

# زر اختيار المجلد
tk.Button(root, text="📁 اختر مجلد الأسماء", command=select_main_folder, 
         font=("Arial", 12, "bold"), bg="#007BFF", fg="white").pack(pady=10)
main_folder_label = tk.Label(root, text="لم يتم اختيار مجلد", fg="red", bg="#f0f4f8", font=("Arial", 12))
main_folder_label.pack()

# قسم البحث والفلترة
search_frame = tk.Frame(root, bg="#f3fce8")
search_frame.pack(pady=10, padx=20, fill="x")

# مربع البحث
tk.Label(search_frame, text="🔍 البحث:", bg="#f3fce8", font=("Arial", 12)).pack(side="left")
search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 12), width=15)
search_entry.pack(side="left", padx=5)
search_entry.bind('<KeyRelease>', lambda e: filter_employees())

# قائمة الأحرف
tk.Label(search_frame, text="🔤 الحرف:", bg="#f3fce8", font=("Arial", 12)).pack(side="left", padx=(20, 5))
letter_filter_combo = ttk.Combobox(search_frame, textvariable=letter_filter_var, 
                                  values=["الكل"], width=8, font=("Arial", 12))
letter_filter_var.set("الكل")
letter_filter_combo.pack(side="left", padx=5)
letter_filter_combo.bind('<<ComboboxSelected>>', lambda e: filter_employees())

# إطار قائمة الموظفين
frame_container = tk.Frame(root)
frame_container.pack(pady=10, fill="both", expand=True)
canvas = tk.Canvas(frame_container, height=100, bg="#f0f4f8")
scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f0f4f8")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
checkboxes_frame = tk.Frame(scrollable_frame, bg="#f0f4f8")
checkboxes_frame.pack(fill="both", expand=True)

# أزرار التحديد
button_frame = tk.Frame(root, bg="#f0f4f8")
button_frame.pack(pady=5)
select_frame = tk.Frame(button_frame, bg="#f0f4f8")
select_frame.pack(side="left", padx=5)
tk.Button(select_frame, text="✔ تحديد الكل", command=select_all, 
         font=("Arial", 10, "bold"), bg="#28A745", fg="white").pack(side="left", padx=2)
tk.Button(select_frame, text="✖ إلغاء التحديد", command=deselect_all, 
         font=("Arial", 10, "bold"), bg="#DC3545", fg="white").pack(side="left", padx=2)
tk.Button(button_frame, text="❓", command=show_instructions, 
         font=("Arial", 10, "bold"), bg="#007BFF", fg="white").pack(side="right", padx=2)

# عدد الملفات المحددة
selected_count_label.pack()

# منطقة السحب والإفلات للملفات
drop_frame = tk.Frame(root, bg="#e8f4f8", relief="ridge", bd=2)
drop_frame.pack(pady=10, padx=20, fill="x")
drop_label = tk.Label(drop_frame, text="🎯 اسحب الملفات هنا أو اضغط على الزر بالأسفل", 
                     bg="#e8f4f8", font=("Arial", 12, "bold"), fg="#0066cc")
drop_label.pack(pady=20)

# تفعيل السحب والإفلات
drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', drop_files)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop_files)

# عرض الملف المحدد
file_label = tk.Label(root, text="لم يتم اختيار ملف", fg="red", bg="#f0f4f8", font=("Arial", 12))
file_label.pack()

# زر اختيار الملف
tk.Button(root, text="📄 اختر الملف المراد نقله", command=select_file, 
         font=("Arial", 12, "bold"), bg="#28A745", fg="white").pack(pady=10)

# خيار حذف الملف الأصلي
tk.Checkbutton(root, text="🗑️ حذف الملف الأصلي بعد النقل", variable=delete_original_var, 
              bg="#f3fce8", font=("Arial", 12)).pack()


# اختيار المجلد الفرعي
tk.Label(root, text="📂 اختر المجلد الفرعي:", bg="#d0e8ff", font=("Arial", 12, "bold")).pack(pady=(10, 5))
sub_folder_var = tk.StringVar(root)
sub_folder_menu = ttk.Combobox(root, textvariable=sub_folder_var, values=sub_folders, font=("Arial", 12))
sub_folder_var.set(sub_folders[0])
sub_folder_menu.pack()

# أزرار إدارة المجلدات الفرعية
sub_folder_buttons_frame = tk.Frame(root, bg="#f3fce8")
sub_folder_buttons_frame.pack(pady=5)
tk.Button(sub_folder_buttons_frame, text="➕ إضافة مجلد", command=add_sub_folder, 
         bg="#28a745", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
tk.Button(sub_folder_buttons_frame, text="🗑 حذف المحدد", command=remove_sub_folder, 
         bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

# زر النقل
tk.Button(root, text="🚀 نقــل الملــف", command=copy_file, 
         font=("Arial", 15, "bold"), bg="#DC3545", fg="white").pack(pady=20)

# معلومات المطور
tk.Label(root, text="فكرة وتنفيذ:  م.م. عمر أحمد عبدالقادر / كلية التربية للعلوم الصرفة / قسم علوم الحياة", 
         bg="#f3fce8", fg="black", font=("Arial", 9, "bold")).pack(side="bottom", pady=5)

# تحميل آخر مجلد محفوظ عند بدء التشغيل
if "last_main_folder" in settings and os.path.exists(settings["last_main_folder"]):
    root.after(100, select_main_folder)

root.mainloop()