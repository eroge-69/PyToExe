import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import filedialog, messagebox

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0"
}

def google_search(query, num_results=30):
    query = query.replace(' ', '+')
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.select("a"):
            href = a.get("href")
            if href and "/url?q=" in href:
                actual_url = href.split("/url?q=")[1].split("&")[0]
                if actual_url.endswith(".pdf") and "payment" in actual_url.lower():
                    links.append(actual_url)
        return list(set(links))
    except Exception as e:
        messagebox.showerror("Error", f"Search failed: {e}")
        return []

def download_pdfs(links, folder):
    for url in links:
        try:
            filename = os.path.basename(url.split("?")[0])
            filepath = os.path.join(folder, filename)
            response = requests.get(url, headers=HEADERS)
            with open(filepath, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

def browse_folder():
    folder = filedialog.askdirectory()
    folder_var.set(folder)

def run_search():
    query = query_entry.get()
    folder = folder_var.get()

    if not query or not folder:
        messagebox.showwarning("Input Needed", "Please enter a search query and select a download folder.")
        return

    result_box.delete(1.0, tk.END)
    result_box.insert(tk.END, f"Searching for: {query}...\n")

    links = google_search(query)
    result_box.insert(tk.END, f"Found {len(links)} PDF(s).\nDownloading...\n")

    download_pdfs(links, folder)
    result_box.insert(tk.END, "Download complete.\n")

# GUI
root = tk.Tk()
root.title("Public PDF Scraper (Ethical Use Only)")
root.geometry("600x400")

tk.Label(root, text="Enter Google-style Search Query:").pack(pady=5)
query_entry = tk.Entry(root, width=80)
query_entry.insert(0, 'site:.edu filetype:pdf "payment instructions"')
query_entry.pack()

tk.Label(root, text="Select Download Folder:").pack(pady=5)
folder_var = tk.StringVar()
tk.Entry(root, textvariable=folder_var, width=60).pack(side=tk.LEFT, padx=(10, 0))
tk.Button(root, text="Browse", command=browse_folder).pack(side=tk.LEFT, padx=5)

tk.Button(root, text="Search & Download", command=run_search).pack(pady=10)

result_box = tk.Text(root, height=10, width=80)
result_box.pack(pady=10)

root.mainloop()
