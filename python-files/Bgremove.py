import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from rembg import remove
from PIL import Image, ImageTk
import os
import threading

# Global setting for the maximum size of the preview image
PREVIEW_FIXED_SIZE = (400, 400) # Guideline for canvas content sizing

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        master.title("Rembg Multi-Tool GUI")
        master.geometry("1000x750")
        master.minsize(800, 600)

        self.input_files = []
        self.output_dir = ""
        self.processed_images = {}
        self.tk_preview_image = None

        # --- Configure Grid Layout (Omitted for brevity, assume original layout) ---
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=0)
        
        main_content_frame = tk.Frame(master, bd=2, relief=tk.GROOVE)
        main_content_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.columnconfigure(1, weight=1)
        main_content_frame.rowconfigure(0, weight=1)
        
        left_panel = tk.Frame(main_content_frame, bd=1, relief=tk.SOLID)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_panel.rowconfigure(2, weight=1)

        file_selection_frame = tk.LabelFrame(left_panel, text="1. Select Images & Output Location")
        file_selection_frame.pack(padx=5, pady=5, fill="x", expand=False)

        self.select_button = tk.Button(file_selection_frame, text="➕ Select Input Images", command=self.select_images)
        self.select_button.pack(pady=5, padx=10, fill="x")

        self.output_button = tk.Button(file_selection_frame, text="📁 Choose Default Output Folder", command=self.select_output_folder)
        self.output_button.pack(pady=5, padx=10, fill="x")

        self.output_label = tk.Label(file_selection_frame, text="Default Output Folder: Not Selected", wraplength=300, anchor='w')
        self.output_label.pack(pady=5, padx=10, fill="x")

        list_display_frame = tk.LabelFrame(left_panel, text="Selected Images:")
        list_display_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.file_listbox = tk.Listbox(list_display_frame, selectmode=tk.SINGLE, font=('Arial', 10))
        self.file_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        self.scrollbar = tk.Scrollbar(list_display_frame, command=self.file_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        self.process_single_button = tk.Button(left_panel, text="🧪 Process Selected Image (Single)", command=self.start_single_processing_thread)
        self.process_single_button.pack(pady=5, padx=5, fill="x")

        self.clear_button = tk.Button(left_panel, text="🗑️ Clear Selected Images", command=self.clear_list)
        self.clear_button.pack(pady=5, padx=5, fill="x")

        right_panel = tk.Frame(main_content_frame, bd=1, relief=tk.SOLID)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_panel.rowconfigure(1, weight=1)

        self.image_info_label = tk.Label(right_panel, text="No image selected.", wraplength=450, font=('Arial', 10, 'bold'), anchor='center')
        self.image_info_label.pack(pady=(10,5), padx=10, fill="x")

        self.preview_canvas = tk.Canvas(right_panel, bg="lightgrey", relief=tk.SUNKEN, bd=2)
        self.preview_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.preview_canvas.bind("<Configure>", self.on_canvas_resize)

        self.preview_mode = tk.StringVar(value="Original")
        mode_frame = tk.Frame(right_panel)
        tk.Radiobutton(mode_frame, text="Original", variable=self.preview_mode, value="Original", command=self.update_preview_display).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Processed", variable=self.preview_mode, value="Processed", command=self.update_preview_display).pack(side=tk.LEFT, padx=5)
        mode_frame.pack(pady=5)
        
        save_btn_frame = tk.Frame(right_panel)
        save_btn_frame.pack(pady=10, padx=10, fill="x")
        save_btn_frame.columnconfigure(0, weight=1)
        
        self.save_individual_button = tk.Button(save_btn_frame, text="💾 Save Current Processed Image", command=self.save_individual_image, state=tk.DISABLED)
        self.save_individual_button.grid(row=0, column=0, sticky="ew")

        process_control_frame = tk.LabelFrame(master, text="2. Process Images (Background Removal)")
        process_control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        batch_frame = tk.Frame(process_control_frame)
        batch_frame.pack(pady=10, padx=10, fill="x")
        batch_frame.columnconfigure(0, weight=1)
        batch_frame.columnconfigure(1, weight=1)

        self.start_button = tk.Button(batch_frame, text="✨ Process ALL Images (Batch)", command=self.start_processing_thread)
        self.start_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.save_all_button = tk.Button(batch_frame, text="💾 Save ALL Processed Images", command=self.save_all_images, state=tk.DISABLED)
        self.save_all_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.progress_label = tk.Label(process_control_frame, text="Progress: Ready", anchor='w')
        self.progress_label.pack(pady=5, padx=10, fill="x")

        self.progress_bar = ttk.Progressbar(process_control_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill="x")

        self.update_ui_state(False)
    
    # --- Utility Methods ---

    def update_ui_state(self, is_processing):
        """Enables/Disables buttons based on processing state and data availability."""
        has_input = bool(self.input_files)
        has_processed_data = bool(self.processed_images)
        is_selected = bool(self.get_selected_file_path())
        
        general_state = tk.DISABLED if is_processing else tk.NORMAL
        
        self.select_button.config(state=general_state)
        self.output_button.config(state=general_state)
        self.clear_button.config(state=general_state)
        
        self.process_single_button.config(state=tk.DISABLED if is_processing or not is_selected else tk.NORMAL)

        self.start_button.config(state=tk.DISABLED if is_processing or not has_input else tk.NORMAL)
        
        self.save_all_button.config(state=tk.DISABLED if is_processing or not has_processed_data else tk.NORMAL)
        
        save_btn_state = tk.DISABLED
        selected_path = self.get_selected_file_path()
        if not is_processing and selected_path and selected_path in self.processed_images:
            save_btn_state = tk.NORMAL
        self.save_individual_button.config(state=save_btn_state)

    def get_selected_file_path(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            return self.input_files[index]
        return None

    def select_images(self):
        """Opens a file dialog to select multiple image files and adds them to the list."""
        filenames = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))
        )
        
        if filenames:
            newly_added = False
            for f in filenames:
                if f not in self.input_files:
                    self.input_files.append(f)
                    self.file_listbox.insert(tk.END, os.path.basename(f))
                    newly_added = True
            
            # This 'pass' is fine, as we don't clear old processed data just because a new file was added.
            if newly_added:
                pass 
                
        self.update_ui_state(False)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Default Output Folder")
        if folder_selected:
            self.output_dir = folder_selected
            self.output_label.config(text=f"Default Output Folder: {os.path.basename(self.output_dir)}")
        self.update_ui_state(False)

    def clear_list(self):
        self.input_files = []
        self.processed_images = {}
        self.file_listbox.delete(0, tk.END)
        self.progress_label.config(text="Progress: Ready")
        self.progress_bar['value'] = 0
        self.clear_preview()
        self.update_ui_state(False)
        
    def clear_preview(self):
        self.preview_canvas.delete("all")
        self.tk_preview_image = None
        self.image_info_label.config(text="No image selected.")
        self.update_ui_state(False)

    def on_listbox_select(self, event):
        selected_path = self.get_selected_file_path()
        if not selected_path:
            self.clear_preview()
            return

        self.image_info_label.config(text=f"File: {os.path.basename(selected_path)}")
        self.update_preview_display()
        self.update_ui_state(False)

    def on_canvas_resize(self, event):
        if self.tk_preview_image:
            self.update_preview_display()

    def update_preview_display(self):
        selected_path = self.get_selected_file_path()
        if not selected_path:
            self.clear_preview()
            return

        self.preview_canvas.delete("all")
        mode = self.preview_mode.get()
        image_to_display = None
        
        try:
            if mode == "Original":
                image_to_display = Image.open(selected_path)
            elif mode == "Processed" and selected_path in self.processed_images:
                image_to_display = self.processed_images[selected_path]
            
            if image_to_display:
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()

                if canvas_width == 0 or canvas_height == 0:
                    canvas_width, canvas_height = PREVIEW_FIXED_SIZE 

                img_width, img_height = image_to_display.size
                
                ratio = min(canvas_width / img_width, canvas_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)

                if new_width > img_width or new_height > img_height:
                    new_width = img_width
                    new_height = img_height

                resized_img = image_to_display.resize((new_width, new_height), Image.LANCZOS)
                self.tk_preview_image = ImageTk.PhotoImage(resized_img)
                
                x_center = (canvas_width - new_width) / 2
                y_center = (canvas_height - new_height) / 2
                
                self.preview_canvas.create_image(x_center, y_center, anchor=tk.NW, image=self.tk_preview_image)
            else:
                text = f"{mode} image not ready."
                if mode == "Processed":
                    text += "\n\nUse 'Process Selected Image' or 'Process ALL Images'."
                
                self.preview_canvas.create_text(
                    self.preview_canvas.winfo_width() / 2, 
                    self.preview_canvas.winfo_height() / 2, 
                    text=text, fill="gray", font=('Arial', 12, 'italic'), justify=tk.CENTER
                )

        except Exception as e:
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() / 2, 
                self.preview_canvas.winfo_height() / 2, 
                text=f"Error loading image: {e}", fill="red", font=('Arial', 12, 'bold')
            )
        self.update_ui_state(False)

    # --- CORRECTED SINGLE PROCESSING METHODS ---
    def start_single_processing_thread(self):
        selected_path = self.get_selected_file_path()
        if not selected_path:
            messagebox.showerror("Error", "Please select a single image file to process.")
            return
        
        # 1. Ensure Original view is shown before processing starts
        self.preview_mode.set("Original")
        self.update_preview_display() 
        
        # 2. Disable buttons and update progress bar
        self.update_ui_state(True)
        self.progress_label.config(text=f"Processing Single: {os.path.basename(selected_path)}... (Please wait)")
        self.progress_bar['maximum'] = 1
        self.progress_bar['value'] = 0

        # 3. Start processing in a new thread
        processing_thread = threading.Thread(target=self._process_single_image, args=(selected_path,))
        processing_thread.start()

    def _process_single_image(self, input_filepath):
        try:
            # 1. Process the image
            img = Image.open(input_filepath)
            output_image = remove(img)
            
            # 2. Store the result
            self.processed_images[input_filepath] = output_image
            
            # 3. Update UI on the main thread (after processing is complete)
            self.master.after(0, self.progress_bar.step, 1)
            self.master.after(0, self.preview_mode.set, "Processed")
            self.master.after(0, self.update_preview_display)
            self.master.after(0, self.progress_label.config, {'text': f"Progress: Finished single image."})
            self.master.after(0, messagebox.showinfo, "Finished", "Single image processing complete.")
            
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Processing Error", 
                              f"Could not process {os.path.basename(input_filepath)}: {e}")
            self.master.after(0, self.progress_label.config, {'text': f"Progress: Error in single process."})
            
        finally:
            self.master.after(0, self.update_ui_state, False)

    # --- Rest of the Batch and Save Methods (Unchanged) ---
    def start_processing_thread(self):
        if not self.input_files:
            messagebox.showerror("Error", "Please select image files first.")
            return

        self.processed_images = {}
        self.preview_mode.set("Processed")

        self.update_ui_state(True)
        self.progress_label.config(text="Progress: Initializing Batch...")
        self.progress_bar['value'] = 0
        
        processing_thread = threading.Thread(target=self._process_images_batch)
        processing_thread.start()

    def _process_images_batch(self):
        total_images = len(self.input_files)
        successful_count = 0
        self.progress_bar['maximum'] = total_images

        for i, input_filepath in enumerate(self.input_files):
            try:
                self.master.after(0, self.progress_label.config, {'text': f"Processing: {os.path.basename(input_filepath)} ({i+1}/{total_images})"})
                self.master.after(0, self.progress_bar.step, 1)

                img = Image.open(input_filepath)
                output_image = remove(img)
                self.processed_images[input_filepath] = output_image
                successful_count += 1
                
                selected_path = self.get_selected_file_path()
                if selected_path == input_filepath:
                    self.master.after(0, self.update_preview_display)
                    
            except Exception as e:
                self.master.after(0, messagebox.showerror, "Processing Error", 
                                  f"Could not process {os.path.basename(input_filepath)}: {e}")
            
        self.master.after(0, self.update_ui_state, False)
        self.master.after(0, self.progress_label.config, {'text': f"Progress: Batch Finished! Processed {successful_count}/{total_images} images."})
        self.master.after(0, lambda: messagebox.showinfo("Finished", 
                          f"Batch processing complete! {successful_count} out of {total_images} images processed. "
                          "Use the Save buttons to save them."))

    def save_individual_image(self):
        selected_path = self.get_selected_file_path()
        if not selected_path or selected_path not in self.processed_images:
            messagebox.showerror("Error", "No processed image selected or available to save.")
            return

        img_to_save = self.processed_images[selected_path]
        base_name = os.path.basename(selected_path)
        name, _ = os.path.splitext(base_name)
        default_filename = f"{name}_no_bg.png"
        
        if self.output_dir:
            save_path = os.path.join(self.output_dir, default_filename)
            try:
                img_to_save.save(save_path)
                messagebox.showinfo("Success", f"Image saved directly to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image to default folder: {e}\nFalling back to Save As...")
            else:
                return

        initial_dir = self.output_dir if self.output_dir else os.path.expanduser("~")
        save_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if save_path:
            try:
                img_to_save.save(save_path)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image: {e}")

    def save_all_images(self):
        if not self.processed_images:
            messagebox.showerror("Error", "No images have been processed yet.")
            return

        output_folder = self.output_dir
        if not output_folder:
            output_folder = filedialog.askdirectory(title="Select Folder to Save ALL Processed Images")
            if not output_folder:
                return

        successful_saves = 0
        total_to_save = len(self.processed_images)

        for input_filepath, processed_img in self.processed_images.items():
            try:
                base_name = os.path.basename(input_filepath)
                name, _ = os.path.splitext(base_name)
                output_filepath = os.path.join(output_folder, f"{name}_no_bg.png")

                processed_img.save(output_filepath)
                successful_saves += 1
            except Exception as e:
                print(f"Error saving {input_filepath}: {e}")

        messagebox.showinfo("Save Complete", 
                            f"Saved {successful_saves} out of {total_to_save} processed images to:\n{output_folder}")

# --- Main application entry point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
