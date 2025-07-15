import os
import threading
import socket
import shutil
import subprocess
from tkinter import Tk, filedialog, Button, Label, Canvas, messagebox
from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import qrcode
from PIL import Image, ImageTk

app = Flask(__name__)

shared_folder = ""
host_ip = ""

@app.route('/')
def home():
    if not shared_folder:
        return "<h2>🚫 Aucun dossier partagé</h2>"
    client_ip = request.remote_addr
    files = os.listdir(shared_folder)
    # لا رفع من المتصفح
    return render_template_string('''
        <h1>📂 Fichiers disponibles</h1>
        <ul>
            {% for file in files %}
                <li><a href="/files/{{ file }}">{{ file }}</a></li>
            {% endfor %}
        </ul>
        <hr>
        <p>✅ Vous pouvez uniquement télécharger les fichiers disponibles.</p>
    ''', files=files)

@app.route('/files/<path:filename>')
def download_file(filename):
    full_path = os.path.join(shared_folder, filename)
    print(f"Trying to send file: {full_path}")
    if not os.path.isfile(full_path):
        return f"❌ File {filename} not found on server.", 404
    return send_from_directory(shared_folder, filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # فقط الرفع من التطبيق، المتصفح مابغيناش يرفع
    return "❌ Upload via browser disabled", 403

def run_flask():
    app.run(host='0.0.0.0', port=8000)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

def add_firewall_rule():
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule", 
             "name=FlaskApp", "dir=in", "action=allow", 
             "protocol=TCP", "localport=8000"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Firewall rule added successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to add firewall rule:", e)

def select_folder():
    global shared_folder, host_ip, qr_img
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        shared_folder = folder_selected
        host_ip = get_local_ip()
        label_info.config(text=f"📁 Dossier sélectionné : {shared_folder}")
        url = f"http://{host_ip}:8000/"
        label_link.config(text=f"🌐 Lien : {url}")

        qr = qrcode.make(url)
        qr = qr.resize((180, 180))
        qr_img = ImageTk.PhotoImage(qr)
        canvas_qr.create_image(90, 90, image=qr_img)

def upload_file_tk():
    if not shared_folder:
        messagebox.showwarning("Avertissement", "Veuillez d'abord choisir un dossier à partager.")
        return
    file_path = filedialog.askopenfilename()
    if file_path:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(shared_folder, filename)
        try:
            shutil.copy(file_path, dest_path)
            messagebox.showinfo("Succès", f"Fichier '{filename}' téléchargé avec succès dans le dossier partagé.")
            label_info.config(text=f"📁 Dernier fichier ajouté : {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement: {e}")

def start_hotspot():
    try:
        ssid = "EduShare_Local"
        password = "12345678"

        subprocess.run(["netsh", "wlan", "set", "hostednetwork", "mode=allow", f"ssid={ssid}", f"key={password}"], check=True)
        subprocess.run(["netsh", "wlan", "start", "hostednetwork"], check=True)

        messagebox.showinfo("Hotspot", f"✅ Hotspot activé avec succès !\nNom : {ssid}\nMot de passe : {password}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Erreur", "❌ Impossible d'activer le hotspot.\nLancez le programme en tant qu'administrateur.")

# تشغيل السيرفر Flask في Thread موازية
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# إضافة قاعدة Firewall تلقائياً
add_firewall_rule()

# واجهة Tkinter
root = Tk()
root.title("📤 Partage de fichiers - Professeur")
root.geometry("450x520")

label_title = Label(root, text="📤 Choisissez un dossier à partager", font=("Arial", 12))
label_title.pack(pady=10)

btn_select_folder = Button(root, text="📂 Choisir un dossier", command=select_folder)
btn_select_folder.pack(pady=10)

btn_upload = Button(root, text="⬆️ Télécharger un fichier", command=upload_file_tk)
btn_upload.pack(pady=10)

btn_hotspot = Button(root, text="🔥 Activer le Hotspot", command=start_hotspot, bg="orange", fg="white")
btn_hotspot.pack(pady=10)

label_info = Label(root, text="")
label_info.pack(pady=5)

label_link = Label(root, text="", fg="blue")
label_link.pack(pady=10)

canvas_qr = Canvas(root, width=180, height=180)
canvas_qr.pack(pady=10)

root.mainloop()
