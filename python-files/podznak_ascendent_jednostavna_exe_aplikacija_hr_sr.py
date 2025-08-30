# Podznak (Ascendent) – jednostavna EXE aplikacija (HR/SR)
# Autor: GPT Chat Hrvatski
# Opis: Tkinter GUI koji računa ascendent (podznak) koristeći Swiss Ephemeris (pyswisseph)
# Licenca: MIT
# 
# Ovisnosti:
#   pip install pyswisseph
#   (za .exe) pip install pyinstaller
# Pakiranje u .exe (Windows):
#   pyinstaller --onefile --noconsole podznak_app.py
#
# Napomena: Unesite geografske koordinate (širina, dužina) i vremensku zonu ručno.
#           Dužina istočno je +, zapadno je -; širina sjeverno +, južno -.

import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt

try:
    import swisseph as swe
except ImportError:
    raise SystemExit("Nedostaje 'pyswisseph'. Instalirajte: pip install pyswisseph")

ZODIJAK_HR = [
    "Ovan", "Bik", "Blizanci", "Rak", "Lav", "Djevica",
    "Vaga", "Škorpion", "Strijelac", "Jarac", "Vodenjak", "Ribe"
]
ZODIJAK_SR = [
    "Ovan", "Bik", "Blizanci", "Rak", "Lav", "Devica",
    "Vaga", "Škorpion", "Strelac", "Jarac", "Vodolija", "Ribe"
]


def ekliptika_u_znak_i_stepene(lon_deg: float, jezik: str = "HR"):
    lon = lon_deg % 360.0
    indeks = int(lon // 30)
    stepeni = lon - indeks * 30
    if jezik.upper() == "SR":
        znak = ZODIJAK_SR[indeks]
    else:
        znak = ZODIJAK_HR[indeks]
    return znak, stepeni


def izracunaj_ascendent(god, mj, dan, sat, minut, tz_offset, lat, lon):
    """Vrati (asc_lon, znak, stepeni) gdje je asc_lon ekliptička dužina u stupnjevima."""
    # Pretvori lokalno vrijeme u UTC decimalne sate
    lokalni = dt.datetime(god, mj, dan, sat, minut)
    utc = lokalni - dt.timedelta(hours=tz_offset)
    decimalni_sat = utc.hour + utc.minute / 60.0 + utc.second / 3600.0

    # Julianski dan (Greg. kalendar)
    jd = swe.julday(utc.year, utc.month, utc.day, decimalni_sat, swe.GREG_CAL)

    # Kuće + ASC; hsys = 'P' (Placidus), ali ASC je neovisan o sustavu kuća
    # swe.houses_ex vraća (cusps, ascmc)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P')
    asc_lon = ascmc[0]  # 0 = ASC
    return asc_lon


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Podznak / Ascendent – HR/SR")
        self.geometry("520x420")
        self.resizable(False, False)

        self.jezik = tk.StringVar(value="HR")  # HR ili SR
        self.datum = tk.StringVar()
        self.vrijeme = tk.StringVar(value="12:00")
        self.tz = tk.StringVar(value="+1")
        self.lat = tk.StringVar(value="45.80")   # npr. Zagreb 45.80 N
        self.lon = tk.StringVar(value="15.97")   # npr. Zagreb 15.97 E

        self._ui()

    def _ui(self):
        pad = 8
        okvir = ttk.Frame(self, padding=pad)
        okvir.pack(fill=tk.BOTH, expand=True)

        naslov = ttk.Label(okvir, text="Određivanje podznaka (ascendenta)", font=("Segoe UI", 14, "bold"))
        naslov.grid(row=0, column=0, columnspan=4, pady=(0, 6))

        # Jezik
        ttk.Label(okvir, text="Jezik oznaka:").grid(row=1, column=0, sticky="w")
        cb = ttk.Combobox(okvir, textvariable=self.jezik, values=["HR", "SR"], width=6, state="readonly")
        cb.grid(row=1, column=1, sticky="w")

        # Datum
        ttk.Label(okvir, text="Datum rođenja (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        ttk.Entry(okvir, textvariable=self.datum, width=18).grid(row=2, column=1, sticky="w")

        # Vrijeme
        ttk.Label(okvir, text="Vrijeme rođenja (HH:MM):").grid(row=3, column=0, sticky="w")
        ttk.Entry(okvir, textvariable=self.vrijeme, width=10).grid(row=3, column=1, sticky="w")

        # Vremenska zona
        ttk.Label(okvir, text="Vremenska zona (npr. +1, +2, -5):").grid(row=4, column=0, sticky="w")
        ttk.Entry(okvir, textvariable=self.tz, width=10).grid(row=4, column=1, sticky="w")

        # Koordinate
        ttk.Label(okvir, text="Geo. širina (° decimalno, +N / -S):").grid(row=5, column=0, sticky="w")
        ttk.Entry(okvir, textvariable=self.lat, width=12).grid(row=5, column=1, sticky="w")

        ttk.Label(okvir, text="Geo. dužina (° decimalno, +E / -W):").grid(row=6, column=0, sticky="w")
        ttk.Entry(okvir, textvariable=self.lon, width=12).grid(row=6, column=1, sticky="w")

        # Gumbi
        ttk.Button(okvir, text="Izračunaj podznak", command=self.izracunaj).grid(row=7, column=0, pady=(10, 6), sticky="w")
        ttk.Button(okvir, text="O programu", command=self.o_programu).grid(row=7, column=1, pady=(10, 6), sticky="w")

        # Rezultat
        self.rez = tk.Text(okvir, height=10, width=58, wrap="word")
        self.rez.grid(row=8, column=0, columnspan=4, pady=(8, 0))

        for i in range(4):
            okvir.columnconfigure(i, weight=1)

    def o_programu(self):
        messagebox.showinfo(
            "O programu",
            "Jednostavna aplikacija za izračun ascendenta (podznaka) koristeći Swiss Ephemeris.\n"
            "Unesite datum, vrijeme, vremensku zonu i koordinate mjesta rođenja."
        )

    def izracunaj(self):
        try:
            jezik = self.jezik.get().strip().upper()
            datum = self.datum.get().strip()
            vrijeme = self.vrijeme.get().strip()
            tz_str = self.tz.get().strip().replace(",", ".")
            lat_str = self.lat.get().strip().replace(",", ".")
            lon_str = self.lon.get().strip().replace(",", ".")

            if not datum or not vrijeme:
                raise ValueError("Unesite datum i vrijeme.")

            god, mj, dan = [int(x) for x in datum.split("-")]
            sat, minut = [int(x) for x in vrijeme.split(":")]

            tz_offset = float(tz_str)
            lat = float(lat_str)
            lon = float(lon_str)

            asc_lon = izracunaj_ascendent(god, mj, dan, sat, minut, tz_offset, lat, lon)
            znak, deg = ekliptika_u_znak_i_stepene(asc_lon, jezik)

            # Formatiranje izlaza
            deg_int = int(deg)
            min_arc = int(round((deg - deg_int) * 60))

            if jezik == "SR":
                tekst = [
                    f"Podznak (ascendent): {znak}",
                    f"Ekliptička dužina ASC: {asc_lon:.2f}°",
                    f"Pozicija u znaku: {deg_int}° {min_arc}'"
                ]
            else:
                tekst = [
                    f"Podznak (ascendent): {znak}",
                    f"Ekliptička dužina ASC: {asc_lon:.2f}°",
                    f"Pozicija u znaku: {deg_int}° {min_arc}'"
                ]

            self.rez.delete("1.0", tk.END)
            self.rez.insert(tk.END, "\n".join(tekst))
        except Exception as e:
            messagebox.showerror("Greška", str(e))


if __name__ == "__main__":
    # Po želji: postavite put do efemerida ako imate lokalne .se1/.se2 datoteke
    # swe.set_ephe_path(".")
    app = App()
    app.mainloop()
