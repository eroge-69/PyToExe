import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import re
import shutil

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

FILENAME_STANDARD = "Globalpartner.json"
FILENAME_TEST = "Globalpartner-test.json"

current_filename = FILENAME_STANDARD  # valeur par défaut, sera changée après choix utilisateur
data = {}

def save_json():
    with open(current_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # Synchroniser fichier test si on sauvegarde dans standard
    if current_filename == FILENAME_STANDARD:
        shutil.copyfile(FILENAME_STANDARD, FILENAME_TEST)

def load_data():
    global data
    try:
        with open(current_filename, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {
            "Structures": [],
            "ADSN_Comments": {
                "AllowedValues": {
                    "Type": "Office, CSN, Conseil Régional, Chambre Interdépartementale, Centre Médiation, Comité technique",
                    "JobTitle": "Notaire, Collaborateur, Service"
                }
            }
        }

def ask_file_choice(root):
    choice_win = tk.Toplevel(root)
    choice_win.title("Choix du fichier JSON")
    choice_win.geometry("340x100")

    ttk.Label(choice_win, text="Choisir le fichier à modifier").pack(pady=10)

    btns_frame = ttk.Frame(choice_win)
    btns_frame.pack(pady=8)

    def select_standard():
        global current_filename
        current_filename = FILENAME_STANDARD
        choice_win.destroy()

    def select_test():
        global current_filename
        current_filename = FILENAME_TEST
        choice_win.destroy()

    ttk.Button(btns_frame, text="Modifier Standard", command=select_standard, width=18).grid(row=0, column=0, padx=15)
    ttk.Button(btns_frame, text="Modifier Test", command=select_test, width=18).grid(row=0, column=1, padx=15)

    choice_win.transient(root)
    choice_win.grab_set()
    root.wait_window(choice_win)

def is_valid_email(email):
    return EMAIL_REGEX.match(email) is not None

def get_types():
    types_raw = data.get('ADSN_Comments', {}).get('AllowedValues', {}).get('Type', '')
    if types_raw:
        return [x.strip() for x in types_raw.split(',')]
    return ["Office"]

def get_job_titles():
    titles_raw = data.get('ADSN_Comments', {}).get('AllowedValues', {}).get('JobTitle', '')
    if titles_raw:
        return [x.strip() for x in titles_raw.split(',')]
    return ["Notaire", "Collaborateur", "Service"]

def add_user(office_key, user):
    crpcen, _ = office_key.split(' - ', 1)
    for office in data.get("Structures", []):
        if office.get('CRPCEN') == crpcen:
            office['Details'][0].setdefault('EmailAddresses', []).append(user)
            save_json()
            return True
    return False

def remove_user(office_key, tech_mail):
    crpcen, _ = office_key.split(' - ', 1)
    for office in data.get("Structures", []):
        if office.get('CRPCEN') == crpcen:
            emails = office['Details'][0].get('EmailAddresses', [])
            for i, usr in enumerate(emails):
                if usr.get('TechnicalAddress') == tech_mail:
                    del emails[i]
                    save_json()
                    return True
    return False

def add_office(office):
    data.get('Structures', []).append(office)
    save_json()

def add_job_title(new_title):
    titles = get_job_titles()
    if new_title not in titles:
        titles.append(new_title)
        data.setdefault('ADSN_Comments', {}).setdefault('AllowedValues', {})['JobTitle'] = ', '.join(titles)
        save_json()
        return True
    return False

def add_type(new_type):
    types = get_types()
    if new_type not in types:
        types.append(new_type)
        data.setdefault('ADSN_Comments', {}).setdefault('AllowedValues', {})['Type'] = ', '.join(types)
        save_json()
        return True
    return False

def fmt_name(name):
    return name[:1].upper() + name[1:].lower() if name else ''

def get_offices_with_labels():
    offices = [(o.get('CRPCEN', '').strip(), o.get('Name', '').strip()) for o in data.get('Structures', [])]
    offices_sorted = sorted(offices, key=lambda x: x[1].lower())
    return [f"{c} - {fmt_name(n)}" for c, n in offices_sorted]

def office_key_from_label(label):
    if not label:
        return None
    parts = label.split(' - ', 1)
    if len(parts) != 2:
        return None
    crpcen, name_part = parts[0].strip(), parts[1].strip()
    for o in data.get('Structures', []):
        if o.get('CRPCEN') == crpcen and fmt_name(o.get('Name')) == name_part:
            return f"{crpcen} - {fmt_name(o.get('Name'))}"
    return None

def main():
    root = tk.Tk()
    root.title("Gestion Utilisateurs JSON")
    root.geometry("580x340")
    root.minsize(580, 340)

    style = ttk.Style(root)
    style.theme_use('clam')

    ask_file_choice(root)
    load_data()

    main_container = ttk.Frame(root)
    main_container.pack(fill='both', expand=True)

    fields_frame = ttk.Frame(main_container, padding=10)
    fields_frame.pack(side='top', anchor='w', fill='x')
    fields_frame.columnconfigure(1, weight=1)

    btn_frame = ttk.Frame(main_container, padding=5)
    btn_frame.pack(side='top', anchor='center', pady=10)
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    selected_office = tk.StringVar()
    firstname = tk.StringVar()
    lastname = tk.StringVar()
    job_title = tk.StringVar()
    job_title.set("Collaborateur")
    mail_tech = tk.StringVar()
    mail_pub = tk.StringVar()
    alias = tk.StringVar()

    def labeled_entry(parent, text, var, row, combo_vals=None):
        ttk.Label(parent, text=text + ":").grid(column=0, row=row, sticky="e", pady=2)
        if combo_vals:
            c = ttk.Combobox(parent, textvariable=var, values=combo_vals, state='readonly')
            c.grid(column=1, row=row, sticky="we", pady=2)
            return c
        else:
            e = ttk.Entry(parent, textvariable=var)
            e.grid(column=1, row=row, sticky="we", pady=2)
            return e

    offices_list = get_offices_with_labels()
    job_titles_list = get_job_titles()
    types_list = get_types()

    office_combo = ttk.Combobox(fields_frame, textvariable=selected_office, values=offices_list, state='readonly')
    office_combo.grid(column=1, row=0, sticky="we", pady=2)
    ttk.Label(fields_frame, text="Office:").grid(column=0, row=0, sticky="e", pady=2)

    labeled_entry(fields_frame, "Prénom", firstname, 1)
    labeled_entry(fields_frame, "Nom", lastname, 2)
    job_combo = ttk.Combobox(fields_frame, textvariable=job_title, values=job_titles_list, state='readonly')
    job_combo.grid(column=1, row=3, sticky="we", pady=2)
    ttk.Label(fields_frame, text='Titre:').grid(column=0, row=3, sticky="e", pady=2)

    labeled_entry(fields_frame, "Email technique", mail_tech, 4)
    labeled_entry(fields_frame, "Email publique", mail_pub, 5)
    labeled_entry(fields_frame, "Alias (optionnel)", alias, 6)

    def clear_inputs():
        firstname.set('')
        lastname.set('')
        job_title.set('Collaborateur')
        mail_tech.set('')
        mail_pub.set('')
        alias.set('')

    def validate_emails():
        for label, val in [('Email technique', mail_tech.get()), ('Email publique', mail_pub.get()), ('Alias', alias.get().strip())]:
            if label == 'Alias' and val == '':
                continue
            if not is_valid_email(val):
                messagebox.showerror("Erreur", f"L'adresse {label} n'est pas valide.")
                return False
        return True

    def add_user_action():
        if not selected_office.get():
            messagebox.showerror("Erreur", "Veuillez choisir un office.")
            return
        if not firstname.get() or not lastname.get() or not mail_tech.get() or not mail_pub.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return
        if not validate_emails():
            return
        key = office_key_from_label(selected_office.get())
        if not key:
            messagebox.showerror("Erreur", "Office incorrect.")
            return
        user = {
            'FirstName': firstname.get(),
            'LastName': lastname.get(),
            'JobTitle': job_title.get(),
            'TechnicalAddress': mail_tech.get(),
            'PublicAddress': mail_pub.get(),
            'Alias': alias.get().strip() or None
        }
        if add_user(key, user):
            messagebox.showinfo("Succès", f"Utilisateur ajouté à {selected_office.get()}.")
            clear_inputs()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout.")

    def add_office_action():
        def submit():
            nm = name_var.get().strip()
            cr = crpcen_var.get().strip()
            tp = type_var.get().strip()
            if not nm or not cr or not tp:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                return
            new_off = {
                'Name': nm,
                'CRPCEN': cr,
                'Type': tp,
                'Details': [{'TechnicalDomain': f"{cr}.notaires.fr", 'PublicDomain': 'notaires.fr', 'EmailAddresses': []}]
            }
            add_office(new_off)
            office_combo['values'] = get_offices_with_labels()
            messagebox.showinfo("Succès", "Nouvel office ajouté!")
            popup.destroy()

        popup = tk.Toplevel(root)
        popup.title("Ajouter un Office")
        popup.geometry('350x180')
        popup.columnconfigure(0, weight=1)
        popup.columnconfigure(1, weight=2)

        name_var = tk.StringVar()
        crpcen_var = tk.StringVar()
        type_var = tk.StringVar()
        type_var.set(types_list[0] if types_list else 'Office')

        ttk.Label(popup, text='Nom:').grid(row=0, column=0, sticky='e', pady=5, padx=5)
        ttk.Entry(popup, textvariable=name_var).grid(row=0, column=1, sticky='we', pady=5, padx=5)
        ttk.Label(popup, text='CRPCEN:').grid(row=1, column=0, sticky='e', pady=5, padx=5)
        ttk.Entry(popup, textvariable=crpcen_var).grid(row=1, column=1, sticky='we', pady=5, padx=5)
        ttk.Label(popup, text='Type:').grid(row=2, column=0, sticky='e', pady=5, padx=5)
        ttk.Combobox(popup, textvariable=type_var, values=types_list, state='readonly').grid(row=2, column=1, sticky='we', pady=5, padx=5)
        ttk.Button(popup, text='Ajouter', command=submit).grid(row=3, column=0, columnspan=2, pady=10)

    def add_job_title_action():
        new_title = simpledialog.askstring("Ajouter Job Title", "Entrez un nouveau titre:")
        if new_title:
            new_title = new_title.strip()
            if not new_title:
                messagebox.showerror("Erreur", "Titre vide impossible.")
                return
            titles = get_job_titles()
            if new_title in titles:
                messagebox.showinfo("Info", "Titre déjà existant.")
                return
            if add_job_title(new_title):
                job_titles_list.append(new_title)
                job_combo['values'] = job_titles_list
                job_combo.set(new_title)
                messagebox.showinfo("Succès", "Titre ajouté.")

    def add_type_action():
        new_type = simpledialog.askstring("Ajouter Type", "Entrez un nouveau type d'office:")
        if new_type:
            new_type = new_type.strip()
            if not new_type:
                messagebox.showerror("Erreur", "Type vide impossible.")
                return
            types = get_types()
            if new_type in types:
                messagebox.showinfo("Info", "Type déjà existant.")
                return
            if add_type(new_type):
                types_list.append(new_type)
                messagebox.showinfo("Succès", "Type ajouté.")

    def add_job_or_type():
        popup = tk.Toplevel(root)
        popup.title("Ajouter Job Title ou Type")
        popup.geometry('320x140')
        popup.columnconfigure(0, weight=1)

        choice_var = tk.StringVar(value='Job Title')

        ttk.Label(popup, text='Que voulez-vous ajouter ?').grid(row=0, column=0, pady=10, padx=10)
        ttk.Radiobutton(popup, text='Job Title', variable=choice_var, value='Job Title').grid(row=1, column=0, sticky='w', padx=30)
        ttk.Radiobutton(popup, text='Type d\'Office', variable=choice_var, value='Type').grid(row=2, column=0, sticky='w', padx=30)

        def confirm():
            popup.destroy()
            if choice_var.get() == 'Job Title':
                add_job_title_action()
            else:
                add_type_action()

        ttk.Button(popup, text='Valider', command=confirm).grid(row=3, column=0, pady=15)

    btn_frame = ttk.Frame(main_container, padding=5)
    btn_frame.pack(side='top', anchor='center', pady=10)
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    btn_add_user = ttk.Button(btn_frame, text='Ajouter Utilisateur', width=20, command=add_user_action)
    btn_add_user.grid(row=0, column=0, padx=10, pady=5)
    btn_del_user = ttk.Button(btn_frame, text='Supprimer Utilisateur', width=20, command=lambda: open_delete_window())
    btn_del_user.grid(row=0, column=1, padx=10, pady=5)
    btn_add_office = ttk.Button(btn_frame, text='Ajouter Office', width=20, command=add_office_action)
    btn_add_office.grid(row=1, column=0, padx=10, pady=5)
    btn_add_job_type = ttk.Button(btn_frame, text='Ajouter Job/Type', width=20, command=add_job_or_type)
    btn_add_job_type.grid(row=1, column=1, padx=10, pady=5)

    def open_delete_window():
        def on_office_select(evt=None):
            selected = office_var.get()
            users_list.delete(0, 'end')
            key = office_key_from_label(selected)
            if not key:
                return
            crpcen = key.split(' - ', 1)[0]
            for o in data.get('Structures', []):
                if o.get('CRPCEN') == crpcen:
                    users = o.get('Details', [{}])[0].get('EmailAddresses', [])
                    users_sorted = sorted(users, key=lambda u: (u.get('LastName', '').lower(), u.get('FirstName', '').lower()))
                    for usr in users_sorted:
                        users_list.insert('end', f"{usr.get('LastName', '')} {usr.get('FirstName', '')} - {usr.get('TechnicalAddress', '')}")
                    break

        def remove_selected():
            sel = users_list.curselection()
            if not sel:
                messagebox.showerror("Erreur", "Sélectionnez un utilisateur.")
                return
            user_info = users_list.get(sel[0])
            mail = user_info.split(' - ')[-1].strip()
            selected_office = office_var.get()
            key = office_key_from_label(selected_office)
            if not key:
                messagebox.showerror("Erreur", "Office introuvable.")
                return
            if messagebox.askyesno("Confirmer", f"Supprimer '{user_info}' ?"):
                if remove_user(key, mail):
                    messagebox.showinfo("Succès", "Utilisateur supprimé.")
                    on_office_select()
                else:
                    messagebox.showerror("Erreur", "Échec suppression.")

        win = tk.Toplevel(root)
        win.title('Supprimer Utilisateur')
        win.geometry('580x380')
        win.columnconfigure(0, weight=1)
        win.rowconfigure(1, weight=1)

        ttk.Label(win, text='Sélectionnez un office :').grid(row=0, column=0, sticky='w', padx=10, pady=8)
        office_var = tk.StringVar()
        office_cb = ttk.Combobox(win, textvariable=office_var, values=get_offices_with_labels(), state='readonly', width=50)
        office_cb.grid(row=0, column=0, sticky='we', padx=190)
        office_cb.bind('<<ComboboxSelected>>', on_office_select)

        users_list = tk.Listbox(win, height=18)
        users_list.grid(row=1, column=0, sticky='nsew', padx=10)

        ttk.Button(win, text='Supprimer Sélection', command=remove_selected).grid(row=2, column=0, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
