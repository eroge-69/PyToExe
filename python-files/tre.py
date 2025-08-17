pip install rembg Pillow
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from PIL import Image
from rembg import remove

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        master.title("Portable Background Remover")
        master.geometry("600x500")
        master.resizable(False, False) # Make window not resizable

        self.input_files = []
        self.output_folder = ""

        # --- Input Section ---
        input_frame = tk.LabelFrame(master, text="1. Select Images", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        self.input_label = tk.Label(input_frame, text="No files selected.")
        self.input_label.pack(side="left", fill="x", expand=True)

        input_button = tk.Button(input_frame, text="Browse Files", command=self.select_input_files)
        input_button.pack(side="right", padx=5)

        # --- Output Section ---
        output_frame = tk.LabelFrame(master, text="2. Select Output Folder", padx=10, pady=10)
        output_frame.pack(pady=10, padx=10, fill="x")

        self.output_label = tk.Label(output_frame, text="No output folder selected.")
        self.output_label.pack(side="left", fill="x", expand=True)

        output_button = tk.Button(output_frame, text="Browse Folder", command=self.select_output_folder)
        output_button.pack(side="right", padx=5)

        # --- Process Button ---
        process_button = tk.Button(master, text="3. Process Images (Remove Background)", command=self.process_images,
                                   font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="raised")
        process_button.pack(pady=20, ipadx=20, ipady=10)

        # --- Log Section ---
        log_frame = tk.LabelFrame(master, text="Activity Log", padx=10, pady=10)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8, state='disabled', bg="#f0f0f0")
        self.log_text.pack(fill="both", expand=True)

        self.log_message("Welcome to the Portable Background Remover!")
        self.log_message("Select images, choose an output folder, then click 'Process'.")

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll to the end
        self.log_text.config(state='disabled')

    def select_input_files(self):
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Image Files", filetypes=filetypes)
        if files:
            self.input_files = list(files)
            self.input_label.config(text=f"{len(self.input_files)} file(s) selected.")
            self.log_message(f"Selected {len(self.input_files)} image(s).")
        else:
            self.input_files = []
            self.input_label.config(text="No files selected.")
            self.log_message("No image files selected.")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Output: {os.path.basename(folder)}")
            self.log_message(f"Output folder set to: {folder}")
        else:
            self.output_folder = ""
            self.output_label.config(text="No output folder selected.")
            self.log_message("No output folder selected.")

    def process_images(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select image files first.")
            self.log_message("Error: No input files selected.")
            return

        if not self.output_folder:
            messagebox.showwarning("Warning", "Please select an output folder first.")
            self.log_message("Error: No output folder selected.")
            return

        self.log_message("\n--- Starting background removal ---")
        processed_count = 0
        failed_count = 0

        for i, input_path in enumerate(self.input_files):
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_no_bg.png" # Always save as PNG for transparency
            output_path = os.path.join(self.output_folder, output_filename)

            self.log_message(f"Processing ({i+1}/{len(self.input_files)}): {filename}")

            try:
                # Open image using Pillow
                img = Image.open(input_path)

                # Convert to RGBA if not already (important for transparency)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Remove background
                output_img = remove(img)

                # Save the processed image
                output_img.save(output_path)
                self.log_message(f"  Saved: {output_filename}")
                processed_count += 1

            except Exception as e:
                self.log_message(f"  Failed to process {filename}: {e}")
                failed_count += 1

        self.log_message("\n--- Processing Complete ---")
        self.log_message(f"Successfully processed: {processed_count} image(s).")
        if failed_count > 0:
            self.log_message(f"Failed to process: {failed_count} image(s). Check log for details.")
            messagebox.showerror("Processing Complete",
                                 f"Finished processing. {processed_count} images processed, {failed_count} failed. See log for details.")
        else:
            messagebox.showinfo("Processing Complete",
                                 f"All {processed_count} images processed successfully!")

def main():
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
