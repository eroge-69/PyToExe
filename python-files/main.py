import os
import shutil
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class PhotoSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Matcher")
        self.root.geometry("800x600")

        self.demo_photo = None
        self.original_photos = []
        self.original_folder = ""
        self.destination_folder = ""

        self.demo_label = Label(self.root, text="No demo photo selected")
        self.demo_label.pack()

        Button(self.root, text="Select Demo Photo", command=self.select_demo_photo).pack(pady=10)
        Button(self.root, text="Select Original Photo Folder", command=self.select_original_folder).pack(pady=10)
        Button(self.root, text="Select Destination Folder", command=self.select_destination_folder).pack(pady=10)

        self.photo_frame = Frame(self.root)
        self.photo_frame.pack(fill=BOTH, expand=True)

    def select_demo_photo(self):
        filepath = filedialog.askopenfilename(title="Select Demo Photo")
        if filepath:
            self.demo_photo = filepath
            self.demo_label.config(text=f"Demo: {os.path.basename(filepath)}")
            self.load_original_photos()

    def select_original_folder(self):
        folder = filedialog.askdirectory(title="Select Original Photo Folder")
        if folder:
            self.original_folder = folder
            self.load_original_photos()

    def select_destination_folder(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder = folder

    def load_original_photos(self):
        for widget in self.photo_frame.winfo_children():
            widget.destroy()

        if not self.original_folder:
            return

        files = [f for f in os.listdir(self.original_folder)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for file in files:
            filepath = os.path.join(self.original_folder, file)
            img = Image.open(filepath)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)

            btn = Button(self.photo_frame, image=photo,
                         command=lambda f=filepath: self.copy_to_destination(f))
            btn.image = photo
            btn.pack(side=LEFT, padx=5, pady=5)

    def copy_to_destination(self, selected_path):
        if not self.destination_folder:
            messagebox.showwarning("No Destination", "Please select a destination folder first.")
            return

        filename = os.path.basename(selected_path)
        dest_path = os.path.join(self.destination_folder, filename)
        shutil.copy2(selected_path, dest_path)
        messagebox.showinfo("Copied", f"{filename} copied to destination!")

if __name__ == "__main__":
    root = Tk()
    app = PhotoSelectorApp(root)
    root.mainloop()
