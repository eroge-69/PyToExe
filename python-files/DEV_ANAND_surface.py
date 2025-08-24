import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
import webbrowser


class HexPatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("DEV_ANAND MICROSOFT SURFACE UNLOCKER PRO")
        self.root.geometry("700x500")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        
        # Colors
        self.bg_color = "#2c3e50"
        self.header_color = "#34495e"
        self.button_color = "#3498db"
        self.button_hover = "#2980b9"
        self.success_color = "#2ecc71"
        self.error_color = "#e74c3c"
        self.text_color = "#ecf0f1"
        self.entry_bg = "#34495e"

        # Patch definitions: {id: (offset, ?, new_value)}
        self.patches = {
            16814278: (16814278, None, 60),
            16819842: (16819842, None, 60),
            16821610: (16821610, None, 60),
            16827746: (16827746, None, 60),
            16830478: (16830478, None, 60),
            16830578: (16830578, None, 60),
            16861114: (16861114, None, 60),
            16861234: (16861234, None, 60),
        }

        # Build UI
        self.create_widgets()

    def check_password(self):
        """Check activation key via argv or dialog."""
        if len(sys.argv) > 1:
            entered_key = sys.argv[1]
        else:
            entered_key = simpledialog.askstring(
                "Password Required",
                "Enter the activation key:",
                show="*"
            )

        if entered_key != self.CORRECT_KEY:
            messagebox.showerror("Access Denied", "Invalid key! Program will exit.")
            sys.exit(1)

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.header_color, padx=10, pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="DEV BIOS SOLUTION --- MICROSOFT SURFACE UNLOCKER PRO",
            font=("Helvetica", 16, "bold"),
            bg=self.header_color,
            fg=self.text_color
        ).pack()

        # Content
        content_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # File select
        file_frame = tk.Frame(content_frame, bg=self.bg_color)
        file_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            file_frame,
            text="Select Binary File:",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor="w")

        self.file_path = tk.StringVar()

        entry_frame = tk.Frame(file_frame, bg=self.bg_color)
        entry_frame.pack(fill=tk.X, pady=5)

        tk.Entry(
            entry_frame,
            textvariable=self.file_path,
            width=50,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.text_color,
            insertbackground="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        browse_btn = tk.Button(
            entry_frame,
            text="Browse",
            command=self.browse_file,
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            padx=15
        )
        browse_btn.pack(side=tk.LEFT)

        # Patch button
        patch_btn = tk.Button(
            content_frame,
            text="APPLY 32MB PATCH",
            command=self.patch_file,
            bg=self.success_color,
            fg="white",
            activebackground="#27ae60",
            relief=tk.FLAT,
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10
        )
        patch_btn.pack(pady=20)

        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="",
            fg=self.text_color,
            bg=self.bg_color,
            font=("Arial", 10),
            wraplength=500,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

        # Instructions
        instr_frame = tk.Frame(content_frame, bg="#35495e", padx=10, pady=10)
        instr_frame.pack(fill=tk.X, pady=(20, 0))

        instructions = (
            "Instructions:\n"
            "1. Backup your original BIOS file before patching\n"
            "2. Select the BIOS file using the Browse button\n"
            "3. Click 'APPLY 32MB PATCH' to create a modified version\n"
            "4. Flash the patched BIOS to your device"
        )
        tk.Label(
            instr_frame,
            text=instructions,
            font=("Arial", 12),
            bg="#34495e",
            fg=self.text_color,
            justify=tk.LEFT
        ).pack(anchor="w")

        # Footer
        footer_frame = tk.Frame(self.root, bg=self.header_color, padx=10, pady=10)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        telegram_btn = tk.Button(
            footer_frame,
            text="TELEGRAM: @DEV_ANAND",
            command=lambda: webbrowser.open("https://t.me/Devdader"),
            bg=self.header_color,
            fg=self.text_color,
            activebackground=self.header_color,
            activeforeground=self.text_color,
            relief=tk.FLAT,
            font=("Arial", 9, "underline"),
            cursor="hand2",
            borderwidth=0
        )
        telegram_btn.pack(side=tk.LEFT)

        version_label = tk.Label(
            footer_frame,
            text="v1.0 PRO",
            bg=self.header_color,
            fg=self.text_color,
            font=("Arial", 8)
        )
        version_label.pack(side=tk.RIGHT)

    def browse_file(self):
        filepath = filedialog.askopenfilename(title="Select Binary File")
        if filepath:
            self.file_path.set(filepath)
            self.status_label.config(text="File selected: " + os.path.basename(filepath))

    def patch_file(self):
        filepath = self.file_path.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a file first!")
            return

        try:
            with open(filepath, "rb") as f:
                original_data = bytearray(f.read())

            modified_data = original_data.copy()

            for addr, (offset, _, new_val) in self.patches.items():
                if offset >= len(modified_data):
                    raise ValueError(f"Offset 0x{offset:X} is beyond file size")
                modified_data[offset] = new_val

            base_path, ext = os.path.splitext(filepath)
            new_path = base_path + "_DEV_ANAND_patched" + ext

            with open(new_path, "wb") as f:
                f.write(modified_data)

            self.status_label.config(text=f"File successfully patched and saved as:\n{new_path}")
            messagebox.showinfo("Success", "File patched successfully!")

        except Exception as e:
            self.status_label.config(text="Error: " + str(e))
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HexPatcher(root)
    root.mainloop()
