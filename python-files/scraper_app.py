import asyncio
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

collected_links = set()

async def scrape_groups(keyword, location, pages):
    global collected_links
    collected_links.clear()
    query = f'site:facebook.com/groups "{keyword}" "{location}"'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.google.com/search?q={query.replace(" ", "+")}')
        for _ in range(pages):
            await page.wait_for_timeout(1500)
            links = await page.eval_on_selector_all("a", "els => els.map(el => el.href)")
            for link in links:
                if "facebook.com/groups/" in link and not any(x in link for x in ["/posts/", "/videos/", "/photos/"]):
                    if "url?q=" in link:
                        try:
                            real_url = link.split("url?q=")[1].split("&")[0]
                            if "facebook.com/groups/" in real_url:
                                collected_links.add(real_url.split("?")[0])
                        except:
                            pass
                    else:
                        collected_links.add(link.split("?")[0])
            next_btn = await page.query_selector("a#pnnext")
            if next_btn:
                await next_btn.click()
            else:
                break
        await browser.close()

def export_to_excel():
    if not collected_links:
        messagebox.showwarning("No Data", "No links collected yet.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if file_path:
        df = pd.DataFrame({"Facebook Group Links": list(collected_links)})
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Saved", f"Saved {len(collected_links)} links.")

def start_scraping():
    keyword = keyword_entry.get().strip()
    location = location_entry.get().strip()
    try:
        pages = int(page_entry.get())
    except:
        messagebox.showerror("Invalid Input", "Pages must be a number.")
        return
    if not keyword or not location:
        messagebox.showwarning("Missing Input", "Please enter both keyword and location.")
        return
    scrape_button.config(state=tk.DISABLED)
    status_label.config(text="Scraping...")
    root.update()
    asyncio.run(scrape_groups(keyword, location, pages))
    status_label.config(text=f"Done! {len(collected_links)} links collected.")
    scrape_button.config(state=tk.NORMAL)

# UI
root = tk.Tk()
root.title("Facebook Group Scraper")
root.configure(bg="#1e1e1e")

ttk.Style().theme_use("default")
ttk.Style().configure("TLabel", background="#1e1e1e", foreground="white")
ttk.Style().configure("TButton", background="#333", foreground="white")
ttk.Style().configure("TEntry", fieldbackground="#333", foreground="white")

ttk.Label(root, text="Keyword:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
keyword_entry = ttk.Entry(root, width=30)
keyword_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="Location:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
location_entry = ttk.Entry(root, width=30)
location_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(root, text="Pages:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
page_entry = ttk.Entry(root, width=10)
page_entry.insert(0, "3")
page_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

scrape_button = ttk.Button(root, text="Start Scraping", command=start_scraping)
scrape_button.grid(row=3, column=0, columnspan=2, pady=10)

export_button = ttk.Button(root, text="Export to Excel", command=export_to_excel)
export_button.grid(row=4, column=0, columnspan=2, pady=5)

status_label = ttk.Label(root, text="", background="#1e1e1e")
status_label.grid(row=5, column=0, columnspan=2)

root.mainloop()