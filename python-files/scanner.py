# install_requirements.py
import os
import sys

def install_requirements():
    """Tự động cài đặt các thư viện cần thiết"""
    requirements = [
        'requests',
        'pandas',
        'numpy',
        'python-telegram-bot'
    ]
    
    for package in requirements:
        try:
            # Kiểm tra xem thư viện đã cài đặt chưa
            __import__(package.split('>=')[0])
            print(f"✓ {package} đã được cài đặt")
        except ImportError:
            print(f"Đang cài đặt {package}...")
            os.system(f'{sys.executable} -m pip install "{package}"')

if __name__ == "__main__":
    install_requirements()
    print("Cài đặt hoàn tất!")