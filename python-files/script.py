import subprocess
import time
import socket

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    چک می‌کند آیا اتصال اینترنت وجود دارد یا نه.
    از DNS گوگل (8.8.8.8) استفاده می‌کند تا چک کند.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def reset_wifi():
    """
    ریست کردن وای‌فای با استفاده از دستورات netsh در ویندوز.
    این فرض می‌کند که اینترفیس وای‌فای با نام 'Wi-Fi' است. اگر متفاوت است، تغییر دهید.
    """
    try:
        # غیرفعال کردن اینترفیس وای‌فای
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], check=True)
        time.sleep(5)  # صبر ۵ ثانیه برای غیرفعال شدن
        # فعال کردن دوباره اینترفیس وای‌فای
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], check=True)
        time.sleep(10)  # صبر ۱۰ ثانیه برای اتصال دوباره
        print("وای‌فای ریست شد.")
    except subprocess.CalledProcessError as e:
        print(f"خطا در ریست وای‌فای: {e}")

def main():
    """
    حلقه اصلی برنامه که به صورت بی‌نهایت اینترنت را چک می‌کند.
    اگر اتصال قطع شد، وای‌فای را ریست می‌کند و ۳۰ ثانیه صبر می‌کند.
    """
    while True:
        if not check_internet_connection():
            print("اتصال اینترنت قطع شده است. ریست وای‌فای...")
            reset_wifi()
            time.sleep(30)  # تاخیر ۳۰ ثانیه بعد از ریست
        else:
            print("اتصال اینترنت برقرار است.")
        time.sleep(10)  # چک هر ۱۰ ثانیه (می‌توانید تغییر دهید)

if __name__ == "__main__":
    print("برنامه شروع شد. برای توقف، Ctrl+C فشار دهید.")
    main()