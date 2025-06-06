import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import datetime
import os

class ImageEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("Image Editor")

        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.noskeh_folder = os.path.join(self.desktop_path, "noskeh")
        os.makedirs(self.noskeh_folder, exist_ok=True)

        self.image_path = None
        self.image = None
        self.photo_image = None
        self.original_image = None
        self.rect_id = None
        self.rect_start_x = None
        self.rect_start_y = None
        self.last_draw = None

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.master, text="Open Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.canvas = tk.Canvas(self.master, width=200, height=200, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.start_drag_rectangle)
        self.canvas.bind("<B1-Motion>", self.drag_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag_rectangle)

        self.code_label = tk.Label(self.master, text="Code:")
        self.code_label.grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.code_entry = tk.Entry(self.master)
        self.code_entry.grid(row=2, column=1, padx=5, pady=2)
        self.code_active = tk.BooleanVar(value=True)
        self.code_check = tk.Checkbutton(self.master, text="Active", variable=self.code_active)
        self.code_check.grid(row=2, column=2, padx=5, pady=2)

        self.id_label = tk.Label(self.master, text="ID:")
        self.id_label.grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.id_entry = tk.Entry(self.master)
        self.id_entry.grid(row=3, column=1, padx=5, pady=2)
        self.id_active = tk.BooleanVar(value=True)
        self.id_check = tk.Checkbutton(self.master, text="Active", variable=self.id_active)
        self.id_check.grid(row=3, column=2, padx=5, pady=2)

        self.ward_label = tk.Label(self.master, text="Ward:")
        self.ward_label.grid(row=4, column=0, padx=5, pady=2, sticky="e")
        self.ward_entry = tk.Entry(self.master)
        self.ward_entry.grid(row=4, column=1, padx=5, pady=2)
        self.ward_active = tk.BooleanVar(value=True)
        self.ward_check = tk.Checkbutton(self.master, text="Active", variable=self.ward_active)
        self.ward_check.grid(row=4, column=2, padx=5, pady=2)

        self.font_size_label = tk.Label(self.master, text="Font Size:")
        self.font_size_label.grid(row=5, column=0, padx=5, pady=2, sticky="e")
        self.font_size_entry = tk.Entry(self.master)
        self.font_size_entry.grid(row=5, column=1, padx=5, pady=2)
        self.font_size_entry.insert(0, "20")

        self.rect_width_label = tk.Label(self.master, text="Rect Width:")
        self.rect_width_label.grid(row=6, column=0, padx=5, pady=2, sticky="e")
        self.rect_width_entry = tk.Entry(self.master)
        self.rect_width_entry.grid(row=6, column=1, padx=5, pady=2)
        self.rect_width_entry.insert(0, "50")

        self.rect_height_label = tk.Label(self.master, text="Rect Height:")
        self.rect_height_label.grid(row=7, column=0, padx=5, pady=2, sticky="e")
        self.rect_height_entry = tk.Entry(self.master)
        self.rect_height_entry.grid(row=7, column=1, padx=5, pady=2)
        self.rect_height_entry.insert(0, "30")

        self.paste_button = tk.Button(self.master, text="Paste Text", command=self.paste_text)
        self.paste_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5)

        self.preview_button = tk.Button(self.master, text="Preview", command=self.show_preview)
        self.preview_button.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

        self.save_button = tk.Button(self.master, text="Save Image", command=self.save_image)
        self.save_button.grid(row=10, column=0, columnspan=3, padx=5, pady=5)

        self.draw_rect_button = tk.Button(self.master, text="Draw Rectangle", command=self.draw_rectangle)
        self.draw_rect_button.grid(row=6, column=2, padx=5, pady=5)

        self.clear_rect_button = tk.Button(self.master, text="Clear Rectangle", command=self.clear_rectangle)
        self.clear_rect_button.grid(row=7, column=2, padx=5, pady=5)

        self.status_label = tk.Label(self.master, text="", fg="pink")
        self.status_label.grid(row=11, column=0, columnspan=4, padx=5, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.tiff;*.bmp")]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                self.original_image = self.image.copy()
                self.last_draw = self.image.copy()
                self.display_image()
                self.status_label.config(text="Image loaded successfully.", fg="pink")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")
                self.status_label.config(text=f"Error loading image: {e}", fg="pink")

    def display_image(self):
        if self.image:
            resized_image = self.image.copy()
            resized_image.thumbnail((200, 200))
            self.photo_image = ImageTk.PhotoImage(resized_image)
            self.canvas.config(width=self.photo_image.width(), height=self.photo_image.height())
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def paste_text(self):
        if not self.image:
            messagebox.showinfo("Info", "Please load an image first.")
            return

        try:
            font_size = int(self.font_size_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid font size. Please enter a number.")
            return

        self.image = self.last_draw.copy() if self.last_draw else self.original_image.copy()
        draw = ImageDraw.Draw(self.image)
        
        try:
            font = ImageFont.truetype("arial.ttf", size=font_size)
        except IOError:
            font = ImageFont.load_default()

        text_color = "violet"
        y_offset = 20

        if self.code_active.get():
            text = f"Code: {self.code_entry.get()}"
            draw.text((10, y_offset), text, fill=text_color, font=font)
            y_offset += font_size + 5

        if self.id_active.get():
            text = f"ID: {self.id_entry.get()}"
            draw.text((10, y_offset), text, fill=text_color, font=font)
            y_offset += font_size + 5

        if self.ward_active.get():
            text = f"Ward: {self.ward_entry.get()}"
            draw.text((10, y_offset), text, fill=text_color, font=font)
            y_offset += font_size + 5

        today = datetime.date.today()
        date_string = today.strftime("%Y-%m-%d")
        draw.text((10, y_offset), f"Date: {date_string}", fill=text_color, font=font)

        self.last_draw = self.image.copy()
        self.display_image()
        self.status_label.config(text="Text pasted.", fg="pink")

    def save_image(self):
        if not self.image:
            messagebox.showinfo("Info", "Please load an image first.")
            return

        today = datetime.date.today()
        date_string = today.strftime("%Y-%m-%d")
        date_folder = os.path.join(self.noskeh_folder, date_string)
        os.makedirs(date_folder, exist_ok=True)
        
        existing_files = [f for f in os.listdir(date_folder) if f.startswith(date_string)]
        max_num = 0
        for file in existing_files:
            try:
                num = int(file.split('-')[-1].split('.')[0])
                if num > max_num:
                    max_num = num
            except:
                continue
        
        new_num = max_num + 1
        filename = f"{date_string}-{new_num}.png"
        file_path = os.path.join(date_folder, filename)

        try:
            self.image.save(file_path)
            self.status_label.config(text=f"Image saved to {file_path}", fg="pink")
            messagebox.showinfo("Success", f"Image saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {e}")
            self.status_label.config(text=f"Error saving image: {e}", fg="pink")

    def show_preview(self):
        if not self.image:
            messagebox.showinfo("Info", "Please load an image first.")
            return

        preview_window = tk.Toplevel(self.master)
        preview_window.title("Preview")
        preview_image = self.image.copy()
        preview_image.thumbnail((600, 600))
        photo = ImageTk.PhotoImage(preview_image)
        label = tk.Label(preview_window, image=photo)
        label.image = photo
        label.pack()

    def draw_rectangle(self):
        if not self.image:
            messagebox.showinfo("Info", "Please load an image first.")
            return

        self.clear_rectangle()
        try:
            width = int(self.rect_width_entry.get())
            height = int(self.rect_height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid width or height. Please enter numbers.")
            return

        x0 = 10
        y0 = 10
        x1 = x0 + width
        y1 = y0 + height

        self.rect_start_x = x0
        self.rect_start_y = y0

        draw = ImageDraw.Draw(self.image)
        draw.rectangle((x0, y0, x1, y1), fill="green")
        self.last_draw = self.image.copy()
        self.display_image()

    def clear_rectangle(self):
        if not self.image or not self.original_image:
            return
        self.image = self.original_image.copy()
        self.display_image()

    def start_drag_rectangle(self, event):
        if not self.image:
            return
        try:
            width = int(self.rect_width_entry.get())
            height = int(self.rect_height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid width or height. Please enter numbers.")
            return
        self.rect_start_x = event.x
        self.rect_start_y = event.y

    def drag_rectangle(self, event):
        if not self.image:
            return
        try:
            width = int(self.rect_width_entry.get())
            height = int(self.rect_height_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid width or height. Please enter numbers.")
            return

        self.image = self.last_draw.copy() if self.last_draw else self.original_image.copy()
        draw = ImageDraw.Draw(self.image)
        x0 = event.x
        y0 = event.y
        x1 = x0 + width
        y1 = y0 + height
        draw.rectangle((x0, y0, x1, y1), fill="green")
        self.display_image()

    def stop_drag_rectangle(self, event):
        self.last_draw = self.image.copy()

root = tk.Tk()
app = ImageEditorApp(root)
root.mainloop()