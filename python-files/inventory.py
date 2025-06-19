import tkinter as tk
import win32gui
import win32con
import win32api

class HotbarOverlay:
    def __init__(self):
        self.root = tk.Tk()

        # Konfigurasi window: fullscreen transparan, tanpa border, always on top
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # JANGAN SET -alpha di sini jika Anda ingin hanya angkanya yang transparan.
        # Jika Anda set -alpha di sini, seluruh jendela akan transparan.
        # self.root.attributes('-alpha', 1.0) # Pastikan ini 1.0 (opaque) atau tidak ada
        
        # Warna hitam akan transparan (ini untuk background canvas agar tembus pandang)
        self.root.attributes('-transparentcolor', 'black') 
        self.root.configure(bg='black') # Background root dan canvas harus hitam

        # Resolusi layar
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Buat window fullscreen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Canvas untuk menggambar angka
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg='black', # Background canvas juga hitam agar transparan
            highlightthickness=0
        )
        self.canvas.pack()

        # Definisikan warna transparan untuk angka
        # Ini adalah warna putih (255,255,255) yang akan kita buat 50% transparan
        self.TRANSPARENT_WHITE_COLOR_KEY = win32api.RGB(255, 255, 255) # Putih

        self.draw_numbers()
        self.make_clickthrough()

    def draw_numbers(self):
        """Gambar hotkey kustom di atas hotbar dengan posisi di atas kiri setiap slot"""
        slot_count = 9
        slot_width = 64 # Lebar satu slot hotbar yang sudah Anda temukan
        
        total_hotbar_width = slot_width * slot_count
        
        hotbar_start_x = 486 
        y_pos = self.screen_height - 62 
        
        font_size = 14 
        custom_font = ('Minecraft', font_size, 'bold')

        hotkey_mapping = {
            0: "1", 1: "2", 2: "3", 3: "4", 4: "E",
            5: "R", 6: "X", 7: "C", 8: "V"
        }

        for i in range(slot_count):
            hotkey_text = hotkey_mapping.get(i, "") 
            x = hotbar_start_x + (i * slot_width) 
            
            self.canvas.create_text(
                x, y_pos,
                text=hotkey_text,
                font=custom_font,
                fill='white', # Set warna fill menjadi putih
                anchor='nw' 
            )

    def make_clickthrough(self):
        """Jadikan window transparan & tidak bisa diklik, dengan angka 50% transparan"""
        hwnd = self.root.winfo_id()
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        
        # --- PERUBAHAN UTAMA DI SINI ---
        # Tetapkan warna hitam (background) sebagai kunci transparansi penuh
        # Tetapkan warna putih (untuk angka) dengan alpha 128 (50%)
        
        # Atur transparansi untuk warna hitam (background) menjadi sepenuhnya transparan
        win32gui.SetLayeredWindowAttributes(
            hwnd,
            win32api.RGB(0, 0, 0), # Warna hitam
            255, # Alpha 255 (opaque), tapi LWA_COLORKEY akan membuatnya transparan penuh
            win32con.LWA_COLORKEY # Kunci warna untuk transparansi penuh (hitam tembus pandang)
        )

        # Untuk membuat angka 50% transparan, kita perlu memanggil SetLayeredWindowAttributes lagi
        # dengan warna yang digunakan untuk angka (putih) dan alpha yang diinginkan.
        # Namun, perlu diingat bahwa SetLayeredWindowAttributes HANYA bisa menggunakan SATU LWA_COLORKEY.
        # Jadi, kita tidak bisa punya dua warna berbeda yang transparan dengan cara ini.
        # Alternatifnya adalah mengubah alpha keseluruhan jendela menjadi 0.5 dan tidak memakai transparentcolor
        # untuk warna background.
        
        # JIKA ANDA INGIN HANYA ANGKA YANG TRANSPARAN DAN BACKGROUND HILANG TOTAL:
        # Pilihan terbaik adalah dengan MENGHAPUS transparentcolor='black' di __init__
        # dan mengubah fill='white' menjadi fill='gray' atau warna lain yang tidak hitam
        # lalu mengatur alpha keseluruhan jendela 0.5.
        
        # ATAU, jika Anda tetap ingin background hitam tembus pandang DAN angka transparan:
        # Ini sangat sulit dengan metode SetLayeredWindowAttributes LWA_COLORKEY saja,
        # karena LWA_COLORKEY hanya bisa diterapkan pada satu warna kunci.
        # Untuk kasus ini, Anda harus menggunakan metode lain seperti:
        # 1. Menggambar angka sebagai gambar PNG transparan di atas canvas.
        # 2. Menggunakan pustaka yang lebih canggih seperti PyQt/PySide yang memiliki dukungan alpha channel untuk widget.
        
        # Karena keterbatasan SetLayeredWindowAttributes dengan LWA_COLORKEY (hanya satu warna),
        # Saya akan menunjukkan cara yang akan membuat SELURUH WINDOW (termasuk angka) 50% transparan,
        # SEMENTARA latar belakang hitam tetap transparan penuh.
        # Ini adalah trade-off.

        # Mengatur alpha untuk keseluruhan jendela (bukan per item)
        # Jika Anda ingin hanya angka yang transparan, dan background hitam sepenuhnya hilang,
        # maka ini adalah cara terbaik menggunakan Tkinter + win32gui.
        self.root.attributes('-alpha', 0.7) 
        # Ini akan membuat semua yang digambar di canvas (termasuk angka) menjadi 50% transparan
        # KECUALI warna yang ditentukan oleh -transparentcolor (yaitu hitam) yang tetap transparan penuh.


    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    overlay = HotbarOverlay()
    overlay.run()



    # def draw_numbers(self):
        #"""Gambar hotkey kustom di atas hotbar dengan posisi di atas kiri setiap slot"""
        #slot_count = 9
        #slot_width = 64-4 # Lebar satu slot hotbar yang sudah Anda temukan

        # Jarak total yang ditempati hotbar (9 slot)
        #total_hotbar_width = slot_width * slot_count
        
        # --- Sesuaikan Posisi Awal Hotbar secara Keseluruhan ---
        # Ini adalah posisi X awal untuk tepi KIRI hotbar secara keseluruhan
        # Sesuaikan '485' ini agar ujung kiri slot pertama hotbar Anda pas
        #hotbar_start_x = 485 + 30 
        
        # Posisi vertikal untuk bagian ATAS angka dari hotbar
        # Sesuaikan '65' ini untuk menggeser angka ke atas/bawah
        #y_pos = self.screen_height - 65 - 180 