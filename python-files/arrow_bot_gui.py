import cv2
import numpy as np
import pyautogui
import time
from mss import mss
import tkinter as tk
from tkinter import messagebox, filedialog

# -----------------
# Config defaults
# -----------------
region = None
threshold = 0.7
running = False
templates = {}
keymap = {"left":"left","down":"down","up":"up","right":"right"}

# -----------------
# Screen capture
# -----------------
def grab(region):
    with mss() as sct:
        img = np.array(sct.grab(region))[:, :, :3]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# -----------------
# Template matching
# -----------------
def find(frame, tpl, thr):
    res = cv2.matchTemplate(frame, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= thr:
        return True
    return False

# -----------------
# Bot loop
# -----------------
def bot_loop():
    global running
    while running:
        frame = grab(region)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        for name, tpl in templates.items():
            if tpl is None:
                continue
            if find(frame_bgr, tpl, threshold):
                pyautogui.press(keymap[name])
        time.sleep(0.01)

# -----------------
# GUI actions
# -----------------
def select_region():
    global region
    messagebox.showinfo("Select region","Move mouse to TOP-LEFT, press Enter; then BOTTOM-RIGHT, press Enter")
    input("Hover over TOP-LEFT of hit zone and press Enter in console...")
    x1, y1 = pyautogui.position()
    input("Hover over BOTTOM-RIGHT of hit zone and press Enter in console...")
    x2, y2 = pyautogui.position()
    region = {"left":x1,"top":y1,"width":x2-x1,"height":y2-y1}
    messagebox.showinfo("Region Set", f"Region: {region}")


def load_template(direction):
    global templates
    path = filedialog.askopenfilename(title=f"Select {direction} arrow image")
    if not path:
        return
    img = cv2.imread(path)
    templates[direction] = img
    messagebox.showinfo("Loaded", f"Loaded {direction} arrow template")


def start_bot():
    global running
    if region is None:
        messagebox.showerror("Error", "Set region first!")
        return
    if not templates:
        messagebox.showerror("Error", "Load arrow templates!")
        return
    running = True
    root.after(10, bot_loop)


def stop_bot():
    global running
    running = False
    messagebox.showinfo("Stopped", "Bot stopped")


def set_threshold(val):
    global threshold
    threshold = float(val)

# -----------------
# GUI Setup
# -----------------
root = tk.Tk()
root.title("Arrow Bot GUI")

frame_controls = tk.Frame(root)
frame_controls.pack(padx=10,pady=10)

btn_region = tk.Button(frame_controls,text="Select Region",command=select_region)
btn_region.grid(row=0,column=0,padx=5,pady=5)

btn_left = tk.Button(frame_controls,text="Load Left",command=lambda:load_template("left"))
btn_left.grid(row=1,column=0)
btn_down = tk.Button(frame_controls,text="Load Down",command=lambda:load_template("down"))
btn_down.grid(row=1,column=1)
btn_up = tk.Button(frame_controls,text="Load Up",command=lambda:load_template("up"))
btn_up.grid(row=1,column=2)
btn_right = tk.Button(frame_controls,text="Load Right",command=lambda:load_template("right"))
btn_right.grid(row=1,column=3)

btn_start = tk.Button(frame_controls,text="Start Bot",bg="green",fg="white",command=start_bot)
btn_start.grid(row=2,column=0,columnspan=2,sticky="ew",pady=5)

btn_stop = tk.Button(frame_controls,text="Stop Bot",bg="red",fg="white",command=stop_bot)
btn_stop.grid(row=2,column=2,columnspan=2,sticky="ew",pady=5)

scale_thr = tk.Scale(frame_controls,from_=0.4,to=0.95,resolution=0.01,orient=tk.HORIZONTAL,label="Sensitivity",command=set_threshold)
scale_thr.set(threshold)
scale_thr.grid(row=3,column=0,columnspan=4,pady=10,sticky="ew")

root.mainloop()
