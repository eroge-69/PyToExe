import tkinter as tk
from tkinter import ttk

class UserFormApp:
    """A user information form built with Tkinter, dark/modern style + fake long process."""

    def __init__(self, root):
        self.root = root
        self.root.title("Generator")
        self.root.geometry("650x750")
        self.root.resizable(False, False)

        # --- Dark theme colors ---
        style = ttk.Style()
        style.theme_use("clam")

        background_color = "#1e1e1e"
        panel_color = "#2c2c2c"
        border_color = "#00a359"
        text_color = "#e0e0e0"
        title_color = "#00a359"
        entry_bg_color = "#3a3a3a"
        button_active_color = "#008a4c"

        style.configure("TFrame", background=background_color)
        style.configure("TLabel", background=panel_color, foreground=text_color, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground=title_color, padding=(0, 15, 0, 10))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground=text_color, padding=(0, 0, 0, 15))
        style.configure("TButton", font=("Segoe UI", 12, "bold"), background=border_color, foreground="white", padding=10)
        style.map("TButton", background=[('active', button_active_color)])
        style.configure("TLabelFrame", background=panel_color, borderwidth=2, relief="solid", bordercolor=border_color)
        style.configure("TLabelFrame.Label", background=panel_color, foreground=text_color, font=("Segoe UI", 12, "bold"))
        style.configure("TEntry", fieldbackground=entry_bg_color, foreground=text_color, font=("Segoe UI", 10))

        # --- Main frame ---
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill="both")

        # --- Header ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x")
        title_label = ttk.Label(header_frame, text="GENERATOR", style="Title.TLabel", background=background_color)
        title_label.pack()
        subtitle_label = ttk.Label(header_frame, text=" INTERFACE", style="Subtitle.TLabel", background=background_color)
        subtitle_label.pack()

        # --- Two-column content area ---
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # Left panel
        left_panel = ttk.LabelFrame(content_frame, text=" USER INFO", padding="15 15")
        left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.first_name = self.create_input(left_panel, "First Name:", 0)
        self.middle_name = self.create_input(left_panel, "Middle Name:", 1)
        self.last_name = self.create_input(left_panel, "Last Name:", 2)
        self.dob = self.create_input(left_panel, "Date of Birth:", 3)
        self.ssn_cpn = self.create_input(left_panel, "SSN/CPN Number:", 4)
        left_panel.columnconfigure(1, weight=1)

        # Right panel
        right_panel = ttk.LabelFrame(content_frame, text=" CONTACT INFO", padding="15 15")
        right_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.address = self.create_input(right_panel, "Address:", 0)
        self.email = self.create_input(right_panel, "Email Address:", 1)
        self.phone_number = self.create_input(right_panel, "Phone Number:", 2)
        right_panel.columnconfigure(1, weight=1)

        # --- Log + Status ---
        status_panel = ttk.LabelFrame(main_frame, text=" SYSTEM STATUS", padding="15 15")
        status_panel.pack(fill="x", pady=10)

        self.log_text = tk.Text(status_panel, height=6, state='disabled',
                                bg="#111111", fg="#00ff00",
                                font=("Consolas", 9), relief=tk.FLAT, borderwidth=0)
        self.log_text.pack(fill="x", pady=(0, 10))

        # Progress bar
        self.progress = ttk.Progressbar(status_panel, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        # --- Big bottom button ---
        self.submit_button = ttk.Button(
            main_frame, text="⚡ GENERATE ⚡",
            style="TButton", command=self.handle_button_click
        )
        self.submit_button.pack(pady=(20, 5), fill="x", ipady=10)

        # --- Footer ---
        footer_label = ttk.Label(main_frame, text="Created by @CPNPROFITS", 
                                 background=background_color, foreground="#00a359", font=("Segoe UI", 10, "italic"))
        footer_label.pack(pady=(5, 0))

        # Track all inputs
        self.all_inputs = [
            self.first_name, self.middle_name, self.last_name,
            self.dob, self.ssn_cpn, self.address,
            self.email, self.phone_number
        ]
        # Inputs are enabled initially

        # Fake duration (demo = 20 sec)
        self.fake_duration = 20
        self.progress_step = 100 / self.fake_duration
        self.progress_counter = 0

    def create_input(self, parent_frame, label_text, row_num):
        label = ttk.Label(parent_frame, text=label_text)
        label.grid(row=row_num, column=0, sticky="w", padx=10, pady=5)
        entry = ttk.Entry(parent_frame)
        entry.grid(row=row_num, column=1, sticky="ew", padx=10, pady=5)
        return entry

    def set_inputs_state(self, state):
        for entry in self.all_inputs:
            entry.config(state=state)

    def update_log(self, message, append=False):
        self.log_text.config(state='normal')
        if not append:
            self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def handle_button_click(self):
        if self.submit_button['text'] == "⚡ GENERATE ⚡":
            # Lock button and inputs
            self.submit_button.config(state="disabled")
            self.set_inputs_state('disabled')
            self.update_log("SYSTEM STATUS:\nPROCESS STARTED...\nPlease wait (simulated 20 sec)...")
            self.progress_counter = 0
            self.progress['value'] = 0
            self.fake_work()
        else:
            # Collect inputs and log
            data = { 
                "First Name": self.first_name.get(),
                "Middle Name": self.middle_name.get(),
                "Last Name": self.last_name.get(),
                "Date of Birth": self.dob.get(),
                "SSN/CPN Number": self.ssn_cpn.get(),
                "Address": self.address.get(),
                "Email Address": self.email.get(),
                "Phone Number": self.phone_number.get()
            }
            log_message = "--- FORM SUBMITTED ---\n"
            for key, value in data.items():
                log_message += f"{key}: {value}\n"
            log_message += "----------------------"
            self.update_log(log_message)

            # Lock inputs again
            self.set_inputs_state('disabled')
            self.submit_button.config(text="⚡ GENERATE ⚡")

    def fake_work(self):
        """Simulate long-running process."""
        if self.progress_counter < self.fake_duration:
            self.progress_counter += 1
            self.progress['value'] += self.progress_step
            self.update_log(f"Processing... {int((self.progress_counter/self.fake_duration)*100)}%", append=True)
            self.root.after(1000, self.fake_work)  # 1 second per step
        else:
            self.update_log("Process finished. Ready to SUBMIT.")
            self.set_inputs_state('normal')
            self.submit_button.config(state="normal", text="⚡ SUBMIT ⚡")

if __name__ == "__main__":
    root = tk.Tk()
    app = UserFormApp(root)
    root.mainloop()
