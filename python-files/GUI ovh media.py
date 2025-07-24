import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import ovh
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
from urllib.parse import urlparse
import threading

# === Options du webdriver ===
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--no-sandbox')

# === Données de configuration ===
media_ids = {
    'sign-plus': 843,
    'sign-sedentary': 847,
    'sign-junior': 848,
    'sign-senior': 845,
    'sign-en': 852,
    'sign-de': 853,
    'sign-fr': 851,
    'sign-es': 913,
    'sign-nl': 990,
    'sign-sales': 911
}

zones = {
    'otexio.fr': ovh.Client(
        endpoint='ovh-eu',
        application_key='3490bcc70fc28895',
        application_secret='e173860ab799f06f75e19b22eea83d63',
        consumer_key='90b93f33a228d40c011b0534dc86e57a',
    ),
    'containers-service.eu': ovh.Client(
        endpoint='ovh-eu',
        application_key='5cb342c4145d4e5f',
        application_secret='9bfa2b51a366095f8b52046ae5cb59fa',
        consumer_key='94ce5f492d45923904f145b88ecc6fcc',
    )
}

zone_map = {
    'sign-sales': 'containers-service.eu'
}

# === Fonctions OVH ===
def update_dns(subd, target):
    zone = zone_map.get(subd, 'otexio.fr')
    client = zones[zone]

    for prefix in ['', 'www.']:
        full_subd = prefix + subd
        redirs = client.get(f'/domain/zone/{zone}/redirection', subDomain=full_subd)
        for redir in redirs:
            client.delete(f'/domain/zone/{zone}/redirection/{redir}')
        client.post(f'/domain/zone/{zone}/redirection',
                    subDomain=full_subd,
                    target=target,
                    type='visible',
                    permanent=False)

    client.post(f'/domain/zone/{zone}/refresh')

# === Fonction d'import d'image ===
def upload_image(subdomain, image_path):
    USER = "lucie.curtil@otexio.com"
    PASS = "LucCur1506*"
    media_id = media_ids[subdomain]
    URL_LOGIN = "https://admin.otexio.com/index.cfm?action=admin:login.form&fw1pk=1"
    URL_MEDIA = f"https://admin.otexio.com/index.cfm?action=admin:medias.form&id={media_id}"

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.get(URL_LOGIN)
    time.sleep(2)
    driver.find_element(By.NAME, "j_username").send_keys(USER)
    driver.find_element(By.NAME, "j_password").send_keys(PASS)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)

    driver.get(URL_MEDIA)
    time.sleep(2)
    try:
        driver.find_element(By.CSS_SELECTOR, "a[href='#tab-upload']").click()
        time.sleep(1)
    except Exception:
        pass

    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][name='file_upload']")
    abs_path = os.path.abspath(image_path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Fichier introuvable : {abs_path}")
    file_input.send_keys(abs_path)
    time.sleep(2)

    driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Enregistrer')]").click()
    time.sleep(2)

    try:
        alert = driver.find_element(By.CSS_SELECTOR, ".alert-danger")
        alert_text = alert.text.strip()
        if "déjà présent" in alert_text.lower() or "erreur" in alert_text.lower():
            driver.quit()
            raise Exception(f"🚫 Erreur détectée sur le site : {alert_text}")
    except NoSuchElementException:
        pass

    driver.get(URL_MEDIA + "#tab-information")
    time.sleep(2)
    checkbox = driver.find_element(By.ID, "clearCache")
    if not checkbox.is_selected():
        checkbox.click()
        time.sleep(1)

    driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Enregistrer')]").click()
    time.sleep(2)

    driver.quit()

# === Interface graphique ===
class DomainRow:
    def __init__(self, parent, subdomain, log_callback):
        self.subdomain = subdomain
        self.log = log_callback
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10, fill='x')

        tk.Label(self.frame, text=subdomain, width=12, anchor='w').grid(row=0, column=0, sticky='w')
        self.url_entry = tk.Entry(self.frame, width=40)
        self.url_entry.grid(row=0, column=1, padx=5)
        self.img_path = tk.StringVar()
        tk.Button(self.frame, text="CHARGER IMAGE", command=self.load_image).grid(row=0, column=2)
        tk.Button(self.frame, text="ENVOYER", command=self.apply_changes).grid(row=0, column=3, padx=5)
        self.label_img = tk.Label(self.frame, text="", fg="gray")
        self.label_img.grid(row=1, column=1, columnspan=3, sticky='w')
        self.preview_label = tk.Label(self.frame)
        self.preview_label.grid(row=2, column=1, columnspan=3, sticky='w')

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png")])
        if path:
            if not path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.log(f"Fichier non valide ignoré : {path}")
                messagebox.showwarning("Fichier invalide", "Veuillez sélectionner une image JPG ou PNG.")
                return

            self.original_img_path = path
            new_name = "sign-sales-cs.jpg" if self.subdomain == "sign-sales" else f"{self.subdomain}.jpg"
            new_path = os.path.join(os.path.dirname(path), new_name)
            self.temp_image_created = False

            if os.path.abspath(path) != os.path.abspath(new_path):
                shutil.copy(path, new_path)
                self.temp_image_created = True
                self.log(f"Image copiée et renommée : {new_name}")
            else:
                self.log(f"Image déjà nommée correctement : {new_name}")

            self.img_path.set(new_path)
            self.label_img.config(text=new_name)
            self.log(f"Image chargée pour {self.subdomain} : {new_name}")

            try:
                img = Image.open(new_path)
                img.thumbnail((100, 100))
                self.photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.photo)
            except Exception as e:
                self.log(f"Erreur lors de l'affichage de l'image : {e}")

    def apply_changes(self):
        thread = threading.Thread(target=self._apply_changes_thread)
        thread.start()

    def _apply_changes_thread(self):
        try:
            ip_or_url = self.url_entry.get().strip()
            img = self.img_path.get()

            if not ip_or_url and not img:
                self._show_warning("Rien à faire", f"Aucune donnée saisie pour {self.subdomain}.")
                return

            if ip_or_url:
                update_dns(self.subdomain, ip_or_url)
                self.log(f"🔁 Redirection créée pour {self.subdomain} → {ip_or_url}")

            if img:
                upload_image(self.subdomain, img)
                self.log(f"Image importée pour {self.subdomain} : {os.path.basename(img)}")
                if getattr(self, 'temp_image_created', False):
                    try:
                        os.remove(img)
                        self.log(f"Image temporaire supprimée : {os.path.basename(img)}")
                    except Exception as e:
                        self.log(f"Erreur lors de la suppression de l'image temporaire : {e}")

            self._show_info("Succès", f"Modifications appliquées pour {self.subdomain}.")

        except Exception as e:
            self.log(f"❌ Erreur lors de l'application des modifications pour {self.subdomain} : {e}")
            self._show_error("Erreur", f"Une erreur est survenue : {e}")

    def _show_info(self, title, message):
        self._show_messagebox(messagebox.showinfo, title, message)

    def _show_warning(self, title, message):
        self._show_messagebox(messagebox.showwarning, title, message)

    def _show_error(self, title, message):
        self._show_messagebox(messagebox.showerror, title, message)

    def _show_messagebox(self, func, title, message):
        def wrapper():
            func(title, message)
        self.frame.after(0, wrapper)

# === Lancement de l'interface ===
def main():
    root = tk.Tk()
    root.title("Gestion des sous-domaines et images")

    outer_frame = tk.Frame(root)
    outer_frame.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(outer_frame)
    scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    log_frame = tk.Frame(root)
    log_frame.pack(side='right', fill='y')
    tk.Label(log_frame, text="Logs").pack()
    log_text = tk.Text(log_frame, width=40, height=30, state='disabled')
    log_text.pack()

    def log(msg):
        log_text.config(state='normal')
        log_text.insert('end', msg + "\n")
        log_text.see('end')
        log_text.config(state='disabled')

    domain_rows = []
    for sd in media_ids:
        row = DomainRow(scrollable_frame, sd, log)
        domain_rows.append(row)

    def clear_all_fields():
        for row in domain_rows:
            row.url_entry.delete(0, tk.END)
            row.img_path.set("")
            row.label_img.config(text="")
            row.preview_label.config(image="")

    clear_btn = tk.Button(scrollable_frame, text="🔄 Rafraîchir tous les champs", command=clear_all_fields)
    clear_btn.pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    main()
