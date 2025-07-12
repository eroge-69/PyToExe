import customtkinter as ctk
import validators
from tkinter import messagebox

# تنظیم حالت ظاهری و تم رنگی
ctk.set_appearance_mode("dark")  # "dark" یا "light"
ctk.set_default_color_theme("dark-blue")  # "blue", "green", "dark-blue"

class SiteExtractionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Site-extraction")
        self.geometry("700x550")
        self.resizable(False, False)

        # تنظیم گرید اصلی
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # فریم اصلی
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # عنوان برنامه
        self.title_label = ctk.CTkLabel(self.main_frame, text="Site-extraction", font=ctk.CTkFont(size=32, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

        # توضیح کوتاه
        self.desc_label = ctk.CTkLabel(self.main_frame,
                                       text="Secure and customizable tool for extracting data from websites",
                                       font=ctk.CTkFont(size=14),
                                       wraplength=650,
                                       justify="center")
        self.desc_label.grid(row=1, column=0, pady=(0, 20), sticky="n")

        # فریم ورودی URL
        self.url_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.url_frame.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.url_frame, text="Website URLs (one per line):", font=ctk.CTkFont(size=12))
        self.url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        self.url_text = ctk.CTkTextbox(self.url_frame, width=600, height=120, corner_radius=8)
        self.url_text.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # فریم تنظیمات خروجی
        self.settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.settings_frame.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)

        self.format_label = ctk.CTkLabel(self.settings_frame, text="Output Format:", font=ctk.CTkFont(size=12))
        self.format_label.grid(row=0, column=0, padx=10, pady=15, sticky="w")

        self.extract_type = ctk.CTkComboBox(self.settings_frame, values=["HTML", "JSON", "CSV", "Excel"], width=180)
        self.extract_type.set("Select output format")
        self.extract_type.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        # نوار پیشرفت
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=640)
        self.progress_bar.grid(row=4, column=0, pady=20, padx=30, sticky="ew")
        self.progress_bar.set(0)

        # وضعیت عملیات
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Waiting for input", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=5, column=0, pady=(0, 20), sticky="w", padx=30)

        # دکمه استخراج
        self.extract_button = ctk.CTkButton(self.main_frame, text="Extract", width=200, height=45, corner_radius=12,
                                            fg_color="#1f6aa5", hover_color="#145a86", command=self.start_extraction)
        self.extract_button.grid(row=6, column=0, pady=(0, 30))

    def start_extraction(self):
        urls = self.url_text.get("0.0", "end").strip().split("\n")
        valid_urls = [u.strip() for u in urls if validators.url(u.strip())]
        ext_type = self.extract_type.get()

        if not valid_urls:
            messagebox.showerror("Input Error", "Please enter at least one valid URL.")
            self.status_label.configure(text="Status: Invalid URLs")
            self.progress_bar.set(0)
            return
        if ext_type == "Select output format":
            messagebox.showerror("Input Error", "Please select an output format.")
            self.status_label.configure(text="Status: Output format not selected")
            self.progress_bar.set(0)
            return

        self.status_label.configure(text=f"Status: Extracting {ext_type} data from {len(valid_urls)} URL(s)...")
        self.progress_bar.set(0.5)

        # اینجا کد استخراج واقعی اضافه شود

        self.progress_bar.set(1)
        self.status_label.configure(text="Status: Extraction completed successfully")


if __name__ == "__main__":
    app = SiteExtractionApp()
    app.mainloop()
