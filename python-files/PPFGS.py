import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import hmac, hashlib, base64, os, json

# --- Sistema di licenza ---
SECRET_KEY = b"AZKBD-99AA4-33BCX-ZK3VZ-OO00E"
LICENSE_FILE = "license.json"  # File locale dove salviamo la licenza attivata

def validate_license(license_key: str) -> bool:
    try:
        user_id, signature_b64 = license_key.split(":")
        expected_sig = hmac.new(SECRET_KEY, user_id.encode(), hashlib.sha256).digest()
        return hmac.compare_digest(expected_sig, base64.urlsafe_b64decode(signature_b64))
    except Exception:
        return False

def save_license(license_key: str):
    with open(LICENSE_FILE, "w") as f:
        json.dump({"license": license_key}, f)

def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
            return data.get("license")
    return None

# --- Finestra di attivazione ---
def license_window():
    root = tk.Tk()
    root.title("PPFSG_[UNACTIVATED]")
    root.resizable(False, False)  # 🔒 disabilita full screen e resize

    tk.Label(root, text="Inserisci la tua License Key:").pack(pady=5)
    license_entry = tk.Entry(root, width=50)
    license_entry.pack(pady=5)

    def check_key():
        key = license_entry.get().strip()
        if validate_license(key):
            save_license(key)
            messagebox.showinfo("Successo", "Licenza valida! Ora puoi usare il programma.")
            root.destroy()
            modify_paypal_balance_gui(True)
        else:
            messagebox.showerror("Errore", "Licenza non valida. Riprova.")

    tk.Button(root, text="Attiva", command=check_key, bg="lightblue").pack(pady=10)

    def on_close():
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# --- Programma "vero" ---
def modify_paypal_balance_gui(activated: bool):
    def select_image():
        file_path = filedialog.askopenfilename(
            title="Seleziona l'immagine",
            filetypes=[("Immagini", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            image_path_var.set(file_path)

    def save_image():
        file_path = filedialog.asksaveasfilename(
            title="Salva immagine modificata",
            defaultextension=".png",
            filetypes=[("Immagini PNG", "*.png")]
        )
        return file_path

    def process_image():
        saved_key = load_license()
        if not (saved_key and validate_license(saved_key)):
            messagebox.showwarning("Attivazione richiesta", "Devi attivare il programma per generare l'immagine.")
            license_window()
            return

        try:
            image_path = image_path_var.get()
            new_balance = balance_var.get()
            if not image_path or not new_balance:
                raise ValueError("Seleziona immagine e inserisci saldo.")
            
            output_path = save_image()
            if not output_path:
                raise ValueError("Devi scegliere dove salvare l'immagine.")

            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            font_path = "Futura Maxi CG Bold Regular.otf"
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Font non trovato: {font_path}")
            font = ImageFont.truetype(font_path, size=55)

            text_color = (0, 0, 0)
            text_position = (80, 285)
            draw.text(text_position, new_balance, font=font, fill=text_color)

            image.save(output_path)
            messagebox.showinfo("Successo", f"Immagine salvata in: {output_path}")

        except Exception as e:
            messagebox.showerror("Errore", str(e))

    root = tk.Tk()
    root.title("PPFSG_[ACTIVATED]" if activated else "PPFSG_[UNACTIVATED]")
    root.resizable(False, False)  # 🔒 disabilita full screen e resize

    image_path_var = tk.StringVar()
    balance_var = tk.StringVar()

    tk.Label(root, text="Seleziona immagine:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Entry(root, textvariable=image_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="Sfoglia", command=select_image).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="Nuovo saldo:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Entry(root, textvariable=balance_var, width=50).grid(row=1, column=1, padx=10, pady=5)

    tk.Button(root, text="Genera Immagine", command=process_image, bg="lightblue").grid(row=2, column=0, columnspan=3, pady=20)

    root.mainloop()

# --- Avvio ---
if __name__ == "__main__":
    saved_key = load_license()
    if saved_key and validate_license(saved_key):
        modify_paypal_balance_gui(True)
    else:
        license_window()
