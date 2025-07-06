
import time
import os
import subprocess
import sys

def main():
    print("Chào mừng đến với kỳ thi sát hạch A1")
    print("Xin nhập số báo danh và kiểm tra thông tin")
    
    # Chờ 3 giây
    time.sleep(3)
    
    # Đường dẫn phần mềm cần chạy
    exe_path = r"D:\thi\sathachhanga.exe"
    
    try:
        # Mở phần mềm kia
        subprocess.Popen(exe_path, shell=True)
    except Exception as e:
        print("Không thể mở phần mềm:", e)
    
    # Thoát sau khi mở phần mềm kia
    sys.exit()

if __name__ == "__main__":
    main()
