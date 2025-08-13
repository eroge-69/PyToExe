import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import tensorflow as tf
from PIL import Image, ImageTk
import cv2

# This is the full, revised class. Replace the old one in your file.
class InferenceApp:
    def __init__(self, root):
        self.root = root
        # Changed window title
        self.root.title("Brain Hemorrhage Segmentation")
        self.root.geometry("800x600")

        # --- Variables ---
        self.model_path = tk.StringVar()
        self.image_path = tk.StringVar()
        self.model = None
        self.img_size = 256 # Must match the size used during training
        self.original_image = None
        self.processed_image_tk = None
        self.result_image_tk = None

        # --- UI Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Load Model (.h5)", command=self.load_model).pack(side=tk.LEFT, padx=5)
        self.model_label = ttk.Label(control_frame, text="No model loaded.", anchor="w")
        self.model_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(control_frame, text="Load CT Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        self.run_button = ttk.Button(control_frame, text="Run Segmentation", command=self.run_segmentation, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=5)

        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        image_frame.columnconfigure(0, weight=1)
        image_frame.columnconfigure(1, weight=1)
        image_frame.rowconfigure(1, weight=1)

        ttk.Label(image_frame, text="Original Image", font=("Helvetica", 12)).grid(row=0, column=0, pady=5)
        self.image_canvas = tk.Canvas(image_frame, bg="gray")
        self.image_canvas.grid(row=1, column=0, sticky="nsew", padx=5)

        ttk.Label(image_frame, text="Segmentation Result", font=("Helvetica", 12)).grid(row=0, column=1, pady=5)
        self.result_canvas = tk.Canvas(image_frame, bg="gray")
        self.result_canvas.grid(row=1, column=1, sticky="nsew", padx=5)

        self.status_label = ttk.Label(main_frame, text="Load a model and an image to begin.", font=("Helvetica", 10))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def load_model(self):
        path = filedialog.askopenfilename(filetypes=[("HDF5 files", "*.h5")])
        if not path: return
        try:
            # When you train your hemorrhage model, you can name it something like 'unet_hemorrhage_segmentation.h5'
            self.model = tf.keras.models.load_model(path, compile=False)
            self.model_path.set(path)
            self.model_label.config(text=f"Loaded: {os.path.basename(path)}")
            self.log("Model loaded successfully.")
            self.check_runnable()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {e}")
            self.log(f"Error loading model: {e}")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not path: return
        
        self.image_path.set(path)
        self.original_image = cv2.imread(path)
        
        self.display_image(self.original_image, self.image_canvas, "processed")
        self.log(f"Image loaded: {os.path.basename(path)}")
        self.result_canvas.delete("all")
        self.check_runnable()

    def run_segmentation(self):
        if not self.model or self.original_image is None:
            messagebox.showwarning("Warning", "Please load a model and an image first.")
            return

        self.log("Running segmentation...")

        img_resized = cv2.resize(self.original_image, (self.img_size, self.img_size))
        img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        img_norm = img_gray / 255.0
        img_input = np.expand_dims(img_norm, axis=0)
        img_input = np.expand_dims(img_input, axis=-1)

        pred_mask = self.model.predict(img_input)[0]
        
        # Changed comment for relevance
        # A low max value means the model thinks nothing is hemorrhagic.
        print(f"DEBUG: Maximum prediction value in mask is: {np.max(pred_mask)}")
        
        pred_mask_binary = (pred_mask > 0.5).astype(np.uint8) * 255
        
        # Renamed variable and updated log message
        hemorrhage_area = np.count_nonzero(pred_mask_binary)
        total_area = self.img_size * self.img_size
        percentage = (hemorrhage_area / total_area) * 100
        self.log(f"Segmentation complete. Hemorrhage area: {hemorrhage_area} pixels ({percentage:.2f}%).")

        mask_resized_to_original = cv2.resize(pred_mask_binary, 
                                              (self.original_image.shape[1], self.original_image.shape[0]),
                                              interpolation=cv2.INTER_NEAREST)

        result_image = self.original_image.copy()

        # The overlay remains red, as this is a common color for highlighting.
        red_overlay = np.zeros_like(result_image, dtype=np.uint8)
        red_overlay[mask_resized_to_original == 255] = [0, 0, 255] # BGR for Red
        result_image = cv2.addWeighted(result_image, 1.0, red_overlay, 0.6, 0)
        
        self.display_image(result_image, self.result_canvas, "result")

    def display_image(self, cv2_image, canvas, type_flag):
        img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 2 or canvas_height < 2:
            canvas_width, canvas_height = 380, 500

        img_pil.thumbnail((canvas_width - 10, canvas_height - 10), Image.Resampling.LANCZOS)
        
        if type_flag == "processed":
            self.processed_image_tk = ImageTk.PhotoImage(image=img_pil)
            canvas.create_image(canvas_width/2, canvas_height/2, anchor='center', image=self.processed_image_tk)
        else:
            self.result_image_tk = ImageTk.PhotoImage(image=img_pil)
            canvas.create_image(canvas_width/2, canvas_height/2, anchor='center', image=self.result_image_tk)

    def log(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def check_runnable(self):
        if self.model is not None and self.original_image is not None:
            self.run_button.config(state=tk.NORMAL)
            self.log("Model and image loaded. Ready to run segmentation.")
        else:
            self.run_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = InferenceApp(root)
    root.mainloop()