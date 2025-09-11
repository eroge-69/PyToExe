"code-keyword">import tkinter "code-keyword">as tk
"code-keyword">from tkinter "code-keyword">import filedialog, messagebox, ttk
"code-keyword">import openpyxl
"code-keyword">import face_recognition
"code-keyword">import os
"code-keyword">import shutil
"code-keyword">import json
"code-keyword">import subprocess  # For opening files (cross-platform)
"code-keyword">import pystray
"code-keyword">from pystray "code-keyword">import MenuItem "code-keyword">as item
"code-keyword">from PIL "code-keyword">import Image "code-keyword">as PILImage
"code-keyword">from cryptography.fernet "code-keyword">import Fernet
"code-keyword">import logging
"code-keyword">import datetime

# Configure logging
logging.basicConfig(filename='automation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

"code-keyword">class AutomationApp:
    "code-keyword">class="code-keyword">def __init__(self, root):
        self.root = root
        self.root.title("Automation App")
        self.root.geometry("800x600")

        self.excel_path = tk.StringVar()
        self.image_dir = tk.StringVar()
        self.consent_dir = tk.StringVar()
        self.known_faces_dir = tk.StringVar()
        self.encryption_key = None
        self.known_face_encodings = []
        self.known_face_names = []
        self.config_file = "config.json"  # Configuration file path

        # Dark Theme
        self.root.tk.call("source", "azure.tcl")
        self.root.tk.call("set_theme", "dark")
        self.style = ttk.Style(root)

        # GUI Components
        self.setup_ui()

        # Load Configuration
        self.load_configuration()

        # Load Known Faces
        self.load_known_faces()

        # System Tray Icon
        self.create_system_tray_icon()

        # Auto-Save
        self.root.after(60000, self.auto_save)  # Auto-save every 60 seconds

    "code-keyword">class="code-keyword">def setup_ui(self):
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(settings_frame, text="Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        excel_entry = ttk.Entry(settings_frame, textvariable=self.excel_path, width=50)
        excel_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(settings_frame, text="Browse", command=self.browse_excel).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Image Directory:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        image_entry = ttk.Entry(settings_frame, textvariable=self.image_dir, width=50)
        image_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(settings_frame, text="Browse", command=self.browse_image_dir).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Consent Form Directory:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        consent_entry = ttk.Entry(settings_frame, textvariable=self.consent_dir, width=50)
        consent_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(settings_frame, text="Browse", command=self.browse_consent_dir).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Known Faces Directory:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        known_faces_entry = ttk.Entry(settings_frame, textvariable=self.known_faces_dir, width=50)
        known_faces_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(settings_frame, text="Browse", command=self.browse_known_faces_dir).grid(row=3, column=2, padx=5, pady=5)

        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(padx=10, pady=10)

        self.run_button = ttk.Button(button_frame, text="Run Face Recognition", command=self.run_face_recognition)
        self.run_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(button_frame, text="Save Settings", command=self.save_configuration)
        save_button.pack(side=tk.LEFT, padx=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Status Label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=5)

        # Excel Data (Placeholder - replace "code-keyword">with actual display)
        self.excel_data_text = tk.Text(self.root, height=10, width=80)
        self.excel_data_text.pack(padx=10, pady=10)
        self.excel_data_text.insert(tk.END, "Excel data will be displayed here.")
        self.excel_data_text.config(state=tk.DISABLED)

    "code-keyword">class="code-keyword">def browse_excel(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        "code-keyword">if filename:
            self.excel_path.set(filename)

    "code-keyword">class="code-keyword">def browse_image_dir(self):
        dirname = filedialog.askdirectory()
        "code-keyword">if dirname:
            self.image_dir.set(dirname)

    "code-keyword">class="code-keyword">def browse_consent_dir(self):
        dirname = filedialog.askdirectory()
        "code-keyword">if dirname:
            self.consent_dir.set(dirname)

    "code-keyword">class="code-keyword">def browse_known_faces_dir(self):
        dirname = filedialog.askdirectory()
        "code-keyword">if dirname:
            self.known_faces_dir.set(dirname)
            self.load_known_faces()  # Reload known faces after changing directory

    "code-keyword">class="code-keyword">def load_known_faces(self):
        self.known_face_encodings = []
        self.known_face_names = []
        known_faces_dir = self.known_faces_dir.get()

        "code-keyword">if "code-keyword">not known_faces_dir:
            self.status_label.config(text="Known faces directory ">not set.")
            "code-keyword">return

        "code-keyword">try:
            "code-keyword">for filename "code-keyword">in os.listdir(known_faces_dir):
                "code-keyword">if filename.endswith(".jpg") "code-keyword">or filename.endswith(".jpeg") "code-keyword">or filename.endswith(".png"):
                    image_path = os.path.join(known_faces_dir, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)

                    "code-keyword">if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        # Extract name "code-keyword">from filename (e.g., "John_Doe.jpg" -> "John Doe")
                        name = os.path.splitext(filename)[0].replace("_", " ")
                        self.known_face_names.append(name)
                    "code-keyword">else:
                        logging.warning(f"No faces found ">in {filename}")

            self.status_label.config(text=f"Loaded {len(self.known_face_names)} known faces.")
            logging.info(f"Loaded {len(self.known_face_names)} known faces.")

        "code-keyword">except Exception "code-keyword">as e:
            self.status_label.config(text=f"Error loading known faces: {e}")
            logging.exception("Error loading known faces")

    "code-keyword">class="code-keyword">def run_face_recognition(self):
        excel_path = self.excel_path.get()
        image_dir = self.image_dir.get()
        consent_dir = self.consent_dir.get()

        "code-keyword">if "code-keyword">not (excel_path "code-keyword">and image_dir "code-keyword">and consent_dir "code-keyword">and self.known_face_encodings):
            messagebox.showerror("Error", "Please set Excel path, image directory, consent form directory, ">and load known faces.")
            "code-keyword">return

        "code-keyword">try:
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active  # Or specify the sheet name

            total_rows = sheet.max_row
            self.progress_bar["maximum"] = total_rows - 1 # Assuming first row "code-keyword">is header

            # Define columns (make sure these exist "code-keyword">in your Excel)
            image_filename_column = 1 #Column A
            person_name_column = 2 # Column B
            consent_form_column = 3 # Column C

            "code-keyword">for row_num "code-keyword">in range(2, total_rows + 1): # Start "code-keyword">from row 2 (assuming row 1 "code-keyword">is header)
                self.progress_bar["value"] = row_num - 1
                self.root.update_idletasks() # Update GUI to show progress

                image_filename = sheet.cell(row=row_num, column=image_filename_column).value
                "code-keyword">if "code-keyword">not image_filename:
                    continue

                # Skip "code-keyword">if person name "code-keyword">is already filled
                person_name = sheet.cell(row=row_num, column=person_name_column).value
                "code-keyword">if person_name:
                    continue

                image_path = os.path.join(image_dir, image_filename)

                "code-keyword">try:
                    image = face_recognition.load_image_file(image_path)
                    face_locations = face_recognition.face_locations(image)
                    face_encodings = face_recognition.face_encodings(image, face_locations)

                    "code-keyword">if "code-keyword">not face_encodings:
                        self.status_label.config(text=f"No faces found ">in {image_filename}")
                        logging.warning(f"No faces found ">in {image_filename}")
                        continue

                    # In case of multiple faces, take the first one
                    face_encoding = face_encodings[0]
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    "code-keyword">if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        sheet.cell(row=row_num, column=person_name_column).value = name

                        # Link Consent Form
                        consent_filename = f"{name.replace(' ', '.')}.pdf" #E.g. 'John.Doe.pdf'
                        consent_path = os.path.join(consent_dir, consent_filename)
                        "code-keyword">if os.path.exists(consent_path):
                            sheet.cell(row=row_num, column=consent_form_column).value = consent_path
                        "code-keyword">else:
                             logging.warning(f"Consent form ">not found: {consent_filename}")

                        self.status_label.config(text=f"Identified {name} ">in {image_filename}")
                        logging.info(f"Identified {name} ">in {image_filename}")
                    "code-keyword">else:
                         self.status_label.config(text=f"Unknown person ">in {image_filename}")
                         logging.warning(f"Unknown person ">in {image_filename}")

                "code-keyword">except FileNotFoundError:
                    self.status_label.config(text=f"Image ">not found: {image_path}")
                    logging.error(f"Image ">not found: {image_path}")
                "code-keyword">except Exception "code-keyword">as e:
                    self.status_label.config(text=f"Error processing {image_filename}: {e}")
                    logging.exception(f"Error processing {image_filename}")

            workbook.save(excel_path)
            self.status_label.config(text="Face recognition complete.")
            logging.info("Face recognition complete.")

        "code-keyword">except FileNotFoundError:
            messagebox.showerror("Error", "Excel file ">not found.")
        "code-keyword">except Exception "code-keyword">as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.exception("An error occurred")
        finally:
            self.progress_bar["value"] = 0

    "code-keyword">class="code-keyword">def save_configuration(self):
         config = {
            "excel_path": self.excel_path.get(),
            "image_dir": self.image_dir.get(),
            "consent_dir": self.consent_dir.get(),
            "known_faces_dir": self.known_faces_dir.get()
        }

        "code-keyword">try:
            # Generate encryption key "code-keyword">if it doesn't exist
            if self.encryption_key is None:
                self.encryption_key = Fernet.generate_key()
            fernet = Fernet(self.encryption_key)

            # Encrypt sensitive data
            encrypted_config = {}
            for key, value in config.items():
                if value:  # Only encrypt if the value is not empty
                    encrypted_config[key] = fernet.encrypt(value.encode()).decode()
                else:
                    encrypted_config[key] = ""  # Store as empty string if the value is empty

            # Save key and encrypted config
            data = {
                "encryption_key": self.encryption_key.decode(),
                "config": encrypted_config
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f)

            self.status_label.config(text="Settings saved successfully.")
            logging.info("Settings saved successfully.")

        except Exception as e:
            self.status_label.config(text=f"Error saving settings: {e}")
            logging.exception("Error saving settings")

    class="code-keyword">def load_configuration(self):
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.encryption_key = data.get("encryption_key").encode() if data.get("encryption_key") else None
                encrypted_config = data.get("config", {})

                if self.encryption_key:
                    fernet = Fernet(self.encryption_key)
                    config = {}
                    for key, value in encrypted_config.items():
                         if value:
                            config[key] = fernet.decrypt(value.encode()).decode()
                         else:
                            config[key] = ""
                    self.excel_path.set(config.get("excel_path", ""))
                    self.image_dir.set(config.get("image_dir", ""))
                    self.consent_dir.set(config.get("consent_dir", ""))
                    self.known_faces_dir.set(config.get("known_faces_dir", ""))

                self.status_label.config(text="Settings loaded successfully.")
                logging.info("Settings loaded successfully.")
        except FileNotFoundError:
            self.status_label.config(text="No configuration file found. Using default settings.")
            logging.info("No configuration file found. Using default settings.")
        except Exception as e:
            self.status_label.config(text=f"Error loading settings: {e}")
            logging.exception("Error loading settings")

    class="code-keyword">def auto_save(self):
        self.save_configuration()
        self.status_label.config(text=f"Auto-saved configuration at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Auto-saved configuration at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.root.after(60000, self.auto_save)  # Reschedule auto-save


    class="code-keyword">def open_file(self, filepath):
        try:
            if os.path.exists(filepath):
                if os.name == 'nt':  # Windows
                    os.startfile(filepath)
                else:  # macOS and Linux
                    subprocess.Popen(['open', filepath])  # Use 'xdg-open' on Linux
            else:
                messagebox.showerror("Error", "File not found: " + filepath)
                logging.error(f"File not found: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            logging.exception(f"Could not open file: {e}")


    class="code-keyword">def create_system_tray_icon(self):
        image = PILImage.open("icon.png")  # Replace "icon.png" with your icon file
        menu = pystray.Menu(
            item('Open', self.show_window),
            item('Run Face Recognition', self.run_face_recognition),
            item('Exit', self.exit_action)
        )
        self.icon = pystray.Icon("Automation App", image, "Automation App", menu)
        self.icon.run_detached()

    "code-keyword">class="code-keyword">def show_window(self):
        self.root.deiconify()

    "code-keyword">class="code-keyword">def exit_action(self):
        self.icon.stop()
        self.root.destroy()

    "code-keyword">class="code-keyword">def on_closing(self):
        self.root.withdraw()  # Hide the window
        messagebox.showinfo("Automation App", "Running ">in the system tray.  Right-click the icon to open ">or exit.")


# --- Main Execution ---
"code-keyword">if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    "code-keyword">import numpy "code-keyword">as np # added to prevent error "code-keyword">in function  face_recognition()
    root.mainloop()