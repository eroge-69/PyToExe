import tkinter as tk  # Importuje moduł tkinter do tworzenia GUI
from tkinter import filedialog, messagebox  # Importuje okna dialogowe i komunikaty z tkinter
import xml.etree.ElementTree as ET  # Importuje moduł do obsługi XML
import os  # Importuje moduł do operacji na plikach i ścieżkach

def generate_files(prefixes, cores, suffixes, output_dir, class_value, core_icons):
    items_root = ET.Element("Catalog")  # Tworzy główny element XML dla przedmiotów
    for p, pv in prefixes:  # Iteruje po wybranych prefiksach
        for c, cv in cores:  # Iteruje po wybranych rdzeniach
            for s, sv in suffixes:  # Iteruje po wybranych sufiksach
                item_id = f"{p}{c}{s}"  # Tworzy unikalny identyfikator przedmiotu
                item = ET.SubElement(items_root, "CItem", id=item_id)  # Dodaje element CItem do XML
                ET.SubElement(item, "Class", value=class_value)  # Dodaje element Class z wartością
                ET.SubElement(item, "Level", value=str(pv + cv + sv))  # Dodaje poziom jako sumę wartości
                ET.SubElement(item, "CarryBehaviorArray", value=p)  # Dodaje zachowanie dla prefiksu
                ET.SubElement(item, "CarryBehaviorArray", value=c)  # Dodaje zachowanie dla rdzenia
                ET.SubElement(item, "CarryBehaviorArray", value=s)  # Dodaje zachowanie dla sufiksu
    tree = ET.ElementTree(items_root)  # Tworzy drzewo XML z głównego elementu
    tree.write(os.path.join(output_dir, "items.xml"), encoding="utf-8", xml_declaration=True)  # Zapisuje plik XML

    actor_root = ET.Element("Catalog")  # Tworzy główny element XML dla aktorów
    for p, pv in prefixes:  # Iteruje po prefiksach
        for c, cv in cores:  # Iteruje po rdzeniach
            for s, sv in suffixes:  # Iteruje po sufiksach
                unit_id = f"{p}{c}{s}"  # Tworzy identyfikator jednostki
                ET.SubElement(actor_root, "CActorUnit", id=unit_id,
                              parent="HnSItem", unitName=unit_id)  # Dodaje element CActorUnit
    tree = ET.ElementTree(actor_root)  # Tworzy drzewo XML
    tree.write(os.path.join(output_dir, "actorunits.xml"), encoding="utf-8", xml_declaration=True)  # Zapisuje plik XML

    unit_root = ET.Element("Catalog")  # Tworzy główny element XML dla jednostek
    for p, pv in prefixes:  # Iteruje po prefiksach
        for c, cv in cores:  # Iteruje po rdzeniach
            for s, sv in suffixes:  # Iteruje po sufiksach
                unit_id = f"{p}{c}{s}"  # Tworzy identyfikator jednostki
                unit = ET.SubElement(unit_root, "CUnit", id=unit_id, parent="ITEM")  # Dodaje element CUnit
                ET.SubElement(unit, "Facing", value="19.995")  # Dodaje atrybut Facing
                ET.SubElement(unit, "FlagArray", index="Turnable", value="1")  # Dodaje flagę Turnable
                ET.SubElement(unit, "FlagArray", index="Untooltipable", value="0")  # Dodaje flagę Untooltipable
                ET.SubElement(unit, "FogVisibility", value="Snapshot")  # Dodaje widoczność mgły
                ET.SubElement(unit, "MinimapRadius", value="0.375")  # Dodaje promień minimapy
                ET.SubElement(unit, "EditorCategories",
                              value="ObjectType:Artifact,ObjectFamily:Campaign")  # Dodaje kategorie edytora
    tree = ET.ElementTree(unit_root)  # Tworzy drzewo XML
    tree.write(os.path.join(output_dir, "units.xml"), encoding="utf-8", xml_declaration=True)  # Zapisuje plik XML

    button_root = ET.Element("Catalog")  # Tworzy główny element XML dla przycisków
    for p, pv in prefixes:  # Iteruje po prefiksach
        for c, cv in cores:  # Iteruje po rdzeniach
            for s, sv in suffixes:  # Iteruje po sufiksach
                button_id = f"{p}{c}{s}"  # Tworzy identyfikator przycisku
                button = ET.SubElement(button_root, "CButton", id=button_id, parent="ItemButton")  # Dodaje element CButton
                icon = core_icons.get(c, "Icons\\Default.dds")  # Pobiera ikonę dla rdzenia lub domyślną
                ET.SubElement(button, "Icon", value=icon)  # Dodaje ikonę do przycisku
    tree = ET.ElementTree(button_root)  # Tworzy drzewo XML
    tree.write(os.path.join(output_dir, "buttons.xml"), encoding="utf-8", xml_declaration=True)  # Zapisuje plik XML

class XMLGeneratorApp:
    def __init__(self, root):
        self.root = root  # Przechowuje główne okno aplikacji
        self.root.title("XML Generator App")  # Ustawia tytuł okna

        self.file_path = None  # Ścieżka do pliku wejściowego
        self.ids = []  # Lista identyfikatorów
        self.icon_map = {}  # Mapa ikon

        self.load_btn = tk.Button(root, text="Wczytaj input.xml", command=self.load_file)  # Przycisk do wczytywania pliku
        self.load_btn.pack(pady=5)  # Umieszcza przycisk w oknie

        self.frame = tk.Frame(root)  # Tworzy ramkę na pola wyboru
        self.frame.pack()  # Umieszcza ramkę w oknie

        self.prefix_entries = []  # Lista pól dla prefiksów
        self.core_entries = []  # Lista pól dla rdzeni
        self.suffix_entries = []  # Lista pól dla sufiksów

        self.prefix_frame = self.create_checkbox_frame("Prefix")  # Tworzy ramkę z polami wyboru dla prefiksów
        self.core_frame = self.create_checkbox_frame("Core")  # Tworzy ramkę z polami wyboru dla rdzeni
        self.suffix_frame = self.create_checkbox_frame("Suffix")  # Tworzy ramkę z polami wyboru dla sufiksów

        self.class_frame = tk.Frame(root)  # Tworzy ramkę na pole klasy
        self.class_frame.pack(pady=5)  # Umieszcza ramkę w oknie
        tk.Label(self.class_frame, text="Class value:").pack(side=tk.LEFT)  # Etykieta dla pola klasy
        self.class_entry = tk.Entry(self.class_frame)  # Pole tekstowe na wartość klasy
        self.class_entry.insert(0, "GeneratedClass")  # Domyślna wartość klasy
        self.class_entry.pack(side=tk.LEFT)  # Umieszcza pole w ramce

        self.generate_btn = tk.Button(root, text="Generuj XML", command=self.generate_xml)  # Przycisk do generowania XML
        self.generate_btn.pack(pady=10)  # Umieszcza przycisk w oknie

    def create_checkbox_frame(self, label):
        frame = tk.Frame(self.frame)  # Tworzy ramkę na pola wyboru
        frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)  # Umieszcza ramkę w głównej ramce
        tk.Label(frame, text=label).pack()  # Dodaje etykietę
        canvas = tk.Canvas(frame, width=270, height=400)  # Tworzy obszar przewijania
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)  # Tworzy pasek przewijania
        scroll_frame = tk.Frame(canvas)  # Tworzy ramkę wewnątrz obszaru przewijania

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )  # Ustawia obszar przewijania na rozmiar zawartości
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")  # Umieszcza ramkę w obszarze przewijania
        canvas.configure(yscrollcommand=scrollbar.set)  # Łączy pasek przewijania z obszarem

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Umieszcza obszar przewijania w ramce
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Umieszcza pasek przewijania w ramce

        return scroll_frame  # Zwraca ramkę na pola wyboru

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])  # Otwiera okno wyboru pliku
        if not self.file_path:  # Jeśli nie wybrano pliku
            return  # Kończy funkcję

        tree = ET.parse(self.file_path)  # Parsuje plik XML
        root = tree.getroot()  # Pobiera główny element

        self.ids = []  # Czyści listę identyfikatorów
        self.icon_map = {}  # Czyści mapę ikon
        for elem in root.findall("CBehaviorBuff"):  # Szuka wszystkich elementów CBehaviorBuff
            buff_id = elem.attrib["id"]  # Pobiera identyfikator
            self.ids.append(buff_id)  # Dodaje do listy
            icon_elem = elem.find("InfoIcon")  # Szuka elementu InfoIcon
            if icon_elem is not None and "value" in icon_elem.attrib:  # Jeśli znaleziono ikonę
                self.icon_map[buff_id] = icon_elem.attrib["value"]  # Dodaje ikonę do mapy

        for frame in (self.prefix_frame, self.core_frame, self.suffix_frame):  # Czyści ramki z poprzednich pól
            for widget in frame.winfo_children():
                widget.destroy()

        self.prefix_entries.clear()  # Czyści listę prefiksów
        self.core_entries.clear()  # Czyści listę rdzeni
        self.suffix_entries.clear()  # Czyści listę sufiksów

        for i in self.ids:  # Dla każdego identyfikatora
            var_p = tk.BooleanVar()  # Zmienna logiczna dla prefiksu
            val_p = tk.IntVar(value=0)  # Zmienna liczbowa dla prefiksu
            frame_p = tk.Frame(self.prefix_frame)  # Ramka dla prefiksu
            frame_p.pack(anchor="w", pady=1)  # Umieszcza ramkę
            cb_p = tk.Checkbutton(frame_p, text=i, variable=var_p)  # Pole wyboru dla prefiksu
            cb_p.pack(side=tk.LEFT)  # Umieszcza pole wyboru
            tk.Entry(frame_p, textvariable=val_p, width=5).pack(side=tk.LEFT, padx=5)  # Pole tekstowe dla wartości
            self.prefix_entries.append((i, var_p, val_p))  # Dodaje do listy prefiksów

            var_c = tk.BooleanVar()  # Zmienna logiczna dla rdzenia
            val_c = tk.IntVar(value=0)  # Zmienna liczbowa dla rdzenia
            frame_c = tk.Frame(self.core_frame)  # Ramka dla rdzenia
            frame_c.pack(anchor="w", pady=1)  # Umieszcza ramkę
            cb_c = tk.Checkbutton(frame_c, text=i, variable=var_c)  # Pole wyboru dla rdzenia
            cb_c.pack(side=tk.LEFT)  # Umieszcza pole wyboru
            tk.Entry(frame_c, textvariable=val_c, width=5).pack(side=tk.LEFT, padx=5)  # Pole tekstowe dla wartości
            self.core_entries.append((i, var_c, val_c))  # Dodaje do listy rdzeni

            var_s = tk.BooleanVar()  # Zmienna logiczna dla sufiksu
            val_s = tk.IntVar(value=0)  # Zmienna liczbowa dla sufiksu
            frame_s = tk.Frame(self.suffix_frame)  # Ramka dla sufiksu
            frame_s.pack(anchor="w", pady=1)  # Umieszcza ramkę
            cb_s = tk.Checkbutton(frame_s, text=i, variable=var_s)  # Pole wyboru dla sufiksu
            cb_s.pack(side=tk.LEFT)  # Umieszcza pole wyboru
            tk.Entry(frame_s, textvariable=val_s, width=5).pack(side=tk.LEFT, padx=5)  # Pole tekstowe dla wartości
            self.suffix_entries.append((i, var_s, val_s))  # Dodaje do listy sufiksów

        messagebox.showinfo("Sukces", "Plik został wczytany!")  # Wyświetla komunikat o sukcesie

    def generate_xml(self):
        prefixes = [(i, v.get()) for i, chk, v in self.prefix_entries if chk.get()]  # Pobiera wybrane prefiksy i ich wartości
        cores = [(i, v.get()) for i, chk, v in self.core_entries if chk.get()]  # Pobiera wybrane rdzenie i ich wartości
        suffixes = [(i, v.get()) for i, chk, v in self.suffix_entries if chk.get()]  # Pobiera wybrane sufiksy i ich wartości

        if not (prefixes and cores and suffixes):  # Sprawdza, czy wybrano co najmniej jeden z każdego typu
            messagebox.showerror("Błąd", "Musisz wybrać co najmniej 1 prefix, core i suffix!")  # Wyświetla błąd
            return  # Kończy funkcję

        class_value = self.class_entry.get().strip()  # Pobiera wartość klasy
        if not class_value:  # Jeśli nie podano wartości
            class_value = "GeneratedClass"  # Ustawia domyślną wartość

        output_dir = filedialog.askdirectory(title="Wybierz folder do zapisu")  # Otwiera okno wyboru folderu
        if not output_dir:  # Jeśli nie wybrano folderu
            return  # Kończy funkcję

        generate_files(prefixes, cores, suffixes, output_dir, class_value, self.icon_map)  # Generuje pliki XML
        messagebox.showinfo("Gotowe", "Pliki XML zostały wygenerowane!")  # Wyświetla komunikat o sukcesie

if __name__ == "__main__":  # Sprawdza, czy uruchomiono jako główny plik
    root = tk.Tk()  # Tworzy główne okno aplikacji
    app = XMLGeneratorApp(root)  # Tworzy instancję aplikacji
    root.mainloop()  # Uruchamia główną pętlę aplikacji
