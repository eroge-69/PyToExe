import os
import sys
import requests
import zipfile
import io
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# ========== PATH FIX FOR BUNDLED .EXE ==========
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # When bundled by PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ========== MAIN FUNCTIONALITY ==========
def download_file(session, url, filename):
    try:
        response = session.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def build_chkn():
    product_id = entry.get().strip()
    if not product_id.isdigit():
        messagebox.showerror("Error", "Please enter a valid numeric Product ID.")
        return

    # Ask for save directory
    folder = filedialog.askdirectory(title="Select folder to save CHKN and textures")
    if not folder:
        return

    session = requests.Session()
    base_url = f"https://userimages-akm.imvu.com/productdata/{product_id}/1/"
    contents_url = base_url + "_contents.json"

    try:
        response = session.get(contents_url)
        response.raise_for_status()
        contents = response.json()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch _contents.json:\n{e}")
        return

    chkn_name = os.path.join(folder, f"{product_id}.chkn")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for entry_data in contents:
            name = entry_data.get("name")
            url_fragment = entry_data.get("url")
            if not name and not url_fragment:
                continue
            file_url = base_url + (url_fragment or name)
            file_name = name or os.path.basename(url_fragment)
            try:
                file_data = session.get(file_url).content
                zipf.writestr(file_name, file_data)
            except Exception as e:
                print(f"Failed to download {file_url}: {e}")

    with open(chkn_name, "wb") as f:
        f.write(buffer.getvalue())
    messagebox.showinfo("Success", f"CHKN downloaded to:\n{chkn_name}")

    # Show texture previews
    preview_frame.delete("all")
    x = 10
    y = 10
    for entry_data in contents:
        if "url" in entry_data and entry_data["url"].lower().endswith((".png", ".jpg", ".jpeg")):
            img_url = base_url + entry_data["url"]
            name = entry_data.get("name") or entry_data["url"]
            try:
                img_data = session.get(img_url).content
                image = Image.open(io.BytesIO(img_data))
                image.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(image)
                image_refs.append(img_tk)
                btn = tk.Button(canvas_frame, image=img_tk, command=lambda u=img_url, n=name: download_file(session, u, os.path.join(folder, n)))
                btn.place(x=x, y=y)
                x += 110
                if x > canvas_frame.winfo_width() - 120:
                    x = 10
                    y += 110
            except:
                continue

# ========== GUI SETUP ==========
root = tk.Tk()
root.title("Bella's Extractor ♡")
root.configure(bg="#fdd8e8")
root.iconbitmap(resource_path("BellaExtractor_FIXED.ico"))

header_img = Image.open(resource_path("BellaExtractor_Header_Rescaled.png"))
header_tk = ImageTk.PhotoImage(header_img)
header_label = tk.Label(root, image=header_tk, bg="#fdd8e8")
header_label.pack(pady=(10, 5))

tk.Label(root, text="Product ID:", font=("Arial", 12, "bold"), bg="#fdd8e8").pack()
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Build CHKN ♡", command=build_chkn).pack(pady=10)

canvas_frame = tk.Canvas(root, width=750, height=300, bg="#fdd8e8", highlightthickness=1, highlightbackground="#a8a8a8")
canvas_frame.pack(padx=10, pady=10)
preview_frame = canvas_frame
image_refs = []

root.mainloop()
