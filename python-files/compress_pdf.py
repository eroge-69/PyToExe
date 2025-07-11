import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Funzione per comprimere PDF con livello standard
def comprimi_pdf_default():
    # Apri dialog per scegliere il PDF
    file_path = filedialog.askopenfilename(
        title="Seleziona il PDF da comprimere",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_path:
        messagebox.showinfo("Info", "Nessun file selezionato. Operazione annullata.")
        return

    # Crea nome file di output
    base_name = os.path.splitext(file_path)[0]
    output_file = f"{base_name}_compressed.pdf"

    if os.path.exists(output_file):
        sovrascrivi = messagebox.askyesno(
            "Attenzione",
            f"Il file {output_file} esiste già. Sovrascrivere?"
        )
        if not sovrascrivi:
            messagebox.showinfo("Interrotto", "Elaborazione interrotta.")
            return

    # Percorso eseguibile Ghostscript (modifica se necessario)
    gs_path = r"C:\Programmi\gs\gs10.05.1\bin\gswin64.exe"

    # Livello compressione (standard)
    livello = "/ebook"

    # Costruisci comando Ghostscript
    comando = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={livello}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_file}",
        file_path
    ]

    try:
        subprocess.run(comando, check=True)
        messagebox.showinfo("Successo", f"File compresso creato:\n{output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Errore", f"Errore nella compressione.\nDettagli:\n{e}")

# Crea finestra principale
root = tk.Tk()
root.title("Comprimere PDF con Ghostscript")

# Pulsante compressione standard
btn = tk.Button(root, text="Compressione standard", command=comprimi_pdf_default, width=30, height=2)
btn.pack(padx=20, pady=20)

# Avvia loop
root.mainloop()