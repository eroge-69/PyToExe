import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def modifier_url():
    url = url_entry.get()
    nouveaux_str = params_entry.get()
    supprimer_str = supprimer_entry.get()

    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Ajouter ou modifier
        if nouveaux_str:
            for pair in nouveaux_str.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    query_params[key.strip()] = [value.strip()]

        # Supprimer
        if supprimer_str:
            for key in supprimer_str.split(','):
                query_params.pop(key.strip(), None)

        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))

        result_label.config(text=new_url)
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

# Interface graphique
app = tk.Tk()
app.title("Modificateur d'URL")

tk.Label(app, text="URL :").pack()
url_entry = tk.Entry(app, width=100)
url_entry.pack()

tk.Label(app, text="Paramètres à ajouter ou modifier (clé=valeur, séparés par virgules) :").pack()
params_entry = tk.Entry(app, width=100)
params_entry.pack()

tk.Label(app, text="Paramètres à supprimer (séparés par virgules) :").pack()
supprimer_entry = tk.Entry(app, width=100)
supprimer_entry.pack()

tk.Button(app, text="Modifier l'URL", command=modifier_url).pack(pady=10)

result_label = tk.Label(app, text="", wraplength=800, fg="blue")
result_label.pack()

app.mainloop()
