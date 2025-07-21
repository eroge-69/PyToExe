import tkinter as tk
import random


# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
begriffe = ["Pantomime", "Malen", "Erklären"]
# Liste mit 100 pantomimisch darstellbaren Begriffen
pantomime = [
    "Katze", "Hund", "Vogel", "Fisch", "Elefant",
    "Auto", "Fahrrad", "Ball", "Schwimmen", "Fliegen",
    "Kochen", "Lesen", "Spielen", "Tanzen", "Laufen",
    "Singen", "Malen", "Zeichnen", "Springen", "Schlafen",
    "Essen", "Trinken", "Jagen", "Angeln", "Klettern",
    "Reiten", "Fußball spielen", "Basketball spielen", "Tennis spielen", "Skifahren",
    "Surfen", "Skateboard fahren", "Roller fahren", "Töpfern", "Gärtnern",
    "Putzen", "Feiern", "Geburtstag feiern", "Geschenke auspacken", "Verkleiden",
    "Zaubern", "Flüstern", "Schreiend lachen", "Weinen", "Winken",
    "Umarmen", "Küssen", "Tanzen im Regen", "Auf einen Baum klettern", "In den Park gehen",
    "Ein Picknick machen", "Ein Lagerfeuer machen", "Geschichten erzählen", "Ein Zelt aufbauen", "Verstecken spielen",
    "Fangen spielen", "Karten spielen", "Brettspiele spielen", "Puppen spielen", "Ein Bild malen",
    "Einen Schneemann bauen", "In den Schnee fallen", "Ein Sandburgen bauen", "Am Strand spielen", "Ein Feuerwerk anschauen",
    "Ein Konzert besuchen", "Ins Kino gehen", "Eine Rutsche runter rutschen", "Ein Karussell fahren", "Ein Geschenk einpacken",
    "Ein Geheimnis erzählen", "Ein Rätsel lösen", "Ein Bild fotografieren", "Ein Buch lesen", "Ein Lied singen",
    "Ein Gedicht aufsagen", "Ein Tier füttern", "Ein Haustier streicheln", "Ein Puzzle lösen", "Ein Experiment durchführen",
    "Ein Video drehen", "Ein Spielzeug reparieren", "Ein Bild ausschneiden", "Ein Kostüm tragen", "Ein Rennen gewinnen",
    "Ein Lied tanzen", "Ein Geschenk basteln", "Ein Lagerfeuer singen", "Ein Fest organisieren", "Ein Theaterstück aufführen",
    "Ein Märchen erzählen", "Ein Abenteuer erleben", "Ein Geheimversteck finden", "Ein Rätsel aufgeben", "Ein Geschenk machen",
    "Ein Freund finden", "Ein Geheimnis bewahren", "Ein Traum verwirklichen", "Ein Ziel erreichen", "Ein neues Hobby beginnen"
]
malen = [
    "Schneemann", "Fahrradhelm", "Küchenstuhl", "Schultasche", "Handschuh",
    "Taschenlampe", "Zahnbürste", "Wasserkocher", "Bücherregal", "Schreibtisch",
    "Fußballplatz", "Schmetterlingsflügel", "Kängurutasche", "Kreidekasten", "Pferdestall",
    "Käsekuchen", "Sandburg", "Erdbeermarmelade", "Schlafsack", "Schneeflocke",
    "Blumenstrauß", "Wassermelone", "Papierflieger", "Kochbuch", "Teddybär",
    "Puzzlestück", "Klettergerüst", "Zeltlager", "Weltkarte", "Sonnenschein",
    "Schulfest", "Ferienhaus", "Eiscreme", "Luftballon", "Schokokekse",
    "Küchenschrank", "Katzenspielzeug", "Blätterteig", "Schneekugel", "Wolkenkratzer",
    "Schultafel", "Wasserfall", "Hochhaus", "Schaufelrad", "Schwanensee",
    "Katzenfutter", "Häuserblock", "Pferdetransporter", "Wetterstation", "Zahnarztpraxis",
    "Schmetterlingsgarten", "Handtuchhalter", "Kaffeetasse", "Schneeball", "Kopfhörer",
    "Hochzeitstorte", "Fischernetz", "Kletterpflanze", "Fußballschuh", "Trompete",
    "Schuhkarton", "Küchenmesser", "Rucksackschloss", "Kochplatte", "Schmetterlingsnetz",
    "Schokoladenkeks", "Wasserball", "Zeltplatz", "Sonnenbrille", "Käfigvogel",
    "Lernspiel", "Schatzkiste", "Buntstifte", "Kunstwerk", "Gartenzaun",
    "Tischtennisball", "Seifenblasen", "Küchenwaage", "Schneekristall", "Zahnpasta",
    "Wolkenbild", "Klettergerüst", "Küchensieb", "Schatzkarte", "Schulranzen",
    "Hüpfburg", "Trommelstock", "Katzensprung", "Küchenutensil", "Schminkspiegel",
    "Bilderrahmen", "Wanderkarte", "Taschenmesser", "Fahrradtour", "Sternenhimmel",
    "Eiskunstlauf", "Wurfspiel", "Schiffahrtskarte", "Küchenrolle", "Sonnenblume",
    "Keksdose", "Tischdecke", "Hüpfspiel", "Lernheft", "Fantasiewelt"
]

# Liste mit erklärbaren Begriffen und nicht verwendbaren Begriffen
erklaeren = {
    "Katze": ["Tier", "Schnurren", "Fell", "Pfote", "Maus"],
    "Hund": ["Tier", "Bellen", "Fell", "Leine", "Hundefutter"],
    "Vogel": ["Fliegen", "Feder", "Nest", "Ei", "Schnabel"],
    "Fisch": ["Wasser", "Schwimmen", "Kiemen", "Schuppen", "Angel"],
    "Elefant": ["Tier", "Groß", "Rüssel", "Ohren", "Afrika"],
    "Auto": ["Fahren", "Räder", "Motor", "Straße", "Fahrer"],
    "Fahrrad": ["Fahren", "Räder", "Pedale", "Lenker", "Helm"],
    "Ball": ["Rund", "Spielen", "Werfen", "Fangen", "Sport"],
    "Schwimmen": ["Wasser", "Bewegung", "Baden", "Tauchen", "Schwimmbad"],
    "Fliegen": ["Luft", "Vogel", "Schweben", "Flugzeug", "Hoch"],
    "Kochen": ["Essen", "Herd", "Rezept", "Zutaten", "Braten"],
    "Lesen": ["Buch", "Worte", "Geschichte", "Vorlesen", "Schreiben"],
    "Spielen": ["Freizeit", "Spaß", "Freunde", "Spiel", "Aktiv"],
    "Tanzen": ["Musik", "Bewegung", "Rhythmus", "Schritte", "Party"],
    "Laufen": ["Bewegung", "Schnell", "Gehen", "Sport", "Füße"],
    "Singen": ["Laut", "Musik", "Lied", "Stimme", "Melodie"],
    "Malen": ["Farben", "Bilder", "Pinsel", "Papier", "Kunst"],
    "Zeichnen": ["Stift", "Bilder", "Papier", "Kreativ", "Linien"],
    "Springen": ["Hüpfen", "Bewegung", "Hoch", "Füße", "Spaß"],
    "Schlafen": ["Nacht", "Bett", "Träumen", "Ruhe", "Energie"],
    "Essen": ["Nahrung", "Mahlzeit", "Kochen", "Lecker", "Hunger"],
    "Trinken": ["Flüssigkeit", "Wasser", "Durst", "Becher", "Glas"],
    "Jagen": ["Tier", "Suchen", "Fangen", "Beute", "Wald"],
    "Angeln": ["Wasser", "Fisch", "Angel", "Rute", "Geduld"],
    "Klettern": ["Hoch", "Berg", "Felsen", "Seil", "Abenteuer"],
    "Reiten": ["Pferd", "Sattel", "Galopp", "Tier", "Stall"],
    "Fußball": ["Ball", "Sport", "Tor", "Mannschaft", "Spiel"],
    "Basketball": ["Ball", "Korb", "Sport", "Mannschaft", "Dribbeln"],
    "Tennis": ["Schläger", "Ball", "Sport", "Netz", "Punkt"],
    "Skifahren": ["Schnee", "Berg", "Ski", "Winter", "Abfahrt"],
    "Surfen": ["Welle", "Wasser", "Brett", "Ozean", "Sport"],
    "Skateboard": ["Brett", "Rollen", "Tricks", "Fahren", "Park"],
    "Roller": ["Fahren", "Rollen", "Räder", "Spaß", "Straße"],
    "Töpfern": ["Ton", "Formen", "Kunst", "Hände", "Töpfer"],
    "Gärtnern": ["Pflanzen", "Blumen", "Erd", "Wachsen", "Garten"],
    "Putzen": ["Sauber", "Ordnung", "Reinigen", "Haus", "Arbeit"],
    "Feiern": ["Party", "Spaß", "Essen", "Freunde", "Musik"],
    "Geburtstag": ["Feiern", "Geschenke", "Kuchen", "Kerzen", "Jahr"],
    "Geschenke": ["Überraschung", "Verpacken", "Feiern", "Freunde", "Freude"],
    "Verkleiden": ["Kostüm", "Rollenspiel", "Spaß", "Fantasie", "Anziehen"],
    "Zaubern": ["Tricks", "Magie", "Hände", "Überraschung", "Illusion"],
    "Flüstern": ["Leise", "Sprache", "Geheimnis", "Ohr", "Sprechen"],
    "Lachen": ["Spaß", "Freunde", "Witz", "Freude", "Lustig"],
    "Weinen": ["Traurig", "Gefühl", "Tränen", "Schmerz", "Emotion"],
    "Winken": ["Begrüßen", "Hand", "Hallo", "Abschied", "Freundlich"],
    "Umarmen": ["Umarmung", "Freund", "Liebe", "Körper", "Zuneigung"],
    "Küssen": ["Mund", "Liebe", "Freund", "Zuneigung", "Begrüßung"],
    "Regen": ["Wetter", "Nass", "Tropfen", "Himmel", "Regenschirm"],
    "Baum": ["Pflanze", "Holz", "Blätter", "Natur", "Wald"],
    "Park": ["Grün", "Natur", "Spielen", "Entspannen", "Bänke"],
    "Picknick": ["Essen", "Draußen", "Decke", "Freunde", "Spaß"],
    "Lagerfeuer": ["Feuer", "Nacht", "Wärme", "Geschichten", "Freunde"],
    "Geschichten": ["Erzählen", "Buch", "Phantasie", "Unterhaltung", "Lernen"],
    "Zelt": ["Camping", "Schlafen", "Natur", "Abenteuer", "Draußen"],
    "Verstecken": ["Spiel", "Suchen", "Verstecken", "Freunde", "Spaß"],
    "Fangen": ["Spiel", "Laufen", "Fangen", "Freunde", "Spaß"],
    "Karten": ["Spiel", "Blätter", "Spielen", "Freunde", "Strategie"],
    "Brettspiele": ["Spiel", "Brett", "Züge", "Freunde", "Spaß"],
    "Puppen": ["Spielen", "Figuren", "Kreativ", "Rollenspiel", "Freunde"],
    "Bild": ["Malen", "Kunst", "Zeichnen", "Farben", "Papier"],
    "Schneemann": ["Schnee", "Bauen", "Nase", "Karotten", "Winter"],
    "Schnee": ["Kalt", "Winter", "Schneemann", "Weiß", "Fallen"],
    "Sandburg": ["Strand", "Bauen", "Sand", "Wasser", "Sommer"],
    "Strand": ["Wasser", "Sand", "Sonne", "Urlaub", "Spielen"],
    "Feuerwerk": ["Nacht", "Licht", "Knallen", "Feiern", "Bunt"],
    "Konzert": ["Musik", "Live", "Singen", "Band", "Feiern"],
    "Kino": ["Film", "Leinwand", "Popcorn", "Sitzen", "Unterhaltung"],
    "Rutsche": ["Spielen", "Hoch", "Runter", "Spaß", "Kinderspielplatz"],
    "Karussell": ["Drehen", "Fahren", "Spaß", "Rund", "Fahrgeschäft"],
    "Geschenk": ["Überraschung", "Verpacken", "Feiern", "Freunde", "Freude"],
    "Geheimnis": ["Verstecken", "Wissen", "Überraschung", "Geheimnisvoll", "Erzählen"],
    "Rätsel": ["Denken", "Lösen", "Fragen", "Spaß", "Herausforderung"],
    "Foto": ["Bild", "Kamera", "Erinnerung", "Lächeln", "Aufnehmen"],
    "Buch": ["Lesen", "Geschichte", "Seiten", "Worte", "Kultur"],
    "Lied": ["Singen", "Musik", "Melodie", "Rhythmus", "Vortragen"],
    "Gedicht": ["Reime", "Worte", "Sprechen", "Kreativ", "Vortragen"],
    "Tier": ["Lebewesen", "Natur", "Lebendig", "Säugetier", "Vogel"],
    "Haustier": ["Tier", "Zuhause", "Pflege", "Freund", "Familie"],
    "Puzzle": ["Teile", "Zusammenbauen", "Bild", "Denken", "Spaß"],
    "Experiment": ["Wissenschaft", "Forschen", "Testen", "Lernen", "Spaß"],
    "Video": ["Film", "Aufnehmen", "Bewegung", "Kamera", "Unterhaltung"],
    "Spielzeug": ["Spielen", "Kind", "Freizeit", "Spaß", "Basteln"],
    "Bild": ["Kunst", "Zeichnen", "Farben", "Papier", "Kreativität"],
    "Kostüm": ["Verkleiden", "Fantasie", "Feiern", "Rollenspiel", "Spaß"],
    "Rennen": ["Schnell", "Laufen", "Wettbewerb", "Sport", "Ziel"],
    "Tanz": ["Bewegung", "Musik", "Rhythmus", "Feiern", "Spaß"],
    "Geschenk": ["Überraschung", "Feiern", "Verpacken", "Freunde", "Freude"],
    "Fest": ["Feiern", "Essen", "Freunde", "Spaß", "Tradition"],
    "Theater": ["Aufführung", "Schauspieler", "Bühne", "Kunst", "Unterhaltung"],
    "Märchen": ["Geschichte", "Fantasie", "Helden", "Lehren", "Vorlesen"],
    "Abenteuer": ["Reise", "Entdeckung", "Spaß", "Erlebnis", "Neues"],
    "Versteck": ["Geheimnis", "Suchen", "Verstecken", "Abenteuer", "Spaß"],
    "Freund": ["Beziehung", "Gemeinschaft", "Spaß", "Vertrauen", "Unterstützung"],
    "Traum": ["Schlafen", "Vorstellung", "Wünsche", "Phantasie", "Erinnerung"],
    "Hobby": ["Interesse", "Freizeit", "Aktiv", "Spaß", "Kreativ"],
    "Schule": ["Lernen", "Lehrer", "Klasse", "Bildung", "Freunde"],
    "Lehrer": ["Unterrichten", "Schule", "Wissen", "Helfen", "Klasse"],
    "Klasse": ["Schule", "Lernen", "Freunde", "Lehrer", "Gruppen"],
    "Hausaufgaben": ["Lernen", "Schule", "Aufgaben", "Schreiben", "Studieren"],
    "Freizeit": ["Spaß", "Aktivitäten", "Hobby", "Entspannung", "Zeit"],
    "Familie": ["Eltern", "Geschwister", "Zusammen", "Liebe", "Unterstützung"],
    "Urlaub": ["Reise", "Entspannung", "Frei", "Abenteuer", "Spaß"],
    "Reise": ["Unterwegs", "Entdecken", "Abenteuer", "Fremde", "Neues"],
    "Natur": ["Umwelt", "Bäume", "Tiere", "Landschaft", "Schönheit"],
    "Wetter": ["Sonne", "Regen", "Wind", "Temperatur", "Jahreszeiten"],
    "Jahreszeiten": ["Frühling", "Sommer", "Herbst", "Winter", "Wetter"],
    "Weihnachten": ["Feiern", "Geschenke", "Familie", "Tradition", "Lichter"],
    "Ostern": ["Feiern", "Eier", "Hase", "Frühling", "Tradition"],
    "Geburtstag": ["Feiern", "Kuchen", "Geschenke", "Kerzen", "Jahr"],
    "Sommer": ["Jahreszeit", "Sonne", "Ferien", "Wärme", "Aktivitäten"]
}


# Funktion zum Anzeigen eines zufälligen Begriffs
def zeige_begriff(event):
    zufall = random.choice(begriffe)
    lblAufgabe.config(text=f"Aufgabe: {zufall}", fg="red")
    auswahl_treffen(zufall)

# Funktion zum Auswählen eines Begriffs
def auswahl_treffen(auswahl):
    if auswahl == "Malen":
        begriff = random.choice(malen)
        lblBegriff.config(text=f"zeichne: {begriff}")
    elif auswahl == "Pantomime":
        begriff = random.choice(pantomime)
        lblBegriff.config(text=f"spiele: {begriff}")
    elif auswahl == "Erklären":
        begriff = random.choice(list(erklaeren.keys()))
        tabuwörter = ", \n".join(erklaeren[begriff])
        lblBegriff.config(text=f"erkläre: {begriff} \n\nDiese Wörter darfst du nicht verwenden:\n{tabuwörter}")
    else:
        lblBegriff.config(text="Ungültige Auswahl.")

# Hauptprogramm
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Spiel")

    aufgabe = "Drücke die Leertaste zum Auslosen"
    lblAufgabe = tk.Label(root, text=aufgabe, font=("Helvetica", 24, "bold"))
    lblAufgabe.pack(pady=20)

    lblBegriff = tk.Label(root, text="", font=("Helvetica", 20))
    lblBegriff.pack(pady=20)

    root.bind("<space>", zeige_begriff)
    root.mainloop()