import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

class PyInstallerGUI:
    """
    A simple GUI application to compile Python programs into executable files
    using PyInstaller.
    """
    def __init__(self, master):
        """
        Initializes the main window and all its widgets.
        """
        self.master = master
        master.title("Python to EXE Compiler")
        master.geometry("600x400")
        master.configure(bg="#f0f0f0")

        # Set up a clean, modern look using padding and a consistent font
        self.font_large = ('Helvetica', 12)
        self.font_button = ('Helvetica', 12, 'bold')
        self.padding_y = 10
        self.padding_x = 20

        # Title Label
        self.title_label = tk.Label(
            master,
            text="Python to Executable Compiler",
            font=('Helvetica', 16, 'bold'),
            bg="#f0f0f0",
            fg="#333",
            pady=20
        )
        self.title_label.pack()

        # Frame for file selection
        self.frame_file = tk.Frame(master, bg="#f0f0f0")
        self.frame_file.pack(pady=self.padding_y)

        # File path label and entry
        self.path_label = tk.Label(
            self.frame_file,
            text="Select .py File:",
            font=self.font_large,
            bg="#f0f0f0"
        )
        self.path_label.pack(side=tk.LEFT, padx=(0, 10))

        self.file_path_entry = tk.Entry(
            self.frame_file,
            width=50,
            font=self.font_large
        )
        self.file_path_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.browse_button = tk.Button(
            self.frame_file,
            text="Browse",
            command=self.browse_file,
            font=self.font_button,
            bg="#4a90e2",
            fg="white",
            relief=tk.RAISED
        )
        self.browse_button.pack(side=tk.LEFT)

        # Options for compilation
        self.options_frame = tk.Frame(master, bg="#f0f0f0")
        self.options_frame.pack(pady=self.padding_y, padx=self.padding_x, anchor='w')

        self.onefile_var = tk.IntVar()
        self.onefile_check = tk.Checkbutton(
            self.options_frame,
            text="Create a single executable file (--onefile)",
            variable=self.onefile_var,
            font=self.font_large,
            bg="#f0f0f0"
        )
        self.onefile_check.pack(anchor='w')

        self.noconsole_var = tk.IntVar()
        self.noconsole_check = tk.Checkbutton(
            self.options_frame,
            text="Hide console window (--noconsole)",
            variable=self.noconsole_var,
            font=self.font_large,
            bg="#f0f0f0"
        )
        self.noconsole_check.pack(anchor='w')

        # Compile Button
        self.compile_button = tk.Button(
            master,
            text="Compile to EXE",
            command=self.start_compile,
            font=self.font_button,
            bg="#5cb85c",
            fg="white",
            relief=tk.RAISED,
            width=20
        )
        self.compile_button.pack(pady=self.padding_y)

        # Status Label
        self.status_label = tk.Label(
            master,
            text="Status: Ready",
            font=self.font_large,
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=self.padding_y)

    def browse_file(self):
        """
        Opens a file dialog to select a Python file.
        """
        file_path = filedialog.askopenfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py")]
        )
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def start_compile(self):
        """
        Starts the compilation process in a separate thread to prevent the GUI from freezing.
        """
        python_file_path = self.file_path_entry.get()
        if not python_file_path:
            messagebox.showerror("Error", "Please select a Python file first.")
            return

        self.compile_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Compiling...")

        # Run the compilation in a separate thread
        threading.Thread(target=self.compile_program, args=(python_file_path,)).start()

    def compile_program(self, python_file_path):
        """
        Executes the PyInstaller command to compile the Python file.
        """
        try:
            # Construct the PyInstaller command
            command = ["pyinstaller", python_file_path]

            if self.onefile_var.get():
                command.append("--onefile")

            if self.noconsole_var.get():
                command.append("--noconsole")

            # Check for the correct path and file existence
            if not os.path.exists(python_file_path):
                raise FileNotFoundError(f"The file {python_file_path} was not found.")

            # Run the command and capture output
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            # Update status on success
            self.master.after(0, self.on_compile_success, result.stdout)

        except subprocess.CalledProcessError as e:
            # Update status on error
            self.master.after(0, self.on_compile_error, e.stderr)
        except Exception as e:
            # Update status for any other exceptions
            self.master.after(0, self.on_compile_error, str(e))

    def on_compile_success(self, output):
        """
        Handles the successful compilation event.
        """
        self.status_label.config(text="Status: Compilation successful!")
        messagebox.showinfo(
            "Success",
            "The executable was created successfully!\n\nCheck the 'dist' directory for the output file."
        )
        self.compile_button.config(state=tk.NORMAL)

    def on_compile_error(self, error_message):
        """
        Handles the compilation failure event.
        """
        self.status_label.config(text="Status: Compilation failed.")
        messagebox.showerror("Error", f"An error occurred during compilation:\n\n{error_message}")
        self.compile_button.config(state=tk.NORMAL)

def main():
    """
    Main function to create and run the Tkinter application.
    """
    # Check if pyinstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        messagebox.showerror(
            "PyInstaller Not Found",
            "PyInstaller is not installed. Please install it by running:\n\npip install pyinstaller"
        )
        return

    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
