import tkinter as tk
from tkinter import ttk, messagebox

class ModMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skate Mod Menu")
        self.root.geometry("400x350")
        self.root.configure(bg="#1e1e1e")

        title = tk.Label(root, text="Skate Mod Menu", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e")
        title.pack(pady=10)

        # Cheats section
        self.infinite_score = tk.BooleanVar()
        self.unlock_boards = tk.BooleanVar()

        tk.Checkbutton(root, text="Infinite Score", variable=self.infinite_score,
                       bg="#1e1e1e", fg="white", selectcolor="#333").pack(anchor="w", padx=20, pady=5)

        tk.Checkbutton(root, text="Unlock All Boards", variable=self.unlock_boards,
                       bg="#1e1e1e", fg="white", selectcolor="#333").pack(anchor="w", padx=20, pady=5)

        # Speed multiplier
        tk.Label(root, text="Speed Multiplier", fg="white", bg="#1e1e1e").pack(pady=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(root, from_=0.5, to=5.0, orient="horizontal", variable=self.speed_var).pack(fill="x", padx=20)

        # Buttons
        tk.Button(root, text="Teleport to Spot", command=self.teleport, bg="#444", fg="white").pack(pady=10)
        tk.Button(root, text="Apply Settings", command=self.apply_settings, bg="#555", fg="white").pack(pady=5)

    def teleport(self):
        messagebox.showinfo("Teleport", "Teleported to skate spot!")

    def apply_settings(self):
        settings = (
            f"Infinite Score: {self.infinite_score.get()}\n"
            f"Unlock Boards: {self.unlock_boards.get()}\n"
            f"Speed Multiplier: {self.speed_var.get():.2f}"
        )
        messagebox.showinfo("Settings Applied", settings)


if __name__ == "__main__":
    root = tk.Tk()
    app = ModMenuApp(root)
    root.mainloop()
