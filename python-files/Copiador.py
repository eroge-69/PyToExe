import tkinter as tk

# Funcions per copiar al portapapers
def copia_usuari():
    root.clipboard_clear()
    root.clipboard_append("ALSBISDJ_079_100ba")
    label_status.config(text="Usuari copiat!", fg="#4ade80")  # verd suau

def copia_contrasenya():
    root.clipboard_clear()
    root.clipboard_append("Spoo9tKrwMwv")
    label_status.config(text="Contrasenya copiada!", fg="#4ade80")

# Funcions per hover (canviar color botó)
def on_enter_usuari(e):
    btn_usuari.config(bg="#3b82f6")  # blau clar

def on_leave_usuari(e):
    btn_usuari.config(bg="#2563eb")  # blau més fosc

def on_enter_contrasenya(e):
    btn_contrasenya.config(bg="#f97316")  # taronja clar

def on_leave_contrasenya(e):
    btn_contrasenya.config(bg="#ea580c")  # taronja més fosc

root = tk.Tk()
root.title("Menú de Copiar")
root.geometry("320x180")
root.configure(bg="#121212")  # fons negre fosquet

# Fonts i colors
font_boto = ("Segoe UI", 14, "bold")
color_usuari = "#2563eb"     # blau fosc
color_usuari_hover = "#3b82f6" 
color_contrasenya = "#ea580c" # taronja fosc
color_contrasenya_hover = "#f97316"
color_text = "#e5e7eb"       # gris clar

# Botó Usuari
btn_usuari = tk.Button(root, text="Usuari", fg=color_text, bg=color_usuari,
                       font=font_boto, bd=0, relief="flat",
                       activebackground=color_usuari_hover, cursor="hand2",
                       command=copia_usuari)
btn_usuari.place(x=40, y=40, width=110, height=50)
btn_usuari.bind("<Enter>", on_enter_usuari)
btn_usuari.bind("<Leave>", on_leave_usuari)

# Botó Contrasenya
btn_contrasenya = tk.Button(root, text="Contrasenya", fg=color_text, bg=color_contrasenya,
                           font=font_boto, bd=0, relief="flat",
                           activebackground=color_contrasenya_hover, cursor="hand2",
                           command=copia_contrasenya)
btn_contrasenya.place(x=170, y=40, width=110, height=50)
btn_contrasenya.bind("<Enter>", on_enter_contrasenya)
btn_contrasenya.bind("<Leave>", on_leave_contrasenya)

# Label d'estat (missatges)
label_status = tk.Label(root, text="", fg=color_text, bg="#121212", font=("Segoe UI", 10))
label_status.place(x=100, y=110)

# Crear botons rodons amb canvas (més complex, però fa botons arrodonits)
# Tkinter no suporta botons rodons nadius, però farem la il·lusió amb un canvas i funcions.

def create_rounded_button(master, text, x, y, w, h, bg_color, hover_color, command):
    canvas = tk.Canvas(master, width=w, height=h, bg=master["bg"], highlightthickness=0)
    canvas.place(x=x, y=y)
    
    radius = 20
    def draw_button(color):
        canvas.delete("all")
        # Dibuixa rectangle rodó
        canvas.create_arc((0,0,radius*2,radius*2), start=90, extent=90, fill=color, outline=color)
        canvas.create_arc((w-radius*2,0,w,h-radius*2), start=0, extent=90, fill=color, outline=color)
        canvas.create_arc((0,h-radius*2,radius*2,h), start=180, extent=90, fill=color, outline=color)
        canvas.create_arc((w-radius*2,h-radius*2,w,h), start=270, extent=90, fill=color, outline=color)
        canvas.create_rectangle((radius,0,w-radius,h), fill=color, outline=color)
        canvas.create_rectangle((0,radius,w,h-radius), fill=color, outline=color)
        # Text
        canvas.create_text(w//2, h//2, text=text, fill=color_text, font=font_boto)
    
    draw_button(bg_color)
    
    def on_enter(event):
        draw_button(hover_color)
    
    def on_leave(event):
        draw_button(bg_color)
    
    canvas.bind("<Button-1>", lambda e: command())
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    
    return canvas

# Si vols, pots substituir els botons tk.Button pels de canvas rodons així:
# btn_usuari_canvas = create_rounded_button(root, "Usuari", 40, 40, 110, 50, color_usuari, color_usuari_hover, copia_usuari)
# btn_contrasenya_canvas = create_rounded_button(root, "Contrasenya", 170, 40, 110, 50, color_contrasenya, color_contrasenya_hover, copia_contrasenya)

root.mainloop()
