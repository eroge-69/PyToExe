import tkinter as tk
import os
import subprocess

def list_and_open_files():
    win = tk.Toplevel()
    win.title("📁 Kostis OS 3 Files")
    win.geometry("600x400")

    folder_path = r"C:\Users\Κωστής\Downloads\Kostis OS 3 Files"

    tk.Label(win, text=f"Τοποθεσία:\n{folder_path}", font=("Arial", 10)).pack(pady=5)

    listbox = tk.Listbox(win, width=80, height=20)
    listbox.pack(padx=10, pady=10)

    # Φόρτωση αρχείων
    if os.path.exists(folder_path):
        try:
            items = os.listdir(folder_path)
            if not items:
                listbox.insert(tk.END, "📂 Ο φάκελος είναι άδειος.")
            else:
                for item in items:
                    full_path = os.path.join(folder_path, item)
                    tag = "[DIR]" if os.path.isdir(full_path) else "[FILE]"
                    listbox.insert(tk.END, f"{tag} {item}")
        except Exception as e:
            listbox.insert(tk.END, f"⚠️ Σφάλμα: {e}")
    else:
        listbox.insert(tk.END, "❌ Ο φάκελος δεν βρέθηκε.")

    # Άνοιγμα αρχείου με διπλό κλικ
    def open_selected_file(event):
        try:
            selection = listbox.get(listbox.curselection())
            filename = selection.replace("[DIR]", "").replace("[FILE]", "").strip()
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                os.startfile(full_path)
        except Exception as e:
            print("❌ Σφάλμα ανοίγματος:", e)

    listbox.bind("<Double-Button-1>", open_selected_file)

    tk.Button(win, text="✖ Κλείσιμο", command=win.destroy).pack(pady=10)

# Εκκίνηση GUI
root = tk.Tk()
root.title("WinPy OS")
root.geometry("300x200")
tk.Button(root, text="📂 Kostis OS 3 Files", command=list_and_open_files).pack(pady=60)
root.mainloop()
