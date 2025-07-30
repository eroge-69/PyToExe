import os
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, UnidentifiedImageError
import customtkinter as ctk
from tkinter import filedialog, messagebox
import queue

MAX_WORKERS = 4
JPEG_DEFAULT_QUALITY = 85

def optimize_image(full_path, quality=JPEG_DEFAULT_QUALITY):
    """
    Optimize JPEG and PNG images with universal quality parameter.
    quality: 0-100 for JPEG, mapped to compress_level 0-9 for PNG.
    """
    allowed_formats = ('JPEG', 'PNG')
    try:
        original_size = os.path.getsize(full_path)
        with Image.open(full_path) as img:
            if img.format not in allowed_formats:
                return None

            if img.format == 'JPEG':
                img.save(full_path, 'JPEG', quality=quality, optimize=True)
            elif img.format == 'PNG':
                if img.mode not in ('P', 'L'):
                    img = img.convert('P', palette=Image.ADAPTIVE)
                compress_level = max(0, min(9, 9 - int((quality / 100) * 9)))
                img.save(full_path, 'PNG', optimize=True, compress_level=compress_level)

        optimized_size = os.path.getsize(full_path)
        saved = original_size - optimized_size
        return (full_path, saved if saved > 0 else 0)
    except (UnidentifiedImageError, OSError) as e:
        return (full_path, -1, str(e))

def optimize_images_in_list(file_paths, quality=JPEG_DEFAULT_QUALITY, progress_callback=None):
    total_saved = 0
    optimized_count = 0
    errors = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(optimize_image, f, quality): f for f in file_paths}
        total = len(futures)
        done = 0

        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                errors.append(("Unknown file", str(e)))
                continue

            done += 1
            if progress_callback:
                progress_callback(done, total)

            if result is None:
                continue

            if len(result) == 3 and result[1] == -1:
                errors.append((result[0], result[2]))
            else:
                path, saved_bytes = result
                if saved_bytes > 0:
                    optimized_count += 1
                    total_saved += saved_bytes

    return optimized_count, total_saved, errors

def get_images_by_folder(folder):
    allowed_ext = ('.jpg', '.jpeg', '.png')
    images = []
    for subdir, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(allowed_ext):
                images.append(os.path.join(subdir, file))
    return images

def get_images_larger_than(folder, size_mb):
    size_bytes = size_mb * 1024 * 1024
    images = []
    for subdir, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(subdir, file)
                try:
                    if os.path.getsize(full_path) > size_bytes:
                        images.append(full_path)
                except Exception:
                    pass
    return images

def get_images_with_sizes(folder):
    images_info = []
    for subdir, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(subdir, file)
                try:
                    size = os.path.getsize(full_path)
                    images_info.append((file, os.path.splitext(file)[1].lower(), size, full_path))
                except Exception:
                    pass
    images_info.sort(key=lambda x: x[2], reverse=True)
    return images_info

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WordPress Image Optimizer")
        self.geometry("820x580")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.log_queue = queue.Queue()

        self.create_main_menu()
        self.after(100, self.process_log_queue)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()
        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(padx=40, pady=40, fill="both", expand=True)

        label = ctk.CTkLabel(frm, text="Choose an option:", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=(10, 30))

        btn_all = ctk.CTkButton(frm, text="Optimize ALL images in folder", width=300, command=self.optimize_all_ui)
        btn_all.pack(pady=12)

        btn_larger = ctk.CTkButton(frm, text="Optimize images LARGER THAN size (MB)", width=300, command=self.optimize_larger_ui)
        btn_larger.pack(pady=12)

        btn_search = ctk.CTkButton(frm, text="Search image sizes in folder (list only)", width=300, command=self.search_sizes_ui)
        btn_search.pack(pady=12)

    def optimize_all_ui(self):
        self.clear_frame()
        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frm, text="Select folder to optimize ALL images:", font=ctk.CTkFont(size=14)).pack(anchor="w")

        self.entry_folder = ctk.CTkEntry(frm, width=600)
        self.entry_folder.pack(pady=8, anchor="w")

        ctk.CTkButton(frm, text="Browse Folder", command=self.browse_folder).pack(pady=(0,10), anchor="w")

        quality_frame = ctk.CTkFrame(frm)
        quality_frame.pack(anchor="w", pady=(10,0))

        ctk.CTkLabel(quality_frame, text="Image Quality (0-100):", font=ctk.CTkFont(size=14)).pack(side="left")

        self.quality_slider = ctk.CTkSlider(quality_frame, from_=10, to=100, number_of_steps=90, width=200)
        self.quality_slider.set(JPEG_DEFAULT_QUALITY)
        self.quality_slider.pack(side="left", padx=(10,5))

        self.label_quality_value = ctk.CTkLabel(quality_frame, text=str(JPEG_DEFAULT_QUALITY), width=30)
        self.label_quality_value.pack(side="left")

        self.quality_slider.configure(command=self.update_quality_label)

        ctk.CTkButton(frm, text="Start Optimization", command=self.start_optimize_all).pack(pady=(10, 10), anchor="w")

        ctk.CTkButton(frm, text="Back to Menu", command=self.create_main_menu).pack(pady=(0, 20), anchor="w")

        self.txt_log = ctk.CTkTextbox(frm, width=760, height=250, corner_radius=8, state="disabled")
        self.txt_log.pack(pady=10, anchor="w")

        self.progress_bar = ctk.CTkProgressBar(frm, width=760)
        self.progress_bar.pack(pady=(5, 0), anchor="w")
        self.progress_bar.set(0)

    def update_quality_label(self, value):
        self.label_quality_value.configure(text=str(int(float(value))))

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder_selected)

    def start_optimize_all(self):
        folder = self.entry_folder.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        quality = int(self.quality_slider.get())

        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

        self.log(f"Scanning images...")
        images = get_images_by_folder(folder)
        if not images:
            messagebox.showinfo("Info", "No images found in the folder.")
            return

        self.log(f"Found {len(images)} images. Starting optimization with quality {quality}...")
        self.progress_bar.set(0)

        self.set_ui_state_all(False)

        threading.Thread(target=self.run_optimize_images, args=(images, quality), daemon=True).start()

    def run_optimize_images(self, images, quality):
        def progress_callback(done, total):
            self.progress_bar.set(done / total)

        try:
            optimized_count, total_saved, errors = optimize_images_in_list(images, quality=quality, progress_callback=progress_callback)

            self.log("\nOptimization completed!")
            self.log(f"Images optimized: {optimized_count}")
            self.log(f"Total space saved: {total_saved / (1024*1024):.2f} MB")
            if errors:
                self.log(f"Errors on {len(errors)} files:")
                for path, err in errors:
                    self.log(f"{path}: {err}")

        except Exception as e:
            self.log(f"An unexpected error occurred: {str(e)}")

        finally:
            self.set_ui_state_all(True)

    def set_ui_state_all(self, enabled):
        state = "normal" if enabled else "disabled"
        self.entry_folder.configure(state=state)
        self.quality_slider.configure(state=state)
        for btn in self.winfo_children():
            if isinstance(btn, ctk.CTkButton):
                btn.configure(state=state)
        self.progress_bar.set(0 if enabled else self.progress_bar.get())

    def log(self, message):
        self.log_queue.put(message)

    def process_log_queue(self):
        updated = False
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            try:
                if hasattr(self, 'txt_log') and self.txt_log.winfo_exists():
                    self.txt_log.configure(state="normal")
                    self.txt_log.insert("end", msg + "\n")
                    self.txt_log.see("end")
                    self.txt_log.configure(state="disabled")
                    updated = True
            except Exception:
                pass
        if updated:
            self.update_idletasks()
        self.after(100, self.process_log_queue)

    def optimize_larger_ui(self):
        self.clear_frame()
        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frm, text="Select folder:", font=ctk.CTkFont(size=14)).pack(anchor="w")

        self.entry_folder2 = ctk.CTkEntry(frm, width=600)
        self.entry_folder2.pack(pady=8, anchor="w")

        ctk.CTkButton(frm, text="Browse Folder", command=self.browse_folder2).pack(pady=(0,10), anchor="w")

        ctk.CTkLabel(frm, text="Enter minimum image size in MB:", font=ctk.CTkFont(size=14)).pack(anchor="w")
        self.entry_min_size = ctk.CTkEntry(frm, width=100)
        self.entry_min_size.pack(pady=8, anchor="w")

        quality_frame2 = ctk.CTkFrame(frm)
        quality_frame2.pack(anchor="w", pady=(10,0))

        ctk.CTkLabel(quality_frame2, text="Image Quality (0-100):", font=ctk.CTkFont(size=14)).pack(side="left")

        self.quality_slider2 = ctk.CTkSlider(quality_frame2, from_=10, to=100, number_of_steps=90, width=200)
        self.quality_slider2.set(JPEG_DEFAULT_QUALITY)
        self.quality_slider2.pack(side="left", padx=(10,5))

        self.label_quality_value2 = ctk.CTkLabel(quality_frame2, text=str(JPEG_DEFAULT_QUALITY), width=30)
        self.label_quality_value2.pack(side="left")

        self.quality_slider2.configure(command=self.update_quality_label2)

        ctk.CTkButton(frm, text="Start Optimization", command=self.start_optimize_larger).pack(pady=(10, 10), anchor="w")

        ctk.CTkButton(frm, text="Back to Menu", command=self.create_main_menu).pack(pady=(0, 20), anchor="w")

        self.txt_log2 = ctk.CTkTextbox(frm, width=760, height=250, corner_radius=8, state="disabled")
        self.txt_log2.pack(pady=10, anchor="w")

        self.progress_bar2 = ctk.CTkProgressBar(frm, width=760)
        self.progress_bar2.pack(pady=(5, 0), anchor="w")
        self.progress_bar2.set(0)

    def update_quality_label2(self, value):
        self.label_quality_value2.configure(text=str(int(float(value))))

    def browse_folder2(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.entry_folder2.delete(0, "end")
            self.entry_folder2.insert(0, folder_selected)

    def start_optimize_larger(self):
        folder = self.entry_folder2.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        try:
            min_size = float(self.entry_min_size.get())
            if min_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for size.")
            return

        quality = int(self.quality_slider2.get())

        self.txt_log2.configure(state="normal")
        self.txt_log2.delete("1.0", "end")
        self.txt_log2.configure(state="disabled")

        self.log2(f"Scanning images larger than {min_size} MB...")
        images = get_images_larger_than(folder, min_size)
        if not images:
            messagebox.showinfo("Info", f"No images larger than {min_size} MB found.")
            return

        self.log2(f"Found {len(images)} images. Starting optimization with quality {quality}...")
        self.progress_bar2.set(0)

        self.set_ui_state_larger(False)

        threading.Thread(target=self.run_optimize_images_larger, args=(images, quality), daemon=True).start()

    def run_optimize_images_larger(self, images, quality):
        def progress_callback(done, total):
            self.progress_bar2.set(done / total)

        try:
            optimized_count, total_saved, errors = optimize_images_in_list(images, quality=quality, progress_callback=progress_callback)

            self.log2("\nOptimization completed!")
            self.log2(f"Images optimized: {optimized_count}")
            self.log2(f"Total space saved: {total_saved / (1024*1024):.2f} MB")
            if errors:
                self.log2(f"Errors on {len(errors)} files:")
                for path, err in errors:
                    self.log2(f"{path}: {err}")

        except Exception as e:
            self.log2(f"An unexpected error occurred: {str(e)}")

        finally:
            self.set_ui_state_larger(True)

    def set_ui_state_larger(self, enabled):
        state = "normal" if enabled else "disabled"
        self.entry_folder2.configure(state=state)
        self.entry_min_size.configure(state=state)
        self.quality_slider2.configure(state=state)
        for btn in self.winfo_children():
            if isinstance(btn, ctk.CTkButton):
                btn.configure(state=state)
        self.progress_bar2.set(0 if enabled else self.progress_bar2.get())

    def log2(self, message):
        # Log messages for larger UI - put to the same queue, but show in txt_log2 as well
        self.log_queue.put(message)
        if hasattr(self, 'txt_log2') and self.txt_log2.winfo_exists():
            try:
                self.txt_log2.configure(state="normal")
                self.txt_log2.insert("end", message + "\n")
                self.txt_log2.see("end")
                self.txt_log2.configure(state="disabled")
            except Exception:
                pass

    def search_sizes_ui(self):
        self.clear_frame()
        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frm, text="Select folder to search image sizes:", font=ctk.CTkFont(size=14)).pack(anchor="w")

        self.entry_folder3 = ctk.CTkEntry(frm, width=600)
        self.entry_folder3.pack(pady=8, anchor="w")

        ctk.CTkButton(frm, text="Browse Folder", command=self.browse_folder3).pack(pady=(0,10), anchor="w")

        amount_frame = ctk.CTkFrame(frm)
        amount_frame.pack(pady=(0, 10), anchor="w")

        ctk.CTkLabel(amount_frame, text="Amount:", font=ctk.CTkFont(size=14)).pack(side="left")
        self.entry_amount = ctk.CTkEntry(amount_frame, width=80)
        self.entry_amount.insert(0, "10")
        self.entry_amount.pack(side="left", padx=(10,0))

        ctk.CTkButton(frm, text="Search", command=self.load_image_sizes).pack(pady=(0, 10), anchor="w")

        ctk.CTkButton(frm, text="Back to Menu", command=self.create_main_menu).pack(pady=(0, 20), anchor="w")

        self.tree_sizes = ctk.CTkScrollableFrame(frm, width=760, height=350, corner_radius=8)
        self.tree_sizes.pack(pady=10, anchor="w")

    def browse_folder3(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.entry_folder3.delete(0, "end")
            self.entry_folder3.insert(0, folder_selected)

    def load_image_sizes(self):
        folder = self.entry_folder3.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        try:
            amount = int(self.entry_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer for amount.")
            return

        for widget in self.tree_sizes.winfo_children():
            widget.destroy()

        images_info = get_images_with_sizes(folder)
        if not images_info:
            messagebox.showinfo("Info", "No images found in the folder.")
            return

        images_info = images_info[:amount]

        header_frame = ctk.CTkFrame(self.tree_sizes)
        header_frame.pack(fill="x")

        ctk.CTkLabel(header_frame, text="Filename", width=400, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(header_frame, text="Format", width=100, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(header_frame, text="Size (MB)", width=150, anchor="e", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)

        for _, (file, ext, size, _) in enumerate(images_info):
            size_mb = size / (1024 * 1024)
            row_frame = ctk.CTkFrame(self.tree_sizes)
            row_frame.pack(fill="x", pady=1, padx=2)

            ctk.CTkLabel(row_frame, text=file, width=400, anchor="w").grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row_frame, text=ext, width=100, anchor="w").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row_frame, text=f"{size_mb:.2f}", width=150, anchor="e").grid(row=0, column=2, padx=5)

    def on_close(self):
        self.destroy()

if __name__ == "__main__":
    # pip install pillow customtkinter
    app = App()
    app.mainloop()
