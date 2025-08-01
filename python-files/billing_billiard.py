
import tkinter as tk
from tkinter import messagebox, simpledialog
import serial
import serial.tools.list_ports
import time

APP_TITLE = "Billing Billiard by Wilsa"
ADMIN_PASSWORD = "admin"
OPERATOR_PASSWORD = "1234"
TARIF_PER_JAM = 20000
JUMLAH_MEJA = 4

def connect_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            arduino = serial.Serial(port.device, 9600, timeout=1)
            print(f"Terhubung ke Arduino di {port.device}")
            return arduino
        except:
            pass
    return None

arduino = connect_arduino()

def kirim_perintah(meja, status):
    if arduino:
        cmd = f"M{meja}_{status}\n"
        arduino.write(cmd.encode())
        print(f"Kirim: {cmd.strip()}")

class Meja:
    def __init__(self, nomor):
        self.nomor = nomor
        self.mulai = None
        self.jalan = False
        self.pause = False
        self.waktu_pause = 0
        self.total_pause = 0

    def mulai_billing(self):
        self.mulai = time.time()
        self.jalan = True
        self.pause = False
        self.total_pause = 0
        kirim_perintah(self.nomor, "ON")

    def stop_billing(self):
        self.jalan = False
        self.pause = False
        kirim_perintah(self.nomor, "OFF")
        total_waktu = self.get_lama_main()
        total_jam = total_waktu / 3600
        biaya = int(total_jam * TARIF_PER_JAM)
        return biaya

    def pause_billing(self):
        if self.jalan and not self.pause:
            self.pause = True
            self.waktu_pause = time.time()
            kirim_perintah(self.nomor, "OFF")

    def resume_billing(self):
        if self.jalan and self.pause:
            self.pause = False
            self.total_pause += time.time() - self.waktu_pause
            kirim_perintah(self.nomor, "ON")

    def get_lama_main(self):
        if not self.jalan:
            return 0
        if self.pause:
            return (self.waktu_pause - self.mulai) - self.total_pause
        else:
            return (time.time() - self.mulai) - self.total_pause

class BillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.mejas = [Meja(i+1) for i in range(JUMLAH_MEJA)]
        self.create_ui()

    def create_ui(self):
        tk.Label(self.root, text=APP_TITLE, font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        for i, meja in enumerate(self.mejas):
            frame = tk.LabelFrame(self.root, text=f"Meja {meja.nomor}", padx=10, pady=10)
            frame.grid(row=1, column=i, padx=5, pady=5)

            tk.Button(frame, text="Mulai", command=lambda m=meja: self.mulai_billing(m)).pack(fill="x")
            tk.Button(frame, text="Pause", command=lambda m=meja: self.pause_billing(m)).pack(fill="x")
            tk.Button(frame, text="Resume", command=lambda m=meja: self.resume_billing(m)).pack(fill="x")
            tk.Button(frame, text="Stop", command=lambda m=meja: self.stop_billing(m)).pack(fill="x")

        tk.Button(self.root, text="Ubah Tarif", command=self.ubah_tarif).grid(row=2, column=0, pady=10)
        tk.Button(self.root, text="Keluar", command=self.root.quit).grid(row=2, column=3, pady=10)

    def mulai_billing(self, meja):
        meja.mulai_billing()
        messagebox.showinfo("Info", f"Meja {meja.nomor} dimulai.")

    def stop_billing(self, meja):
        biaya = meja.stop_billing()
        messagebox.showinfo("Info", f"Meja {meja.nomor} selesai.\nBiaya: Rp {biaya:,}")

    def pause_billing(self, meja):
        meja.pause_billing()
        messagebox.showinfo("Info", f"Meja {meja.nomor} di-pause.")

    def resume_billing(self, meja):
        meja.resume_billing()
        messagebox.showinfo("Info", f"Meja {meja.nomor} dilanjutkan.")

    def ubah_tarif(self):
        global TARIF_PER_JAM
        password = simpledialog.askstring("Password", "Masukkan password admin:", show="*")
        if password == ADMIN_PASSWORD:
            tarif_baru = simpledialog.askinteger("Ubah Tarif", "Masukkan tarif baru per jam:")
            if tarif_baru:
                TARIF_PER_JAM = tarif_baru
                messagebox.showinfo("Info", f"Tarif diubah menjadi Rp {tarif_baru:,} per jam.")
        else:
            messagebox.showerror("Error", "Password salah!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()
