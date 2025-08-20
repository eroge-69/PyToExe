import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import csv

def scrape():
    urls = url_text.get("1.0", tk.END).strip().splitlines()
    if not urls:
        messagebox.showerror("Greška", "Unesi bar jedan URL!")
        return

    results_list.delete(0, tk.END)

    for url in urls:
        url = url.strip()
        if not url:
            continue

        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu da učitam stranicu:\n{url}\n{e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        firm_names = soup.find_all('h6')

        if not firm_names:
            continue

        for h in firm_names:
            name = h.get_text(strip=True)

            # pokušaj da nađe email u bloku gde je firma
            email = None
            parent = h.find_parent()
            if parent:
                mail_tag = parent.find("a", href=lambda x: x and "mailto:" in x)
                if mail_tag:
                    email = mail_tag.get("href").replace("mailto:", "").strip()

            line = f"{name} | {email if email else 'Nema email'}"
            results_list.insert(tk.END, line)


def delete_selected():
    selected = results_list.curselection()
    for i in reversed(selected):
        results_list.delete(i)


def export_csv():
    if results_list.size() == 0:
        messagebox.showwarning("Greška", "Nema podataka za izvoz.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV fajl", "*.csv")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Naziv firme", "Email"])

            for i in range(results_list.size()):
                line = results_list.get(i)
                if " | " in line:
                    name, email = line.split(" | ", 1)
                else:
                    name, email = line, ""
                writer.writerow([name, email])

        messagebox.showinfo("Uspeh", f"Podaci su izvezeni u:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Greška", f"Nisam uspeo da sačuvam fajl:\n{e}")


# GUI setup
root = tk.Tk()
root.title("Privredni imenik - Scraper (više URL-ova)")
root.geometry("900x650")

frm = ttk.Frame(root, padding=10)
frm.pack(fill=tk.BOTH, expand=True)

ttk.Label(frm, text="Unesi jedan ili više URL-ova (svaki u novom redu):").pack(anchor="w")
url_text = tk.Text(frm, height=5, width=100)
url_text.pack(fill=tk.X, pady=5)

ttk.Button(frm, text="Pretraži", command=scrape).pack(pady=5)

results_list = tk.Listbox(frm, height=20, font=("Arial", 10), selectmode=tk.EXTENDED)
results_list.pack(fill=tk.BOTH, expand=True, pady=5)

btn_frame = ttk.Frame(frm)
btn_frame.pack(pady=5)

ttk.Button(btn_frame, text="Obriši selektovano", command=delete_selected).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="Izvoz u CSV", command=export_csv).pack(side=tk.LEFT, padx=5)

root.mainloop()
