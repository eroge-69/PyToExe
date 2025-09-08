import pandas as pd

# Daten vorbereiten
data = [
    ["Frühstück", "Magerquark + Proteinpulver", "250 g Magerquark + 50 g Proteinpulver", "348 kcal | 12 g KH | 71.5 g E | 1.6 g F", "Mit Wasser oder ungesüßter Milch cremig rühren"],
    ["Mittag", "Pute-Kartoffel-Pfanne", "250 g Kartoffeln, 200 g Putenbrust, 200 g TK-Gemüse, Gewürze", "470 kcal | 40 g KH | 52 g E | 5 g F", "Kartoffeln vorkochen und würfeln. Putenbrust würzen und anbraten. Gemüse dazugeben. Alles mischen und servieren."],
    ["Mittag", "Thunfisch-Kartoffel-Salat", "300 g Kartoffeln, 150 g Thunfisch, 150 g Gemüse, 100 g Magerjoghurt, Senf/Essig", "510 kcal | 48 g KH | 46 g E | 8 g F", "Kartoffeln kochen, abkühlen lassen, würfeln. Gemüse klein schneiden. Mit Thunfisch und Joghurt mischen, würzen."],
    ["Abend", "Hähnchen-Kartoffel-Blech", "250 g Kartoffeln, 250 g Hähnchenbrust, 200 g Gemüse, Gewürze", "490 kcal | 42 g KH | 58 g E | 6 g F", "Kartoffeln in Spalten schneiden, würzen. Hähnchen und Gemüse aufs Blech legen. Bei 200 °C Umluft 25–30 Min. backen."],
    ["Abend", "Thunfisch-Kartoffel-Auflauf", "300 g Kartoffeln, 150 g Thunfisch, 150 g Magerquark, 100 g Spinat", "460 kcal | 36 g KH | 52 g E | 5 g F", "Kartoffeln vorkochen, in Scheiben schneiden. Mit Quark, Thunfisch und Spinat in Auflaufform schichten. 180 °C Umluft 25 Min. backen."],
    ["Snack", "Quark + Beeren", "150 g Magerquark, 100 g Beeren", "140 kcal | 12 g KH | 18 g E | 0 g F", "Quark cremig rühren, Beeren unterheben."],
    ["Snack", "Eiklar-Rührei", "4 Eiklar + 1 Ei, 100 g Champignons", "120 kcal | 2 g KH | 18 g E | 4 g F", "Alles in Pfanne braten, würzen."]
]

# DataFrame erstellen
df = pd.DataFrame(data, columns=["Mahlzeit", "Rezeptname", "Zutaten", "Nährwerte", "Zubereitung"])

# Excel-Datei speichern
excel_file = "/mnt/data/wochenplan_fettabbau.xlsx"
df.to_excel(excel_file, index=False)
excel_file
