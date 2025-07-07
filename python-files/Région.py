import tkinter as tk
from tkinter import messagebox

# Dictionnaire simplifié pour mapper les départements aux grandes régions
def get_region(code):
    try:
        code = code.upper().zfill(2)
        if code in ['75', '77', '78', '91', '92', '93', '94', '95']:
            return "ile de france"
        elif code in ['08', '10', '51', '52', '54', '55', '57', '67', '68', '88', '02', '59', '60', '62', '80']:
            return "nord est"
        elif code in ['01', '03', '04', '05', '06', '07', '13', '26', '38', '42', '43', '63', '69', '73', '74', '83', '84']:
            return "sud est"
        elif code in ['14', '18', '22', '27', '28', '29', '35', '36', '37', '41', '44', '45', '50', '53', '56', '61', '72', '76', '85']:
            return "ouest"
        elif code in ['09', '11', '12', '16', '17', '19', '23', '24', '31', '32', '33', '34', '40', '46', '47', '48', '64', '65', '66', '79', '81', '82', '86', '87']:
            return "sud ouest"
        else:
            return "inconnu"
    except:
        return "inconnu"

def find_region():
    code = entry.get().strip()
    region = get_region(code)
    messagebox.showinfo("Région", f"La région pour le département {code} est : {region}")

# Interface Tkinter
root = tk.Tk()
root.title("Trouver la région simplifiée")

label = tk.Label(root, text="Entrez les 2 premiers chiffres du département :")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=10)

button = tk.Button(root, text="Trouver la région", command=find_region)
button.pack(pady=20)

root.mainloop()
