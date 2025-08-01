import customtkinter as ctk
from webbrowser import open
# Set appearance and theme
ctk.set_appearance_mode("dark")        # Options: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")    # Themes: "blue", "green", "dark-blue"

# Functions to open links
def jee1():
    open("https://www.pw.live/study/batches/arjuna-jee-2024-626729/batch-overview?")

def jee2():
    open("https://www.pw.live/study/batches/arjuna-jee-2-0-2024-429328/batch-overview?")

# App window
app = ctk.CTk()
app.title("PW Batches")
app.geometry("400x220")
app.resizable(False, False)

# Heading label
title_label = ctk.CTkLabel(app, text="Choose Your JEE Batch", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=(30, 20))

# Buttons
btn1 = ctk.CTkButton(app, text="Arjuna JEE 2024", width=200, command=jee1)
btn1.pack(pady=10)

btn2 = ctk.CTkButton(app, text="Arjuna JEE 2.0 2024", width=200, command=jee2)
btn2.pack(pady=10)

# Run app
app.mainloop()
