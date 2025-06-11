import tkinter as tk
from tkinter import messagebox
import urllib.parse
import pyperclip

def generate_direct_download_link():
    input_url = url_entry.get().strip()
    if not input_url:
        messagebox.showwarning("Tühi väli", "Palun sisesta SharePointi faili link.")
        return

    try:
        parsed_url = urllib.parse.urlparse(input_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        file_path = parsed_url.path

        if not file_path:
            raise ValueError("Vigane URL – tee puudub.")

        encoded_path = urllib.parse.quote(file_path)
        download_link = f"{base_url}/_layouts/15/download.aspx?SourceUrl={encoded_path}"

        result_var.set(download_link)
        pyperclip.copy(download_link)
        messagebox.showinfo("Kopeeritud", "Allalaadimise link on kopeeritud lõikelauale.")
    except Exception as e:
        messagebox.showerror("Viga", f"Linki ei õnnestunud töödelda:\n{e}")

# GUI
root = tk.Tk()
root.title("SharePointi allalaadimise lingi generaator")

tk.Label(root, text="Kleebi SharePointi faili link:").pack(pady=(10, 0))
url_entry = tk.Entry(root, width=80)
url_entry.pack(padx=10, pady=5)

tk.Button(root, text="Genereeri allalaadimise link", command=generate_direct_download_link).pack(pady=10)

result_var = tk.StringVar()
tk.Entry(root, textvariable=result_var, width=80, state='readonly').pack(padx=10, pady=(0, 10))

root.mainloop()
