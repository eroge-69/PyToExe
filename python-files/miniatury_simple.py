import os
import subprocess
import sys
import multiprocessing
from tkinter import Tk, filedialog, Button, Label, messagebox, Frame, Scale, Entry
from tkinter import ttk
from PIL import Image, ImageOps, ImageFilter
import shutil

# Wymagane dla PyInstaller z multiprocessing
multiprocessing.freeze_support()

def install_missing_packages():
    required_packages = ["Pillow"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Instalowanie {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages()

def add_white_frame_to_images(folder_path, border_size=50):
    output_folder = os.path.join(folder_path, "Gotowe miniatury")
    os.makedirs(output_folder, exist_ok=True)
    
    # Znajdź wszystkie pliki obrazów
    image_files = [f for f in os.listdir(folder_path) 
                   if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
    
    total_files = len(image_files)
    if total_files == 0:
        messagebox.showinfo("Info", "Nie znaleziono plików obrazów w wybranym folderze.")
        return
    
    # Aktualizuj progress bar
    progress_bar_frames.config(value=0)
    label_status_for_frames.config(text=f"Znaleziono {total_files} plików. Rozpoczynam przetwarzanie...")
    root.update()
    
    for i, filename in enumerate(image_files):
        file_path = os.path.join(folder_path, filename)
        try:
            label_status_for_frames.config(text=f"Przetwarzanie: {filename}")
            root.update()
            
            with Image.open(file_path) as img:
                max_dimension = 2460
                scale_factor = max_dimension / max(img.width, img.height)
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                img = improve_image_quality(img)
                img_with_border = ImageOps.expand(img, border=border_size, fill="white")
                img_with_border.save(os.path.join(output_folder, filename))
            
            # Aktualizuj progress bar
            progress = int((i + 1) / total_files * 100)
            progress_bar_frames.config(value=progress)
            root.update()
                
        except Exception as e:
            print(f"Błąd przy przetwarzaniu {filename}: {e}")
            label_status_for_frames.config(text=f"Błąd przy przetwarzaniu {filename}: {e}")
            root.update()
    
    label_status_for_frames.config(text=f"Zakończono! Przetworzono {total_files} plików z ramką {border_size}px.")
    messagebox.showinfo("Sukces", f"Przetworzono {total_files} plików!\nZnajdziesz je w folderze 'Gotowe miniatury'")

def improve_image_quality(img):
    return img.filter(ImageFilter.MedianFilter(size=3)).filter(ImageFilter.SHARPEN)

def extract_images(folder_path):
    output_folder = os.path.join(folder_path, "Miniatury ofert")
    os.makedirs(output_folder, exist_ok=True)
    
    # Znajdź wszystkie foldery
    folders = [f for f in os.listdir(folder_path) 
               if os.path.isdir(os.path.join(folder_path, f))]
    
    total_folders = len(folders)
    if total_folders == 0:
        messagebox.showinfo("Info", "Nie znaleziono folderów w wybranym katalogu.")
        return
    
    # Aktualizuj progress bar
    progress_bar_extraction.config(value=0)
    label_status_for_extraction.config(text=f"Znaleziono {total_folders} folderów. Rozpoczynam wyodrębnianie...")
    root.update()
    
    processed_count = 0
    for i, folder in enumerate(folders):
        folder_path_full = os.path.join(folder_path, folder)
        image_path = os.path.join(folder_path_full, 'image_1.jpg')
        
        label_status_for_extraction.config(text=f"Sprawdzanie folderu: {folder}")
        root.update()
        
        if os.path.exists(image_path):
            try:
                shutil.copy(image_path, os.path.join(output_folder, f"{folder}.jpg"))
                processed_count += 1
            except Exception as e:
                print(f"Błąd przy kopiowaniu {folder}: {e}")
                label_status_for_extraction.config(text=f"Błąd przy kopiowaniu {folder}: {e}")
                root.update()
        
        # Aktualizuj progress bar
        progress = int((i + 1) / total_folders * 100)
        progress_bar_extraction.config(value=progress)
        root.update()
    
    label_status_for_extraction.config(text=f"Zakończono! Wyodrębniono {processed_count} zdjęć.")
    messagebox.showinfo("Sukces", f"Wyodrębniono {processed_count} zdjęć!\nZnajdziesz je w folderze 'Miniatury ofert'")

def choose_folder(label, button):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        label.config(text=f"Wybrany folder: {folder_selected}")
        button.config(state="normal")
        return folder_selected

def on_border_width_change(value):
    """Aktualizuje pole tekstowe gdy zmienia się suwak"""
    border_width_entry.delete(0, 'end')
    border_width_entry.insert(0, str(int(float(value))))

def on_border_width_entry_change(event=None):
    """Aktualizuje suwak gdy zmienia się pole tekstowe"""
    try:
        value = int(border_width_entry.get())
        if 1 <= value <= 100:
            border_width_scale.set(value)
        else:
            # Przywróć poprzednią wartość jeśli poza zakresem
            border_width_scale.set(border_width_scale.get())
    except ValueError:
        # Przywróć poprzednią wartość jeśli nieprawidłowy format
        border_width_scale.set(border_width_scale.get())

def on_start_for_frames():
    folder = label_folder_for_frames.cget("text").replace("Wybrany folder: ", "")
    if folder:
        try:
            border_size = int(border_width_entry.get())
            if not (1 <= border_size <= 100):
                messagebox.showerror("Błąd", "Szerokość ramki musi być w zakresie 1-100 pikseli.")
                return
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź prawidłową szerokość ramki (1-100).")
            return
        
        # Wyłącz przycisk podczas przetwarzania
        button_start_for_frames.config(state="disabled")
        add_white_frame_to_images(folder, border_size)
        button_start_for_frames.config(state="normal")

def on_start_for_extraction():
    folder = label_folder_for_extraction.cget("text").replace("Wybrany folder: ", "")
    if folder:
        # Wyłącz przycisk podczas przetwarzania
        button_start_for_extraction.config(state="disabled")
        extract_images(folder)
        button_start_for_extraction.config(state="normal")

# Główny program
if __name__ == "__main__":
    root = Tk()
    root.title("vSprint - ramki do zdjęć")
    root.geometry("700x700")
    root.eval('tk::PlaceWindow . center')
    root.configure(bg='#ffffff')

    # Konfiguracja stylu
    style = ttk.Style()
    style.theme_use('clam')

    # Nowoczesne style - Bootstrap-inspired
    style.configure('TNotebook', background='#ffffff', borderwidth=0)
    style.configure('TNotebook.Tab', padding=[30, 15], background='#f8f9fa', foreground='#6c757d', 
                    font=('Segoe UI', 10, 'bold'), borderwidth=0, focuscolor='none')
    style.map('TNotebook.Tab', background=[('selected', '#ffffff'), ('active', '#e9ecef')], 
              focuscolor=[('!focus', 'none')])
    style.configure('TFrame', background='#ffffff')
    style.configure('TProgressbar', background='#007bff', troughcolor='#e9ecef', borderwidth=0, lightcolor='#007bff', darkcolor='#007bff')

    notebook = ttk.Notebook(root)
    tab_frame, tab_extract = ttk.Frame(notebook), ttk.Frame(notebook)
    notebook.add(tab_frame, text="Ramki")
    notebook.add(tab_extract, text="Wyodrębnij zdjęcia")
    notebook.pack(fill="both", expand=True, pady=10)

    # Główny kontener z paddingiem
    main_container = Frame(tab_frame, bg='#ffffff')
    main_container.pack(fill='both', expand=True, padx=20, pady=15)

    # Nagłówek
    header_frame = Frame(main_container, bg='#ffffff')
    header_frame.pack(fill='x', pady=(0, 20))

    title_label = Label(header_frame, text="🎨 Dodaj ramki do zdjęć", 
                       font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
    title_label.pack()

    subtitle_label = Label(header_frame, text="Wybierz folder zawierający zdjęcia bez ramek", 
                          font=('Segoe UI', 10), fg='#7f8c8d', bg='#ffffff')
    subtitle_label.pack(pady=(3, 0))

    # Sekcja kontroli szerokości ramki
    control_section = Frame(main_container, bg='#f8f9fa', relief='flat', bd=0)
    control_section.pack(fill='x', pady=(0, 20))

    # Tytuł sekcji
    section_title = Label(control_section, text="⚙️ Ustawienia ramki", 
                         font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#f8f9fa')
    section_title.pack(pady=(15, 8))

    # Kontrolki szerokości
    width_control_frame = Frame(control_section, bg='#f8f9fa')
    width_control_frame.pack(pady=10, padx=20)

    label_border_width = Label(width_control_frame, text="Szerokość ramki:", 
                              font=('Segoe UI', 11), fg='#495057', bg='#f8f9fa')
    label_border_width.pack(pady=(0, 10))

    # Kontener dla suwaka i pola tekstowego
    slider_container = Frame(width_control_frame, bg='#f8f9fa')
    slider_container.pack(pady=10)

    border_width_entry = Entry(slider_container, width=8, font=('Segoe UI', 12, 'bold'), 
                              justify='center', relief='solid', bd=2, bg='#ffffff',
                              fg='#2c3e50', insertbackground='#2c3e50')
    border_width_entry.insert(0, "50")
    border_width_entry.bind('<KeyRelease>', on_border_width_entry_change)
    border_width_entry.pack(side="left", padx=(0, 20))

    px_label = Label(slider_container, text="px", font=('Segoe UI', 11), 
                    fg='#7f8c8d', bg='#f8f9fa')
    px_label.pack(side="left", padx=(0, 20))

    border_width_scale = Scale(slider_container, from_=1, to=100, orient="horizontal", 
                              command=on_border_width_change, length=350, 
                              resolution=1, tickinterval=25, showvalue=0,
                              bg='#f8f9fa', troughcolor='#e9ecef', 
                              activebackground='#3498db', highlightbackground='#3498db',
                              sliderrelief='flat', sliderlength=25, highlightthickness=0)
    border_width_scale.set(50)
    border_width_scale.pack(side="left")

    # Sekcja wyboru folderu
    folder_section = Frame(main_container, bg='#ffffff')
    folder_section.pack(fill='x', pady=(0, 20))

    folder_title = Label(folder_section, text="📁 Wybierz folder", 
                        font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#ffffff')
    folder_title.pack(pady=(0, 10))

    button_choose_for_frames = Button(folder_section, text="Przeglądaj foldery", 
                                     command=lambda: choose_folder(label_folder_for_frames, button_start_for_frames),
                                     font=('Segoe UI', 11, 'bold'), bg='#95a5a6', fg='white', 
                                     relief='flat', bd=0, padx=25, pady=12,
                                     activebackground='#7f8c8d', activeforeground='white',
                                     cursor='hand2')
    button_choose_for_frames.pack(pady=(0, 10))

    label_folder_for_frames = Label(folder_section, text="Nie wybrano folderu.", 
                                   font=('Segoe UI', 10), fg='#7f8c8d', bg='#ffffff')
    label_folder_for_frames.pack(pady=5)

    # Sekcja startu
    start_section = Frame(main_container, bg='#ffffff')
    start_section.pack(fill='x', pady=(0, 15))

    button_start_for_frames = Button(start_section, text="🚀 Rozpocznij dodawanie ramek", 
                                    state="disabled", command=on_start_for_frames,
                                    font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white', 
                                    relief='flat', bd=0, padx=35, pady=12,
                                    activebackground='#229954', activeforeground='white',
                                    cursor='hand2')
    button_start_for_frames.pack(pady=8)

    # Progress bar dla ramek
    progress_section = Frame(main_container, bg='#ffffff')
    progress_section.pack(fill='x', pady=(0, 10))

    progress_bar_frames = ttk.Progressbar(progress_section, mode='determinate', length=500)
    progress_bar_frames.pack(pady=10)

    label_status_for_frames = Label(progress_section, text="", font=('Segoe UI', 10), 
                                   fg='#27ae60', bg='#ffffff')
    label_status_for_frames.pack(pady=5)

    # Druga zakładka - wyodrębnianie
    main_container_extract = Frame(tab_extract, bg='#ffffff')
    main_container_extract.pack(fill='both', expand=True, padx=20, pady=15)

    # Nagłówek
    header_frame_extract = Frame(main_container_extract, bg='#ffffff')
    header_frame_extract.pack(fill='x', pady=(0, 20))

    title_label_extract = Label(header_frame_extract, text="📤 Wyodrębnij zdjęcia", 
                               font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
    title_label_extract.pack()

    subtitle_label_extract = Label(header_frame_extract, text="Wybierz folder zawierający foldery ze zdjęciami ofert", 
                                  font=('Segoe UI', 10), fg='#7f8c8d', bg='#ffffff')
    subtitle_label_extract.pack(pady=(3, 0))

    # Sekcja wyboru folderu
    folder_section_extract = Frame(main_container_extract, bg='#ffffff')
    folder_section_extract.pack(fill='x', pady=(0, 20))

    folder_title_extract = Label(folder_section_extract, text="📁 Wybierz folder", 
                                font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#ffffff')
    folder_title_extract.pack(pady=(0, 10))

    button_choose_for_extraction = Button(folder_section_extract, text="Przeglądaj foldery", 
                                         command=lambda: choose_folder(label_folder_for_extraction, button_start_for_extraction),
                                         font=('Segoe UI', 11, 'bold'), bg='#95a5a6', fg='white', 
                                         relief='flat', bd=0, padx=25, pady=12,
                                         activebackground='#7f8c8d', activeforeground='white',
                                         cursor='hand2')
    button_choose_for_extraction.pack(pady=(0, 10))

    label_folder_for_extraction = Label(folder_section_extract, text="Nie wybrano folderu.", 
                                       font=('Segoe UI', 10), fg='#7f8c8d', bg='#ffffff')
    label_folder_for_extraction.pack(pady=5)

    # Sekcja startu
    start_section_extract = Frame(main_container_extract, bg='#ffffff')
    start_section_extract.pack(fill='x', pady=(0, 15))

    button_start_for_extraction = Button(start_section_extract, text="🚀 Rozpocznij wyodrębnianie", 
                                        state="disabled", command=on_start_for_extraction,
                                        font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white', 
                                        relief='flat', bd=0, padx=35, pady=12,
                                        activebackground='#229954', activeforeground='white',
                                        cursor='hand2')
    button_start_for_extraction.pack(pady=8)

    # Progress bar dla wyodrębniania
    progress_section_extract = Frame(main_container_extract, bg='#ffffff')
    progress_section_extract.pack(fill='x', pady=(0, 10))

    progress_bar_extraction = ttk.Progressbar(progress_section_extract, mode='determinate', length=500)
    progress_bar_extraction.pack(pady=10)

    label_status_for_extraction = Label(progress_section_extract, text="", font=('Segoe UI', 10), 
                                       fg='#27ae60', bg='#ffffff')
    label_status_for_extraction.pack(pady=5)

    # Uruchom program
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program zakończony przez użytkownika")
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        root.quit()
