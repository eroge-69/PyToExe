from collections import defaultdict
import os
import time
from dataclasses import dataclass
from typing import List, Dict, Any
import sys

while True:
    try:
        odchylka = input("Odchylka v procentech(zmáčkněte v pro nekonečnou odchylku): ").strip()
        if odchylka != "v":
            odchylka = int(odchylka)/100
        break
    except:
        print("Chyba při zadávání odchylky, zadejte celé číslo.")
        time.sleep(3)
        sys.exit()
import pandas as pd
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
max_width = 0
NAZEV_SLOUPCE = "Příkaz"


@dataclass
class work_data:
    druhy_nazev: str
    work_time: float
    normalized_time: float

    def __str__(self):
        return f"{NAZEV_SLOUPCE}: {self.druhy_nazev:33}, Odprac. čas: {self.work_time:.2f}, Tehdejší normovaný čas: {self.normalized_time:.2f}"

def get_file_dir() -> str:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(title="Vyber soubor", filetypes=[("Excel files", "*.xlsx")], initialdir = DESKTOP_DIR)
    if file_path == "":
        print("nebyl vybrán soubor")
        time.sleep(3)
        sys.exit()
    return file_path

def get_save_as_file() -> str:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.asksaveasfilename(
        title="Uložit jako",
        defaultextension=".xlsx",   
        filetypes=[("Sešit Excelu (*.xlsx)", "*.xlsx"), ("Textový dokument (*.txt)", "*.txt"), ("All files", "*.*"), ],
        initialdir=DESKTOP_DIR,
        initialfile="výsledky.xlsx" 
    )

    if file_path == "":
        print("Nebyl vybrán soubor")
        time.sleep(3)
        sys.exit()

    return file_path

def get_first_time(df: pd.DataFrame) -> float:
    for i in df.to_dict(orient="records"):
        if(i["Normovaný čas stroje (min)"] > 0 or i["Normovaný čas obsluhy (min)"] > 0):
            if(i["Normovaný čas stroje (min)"] != i["Normovaný čas obsluhy (min)"]):
                print("Normovaný čas stroje se nerovná Normovaný čas obsluhy", f"{NAZEV_SLOUPCE}: {i[NAZEV_SLOUPCE]}")
                time.sleep(3)
                sys.exit()
            first_normalized_time = i["Normovaný čas obsluhy (min)"] / i["Odváděné kusy"]
            return first_normalized_time

def time_filter(input_list:list[work_data], fst_time: float) -> tuple[List[work_data], List[work_data]]:
    ubnormal = []
    normal = []
    for i in input_list:
        if(fst_time*(1-odchylka) < i.work_time < fst_time*(1+odchylka)):
            normal.append(i)
        else:
            ubnormal.append(i)
    return normal, ubnormal

def get_average(input_list:list[work_data]) -> float:
    sum = 0
    for i in input_list:
        sum += i.work_time
    return sum / len(input_list)

def get_median(input_list: List[work_data]) -> float:
    lst = [i.work_time for i in input_list]
    n = len(lst)
    if n == 0:
        print("Seznam je prázdný, nelze vypočítat medián.")
        time.sleep(3)
        sys.exit()
    s = sorted(lst)
    if n % 2 == 1:  
        return s[n // 2]
    else:
        return (s[n // 2 - 1] + s[n // 2]) / 2

def display(input_list:list[work_data]) -> None:
    for i in input_list:
        print(i)

def lst_to_df(input_list: list[work_data]) -> pd.DataFrame:
    data = {
        NAZEV_SLOUPCE: [i.druhy_nazev for i in input_list],
        "Odprac. čas (min)": [i.work_time for i in input_list],
        "Normovaný čas (min)": [i.normalized_time for i in input_list]
    }
    return pd.DataFrame(data)

def save_excel(normal: list[work_data], ubnormal:list[work_data], average:float,median:float, file_path: str) -> None:
    from openpyxl.utils import get_column_letter
    df_normalni = lst_to_df(normal)
    df_odchylky = lst_to_df(ubnormal)
    avg_row = {
        NAZEV_SLOUPCE: f"Registrační číslo: {data_list[0]['Registrační číslo'] if len(data_list) > 0 else 'N/A'}",
        "Odprac. čas (min)": f"Průměr: {average:.2f}",
        "Normovaný čas (min)": f"Aktuální normovaný čas: {first_normalized_time:.2f}"
    }
    med_row = {
        NAZEV_SLOUPCE: "",
        "Odprac. čas (min)": f"Medián: {median:.2f}",
        "Normovaný čas (min)": "Nekonečná odchylka" if odchylka == "v" else f"Odchylka: {odchylka*100:.0f} %"
    }

    df_normalni = pd.concat([df_normalni, pd.DataFrame([avg_row, med_row])], ignore_index=True)

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_normalni.to_excel(writer, sheet_name="Normální časy", index=False)
        df_odchylky.to_excel(writer, sheet_name="Odchylky", index=False)

        writer.book  
        for sheetname, df in {"Normální časy": df_normalni, "Odchylky": df_odchylky}.items():
            worksheet = writer.sheets[sheetname]
            for i, col in enumerate(df.columns, 1):
                max_len = max(
                    [len(str(col))] + [len(str(val)) for val in df[col]]
                )
                worksheet.column_dimensions[get_column_letter(i)].width = max_len + 2

        

data_path = get_file_dir()
try:
    df = pd.read_excel(
        data_path, 
        usecols=["Registrační číslo", 
                "Skutečně odprac. čas obsluhy (min)", 
                "Normovaný čas stroje (min)", 
                "Normovaný čas obsluhy (min)", 
                "Odváděné kusy", 
                NAZEV_SLOUPCE]
    )
except:
    print("Chyba při načítání souboru, zkontrolujte jestli soubor není otevřený, formát a sloupce.")
    time.sleep(4)
    sys.exit()

first_normalized_time = get_first_time(df)

data_list = df.to_dict(orient="records")

grouped = defaultdict(list)
for row in data_list:
    grouped[row[NAZEV_SLOUPCE]].append(row)
list_of_lists: List[List[Dict[str, Any]]] = list(grouped.values()) #každý list obsahuje data pro jeden {NAZEV_SLOUPCE}

result_list = []

for list_of_values in list_of_lists:
    work_time = 0
    normalized_time = 0
    pieces_done = 0
    for row in list_of_values:
        pieces_done += row["Odváděné kusy"]
        work_time += row["Skutečně odprac. čas obsluhy (min)"]
        if(row["Odváděné kusy"] > 0 and normalized_time == 0):
            if(row["Normovaný čas stroje (min)"] != row["Normovaný čas obsluhy (min)"]):
                print("Normovaný čas stroje se nerovná Normovaný čas obsluhy", f"{NAZEV_SLOUPCE}: {row[NAZEV_SLOUPCE]}")
                time.sleep(3)
                sys.exit()
            normalized_time = row["Normovaný čas obsluhy (min)"] / row["Odváděné kusy"]
            
    if (normalized_time > 0):
        result_list.append(work_data(row[NAZEV_SLOUPCE], work_time/pieces_done, normalized_time))

if odchylka == "v":
    normal = result_list
    ubnormal = []
else:
    normal, ubnormal = time_filter(result_list, first_normalized_time)
if(len(normal) > 0):
   average = get_average(normal)
   median = get_median(normal)
else:
    average = 0
    median =0

print(f"Aktuální normovaný čas: {first_normalized_time:.2f} min")
print("Odchylky:")
display(ubnormal)
print("\nNormální časy:")
display(normal)
print(f"\nPrůměr: {average:.2f}, Medián: {median:.2f}")


if input("Zmáčkni enter pro vypnutí, nebo t pro uložení do souboru: ").strip() == "t":
    path = get_save_as_file()
    while True:
        try:
            save_excel(normal, ubnormal, average, median, path)
            break
        except PermissionError:
            input(f"Chyba při ukládání souboru, zavřete soubor a zmáčkněte enter pro uložení: ")

    os.system(f'start "" "{path}"')
    print(f"Výsledky uloženy do souboru: {path}")
    time.sleep(1)