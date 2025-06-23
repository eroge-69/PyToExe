import os
import shutil
import sys
import customtkinter as ctk
from tkinter import messagebox # We still need messagebox for alerts

class ArtTransferApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Art Transfer Wizard")
        self.geometry("600x450")
        self.resizable(False, False) # Prevent resizing for a consistent look

        # Set a modern appearance mode and theme
        ctk.set_appearance_mode("System") # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

        # --- Fonts (mimicking a clean, modern, iOS-like aesthetic) ---
        # Using common sans-serif fonts available on most systems for broad compatibility.
        # 'Segoe UI' (Windows), 'Helvetica Neue' (macOS, if available), 'Arial', 'Roboto'
        self.main_font = ctk.CTkFont(family="Segoe UI", size=15)
        self.header_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.button_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.log_font = ctk.CTkFont(family="Consolas", size=12) # Monospace for log output

        # --- Widgets ---

        # Header
        self.header_label = ctk.CTkLabel(self, text="🎨 Art Transfer Wizard 🚀", font=self.header_font)
        self.header_label.pack(pady=20)

        # Source Folder (Automatically Set)
        self.source_label = ctk.CTkLabel(self, text="Source Folder (Fixed):", font=self.main_font)
        self.source_label.pack(pady=(0, 5), padx=20, anchor="w")

        # The automatically entered source path
        self.source_path_var = ctk.StringVar(value=r"C:\Users\jassm\Downloads\Bearer")
        self.source_entry = ctk.CTkEntry(self, textvariable=self.source_path_var,
                                         width=500, font=self.main_font, state="readonly") # Make it read-only
        self.source_entry.pack(pady=(0, 20), padx=20, fill="x")

        # Destination Folder (Fixed)
        self.destination_label = ctk.CTkLabel(self, text="Destination Folder (Fixed):", font=self.main_font)
        self.destination_label.pack(pady=(0, 5), padx=20, anchor="w")

        # The fixed destination path you provided
        self.fixed_destination_path = r"D:\Android\Pictures\Feem 2018\bearer\moreart"
        self.destination_entry = ctk.CTkEntry(self, textvariable=ctk.StringVar(value=self.fixed_destination_path),
                                              width=500, font=self.main_font, state="readonly") # Make it read-only
        self.destination_entry.pack(pady=(0, 20), padx=20, fill="x")

        # Transfer Button
        self.transfer_button = ctk.CTkButton(self, text="🚀 Transfer All Art! 🚀",
                                             command=self.start_transfer,
                                             font=self.button_font, height=40)
        self.transfer_button.pack(pady=10)

        # Log / Status Display
        self.log_label = ctk.CTkLabel(self, text="Status Log:", font=self.main_font)
        self.log_label.pack(pady=(10, 5), padx=20, anchor="w")

        self.log_textbox = ctk.CTkTextbox(self, width=560, height=120, font=self.log_font, wrap="word")
        self.log_textbox.pack(pady=(0, 20), padx=20)
        self.log_textbox.insert("end", "Welcome! Ready to transfer art from your Bearer folder.\n")
        self.log_textbox.configure(state="disabled") # Make it read-only by default

    def log_message(self, message):
        """Appends a message to the log textbox."""
        self.log_textbox.configure(state="normal") # Enable writing
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end") # Scroll to the end
        self.log_textbox.configure(state="disabled") # Disable writing

    def start_transfer(self):
        """Initiates the file transfer process."""
        source_folder = self.source_path_var.get()
        destination_folder = self.fixed_destination_path

        # Validate source folder existence
        if not os.path.isdir(source_folder):
            messagebox.showerror("Path Error", f"Source folder does not exist: {source_folder}\nPlease ensure the folder is present.")
            self.log_message(f"Error: Source folder not found: {source_folder}")
            return

        # Disable button during transfer to prevent multiple clicks
        self.transfer_button.configure(state="disabled", text="Transferring...")
        self.log_message("\n--- Starting Transfer ---")

        # Perform the actual transfer
        self.perform_transfer(source_folder, destination_folder)

        # Re-enable button after transfer completes
        self.transfer_button.configure(state="normal", text="🚀 Transfer All Art! 🚀")
        self.log_message("--- Transfer Complete! ---")
        messagebox.showinfo("Transfer Complete", "All eligible art files have been transferred!")


    def perform_transfer(self, source_folder, destination_folder):
        """Core logic to move files and folders from source to destination."""
        # Ensure destination folder exists, create if it doesn't
        if not os.path.exists(destination_folder):
            try:
                os.makedirs(destination_folder)
                self.log_message(f"Created destination folder: {destination_folder}")
            except OSError as e:
                self.log_message(f"Error creating destination folder '{destination_folder}': {e}")
                messagebox.showerror("Permission Error", f"Could not create destination folder:\n{e}\nPlease check permissions or create it manually.")
                return

        moved_count = 0
        skipped_count = 0
        error_count = 0

        # Files and extensions to exclude from moving
        # This list ensures the script itself and any other Python/batch files
        # within the 'Bearer' folder are not moved.
        current_script_name = os.path.basename(__file__)
        exclude_files = {current_script_name, current_script_name.replace(".py", ".bat")} # Exclude .py and potential .bat
        exclude_extensions = ['.py', '.bat', '.exe', '.sh', '.dll', '.sys'] # Add other system-related extensions

        items_in_source = os.listdir(source_folder)

        if not items_in_source:
            self.log_message("No files or folders found in the source folder to move.")
            return

        for item_name in items_in_source:
            source_item_path = os.path.join(source_folder, item_name)
            destination_item_path = os.path.join(destination_folder, item_name)

            # Skip excluded items
            if item_name in exclude_files or any(item_name.lower().endswith(ext) for ext in exclude_extensions):
                self.log_message(f"Skipped (excluded type): '{item_name}'")
                continue

            try:
                if os.path.exists(destination_item_path):
                    # If an item with the same name already exists in the destination, skip it.
                    self.log_message(f"Skipped: '{item_name}' already exists in destination.")
                    skipped_count += 1
                else:
                    # Move files or directories
                    shutil.move(source_item_path, destination_item_path)
                    if os.path.isfile(destination_item_path): # Check if it was a file after moving
                        self.log_message(f"Moved file: '{item_name}'")
                    else: # Must have been a directory
                        self.log_message(f"Moved folder: '{item_name}'")
                    moved_count += 1
            except Exception as e:
                self.log_message(f"Error moving '{item_name}': {e}")
                error_count += 1

        self.log_message(f"\nTransfer Summary: Moved {moved_count}, Skipped {skipped_count}, Errors {error_count}")


if __name__ == "__main__":
    # This block tries to prevent the console window from appearing on Windows
    # when the script is double-clicked. This part often requires the 'pywin32' library.
    # The most reliable way to prevent the console is to associate .py files with pythonw.exe.
    if sys.platform == "win32":
        try:
            import win32console
            win32console.FreeConsole()
        except ImportError:
            # win32console is not installed, console might still pop up if launched via python.exe
            pass
        except Exception as e:
            # Catch other potential errors during FreeConsole
            print(f"Warning: Could not free console: {e}") # This message would still appear in console if it pops up

    app = ArtTransferApp()
    app.mainloop()
