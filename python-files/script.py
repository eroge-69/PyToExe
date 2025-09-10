import subprocess
import time
import socket
import re
import sys
import os

# تنظیم کدپیج به UTF-8 برای پشتیبانی از نمایش صحیح در CMD
os.system("chcp 65001")  # تنظیم کدپیج به UTF-8

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Check if internet connection is available using Google's DNS (8.8.8.8).
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def get_ping(host="8.8.8.8"):
    """
    Calculate ping to the specified host (default: 8.8.8.8).
    Returns average ping time in milliseconds or None if failed.
    """
    try:
        output = subprocess.run(
            ["ping", "-n", "4", host],
            capture_output=True,
            text=True,
            check=True
        )
        match = re.search(r"Average = (\d+)ms", output.stdout)
        if match:
            return int(match.group(1))
        return None
    except subprocess.CalledProcessError:
        return None

def reset_wifi():
    """
    Reset Wi-Fi interface using netsh commands in Windows.
    Assumes interface name is 'Wi-Fi'.
    """
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], check=True)
        time.sleep(5)
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], check=True)
        time.sleep(10)
        print("fiwi reset shod.")
    except subprocess.CalledProcessError as e:
        print(f"khata dar reset fiwi: {e}")

def main():
    """
    Main loop: Check internet, show ping if connected, reset Wi-Fi if disconnected.
    """
    while True:
        if not check_internet_connection():
            print("etesal internet ghat shode ast. reset fiwi...")
            reset_wifi()
            time.sleep(30)
        else:
            ping_time = get_ping()
            if ping_time is not None:
                print(f"etesal internet bargharar ast. ping: {ping_time} mili sanie")
            else:
                print("etesal internet bargharar ast, ama ping namovafagh bood.")
        time.sleep(5)

if __name__ == "__main__":
    print("barname shoru shod. baraye toghf, Ctrl+C feshar bedid.")
    main()