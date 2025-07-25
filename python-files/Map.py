#! /usr/bin/env python3
import requests
import time
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO

def download_image(url):
    response = requests.get(url)
    img_data = BytesIO(response.content)
    return Image.open(img_data)

def update_image():
    global img
    img = download_image(image_url)
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk)
    label.image = img_tk
    root.after(600000, update_image)  # Update every 10 minutes

def close_app(event):
    root.quit()

image_url = "https://s.w-x.co/staticmaps/us_ne_9regradar_1280x720_usen.jpg"  # Replace with your image URL
root = tk.Tk()
root.title("Image Viewer")

img = download_image(image_url)
img_tk = ImageTk.PhotoImage(img)

label = tk.Label(root, image=img_tk)
label.pack()

root.bind("<Button-1>", close_app)  # Click to close
update_image()
root.mainloop()





