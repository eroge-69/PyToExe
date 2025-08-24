import Tkinter as tk
import tkFileDialog
import tkMessageBox

class MD11Editor:
    def __init__(self, root):
        self.root = root
        self.root.title("MD11 Teksteditor")

        self.text = tk.Text(self.root, wrap="word", font=("Arial", 12))
        self.text.pack(expand=1, fill="both")

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)

        filemenu.add_command(label="Nieuw", command=self.nieuw)
        filemenu.add_command(label="Openen", command=self.openen)
        filemenu.add_command(label="Opslaan", command=self.opslaan)
        filemenu.add_separator()
        filemenu.add_command(label="Afsluiten", command=self.root.quit)

        menubar.add_cascade(label="Bestand", menu=filemenu)
        self.root.config(menu=menubar)

    def nieuw(self):
        self.text.delete("1.0", tk.END)

    def openen(self):
        bestand = tkFileDialog.askopenfilename(defaultextension=".md11", filetypes=[("MD11 bestanden", "*.md11")])
        if bestand:
            try:
                with open(bestand, "r") as f:
                    inhoud = f.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, inhoud)
            except Exception as e:
                tkMessageBox.showerror("Fout", "Fout bij openen:\n%s" % e)

    def opslaan(self):
        bestand = tkFileDialog.asksaveasfilename(defaultextension=".md11", filetypes=[("MD11 bestanden", "*.md11")])
        if bestand:
            try:
                with open(bestand, "w") as f:
                    f.write(self.text.get("1.0", tk.END))
            except Exception as e:
                tkMessageBox.showerror("Fout", "Fout bij opslaan:\n%s" % e)


if __name__ == "__main__":
    root = tk.Tk()
    app = MD11Editor(root)
    root.mainloop()
