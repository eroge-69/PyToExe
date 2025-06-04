import csv
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox

class TrasaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Najkrótsza trasa między miastami")
        self.miasta = []
        self.sasiedztwo = []
        self.odleglosci = []
        self.graf = {}
        self.ostatnio_aktywny_entry = None
        self.ostatnia_sciezka = []
        self.ostatni_dystans = None

        # Układ główny
        ramka = tk.Frame(root)
        ramka.pack(padx=10, pady=10)

        # Lewa kolumna
        lewa = tk.Frame(ramka)
        lewa.grid(row=0, column=0, padx=10)

        self.btn_macierz = tk.Button(lewa, text="Importuj macierz sąsiedztwa", command=self.importuj_macierz)
        self.btn_macierz.pack(pady=5)

        self.btn_odleglosci = tk.Button(lewa, text="Importuj odległości drogowe", command=self.importuj_odleglosci)
        self.btn_odleglosci.pack(pady=5)

        self.entry_start = tk.Entry(lewa)
        self.entry_start.pack(pady=5)
        self.entry_start.insert(0, "Miasto początkowe")
        self.entry_start.bind("<FocusIn>", lambda e: self.zaznacz_entry("start"))

        self.entry_end = tk.Entry(lewa)
        self.entry_end.pack(pady=5)
        self.entry_end.insert(0, "Miasto docelowe")
        self.entry_end.bind("<FocusIn>", lambda e: self.zaznacz_entry("end"))

        self.btn_szukaj = tk.Button(lewa, text="Szukaj trasy", command=self.szukaj_trasy)
        self.btn_szukaj.pack(pady=5)

        self.btn_zapisz = tk.Button(lewa, text="Zapisz do CSV", command=self.zapisz_csv)
        self.btn_zapisz.pack(pady=5)

        self.result = tk.Text(lewa, height=10, width=45)
        self.result.pack()

        # Prawa kolumna
        prawa = tk.Frame(ramka)
        prawa.grid(row=0, column=1, padx=10)

        self.label_lista = tk.Label(prawa, text="Lista miast:")
        self.label_lista.pack()

        self.lista_miast = tk.Listbox(prawa, width=25, height=20)
        self.lista_miast.pack()
        self.lista_miast.bind("<<ListboxSelect>>", self.wybierz_miasto_z_listy)

    def zaznacz_entry(self, ktory):
        self.ostatnio_aktywny_entry = ktory

    def importuj_macierz(self):
        filename = filedialog.askopenfilename(filetypes=[("TXT files", "*.txt")])
        if filename:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                dane = list(reader)
            self.miasta = dane[0][1:]
            self.sasiedztwo = [list(map(int, w[1:])) for w in dane[1:]]
            self.lista_miast.delete(0, tk.END)
            for miasto in self.miasta:
                self.lista_miast.insert(tk.END, miasto)
            self.result.insert(tk.END, "Zaimportowano macierz sąsiedztwa.\n")

    def importuj_odleglosci(self):
        filename = filedialog.askopenfilename(filetypes=[("TXT files", "*.txt")])
        if filename:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                dane = list(reader)
            miasta2 = dane[0][1:]
            if miasta2 != self.miasta:
                messagebox.showerror("Błąd", "Miasta w plikach nie są zgodne!")
                return
            self.odleglosci = [list(map(int, w[1:])) for w in dane[1:]]
            self.zbuduj_graf()
            self.result.insert(tk.END, "Zaimportowano odległości drogowe.\n")

    def zbuduj_graf(self):
        self.graf = {miasto: {} for miasto in self.miasta}
        for i, m1 in enumerate(self.miasta):
            for j, m2 in enumerate(self.miasta):
                if self.sasiedztwo[i][j] == 1:
                    self.graf[m1][m2] = self.odleglosci[i][j]

    def dijkstra(self, start, cel):
        kolejka = [(0, start, [])]
        odwiedzone = set()
        while kolejka:
            (koszt, miasto, sciezka) = heapq.heappop(kolejka)
            if miasto in odwiedzone:
                continue
            sciezka = sciezka + [miasto]
            if miasto == cel:
                return koszt, sciezka
            odwiedzone.add(miasto)
            for sasiad, odl in self.graf.get(miasto, {}).items():
                if sasiad not in odwiedzone:
                    heapq.heappush(kolejka, (koszt + odl, sasiad, sciezka))
        return float('inf'), []

    def wybierz_miasto_z_listy(self, event):
        wyb = self.lista_miast.curselection()
        if wyb:
            wybrane = self.lista_miast.get(wyb[0])
            if self.ostatnio_aktywny_entry == "start":
                self.entry_start.delete(0, tk.END)
                self.entry_start.insert(0, wybrane)
            elif self.ostatnio_aktywny_entry == "end":
                self.entry_end.delete(0, tk.END)
                self.entry_end.insert(0, wybrane)

    def szukaj_trasy(self):
        start = self.entry_start.get().strip()
        cel = self.entry_end.get().strip()
        self.result.delete('1.0', tk.END)
        self.ostatnia_sciezka = []
        self.ostatni_dystans = None

        if start not in self.graf or cel not in self.graf:
            self.result.insert(tk.END, "Błąd: Jedno z miast nie istnieje.\n")
            return

        dystans, sciezka = self.dijkstra(start, cel)
        if dystans == float('inf'):
            self.result.insert(tk.END, f"Brak połączenia między {start} a {cel}.\n")
        else:
            self.result.insert(tk.END, f"Najkrótsza trasa z {start} do {cel}:\n")
            self.result.insert(tk.END, " → ".join(sciezka) + "\n")
            self.result.insert(tk.END, f"Długość trasy: {dystans} km\n")
            self.ostatnia_sciezka = sciezka
            self.ostatni_dystans = dystans

    def zapisz_csv(self):
        if not self.ostatnia_sciezka or self.ostatni_dystans is None:
            messagebox.showwarning("Brak danych", "Najpierw oblicz trasę.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.ostatnia_sciezka + ['Dystans'])
                writer.writerow([''] * len(self.ostatnia_sciezka) + [self.ostatni_dystans])
            self.result.insert(tk.END, f"Wynik zapisano do pliku: {filename}\n")

# Uruchomienie GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TrasaApp(root)
    root.mainloop()
