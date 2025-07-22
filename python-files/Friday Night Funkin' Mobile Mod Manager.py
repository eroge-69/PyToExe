"code-keyword">import tkinter "code-keyword">as tk
"code-keyword">from tkinter "code-keyword">import filedialog, messagebox, ttk  # Import ttk "code-keyword">for themed widgets
"code-keyword">import os
"code-keyword">import shutil
"code-keyword">import zipfile
"code-keyword">import subprocess  # For running ADB commands

"code-keyword">class ModManager:
    "code-keyword">class="code-keyword">def __init__(self, master):
        self.master = master
        master.title("Friday Night Funkin' Mobile Mod Manager")

        # --- Dark Theme (Simple Implementation) ---
        self.bg_color = "#2e2e2e"
        self.fg_color = "white"
        master.configure(bg=self.bg_color)

        # Style "code-keyword">for themed widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')  # "code-keyword">or 'alt', 'default', 'classic'
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', padding=6)

        # --- UI Elements ---
        self.upload_button = ttk.Button(master, text="Upload Mod .zip File", command=self.upload_mod)
        self.upload_button.pack(pady=20)

        self.status_label = tk.Label(master, text="Ready", bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack()

    "code-keyword">class="code-keyword">def upload_mod(self):
        """Handles the mod upload process."""
        filename = filedialog.askopenfilename(title="Select Mod .zip File", filetypes=[("Zip files", "*.zip")])

        "code-keyword">if filename:
            "code-keyword">try:
                self.status_label.config(text="Uploading...")
                self.process_mod(filename)
                self.status_label.config(text="Upload Complete!")
                messagebox.showinfo("Success", "Mod uploaded successfully!")

            "code-keyword">except Exception "code-keyword">as e:
                self.status_label.config(text=f"Error: {e}")
                messagebox.showerror("Error", str(e))


    "code-keyword">class="code-keyword">def process_mod(self, zip_file_path):
        """Extracts, finds target directory, ">and moves the mod."""

        # 1. Extract the ZIP file
        extract_path = os.path.splitext(zip_file_path)[0]  # Extract to a folder "code-keyword">with the same name "code-keyword">as the zip
        "code-keyword">with zipfile.ZipFile(zip_file_path, 'r') "code-keyword">as zip_ref:
            zip_ref.extractall(extract_path)

        # 2. Find the extracted mod folder (assuming it's the only folder directly under the extract_path)
        extracted_folder = None
        for item in os.listdir(extract_path):
            item_path = os.path.join(extract_path, item)
            if os.path.isdir(item_path):
                extracted_folder = item_path
                break  # Assuming only one top-level folder

        if not extracted_folder:
            raise ValueError("Could not find the extracted mod folder.")

        # 3. Target directory on the Android device
        target_dir = "Android/obb/me.funkin.fnf/mods"

        # 4. Check if the device is connected (very basic check)
        if not self.is_device_connected():
            raise ValueError("No Android device detected. Please connect your device via USB and enable USB debugging.")

        # 5. Check if the target directory exists (using ADB)
        if not self.directory_exists_on_device(target_dir):
            raise ValueError("Could not find directory. Install the game, and make sure USB debugging is on.")

        # 6. Push the extracted folder to the device using ADB
        self.push_folder_to_device(extracted_folder, target_dir)


    class="code-keyword">def is_device_connected(self):
        """Checks if an Android device is connected via ADB."""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            output = result.stdout
            # Check for device listed in adb devices output
            return "device" in output and len(output.splitlines()) > 1 # Make sure the list isn't just the header
        "code-keyword">except subprocess.CalledProcessError "code-keyword">as e:
            print(f"ADB Error: {e}")
            "code-keyword">return False


    "code-keyword">class="code-keyword">def directory_exists_on_device(self, remote_path):
        """Checks ">if a directory exists on the Android device using ADB."""
        "code-keyword">try:
            result = subprocess.run(["adb", "shell", "ls", remote_path], capture_output=True, text=True)
            # If the command returns an error (e.g., "No such file ">or directory"), it doesn't exist
            return result.returncode == 0  # Success = directory exists
        except subprocess.CalledProcessError as e:
            print(f"ADB Error: {e}")  # Log the error
            return False  # Assume directory doesn't exist on error

    "code-keyword">class="code-keyword">def push_folder_to_device(self, local_path, remote_path):
        """Pushes a folder to the Android device using ADB."""

        #Need to get device id first
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        output = result.stdout
        device_id = output.splitlines()[1].split()[0]

        "code-keyword">try:
            command = ["adb", "-s", device_id, "push", local_path, remote_path]
            print(f"Running ADB command: {' '.join(command)}")  # Debugging
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"ADB Output: {result.stdout}")  # Debugging
        "code-keyword">except subprocess.CalledProcessError "code-keyword">as e:
            print(f"ADB Error: {e.stderr}")
            raise ValueError(f"Failed to push folder to device: {e.stderr}")


root = tk.Tk()
app = ModManager(root)
root.mainloop()