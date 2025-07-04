import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image
import threading

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konwerter obrazów do WebP")
        self.root.geometry("550x450")
        self.root.resizable(False, False)

        self.file_paths = []
        self.output_dir = ""

        # --- GŁÓWNY KONTENER ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # --- SEKCJA WYBORU PLIKÓW ---
        select_files_button = ttk.Button(main_frame, text="1. Wybierz pliki", command=self.select_files)
        select_files_button.pack(pady=5, fill='x')
        self.files_label = ttk.Label(main_frame, text="Nie wybrano plików")
        self.files_label.pack(pady=2)

        # --- SEKCJA WYBORU FOLDERU DOCELOWEGO ---
        select_dir_button = ttk.Button(main_frame, text="2. Wybierz folder docelowy", command=self.select_output_dir)
        select_dir_button.pack(pady=5, fill='x')
        self.dir_label = ttk.Label(main_frame, text="Nie wybrano folderu")
        self.dir_label.pack(pady=2)

        # --- SEKCJA JAKOŚCI ---
        quality_frame = ttk.Frame(main_frame)
        quality_frame.pack(pady=15, fill='x')
        ttk.Label(quality_frame, text="Jakość konwersji:").pack(side='left', padx=5)
        self.quality_scale = ttk.Scale(quality_frame, from_=1, to=100, orient='horizontal')
        self.quality_scale.set(85)
        self.quality_scale.pack(side='left', expand=True, fill='x')
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_scale.config(command=lambda v: self.quality_label.config(text=f"{int(float(v))}"))
        self.quality_label.pack(side='left', padx=5)

        # --- PRZYCISK KONWERSJI ---
        self.convert_button = ttk.Button(main_frame, text="3. Rozpocznij konwersję", command=self.start_conversion_thread)
        self.convert_button.pack(pady=20, ipady=10, fill='x')

        # --- SEKCJA POSTĘPU ---
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(pady=5, fill='x')
        self.status_label = ttk.Label(main_frame, text="Gotowy do pracy!")
        self.status_label.pack(pady=5)

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(
            title="Wybierz pliki obrazów",
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png"), ("Wszystkie pliki", "*.*")]
        )
        if self.file_paths:
            self.files_label.config(text=f"Wybrano plików: {len(self.file_paths)}")
        else:
            self.files_label.config(text="Nie wybrano plików")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title="Wybierz folder, w którym zapiszą się pliki")
        if self.output_dir:
            self.dir_label.config(text=self.output_dir)
        else:
            self.dir_label.config(text="Nie wybrano folderu")

    def start_conversion_thread(self):
        # Uruchomienie konwersji w osobnym wątku, aby nie blokować interfejsu
        conversion_thread = threading.Thread(target=self.convert_images)
        conversion_thread.start()

    def convert_images(self):
        if not self.file_paths:
            messagebox.showerror("Błąd", "Proszę wybrać pliki do konwersji.")
            return
        if not self.output_dir:
            messagebox.showerror("Błąd", "Proszę wybrać folder docelowy.")
            return

        self.convert_button.config(state="disabled")
        self.progress_bar['value'] = 0
        quality = int(self.quality_scale.get())
        total_files = len(self.file_paths)

        for i, file_path in enumerate(self.file_paths):
            try:
                # Aktualizacja interfejsu
                self.status_label.config(text=f"Konwertowanie: {os.path.basename(file_path)}")
                self.progress_bar['value'] = (i + 1) / total_files * 100
                self.root.update_idletasks() # Odświeżenie UI

                # Konwersja
                image = Image.open(file_path).convert("RGB")
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(self.output_dir, f"{base_name}.webp")
                image.save(output_path, 'webp', quality=quality)

            except Exception as e:
                print(f"Nie udało się przekonwertować pliku {file_path}: {e}")
        
        self.status_label.config(text="Konwersja zakończona pomyślnie!")
        self.convert_button.config(state="normal")
        messagebox.showinfo("Sukces", f"Zakończono konwersję {total_files} plików!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()