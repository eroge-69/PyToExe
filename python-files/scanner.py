import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import win32com.client
import os


class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Scanner and Cropper")

        self.original_image = None
        self.display_image = None
        self.photo = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.scale_factor = 1.0

        # GUI elements
        self.scan_button = tk.Button(root, text="Scan Photo", command=self.scan_photo)
        self.scan_button.pack(pady=10)

        self.crop_button = tk.Button(root, text="Crop and Save", command=self.crop_and_save, state=tk.DISABLED)
        self.crop_button.pack(pady=10)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="gray")
        self.canvas.pack()

        # Bind mouse events for cropping
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def scan_photo(self):
        try:
            wia = win32com.client.Dispatch("WIA.CommonDialog")
            image = wia.ShowAcquireImage()
            temp_file = os.path.join(os.getenv("TEMP"), "scanned_image.jpg")
            image.SaveFile(temp_file)
            self.original_image = Image.open(temp_file)

            # Resize for display (keep aspect ratio, max 800x600)
            width, height = self.original_image.size
            self.scale_factor = min(800 / width, 600 / height)
            display_width = int(width * self.scale_factor)
            display_height = int(height * self.scale_factor)
            self.display_image = self.original_image.resize((display_width, display_height), Image.LANCZOS)

            self.photo = ImageTk.PhotoImage(self.display_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.crop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Scan Complete", "Image scanned. Drag mouse to select crop area.")
        except Exception as e:
            messagebox.showerror("Error", f"Scanning failed: {str(e)}")

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red",
                                                 width=2)

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

    def crop_and_save(self):
        if self.original_image and self.start_x is not None and self.end_x is not None:
            left = int(min(self.start_x, self.end_x) / self.scale_factor)
            top = int(min(self.start_y, self.end_y) / self.scale_factor)
            right = int(max(self.start_x, self.end_x) / self.scale_factor)
            bottom = int(max(self.start_y, self.end_y) / self.scale_factor)

            cropped_image = self.original_image.crop((left, top, right, bottom))

            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
            if save_path:
                cropped_image.save(save_path)
                messagebox.showinfo("Save Complete", "Cropped image saved successfully.")
            self.start_x = self.start_y = self.end_x = self.end_y = None
            if self.rect:
                self.canvas.delete(self.rect)
        else:
            messagebox.showwarning("Warning", "No crop area selected.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()