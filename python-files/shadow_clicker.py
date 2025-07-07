import tkinter as tk
import random
import time
import os
import sys

class ShadowClickerGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Shadow Clicker")
        self.master.geometry("600x400")
        self.master.resizable(False, False)

        # ICON AYARI (.ico dosyası aynı klasörde olmalı)
        try:
            icon_path = os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), "favicon.ico")
            self.master.iconbitmap(icon_path)
        except:
            pass  # ikon bulunamazsa hata verme

        self.canvas = tk.Canvas(self.master, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.score = 0
        self.game_running = True
        self.circle_id = None
        self.start_time = time.time()
        self.total_time = 60  # saniye
        self.last_click_time = time.time()

        # Skor metni
        self.score_text = self.canvas.create_text(
            10, 10, anchor="nw", fill="white",
            font=("Helvetica", 14), text="Score: 0"
        )

        # Zaman metni
        self.time_text = self.canvas.create_text(
            300, 10, anchor="n", fill="white",
            font=("Helvetica", 14), text="Time: 60s"
        )

        # İmza
        self.canvas.create_text(
            590, 390, anchor="se", fill="gray",
            font=("Helvetica", 10), text="By WestaCape"
        )

        self.spawn_circle()
        self.update_game()

    def spawn_circle(self):
        if self.circle_id:
            self.canvas.delete(self.circle_id)

        x = random.randint(50, 550)
        y = random.randint(50, 350)
        r = 25

        self.circle_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="gray20", outline="white"
        )
        self.canvas.tag_bind(self.circle_id, "<Button-1>", self.on_click)

    def on_click(self, event):
        if not self.game_running:
            return
        self.score += 1
        self.last_click_time = time.time()
        self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
        self.spawn_circle()

    def update_game(self):
        if not self.game_running:
            return

        elapsed = time.time() - self.start_time
        remaining = int(self.total_time - elapsed)

        if remaining <= 0:
            self.end_game()
            return

        # Zaman güncelle
        self.canvas.itemconfigure(self.time_text, text=f"Time: {remaining}s")

        # Hız artışı: skor arttıkça süre kısalır
        speed = max(300, 1000 - self.score * 20)
        self.master.after(speed, self.update_game)

    def end_game(self):
        self.game_running = False
        self.canvas.delete(self.circle_id)
        self.canvas.create_text(
            300, 180, fill="white", font=("Helvetica", 24, "bold"),
            text="Time's Up!"
        )
        self.canvas.create_text(
            300, 220, fill="gray", font=("Helvetica", 14),
            text=f"Final Score: {self.score}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    game = ShadowClickerGame(root)
    root.mainloop()
