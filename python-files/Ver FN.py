import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
import customtkinter as ctk
from PIL import Image, ImageTk # Import Pillow for image handling

# --- Global Variables ---
rom_folder = ""
rom_files = []
thumbnail_map = {}
current_theme = "Dark" # Default theme
# Store PhotoImage references to prevent garbage collection
thumbnail_previews = {}
no_image_icon = None # To store a default "no image" icon

# --- Functions ---
def set_theme(theme_name):
    ctk.set_appearance_mode(theme_name)
    global current_theme
    current_theme = theme_name
    # Re-apply ttk theme settings after changing customtkinter theme
    # This ensures ttk widgets (like Treeview) also update their appearance
    configure_ttk_theme(theme_name) 

    # Update button text/icon for theme toggle
    if theme_name == "Dark":
        btn_theme_toggle.configure(text="☀️ Light Mode", fg_color="#d9d9d9", text_color="black", hover_color="#c0c0c0")
    else:
        btn_theme_toggle.configure(text="🌙 Dark Mode", fg_color="#363636", text_color="white", hover_color="#454545")

def select_rom_folder():
    global rom_folder, rom_files, thumbnail_map
    new_rom_folder = filedialog.askdirectory(title="Chọn thư mục chứa game (.jar)")
    if not new_rom_folder:
        return

    rom_folder = new_rom_folder
    rom_files = [f for f in os.listdir(rom_folder) if f.lower().endswith(".jar")]
    thumbnail_map = {} # Reset map when new folder is selected
    thumbnail_previews.clear() # Clear existing previews

    # Update GUI elements
    lbl_rom_path_display.configure(text=f"{os.path.basename(rom_folder)}") # Only base name
    lbl_full_path_tooltip.set(rom_folder) # Set tooltip for full path
    
    # Update game count label and animate
    lbl_rom_count.configure(text=f"Đã quét được: {len(rom_files)} game")
    animate_label_color(lbl_rom_count) # Animate count label
    
    update_table()

def animate_label_color(label, original_color=None, highlight_color="#4CAF50", duration=500):
    if original_color is None:
        # Get current text color considering it might be a tuple for themes
        if isinstance(label.cget("text_color"), tuple):
            original_color = label.cget("text_color")[0] if ctk.get_appearance_mode() == "Light" else label.cget("text_color")[1]
        else:
            original_color = label.cget("text_color")

    label.configure(text_color=highlight_color)
    root.after(duration, lambda: label.configure(text_color=original_color))


def choose_thumbnail(index):
    # Ensure index is valid
    if index < 0 or index >= len(rom_files):
        return

    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    if image_path:
        rom_name = rom_files[index]
        thumbnail_map[rom_name] = image_path
        update_table()

def export_xml():
    if not rom_folder or not rom_files:
        messagebox.showerror("Lỗi", "Chưa chọn thư mục game hoặc thư mục trống!", icon="warning")
        return

    images_folder = os.path.join(rom_folder, "images")
    try:
        os.makedirs(images_folder, exist_ok=True)
    except OSError as e:
        messagebox.showerror("Lỗi", f"Không thể tạo thư mục 'images': {e}", icon="error")
        return

    root_xml_elem = ET.Element("gameList")

    for rom in rom_files:
        rom_name = os.path.splitext(rom)[0]
        image_path = thumbnail_map.get(rom, "")
        image_filename = ""

        if image_path:
            ext = os.path.splitext(image_path)[1]
            image_filename = rom_name + ext
            try:
                shutil.copy(image_path, os.path.join(images_folder, image_filename))
            except IOError as e:
                messagebox.showwarning("Cảnh báo", f"Không thể sao chép ảnh cho {rom_name}: {e}. Game này sẽ không có thumbnail trong XML.", icon="warning")
                image_filename = "" # Do not link if copy failed

        game_elem = ET.SubElement(root_xml_elem, "game")
        ET.SubElement(game_elem, "path").text = f"./{rom}"
        ET.SubElement(game_elem, "name").text = rom_name
        ET.SubElement(game_elem, "image").text = f"./images/{image_filename}" if image_filename else ""
        ET.SubElement(game_elem, "desc").text = "Game Java"
        ET.SubElement(game_elem, "genre").text = "Unknown"
        ET.SubElement(game_elem, "releasedate").text = "20000101T000000"
        ET.SubElement(game_elem, "developer").text = "Unknown"
        ET.SubElement(game_elem, "publisher").text = "Unknown"
        ET.SubElement(game_elem, "rating").text = "0.0"
        ET.SubElement(game_elem, "players").text = "1"
        ET.SubElement(game_elem, "controller").text = "standard"

    tree_xml = ET.ElementTree(root_xml_elem)
    try:
        tree_xml.write(os.path.join(rom_folder, "gamelist.xml"), encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Thành công", "Đã xuất file gamelist.xml và sao chép ảnh thành công!", icon="info")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xuất file gamelist.xml: {e}", icon="error")

def update_table():
    for row in tree.get_children():
        tree.delete(row)
    
    # Clear old references
    thumbnail_previews.clear()

    # Define thumbnail size for preview
    preview_size = (32, 32) # Small size for inline display

    for i, rom in enumerate(rom_files):
        image_path = thumbnail_map.get(rom, "")
        
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail(preview_size) # Resize for preview
                photo = ImageTk.PhotoImage(img)
                
                # Store the PhotoImage object to prevent garbage collection
                # Use a unique key for each item in the tree
                thumbnail_previews[f"preview_{i}"] = photo 
                
                # Insert item with the image. Tkinter's Treeview supports images.
                # The image appears in the first column (Game Name)
                tree.insert("", "end", iid=i, values=(rom, "✅ Đã có ảnh"), image=photo, tags=('thumb_col_exists',))
            except Exception as e:
                # If image loading fails, treat as no image
                print(f"Error loading thumbnail for {rom}: {e}")
                tree.insert("", "end", iid=i, values=(rom, "Chưa có ảnh (Click để chọn)"), image=no_image_icon, tags=('thumb_col_no_img',))
        else:
            tree.insert("", "end", iid=i, values=(rom, "Chưa có ảnh (Click để chọn)"), image=no_image_icon, tags=('thumb_col_no_img',))

def on_tree_click(event):
    item = tree.identify_row(event.y)
    if item:
        col = tree.identify_column(event.x)
        # Check if the click was on the "Thumbnail Status" column (second visible column)
        if col == '#2': 
            choose_thumbnail(int(item))

def toggle_theme():
    if current_theme == "Dark":
        set_theme("Light")
    else:
        set_theme("Dark")

# Function to configure ttk.Treeview theme and tags
def configure_ttk_theme(mode):
    if mode == "Dark":
        style.configure("Treeview",
                        background="#2B2B2B",  # Dark grey background
                        foreground="white",
                        fieldbackground="#2B2B2B",
                        font=('Arial', 10),
                        rowheight=36) # Increased row height for thumbnail
        style.map('Treeview', background=[('selected', '#1F6AA5')]) # Darker blue selection
        style.configure("Treeview.Heading",
                        font=('Arial', 11, 'bold'),
                        background="#363636", # Darker heading
                        foreground="white",
                        relief="flat") # Make heading flatter
        style.map('Treeview.Heading', background=[('active', '#454545')])
        style.configure("Treeview", borderwidth=0, highlightthickness=0) # Remove default borders
        style.map("Treeview",
            background=[('selected', '#1F6AA5')],
            foreground=[('selected', 'white')]
        )
    else: # Light Mode
        style.configure("Treeview",
                        background="#E0E0E0",
                        foreground="black",
                        fieldbackground="#E0E0E0",
                        font=('Arial', 10),
                        rowheight=36) # Increased row height
        style.map('Treeview', background=[('selected', '#3B8ED0')])
        style.configure("Treeview.Heading",
                        font=('Arial', 11, 'bold'),
                        background="#D0D0D0",
                        foreground="black",
                        relief="flat") # Make heading flatter
        style.map('Treeview.Heading', background=[('active', '#C0C0C0')])
        style.configure("Treeview", borderwidth=0, highlightthickness=0)
        style.map("Treeview",
            background=[('selected', '#3B8ED0')],
            foreground=[('selected', 'white')]
        )
    
    # Custom colors for rows/items based on tags
    # These configurations rely on 'tree' being defined globally before this function is first called
    tree.tag_configure('thumb_col_exists', foreground="#28a745") # Green for "has image" status
    tree.tag_configure('thumb_col_no_img', foreground="#dc3545", font=('Arial', 10, 'italic')) # Red for "no image" status


# Simple Tooltip class for full path display
class Tooltip:
    def __init__(self, widget, text_var):
        self.widget = widget
        self.text_var = text_var # Use StringVar for dynamic text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tooltip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show_tooltip) # Show after 500ms

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def show_tooltip(self):
        tooltip_text = self.text_var.get()
        if self.tooltip_window or not tooltip_text:
            return
        
        # Position the tooltip slightly offset from the cursor
        x, y = root.winfo_pointerx() + 10, root.winfo_pointery() + 10

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) # Removes window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Determine background color based on current theme
        bg_color = "#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#454545"
        fg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"

        label = ctk.CTkLabel(self.tooltip_window, text=tooltip_text,
                             fg_color=bg_color, # Use fg_color for background in CTkLabel for tooltip
                             text_color=fg_color,
                             padx=8, pady=4, corner_radius=5)
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def set(self, new_text):
        self.text_var.set(new_text)
        if self.tooltip_window: # Update live if tooltip is shown
            self.hide_tooltip()
            self.show_tooltip()


# --- GUI Setup ---
ctk.set_appearance_mode("Dark") # Initial theme
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Java Thumbnail R36S - Công cụ quản lý ROM")
root.geometry("700x550")
root.resizable(False, False)

# Main frame (outermost container for overall rounded look)
main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color=("gray92", "gray15")) # Lighter/Darker background for rounded corners
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Header Section (Top part with Theme toggle, Select Folder, Path)
header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
header_frame.pack(pady=(15, 5), padx=20, fill="x")

# Theme toggle button
btn_theme_toggle = ctk.CTkButton(header_frame, text="☀️ Light Mode", command=toggle_theme,
                                 width=120, height=35, corner_radius=8,
                                 fg_color="#d9d9d9", text_color="black", # Default Light mode look
                                 hover_color="#c0c0c0", font=ctk.CTkFont(size=12, weight="bold"))
btn_theme_toggle.pack(side="right", padx=(0, 0)) # Aligned to top-right

# Folder Selection and Path Display
folder_path_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
folder_path_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

btn_rom = ctk.CTkButton(folder_path_frame, text="Chọn Thư Mục Game (.jar)", command=select_rom_folder,
                        width=200, height=40, corner_radius=10,
                        font=ctk.CTkFont(size=14, weight="bold"),
                        fg_color="#2FA572", # Green color
                        hover_color="#25825A")
btn_rom.pack(side="left", padx=(0, 15))

lbl_rom_path_display = ctk.CTkLabel(folder_path_frame, text="D: \\ Java", # Placeholder text
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   text_color=("gray20", "gray70"))
lbl_rom_path_display.pack(side="left", anchor="center")

# Tooltip for full path display
full_path_var = tk.StringVar(value="Đường dẫn đầy đủ sẽ hiển thị ở đây.")
lbl_full_path_tooltip = Tooltip(lbl_rom_path_display, full_path_var)

# Separator line
separator = ctk.CTkFrame(main_frame, height=1, fg_color=("gray80", "gray30"))
separator.pack(fill="x", padx=20, pady=5)

# Game Count Label
lbl_rom_count = ctk.CTkLabel(main_frame, text="Đã quét được: 20 game", # Placeholder text
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color=("gray10", "gray80"))
lbl_rom_count.pack(pady=(10, 10))

# Game List Section
list_section_frame = ctk.CTkFrame(main_frame, fg_color=("gray92", "gray20"), corner_radius=10) # Frame for list with background
list_section_frame.pack(pady=10, padx=20, fill="both", expand=True)

lbl_list_title = ctk.CTkLabel(list_section_frame, text="Danh Sách Game",
                              font=ctk.CTkFont(size=16, weight="bold"))
lbl_list_title.pack(pady=(10, 5), anchor="w", padx=10)


# Styling for Treeview (ttk)
style = ttk.Style()
style.theme_use("default") # Important: use a default theme before configuring

# Create the Treeview widget FIRST
# Columns: Game Name, Thumbnail Status
tree = ttk.Treeview(list_section_frame, columns=("Game", "Thumbnail"), show="headings", height=10) # Set height for fewer rows initally
tree.heading("Game", text="Tên game (.jar)")
tree.heading("Thumbnail", text="Trạng thái Thumbnail")
tree.column("Game", width=300, anchor="w")
tree.column("Thumbnail", width=250, anchor="center")
tree.bind("<ButtonRelease-1>", on_tree_click)
tree.pack(fill="both", expand=True, padx=10, pady=(0, 10)) # Added padding for visual separation

# NOW call configure_ttk_theme after 'tree' is defined, and initial theme set
configure_ttk_theme(current_theme) 

# Load a default "no image" icon
try:
    # Make sure 'no_image_icon.png' exists in the same directory as your script
    # This icon will appear when no thumbnail is set for a game
    no_img = Image.open("no_image_icon.png") 
    no_img.thumbnail((32,32))
    no_image_icon = ImageTk.PhotoImage(no_img)
except FileNotFoundError:
    print("Warning: 'no_image_icon.png' not found. Using default blank icon for no image.")
    no_image_icon = ImageTk.PhotoImage(Image.new('RGBA', (32, 32), (0, 0, 0, 0))) # Transparent 32x32

# Scrollbar for Treeview
scrollbar = ctk.CTkScrollbar(tree, command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# Export Button Section
btn_export = ctk.CTkButton(main_frame, text="📤 Xuất file gamelist.xml", command=export_xml,
                           width=280, height=45, corner_radius=12,
                           font=ctk.CTkFont(size=16, weight="bold"),
                           fg_color="#00A86B", # Green color
                           hover_color="#008C5A",
                           text_color="white")
btn_export.pack(pady=(10, 20)) # Added padding for visual separation

# Set initial theme (redundant if already set above, but good for clarity)
set_theme(current_theme)

root.mainloop()