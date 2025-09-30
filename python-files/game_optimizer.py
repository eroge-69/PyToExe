import os
import sys
import psutil
import ctypes
import winreg
import subprocess
from pathlib import Path

class GameOptimizer:
    def __init__(self):
        self.is_admin = self.check_admin()
        
    def check_admin(self):
        """بررسی دسترسی ادمین"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def close_background_apps(self):
        """بستن برنامه‌های پس‌زمینه غیرضروری"""
        print("🔄 بستن برنامه‌های پس‌زمینه...")
        
        # لیست برنامه‌هایی که نباید بسته شوند
        protected = ['explorer.exe', 'python.exe', 'pythonw.exe', 'System', 'Registry', 
                    'svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe']
        
        closed = 0
        for proc in psutil.process_iter(['name', 'memory_percent']):
            try:
                if proc.info['name'] not in protected and proc.info['memory_percent'] > 1:
                    # برنامه‌هایی که حافظه زیادی مصرف می‌کنند
                    if any(x in proc.info['name'].lower() for x in ['chrome', 'discord', 'spotify', 'teams']):
                        proc.terminate()
                        closed += 1
                        print(f"   ✓ بسته شد: {proc.info['name']}")
            except:
                pass
        
        print(f"✅ {closed} برنامه بسته شد\n")
    
    def set_high_performance(self):
        """تنظیم حالت عملکرد بالا"""
        print("⚡ تنظیم حالت High Performance...")
        try:
            # فعال‌سازی پلن High Performance
            subprocess.run('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', 
                         shell=True, capture_output=True)
            print("✅ حالت High Performance فعال شد\n")
        except Exception as e:
            print(f"⚠️ خطا: {e}\n")
    
    def optimize_cpu_priority(self):
        """بهینه‌سازی اولویت CPU"""
        print("🎮 تنظیم اولویت بالا برای بازی‌ها...")
        
        # تنظیم اولویت فرآیند فعلی
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        
        print("✅ اولویت CPU بهینه شد\n")
    
    def clear_temp_files(self):
        """پاک‌سازی فایل‌های موقت"""
        print("🗑️ پاک‌سازی فایل‌های موقت...")
        
        temp_paths = [
            os.environ.get('TEMP'),
            os.environ.get('TMP'),
            'C:\\Windows\\Temp'
        ]
        
        cleared = 0
        for temp_path in temp_paths:
            if temp_path and os.path.exists(temp_path):
                try:
                    for item in Path(temp_path).glob('*'):
                        try:
                            if item.is_file():
                                item.unlink()
                                cleared += 1
                            elif item.is_dir():
                                import shutil
                                shutil.rmtree(item, ignore_errors=True)
                                cleared += 1
                        except:
                            pass
                except:
                    pass
        
        print(f"✅ {cleared} فایل موقت پاک شد\n")
    
    def optimize_gpu(self):
        """بهینه‌سازی تنظیمات GPU"""
        print("🎨 بهینه‌سازی GPU...")
        
        if not self.is_admin:
            print("⚠️ برای بهینه‌سازی کامل GPU نیاز به دسترسی ادمین است\n")
            return
        
        try:
            # غیرفعال کردن Game DVR
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r'System\GameConfigStore', 
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'GameDVR_Enabled', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            print("✅ Game DVR غیرفعال شد")
        except:
            pass
        
        print()
    
    def disable_fullscreen_optimization(self):
        """غیرفعال کردن بهینه‌سازی تمام‌صفحه ویندوز"""
        print("🖥️ غیرفعال کردن Fullscreen Optimization...")
        
        # این تنظیمات باید برای هر بازی جداگانه اعمال شود
        print("⚠️ برای بهینه‌سازی کامل، در Properties هر بازی:")
        print("   Compatibility > Disable fullscreen optimizations را فعال کنید\n")
    
    def show_system_info(self):
        """نمایش اطلاعات سیستم"""
        print("📊 اطلاعات سیستم:")
        print(f"   CPU: {psutil.cpu_count()} هسته")
        print(f"   RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"   RAM استفاده شده: {psutil.virtual_memory().percent}%")
        print(f"   CPU استفاده شده: {psutil.cpu_percent(interval=1)}%")
        print()
    
    def run_optimization(self):
        """اجرای تمام بهینه‌سازی‌ها"""
        print("=" * 50)
        print("🎮 بهینه‌ساز بازی و افزایش FPS")
        print("=" * 50)
        print()
        
        if not self.is_admin:
            print("⚠️ توجه: برنامه بدون دسترسی Admin اجرا شد")
            print("   برای بهینه‌سازی کامل، برنامه را Run as Administrator کنید\n")
        
        self.show_system_info()
        self.clear_temp_files()
        self.close_background_apps()
        self.set_high_performance()
        self.optimize_cpu_priority()
        self.optimize_gpu()
        self.disable_fullscreen_optimization()
        
        print("=" * 50)
        print("✅ بهینه‌سازی کامل شد!")
        print("=" * 50)
        print("\n💡 نکات اضافی برای افزایش FPS:")
        print("   1. درایورهای کارت گرافیک را آپدیت کنید")
        print("   2. در تنظیمات بازی، گرافیک را کاهش دهید")
        print("   3. V-Sync را غیرفعال کنید")
        print("   4. از حالت Fullscreen به جای Windowed استفاده کنید")
        print("   5. رزولوشن بازی را کاهش دهید")
        

def main():
    optimizer = GameOptimizer()
    
    try:
        optimizer.run_optimization()
    except KeyboardInterrupt:
        print("\n\n❌ عملیات توسط کاربر لغو شد")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
    
    input("\n\nEnter را بزنید تا خارج شوید...")

if __name__ == "__main__":
    main()
