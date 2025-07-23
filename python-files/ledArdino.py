import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import serial
import time

# Create Tk root first
root = tk.Tk()
root.title(" PC LED Control ")
root.geometry("220x200")  # Remove or comment this

root.iconbitmap(""https://icons.iconarchive.com/icons/sirubico/black-metal/128/PC-a-icon.png")

# Setup serial connection to Arduino
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2)
except:
    arduino = None
    print("Failed to connect to Arduino")

# Load image from URL and convert for Tkinter
def load_image_from_url(url, size=(128, 128)):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    # Update to new recommended resample method (for Pillow >= 10)
    image = image.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)

# URLs
url_on = "https://icons.iconarchive.com/icons/hopstarter/sleek-xp-basic/128/Lamp-icon.png"
url_off = "https://static.vecteezy.com/system/resources/previews/005/972/791/original/light-off-icon-for-web-vector.jpg"

# Load images AFTER creating root window!
img_on = load_image_from_url(url_on)
img_off = load_image_from_url(url_off)

# LED control functions
def led_on():
    if arduino:
        arduino.write(b'1')
    led_label.config(image=img_on)
    led_label.image = img_on

def led_off():
    if arduino:
        arduino.write(b'0')
    led_label.config(image=img_off)
    led_label.image = img_off

# Label for LED icon (clickable)
led_label = tk.Label(root, image=img_off, cursor="hand2")
led_label.pack(pady=20)

# Click toggles between ON/OFF
is_on = [False]
def toggle_led(event):
    if is_on[0]:
        led_off()
    else:
        led_on()
    is_on[0] = not is_on[0]

led_label.bind("<Button-1>", toggle_led)

root.mainloop()
