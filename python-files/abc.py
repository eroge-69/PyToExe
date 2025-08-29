import os
import io
import time
import threading

import google.generativeai as genai


from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController
from PIL import Image
import mss  # cross-platform screenshot
import pyperclip
import tkinter as tk

# -------------------- CONFIG --------------------
API_KEY = os.environ.get("GENAI_API_KEY", "AIzaSyDdW6sn_Jag4IdCxY6tJLneCQKRjqqBlPA")
genai.configure(api_key=API_KEY)

keyboard_controller = KeyboardController()

# -------------------- OVERLAY --------------------
def _show_overlay_thread(text: str, duration: float = 3.0):
    try:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.3)

        label = tk.Label(root, text=text, font=("Arial", 11), fg="black", bd=2, relief="solid")
        label.pack(ipadx=8, ipady=4)

        root.update_idletasks()
        w = root.winfo_width()
        h = root.winfo_height()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        margin_x = 20
        margin_y = 40
        x = screen_width - w - margin_x
        y = screen_height - h - margin_y
        root.geometry(f"+{x}+{y}")

        root.after(int(duration * 1000), root.destroy)
        root.mainloop()
    except Exception as e:
        print("Overlay error (fallback to console):", e)
        print(f"Overlay Text: {text}")

def show_overlay(text: str, duration: float = 3.0):
    threading.Thread(target=_show_overlay_thread, args=(text, duration), daemon=True).start()

# -------------------- FUNCTIONS --------------------
def paste_at_cursor(text: str):
    pyperclip.copy(text)
    keyboard_controller.press(keyboard.Key.ctrl)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(keyboard.Key.ctrl)

def take_screenshot():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

def ask_gemini(filename):
    img = Image.open(filename)

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = """Give me a one-word answer without any explanations.
        If the answer is small just tell the answer instead of the option.
        If it is a programming LeetCode-type question give the full code in C.
        If the answer consists of multiple words, provide the most suitable option letter a, b, c, d or closest alternative.
        If it is a fill-in-the-blank question I want you to give me the one word answer itself.
        If there are multiple answers, give only the options (a, b, c, d), not full answers.
    """
    response = model.generate_content([prompt, img])
    answer = response.text.strip()
    print("Gemini returned:", answer)

    if len(answer) > 1000:
        paste_at_cursor(answer)
    else:
        show_overlay(answer, duration=5.0)
        if answer.lower() == 'a':
            os.system("date 01-1-2001")
        elif answer.lower() == 'b':
            os.system("date 02-1-2001")
        elif answer.lower() == 'c':
            os.system("date 03-1-2001")
        elif answer.lower() == 'd':
            os.system("date 04-1-2001")

    return answer

def process():
    print("Taking screenshot...")
    img_bytes = take_screenshot()

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    img = Image.open(img_bytes)
    img.save(filename)
    print(f"Screenshot saved as {filename}")

    print("Asking Gemini...")
    answer = ask_gemini(filename)
    print("Gemini Answer:", answer)

# -------------------- HOTKEY --------------------
def on_activate():
    print("Shortcut pressed!")
    threading.Thread(target=process, daemon=True).start()

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<ctrl>+<shift>+q'),
    on_activate
)

with keyboard.Listener(
    on_press=for_canonical(hotkey.press),
    on_release=for_canonical(hotkey.release)
) as l:
    print("Listening for Ctrl+Shift+q ...")
    l.join()
