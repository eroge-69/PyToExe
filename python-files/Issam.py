import tkinter as tk
from tkinter import ttk


# Créer la fenêtre
fenetre = tk.Tk()
fenetre.geometry("900x900")
fenetre.configure(background="lightblue")
fenetre.title("Gestion des Employés")

# Définir le style
style = ("Arial", 14)

# Titre
lblTitre = tk.Label(fenetre, text="Formulaire Employé", width=15)
lblTitre.place(x=400, y=10)

# Nom
lblNom = tk.Label(fenetre, text="Nom", width=15, font=style, bg="#33ff22")
lblNom.place(x=100, y=50)
entryNom = tk.Entry(fenetre, font=style)
entryNom.place(x=300, y=50)

# ID
lblId = tk.Label(fenetre, text="ID", width=15, font=style, bg="#33ff22")
lblId.place(x=100, y=100)
entryId = tk.Entry(fenetre, font=style)
entryId.place(x=300, y=100)

# Prénom
lblPrenom = tk.Label(fenetre, text="Prénom", width=15, font=style, bg="#33ff22")
lblPrenom.place(x=500, y=50)
entryPrenom = tk.Entry(fenetre, font=style)
entryPrenom.place(x=700, y=50)

# Poste
lblPoste = tk.Label(fenetre, text="Poste", width=15, font=style, bg="#33ff22")
lblPoste.place(x=100, y=200)
entryPoste = tk.Entry(fenetre, font=style)
entryPoste.place(x=300, y=200)

# Tel
lblTelephone = tk.Label(fenetre, text="Téléphone", width=15, font=style, bg="#33ff22")
lblTelephone.place(x=100, y=250)
entryTelephone = tk.Entry(fenetre, font=style)
entryTelephone.place(x=300, y=250)


# === Tableau Treeview ===
colonnes = ("ID", "Nom", "Prénom", "Poste", "Téléphone")
tree = ttk.Treeview(fenetre, columns=colonnes, show="headings")
for col in colonnes:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.place(x=100, y=300)




def connecter():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Formulaire Employé"
    )
def ajouter():
    try:
        conn = connecter()
        cursor = conn.cursor()
        sql = "INSERT INTO stagiaires (id, nom, prenom, telephone, poste) VALUES (%s, %s, %s, %s, %s)"
        values = (entryId.get(), entryNom.get(), entryPrenom.get(), entryTelephone.get(), entryposte.get())
        cursor.execute(sql, values)
        conn.commit()
        messagebox.showinfo("Succès", "Stagiaire ajouté.")
        conn.close()
        afficher()
    except:
        messagebox.showerror("Erreur", "Échec de l'ajout.")
def supprimer():
    conn = connecter()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stagiaires WHERE id = %s", (entryId.get(),))
    conn.commit()
    conn.close()
    afficher()
    messagebox.showinfo("Succès", "Stagiaire supprimé.")
def afficher():
    conn = connecter()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stagiaires")
    rows = cursor.fetchall()
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()
def modifier():
    conn = connecter()
    cursor = conn.cursor()
    sql = "UPDATE stagiaires SET nom=%s, prenom=%s, telephone=%s, poste=%s WHERE id=%s"
    values = (entryNom.get(), entryPrenom.get(), entryTelephone.get(), entryAge.get(), entryId.get())
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

# === Boutons ===


btnAjouter = tk.Button(fenetre, text="Ajouter", font=style, command=ajouter)
btnAfficher = tk.Button(fenetre, text="Afficher", font=style, command=afficher)
btnModifier = tk.Button(fenetre, text="Modifier", font=style, command=modifier)
btnSupprimer = tk.Button(fenetre, text="Supprimer", font=style, command=supprimer)


btnAjouter.place(x=150, y=620)
btnSupprimer.place(x=250, y=620)
btnModifier.place(x=550, y=620)
btnAfficher.place(x=400, y=620)

fenetre.mainloop()