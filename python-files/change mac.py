import subprocess
import random
import os
import sys
import winreg
import uuid
import ctypes  # <-- هذا السطر كان مفقود

def is_admin():
    """التحقق من صلاحيات المدير"""
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_as_admin():
    """تشغيل الكود بصلاحيات المدير"""
    if is_admin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False

def generate_random_mac():
    """إنتاج عنوان MAC عشوائي"""
    mac = [0x02, 0x00, 0x00, 
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def change_mac_address(interface_name):
    """تغيير عنوان MAC للواجهة المحددة"""
    try:
        new_mac = generate_random_mac().replace(':', '')
        
        print(f"محاولة تغيير MAC لـ: {interface_name}")
        
        # إيقاف الواجهة
        subprocess.run(f'netsh interface set interface "{interface_name}" admin=disable', 
                      shell=True, check=True)
        
        # تغيير عنوان MAC في الريجستري
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                subkey_count = winreg.QueryInfoKey(key)[0]
                
                for i in range(subkey_count):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = f"{reg_path}\\{subkey_name}"
                        
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_ALL_ACCESS) as subkey:
                            try:
                                # البحث عن الواجهة الصحيحة
                                adapter_desc, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                                if any(word in adapter_desc.lower() for word in ['ethernet', 'wireless', 'wi-fi', 'network']):
                                    winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                                    print(f"تم تغيير MAC لـ {interface_name} إلى: {new_mac}")
                                    break
                            except FileNotFoundError:
                                continue
                    except OSError:
                        continue
        except Exception as e:
            print(f"تعذر الوصول للريجستري: {e}")
        
        # إعادة تشغيل الواجهة
        subprocess.run(f'netsh interface set interface "{interface_name}" admin=enable', 
                      shell=True, check=True)
        
        return new_mac
        
    except Exception as e:
        print(f"خطأ في تغيير MAC: {e}")
        return None

def change_computer_name():
    """تغيير اسم الكمبيوتر"""
    try:
        new_name = f"PC-{random.randint(1000, 9999)}"
        cmd = f'wmic computersystem where name="%computername%" call rename name="{new_name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"تم تغيير اسم الكمبيوتر إلى: {new_name}")
            return new_name
        else:
            print(f"فشل تغيير اسم الكمبيوتر: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"خطأ في تغيير اسم الكمبيوتر: {e}")
        return None

def change_machine_guid():
    """تغيير Machine GUID"""
    try:
        new_guid = str(uuid.uuid4())
        reg_path = r"SOFTWARE\Microsoft\Cryptography"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            print(f"تم تغيير Machine GUID إلى: {new_guid}")
            return new_guid
            
    except Exception as e:
        print(f"خطأ في تغيير Machine GUID: {e}")
        return None

def change_installation_id():
    """تغيير Installation ID"""
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_DWORD, random.randint(1000000000, 1999999999))
            print(f"تم تغيير Installation ID")
            return True
            
    except Exception as e:
        print(f"خطأ في تغيير Installation ID: {e}")
        return False

def get_network_interfaces():
    """الحصول على قائمة بواجهات الشبكة"""
    try:
        result = subprocess.run('netsh interface show interface', 
                              shell=True, capture_output=True, text=True)
        
        interfaces = []
        lines = result.stdout.split('\n')[3:]  # تجاهل العناوين
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 4 and parts[1] == "Connected":
                    interface_name = ' '.join(parts[3:])
                    interfaces.append(interface_name)
        
        return interfaces
        
    except Exception as e:
        print(f"خطأ في الحصول على واجهات الشبكة: {e}")
        return []

def clear_system_logs():
    """مسح سجلات النظام"""
    try:
        logs = ['System', 'Application', 'Security']
        for log in logs:
            try:
                subprocess.run(f'wevtutil cl {log}', shell=True, check=True)
                print(f"تم مسح سجل {log}")
            except subprocess.CalledProcessError:
                print(f"تعذر مسح سجل {log}")
        return True
    except Exception as e:
        print(f"خطأ في مسح السجلات: {e}")
        return False

def main():
    """الوظيفة الرئيسية"""
    print("=" * 50)
    print("أداة تغيير هوية الجهاز - Windows 10")
    print("=" * 50)
    
    if not is_admin():
        print("يتطلب تشغيل البرنامج بصلاحيات المدير...")
        print("سيتم إعادة تشغيل البرنامج بصلاحيات المدير...")
        run_as_admin()
        return
    
    try:
        print("تم تشغيل البرنامج بصلاحيات المدير ✓")
        
        # عرض واجهات الشبكة
        interfaces = get_network_interfaces()
        if interfaces:
            print(f"\nتم العثور على {len(interfaces)} واجهة شبكة متصلة:")
            for i, interface in enumerate(interfaces):
                print(f"{i+1}. {interface}")
            
            print("\nخيارات تغيير MAC:")
            print("1. تغيير MAC لواجهة واحدة")
            print("2. تغيير MAC لجميع الواجهات")
            print("3. تخطي تغيير MAC")
            
            choice = input("اختر (1-3): ").strip()
            
            if choice == "1":
                try:
                    interface_num = int(input("أدخل رقم الواجهة: ")) - 1
                    if 0 <= interface_num < len(interfaces):
                        change_mac_address(interfaces[interface_num])
                    else:
                        print("رقم واجهة غير صحيح")
                except ValueError:
                    print("يرجى إدخال رقم صحيح")
            elif choice == "2":
                for interface in interfaces:
                    change_mac_address(interface)
            elif choice == "3":
                print("تم تخطي تغيير MAC")
            else:
                print("اختيار غير صحيح")
        else:
            print("لم يتم العثور على واجهات شبكة متصلة")
        
        # تغيير بيانات النظام الأخرى
        print("\nتغيير بيانات النظام...")
        
        system_choice = input("هل تريد تغيير بيانات النظام (اسم الكمبيوتر، GUID، إلخ)؟ (y/n): ")
        if system_choice.lower() == 'y':
            change_computer_name()
            change_machine_guid()
            change_installation_id()
        
        # مسح السجلات (اختياري)
        clear_logs = input("\nهل تريد مسح سجلات النظام؟ (y/n): ")
        if clear_logs.lower() == 'y':
            clear_system_logs()
        
        print("\n" + "=" * 50)
        print("تم الانتهاء من عملية تغيير هوية الجهاز!")
        print("يُنصح بإعادة تشغيل الجهاز لتطبيق جميع التغييرات")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\nتم إلغاء العملية بواسطة المستخدم")
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
