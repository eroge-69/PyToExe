import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import win32print
import win32ui
import os
import json

TOKEN_FILE = "token_data.json"

class PharmacyTokenSystem:
    def __init__(self, root, on_logout):
        self.root = root
        self.on_logout = on_logout
        self.token_number = self.load_token()
        self.admin_logged_in = True  # Automatically grant admin access

        self.root.title("Pharmacy Token System")
        self.root.geometry("440x380")
        self.root.configure(bg="#e6ffe6")

        self.create_widgets()
        self.update_token_display()
        self.schedule_midnight_reset()

    def create_widgets(self):
        self.hospital_label = tk.Label(self.root, text="Kings Hospital Colombo (PVT) LTD", font=("Helvetica", 14, "bold"), fg="#003366", bg="#e6ffe6")
        self.hospital_label.pack(pady=(5, 0))

        self.address_label = tk.Label(self.root, text="No: 18/A, Evergreen Park Rd,\nColombo 05, Sri Lanka", font=("Helvetica", 12), fg="#333333", bg="#e6ffe6")
        self.address_label.pack()

        self.line_label = tk.Label(self.root, text="────────────────────────────────────────────", font=("Helvetica", 10), bg="#e6ffe6", fg="#003366")
        self.line_label.pack(pady=(0, 10))

        self.token_label = tk.Label(self.root, text="", font=("Helvetica", 32, "bold"), fg="#333333", bg="#e6ffe6")
        self.token_label.pack(pady=(5, 5))

        self.time_label = tk.Label(self.root, text="", font=("Helvetica", 14), fg="#555555", bg="#e6ffe6")
        self.time_label.pack(pady=(0, 10))

        button_frame = tk.Frame(self.root, bg="#e6ffe6")
        button_frame.pack(pady=10)

        self.print_button = tk.Button(button_frame, text="Print Token", font=("Helvetica", 10, "bold"), bg="#12b05e", fg="white", width=16, command=self.print_token)
        self.print_button.pack(side="left", padx=10)

        self.issue_button = tk.Button(button_frame, text="Next Token →", font=("Helvetica", 10, "bold"), bg="#ff7f24", fg="white", width=16, command=self.issue_token)
        self.issue_button.pack(side="left")

        # Admin functions frame
        admin_frame = tk.Frame(self.root, bg="#e6ffe6")
        admin_frame.pack(pady=10)

        self.edit_button = tk.Button(admin_frame, text="Edit Token Number", font=("Helvetica", 10, "bold"), bg="#3399ff", fg="white", width=16, command=self.open_edit_window)
        self.edit_button.pack(side="left", padx=10)

        self.logout_button = tk.Button(admin_frame, text="Exit", font=("Helvetica", 10, "bold"), bg="#cc0000", fg="white", width=16, command=self.logout_user)
        self.logout_button.pack(side="left")

    def update_token_display(self):
        now = datetime.now()
        self.current_date = now.strftime("%Y-%m-%d")
        self.current_time = now.strftime("%H:%M:%S")
        self.token_label.config(text=f"Token Number: G{self.token_number}")
        self.time_label.config(text=f"{self.current_date}\n{self.current_time}")

    def issue_token(self):
        if not self.admin_logged_in:
            messagebox.showwarning("Unauthorized", "Only admin can issue tokens.")
            return
        self.token_number += 1
        self.save_token()
        self.update_token_display()

    def print_token(self):
        try:
            printer_name = win32print.GetDefaultPrinter()
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            hdc.StartDoc("Pharmacy Token")
            hdc.StartPage()

            page_width = 576
            y = 10

            def center_text(hdc, text, font, y_pos):
                hdc.SelectObject(font)
                text_width = hdc.GetTextExtent(text)[0]
                x = (page_width - text_width) // 2
                hdc.TextOut(x, y_pos, text)
                return y_pos + hdc.GetTextExtent(text)[1] + 8

            header_font = win32ui.CreateFont({"name": "Arial", "height": 28, "weight": 700})
            address_font = win32ui.CreateFont({"name": "Arial", "height": 26})
            line_font = win32ui.CreateFont({"name": "Arial", "height": 20})
            token_font = win32ui.CreateFont({"name": "Arial", "height": 100, "weight": 900})
            date_font = win32ui.CreateFont({"name": "Arial", "height": 36})
            footer_font = win32ui.CreateFont({"name": "Arial", "height": 22})

            y = center_text(hdc, "Kings Hospital Colombo (PVT) LTD", header_font, y)
            y = center_text(hdc, "No:18/A, Evergreen Park Rd", address_font, y)
            y = center_text(hdc, "Colombo 05", address_font, y)
            y = center_text(hdc, "Sri Lanka", address_font, y)
            y += 5
            y = center_text(hdc, "------------------------------------------------", line_font, y)

            y += 25
            token_str = f"G00{self.token_number}"
            y = center_text(hdc, token_str, token_font, y)

            y += 30
            y = center_text(hdc, f"DATE : {self.current_date}", date_font, y)
            y = center_text(hdc, f"TIME : {self.current_time}", date_font, y)

            y += 40
            y = center_text(hdc, "©2025 by Kings ICT Dept.", footer_font, y)

            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()

        except Exception as e:
            print(f"Printing failed: {str(e)}")

    def reset_token_number(self):
        self.token_number = 1
        self.save_token()
        self.update_token_display()
        self.schedule_midnight_reset()

    def schedule_midnight_reset(self):
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        ms_until_midnight = int((tomorrow - now).total_seconds() * 1000)
        self.root.after(ms_until_midnight, self.reset_token_number)

    def save_token(self):
        with open(TOKEN_FILE, "w") as f:
            json.dump({"token_number": self.token_number}, f)

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                return data.get("token_number", 1)
        return 1

    def logout_user(self):
        self.root.destroy()

    def open_edit_window(self):
        AdminEditWindow(self.root, self.token_number, self.update_token_from_admin)

    def update_token_from_admin(self, new_token):
        self.token_number = new_token
        self.save_token()
        self.update_token_display()


class AdminEditWindow:
    def __init__(self, master, current_token, on_update):
        self.master = tk.Toplevel(master)
        self.master.title("Edit Token Number")
        self.master.geometry("300x150")
        self.master.configure(bg="#fff")

        self.on_update = on_update

        tk.Label(self.master, text="Current Token Number:").pack(pady=(10, 0))
        self.token_entry = tk.Entry(self.master)
        self.token_entry.insert(0, str(current_token))
        self.token_entry.pack(pady=5)

        tk.Button(self.master, text="Update Token", command=self.update_token).pack(pady=10)

    def update_token(self):
        try:
            new_token = int(self.token_entry.get())
            self.on_update(new_token)
            messagebox.showinfo("Success", "Token number updated successfully!")
            self.master.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid token number")


def main():
    root = tk.Tk()
    app = PharmacyTokenSystem(root, on_logout=main)
    root.mainloop()


if __name__ == "__main__":
    main()
