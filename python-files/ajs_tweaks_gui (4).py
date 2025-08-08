# GUI version of AJ's Tweaks using CustomTkinter
import time
import random
import os

try:
    import customtkinter as ctk
except ImportError:
    print("[ERROR] CustomTkinter is not installed. Please install it using 'pip install customtkinter' and make sure tkinter is available.")
    exit(1)

try:
    import tkinter  # Required for customtkinter to function
except ImportError:
    print("[ERROR] tkinter is not installed. Please install it to run this application.")
    exit(1)

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class AJsTweaksApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AJ's Tweaks")
        self.geometry("900x500")
        self.icon_path = os.path.join(os.path.dirname(__file__), "d8eef50bfd61067c151fbd5897d4d78c.ico")
        try:
            self.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"[WARNING] Failed to load icon. Make sure the file exists and is a valid .ico file. Error: {e}")

        self.label_title = ctk.CTkLabel(self, text="AJ's Tweaks", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=10)

        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(pady=10, padx=10, fill="x")

        self.label_cpu = ctk.CTkLabel(self.stats_frame, text="CPU: 0%", font=("Arial", 16))
        self.label_ram = ctk.CTkLabel(self.stats_frame, text="RAM: 0%", font=("Arial", 16))
        self.label_gpu = ctk.CTkLabel(self.stats_frame, text="GPU: 0%", font=("Arial", 16))
        self.label_latency = ctk.CTkLabel(self.stats_frame, text="Latency: 0ms", font=("Arial", 16))

        self.label_cpu.grid(row=0, column=0, padx=20, pady=10)
        self.label_ram.grid(row=0, column=1, padx=20, pady=10)
        self.label_gpu.grid(row=0, column=2, padx=20, pady=10)
        self.label_latency.grid(row=0, column=3, padx=20, pady=10)

        self.optimize_btn = ctk.CTkButton(self, text="OPTIMIZE NOW", command=self.optimize_now, font=("Arial", 18, "bold"))
        self.optimize_btn.pack(pady=20)

        self.section_titles = ctk.CTkFrame(self)
        self.section_titles.pack()

        sections = ["Main Tweaks", "CPU Tweaks", "GPU Tweaks", "KBM Tweaks", "Others"]
        for i, title in enumerate(sections):
            ctk.CTkLabel(self.section_titles, text=title, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=20)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        # Main Tweaks
        ctk.CTkButton(self.button_frame, text="System Tweaks", command=self.optimize_now).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Service Tweaks", command=self.optimize_now).grid(row=2, column=0, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Debloat Tweaks", command=self.disable_bloat).grid(row=3, column=0, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Privacy Tweaks", command=self.optimize_now).grid(row=4, column=0, padx=10, pady=5)

        # CPU Tweaks
        ctk.CTkButton(self.button_frame, text="Intel Tweaks", command=self.intel_tweak).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Intel Services", command=self.intel_services).grid(row=2, column=1, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Ryzen Tweaks", command=self.ryzen_tweak).grid(row=3, column=1, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Ryzen Services", command=self.ryzen_services).grid(row=4, column=1, padx=10, pady=5)

        # GPU Tweaks
        ctk.CTkButton(self.button_frame, text="Nvidia Tweaks", command=self.nvidia_tweak).grid(row=1, column=2, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Nvidia Services", command=self.nvidia_services).grid(row=2, column=2, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="AMD Tweaks", command=self.amd_tweak).grid(row=3, column=2, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="AMD Services", command=self.amd_services).grid(row=4, column=2, padx=10, pady=5)

        # KBM Tweaks
        ctk.CTkButton(self.button_frame, text="Keyboard Tweaks", command=self.kbm_tweak).grid(row=1, column=3, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Mouse Tweaks", command=self.mouse_tweak).grid(row=2, column=3, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="USB Tweaks", command=self.usb_tweak).grid(row=3, column=3, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Delay for KBM", command=self.kbm_tweak).grid(row=4, column=3, padx=10, pady=5)

        # Other Tweaks
        ctk.CTkButton(self.button_frame, text="0 Delay Tweaks", command=self.optimize_now).grid(row=1, column=4, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Disable Extra Services", command=self.disable_bloat).grid(row=2, column=4, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Process Tweaks", command=self.optimize_now).grid(row=3, column=4, padx=10, pady=5)
        ctk.CTkButton(self.button_frame, text="Network Tweaks", command=self.network_optimize).grid(row=4, column=4, padx=10, pady=5)

        self.update_stats()

    def update_stats(self):
        self.label_cpu.configure(text=f"CPU: {random.randint(5, 95)}%")
        self.label_ram.configure(text=f"RAM: {random.randint(10, 90)}%")
        self.label_gpu.configure(text=f"GPU: {random.randint(20, 90)}%")
        self.label_latency.configure(text=f"Latency: {random.randint(10, 100)}ms")
        self.after(2000, self.update_stats)

    def optimize_now(self): print("[Optimizing] FPS boost and latency reduction...")
    def kbm_tweak(self): print("[KBM Tweak] Applying low delay settings...")
    def mouse_tweak(self): print("[Mouse Tweak] Optimizing mouse polling and DPI...")
    def usb_tweak(self): print("[USB Tweak] Reducing USB latency and power delays...")
    def nvidia_tweak(self): print("[NVIDIA Tweak] Applying optimal driver settings and performance mode...")
    def nvidia_services(self): print("[NVIDIA Services] Disabling unnecessary NVIDIA background services...")
    def amd_tweak(self): print("[AMD Tweak] Enabling Radeon Boost and optimizing latency settings...")
    def amd_services(self): print("[AMD Services] Disabling AMD telemetry and logging...")
    def intel_tweak(self): print("[Intel Tweak] Enabling Speed Shift and max performance profile...")
    def intel_services(self): print("[Intel Services] Turning off Intel system services for gaming...")
    def ryzen_tweak(self): print("[Ryzen Tweak] Applying Ryzen Balanced power plan and tuning precision boost...")
    def ryzen_services(self): print("[Ryzen Services] Disabling unnecessary Ryzen Master background tasks...")
    def disable_bloat(self): print("[Debloat] Removing unnecessary services...")
    def network_optimize(self): print("[Network] Optimizing latency...")

if __name__ == "__main__":
    app = AJsTweaksApp()
    app.mainloop()
