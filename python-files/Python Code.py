import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Label, Button, Listbox, Scrollbar
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import numpy as np
import os

class ImageUtilityApp:
    """
    A Tkinter application combining multiple image utilities:
    - BMP to PNG Converter
    - PNG to BMP Converter (with white pixels becoming black)
    - Image Vertical Stacker
    - Add Right Padding to Images
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Image Utility")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # Initialize file_list for the Image Stacker, will be reset when module is opened
        self.file_list = []

        self.create_main_menu()

    def create_main_menu(self):
        """
        Creates and displays the main menu with buttons to select different utilities.
        """
        # Clear existing widgets from the root window
        self.clear_frame()

        # Ensure the main window title is set when returning to the main menu
        self.root.title("Image Utility")

        Label(self.root, text="Select an Image Utility:", font=("Helvetica", 16)).pack(pady=20)

        Button(self.root, text="🖼️ BMP to PNG Converter", command=self.show_bmp_to_png_converter, width=30, height=2).pack(pady=10)
        Button(self.root, text="🖼️ PNG to BMP Converter", command=self.show_png_to_bmp_converter, width=30, height=2).pack(pady=10)
        Button(self.root, text="⬆️ Image Vertical Stacker", command=self.show_image_stacker, width=30, height=2).pack(pady=10)
        Button(self.root, text="➡️ Add Right Padding", command=self.show_add_right_padding, width=30, height=2).pack(pady=10)
        Button(self.root, text="❌ Exit", command=self.root.quit, width=30, height=2).pack(pady=20)

    def clear_frame(self):
        """
        Destroys all widgets currently packed or gridded on the root window,
        preparing it for a new layout. Resets grid configurations.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        # Reset grid configuration for new layouts (important for stacker's grid)
        for i in range(self.root.grid_size()[0]):
            self.root.grid_columnconfigure(i, weight=0)
        for i in range(self.root.grid_size()[1]):
            self.root.grid_rowconfigure(i, weight=0)

    # --- BMP to PNG Converter Functions ---
    def show_bmp_to_png_converter(self):
        """
        Displays the UI for the BMP to PNG converter.
        """
        self.clear_frame()
        self.root.title("BMP to PNG Converter (with Drag-and-Drop)") # Specific title for this module

        drop_label = Label(self.root, text="🖼️ Drag and drop BMP file here", relief="ridge", width=60, height=6)
        drop_label.pack(pady=20)
        # Register the label as a drop target for files
        drop_label.drop_target_register(DND_FILES)
        # Bind the drop event to the handler function
        drop_label.dnd_bind('<<Drop>>', self.on_drop_bmp_to_png)

        Button(self.root, text="📂 Select BMP and Convert", command=self.open_file_dialog_bmp_to_png).pack(pady=5)
        Button(self.root, text="⬅️ Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def convert_bmp_to_png(self, filepath):
        """
        Converts a BMP image to PNG format.
        """
        if not filepath.lower().endswith(".bmp"):
            messagebox.showwarning("Invalid File", "Only BMP files are supported for this conversion.")
            return

        try:
            img = Image.open(filepath)

            # Ask for save location, defaulting to the same folder and name
            default_name = os.path.splitext(os.path.basename(filepath))[0]
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=default_name,
                initialdir=os.path.dirname(filepath),
                filetypes=[("PNG files", "*.png")],
                title="Save PNG Image"
            )
            if save_path:
                img.save(save_path, format='PNG')
                messagebox.showinfo("Success", f"Image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{e}")

    def open_file_dialog_bmp_to_png(self):
        """
        Opens a file dialog to select a BMP file for conversion.
        """
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.convert_bmp_to_png(file_path)

    def on_drop_bmp_to_png(self, event):
        """
        Handles files dropped onto the BMP to PNG converter's drop area.
        """
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(".bmp"):
                self.convert_bmp_to_png(file)
            else:
                messagebox.showwarning("Invalid File", f"Skipped: {file} (Only BMP files are supported)")

    # --- PNG to BMP Converter Functions ---
    def show_png_to_bmp_converter(self):
        """
        Displays the UI for the PNG to BMP converter.
        """
        self.clear_frame()
        self.root.title("PNG to BMP Converter (with Drag-and-Drop)") # Specific title for this module

        drop_label = Label(self.root, text="🖼️ Drag and drop PNG file here", relief="ridge", width=60, height=6)
        drop_label.pack(pady=20)
        # Register the label as a drop target for files
        drop_label.drop_target_register(DND_FILES)
        # Bind the drop event to the handler function
        drop_label.dnd_bind('<<Drop>>', self.on_drop_png_to_bmp)

        Button(self.root, text="📂 Select PNG and Convert", command=self.open_file_dialog_png_to_bmp).pack(pady=5)
        Button(self.root, text="⬅️ Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def convert_png_to_bmp(self, filepath):
        """
        Converts a PNG image to a 1-bit BMP format, where white pixels remain white
        and all other colors become black.
        """
        if not filepath.lower().endswith(".png"):
            messagebox.showwarning("Invalid File", "Only PNG files are supported for this conversion.")
            return

        try:
            # Load image and convert to RGB to ensure consistent color channels
            img = Image.open(filepath).convert("RGB")
            img_array = np.array(img)

            # Create a mask: white pixels ([255, 255, 255]) stay white, others become black (0)
            white_mask = np.all(img_array == [255, 255, 255], axis=-1)
            bw_array = np.where(white_mask, 255, 0).astype(np.uint8)

            # Convert the NumPy array to a 1-bit PIL image (black and white)
            bw_image = Image.fromarray(bw_array, mode='L').convert('1')

            # Ask for save location, defaulting to the same folder and name
            default_name = os.path.splitext(os.path.basename(filepath))[0]
            save_path = filedialog.asksaveasfilename(
                defaultextension=".bmp",
                initialfile=default_name,
                initialdir=os.path.dirname(filepath),
                filetypes=[("Bitmap files", "*.bmp")],
                title="Save BMP Image"
            )
            if save_path:
                bw_image.save(save_path)
                messagebox.showinfo("Success", f"Image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{e}")

    def open_file_dialog_png_to_bmp(self):
        """
        Opens a file dialog to select a PNG file for conversion.
        """
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.convert_png_to_bmp(file_path)

    def on_drop_png_to_bmp(self, event):
        """
        Handles files dropped onto the PNG to BMP converter's drop area.
        """
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith(".png"):
                self.convert_png_to_bmp(file)
            else:
                messagebox.showwarning("Invalid File", f"Skipped: {file} (Only PNG files are supported)")

    # --- Image Vertical Stacker Functions ---
    def show_image_stacker(self):
        """
        Displays the UI for the Image Vertical Stacker.
        """
        self.clear_frame()
        self.root.title("Image Vertical Stacker") # Specific title for this module
        self.file_list = [] # Reset file list for a new stacking session

        # Configure grid for better layout, allowing listbox to expand
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(0, weight=1) # Allow listbox row to expand vertically

        # File list Listbox with drag-and-drop
        self.listbox = Listbox(self.root, selectmode=tk.SINGLE, width=70)
        self.listbox.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        scrollbar = Scrollbar(self.root, command=self.listbox.yview)
        scrollbar.grid(row=0, column=4, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Register the listbox as a drop target for files
        self.listbox.drop_target_register(DND_FILES)
        # Bind the drop event to the handler function
        self.listbox.dnd_bind('<<Drop>>', self.drop_files_stacker)

        # Buttons for managing the list and combining images
        tk.Button(self.root, text="Add Image Files", command=self.add_files_stacker).grid(row=1, column=0, pady=5)
        tk.Button(self.root, text="Remove Selected", command=self.remove_selected_stacker).grid(row=1, column=1, pady=5)
        tk.Button(self.root, text="Move Up", command=self.move_up_stacker).grid(row=1, column=2, pady=5)
        tk.Button(self.root, text="Move Down", command=self.move_down_stacker).grid(row=1, column=3, pady=5)
        tk.Button(self.root, text="Combine & Save", command=self.combine_and_save_stacker).grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button(self.root, text="⬅️ Back to Main Menu", command=self.create_main_menu).grid(row=3, column=0, columnspan=4, pady=5) # Added this button

    def drop_files_stacker(self, event):
        """
        Handles files dropped onto the Image Stacker's listbox.
        Adds valid image files to the list.
        """
        dropped = self.root.tk.splitlist(event.data)
        for f in dropped:
            # Check if it's a file and a common image extension
            if os.path.isfile(f) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff', '.webp')):
                if f not in self.file_list: # Avoid adding duplicates
                    self.file_list.append(f)
                    self.listbox.insert(tk.END, os.path.basename(f)) # Display only filename in listbox

    def add_files_stacker(self):
        """
        Opens a file dialog to allow users to select multiple image files.
        """
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.*")]) # Allow all image types
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def remove_selected_stacker(self):
        """
        Removes the currently selected image file from the list.
        """
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.file_list[index]

    def move_up_stacker(self):
        """
        Moves the selected image file up in the list, changing its stacking order.
        """
        selected = self.listbox.curselection()
        if selected and selected[0] > 0: # Ensure an item is selected and not the first one
            i = selected[0]
            # Swap the file paths in the internal list
            self.file_list[i], self.file_list[i-1] = self.file_list[i-1], self.file_list[i]
            self.refresh_listbox_stacker() # Update the displayed listbox
            self.listbox.select_set(i-1) # Keep the moved item selected

    def move_down_stacker(self):
        """
        Moves the selected image file down in the list, changing its stacking order.
        """
        selected = self.listbox.curselection()
        if selected and selected[0] < len(self.file_list) - 1: # Ensure an item is selected and not the last one
            i = selected[0]
            # Swap the file paths in the internal list
            self.file_list[i], self.file_list[i+1] = self.file_list[i+1], self.file_list[i]
            self.refresh_listbox_stacker() # Update the displayed listbox
            self.listbox.select_set(i+1) # Keep the moved item selected

    def refresh_listbox_stacker(self):
        """
        Clears and repopulates the listbox to reflect changes in `self.file_list`.
        """
        self.listbox.delete(0, tk.END)
        for f in self.file_list:
            self.listbox.insert(tk.END, os.path.basename(f))

    def combine_and_save_stacker(self):
        """
        Combines all images in `self.file_list` vertically and saves the result.
        If the output format is BMP, it converts the image to 1-bit monochrome.
        Checks if all images have the same width before proceeding.
        """
        if not self.file_list:
            messagebox.showwarning("No Files", "Please add image files to combine.")
            return

        try:
            # Open all images and convert to RGB for consistent pasting
            images = [Image.open(f).convert("RGB") for f in self.file_list]

            # Get widths of all images
            widths = [img.width for img in images]
            heights = [img.height for img in images]

            # Check if all widths are the same
            if len(set(widths)) > 1:
                messagebox.showwarning(
                    "Different Widths",
                    "Images have different widths. Please ensure all images have the same width for stacking."
                )
                return

            max_width = widths[0] # All widths are the same, so take the first one
            total_height = sum(heights)

            # Create a new blank image with white background
            combined_rgb_image = Image.new("RGB", (max_width, total_height), color=(255, 255, 255))

            # Paste images one by one vertically
            y_offset = 0
            for img in images:
                combined_rgb_image.paste(img, (0, y_offset)) # Paste at (0, current_y_offset)
                y_offset += img.height # Increment y_offset for the next image

            # Let the user choose the output format explicitly.
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png", # Default to PNG as a common, versatile format
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("BMP files", "*.bmp"), # BMP option
                    ("GIF files", "*.gif"),
                    ("TIFF files", "*.tif *.tiff"),
                    ("All files", "*.*")
                ],
                title="Save Combined Image As"
            )

            if save_path:
                # Determine the chosen file extension
                _, output_ext = os.path.splitext(save_path)
                output_ext = output_ext.lower()

                final_image_to_save = combined_rgb_image

                # If the user selected BMP, convert to 1-bit monochrome
                if output_ext == ".bmp":
                    img_array = np.array(combined_rgb_image)
                    # Create mask: white stays white, others become black
                    white_mask = np.all(img_array == [255, 255, 255], axis=-1)
                    bw_array = np.where(white_mask, 255, 0).astype(np.uint8)
                    # Convert to 1-bit PIL image
                    final_image_to_save = Image.fromarray(bw_array, mode='L').convert('1')

                # Save the final image
                final_image_to_save.save(save_path)
                messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to combine images:\n{e}")

    # --- Add Right Padding to Images Functions ---
    def show_add_right_padding(self):
        """
        Displays the UI for adding right padding to images.
        """
        self.clear_frame()
        self.root.title("Add Right Padding to Images") # Specific title for this module
        # Removed: self.root.geometry("400x230") to prevent resizing

        label = Label(self.root, text="Drag and drop image files here", width=40, height=5, relief="ridge", bg="#f0f0f0")
        label.pack(pady=20)
        label.drop_target_register(DND_FILES)
        label.dnd_bind('<<Drop>>', self.on_drop_padding)

        button_add = Button(self.root, text="Add Images via Dialog", command=self.add_image_via_button_padding)
        button_add.pack(pady=5)

        Button(self.root, text="⬅️ Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def add_right_padding_logic(self, image, new_width):
        """
        Adds white padding to the right of an image to reach a new_width.
        Returns None if new_width is less than original_width.
        """
        original_width, height = image.size
        if new_width < original_width:
            return None
        # Create a new image with the desired width and original height, filled with white
        new_image = Image.new("RGB", (new_width, height), color=(255, 255, 255))
        # Paste the original image onto the new image at the top-left corner
        new_image.paste(image, (0, 0))
        return new_image

    def process_images_padding(self, filepaths):
        """
        Processes a list of image filepaths to add right padding.
        Asks for a new width and save mode (replace or save as new file).
        """
        if not filepaths:
            return

        # Open first image to get reference width for the dialog prompt
        try:
            ref_image = Image.open(filepaths[0])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open reference image:\n{e}")
            return

        ref_width, _ = ref_image.size
        new_width = simpledialog.askinteger("New Width", f"Enter total width (>= {ref_width}):", parent=self.root)

        if new_width is None: # User cancelled the width dialog
            return

        if new_width < ref_width:
            messagebox.showerror("Invalid Width", f"Entered width {new_width} is less than original width {ref_width}.")
            return

        # Ask once: replace or save as
        choice = messagebox.askyesnocancel(
            "Save Mode",
            "How do you want to save all images?\n\nYes = Replace all original files\nNo = Save As new files\nCancel = Abort",
            parent=self.root
        )

        if choice is None: # Corrected: changed '===' to 'is'
            return

        save_as = not choice  # False = replace, True = save as

        processed_count = 0
        for filepath in filepaths:
            try:
                image = Image.open(filepath).convert("RGB") # Ensure RGB for consistent padding color
                original_width, _ = image.size

                if new_width < original_width:
                    messagebox.showwarning("Skipped", f"Skipped {os.path.basename(filepath)}: New width is less than original width.")
                    continue

                new_image = self.add_right_padding_logic(image, new_width)
                if not new_image: # Should not happen if new_width >= original_width, but as a safeguard
                    messagebox.showerror("Error", f"Failed to pad {os.path.basename(filepath)}.")
                    continue

                if save_as:
                    default_name = os.path.splitext(os.path.basename(filepath))[0] + "_padded.png"
                    save_path = filedialog.asksaveasfilename(
                        title=f"Save Padded Image As: {os.path.basename(filepath)}",
                        defaultextension=".png",
                        initialfile=default_name,
                        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("BMP Image", "*.bmp"), ("All Files", "*.*")],
                        parent=self.root
                    )
                    if save_path:
                        new_image.save(save_path)
                        processed_count += 1
                else:
                    new_image.save(filepath) # Overwrite original
                    processed_count += 1

            except Exception as e:
                messagebox.showerror("Error", f"Error processing {os.path.basename(filepath)}:\n{e}")

        # Show final message once
        if processed_count > 0:
            messagebox.showinfo("Done", f"✅ Done: {processed_count} images processed.", parent=self.root)
        else:
            messagebox.showinfo("Done", "No images were processed.", parent=self.root)


    def add_image_via_button_padding(self):
        """
        Callback for the 'Add Images' button in the padding module.
        Opens a file dialog and passes selected files to process_images_padding.
        """
        filepaths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        self.process_images_padding(filepaths)

    def on_drop_padding(self, event):
        """
        Handles files dropped onto the padding module's drop area.
        Filters for image files and passes them to process_images_padding.
        """
        files = self.root.tk.splitlist(event.data)
        image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))]
        if image_files:
            self.process_images_padding(image_files)
        else:
            messagebox.showwarning("Invalid File", "Please drop valid image files.")


# Main execution block
if __name__ == "__main__":
    # Create the main TkinterDnD window
    root = TkinterDnD.Tk()
    # Instantiate the application
    app = ImageUtilityApp(root)
    # Start the Tkinter event loop
    root.mainloop()
