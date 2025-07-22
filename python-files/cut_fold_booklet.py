import os
import shutil
import sys, tkinter.filedialog as fd
from collections import defaultdict
import tkinter as tk
import tkinter.filedialog as fd

import PyPDF2
import subprocess

def choice_savingNames(paths):
    path_map = {}
    future_default = False
    default_names = False
    prec_path = None

    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale

    for path in paths:
        if future_default:
            filename = os.path.basename(path).removesuffix('.pdf')
            val_for_all = path_map[prec_path] if not default_names else filename
            path_map[path] = val_for_all
            continue

        # Crea nuova finestra
        dialog = tk.Toplevel()
        dialog.title("Nome di Salvataggio")

        filename = os.path.basename(path).removesuffix('.pdf')

        label = tk.Label(dialog, text=f'Immetti il nome senza estensione per:\n"{filename}"')
        label.pack(pady=10)

        entry = tk.Entry(dialog, width=40)
        entry.insert(0, '')
        entry.pack(pady=10)

        apply_to_all_var = tk.BooleanVar()
        set_bool = tk.BooleanVar()
        check = tk.Checkbutton(dialog, text="Applica la scelta a tutti", variable=apply_to_all_var)
        check.pack()

        # Variabile di stato per sapere quando l'utente ha cliccato
        user_choice = {"done": False}

        def confirm():
            set_bool.set(False)
            name = entry.get().strip()
            path_map[path] = name if name else None
            user_choice["done"] = True
            dialog.destroy()

        def use_default():
            set_bool.set(False)
            path_map[path] = None
            user_choice["done"] = True
            dialog.destroy()

        def old_name():
            set_bool.set(True)
            path_map[path] = filename
            user_choice["done"] = True
            dialog.destroy()

        b1 = tk.Button(dialog, text="Conferma Nome", command=confirm)
        b2 = tk.Button(dialog, text="Usa Nome di Default", command=use_default)
        b3 = tk.Button(dialog, text="Usa il nome del file", command=old_name)
        b1.pack(pady=3)
        b3.pack(pady=3)
        b2.pack(pady=3)

        dialog.protocol("WM_DELETE_WINDOW", use_default)  # Se chiude la finestra

        dialog.wait_window()  # Aspetta che venga chiusa

        if apply_to_all_var.get():
            future_default = True
            prec_path = path
        default_names = set_bool.get()

    root.destroy()
    return path_map

def choice_Directory():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale
    pbool = tk.BooleanVar()

    dialog = tk.Toplevel()
    dialog.title("Nome di Salvataggio")

    label = tk.Label(dialog, text=f'Scegliere la Directory di Output:')
    label.pack(pady=10)

    # Variabile di stato per sapere quando l'utente ha cliccato
    user_choice = {"done": False, 'path': ''}

    def confirm():
        pbool.set(False)
        user_choice["done"] = True
        user_choice['path'] = fd.askdirectory()
        dialog.destroy()

    def use_default():
        pbool.set(True)
        user_choice["done"] = True
        dialog.destroy()

    b1 = tk.Button(dialog, text="Cambia Directory", command=confirm)
    b2 = tk.Button(dialog, text="Questa Directory", command=use_default)
    b1.pack(pady=3)
    b2.pack(pady=3)

    dialog.protocol("WM_DELETE_WINDOW", use_default)  # Se chiude la finestra

    dialog.wait_window()  # Aspetta che venga chiusa

    root.destroy()

    return pbool.get(), user_choice['path']


def generate_cut_fold_tex_no_blanks(pdf_filename, output_tex_name, default_path=True, path=''):
    reader = PyPDF2.PdfReader(pdf_filename)
    actual_num_pages = len(reader.pages)
    dest_dir = os.getcwd() if default_path else path
    os.makedirs(dest_dir, exist_ok=True)
    output_tex = os.path.join(dest_dir, output_tex_name)
    pdf_filename = os.path.basename(pdf_filename)

    def safe_page(p):
        return str(p) if 1 <= p <= actual_num_pages else ''

    page_order = []
    for i in range(0, actual_num_pages, 4):
        p1 = i + 1
        p2 = i + 2
        p3 = i + 3
        p4 = i + 4
        page_order.append((p3, p1, p4, p2))

    with open(output_tex, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[paperwidth=29.7cm,paperheight=21cm,landscape,margin=0cm]{geometry}\n")
        f.write("\\usepackage{pdfpages}\n")
        f.write("\\begin{document}\n\n")

        for group in page_order:
            front_pages = ",".join([p for p in [safe_page(group[0]), safe_page(group[1])] if p != ''])
            back_pages = ",".join([p for p in [safe_page(group[3]), safe_page(group[2])] if p != ''])

            if front_pages:
                f.write(f"\\includepdf[pages={{{front_pages}}},nup=2x1,landscape,frame=false,pagecommand={{}}]{{{pdf_filename}}}\n")
            if back_pages:
                f.write(f"\\includepdf[pages={{{back_pages}}},nup=2x1,landscape,frame=false,pagecommand={{}}]{{{pdf_filename}}}\n")

        f.write("\n\\end{document}\n")

    #print(f"Creato file LaTeX senza pagine vuote aggiunte: {output_tex}")

    # Compila automaticamente il file .tex
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", os.path.basename(output_tex)],
            cwd=dest_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        #print("Compilazione LaTeX completata con successo.")
    except subprocess.CalledProcessError:
        print("Errore durante la compilazione LaTeX.")
        return False

    #print(output_tex)
    clean_auxiliary_files(output_tex)
    return True


def clean_auxiliary_files(tex_file):
    base_name = os.path.splitext(tex_file)[0]
    extensions = [".aux", ".log", ".out", ".toc", ".tex"]
    removed = []

    for ext in extensions:
        file_to_delete = base_name + ext
        if os.path.exists(file_to_delete):
            try:
                os.remove(file_to_delete)
                removed.append(file_to_delete)
            except Exception as e:
                print(f"Errore durante la rimozione di {file_to_delete}: {e}")

    #if removed:
    #    print("File temporanei rimossi:")
    #    for f in removed:
    #        print(" -", f)

def select_files():
    paths = fd.askopenfilenames(filetypes=[('PDF Files', '*.pdf')])
    if len(paths) < 1:
        exit("Errore!\nNessun file selezionato")
    map_fileName = choice_savingNames(paths)
    for path in map_fileName.keys():
        if map_fileName[path] is None:
            map_fileName[path] = 'cut_fold_booklet'
    if len(map_fileName.values()) != len(set(map_fileName.values())):
        name_counter = defaultdict(int)
        new_map = {}

        for path, name in map_fileName.items():
            if name is None:
                new_map[path] = None
                continue

            name_counter[name] += 1
            if name_counter[name] == 1:
                new_map[path] = name  # primo uso, nome senza numero
            else:
                new_map[path] = f"{name} ({name_counter[name]})"  # aggiunge numero dal secondo in poi
        map_fileName = new_map

    bool_output, path_out = choice_Directory()
    #print(map_fileName, bool_output, path_out)
    err_bool = []

    for path in map_fileName.keys():
        temp = 'clone_temporary_file.pdf' if path_out == '' else os.path.join(path_out, 'clone_temporary_file.pdf')
        shutil.copy2(path, temp)
        err_bool.append(generate_cut_fold_tex_no_blanks(temp, f'{map_fileName[path]}.tex', bool_output, path_out))
        os.remove(temp)
    if False in err_bool:
        print("Errore durante la compilazione LaTeX.")
    else:
        print("Compilazione LaTeX completata con successo.")

#if __name__ == "__main__":
#    if len(sys.argv) < 2:
#        print("Uso: py cut_fold_booklet.py nomefile.pdf")
#    else:
#        pdffile = sys.argv[1]
#        generate_cut_fold_tex_no_blanks(pdffile)

if __name__ == "__main__":
    select_files()