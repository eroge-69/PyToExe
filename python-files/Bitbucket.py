import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# === CONFIGURATIE ===
repo_url = "git@bitbucket.org:van_uitert_bv/handleiding.git"
current_pad = Path.cwd()  # Huidige map waarin het script draait
doel_pad = current_pad / "handleiding"  # De map waarin de repo wordt gekloond

# Submodules om te initialiseren bij clone
submodules = ["generiek", "specifiek", "Afbeeldingen"]

def run_git_command(command, cwd):
    result = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Fout bij uitvoeren van: {command}\n{result.stderr}")
    else:
        print(result.stdout.strip())

def split_path_submodule(full_path):
    p = Path(full_path)
    directory = p.parent
    submodule_name = p.name
    return directory, submodule_name
    
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Selecteer een submodule-map om bij te werken (of klik op X om te stoppen)")
    return Path(folder_selected) if folder_selected else None

def initial_clone():
    print(f"Clonen van hoofdrepository naar: {doel_pad}")
    run_git_command(f"git clone {repo_url} {doel_pad}", cwd=".")

    print("Initialiseren van submodules...")
    run_git_command("git submodule init", cwd=doel_pad)

    for submodule in submodules:
        print(f"Updaten van submodule: {submodule}")
        run_git_command(f"git submodule update --remote -- {submodule}", cwd=doel_pad)

        sub_path = doel_pad / submodule
        if not sub_path.exists():
            print(f"Submodulepad bestaat niet: {sub_path}")
            continue

        print(f"Schakelen naar 'Master' in submodule: {submodule}")
        run_git_command("git checkout Master", cwd=sub_path)
        run_git_command("git pull origin Master", cwd=sub_path)

def update_nested_submodules(pad, module, doel_pad):
    pad = Path(pad).resolve()

    if not pad.exists():
        print(f"Pad bestaat niet: {pad}")
        return

    # Controleer of pad een git repo is
    if not (pad / ".git").exists() and not (pad / ".git").is_file():
        print(f"Pad is geen geldige git repo/submodule: {pad}")
        return

    print(f"Initialiseren en updaten van submodule in: {pad}")

    # Bepaal pad relatief t.o.v. hoofdrepo
    try:
        relative_path = pad.relative_to(doel_pad).as_posix()
    except ValueError:
        print(f"{pad} ligt niet binnen hoofdpad {doel_pad}")
        return

    # Alleen de opgegeven submodule initialiseren en bijwerken
    run_git_command(f"git submodule init {module}", cwd=pad)
    run_git_command(f"git submodule update --remote -- {module}", cwd=pad)

    # Checkout & pull master branch
    run_git_command("git checkout Master", cwd=pad)
    run_git_command("git pull origin Master", cwd=pad)

def update_selected_submodules():
    while True:
        print("Selecteer de map van een submodule die je wilt updaten (of sluit het venster om te stoppen)...")
        path = select_folder()
        if not path:
            print("Geen map geselecteerd. Stoppen met selecteren.")
            break

        try:
            # Zorg dat het pad absoluut is en binnen doel_pad ligt
            path = path.resolve()
            relative_path = path.relative_to(doel_pad)
        except ValueError:
            print(f"Geselecteerd pad '{path}' ligt niet binnen hoofdpad '{doel_pad}'")
            show_popup("Ongeldig pad", "De geselecteerde map ligt niet binnen de hoofdrepository.")
            continue

        # Submodule pad opbreken t.o.v. doel_pad
        directory, submodule_name = split_path_submodule(relative_path)

        full_module_path = doel_pad / directory
        update_nested_submodules(full_module_path, submodule_name, doel_pad)

        show_popup("Submodule geüpdatet", f"De submodule '{submodule_name}' is bijgewerkt naar 'master'.")

def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)

def main():
    initial_clone()    
    update_selected_submodules()
    show_popup("Script afgerond", "Alle geselecteerde submodules zijn bijgewerkt.")

if __name__ == "__main__":
    main()
