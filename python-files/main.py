import os
import sys

def immediate_shutdown():
    if sys.platform == "win32":
        os.system("shutdown /s /f /t 0")
    elif sys.platform == "linux" or sys.platform == "linux2":
        os.system("sudo shutdown now")
    elif sys.platform == "darwin":
        os.system("sudo shutdown -h now")
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    immediate_shutdown()