import subprocess
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

class DriveMapperApp:
    def __init__(self, master):
        self.master = master
        master.title("Network Drive Mapper")
        master.geometry("600x600") # Set initial window size
        master.resizable(True, True) # Allow window resizing

        # Configure grid weights for responsive layout
        master.grid_rowconfigure(0, weight=0)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)
        master.grid_rowconfigure(3, weight=0)
        master.grid_rowconfigure(4, weight=1) # Output area expands
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        # --- Input Frame ---
        input_frame = tk.LabelFrame(master, text="Drive Mapping Details", padx=10, pady=10)
        input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1) # Make entry fields expand

        tk.Label(input_frame, text="Drive Letter (e.g., Z:):").grid(row=0, column=0, sticky="w", pady=2)
        self.drive_letter_entry = tk.Entry(input_frame, width=30)
        self.drive_letter_entry.grid(row=0, column=1, sticky="ew", pady=2)
        self.drive_letter_entry.insert(0, "Z:") # Default value

        tk.Label(input_frame, text="Share Path (e.g., \\\\server\\share):").grid(row=1, column=0, sticky="w", pady=2)
        self.share_path_entry = tk.Entry(input_frame, width=40)
        self.share_path_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(input_frame, text="Username (Optional):").grid(row=2, column=0, sticky="w", pady=2)
        self.username_entry = tk.Entry(input_frame, width=30)
        self.username_entry.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Label(input_frame, text="Password (Optional):").grid(row=3, column=0, sticky="w", pady=2)
        self.password_entry = tk.Entry(input_frame, show="*", width=30) # Mask password input
        self.password_entry.grid(row=3, column=1, sticky="ew", pady=2)

        self.persistent_var = tk.BooleanVar()
        self.persistent_check = tk.Checkbutton(input_frame, text="Make persistent across reboots", variable=self.persistent_var)
        self.persistent_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

        # --- Action Buttons Frame ---
        button_frame = tk.Frame(master, padx=10, pady=5)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)

        self.map_button = tk.Button(button_frame, text="Map Drive", command=self.map_drive_gui, bg="#4CAF50", fg="white", relief="raised", bd=3)
        self.map_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.unmap_button = tk.Button(button_frame, text="Unmap Drive", command=self.unmap_drive_gui, bg="#f44336", fg="white", relief="raised", bd=3)
        self.unmap_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.list_button = tk.Button(button_frame, text="List Mapped Drives", command=self.list_mapped_drives_gui, bg="#2196F3", fg="white", relief="raised", bd=3)
        self.list_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.clear_button = tk.Button(button_frame, text="Clear Output", command=self.clear_output, bg="#FFC107", fg="black", relief="raised", bd=3)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # --- Output Area ---
        tk.Label(master, text="Output:").grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.output_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=70, height=15, bg="#f0f0f0", relief="sunken", bd=2)
        self.output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # --- Exit Button ---
        self.exit_button = tk.Button(master, text="Exit", command=master.quit, bg="#607D8B", fg="white", relief="raised", bd=3)
        self.exit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Initial check for OS
        if os.name != 'nt':
            messagebox.showwarning("OS Not Supported",
                                   "This application is designed for Windows operating systems using the 'net use' command.\n"
                                   "Functionality may be limited or non-existent on other OSes.")
            self.map_button.config(state=tk.DISABLED)
            self.unmap_button.config(state=tk.DISABLED)
            self.list_button.config(state=tk.DISABLED)


    def _run_net_command(self, command_parts, success_message, error_prefix):
        """Helper to run net commands and update GUI."""
        self.clear_output()
        self.output_text.insert(tk.END, f"Executing: {' '.join(command_parts)}\n")
        try:
            # Use shell=True for 'net use' to correctly parse arguments with spaces/quotes if needed,
            # though subprocess.run with list of args is generally safer.
            # For 'net use', it often behaves better with shell=True for complex arguments.
            result = subprocess.run(command_parts, capture_output=True, text=True, check=True, shell=True)
            self.output_text.insert(tk.END, f"{success_message}\n")
            self.output_text.insert(tk.END, "Output:\n" + result.stdout)
            if result.stderr:
                self.output_text.insert(tk.END, "Standard Error (if any):\n" + result.stderr)
            self.output_text.see(tk.END) # Scroll to end
        except subprocess.CalledProcessError as e:
            error_msg = f"{error_prefix}: {e}\n"
            error_msg += "Error Output:\n" + e.stderr
            error_msg += "\nNote: This operation requires the user running the script to have permissions to access the network share."
            messagebox.showerror("Command Error", error_msg)
            self.output_text.insert(tk.END, error_msg)
            self.output_text.see(tk.END)
        except FileNotFoundError:
            error_msg = "Error: 'net' command not found. This script is intended for Windows systems."
            messagebox.showerror("System Error", error_msg)
            self.output_text.insert(tk.END, error_msg)
            self.output_text.see(tk.END)
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            messagebox.showerror("Unexpected Error", error_msg)
            self.output_text.insert(tk.END, error_msg)
            self.output_text.see(tk.END)

    def map_drive_gui(self):
        drive_letter = self.drive_letter_entry.get().strip().upper()
        share_path = self.share_path_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        persistent = self.persistent_var.get()

        if not drive_letter or not share_path:
            messagebox.showwarning("Input Error", "Drive Letter and Share Path are required.")
            return

        if not drive_letter.endswith(':'):
            drive_letter += ':'

        command = ["net", "use", drive_letter, share_path]

        if username and password:
            command.extend([password, "/user:{}".format(username)])
        elif username:
            # If only username is provided, net use will prompt for password
            command.extend(["/user:{}".format(username)])

        if persistent:
            command.append("/persistent:yes")
        else:
            command.append("/persistent:no")

        self._run_net_command(command, f"Drive '{drive_letter}' mapped successfully!", "Error mapping drive")

    def unmap_drive_gui(self):
        drive_letter = self.drive_letter_entry.get().strip().upper()
        if not drive_letter:
            messagebox.showwarning("Input Error", "Drive Letter is required to unmap.")
            return

        if not drive_letter.endswith(':'):
            drive_letter += ':'

        command = ["net", "use", drive_letter, "/delete"]
        self._run_net_command(command, f"Drive '{drive_letter}' unmapped successfully!", "Error unmapping drive")

    def list_mapped_drives_gui(self):
        command = ["net", "use"]
        self._run_net_command(command, "Currently mapped drives listed.", "Error listing drives")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

if __name__ == "__main__":
    if os.name != 'nt':
        # This check is also in __init__ but good to have it early for non-GUI startup
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showwarning("OS Not Supported",
                               "This application is designed for Windows operating systems using the 'net use' command.\n"
                               "Functionality may be limited or non-existent on other OSes.")
        root.destroy()
    else:
        root = tk.Tk()
        app = DriveMapperApp(root)
        root.mainloop()
