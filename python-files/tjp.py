import sys
import os
import tkinter as tk

def open_tajpan_file(file_path):
    root = tk.Tk()
    filename = os.path.basename(file_path)
    root.title(filename)
    root.geometry("600x400")

    # Ustawienie ikony z pliku PNG
    icon_path = "tjp_icon.png"  # podmień na nazwę swojego PNG
    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python tajpan.py <plik.tjp>")
    else:
        file_path = sys.argv[1]
        open_tajpan_file(file_path)
