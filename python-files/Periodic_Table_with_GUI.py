import tkinter as tk
from tkinter import messagebox
import periodictable


class MendeleyevTable:
    def __init__(self, element):
        self.name = element.name
        self.symbol = element.symbol
        self.atomic_number = element.number
        self.atomic_mass = element.mass

    def display_info(self):
        return f"Name: {self.name}\nSymbol: {self.symbol}\nAtomic number: {self.atomic_number}\nAtomic mass: {self.atomic_mass} gr"


# Mapping Name → Element manuell herstellen
def get_element_by_name(name):
    for el in periodictable.elements:
        if el.name.lower() == name.lower():
            return el
    return None


class PeriodicTableGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mendeleyev Periodic Table")
        self.root.geometry("400x300")

        # Labels
        self.name_label = tk.Label(root, text="Enter Element Name:")
        self.name_label.pack(pady=10)

        # Entry for user input
        self.name_entry = tk.Entry(root, width=30)
        self.name_entry.pack(pady=10)

        # Button to search the element
        self.search_button = tk.Button(root, text="Search", command=self.search_element)
        self.search_button.pack(pady=10)

        # Text box to display element info
        self.result_text = tk.Text(root, height=8, width=40, wrap=tk.WORD)
        self.result_text.pack(pady=10)

    def search_element(self):
        name = self.name_entry.get()
        element = get_element_by_name(name)

        if element:
            table_entry = MendeleyevTable(element)
            self.result_text.delete(1.0, tk.END)  # Clear previous results
            self.result_text.insert(tk.END, table_entry.display_info())
        else:
            self.result_text.delete(1.0, tk.END)
            messagebox.showerror("Error", "Element not found!")


# Main window creation
root = tk.Tk()
app = PeriodicTableGUI(root)
root.mainloop()


# Aurel Isufati