import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import shutil
import json

# Lista do przechowywania nazw udostępnionych tekstur
shared_textures = []
icon_path = None

# Tworzenie głównego okna aplikacji
root = tk.Tk()
root.title("Minecraft Texture Pack Maker")
szerokosc = 800
wysokosc = 450
root.geometry(f"{szerokosc}x{wysokosc}")

# Tworzenie pola tekstowego z placeholderem dla nazwy
entry_pack_name = tk.Entry(
    root,
    font=("Arial", 12),
    justify="center"
)
entry_pack_name.insert(0, "Nazwa Texture packa...")
entry_pack_name.pack(pady=20, padx=20, fill="x")

# Tworzenie pola tekstowego z placeholderem dla opisu
entry_description = tk.Entry(
    root,
    font=("Arial", 12),
    justify="center"
)
entry_description.insert(0, "Opis")
entry_description.pack(pady=10, padx=20, fill="x")

# Funkcja do otwierania okna wyboru pliku dla ikony
def choose_icon():
    global icon_path
    file_path = filedialog.askopenfilename(
        title="Wybierz ikonę Texture Packa",
        filetypes=[("Pliki PNG", "*.png"), ("Wszystkie pliki", "*.*")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        if file_name != "pack.png":
            messagebox.showerror("Błąd", "Ikona musi nazywać się 'pack.png'!")
            return
        button_choose_icon.config(text=file_name)
        icon_path = file_path

# Funkcja do otwierania okna wyboru pliku dla przedmiotu
def choose_item():
    file_path = filedialog.askopenfilename(
        title="Wybierz teksturę przedmiotu",
        filetypes=[("Pliki PNG", "*.png"), ("Wszystkie pliki", "*.*")]
    )
    if file_path:
        texture_name = os.path.basename(file_path)
        shared_textures.append((texture_name, file_path))
        print(f"Dodano teksturę: {texture_name}")

# Funkcja do otwierania okna z udostępnionymi teksturami
def show_shared_textures():
    # Tworzenie nowego okna
    textures_window = tk.Toplevel(root)
    textures_window.title("Udostępnione tekstury")
    textures_window.geometry("400x300")
    
    # Nagłówek
    label = tk.Label(textures_window, text="Udostępnione tekstury:", font=("Arial", 14, "bold"))
    label.pack(pady=10)
    
    # Obszar tekstowy z przewijaniem
    text_area = scrolledtext.ScrolledText(textures_window, font=("Arial", 11))
    text_area.pack(padx=20, pady=10, fill="both", expand=True)
    
    # Wypisanie wszystkich udostępnionych tekstur
    if shared_textures:
        for texture_name, texture_path in shared_textures:
            text_area.insert(tk.END, f"• {texture_name}\n")
    else:
        text_area.insert(tk.END, "Brak udostępnionych tekstur")
    
    # Ustawienie trybu tylko do odczytu
    text_area.config(state=tk.DISABLED)

# Funkcja dla przycisku zapakuj do zip
def pack_to_zip():
    global icon_path
    
    # Pobierz nazwę packa
    pack_name = entry_pack_name.get()
    if pack_name == "Nazwa Texture packa..." or not pack_name.strip():
        messagebox.showerror("Błąd", "Proszę podać nazwę texture packa!")
        return
    
    # Sprawdź czy wybrano ikonę
    if not icon_path:
        messagebox.showerror("Błąd", "Proszę wybrać ikonę texture packa!")
        return
    
    # Sprawdź czy ikona ma poprawną nazwę
    if os.path.basename(icon_path) != "pack.png":
        messagebox.showerror("Błąd", "Wybrana ikona musi nazywać się 'pack.png'!")
        return
    
    # Pobierz opis
    description = entry_description.get()
    if description == "Opis":
        description = ""
    
    # Utwórz folder o nazwie packa
    folder_name = pack_name
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)
    
    # Skopiuj ikonę (już ma nazwę pack.png)
    shutil.copy2(icon_path, os.path.join(folder_name, "pack.png"))
    
    # Utwórz plik pack.mcmeta
    mcmeta_content = {
        "pack": {
            "pack_format": 34,
            "description": f"§e• {description}\n§6• {pack_name}"
        }
    }
    
    with open(os.path.join(folder_name, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(mcmeta_content, f, indent=4, ensure_ascii=False)
    
    # Utwórz strukturę folderów assets/minecraft/textures/item/
    assets_path = os.path.join(folder_name, "assets", "minecraft", "textures", "item")
    os.makedirs(assets_path, exist_ok=True)
    
    # Skopiuj wszystkie dodane tekstury do folderu item
    for texture_name, texture_path in shared_textures:
        shutil.copy2(texture_path, os.path.join(assets_path, texture_name))
    
    messagebox.showinfo("Sukces", f"Texture pack '{pack_name}' został utworzony!")
    print(f"Utworzono texture pack: {folder_name}")

# Tworzenie przycisku do wyboru ikony
button_choose_icon = tk.Button(
    root,
    text="Ustaw ikonę Texturepacka",
    font=("Arial", 12),
    command=choose_icon
)
button_choose_icon.pack(pady=(2, 10), padx=20, fill="x")

# Tworzenie przycisku do dodawania przedmiotu
button_add_item = tk.Button(
    root,
    text="Dodaj przedmiot",
    font=("Arial", 12),
    command=choose_item
)
button_add_item.pack(pady=10, padx=20, fill="x")

# Tworzenie przycisku do pokazywania udostępnionych tekstur
button_show_textures = tk.Button(
    root,
    text="Zobacz udostępnione pliki tekstur",
    font=("Arial", 12),
    command=show_shared_textures
)
button_show_textures.pack(pady=10, padx=20, fill="x")

# Tworzenie przycisku do pakowania do ZIP
button_pack_zip = tk.Button(
    root,
    text="Zapakuj do zip",
    font=("Arial", 12),
    command=pack_to_zip
)
button_pack_zip.pack(pady=10, padx=20, fill="x")

# Uruchomienie głównej pętli aplikacji
root.mainloop()