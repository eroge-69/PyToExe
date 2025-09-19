import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

class ImageJoinerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Joiner - Horizontal")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.image_paths = []
        self.preview_images = []
        self.joined_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Preview area gets most space
        
        # Title
        title_label = ttk.Label(main_frame, text="Horizontal Image Joiner", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Buttons
        ttk.Button(button_frame, text="Add Images", command=self.add_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Background color
        ttk.Label(options_frame, text="Background Color:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        
        self.bg_color_var = tk.StringVar(value="white")
        color_frame = ttk.Frame(options_frame)
        color_frame.grid(row=0, column=1, sticky=tk.W)
        
        colors = [("White", "white"), ("Black", "black"), ("Gray", "gray"), 
                 ("Red", "red"), ("Green", "green"), ("Blue", "blue"), ("Custom", "custom")]
        
        for i, (text, value) in enumerate(colors):
            if value == "custom":
                ttk.Radiobutton(color_frame, text=text, variable=self.bg_color_var, 
                               value=value, command=self.choose_custom_color).grid(row=0, column=i, padx=2)
            else:
                ttk.Radiobutton(color_frame, text=text, variable=self.bg_color_var, 
                               value=value).grid(row=0, column=i, padx=2)
        
        # Spacing
        ttk.Label(options_frame, text="Spacing (px):").grid(row=1, column=0, padx=(0, 5), sticky=tk.W)
        self.spacing_var = tk.IntVar(value=0)
        ttk.Spinbox(options_frame, from_=0, to=100, textvariable=self.spacing_var, width=5).grid(row=1, column=1, sticky=tk.W)
        
        # Resize option
        self.resize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Resize all to tallest image", 
                       variable=self.resize_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Selected Images", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Listbox with scrollbar for image list
        list_frame = ttk.Frame(preview_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.image_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.image_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Image preview
        self.preview_label = ttk.Label(preview_frame, text="No image selected", 
                                      relief="sunken", padding=10)
        self.preview_label.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Join button
        ttk.Button(main_frame, text="JOIN IMAGES", command=self.join_images, 
                  style="Accent.TButton").grid(row=4, column=0, columnspan=3, pady=10, ipadx=20, ipady=10)
        
        # Save button (initially disabled)
        self.save_button = ttk.Button(main_frame, text="Save Joined Image", 
                                     command=self.save_image, state=tk.DISABLED)
        self.save_button.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to join images")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind events
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        self.image_listbox.bind('<Double-1>', self.on_image_double_click)
        
        # Style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 12, "bold"))
    
    def add_images(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="Select Images to Join",
            filetypes=filetypes
        )
        
        if filenames:
            for filename in filenames:
                if filename not in self.image_paths:
                    self.image_paths.append(filename)
                    self.image_listbox.insert(tk.END, os.path.basename(filename))
            
            self.status_var.set(f"Added {len(filenames)} images. Total: {len(self.image_paths)}")
            self.update_preview()
    
    def remove_selected(self):
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.image_paths.pop(index)
            self.image_listbox.delete(index)
            self.status_var.set(f"Removed image. {len(self.image_paths)} images remaining")
            self.update_preview()
        else:
            messagebox.showinfo("Info", "Please select an image to remove")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove all images?"):
            self.image_paths.clear()
            self.image_listbox.delete(0, tk.END)
            self.preview_label.config(image='', text="No image selected")
            self.status_var.set("All images cleared")
            self.save_button.config(state=tk.DISABLED)
            self.joined_image = None
    
    def move_up(self):
        selection = self.image_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in data list
            self.image_paths[index-1], self.image_paths[index] = self.image_paths[index], self.image_paths[index-1]
            # Swap in listbox
            text = self.image_listbox.get(index)
            self.image_listbox.delete(index)
            self.image_listbox.insert(index-1, text)
            # Keep selection
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(index-1)
            self.image_listbox.activate(index-1)
            self.update_preview()
            self.status_var.set("Image moved up")
    
    def move_down(self):
        selection = self.image_listbox.curselection()
        if selection and selection[0] < self.image_listbox.size() - 1:
            index = selection[0]
            # Swap in data list
            self.image_paths[index+1], self.image_paths[index] = self.image_paths[index], self.image_paths[index+1]
            # Swap in listbox
            text = self.image_listbox.get(index)
            self.image_listbox.delete(index)
            self.image_listbox.insert(index+1, text)
            # Keep selection
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(index+1)
            self.image_listbox.activate(index+1)
            self.update_preview()
            self.status_var.set("Image moved down")
    
    def on_image_select(self, event=None):
        self.update_preview()
    
    def on_image_double_click(self, event=None):
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.show_full_image(self.image_paths[index])
    
    def update_preview(self):
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.show_image_preview(self.image_paths[index])
        elif self.image_paths:
            self.show_image_preview(self.image_paths[0])
            self.image_listbox.selection_set(0)
        else:
            self.preview_label.config(image='', text="No image selected")
    
    def show_image_preview(self, image_path):
        try:
            img = Image.open(image_path)
            
            # Resize for preview (max 300x200)
            img.thumbnail((300, 200), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
        except Exception as e:
            self.preview_label.config(text=f"Error loading image: {e}", image="")
    
    def show_full_image(self, image_path):
        # Create a new window to show full image
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {os.path.basename(image_path)}")
        preview_window.geometry("800x600")
        
        try:
            img = Image.open(image_path)
            
            # Calculate dimensions to fit in window while maintaining aspect ratio
            window_width, window_height = 780, 560
            img_width, img_height = img.size
            
            scale = min(window_width / img_width, window_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = ttk.Label(preview_window, image=photo)
            label.image = photo  # Keep reference
            label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            
            ttk.Label(preview_window, text=f"Size: {img_width}x{img_height}").pack(pady=5)
            
        except Exception as e:
            ttk.Label(preview_window, text=f"Error: {e}").pack(pady=20)
    
    def choose_custom_color(self):
        if self.bg_color_var.get() == "custom":
            # Simple color input dialog
            color_dialog = tk.Toplevel(self.root)
            color_dialog.title("Choose Custom Color")
            color_dialog.geometry("300x200")
            color_dialog.resizable(False, False)
            color_dialog.transient(self.root)
            color_dialog.grab_set()
            
            ttk.Label(color_dialog, text="Enter RGB values (0-255):").pack(pady=10)
            
            frame = ttk.Frame(color_dialog)
            frame.pack(pady=10)
            
            ttk.Label(frame, text="Red:").grid(row=0, column=0, padx=5)
            red_var = tk.StringVar(value="255")
            ttk.Entry(frame, textvariable=red_var, width=5).grid(row=0, column=1, padx=5)
            
            ttk.Label(frame, text="Green:").grid(row=0, column=2, padx=5)
            green_var = tk.StringVar(value="255")
            ttk.Entry(frame, textvariable=green_var, width=5).grid(row=0, column=3, padx=5)
            
            ttk.Label(frame, text="Blue:").grid(row=0, column=4, padx=5)
            blue_var = tk.StringVar(value="255")
            ttk.Entry(frame, textvariable=blue_var, width=5).grid(row=0, column=5, padx=5)
            
            def apply_color():
                try:
                    r = int(red_var.get())
                    g = int(green_var.get())
                    b = int(blue_var.get())
                    
                    if all(0 <= val <= 255 for val in [r, g, b]):
                        self.bg_color_var.set(f"#{r:02x}{g:02x}{b:02x}")
                        color_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "RGB values must be between 0 and 255")
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers")
            
            ttk.Button(color_dialog, text="Apply", command=apply_color).pack(pady=10)
            ttk.Button(color_dialog, text="Cancel", 
                      command=color_dialog.destroy).pack()
    
    def get_background_color(self):
        color = self.bg_color_var.get()
        if color.startswith("#"):
            # Convert hex to RGB tuple
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return (r, g, b)
        else:
            # Named colors
            color_map = {
                "white": (255, 255, 255),
                "black": (0, 0, 0),
                "gray": (128, 128, 128),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255)
            }
            return color_map.get(color, (255, 255, 255))
    
    def join_images(self):
        if not self.image_paths:
            messagebox.showerror("Error", "Please add at least one image")
            return
        
        try:
            # Get options
            background_color = self.get_background_color()
            spacing = self.spacing_var.get()
            resize_to_tallest = self.resize_var.get()
            
            # Open all images
            images = []
            for path in self.image_paths:
                img = Image.open(path)
                images.append(img)
            
            if resize_to_tallest:
                max_height = max(img.height for img in images)
                resized_images = []
                for img in images:
                    if img.height != max_height:
                        # Calculate new width to maintain aspect ratio
                        new_width = int(img.width * (max_height / img.height))
                        img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)
                    resized_images.append(img)
                images = resized_images
            
            # Calculate dimensions
            max_height = max(img.height for img in images)
            total_width = sum(img.width for img in images) + (len(images) - 1) * spacing
            
            # Determine output mode
            has_alpha = any(img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info) 
                           for img in images)
            output_mode = 'RGBA' if has_alpha else 'RGB'
            
            # Create background color tuple for the output mode
            if output_mode == 'RGBA':
                bg_color = background_color + (255,) if len(background_color) == 3 else background_color
            else:
                bg_color = background_color[:3]  # Ensure RGB only
            
            # Create new image
            joined_image = Image.new(output_mode, (total_width, max_height), bg_color)
            
            # Paste images
            x_offset = 0
            for img in images:
                y_offset = (max_height - img.height) // 2
                
                # Handle different image modes
                if img.mode != output_mode:
                    if output_mode == 'RGBA':
                        if img.mode == 'RGB':
                            img = img.convert('RGBA')
                        else:
                            img = img.convert(output_mode)
                    else:
                        img = img.convert(output_mode)
                
                # Paste with transparency if RGBA
                mask = img if img.mode == 'RGBA' else None
                joined_image.paste(img, (x_offset, y_offset), mask)
                
                x_offset += img.width + spacing
            
            self.joined_image = joined_image
            self.save_button.config(state=tk.NORMAL)
            
            # Show preview of joined image
            self.show_joined_preview()
            
            self.status_var.set(f"Successfully joined {len(images)} images! Click 'Save Joined Image' to save.")
            messagebox.showinfo("Success", f"Images joined successfully!\nSize: {total_width} x {max_height}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to join images: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def show_joined_preview(self):
        if self.joined_image:
            # Create preview (resize to fit)
            preview_img = self.joined_image.copy()
            preview_img.thumbnail((800, 300), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
    
    def save_image(self):
        if not self.joined_image:
            return
        
        # Default filename
        default_name = "joined_images_horizontal.jpg"
        if len(self.image_paths) > 0:
            base_name = os.path.splitext(os.path.basename(self.image_paths[0]))[0]
            default_name = f"{base_name}_joined.jpg"
        
        filetypes = [
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("GIF files", "*.gif"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Save Joined Image",
            defaultextension=".jpg",
            initialfile=default_name,
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Determine format based on extension
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    # Convert to RGB if saving as JPEG
                    save_img = self.joined_image.convert('RGB') if self.joined_image.mode in ('RGBA', 'LA') else self.joined_image
                    save_img.save(filename, 'JPEG', quality=95)
                else:
                    self.joined_image.save(filename)
                
                self.status_var.set(f"Image saved successfully: {filename}")
                messagebox.showinfo("Success", f"Image saved to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
                self.status_var.set(f"Error saving image: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageJoinerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()