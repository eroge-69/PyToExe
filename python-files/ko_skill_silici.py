import pyautogui
import keyboard
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import time
import threading

skill_image = None
skill_box = None

def capture_skill_image():
    global skill_image, skill_box

    messagebox.showinfo("Simge Seçimi", "Skill simgesini seçmek için mouse ile bir alan çizin. (3 saniye içinde)")
    time.sleep(3)
    skill_box = pyautogui.selectRegion("Skill simgesini seç")
    if skill_box is None:
        messagebox.showerror("Hata", "Herhangi bir bölge seçilmedi.")
        return

    screenshot = ImageGrab.grab(bbox=skill_box)
    skill_image = screenshot
    screenshot.save("skill_icon.png")
    messagebox.showinfo("Başarılı", "Skill simgesi kaydedildi. Artık 'F8' tuşuyla çalıştırabilirsin.")

def find_and_double_click():
    global skill_image

    if skill_image is None:
        return

    screenshot = pyautogui.screenshot()
    location = pyautogui.locateCenterOnScreen("skill_icon.png", confidence=0.8)
    if location:
        pyautogui.moveTo(location.x, location.y, duration=0.2)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.click()
    else:
        print("Skill simgesi bulunamadı.")

def listen_key():
    keyboard.add_hotkey("f8", find_and_double_click)
    keyboard.wait("esc")  # ESC ile çıkış

def run_gui():
    root = tk.Tk()
    root.title("KO Skill Silici")
    root.geometry("300x150")
    root.resizable(False, False)

    label = tk.Label(root, text="🎮 Knight Online Skill Silici", font=("Helvetica", 14))
    label.pack(pady=10)

    select_button = tk.Button(root, text="Skill Simgesini Seç", command=capture_skill_image)
    select_button.pack(pady=10)

    info = tk.Label(root, text="F8 ile çift tıkla sil\nESC ile çık", font=("Helvetica", 10))
    info.pack()

    threading.Thread(target=listen_key, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    run_gui()
