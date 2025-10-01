import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

filetypes = (("Text files", "*.txt"),)
input_file = ""
output_folder = ""

def choose_file():
    global input_file
    filename = fd.askopenfilename(filetypes=filetypes)
    if filename:
        input_file = filename
        inputfilelabel.config(text=os.path.basename(filename))

def choose_folder():
    global output_folder
    foldername = fd.askdirectory()
    if foldername:
        output_folder = foldername
        outputfolderlabel.config(text=os.path.basename(foldername))

def convert_file():
    global input_file, output_folder
    if not input_file or not output_folder:
        messagebox.showerror("Erreur", "Veuillez sélectionner un fichier et un dossier.")
        return
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        converted = []
        for line in lines:
            if len(line) >= 2:
                converted.append(f"{line[:2]}:{line[2:]}")

        result = ",".join(converted)

        output_path = os.path.join(output_folder, "output.csv")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

        messagebox.showinfo("Succès", f"Conversion terminée !\nFichier : {output_path}")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def open_output():
    global output_folder
    if output_folder:
        os.startfile(output_folder)  # Windows
    else:
        messagebox.showwarning("Attention", "Aucun dossier choisi.")

# ==== Interface graphique ====
main = tk.Tk()
main.title("auto csv")
main.config(bg="#E4E2E2")
main.geometry("203x412")

style = ttk.Style(main)
style.theme_use("clam")

# Bouton select file
style.configure("selectfilebutton.TButton", background="#E4E2E2", foreground="#000")
selectfilebutton = ttk.Button(main, text="select file", style="selectfilebutton.TButton", command=choose_file)
selectfilebutton.place(x=39, y=39, width=120, height=30)

# Bouton select output
style.configure("selectoutputbutton.TButton", background="#E4E2E2", foreground="#000")
selectoutputbutton = ttk.Button(main, text="select output", style="selectoutputbutton.TButton", command=choose_folder)
selectoutputbutton.place(x=39, y=79, width=120, height=30)

# Label input file
style.configure("inputfilelabel.TLabel", background="#E4E2E2", foreground="#000", anchor="center")
inputfilelabel = ttk.Label(main, text="Aucun fichier", style="inputfilelabel.TLabel")
inputfilelabel.place(x=39, y=119, width=120, height=30)

# Label output folder
style.configure("outputfolderlabel.TLabel", background="#E4E2E2", foreground="#000", anchor="center")
outputfolderlabel = ttk.Label(main, text="Aucun dossier", style="outputfolderlabel.TLabel")
outputfolderlabel.place(x=39, y=159, width=120, height=30)

# Bouton convert
style.configure("convertbutton.TButton", background="#E4E2E2", foreground="#000")
convertbutton = ttk.Button(main, text="convert", style="convertbutton.TButton", command=convert_file)
convertbutton.place(x=39, y=199, width=120, height=30)

# Bouton open output
style.configure("openoutputbutton.TButton", background="#E4E2E2", foreground="#000")
openoutputbutton = ttk.Button(main, text="open output", style="openoutputbutton.TButton", command=open_output)
openoutputbutton.place(x=39, y=239, width=120, height=30)

main.mainloop()


