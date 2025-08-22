print("Hello, World!")
import socket
import subprocess
import re

def get_network_info_simple():
    print("=" * 50)
    print("لیست کارت‌های شبکه")
    print("=" * 50)
    print()
    
    # اجرای دستور ipconfig و دریافت خروجی
    try:
        result = subprocess.run(['ipconfig', '/all'], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ خطا در اجرای ipconfig")
            
    except Exception as e:
        print(f"❌ خطا: {e}")

def get_adapters_list():
    print("\n" + "=" * 50)
    print("لیست کارت‌های شبکه")
    print("=" * 50)
    
    try:
        # دریافت لیست کارت‌های شبکه
        result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ خطا در دریافت لیست کارت‌ها")
            
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    get_adapters_list()
    print("\n")
    get_network_info_simple()
    
    input("\nبرای خروج Enter بزنید...")