import tkinter as tk
import random
import os

class GoyangTeksApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARE YOU SURE WANT TO KILL EXPLORER.EXE?")

        self.canvas = tk.Canvas(root, width=500, height=300, bg="black")
        self.canvas.pack()

        # Tampilkan teks
        self.text_id = self.canvas.create_text(
            250, 150, text="KILL EXPLORER.EXE!!!!",
            font=("Helvetica", 24, "bold"), fill="red"
        )

        # Simpan posisi awal
        self.original_coords = self.canvas.coords(self.text_id)

        # Bind klik ke teks
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.matikan_explorer)

        # Mulai goyangan otomatis
        self.goyang = False
        self.jadwalkan_goyang_otomatis()

    def goyang_bergerak(self, count=10):
        if count > 0:
            dx = random.randint(-16, 16)
            dy = random.randint(-16, 16)
            x, y = self.original_coords
            self.canvas.coords(self.text_id, x + dx, y + dy)
            self.root.after(50, self.goyang_bergerak, count - 1)
        else:
            # Kembalikan ke posisi awal
            self.canvas.coords(self.text_id, *self.original_coords)

    def jadwalkan_goyang_otomatis(self):
        self.goyang_bergerak()  # Mulai goyang sekali
        self.root.after(4000, self.jadwalkan_goyang_otomatis)  # Ulangi tiap 5 detik

    def matikan_explorer(self, event):
        os.system("taskkill /f /im explorer.exe")
        self.root.destroy()  # Tutup aplikasi setelah command dijalankan

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = GoyangTeksApp(root)
    root.mainloop()
