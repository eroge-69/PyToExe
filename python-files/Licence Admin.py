import tkinter as tk
from tkinter import messagebox
import hashlib

SECRET_KEY = "MY_SECRET_KEY_123456"  # کلید خصوصی شما

def generate_license(hwid: str) -> str:
    raw = hwid + SECRET_KEY
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return hashed[:16].upper()

class LicenseGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("License Generator")
        self.root.geometry("450x200")
        self.root.resizable(False, False)
        self.root.configure(bg="#1C1F26")

        tk.Label(root, text="License Generator", font=("Helvetica", 18, "bold"),
                 bg="#1C1F26", fg="#F1C40F").pack(pady=15)

        frame_input = tk.Frame(root, bg="#2C3E50", bd=0, relief="ridge")
        frame_input.pack(pady=10, padx=20, fill="x")
        frame_input.pack_propagate(False)
        frame_input.configure(height=50)

        tk.Label(frame_input, text="Enter User HWID:", font=("Helvetica", 12),
                 bg="#2C3E50", fg="#ECF0F1").pack(anchor="w", padx=10, pady=2)

        # Entry با قابلیت Paste
        self.entry_hwid = tk.Entry(frame_input, font=("Helvetica", 12), bd=0,
                                   bg="#34495E", fg="white", insertbackground="white",
                                   justify="center")
        self.entry_hwid.pack(fill="x", padx=10, pady=5)
        self.entry_hwid.focus_set()  # تمرکز روی فیلد

        # دکمه تولید لایسنس
        tk.Button(root, text="Generate License", font=("Helvetica", 12, "bold"),
                  bg="#27AE60", fg="white", activebackground="#2ECC71", bd=0,
                  command=self.generate_and_copy).pack(pady=15, ipadx=10, ipady=5)

        # کادر نمایش لایسنس
        self.entry_license = tk.Entry(root, font=("Helvetica", 12), state="readonly",
                                      justify="center", bd=0, bg="#34495E", fg="white")
        self.entry_license.pack(padx=20, fill="x", pady=5)

    def generate_and_copy(self):
        hwid = self.entry_hwid.get().strip()
        if not hwid:
            messagebox.showwarning("Warning", "Please enter HWID!")
            return

        license_code = generate_license(hwid)

        self.entry_license.config(state="normal")
        self.entry_license.delete(0, tk.END)
        self.entry_license.insert(0, license_code)
        self.entry_license.config(state="readonly")

        # کپی به کلیپ‌بورد
        self.root.clipboard_clear()
        self.root.clipboard_append(license_code)

        messagebox.showinfo("Success", f"License generated and copied to clipboard:\n{license_code}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseGeneratorApp(root)
    root.mainloop()
