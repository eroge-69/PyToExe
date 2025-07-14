import tkinter as tk
import random
from tkinter import messagebox
from faker import Faker

# Erstelle eine Instanz der Faker-Bibliothek f�r zuf�llige Daten
fake = Faker('de_DE')

def generate_data():
    name = fake.first_name()
    surname = fake.last_name()
    address = fake.street_address()
    house_number = fake.building_number()
    postal_code = fake.zipcode()
    city = fake.city()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d.%m.%Y")
    gender = gender_var.get()

    # Anzeigen der generierten Daten im GUI
    result_label.config(text=f"Name: {name} {surname}\n"
                            f"Adresse: {address} {house_number}\n"
                            f"PLZ: {postal_code}\n"
                            f"Stadt: {city}\n"
                            f"Geburtsdatum: {birthdate}\n"
                            f"Geschlecht: {gender}")

# Hauptfenster der Anwendung
root = tk.Tk()
root.title("Zufallsgenerator f�r deutsche Daten")

# Eingabefelder f�r die Auswahl von m�nnlich oder weiblich
gender_var = tk.StringVar()
gender_var.set("M�nnlich")  # Standardwert ist M�nnlich

gender_label = tk.Label(root, text="Geschlecht:")
gender_label.pack()

gender_frame = tk.Frame(root)
gender_frame.pack()

male_radio = tk.Radiobutton(gender_frame, text="M�nnlich", variable=gender_var, value="M�nnlich")
male_radio.pack(side=tk.LEFT)

female_radio = tk.Radiobutton(gender_frame, text="Weiblich", variable=gender_var, value="Weiblich")
female_radio.pack(side=tk.LEFT)

# Button zum Generieren der Daten
generate_button = tk.Button(root, text="Generiere zuf�llige Daten", command=generate_data)
generate_button.pack()

# Label zum Anzeigen der generierten Daten
result_label = tk.Label(root, text="", font=("Arial", 12), justify=tk.LEFT)
result_label.pack(pady=10)

# Hauptloop der Anwendung
root.mainloop()

