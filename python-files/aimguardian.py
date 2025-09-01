import tkinter as tk
import customtkinter as ctk
import threading
import time

# -----------------------------
# Main Application
# -----------------------------
class AimGuardianApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AimGuardian")
        self.geometry("1000x650")
        self.configure(bg="black")

        # -----------------------------
        # Moving Ball Background
        # -----------------------------
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.ball = self.canvas.create_oval(50, 50, 100, 100, fill="red", outline="")
        self.dx, self.dy = 3, 2
        threading.Thread(target=self.animate_ball, daemon=True).start()

        # -----------------------------
        # Tab System
        # -----------------------------
        self.tabview = ctk.CTkTabview(self.canvas, fg_color="black")
        self.tabview.place(relx=0.5, rely=0.5, anchor="center")

        self.regedit_tab = self.tabview.add("Regedit")
        self.sensi_tab = self.tabview.add("Sensi")

        self.build_regedit_tab()
        self.build_sensi_tab()

    # -----------------------------
    # Regedit Tab
    # -----------------------------
    def build_regedit_tab(self):
        button_names = [
            "LEGIT", "VIP", "PRIME", "HYPERIUS", "ACCELEREX",
            "ELITE", "EXTREME", "SUPREME", "NOVALUX", "BIONIX",
            "ULTIMATE", "PLATINIUM", "ROYAL", "OMNITRON", "CIRCUITRON",
            "SUPERIOR", "DELUXE", "INFINITE", "QUASARX", "DYNATRON",
            "PREMIUM", "PLUS", "GRAND", "REACTRON", "ENERGIX",
            "ADVANCED", "NEXIUS", "VORTEXA", "SPECTRUMX", "FUTURON"
        ]

        frame = ctk.CTkFrame(self.regedit_tab, fg_color="black")
        frame.pack(expand=True, fill="both", pady=10)

        rows, cols = 6, 5
        for i, name in enumerate(button_names):
            btn = ctk.CTkButton(
                frame,
                text=name,
                fg_color="red",
                hover_color="darkred",
                width=120,
                height=40,
                command=lambda n=name: self.apply_regedit(n)
            )
            btn.grid(row=i // cols, column=i % cols, padx=10, pady=10)

        delete_btn = ctk.CTkButton(
            frame,
            text="DELETE REGEDIT",
            fg_color="black",
            border_color="red",
            border_width=2,
            hover_color="red",
            width=200,
            height=40,
            command=self.delete_regedit
        )
        delete_btn.grid(row=rows, column=0, columnspan=cols, pady=15)

    # -----------------------------
    # Sensi Tab
    # -----------------------------
    def build_sensi_tab(self):
        frame = ctk.CTkFrame(self.sensi_tab, fg_color="black")
        frame.pack(expand=True, fill="both", pady=10)

        # Sensitivity
        ctk.CTkLabel(frame, text="Mouse Sensitivity :", text_color="white").pack(pady=5)
        self.sensi_slider = ctk.CTkSlider(frame, from_=0, to=100, fg_color="red", progress_color="white")
        self.sensi_slider.pack(pady=5)

        # Speed
        ctk.CTkLabel(frame, text="Mouse Speed :", text_color="white").pack(pady=5)
        self.speed_slider = ctk.CTkSlider(frame, from_=0, to=100, fg_color="red", progress_color="white")
        self.speed_slider.pack(pady=5)

        # X Axis
        ctk.CTkLabel(frame, text="X :", text_color="white").pack(pady=5)
        self.x_slider = ctk.CTkSlider(frame, from_=-10, to=10, fg_color="red", progress_color="white")
        self.x_slider.pack(pady=5)

        # Y Axis
        ctk.CTkLabel(frame, text="Y :", text_color="white").pack(pady=5)
        self.y_slider = ctk.CTkSlider(frame, from_=-10, to=10, fg_color="red", progress_color="white")
        self.y_slider.pack(pady=5)

        # Apply Button
        apply_btn = ctk.CTkButton(frame, text="Apply", fg_color="red", hover_color="darkred", command=self.apply_sensi)
        apply_btn.pack(pady=15)

    # -----------------------------
    # Animation
    # -----------------------------
    def animate_ball(self):
        while True:
            coords = self.canvas.coords(self.ball)
            if coords[2] >= self.winfo_width() or coords[0] <= 0:
                self.dx = -self.dx
            if coords[3] >= self.winfo_height() or coords[1] <= 0:
                self.dy = -self.dy
            self.canvas.move(self.ball, self.dx, self.dy)
            time.sleep(0.02)

    # -----------------------------
    # Actions
    # -----------------------------
    def apply_regedit(self, name):
        print(f"Applied Regedit: {name}")

    def delete_regedit(self):
        print("Regedit Deleted")

    def apply_sensi(self):
        sensi = self.sensi_slider.get()
        speed = self.speed_slider.get()
        x = self.x_slider.get()
        y = self.y_slider.get()
        print(f"Sensi Applied -> Sensitivity: {sensi}, Speed: {speed}, X: {x}, Y: {y}")


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = AimGuardianApp()
    app.mainloop()
