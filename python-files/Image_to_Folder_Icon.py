#!/usr/bin/env python3
"""
Image to Folder Icon - single-file Python GUI
- Pick an image file
- Convert it to a multi-size .ico
- Optionally delete the original
- Choose a target folder and apply the icon
"""

import os, sys, subprocess, tkinter as tk
from tkinter import filedialog
from PIL import Image

ICON_NAME = "folder_icon.ico"
DESKTOP_INI = "desktop.ini"

class App:
    def __init__(self, root):
        self.root = root
        root.title("Image to Folder Icon")
        root.geometry('520x300')
        root.resizable(False, False)

        self.image_path = tk.StringVar()
        self.folder_path = tk.StringVar()
        self.delete_original = tk.BooleanVar(value=False)

        frame = tk.Frame(root, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='1) Choose image to convert:').grid(row=0, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.image_path, width=58).grid(row=1, column=0, columnspan=2, sticky='w')
        tk.Button(frame, text='Browse...', command=self.pick_image).grid(row=1, column=2, padx=6)

        tk.Label(frame, text='2) Choose target folder:').grid(row=2, column=0, sticky='w', pady=(12,0))
        tk.Entry(frame, textvariable=self.folder_path, width=58).grid(row=3, column=0, columnspan=2, sticky='w')
        tk.Button(frame, text='Browse...', command=self.pick_folder).grid(row=3, column=2, padx=6)

        tk.Checkbutton(frame, text='Delete original image after conversion', variable=self.delete_original).grid(row=4, column=0, columnspan=3, sticky='w', pady=(10,0))

        tk.Button(frame, text='Convert & Apply Icon', command=self.convert_and_apply, width=25).grid(row=5, column=0, pady=14)
        tk.Button(frame, text='Exit', command=root.quit, width=10).grid(row=5, column=2, pady=14)

    def pick_image(self):
        p = filedialog.askopenfilename(title='Choose Image', filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff'), ('All files','*.*')])
        if p: self.image_path.set(p)

    def pick_folder(self):
        p = filedialog.askdirectory(title='Choose Folder')
        if p: self.folder_path.set(p)

    def convert_to_ico(self, src_path, dest_ico_path):
        img = Image.open(src_path).convert('RGBA')
        sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
        img.save(dest_ico_path, format='ICO', sizes=sizes)

    def write_desktop_ini(self, folder, ico_name):
        ini_path = os.path.join(folder, DESKTOP_INI)
        content = f"[.ShellClassInfo]\nIconResource={ico_name},0\n"
        with open(ini_path, 'w') as f:
            f.write(content)
        return ini_path

    def convert_and_apply(self):
        img = self.image_path.get().strip()
        folder = self.folder_path.get().strip()
        if not os.path.isfile(img) or not os.path.isdir(folder):
            return

        ico_path = os.path.join(folder, ICON_NAME)
        self.convert_to_ico(img, ico_path)

        if self.delete_original.get():
            try: os.remove(img)
            except: pass

        ini_path = self.write_desktop_ini(folder, ICON_NAME)

        try:
            subprocess.check_call(f'attrib +h +s +r \"{ini_path}\"', shell=True)
            subprocess.check_call(f'attrib +s \"{folder}\"', shell=True)
        except: pass

        tk.messagebox.showinfo("Done", "Icon applied successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
