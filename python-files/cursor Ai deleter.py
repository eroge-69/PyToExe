import os
import shutil
import subprocess
import winreg
import tkinter as tk
from tkinter import messagebox
import webbrowser

# مسار المستخدم
USER_PROFILE = os.environ["USERPROFILE"]

folders_to_delete = [
    os.path.join(USER_PROFILE, ".cursor"),
    os.path.join(USER_PROFILE, "AppData", "Local", "Programs", "cursor"),
    os.path.join(USER_PROFILE, "AppData", "Roaming", "Cursor")
]

def folders_exist():
    return any(os.path.exists(folder) for folder in folders_to_delete)

def program_exists_in_registry(program_name="cursor"):
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in uninstall_keys:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                if program_name.lower() in display_name.lower():
                                    return True
                        except Exception:
                            continue
            except FileNotFoundError:
                continue
    return False

def delete_folder(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return f"✔️ تم حذف المجلد:\n{path}"
    except Exception as e:
        return f"⚠️ خطأ أثناء الحذف:\n{path}\n{e}"
    return None

def uninstall_program_from_registry(program_name="cursor"):
    messages = []
    found = False

    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in uninstall_keys:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                if program_name.lower() in display_name.lower():
                                    uninstall_string, _ = winreg.QueryValueEx(subkey, "UninstallString")
                                    subprocess.run(uninstall_string, shell=True)
                                    messages.append(f"🧹 تم حذف البرنامج من النظام: {display_name}")
                                    found = True
                                    break
                        except Exception:
                            continue
            except FileNotFoundError:
                continue
    
    if not found:
        return None
    return "\n".join(messages)

def run_deletion():
    results = []

    for folder in folders_to_delete:
        msg = delete_folder(folder)
        if msg:
            results.append(msg)
    
    uninstall_result = uninstall_program_from_registry("cursor")
    if uninstall_result:
        results.append(uninstall_result)

    if results:
        messagebox.showinfo("النتائج", "\n\n".join(results))
    else:
        messagebox.showinfo("لا يوجد شيء", "لم يتم العثور على أي ملفات أو برنامج لحذفه.")

def check_and_warn():
    has_folders = folders_exist()
    has_program = program_exists_in_registry("cursor")

    if not has_folders and not has_program:
        messagebox.showinfo("لا حاجة للحذف", "Cursor AI غير موجود أو تم حذفه مسبقًا ✅")
        root.destroy()
    else:
        info.set("البرنامج موجود وجاهز للحذف 🧹")

def open_instagram(event=None):
    webbrowser.open_new("http://instagram.com/aio.tv1")

# واجهة المستخدم
root = tk.Tk()
root.title("Cursor AI Deleter")
root.geometry("350x240")
root.resizable(False, False)

info = tk.StringVar()
info.set("...جاري الفحص")

label = tk.Label(root, textvariable=info, font=("Arial", 12))
label.pack(pady=20)

btn = tk.Button(root, text="احذف Cursor", font=("Arial", 14), bg="#e74c3c", fg="white", command=run_deletion)
btn.pack(pady=10)

note = tk.Label(root, text="💡 تأكد من تشغيل البرنامج كمسؤول", fg="gray", font=("Arial", 9))
note.pack(pady=10)

# رابط AIO
credit = tk.Label(root, text="by AIO", fg="#4A90E2", cursor="hand2", font=("Arial", 10, "underline"))
credit.pack(pady=5)
credit.bind("<Button-1>", open_instagram)

# الفحص التلقائي
root.after(300, check_and_warn)

root.mainloop()
