import tkinter as tk
import csv
from datetime import date, datetime

# Konstanten für die Produktionsmengen
Tagesproduktion_Normal = 210000
Tagesproduktion_Samstag = 130000
Gewicht_Silo = 26000
Gewicht_Palox = 500

# Variabelen voor de planning
planungsdaten = {}
eingabe_kunde = None
eingabe_art = None
eingabe_anzahl = None
eingabe_mix = None
eingabe_zerlegung = None
eingabe_kippware = None
eingabe_wolf = None
eingabe_zeit = None
status_label = None
planungs_text = None

def speichere_planung():
    """Slaat de planning op in een CSV-bestand."""
    try:
        with open('produktionsplan.csv', 'w', newline='', encoding='utf-8') as datei:
            writer = csv.writer(datei)
            writer.writerow(['Datum', 'Kunde', 'Art', 'Anzahl', 'kg', 'Status', 'Mix', 'Zerlegung', 'Kippware', 'Wolf', 'Zeit', 'Palox-Nr'])
            for datum, tagesplaene in planungsdaten.items():
                for plan in tagesplaene:
                    if 'Paloxen' in plan and plan['Paloxen']:
                        for palox_nr in range(1, len(plan['Paloxen']) + 1):
                            status_palox = plan['Paloxen'][palox_nr - 1].get('Status', 'offen')
                            writer.writerow([
                                datum,
                                plan['Kunde'],
                                plan['Art'],
                                1,
                                Gewicht_Palox,
                                status_palox,
                                plan.get('Mix', ''),
                                plan.get('Zerlegung', ''),
                                plan.get('Kippware', ''),
                                plan.get('Wolf', ''),
                                plan.get('Zeit', ''),
                                palox_nr
                            ])
                    else:
                        writer.writerow([
                            datum,
                            plan['Kunde'],
                            plan['Art'],
                            plan['Anzahl'],
                            plan['kg'],
                            plan.get('Status', 'offen'),
                            plan.get('Mix', ''),
                            plan.get('Zerlegung', ''),
                            plan.get('Kippware', ''),
                            plan.get('Wolf', ''),
                            plan.get('Zeit', ''),
                            ''
                        ])
        print("Planung erfolgreich gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Planung: {e}")

def lade_planung():
    """Laadt de planning uit een CSV-bestand."""
    try:
        with open('produktionsplan.csv', 'r', newline='', encoding='utf-8') as datei:
            reader = csv.reader(datei)
            header = next(reader)
            kolom_mapping = {header_naam: i for i, header_naam in enumerate(header)}
            
            for row in reader:
                datum = row[kolom_mapping['Datum']]
                
                auftrags_info = {
                    'Kunde': row[kolom_mapping['Kunde']],
                    'Art': row[kolom_mapping['Art']],
                    'Anzahl': int(row[kolom_mapping['Anzahl']]),
                    'kg': int(row[kolom_mapping['kg']]),
                    'Status': row[kolom_mapping.get('Status', -1)] if 'Status' in kolom_mapping else 'offen',
                    'Mix': row[kolom_mapping.get('Mix', -1)] if 'Mix' in kolom_mapping else '',
                    'Zerlegung': row[kolom_mapping.get('Zerlegung', -1)] if 'Zerlegung' in kolom_mapping else '',
                    'Kippware': row[kolom_mapping.get('Kippware', -1)] if 'Kippware' in kolom_mapping else '',
                    'Wolf': row[kolom_mapping.get('Wolf', -1)] if 'Wolf' in kolom_mapping else '',
                    'Zeit': row[kolom_mapping.get('Zeit', -1)] if 'Zeit' in kolom_mapping else ''
                }
                
                if 'Palox-Nr' in kolom_mapping and row[kolom_mapping['Palox-Nr']]:
                    hoofd_bestelling_gevonden = False
                    if datum in planungsdaten:
                        for bestelling in planungsdaten[datum]:
                            if bestelling['Kunde'] == auftrags_info['Kunde'] and bestelling.get('Mix') == auftrags_info.get('Mix') and 'Paloxen' in bestelling:
                                bestelling['Paloxen'].append({'kg': auftrags_info['kg'], 'Status': auftrags_info['Status'], 'Palox-Nr': int(row[kolom_mapping['Palox-Nr']])})
                                hoofd_bestelling_gevonden = True
                                break
                    if not hoofd_bestelling_gevonden:
                        auftrags_info['Paloxen'] = [{'kg': auftrags_info['kg'], 'Status': auftrags_info['Status'], 'Palox-Nr': int(row[kolom_mapping['Palox-Nr']])}]
                        if datum not in planungsdaten:
                            planungsdaten[datum] = []
                        planungsdaten[datum].append(auftrags_info)
                else:
                    if datum not in planungsdaten:
                        planungsdaten[datum] = []
                    planungsdaten[datum].append(auftrags_info)
        print("Planung erfolgreich geladen.")
    except FileNotFoundError:
        print("Keine vorhandene Planungsdatei gefunden. Starte met einer leeren Planung.")
    except Exception as e:
        print(f"Fehler beim Laden der Planung: {e}")

def auftrag_hinzufuegen():
    """Adds a new order to the planning with all details."""
    kunde = eingabe_kunde.get()
    art = eingabe_art.get().lower()
    anzahl_str = eingabe_anzahl.get()
    mix = eingabe_mix.get()
    zerlegung = eingabe_zerlegung.get()
    kippware = eingabe_kippware.get()
    wolf = eingabe_wolf.get()
    zeit = eingabe_zeit.get()

    if not kunde or not art or not anzahl_str:
        status_label.config(text="Bitte die Hauptfelder ausfüllen!", fg="red")
        return

    try:
        anzahl = int(anzahl_str)
        if anzahl <= 0:
            status_label.config(text="Anzahl muss größer als 0 sein.", fg="red")
            return
    except ValueError:
        status_label.config(text="Anzahl muss eine ganze Zahl sein.", fg="red")
        return

    gewicht = 0
    auftrags_info = {}
    
    if art == 'silo':
        gewicht = Gewicht_Silo * anzahl
        auftrags_info = {
            'Kunde': kunde,
            'Art': art.capitalize(),
            'Anzahl': anzahl,
            'kg': gewicht,
            'Status': 'offen',
            'Mix': mix,
            'Zerlegung': zerlegung,
            'Kippware': kippware,
            'Wolf': wolf,
            'Zeit': zeit
        }
    elif art == 'palox':
        auftrags_info = {
            'Kunde': kunde,
            'Art': art.capitalize(),
            'Anzahl': anzahl,
            'kg': Gewicht_Palox * anzahl,
            'Status': 'offen',
            'Mix': mix,
            'Zerlegung': zerlegung,
            'Kippware': kippware,
            'Wolf': wolf,
            'Zeit': zeit,
            'Paloxen': [{'kg': Gewicht_Palox, 'Status': 'offen'}] * anzahl
        }
    else:
        status_label.config(text="Art muss 'Silo' oder 'Palox' zijn.", fg="red")
        return
    
    vandaag = str(date.today())
    if vandaag not in planungsdaten:
        planungsdaten[vandaag] = []
    
    planungsdaten[vandaag].append(auftrags_info)
    
    aktualisiere_anzeige()
    status_label.config(text=f"Auftrag voor {kunde} toegevoegd.", fg="green")
    
    eingabe_kunde.delete(0, tk.END)
    eingabe_art.delete(0, tk.END)
    eingabe_anzahl.delete(0, tk.END)
    eingabe_mix.delete(0, tk.END)
    eingabe_zerlegung.delete(0, tk.END)
    eingabe_kippware.delete(0, tk.END)
    eingabe_wolf.delete(0, tk.END)
    eingabe_zeit.delete(0, tk.END)

def markiere_als_produziert():
    """Marks the selected order as 'produced'."""
    try:
        geselecteerde_index = planungs_text.tag_ranges('sel')
        if not geselecteerde_index:
            status_label.config(text="Bitte einen Auftrag zum Markieren auswählen.", fg="red")
            return

        begin_index = int(float(geselecteerde_index[0])) - 2
        
        vandaag = str(date.today())
        if vandaag in planungsdaten and begin_index >= 0 and begin_index < len(planungsdaten[vandaag]):
            bestelling = planungsdaten[vandaag][begin_index]

            if 'Paloxen' in bestelling:
                geproduceerde_paloxen = sum(1 for palox in bestelling['Paloxen'] if palox['Status'] == 'produziert')
                if geproduceerde_paloxen == len(bestelling['Paloxen']):
                    for palox in bestelling['Paloxen']:
                        palox['Status'] = 'offen'
                else:
                    bestelling['Paloxen'][geproduceerde_paloxen]['Status'] = 'produziert'
                
            else:
                if bestelling['Status'] == 'produziert':
                    bestelling['Status'] = 'offen'
                else:
                    bestelling['Status'] = 'produziert'
            
            aktualisiere_anzeige()
            speichere_planung()
            status_label.config(text="Status van de bestelling bijgewerkt.", fg="green")
        else:
            status_label.config(text="Konnte Auftrag nicht finden.", fg="red")

    except Exception as e:
        status_label.config(text=f"Fehler: {e}", fg="red")

def berechne_produktion():
    """Calculates the total production for each day and adjusts the balance."""
    saldo = 0
    gesorteerde_datums = sorted(planungsdaten.keys())
    produktionsuebersicht = {}

    for datum in gesorteerde_datums:
        dag_van_de_week = datetime.strptime(datum, '%Y-%m-%d').weekday()
        if dag_van_de_week == 5:
            tages_soll = Tagesproduktion_Samstag
        elif dag_van_de_week == 6:
            tages_soll = 0
        else:
            tages_soll = Tagesproduktion_Normal

        tages_ist = sum(auftrag['kg'] for auftrag in planungsdaten.get(datum, []))
        tages_ist += saldo
        ueberproduktion = max(0, tages_ist - tages_soll)
        
        produktionsuebersicht[datum] = {
            'gesamtkilogramm': tages_ist,
            'ueberproduktion': ueberproduktion
        }
        saldo = ueberproduktion
    
    return produktionsuebersicht

def aktualisiere_anzeige():
    """Updates the display of the planning in the text box."""
    planungs_text.delete(1.0, tk.END)
    
    produktionsuebersicht = berechne_produktion()

    for datum, details in produktionsuebersicht.items():
        tages_ist = details['gesamtkilogramm']
        ueberproduktion = details['ueberproduktion']
        
        dag_van_de_week = datetime.strptime(datum, '%Y-%m-%d').weekday()
        if dag_van_de_week == 5:
            tages_soll = Tagesproduktion_Samstag
        elif dag_van_de_week == 6:
            tages_soll = 0
        else:
            tages_soll = Tagesproduktion_Normal

        planungs_text.insert(tk.END, f"Planung für {datum}:\n")
        planungs_text.insert(tk.END, "-------------------------\n")
        
        reeds_geproduceerd = 0
        
        if datum in planungsdaten:
            for auftrag in planungsdaten[datum]:
                line = f"Kunde: {auftrag['Kunde']}, Art: {auftrag['Art']}, Anzahl: {auftrag['Anzahl']}, kg: {auftrag['kg']}\n"
                details_line = f"  -> Zeit: {auftrag.get('Zeit', '')}, Mix: {auftrag.get('Mix', '')}, Zerlegung: {auftrag.get('Zerlegung', '')}, Kippware: {auftrag.get('Kippware', '')}, Wolf: {auftrag.get('Wolf', '')}\n"

                if 'Paloxen' in auftrag:
                    geproduceerde_paloxen = sum(1 for palox in auftrag['Paloxen'] if palox['Status'] == 'produziert')
                    status_emoji = "✅" if geproduceerde_paloxen == len(auftrag['Paloxen']) else "❌"
                    planungs_text.insert(tk.END, f"{status_emoji} {line}")
                    planungs_text.insert(tk.END, details_line)
                    planungs_text.insert(tk.END, f"   - Geproduceerde Paloxen: {geproduceerde_paloxen} von {len(auftrag['Paloxen'])}\n")
                    reeds_geproduceerd += geproduceerde_paloxen * Gewicht_Palox
                else:
                    status_emoji = "✅" if auftrag['Status'] == 'produziert' else "❌"
                    planungs_text.insert(tk.END, f"{status_emoji} {line}")
                    planungs_text.insert(tk.END, details_line)
                    if auftrag['Status'] == 'produziert':
                        reeds_geproduceerd += auftrag['kg']
        
        rest_uit_vorig_dag = tages_ist - sum(auftrag['kg'] for auftrag in planungsdaten.get(datum, []))
        
        planungs_text.insert(tk.END, f"\nSaldo aus Vortag: {rest_uit_vorig_dag} kg\n")
        planungs_text.insert(tk.END, f"Bereits produziert heute: {reeds_geproduceerd} kg\n")
        planungs_text.insert(tk.END, f"Noch zu produzieren: {tages_soll - (sum(auftrag['kg'] for auftrag in planungsdaten.get(datum, [])) + rest_uit_vorig_dag)} kg\n")
        planungs_text.insert(tk.END, f"Gesamtproduktion: {tages_ist} kg\n")
        planungs_text.insert(tk.END, f"Tages-Soll: {tages_soll} kg\n")

        if ueberproduktion > 0:
            planungs_text.insert(tk.END, f"Überschuss (wird auf morgen übertragen): {ueberproduktion} kg\n")
        else:
            planungs_text.insert(tk.END, f"Noch zu produzieren: {tages_soll - tages_ist} kg\n")
        planungs_text.insert(tk.END, "=========================================\n\n")

def erstelle_hauptfenster():
    fenster = tk.Tk()
    fenster.title("Karkassen-Planung")
    fenster.geometry("1000x800")

    eingabe_frame = tk.LabelFrame(fenster, text="Neuen Auftrag hinzufügen", padx=10, pady=10)
    eingabe_frame.pack(pady=10, padx=10, fill="x")

    tk.Label(eingabe_frame, text="Kunde:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    global eingabe_kunde
    eingabe_kunde = tk.Entry(eingabe_frame, width=30)
    eingabe_kunde.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(eingabe_frame, text="Art (Silo/Palox):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    global eingabe_art
    eingabe_art = tk.Entry(eingabe_frame, width=30)
    eingabe_art.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(eingabe_frame, text="Anzahl:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    global eingabe_anzahl
    eingabe_anzahl = tk.Entry(eingabe_frame, width=30)
    eingabe_anzahl.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(eingabe_frame, text="Mix:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    global eingabe_mix
    eingabe_mix = tk.Entry(eingabe_frame, width=30)
    eingabe_mix.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(eingabe_frame, text="Zerlegung (1 of 2):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
    global eingabe_zerlegung
    eingabe_zerlegung = tk.Entry(eingabe_frame, width=30)
    eingabe_zerlegung.grid(row=1, column=3, padx=5, pady=5)
    
    tk.Label(eingabe_frame, text="Kippware:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
    global eingabe_kippware
    eingabe_kippware = tk.Entry(eingabe_frame, width=30)
    eingabe_kippware.grid(row=2, column=3, padx=5, pady=5)
    
    tk.Label(eingabe_frame, text="Wolf (20mm, 6mm, ohne):").grid(row=3, column=2, sticky="w", padx=5, pady=5)
    global eingabe_wolf
    eingabe_wolf = tk.Entry(eingabe_frame, width=30)
    eingabe_wolf.grid(row=3, column=3, padx=5, pady=5)

    tk.Label(eingabe_frame, text="Zeit (hh:mm):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    global eingabe_zeit
    eingabe_zeit = tk.Entry(eingabe_frame, width=30)
    eingabe_zeit.grid(row=4, column=1, padx=5, pady=5)
    
    tk.Button(eingabe_frame, text="Auftrag hinzufügen", command=auftrag_hinzufuegen).grid(row=5, column=0, columnspan=2, pady=10)
    tk.Button(eingabe_frame, text="Planung speichern", command=speichere_planung).grid(row=6, column=0, columnspan=2, pady=5)

    global status_label
    status_label = tk.Label(eingabe_frame, text="", font=("Helvetica", 10))
    status_label.grid(row=7, column=0, columnspan=4, pady=5)

    anzeige_frame = tk.LabelFrame(fenster, text="Tagesplanung", padx=10, pady=10)
    anzeige_frame.pack(pady=10, padx=10, fill="both", expand=True)

    global planungs_text
    planungs_text = tk.Text(anzeige_frame, height=20, width=80)
    planungs_text.pack(fill="both", expand=True)
    
    tk.Button(anzeige_frame, text="Ausgewählten Auftrag als 'Produziert' markieren", command=markiere_als_produziert).pack(pady=5)
    
    lade_planung()
    aktualisiere_anzeige()

    fenster.mainloop()

if __name__ == "__main__":
    erstelle_hauptfenster()