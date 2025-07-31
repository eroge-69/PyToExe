import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from pathlib import Path

# Configuration
DEFAULT_BASE_PATH = Path.home() / "Clients"
CONFIG_FILE = Path.home() / "client_config.json"

# Default project structure
DEFAULT_STRUCTURE = {
    "project_root": [
        "01_Assets",
        {
            "folders": [
                "01_Assets/01_Images",
                "01_Assets/02_Video",
                "01_Assets/03_Audio",
                "01_Assets/04_Fonts",
                "01_Assets/05_Branding",
                "01_Assets/05_Branding/Logos",
                "01_Assets/05_Branding/Color_Palette",
                "01_Assets/05_Branding/Guidelines.pdf",
                "01_Assets/06_Pre-Renders",
                "01_Assets/06_Pre-Renders/Rotoscoped",
                "01_Assets/06_Pre-Renders/3D_Renders"
            ]
        },
        "02_Project_Files",
        {
            "folders": [
                "02_Project_Files/01_Design",
                "02_Project_Files/01_Design/Storyboards",
                "02_Project_Files/01_Design/Sketches",
                "02_Project_Files/01_Design/Styleframes",
                "02_Project_Files/01_Design/Styleframes/Illustrator",
                "02_Project_Files/01_Design/Styleframes/Photoshop",
                "02_Project_Files/02_Animation",
                "02_Project_Files/02_Animation/AfterEffects",
                "02_Project_Files/02_Animation/Blender",
                "02_Project_Files/03_Edits",
                "02_Project_Files/03_Edits/PremierePro",
                "02_Project_Files/04_Sound_Design",
                "02_Project_Files/04_Sound_Design/DAW_ProjectFiles"
            ]
        },
        "03_Renders",
        {
            "folders": [
                "03_Renders/01_Rough_Cuts",
                "03_Renders/02_Final_Renders"
            ]
        },
        "04_Documents",
        {
            "folders": [
                "04_Documents/Script",
                "04_Documents/Creative_Direction",
                "04_Documents/Client_Feedback",
                "04_Documents/Delivery_Checklist"
            ]
        },
        "05_Exports",
        {
            "folders": [
                "05_Exports/Social",
                "05_Exports/YouTube",
                "05_Exports/ClientDelivery"
            ]
        }
    ]
}

class ProjectManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Manager")
        self.root.geometry("400x600")

        # Set window and taskbar icon (replace 'path/to/app_icon.ico' with your actual ICO file path)
        try:
            self.root.iconbitmap('settings.ico')
        except tk.TclError:
            print("Icon file not found. Please provide a valid .ico file path.")

        # Create canvas for subtle gradient background
        self.canvas = tk.Canvas(self.root, width=400, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.create_gradient()

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 10), padding=10, background="#007AFF", foreground="black", borderwidth=2)
        self.style.map("TButton", background=[("active", "#005BB5")], foreground=[("active", "black")])
        self.style.configure("TLabel", font=("Helvetica", 10), background="#F2F2F7")
        self.style.configure("TEntry", font=("Helvetica", 10))
        self.style.configure("TCombobox", font=("Helvetica", 10))

        # Load existing clients and base path
        self.clients, self.base_path = self.load_config()
        if not self.base_path:
            self.base_path = DEFAULT_BASE_PATH

        # UI Elements
        self.create_ui()
        self.update_client_list()  # Call after UI is created

    def create_gradient(self):
        # Subtle gradient from light gray (#F2F2F7) to slightly darker gray (#E5E5EA)
        for i in range(600):
            r = int(242 - (242 - 229) * (i / 600))
            g = int(242 - (242 - 229) * (i / 600))
            b = int(247 - (247 - 234) * (i / 600))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_rectangle(0, i, 400, i + 1, fill=color, outline=color)

    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header with larger serif font
        ttk.Label(main_frame, text="Hello", font=("Times New Roman", 32, "bold")).grid(row=0, column=0, pady=(0, 5))
        # Date under Hello in non-serif, thin font
        ttk.Label(main_frame, text="Thu, Jul 31, 2025, 02:57 PM EEST", font=("Helvetica", 8, "normal")).grid(row=1, column=0, pady=(0, 20))

        # Base Path with Browse button
        base_path_frame = ttk.Frame(main_frame)
        base_path_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(base_path_frame, text="Base Path:").grid(row=0, column=0, sticky=tk.W)
        self.base_path_label = ttk.Label(base_path_frame, text=str(self.base_path), width=25)
        self.base_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(base_path_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2, padx=5)

        # Project Name and Entry on same row
        project_frame = ttk.Frame(main_frame)
        project_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(project_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W)
        self.project_name = ttk.Entry(project_frame, width=30)
        self.project_name.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Client and Dropdown on same row
        client_frame = ttk.Frame(main_frame)
        client_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(client_frame, text="Client:").grid(row=0, column=0, sticky=tk.W)
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(client_frame, textvariable=self.client_var, width=28)
        self.client_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(client_frame, text="New Client", command=self.add_new_client).grid(row=0, column=2, padx=5)

        # New Client Name (hidden initially)
        self.new_client_frame = ttk.Frame(main_frame)
        self.new_client_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(self.new_client_frame, text="New Client Name:").grid(row=0, column=0, sticky=tk.W)
        self.new_client_name = ttk.Entry(self.new_client_frame, width=30)
        self.new_client_name.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.new_client_frame.grid_remove()

        # Bind client selection
        self.client_dropdown.bind("<<ComboboxSelected>>", self.toggle_new_client)

        # Create Button with wired border
        create_button = ttk.Button(main_frame, text="Create", command=self.create_project, style="TButton")
        create_button.grid(row=6, column=0, pady=20)

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        base_path_frame.columnconfigure(1, weight=1)
        project_frame.columnconfigure(1, weight=1)
        client_frame.columnconfigure(1, weight=1)

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=str(self.base_path))
        if directory:
            self.base_path = Path(directory)
            self.base_path_label.config(text=str(self.base_path))
            self.update_client_list()

    def toggle_new_client(self, event=None):
        if self.client_var.get() == "New Client":
            self.new_client_frame.grid()
        else:
            self.new_client_frame.grid_remove()

    def add_new_client(self):
        self.new_client_frame.grid()
        self.client_dropdown.set("")

    def update_client_list(self):
        if self.base_path.exists() and self.base_path.is_dir():
            client_folders = [d for d in self.base_path.iterdir() if d.is_dir()]
            self.clients = {d.name: str(d) for d in client_folders}
            self.client_dropdown['values'] = list(self.clients.keys())
        else:
            self.clients = {}
            self.client_dropdown['values'] = []

    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get("clients", {}), Path(data.get("base_path", str(DEFAULT_BASE_PATH)))
        return {}, DEFAULT_BASE_PATH

    def save_config(self):
        config = {
            "clients": self.clients,
            "base_path": str(self.base_path)
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def create_folder_structure(self, base_path, structure):
        os.makedirs(base_path, exist_ok=True)
        for item in structure:
            if isinstance(item, str):
                os.makedirs(base_path / item, exist_ok=True)
            elif isinstance(item, dict) and "folders" in item:
                for folder in item["folders"]:
                    os.makedirs(base_path / folder, exist_ok=True)

    def create_project(self):
        project_name = self.project_name.get().strip()
        client_name = self.client_var.get()

        if not project_name:
            messagebox.showerror("Error", "Please enter a project name")
            return

        if not client_name:
            messagebox.showerror("Error", "Please select or add a client name")
            return

        if client_name == "New Client":
            client_name = self.new_client_name.get().strip()
            if not client_name:
                messagebox.showerror("Error", "Please enter a new client name")
                return
            self.clients[client_name] = str(self.base_path / client_name)
            self.client_dropdown['values'] = list(self.clients.keys())
            self.new_client_frame.grid_remove()

        client_path = self.base_path / client_name
        project_path = client_path / project_name

        if project_path.exists():
            messagebox.showerror("Error", f"Project '{project_name}' already exists for client '{client_name}'")
            return

        self.create_folder_structure(project_path, DEFAULT_STRUCTURE["project_root"])

        self.save_config()
        messagebox.showinfo("Success", f"Project '{project_name}' created for client '{client_name}' at {project_path}")
        self.project_name.delete(0, tk.END)
        self.new_client_name.delete(0, tk.END)
        self.client_var.set("")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagerApp(root)
    app.run()