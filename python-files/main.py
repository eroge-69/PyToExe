import customtkinter as ctk

# Design-Farben
ORANGE = "#FF8000"
HINTERGRUND = "#121212"
TEXTFARBE = "#FFFFFF"

# Custom GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class StrukturGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧱 Struktur + Inhalt Generator")
        self.geometry("700x500")
        self.configure(fg_color=HINTERGRUND)

        # Zielpfad
        self.pfad_label = ctk.CTkLabel(self, text="📁 Zielverzeichnis:", text_color=TEXTFARBE)
        self.pfad_label.pack(pady=(15, 0))

        self.pfad_entry = ctk.CTkEntry(self, width=580, fg_color="#1E1E1E", text_color=TEXTFARBE)
        self.pfad_entry.pack(pady=(5, 10))

        self.browse_button = ctk.CTkButton(self, text="📂 Durchsuchen", fg_color=ORANGE, hover_color="#cc6600")
        self.browse_button.pack()

        # Strukturfeld
        self.struktur_label = ctk.CTkLabel(self, text="🗂️ Struktur (mit oder ohne Inhalt):", text_color=TEXTFARBE)
        self.struktur_label.pack(pady=(20, 5))

        self.struktur_text = ctk.CTkTextbox(self, width=650, height=300, fg_color="#1E1E1E", text_color=TEXTFARBE)
        self.struktur_text.pack()

        # Aktion
        self.erstelle_button = ctk.CTkButton(self, text="🚀 Struktur erstellen", fg_color=ORANGE, hover_color="#cc6600")
        self.erstelle_button.pack(pady=15)

if __name__ == "__main__":
    app = StrukturGenerator()
    app.mainloop()
