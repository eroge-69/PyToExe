import tkinter as tk
import random
import os  # Gunakan os untuk eksekusi command

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

        # Bind aksi
        self.canvas.tag_bind(self.text_id, "<Enter>", self.mulai_goyang)
        self.canvas.tag_bind(self.text_id, "<Leave>", self.berhenti_goyang)
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.matikan_explorer)

        self.goyang = False

    def mulai_goyang(self, event):
        if not self.goyang:
            self.goyang = True
            self.goyang_bergerak()

    def berhenti_goyang(self, event):
        self.goyang = False
        self.canvas.coords(self.text_id, *self.original_coords)

    def goyang_bergerak(self):
        if self.goyang:
            dx = random.randint(-16, 16)
            dy = random.randint(-16, 16)
            x, y = self.original_coords
            self.canvas.coords(self.text_id, x + dx, y + dy)
            self.root.after(20, self.goyang_bergerak)

    def matikan_explorer(self, event):
        os.system("taskkill /f /im explorer.exe")
        self.root.destroy()  # Tutup aplikasi setelah command dijalankan

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = GoyangTeksApp(root)
    root.mainloop()
