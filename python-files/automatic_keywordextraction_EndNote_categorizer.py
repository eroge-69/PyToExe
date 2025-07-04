import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import csv
import re
from collections import Counter

search_results = []
filtered_results = []
detected_keywords = []

def load_endnote_xml(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load XML: {e}")
        return None

def extract_metadata(record):
    def deep_find_text(parent, path, fallback):
        elem = parent.find(path)
        if elem is not None:
            style_elem = elem.find("style")
            if style_elem is not None and style_elem.text:
                return style_elem.text.strip()
        return fallback

    title = deep_find_text(record, ".//titles/title", "No Title")
    author_elems = record.findall(".//contributors/authors/author")
    authors = []
    for author in author_elems:
        style = author.find("style")
        if style is not None and style.text:
            authors.append(style.text.strip())
    author = ", ".join(authors) if authors else "Unknown Author"

    year = deep_find_text(record, ".//dates/year", "Unknown Year")
    journal = deep_find_text(record, ".//periodical/full-title", "No Journal")

    return title, author, year, journal

def detect_keywords_from_titles(root, top_n=10):
    title_words = []
    for record in root.findall(".//record"):
        title_elem = record.find(".//titles/title")
        if title_elem is not None:
            style_elem = title_elem.find("style")
            if style_elem is not None and style_elem.text:
                words = re.findall(r'\b\w+\b', style_elem.text.lower())
                title_words.extend(words)

    stopwords = {"the", "and", "in", "of", "a", "to", "on", "for", "by", "with",
                 "an", "at", "as", "from", "using", "based", "use", "analysis"}
    keywords = [w for w in title_words if w not in stopwords and len(w) > 3]
    top_keywords = Counter(keywords).most_common(top_n)
    return [kw for kw, _ in top_keywords]

def categorize_title(title, keywords):
    if not title:
        return "Uncategorized"
    matched = [kw for kw in keywords if re.search(rf"\b{kw}\b", title.lower())]
    if not matched:
        return "Uncategorized"
    elif len(matched) == 1:
        return f"{matched[0].capitalize()} Related"
    else:
        return f"{' & '.join(kw.capitalize() for kw in matched)} Crossover"

def run_analysis():
    global search_results, filtered_results, detected_keywords
    file_path = entry_file.get()
    root = load_endnote_xml(file_path)
    if root is None:
        return

    detected_keywords = detect_keywords_from_titles(root, top_n=10)
    search_results = []

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"🔍 Detected Keywords: {', '.join(detected_keywords)}\n\n")

    for record in root.findall(".//record"):
        title, author, year, journal = extract_metadata(record)
        category = categorize_title(title, detected_keywords)
        search_results.append((category, title, author, year, journal))

    filtered_results = list(search_results)  # Default: show all
    update_display(filtered_results)

def update_display(results):
    output_text.delete(1.0, tk.END)
    for category, title, author, year, journal in results:
        output_text.insert(tk.END, f"[{category}] {title}\n   ↪ Author: {author}, Year: {year}, Journal: {journal}\n\n")

def search_titles():
    global filtered_results
    keyword = entry_search.get().strip().lower()
    if not keyword:
        filtered_results = list(search_results)
    else:
        filtered_results = [r for r in search_results if keyword in r[1].lower()]
    update_display(filtered_results)

def export_to_csv():
    if not filtered_results:
        messagebox.showinfo("No Data", "Run analysis first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Category", "Title", "Author(s)", "Year", "Journal"])
            for row in filtered_results:
                writer.writerow(row)
        messagebox.showinfo("Success", f"Results exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save CSV: {e}")

# GUI setup
window = tk.Tk()
window.title("EndNote Auto-Categorizer")
window.geometry("800x650")

tk.Label(window, text="EndNote XML File:").pack()
entry_file = tk.Entry(window, width=60)
entry_file.pack()
tk.Button(window, text="Browse", command=lambda: entry_file.insert(0, filedialog.askopenfilename(title="Select XML", filetypes=[("XML files", "*.xml")]))).pack()

tk.Button(window, text="Analyze & Auto-Categorize", command=run_analysis).pack(pady=10)

# New Search Box
tk.Label(window, text="Search Title Keyword:").pack()
entry_search = tk.Entry(window, width=40)
entry_search.pack()
tk.Button(window, text="Search Titles", command=search_titles).pack(pady=5)

tk.Button(window, text="Export Results to CSV", command=export_to_csv).pack(pady=10)

output_text = tk.Text(window, wrap=tk.WORD, height=25)
output_text.pack(fill=tk.BOTH, expand=True)

window.mainloop()
