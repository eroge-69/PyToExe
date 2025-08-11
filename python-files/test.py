import tkinter as tk
import customtkinter as ctk
import random
import threading
import time
import sys
import winsound
import pyautogui
from pynput.mouse import Listener, Button
from ctypes import windll
from PIL import Image, ImageTk
import hashlib
import subprocess

# --- Variablen ---
running = False
alive = True
right_mouse_pressed = False
search_color = 5197761
click_delay = 0.25

user = windll.LoadLibrary('user32.dll')
dc = user.GetDC(0)
gdi = windll.LoadLibrary('gdi32.dll')

# --- HWID-Funktion (nur Windows 11 PowerShell) ---
def get_hwid():
    try:
        # PowerShell-Befehl für Windows 11 (und 10 geht meist auch)
        cmd = 'powershell "Get-WmiObject Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
        hwid = subprocess.check_output(cmd, shell=True).decode().strip()
        if hwid:
            return hwid
        else:
            return None
    except Exception as e:
        return None

# --- Lizenz generieren aus HWID + SECRET ---
SECRET = "GeheimesSchluessel123"  # Hier deinen geheimen Key ändern!

def generate_license_key(hwid):
    if not hwid:
        return None
    return hashlib.sha256((hwid + SECRET).encode()).hexdigest()

# --- Starfield Klasse ---
class Starfield:
    def __init__(self, canvas, width, height, num_stars=80):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.stars = [{'x': random.randint(0, width), 'y': random.randint(0, height), 'size': random.randint(1, 3), 'speed': random.uniform(0.5, 1.5)} for _ in range(num_stars)]
        self.animate()

    def animate(self):
        self.canvas.delete('star')
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)
            size = star['size']
            self.canvas.create_oval(star['x'], star['y'], star['x'] + size, star['y'] + size, fill='white', outline='', tags='star')
        self.canvas.after(30, self.animate)

# --- Lizenz-Check GUI ---
class LicenseWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lizenz prüfen")
        self.geometry("400x200")
        self.resizable(False, False)
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('dark-blue')

        self.label = ctk.CTkLabel(self, text="Bitte Lizenz eingeben:")
        self.label.pack(pady=(30,10))

        self.license_entry = ctk.CTkEntry(self, placeholder_text="Lizenz hier eingeben")
        self.license_entry.pack(pady=(0,10), padx=20, fill='x')

        self.verify_button = ctk.CTkButton(self, text="Verifizieren", command=self.verify_license)
        self.verify_button.pack(pady=(0,10))

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack()

    def verify_license(self):
        user_key = self.license_entry.get().strip()
        hwid = get_hwid()
        if hwid is None:
            self.message_label.configure(text="Fehler beim Auslesen der HWID!", text_color="red")
            return
        expected_key = generate_license_key(hwid)
        if user_key == expected_key:
            self.message_label.configure(text="Lizenz gültig!", text_color="green")
            # Nach 1 Sekunde Fenster schließen
            self.after(1000, self.destroy)
        else:
            self.message_label.configure(text="Key fehlgeschlagen!", text_color="red")

# --- Haupt-Anwendung ---
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app
        app = self
        self.title('Assmar00')
        self.geometry('500x480')
        self.resizable(False, False)

        canvas = tk.Canvas(self, bg='#1e1e1e', highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.starfield = Starfield(canvas, 500, 480)

        logo_path = 'logo.png'
        try:
            logo_image = Image.open(logo_path).resize((100, 100))
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self, image=logo_photo, bg='#1e1e1e')
            logo_label.image = logo_photo
            logo_label.place(relx=0.5, rely=0.05, anchor='n')
        except FileNotFoundError:
            print('Logo-Bild nicht gefunden:', logo_path)

        self.main_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.status_icon = ctk.CTkLabel(self.main_frame, text='📶', text_color='red', font=('Arial', 30))
        self.status_icon.pack(pady=(40, 5))

        self.status_label = ctk.CTkLabel(self.main_frame, text='Inactive', text_color='red', font=('Arial', 16))
        self.status_label.pack(pady=(0, 30))

        self.delay_label = ctk.CTkLabel(self.main_frame, text='Verzögerung: 250 ms', font=('Arial', 14))
        self.delay_label.pack(pady=(0, 5))

        self.slider = ctk.CTkSlider(self.main_frame, from_=10, to=1000, command=self.update_slider_label, button_color='white')
        self.slider.set(250)
        self.slider.pack(pady=(0, 25))

        self.start_button = ctk.CTkButton(self.main_frame, text='Start', fg_color='red', command=self.toggle_clicker, width=150)
        self.start_button.pack(pady=(0, 10))

        self.kill_button = ctk.CTkButton(self.main_frame, text='Kill', fg_color='#555555', command=self.kill_script, width=150)
        self.kill_button.pack()

        self.made_by_label = ctk.CTkLabel(self, text='Made By Assmar00', text_color='white', font=('Consolas', 10))
        self.made_by_label.place(relx=1.0, y=5, anchor='ne')

        # Start Mouse Listener
        self.mouse_listener = Listener(on_click=self.on_click)
        self.mouse_listener.start()

        # Start Clicker-Thread
        threading.Thread(target=self.run_clicker, daemon=True).start()

        self.mainloop()

    def kill_script(self):
        global alive
        alive = False
        self.destroy()
        sys.exit()

    def get_pixel(self):
        x = user.GetSystemMetrics(0) // 2
        y = user.GetSystemMetrics(1) // 2
        return gdi.GetPixel(dc, x, y)

    def change_pixel_color(self):
        global search_color
        search_color = self.get_pixel()
        winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)

    def check(self):
        try:
            if self.get_pixel() == search_color:
                pyautogui.mouseDown()
                time.sleep(random.uniform(0.06, 0.2))
                pyautogui.mouseUp()
            return
        except pyautogui.FailSafeException:
            return None

    def on_click(self, x, y, button, pressed):
        global right_mouse_pressed
        if button == Button.right:
            right_mouse_pressed = pressed
        return None

    def run_clicker(self):
        global alive
        while alive:
            if running and right_mouse_pressed:
                self.check()
            time.sleep(click_delay)

    def toggle_clicker(self):
        global running
        running = not running
        self.status_label.configure(text='Active' if running else 'Inactive', text_color='green' if running else 'red')
        self.status_icon.configure(text_color='green' if running else 'red')
        self.start_button.configure(text='Stop' if running else 'Start', fg_color='green' if running else 'red')

    def update_slider_label(self, value):
        global click_delay
        click_delay = float(value) / 1000.0
        self.delay_label.configure(text=f'Verzögerung: {int(float(value))} ms')

if __name__ == "__main__":
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')

    login = LicenseWindow()
    login.mainloop()  # Starte Loginfenster und warte bis es geschlossen wird

    # Nach erfolgreichem Login wird MainApp gestartet
    MainApp()
