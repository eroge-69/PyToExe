import tkinter as tk
from tkinter import messagebox, scrolledtext
from twilio.rest import Client
import pyperclip
import re

class TwilioCanadaBuyer:
    def __init__(self, root):
        self.root = root
        self.root.title("🇨🇦 Twilio Canada Number Buyer - Itzbadhon69")
        self.root.geometry("350x800")
        
        self.dark_mode = False
        self.update_theme_colors()
        
        self.client = None
        self.sid = ""
        self.token = ""
        self.last_purchased_number = None
        self.purchased_numbers = []  # Track purchased numbers
        
        self.create_login_ui()

    def update_theme_colors(self):
        if self.dark_mode:
            self.bg_color = "#2d2d2d"
            self.fg_color = "#ffffff"
            self.frame_bg = "#1e1e1e"
            self.number_frame_bg = "#333333"
            self.purchased_frame_bg = "#2e3e2e"
            self.button_bg = "#3e3e3e"
            self.text_bg = "#252525"
        else:
            self.bg_color = "#e6f2ff"
            self.fg_color = "#000000"
            self.frame_bg = "#f0f8ff"
            self.number_frame_bg = "#ffffff"
            self.purchased_frame_bg = "#e8f5e9"
            self.button_bg = "#f0f0f0"
            self.text_bg = "#f9f9f9"

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_theme_colors()
        self.apply_theme()

    def apply_theme(self):
        self.root.config(bg=self.bg_color)
        for widget in self.root.winfo_children():
            self.update_widget_theme(widget)

    def update_widget_theme(self, widget):
        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.config(bg=self.frame_bg if "result" not in str(widget) else self.bg_color)
        elif isinstance(widget, (tk.Label, tk.Button, tk.Entry)):
            widget.config(bg=self.button_bg if isinstance(widget, tk.Button) else self.bg_color, 
                         fg=self.fg_color)
        elif isinstance(widget, scrolledtext.ScrolledText):
            widget.config(bg=self.text_bg, fg=self.fg_color)
        
        for child in widget.winfo_children():
            self.update_widget_theme(child)

    def create_login_ui(self):
        self.clear_window()
        
        dark_mode_btn = tk.Button(self.root, text="🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode",
                                command=self.toggle_dark_mode, font=("Arial", 10))
        dark_mode_btn.pack(anchor="ne", padx=10, pady=5)

        tk.Label(self.root, text="Twilio SID:", font=("Arial", 12, "bold")).pack(pady=5)
        self.sid_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        self.sid_entry.pack(pady=5)

        tk.Label(self.root, text="Auth Token:", font=("Arial", 12, "bold")).pack(pady=5)
        self.token_entry = tk.Entry(self.root, width=40, show="*", font=("Arial", 12))
        self.token_entry.pack(pady=5)

        tk.Button(self.root, text="Login", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                command=self.login).pack(pady=10)

        self.status_label = tk.Label(self.root, text="", fg="red", font=("Arial", 10, "bold"))
        self.status_label.pack()

        self.watermark = tk.Label(self.root, text="Created by @Itzbadhon69 (Telegram)", 
                                font=("Arial", 10, "bold"), fg="purple")
        self.watermark.pack(side="bottom", pady=5)
        
        self.apply_theme()

    def login(self):
        self.sid = self.sid_entry.get().strip()
        self.token = self.token_entry.get().strip()
        try:
            self.client = Client(self.sid, self.token)
            self.status_label.config(text="✅ Logged in successfully!", fg="green")
            self.show_search_ui()
        except Exception:
            self.status_label.config(text="❌ Invalid SID or Token", fg="red")

    def show_search_ui(self):
        self.clear_window()
        
        # Dark mode toggle
        dark_mode_btn = tk.Button(self.root, text="🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode",
                                command=self.toggle_dark_mode, font=("Arial", 10))
        dark_mode_btn.pack(anchor="ne", padx=10, pady=5)

        # Logout button
        logout_btn = tk.Button(self.root, text="🚪 Logout", bg="#f44336", fg="white",
                               font=("Arial", 10, "bold"), command=self.logout)
        logout_btn.pack(anchor="nw", padx=10, pady=5)

        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(self.result_frame, text="Enter Prefix (e.g., 778475):", font=("Arial", 12, "bold")).pack(pady=5)
        self.prefix_entry = tk.Entry(self.result_frame, width=20, font=("Arial", 12))
        self.prefix_entry.pack(pady=5)

        tk.Button(self.result_frame, text="Search Available Canada Numbers", bg="#2196F3", fg="white", 
                font=("Arial", 12, "bold"), command=self.search_numbers).pack(pady=10)

        tk.Button(self.result_frame, text="📥 Purchase Like Before", bg="#9C27B0", fg="white", 
                font=("Arial", 12, "bold"), command=self.purchase_like_before).pack(pady=5)

        # Custom Number Input
        tk.Label(self.result_frame, text="Enter Custom Number (e.g. +18259047869):", font=("Arial", 12, "bold")).pack(pady=5)
        self.custom_number_entry = tk.Entry(self.result_frame, width=25, font=("Arial", 12))
        self.custom_number_entry.pack(pady=5)
        tk.Button(self.result_frame, text="Try to Buy Custom Number", bg="#FF5722", fg="white", 
                font=("Arial", 12, "bold"), command=self.try_buy_custom_number).pack(pady=5)

        # Sequential Number Search
        tk.Label(self.result_frame, text="Enter Base Number to Search Sequence:", font=("Arial", 12, "bold")).pack(pady=5)
        self.sequential_base_entry = tk.Entry(self.result_frame, width=25, font=("Arial", 12))
        self.sequential_base_entry.pack(pady=5)
        tk.Button(self.result_frame, text="Search Sequential Numbers", bg="#3F51B5", fg="white", 
                font=("Arial", 12, "bold"), command=self.search_sequential_numbers).pack(pady=5)

        # Scrollable frame
        self.canvas = tk.Canvas(self.result_frame, bg=self.bg_color)
        self.scrollbar = tk.Scrollbar(self.result_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        self.watermark = tk.Label(self.root, text="Created by @Itzbadhon69 (Telegram)", 
                                font=("Arial", 10, "bold"), fg="purple")
        self.watermark.pack(side="bottom", pady=5)
        
        self.apply_theme()

    def logout(self):
        self.client = None
        self.sid = ""
        self.token = ""
        self.last_purchased_number = None
        self.purchased_numbers = []
        self.create_login_ui()

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def search_numbers(self):
        prefix = self.prefix_entry.get().strip()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            numbers = self.client.available_phone_numbers("CA").local.list(
                contains=prefix,
                sms_enabled=True,
                limit=6 # limit can be increased
            )
            if not numbers:
                tk.Label(self.scrollable_frame, text="❌ No numbers found.", font=("Arial", 12)).pack()
                return

            for number in numbers:
                self.display_number(number.phone_number)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch numbers:\n{e}")

    def search_sequential_numbers(self):
        base_number = self.sequential_base_entry.get().strip()
        if not re.match(r'^\+\d+$', base_number):
            messagebox.showerror("Invalid Input", "Please enter a valid number starting with +")
            return

        base = base_number[:-4]
        try:
            start = int(base_number[-4:])
        except ValueError:
            messagebox.showerror("Error", "Last 4 digits must be numeric.")
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        found_count = 0
        current_suffix = start
        max_to_find = 10
        max_attempts = 50

        while found_count < max_to_find and current_suffix < start + max_attempts:
            candidate = f"{base}{current_suffix:04d}"
            try:
                numbers = self.client.available_phone_numbers("CA").local.list(
                    contains=candidate,
                    sms_enabled=True,
                    limit=1
                )
                for number in numbers:
                    if number.phone_number == candidate:
                        self.display_number(number.phone_number)
                        found_count += 1
                        break
            except Exception:
                pass
            current_suffix += 1

        if found_count == 0:
            tk.Label(self.scrollable_frame, text="❌ No sequential numbers found.", font=("Arial", 12),
                     bg=self.frame_bg, fg=self.fg_color).pack()
        elif found_count < max_to_find:
            tk.Label(self.scrollable_frame, text=f"⚠️ Only found {found_count} numbers.", font=("Arial", 12),
                     bg=self.frame_bg, fg=self.fg_color).pack()

    def display_number(self, number):
        frame = tk.Frame(self.scrollable_frame, bg=self.number_frame_bg, bd=1, relief="solid")
        frame.pack(fill="x", pady=5, padx=10)

        tk.Label(frame, text=number, font=("Arial", 12, "bold"), 
                bg=self.number_frame_bg, fg=self.fg_color).pack(side="left", padx=10)

        tk.Button(frame, text="Hide", bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"),
                command=lambda f=frame: f.destroy()).pack(side="right", padx=5)

        tk.Button(frame, text="Copy", bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                command=lambda n=number: pyperclip.copy(n)).pack(side="right", padx=5)

        tk.Button(frame, text="Buy", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                command=lambda n=number, f=frame: self.buy_number(n, f)).pack(side="right", padx=5)

    def buy_number(self, number, frame):
        try:
            purchased = self.client.incoming_phone_numbers.create(phone_number=number)
            self.last_purchased_number = purchased.phone_number
            self.purchased_numbers.insert(0, (purchased.phone_number, purchased.sid))
            pyperclip.copy(purchased.phone_number)
            messagebox.showinfo("Success", f"✅ Number purchased and copied to clipboard:\n{purchased.phone_number}")
            frame.destroy()
            self.display_purchased_number(purchased.phone_number, purchased.sid)
        except Exception as e:
            messagebox.showerror("Buy Failed", f"❌ Could not buy number:\n{e}")

    def display_purchased_number(self, number, sid):
        frame = tk.Frame(self.scrollable_frame, bg=self.purchased_frame_bg, bd=1, relief="solid")
        if self.scrollable_frame.winfo_children():
            frame.pack(fill="x", pady=5, padx=10, before=self.scrollable_frame.winfo_children()[0])
        else:
            frame.pack(fill="x", pady=5, padx=10)

        tk.Label(frame, text=number, font=("Arial", 12, "bold"), 
                bg=self.purchased_frame_bg, fg=self.fg_color).pack(side="left", padx=10)

        tk.Button(frame, text="Hide", bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"),
                command=lambda f=frame: f.destroy()).pack(side="right", padx=5)

        tk.Button(frame, text="Copy", bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                command=lambda: pyperclip.copy(number)).pack(side="right", padx=5)

        tk.Button(frame, text="Release", bg="#e53935", fg="white", font=("Arial", 10, "bold"),
                command=lambda sid=sid, f=frame: self.release_number(sid, f)).pack(side="right", padx=5)

        tk.Button(frame, text="Show Logs", bg="#3949ab", fg="white", font=("Arial", 10, "bold"),
                command=lambda sid=sid: self.show_logs(sid)).pack(side="right", padx=5)

    def release_number(self, sid, frame):
        try:
            self.client.incoming_phone_numbers(sid).delete()
            frame.destroy()
            messagebox.showinfo("Released", "✅ Number released successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to release number:\n{e}")

    def show_logs(self, sid):
        try:
            number_obj = self.client.incoming_phone_numbers(sid).fetch()
            phone_number = number_obj.phone_number
            messages = self.client.messages.list(to=phone_number, limit=50)

            verification_code = None
            if messages:
                for msg in messages:
                    code_match = re.search(r'(\d{3}-\d{3})', msg.body)
                    if code_match:
                        verification_code = code_match.group(1)
                        break

            if verification_code:
                pyperclip.copy(verification_code)
                self.show_toast(f"Copied code: {verification_code}")
            else:
                self.show_toast("No verification code found in messages")

        except Exception:
            self.show_toast("Error: Could not check logs")

    def purchase_like_before(self):
        if not self.last_purchased_number:
            messagebox.showinfo("Info", "No previously purchased number found.")
            return

        base = self.last_purchased_number[:-4]
        start_suffix = int(self.last_purchased_number[-4:])
        bought_any = False

        for suffix in range(start_suffix + 1, start_suffix + 10):
            new_number = f"{base}{suffix:04d}"
            try:
                purchased = self.client.incoming_phone_numbers.create(phone_number=new_number)
                self.last_purchased_number = purchased.phone_number
                self.purchased_numbers.insert(0, (purchased.phone_number, purchased.sid))
                pyperclip.copy(purchased.phone_number)
                messagebox.showinfo("Success", f"✅ Number purchased and copied to clipboard:\n{purchased.phone_number}")
                self.display_purchased_number(purchased.phone_number, purchased.sid)
                bought_any = True
                break
            except Exception:
                continue

        if not bought_any:
            messagebox.showinfo("Info", "Could not purchase similar number.")

    def try_buy_custom_number(self):
        custom_number = self.custom_number_entry.get().strip()
        if not custom_number:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        try:
            purchased = self.client.incoming_phone_numbers.create(phone_number=custom_number)
            self.last_purchased_number = purchased.phone_number
            self.purchased_numbers.insert(0, (purchased.phone_number, purchased.sid))
            pyperclip.copy(purchased.phone_number)
            messagebox.showinfo("Success", f"✅ Custom Number purchased and copied to clipboard:\n{purchased.phone_number}")
            self.display_purchased_number(purchased.phone_number, purchased.sid)
        except Exception as e:
            messagebox.showerror("Unavailable", f"❌ Could not buy number:\n{e}")

    def show_toast(self, message):
        toast = tk.Toplevel(self.root)
        toast.geometry("300x60+{}+{}".format(
            self.root.winfo_x() + 200,
            self.root.winfo_y() + 50
        ))
        toast.overrideredirect(1)
        toast.config(bg="#4CAF50")
        tk.Label(toast, text=message, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=15)
        toast.after(1000, toast.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = TwilioCanadaBuyer(root)
    root.mainloop()
