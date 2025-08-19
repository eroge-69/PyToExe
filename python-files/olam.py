import tkinter as tk
from tkinter import ttk
import csv
from collections import defaultdict

# Load data from enml file (tab-separated)
def load_data(filename="enml"):
    data = defaultdict(list)  # word -> list of meanings
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            word = row["from_content"].strip()
            meaning = row["to_content"].strip()
            data[word].append(meaning)
    return dict(data)

class DictionaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Olam Dictionary App")
        self.root.geometry("700x700")

        # Load dictionary data
        self.data = load_data()
        self.words = sorted(self.data.keys())

        # Title Label
        title_label = tk.Label(root, text="ഓളം", font=("Arial", 40, "bold"))
        title_label.pack(pady=10)

        # Search bar with placeholder
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(root, textvariable=self.search_var, font=("Arial", 14), width=60)
        search_entry.pack(pady=5)

        # Placeholder behavior
        search_entry.insert(0, "Word")
        search_entry.config(foreground="gray")

        def on_focus_in(event):
            if search_entry.get() == "Word":
                search_entry.delete(0, tk.END)
                search_entry.config(foreground="black")

        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Word")
                search_entry.config(foreground="gray")

        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)

        # Trace variable for suggestions
        self.search_var.trace("w", self.update_suggestions)

        # Suggestions list
        self.suggestion_list = tk.Listbox(root, font=("Arial", 12), height=8)
        self.suggestion_list.pack(fill=tk.X, padx=10)
        self.suggestion_list.bind("<<ListboxSelect>>", self.show_meaning)

        # Result display
        self.word_label = tk.Label(root, text="", font=("Arial", 16, "bold"), wraplength=650, justify="center")
        self.word_label.pack(pady=10)

        self.meaning_label = tk.Label(root, text="", font=("Arial", 13), wraplength=650, justify="left")
        self.meaning_label.pack(pady=10)

    def update_suggestions(self, *args):
        query = self.search_var.get().lower()
        self.suggestion_list.delete(0, tk.END)
        if query and query != "word":  # ignore placeholder
            for word in self.words:
                if word.lower().startswith(query):
                    self.suggestion_list.insert(tk.END, word)

    def show_meaning(self, event):
        if not self.suggestion_list.curselection():
            return
        selected_word = self.suggestion_list.get(self.suggestion_list.curselection())
        meanings = self.data.get(selected_word, [])
        
        self.word_label.config(text=selected_word)
        self.meaning_label.config(text="\n• " + "\n• ".join(meanings))

if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()
