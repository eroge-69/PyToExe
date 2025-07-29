
import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_groups():
    niche = niche_entry.get()
    country = country_entry.get()
    platform = platform_entry.get()

    if not niche or not country:
        messagebox.showerror("خطأ", "يرجى إدخال النيش والدولة.")
        return

    query = f"site:chat.whatsapp.com \"{niche}\" \"{country}\""
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and "chat.whatsapp.com" in href:
                link = href.split("&")[0].replace("/url?q=", "")
                if link not in links:
                    links.append(link)

        if links:
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    for link in links:
                        f.write(link + "\n")
                messagebox.showinfo("تم", f"تم حفظ {len(links)} رابط في الملف.")
        else:
            messagebox.showinfo("لا توجد نتائج", "لم يتم العثور على روابط.")
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

# واجهة المستخدم
root = tk.Tk()
root.title("أداة استخراج مجموعات واتساب")
root.geometry("400x300")

tk.Label(root, text="النيش (مثال: gamer)").pack(pady=5)
niche_entry = tk.Entry(root, width=50)
niche_entry.pack()

tk.Label(root, text="الدولة (مثال: Canada)").pack(pady=5)
country_entry = tk.Entry(root, width=50)
country_entry.pack()

tk.Label(root, text="المنصة (مثال: WhatsApp)").pack(pady=5)
platform_entry = tk.Entry(root, width=50)
platform_entry.insert(0, "WhatsApp")
platform_entry.pack()

tk.Button(root, text="ابدأ البحث", command=search_groups).pack(pady=20)

root.mainloop()
