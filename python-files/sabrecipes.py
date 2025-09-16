import tkinter as tk
from tkinter import ttk

# Data: (Name, Ingredients, Craft Time)
recipes = [
    ("Bandito Axolito", ["2 Trippi Troppi", "2 Bandito Bobritto"], "7 minutes"),
    ("Malame Amarele", ["2 Tung Tung Tung Sahur", "1 Ta Ta Ta Ta Sahur", "1 Brr Brr Patapim"], "7 minutes"),
    ("Mangolini Parrocini", ["1 Pipi Kiwi", "1 Pipi Avocado", "1 Boneca Ambalabu", "1 Perochello Lemonchello"], "7 minutes"),
    ("Tirilikalika Tirilikalako", ["1 Cacto Hipopotamo", "1 Penguino Cocosino", "2 Cappuccino Assassino"], "15 minutes"),
    ("Caramello Filtrello", ["1 Salamino Penguino", "1 Bananita Dolphinita", "1 Chimpanzini Bananini", "1 Burbaloni Loliloli"], "15 minutes"),
    ("Signore Carapace", ["1 Brri Brri Bicus Dicus Bombicus", "1 Glorbo Fruttodrillo", "2 Penguino Cocosino"], "15 minutes"),
    ("Brutto Gialutto", ["2 Salamino Penguino", "1 Blueberrini Octopusini", "1 Rhino Toasterino"], "30 minutes"),
    ("Los Noobinis", ["3 Noobini Pizzanini", "1 Carrotini Brainini"], "30 minutes"),
    ("Gorillo Subwoofero", ["2 Spioniro Golubiro", "2 Orangutini Ananassini"], "30 minutes"),
    ("Las Capuchinas", ["2 Ballerina Cappuccina", "2 Tralalita Tralala"], "45 minutes"),
    ("Orcalita Orcala", ["2 Orcalero Orcala", "1 Tralalita Tralala", "1 Espresso Signora"], "45 minutes"),
    ("Piccionetta Machina", ["1 Piccione Macchina", "1 Matteo", "2 Gattatino Nyanino"], "45 minutes"),
    ("Antonio", ["2 Ganganzelli Trulala", "1 Bombardiro Crocodilo", "1 Frigo Camelo"], "45 minutes"),
    ("Anpali Babel", ["3 Te Te Te Sahur", "1 Mastodontico Telepiedone"], "45 minutes"),
    ("La Karkerkar Combinasion", ["2 La Grande Combinasion", "2 Karkerkar Kurkur"], "1 hour 30 minutes"),
    ("La Sahur Combinasion", ["1 Ta Ta Ta Ta Sahur", "1 Te Te Te Sahur", "1 Graipuss Medussi", "1 Job Job Job Sahur"], "1 hour 30 minutes"),
    ("Tralaledon", ["3 Tralalero Tralala", "1 Nuclearo Dinossauro"], "1 hour 30 minutes"),
    ("Fragelo La La La", ["3 Odin Din Din Dun", "1 Sammyni Spyderini"], "1 hour 30 minutes"),
    ("Los Bros", ["1 Los Tungtungtungcitos", "2 Los Combinasion", "1 Los Tralaleritos"], "1 hour 30 minutes"),
    ("Trenzostruzzo Turbo 4000", ["2 Girafa Celestre", "2 Trenostruzzo Turbo 3000"], "1 hour 30 minutes")
]

# App window
root = tk.Tk()
root.title("Steal A Brainrot - Crafting Recipes")
root.geometry("950x600")
root.configure(bg="#181825")

# Fonts
try:
    import tkinter.font as tkFont
    font_title = tkFont.Font(family="Fredoka One", size=18)
    font_header = tkFont.Font(family="Fredoka One", size=12)
    font_content = tkFont.Font(family="Fredoka One", size=10)
except:
    font_title = ("Helvetica", 18, "bold")
    font_header = ("Helvetica", 12, "bold")
    font_content = ("Helvetica", 10)

# Header Label
title_label = tk.Label(root, text="Steal A Brainrot Recipes", font=font_title, bg="#181825", fg="#ff5c8d")
title_label.pack(pady=20)

# Treeview style
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#282c34",
                foreground="white",
                rowheight=28,
                fieldbackground="#282c34",
                font=font_content)
style.configure("Treeview.Heading", font=font_header, background="#3c3f4a", foreground="#ff5c8d")
style.map("Treeview", background=[("selected", "#ff5c8d")])

# Treeview
columns = ("Name", "Ingredients", "Time")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
tree.heading("Name", text="Name")
tree.heading("Ingredients", text="Ingredients")
tree.heading("Time", text="Craft Time")
tree.column("Name", width=200)
tree.column("Ingredients", width=550)
tree.column("Time", width=120)

# Populate data
for name, ingredients, time in recipes:
    tree.insert("", "end", values=(name, ", ".join(ingredients), time))

# Scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)

# Layout
tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)

# Run app
root.mainloop()
