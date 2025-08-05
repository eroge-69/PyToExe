import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, ttk
from googlesearch import search
import requests
import os
import threading

class BookDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Smart Book Downloader")
        self.root.geometry("820x620")
        self.root.configure(bg="#f0f8ff")

        self.links = []
        self.failed_links = []

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Smart Book Downloader", font=("Segoe UI", 16, "bold"),
                 bg="#f0f8ff", fg="#333").pack(pady=10)

        input_frame = tk.Frame(self.root, bg="#f0f8ff")
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Book Title / Topic:", font=("Segoe UI", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.query_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=45)
        self.query_entry.grid(row=0, column=1, padx=5)

        btn_frame = tk.Frame(self.root, bg="#f0f8ff")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🔍 Search Books", command=self.search_books, bg="#0078d4", fg="white",
                  font=("Segoe UI", 11), width=18).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="⬇ Download Selected", command=self.download_selected, bg="#28a745", fg="white",
                  font=("Segoe UI", 11), width=18).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="📥 Download All", command=self.download_all, bg="#17a2b8", fg="white",
                  font=("Segoe UI", 11), width=16).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="🗑 Clear List", command=self.clear_list, bg="#dc3545", fg="white",
                  font=("Segoe UI", 11), width=16).grid(row=0, column=3, padx=10)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.listbox = Listbox(list_frame, width=110, height=18, selectmode=tk.MULTIPLE, font=("Consolas", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar = Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.status_label = tk.Label(self.root, text="", fg="#333", bg="#f0f8ff", font=("Segoe UI", 10))
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=750, mode="determinate")
        self.progress.pack(pady=10)

    def search_books(self):
        query = self.query_entry.get().strip()

        if not query:
            messagebox.showwarning("Missing Input", "Please enter a book name or topic.")
            return

        self.status_label.config(text="Searching...")
        self.listbox.delete(0, tk.END)
        self.links.clear()
        self.failed_links.clear()

        try:
            search_query = f'"{query}" filetype:pdf book OR ebook OR site:archive.org OR site:libgen.is'
            for url in search(search_query, num_results=200):
                if url.lower().endswith(".pdf") and url not in self.links:
                    self.links.append(url)
                    self.listbox.insert(tk.END, url)
            self.status_label.config(text=f"✅ Found {len(self.links)} PDF book(s).")
        except Exception as e:
            self.status_label.config(text="❌ Search failed.")
            messagebox.showerror("Search Error", str(e))

    def download_selected(self):
        selected = [self.listbox.get(i) for i in self.listbox.curselection()]
        if not selected:
            messagebox.showinfo("No Selection", "Please select at least one book.")
            return
        threading.Thread(target=self.download_files, args=(selected,), daemon=True).start()

    def download_all(self):
        if not self.links:
            messagebox.showinfo("No Books", "No books to download.")
            return
        threading.Thread(target=self.download_files, args=(self.links,), daemon=True).start()

    def download_files(self, urls):
        folder = filedialog.askdirectory(title="Select folder to save books")
        if not folder:
            return

        self.progress["maximum"] = len(urls)
        self.progress["value"] = 0
        self.failed_links.clear()

        for i, url in enumerate(urls, 1):
            try:
                filename = os.path.basename(url.split("?")[0])
                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"
                filepath = os.path.join(folder, filename)

                self.status_label.config(text=f"⬇ Downloading {i}/{len(urls)}: {filename}")
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f"[Error] Could not download {url}: {e}")
                self.failed_links.append(url)
                idx = self.listbox.get(0, tk.END).index(url)
                self.listbox.itemconfig(idx, {'fg': 'red'})

            self.progress["value"] = i
            self.root.update_idletasks()

        if self.failed_links:
            self.status_label.config(text=f"⚠️ Completed with {len(self.failed_links)} failures (marked red).")
        else:
            self.status_label.config(text="✅ All books downloaded successfully.")

    def clear_list(self):
        self.listbox.delete(0, tk.END)
        self.links.clear()
        self.failed_links.clear()
        self.progress["value"] = 0
        self.status_label.config(text="List cleared.")

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = BookDownloader(root)
    root.mainloop()
