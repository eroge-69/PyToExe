"""
Korrigiert in einer Reihe von eingegeben rcd Dateien die Zeitstempel bei aufeinandererfolgenden gleichen Stationen, sowie den
Stationsnamen, wenn ein GPS vorhanden ist und überprüft ob die Traktung (unit) fehlerhaft bzw. ungewöhnlich ist
"""
import csv
import os, glob
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter.filedialog import askdirectory
from math import sin, cos, sqrt, atan2, radians
from GPS import *
import statistics
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path

def findstation(gpsy,gpsx,vehicle):
    """
    Bestimmt die nächstgelegene ÖPNV-Station anhand von übergebenen GPS-Koordinaten.

    Die Funktion erhält zwei Strings, die die Geo-Koordinaten (im Format "50.18302") darstellen:
      - gpsy: Längengrad (Longitude)
      - gpsx: Breitengrad (Latitude)
      - int: vehicle number

    Es wird die Haversine-Formel verwendet, um die Entfernung zwischen dem übergebenen Punkt
    und allen in den globalen Listen 'koordinatenlat' (Breitengrade) und 'koordinatenlong' (Längengrade)
    gespeicherten Stationen zu berechnen. Anschließend wird die Station ermittelt, die die geringste
    Entfernung zum übergebenen Punkt aufweist.

    Parameter:
      gpsy (str): Längengrad als String.
      gpsx (str): Breitengrad als String.

    Rückgabewert:
      str: Der Name der nächstgelegenen Station, abgeschnitten auf maximal 16 Zeichen.
    """
    R = 6373.0
    checklist = []
    stationenlisteneu = []
    lat1 = radians(float(gpsx))
    long1 = radians(float(gpsy))
    if vehicle > 3614:
        #Wenn U-Bahn gehe in U-Bahn Liste
        for j in range(len(U_koordinatenlat)):
            lat2 = radians(float(U_koordinatenlat[j]))
            long2 = radians(float(U_koordinatenlong[j]))
            dlon = long2 - long1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            checklist.append(distance)
    else:
        #Sonst gehe über andere Liste
        for j in range(len(koordinatenlat)):
            lat2 = radians(float(koordinatenlat[j]))
            long2 = radians(float(koordinatenlong[j]))
            dlon = long2 - long1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            checklist.append(distance)
    if min(checklist) > 0.8:
        return(0)
    index_min = min(range(len(checklist)), key=checklist.__getitem__)
    if vehicle > 3614:
        #Wenn U-Bahn durchsuche U-Bahn Liste sonst Bus
        return(U_stationname[index_min][0:16])  # return station string
    else:
        return(stationname[index_min][0:16])  # return station string

def last15folders(path):
    """
    Verarbeitet Unterordner in einem angegebenen Verzeichnis, die dem Muster 'YYYY_MM_DD_rcd' entsprechen.

    Die Funktion führt folgende Schritte aus:
      - Wandelt den übergebenen Pfad in ein Path-Objekt um.
      - Filtert die Unterordner, die dem regulären Ausdruck für 'YYYY_MM_DD_rcd' entsprechen.
      - Behaltet nur jene Ordner, deren Datum (im Namenspräfix, die ersten 10 Zeichen) nicht älter als 15 Tage ist.
      - Gibt für jeden gültigen Ordner den vollständigen Pfad aus und ruft die Funktion 'onefolder' (Korrekturfunktion) auf.

    Parameter:
      path (str): Der Pfad zum Verzeichnis, das nach passenden Unterordnern durchsucht werden soll.

    Rückgabewert:
      None
    """
    pfad = Path(path)  # Konvertiere den String in ein Path-Objekt
    ordner = [d.name for d in pfad.iterdir() if d.is_dir()]
    # Regulärer Ausdruck für das Muster 'YYYY_MM_DD_rcd'
    pattern = re.compile(r"^\d{4}_\d{2}_\d{2}_rcd$")
    # Nur Ordner mit passendem Namen behalten
    ordner = [d.name for d in pfad.iterdir() if d.is_dir() and pattern.match(d.name)]
    #alles löschen was älter als 15 tage ist
    heute = datetime.today()
    ordner = [
        d.name for d in pfad.iterdir()
        if d.is_dir() and pattern.match(d.name)
        and 2 <= (heute - datetime.strptime(d.name[:10], "%Y_%m_%d")).days <= 15
    ]
    for directory in ordner:
        vollständiger_pfad =str(pfad/directory)
        print(vollständiger_pfad)
        onefolder(vollständiger_pfad)
    return()

def onefolder(path):
    """
       Verarbeitet alle .csv-Dateien (rcd Dateien) in einem angegebenen Ordner, führt diverse Korrekturschritte durch
       und speichert die korrigierten Dateien in einem neuen Zielordner.

       Vorgehen:
         - Extrahiert den Ordnernamen aus dem übergebenen Pfad.
         - Erstellt einen neuen Ordner mit der Benennung <aktueller_Ordnername>_korrigiert+.
         - Prüft, ob dieser Ordner bereits existiert. Falls ja, wird er mit dem aktuellen Ordner verglichen:
             - Sind neue .csv-Dateien vorhanden, werden diese in einem speziellen "Nachzügler"-Ordner abgelegt.
             - Andernfalls wird die Funktion beendet.
         - Liest alle .csv-Dateien im Quellordner ein und führt nacheinander mehrere Korrekturschritte durch:
             - Fahrzeugnummer extrahieren
             - Entfernen von None-Werten
             - Hinzufügen bzw. Prüfen eines End-of-File-Markers (EOF)
             - GPS-Korrektur
             - Zeitstempelkorrektur
             - Ergänzen fehlender oder fehlerhafter Units
         - Schreibt die korrigierten Dateien in den entsprechenden Ordner.
         - Kopiert im Falle eines "Nachzügler"-Vorgangs die Dateien auch in definierte Netzwerkpfade
           (z. B. AFZS 2025 Eingang und ggf. VGF-Ordner).

       Parameter:
         path (str): Der Pfad des zu bearbeitenden Ordners.

       Rückgabewert:
         int: 0, wenn die Verarbeitung erfolgreich abgeschlossen wurde.
       """
    # Liste die die Namen aller .csv Dateien in diesem Ordner speichert
    csvfiles = []

    # Holt sich den Namen des Ordners
    aktuelle_folder = path.split("/")[-1]
    # Holt den aktuellen Ordnerpfad
    folder = path.replace(aktuelle_folder, "")

    # Erstellt neuen Ordner mit der richtigen Benennung
    dirName = aktuelle_folder + "_korrigiert+"
    folder_path = os.path.join(folder, dirName)
    korrigierter_path = folder_path
    # Prüft ob der Ordner bereits existiert und speichert das Ergebnis in abgleich
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Ordner {folder_path} wurde erstellt.")
        abgleich = 0
    else:
        print(f"Ordner {folder_path} existiert bereits.")
        abgleich = 1
    # Überprüft und filtert die .csv Dateien aus dem gewählten Ordner, weitere Dateien bleiben unberücksichtigt
    for file in os.listdir(path):
        if file.endswith(".csv"):
            csvfiles.append(str(file))
    # Wenn der Ordner mit korrigierten Dateien schon existiert, vergleiche ihn mit dem aktuellen Ordner und nur die Differenz behalten
    if abgleich == 1:
        csv_files_korrigiert = []
        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                csv_files_korrigiert.append(str(file))
        csv_files_dif = list(set(csvfiles) ^ set(csv_files_korrigiert))
        # Wenn es neue Dateien gibt, setze abgleich = 2, sonst brich ab
        if len(csv_files_dif) > 0:
            abgleich = 2
        else:
            print(f"Ordner {folder_path} existiert bereits und es gibt keine Nachzügler-Dateien.")
            return(0)
    # Wenn abgleich = 2, also neue Dateien existieren, erstelle einen Nachzügler-Ordner
    if abgleich == 2:
        dirName = aktuelle_folder.replace("rcd", "") + "Nachzügler"
        folder_path = os.path.join(folder, dirName)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Ordner {folder_path} wurde erstellt.")
        else:
            print("Nachzügler-Ordner existiert bereits.")
        csvfiles = csv_files_dif

    # Geht jetzt alle csv-Dateien der Liste durch
    for file in csvfiles:
        print(file)
        # Erstellt Pfad zum späteren Speichern und Lesen der aktuellen .csv
        filenameaktuell = file
        filename = os.path.join(path, file)
        with open(filename) as file:  # Get all data of the csv file
            reader = csv.reader(file, delimiter=';')
            gesamtdatenliste = list(reader)
            # Hier die verschiedenen Korrekturschritte
            # Hole Fahrzeugnummer
            vehicle = getvehicledata(gesamtdatenliste)
            # Entferne alle None-Werte
            gesamtdatenliste = nonecheck(gesamtdatenliste)
            # Hole Unit Liste falls eine U-Bahn und nachzüglerordner erstellt
            if vehicle > 3600 and abgleich == 2:
                in_verbund = get_verbund(gesamtdatenliste)
            else:
                in_verbund = []
            # Füge eof hinzu
            gesamtdatenliste = eofcheck(gesamtdatenliste, filename)
            # Führe zuerst GPS-Korrektur aus
            gesamtdatenliste = gpscomparison(gesamtdatenliste, vehicle)
            #Füge stops für die halts ein
            gesamtdatenliste = halts_to_stop(gesamtdatenliste,vehicle)
            # Korrektur der reiehnfollge
            gesamtdatenliste = correct_order(gesamtdatenliste)
            # Führe nun Zeitstempelkorrektur aus
            gesamtdatenliste = evenuptimes(gesamtdatenliste)
            # Führe Unit-Korrektur durch
            gesamtdatenliste = addmissingunits(gesamtdatenliste)

        # Schreibt schließlich die geänderte Liste in den korrigierten bzw. Nachzügler-Ordner
        with open(folder + dirName + "/" + filenameaktuell, 'w', newline='') as archive_file:  # Writes the file
            writer = csv.writer(archive_file, delimiter=";")
            for row4 in gesamtdatenliste:
                writer.writerow(row4)

        # Das hier ist der Part bei welchem die Zugverbände aus dem Archiv in den Eingang kopiert werden,
        # falls ein Nachzügler U-Bahn rcd erstellt wird
        if vehicle > 3600 and abgleich == 2 and len(in_verbund) > 0:
            date = filenameaktuell.split('_')[1]
            #Von wo nach wo soll geschoben werden
            destination_dir = Path(r"\\srv-afzs02\AFZS\FAN HGS_ab_2025\import\AFZ\2025\eingang")
            source_dir = Path(r"\\srv-afzs02\AFZS\FAN HGS_ab_2025\import\AFZ\2025\archiv")
            # Gehe nun alle Fahrzeuge durch die vorher im Verbund in der rcd gefunden worden sind
            for fahrzeug in in_verbund:
                praefix_date_veh = fahrzeug + "_" + date
                for csv_file in source_dir.glob("*.csv"):
                    # Gehe durch den Archiv Ordner und prüfe ob, die Datei mit Fahrzeug + Datum vorliegt
                    if praefix_date_veh in csv_file.name:
                        #Verschiebe Sie
                        shutil.move(str(csv_file), str(destination_dir / csv_file.name))
                        log_path = r"\\SRV-FILE01\Daten\7_Projekte\P0053_AFZS\10_Arbeitsordner\r2p\AFZS - Auswertetool 20200511\10 - Zusammengefasste Counterlogs zur Weiterverarbeitung\Logdateien RCD korrigiert\Logfile_archiv_to_eingang.txt"
                        with open(log_path, "a", encoding="utf-8") as file:
                            file.write(f"{datetime.now().strftime('%Y-%m-%d;%H:%M:%S')};Datei {csv_file.name} wurde vom Archiv in den Eingang verschoben.\n")


    # Kopiere die Dateien vom korrigierten Ordner in den AFZS 2025 Eingang Ordner
    if abgleich == 0:
        for datei_name in os.listdir(folder_path):
            quellpfad = os.path.join(folder_path, datei_name)
            zielpfad_eingang_afzs = os.path.join(r"\\srv-afzs02\AFZS\FAN HGS_ab_2025\import\AFZ\2025\eingang", datei_name)
            shutil.copy2(quellpfad, zielpfad_eingang_afzs)
            
    # Kopiere die Dateien vom Nachzügler-Ordner in den korrigierten Ordner (falls nicht gewünscht löschen)
    # Und kopiert in den AFZS 2025 Eingang Ordner bitte Link bei Bedarf anpassen
    if abgleich == 2:
        for datei_name in os.listdir(folder_path):
            quellpfad = os.path.join(folder_path, datei_name)
            zielpfad = os.path.join(korrigierter_path, datei_name)
            zielpfad_eingang_afzs = os.path.join(r"\\srv-afzs02\AFZS\FAN HGS_ab_2025\import\AFZ\2025\eingang", datei_name)
            shutil.copy2(quellpfad, zielpfad)
            shutil.copy2(quellpfad, zielpfad_eingang_afzs)

        # Lösche den Nachzügler-Ordner nach dem Kopieren
        print(f"Nachzügler-Ordner {folder_path} wird nun gelöscht...")
        shutil.rmtree(folder_path)  # Löscht den Ordner und dessen Inhalt
        print(f"Nachzügler-Ordner {folder_path} wurde gelöscht!")

    print("Dateien wurden erfolgreich bearbeitet!")
    return(0)

def get_verbund(gesamtdatenliste):
    """
    Ermittelt alle Fahrzeuge mit denen das Eingabefahrzeug im Verbund gefahren ist
    Parameters:
        gesamtdatenliste (list): rcd als Liste von Listen

    Returns:
        list: List von allen Fahrzeugen mit denen das Inputfahrzeug als Verbund gefahren ist
    """
    result = []
    # Iteriere über alle Elemente in der Gesamtdatenliste
    for i in range(len(gesamtdatenliste)):
        # Überprüfe, ob der aktuelle Datensatz mindestens drei Elemente hat
        if len(gesamtdatenliste[i]) > 2:
            # Prüfe, ob das zweite Element "unit" ist und das dritte Element noch nicht in result vorhanden ist
            if gesamtdatenliste[i][1] == "unit" and gesamtdatenliste[i][2] not in result:
                result.append(gesamtdatenliste[i][2])
    return result

def getvehicledata(gesamtdatenliste):
    """
    Extrahiert die Fahrzeugnummer aus einer CSV-Datenliste.

    Sucht in Zeile 24 bzw. 25 (Index 24/25) nach dem Schlüsselwort "vehicle" und
    filtert die Ziffern aus dem fünften Element (Index 4). Ist die Liste zu kurz,
    wird 0 zurückgegeben; falls kein "vehicle"-Eintrag gefunden wird, wird 9999 zurückgegeben.

    Parameter:
      gesamtdatenliste (list): Liste von CSV-Zeilen.

    Rückgabewert:
      int: Ermittelte Fahrzeugnummer.
    """
    # Get Vehicle Nummer für die Fahrzeuge (spezialfall 25 bei Fahrzeug 1000)
    if len(gesamtdatenliste) > 25:
        if gesamtdatenliste[24][1] == "vehicle":
            vehicle = int(''.join(filter(str.isdigit, str(gesamtdatenliste[24][4]))))
        elif gesamtdatenliste[25][1] == "vehicle":
            vehicle = int(''.join(filter(str.isdigit, str(gesamtdatenliste[25][4]))))
        else:
            vehicle = 9999
    else:
        return(0)
    return(vehicle)

def gpscomparison(gesamtdatenliste,vehicle):
    """
    Korrigiert GPS-Daten in einer CSV-Datenliste anhand des Fahrzeugtyps und vordefinierter Tunnelstationen.

    Für Zeilen, die einen "stop" darstellen (ab Index > 20) und mehr als 7 Spalten enthalten,
    wird überprüft:
      - Falls der Fahrzeugtyp (vehicle) größer als 3614 (U-Bahn) ist und die Station (Spalte 7)
        in der vordefinierten Tunnelstationsliste enthalten ist, werden die GPS-Koordinaten
        (Spalten 9, 10, 11) auf "0,000000" gesetzt.
      - Andernfalls, sofern gültige GPS-Daten vorliegen, wird mittels der Funktion `findstation`
        die Station anhand der GPS-Koordinaten (nach Ersetzen von Komma durch Punkt) neu bestimmt.

    Parameter:
      gesamtdatenliste (list): Liste von CSV-Datenzeilen (jede Zeile als Liste von Strings).
      vehicle (int): Fahrzeugnummer, die zur Unterscheidung von Fahrzeugtypen dient.

    Rückgabewert:
      list: Die modifizierte Datenliste mit ggf. korrigierten GPS-Daten.
    """
    #Liste der aktuellen Tunnelstationen bitte aktuell halten
    tunnelliste = ["Nordwestzentrum", "Miquel-/Adickesa", "Holzhausenstraße", "Grüneburgweg", "Eschenheimer Tor",
                   "Hauptwache/Zeil", "Willy-Brandt-Pla", "Schweizer Platz", "Südbahnhof", "Bockenheimer War",
                   "Festhalle/Messe", "Hauptbahnhof", "Dom/Römer", "Konstablerwache/", "Merianplatz", "Höhenstraße",
                   "Bornheim Mitte", "Seckbacher Ldstr", "Kirchplatz", "Leipziger Straße", "Westend", "Alte Oper",
                   "Zoo", "Ostbahnhof", "Habsburgerallee", "Parlamentsplatz", "Eissporthalle/Fe"]
    #Liste der Busstationen die nicht korrkigiert werden sollen:
    busliste = ["Nordwestzentrum"]

    for i in range(len(gesamtdatenliste) - 2):
        if len(gesamtdatenliste[i]) > 7 and gesamtdatenliste[i][1] == "stop" and i > 20:
                # Fall ist eine Tunnelstation, dann wird GPS sicherheitshalber auf 0 gesetzt
                if vehicle > 3614 and gesamtdatenliste[i][7] in tunnelliste:
                    gesamtdatenliste[i][9] = "0,000000"
                    gesamtdatenliste[i][10] = "0,000000"
                    gesamtdatenliste[i][11] = "0,000000"
                # Fall hat GPS Koordinate
                if  gesamtdatenliste[i][9] != "0,000000" and gesamtdatenliste[i][10] != "0,000000" and \
                        gesamtdatenliste[i][10] != "0" and gesamtdatenliste[i][7] not in busliste:
                    """Korrigiert die Station des aktuellen Stops wenn GPS vorhanden und die Station nicht in der 
                    busliste ist"""
                    vor = gesamtdatenliste[i][7]
                    #Holt die näheste Station zur Gpsx/Gpsy Koordinate, gibt 0 zurück wenn weiter als 800m entfernt zur nähesten Station
                    new = findstation(gesamtdatenliste[i][9].replace(",", "."),
                                                             gesamtdatenliste[i][10].replace(",", "."),vehicle)
                    #Wenn zu weit entfernt (0) nicht ersetzten
                    if new != 0:
                        gesamtdatenliste[i][7] = new
                #Sonderfall Koordinaten falls Bus und stop Nordwestzentrum einfügen
                if vehicle < 3614 and gesamtdatenliste[i][7] == "Nordwestzentrum":
                    gesamtdatenliste[i][9] = "8,63226"
                    gesamtdatenliste[i][10] = "50,1580587"
                    gesamtdatenliste[i][11] = "114,3"

    return(gesamtdatenliste)

def addmissingunits(gesamtdatenliste):
    """
    Führt eine Korrektur der Unit-Einträge in einer CSV-Datenliste durch.

    Die Funktion durchsucht die Datenliste nach Zeilen, die "unit" oder "comp" enthalten,
    sammelt relevante Werte und Positionen und vergleicht wiederholte Einträge, um
    überzählige bzw. fehlerhafte Unit-Einträge zu identifizieren und zu entfernen.

    Parameter:
      gesamtdatenliste (list): Liste von CSV-Datenzeilen, wobei jede Zeile als Liste von Strings vorliegt.

    Rückgabewert:
      list: Die bereinigte Datenliste nach Durchführung der Unit-Korrektur.
    """
    listunit = []
    """Ab hier Unit - Korrektur"""
    listposition = []
    deletelist = []
    aktuellzahler = 0
    altzahler = 0
    altaltzahler = 0
    for i in range(len(gesamtdatenliste) - 2):
        if len(gesamtdatenliste[i]) > 4 and gesamtdatenliste[i][1] == "unit":
            listunit.append(gesamtdatenliste[i][2])
        elif len(gesamtdatenliste[i]) > 3 and gesamtdatenliste[i][1] == "comp":
            listunit.append(gesamtdatenliste[i][1])
            listposition.append(i)
    listunit = listunit[2:]
    listposition = listposition[1:]
    # print(listunit)
    # print(listposition)
    compnum = 0
    for i in range(len(listunit)):
        if listunit[i] == "comp":
            compnum = compnum + 1
            if altzahler == altaltzahler and aktuellzahler != altaltzahler and altaltzahler != 0 and aktuellzahler == 1:
                deletelist.append(listposition[compnum - 2])
            elif aktuellzahler == altaltzahler and altzahler != aktuellzahler and altaltzahler != 0 and altzahler == 1:
                deletelist.append(listposition[compnum - 3])
            elif altzahler == aktuellzahler and altzahler != altaltzahler and altaltzahler != 0 and altaltzahler == 1:
                deletelist.append(listposition[compnum - 4])
            # print(altaltzahler, altzahler, aktuellzahler)
            # print(deletelist)
            altaltzahler = altzahler
            altzahler = aktuellzahler
            aktuellzahler = 0
        else:
            aktuellzahler = aktuellzahler + 1
    deletelist = list(dict.fromkeys(deletelist))
    # print(deletelist)
    for i in range(len(deletelist)):
        del gesamtdatenliste[deletelist[i]]
        del gesamtdatenliste[deletelist[i]]
        deletelist = [x - 2 for x in deletelist]
    return(gesamtdatenliste)

def evenuptimes(gesamtdatenliste):
    """
    Führt eine Zeitstempelkorrektur in einer CSV-Datenliste durch.

    Für Zeilen mit dem Schlüsselwort "stop" wird geprüft, ob aufeinanderfolgende Stopps
    an derselben Station (Spalte 7) vorliegen. Ist dies der Fall (und der Eintrag liegt nach
    Zeile 20), wird der Zeitstempel (Spalte 3) des aktuellen Stopps in den vorherigen Stop-Eintrag
    (Spalte 5) übernommen. Dadurch werden inkonsistente Zeitstempel zwischen aufeinanderfolgenden
    Stopps korrigiert. Außerdem wird geprüft, ob ein unit vor dem Stop liegt, in diesem Fall wird der Richtungswechsel
    erkannt und keine Anpassung vorgenommen.

    Parameter:
      gesamtdatenliste (list): Liste von CSV-Datenzeilen, wobei jede Zeile als Liste von Strings vorliegt.

    Rückgabewert:
      list: Die modifizierte Datenliste mit korrigierten Zeitstempeln.
    """
    stationdiese = 0
    zeilenspeicher2 = 0
    last_entry = "stop"
    nicht_anpassen = ["Südbahnhof","Riedberg","Hauptbahnhof","Bockenheimer War","Seckbacher Ldstr"]


    for i in range(len(gesamtdatenliste) - 2):
        """Im Nachhinein läuft dann die Zeitstempelkorrektur durch nachdem bereits Stationen korrigiert wurden"""
        if len(gesamtdatenliste[i]) > 7 and gesamtdatenliste[i][1] == "stop":
            #Prüft ob der letzte Eintag stop war, falls nicht setzte ihn auf stop mache aber nicht
            stationletzte = stationdiese
            stationdiese = gesamtdatenliste[i][7]
            zeitdiese = gesamtdatenliste[i][3]
            if last_entry == "stop" or (stationletzte and stationdiese) == "Ostbahnhof":
                #Bei Ostbahnhof wird die Zeit auch angepasst wenn direkt davor unit geschrieben wurde
                if stationletzte == stationdiese and i > 20:
                    gesamtdatenliste[zeilenspeicher2][5] = zeitdiese
            zeilenspeicher2 = i
            last_entry = "stop"
        # Wenn Unit gefunden speichere unit als last_entry
        elif len(gesamtdatenliste[i]) > 2 and gesamtdatenliste[i][1] == "unit":
            if stationdiese in nicht_anpassen:
                #nur last entry auf unit setzen und damit zeitstempelkorrektur blockieren wenn station in der liste ist
                last_entry = "unit"
            else:
                last_entry = "stop"
    return(gesamtdatenliste)

def nonecheck(list):
    """Checks the list for None Values and deletes them"""
    result = [liste for liste in list if "None" not in liste]
    return(result)

def eofcheck(list,dateiname):
    """Function check if eof is written, if not it deletes all lines until it finds the first "stop" line.
    Then also deletes the stop line and writes eof"""
    #Pfad für den log
    log_path = r"\\SRV-FILE01\Daten\7_Projekte\P0053_AFZS\10_Arbeitsordner\r2p\AFZS - Auswertetool 20200511\10 - Zusammengefasste Counterlogs zur Weiterverarbeitung\Logdateien RCD korrigiert\Logfile_eof.txt"
    ordnername = os.path.basename(os.path.dirname(dateiname)) # Ordnername extrahieren
    
    if list == []:
        return(list)
    if list[-1][0] != "eof":
        #schreibe das kein eof gefunden in die txt
        with open(log_path, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d;%H:%M:%S')};{ordnername};{os.path.basename(dateiname)}\n")
        for i in range(len(list) - 1, -1, -1):
            # Wenn der Eintrag an der zweiten Stelle nicht 'stop' ist, Liste bis zum 'stop' löschen
            if len(list[i]) < 2:
                #für den Fall, dass die letzte Zeile länge = 1 hat
                list = list[:-1]
            elif list[i][1] != 'stop' and list[i][1] != "wayp":
                list = list[:i]
            elif list[i][1] == "stop" or list[i][1] == "wayp":
                list = list[:i]
                list = list + [["eof"]]
                return (list)
    return(list)

def correct_order(datalist):
    """Durchläuft die ganze Datenliste, sucht nach verdächtigen Haltestellenfolgen und passt diese entsprechend an"""
    #Liste für kritische Haltestellenfolgen erste Haltefolge, dann zu korrigerender Halt und Postion in der Haltefolge mit Start = 0
    critical_orders = [['Miquel-/Adickesa', 'Fritz-Tarnow-Str', 'Fritz-Tarnow-Str', 'Hügelstraße'],["Dornbusch",1],["Zeilweg","Weißer Stein","Weißer Stein","Lindenbaum"],["Heddernheim",1],
                       ["Westend","Hauptwache/Zeil","Konstablerwache/","Konstablerwache/"],["Hauptwache/Zeil",2], ["Hauptwache/Zeil","Hauptwache/Zeil","Konstablerwache/","Zoo"],["Alte Oper",0],
                       ["Westend","Alte Oper","Konstablerwache/","Konstablerwache/"],["Hauptwache/Zeil",2],["Bornheim Mitte","Schäfflestraße","Schäfflestraße","Gwinnerstraße"],["Seckbacher Ldstr",1],
                       ["Ostbahnhof","Zoo","Zoo","Zoo"],["Ostbahnhof",1],["Ostbahnhof","Ostbahnhof","Zoo","Zoo"],["Ostbahnhof",2],["Schäfflestraße","Bornheim Mitte","Bornheim Mitte","Höhenstraße"],["Seckbacher Ldstr",1]
                       ,["Gwinnerstraße","Bornheim Mitte","Bornheim Mitte","Höhenstraße"],["Seckbacher Ldstr",1],["Seckbacher Ldstr","Bornheim Mitte","Bornheim Mitte","Höhenstraße"],["Seckbacher Ldstr",1],
                       ["Bornheim Mitte","Schäfflestraße","Schäfflestraße","Kruppstraße"],["Seckbacher Ldstr",1]]
    #speichert immer die nächsten 4 stationen zum überprüfen ob eine der krtischen Haltestellenfolge getroffen
    current_stations = []
    #speichert die Positionen der 4 Stationen
    current_stations_numbers = []
    counter = 0
    for i in range(20,len(datalist)):
        #Iteriert über gesamte Datenliste
        if len(datalist[i]) > 6 and datalist[i][1] == "stop":
            #Wenn Stopp gefunden wird speichere Station
            current_stations = []
            current_stations_numbers = []
            current_stations.append(datalist[i][7])
            current_stations_numbers.append(i)
            #Counter zum zählen der gefundenen Stationen
            k = 0
            for j in range(i+1,len(datalist)):
                #Suche nun von dort aus die 3 nächsten Stops und speichere diese und deren Positionen
                if len(datalist[j]) > 6 and datalist[j][1] == "stop" and k < 3:
                    current_stations.append(datalist[j][7])
                    current_stations_numbers.append(j)
                    k = k +1
                elif k >= 3:
                    #Höre auf wenn 4 gefunden
                    break
            for m in range(len(critical_orders)):
                #Durchsuche nun die kritischen Folgen und prüfe ob eine kritische Folge mit der aktuellen übereinstimmt
                if current_stations == critical_orders[m]:
                    counter += 1
                    #print(current_stations)
                    #print(current_stations_numbers)
                    #print(critical_orders[m+1])
                    #Falls ja hole die position in der gesamtliste welche korrigiert werden muss
                    position_in_list = current_stations_numbers[critical_orders[m+1][1]]
                    #Hole auch die Station
                    station = critical_orders[m+1][0]
                    #Korrigiere nun
                    datalist[position_in_list][7] = station
    print("Insgesamt " + str(counter) + " Haltestellenfolgen korrigiert.")
    return(datalist)

def halts_to_stop(liste,vehicle):
    """Durchläuft die gesamte rcd und ändert alle halts mit Türöffnungen zu stops und fügt naheste Station ein"""
    for i in range(26,len(liste)-1):
        if len(liste[i+1]) > 1:
            #Wenn ein halt mit folgendener Türöffnung geschrieben wird
            if liste[i][1] == "halt" and liste[i+1][1] == "door":
                #Suche naheste Stations
                if liste[i][6] == "0,000000" or liste[i][7] == "0,000000":
                    continue
                else:
                    nearest_stop = findstation(liste[i][6].replace(",", "."),
                                                                     liste[i][7].replace(",", "."),vehicle)
                    new_elements = ["",nearest_stop,""]
                    #ändere Eintrag zu stop
                    liste[i][1] = "stop"
                    #Füge die neuen Elemente ein
                    liste[i][6:6] = new_elements
    return(liste)

def get_user_choice():
    """
    Öffnet einen Dialog, um den Benutzer eine Auswahl treffen zu lassen.

    Der Dialog fragt, ob ein Ordner ausgewählt werden soll (Option "1") oder ob
    Dateien der letzten 15 Tage verwendet werden sollen (Option "15").

    Rückgabewert:
      str: Die vom Benutzer eingegebene Auswahl.
    """
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    choice = simpledialog.askstring("Option wählen", "Möchten Sie einen Ordner auswählen (1) oder Dateien der letzten 15 Tage verwenden (15)?")
    return choice

def main():
    """
    Startet das Programm, indem der Benutzer eine Auswahl trifft:

      - Bei Auswahl "1" wird ein Dialog zur Auswahl eines Ordners angezeigt,
        wonach die Funktion `onefolder` mit dem ausgewählten Pfad ausgeführt wird.
      - Bei Auswahl "15" wird ein vordefinierter Pfad genutzt, um die Funktion
        `last15folders` aufzurufen, die die Dateien der letzten 15 Tage verarbeitet.

    Rückgabewert:
      int: 0 bei erfolgreichem Abschluss.
    """

    """
    # Hole Path und führe Funktion aus
    choice = get_user_choice()
    if choice == "1":
        path = askdirectory(title='Select Folder')  # shows dialog box and return the path
        onefolder(path)
    elif choice == "15":
        path = r"\\SRV-FILE01\Daten\7_Projekte\P0053_AFZS\10_Arbeitsordner\r2p\AFZS - Auswertetool 20200511\10 - Zusammengefasste Counterlogs zur Weiterverarbeitung"
        last15folders(path)
    return(0)
    """

    #"""
    path = r"\\SRV-FILE01\Daten\7_Projekte\P0053_AFZS\10_Arbeitsordner\r2p\AFZS - Auswertetool 20200511\10 - Zusammengefasste Counterlogs zur Weiterverarbeitung"
    last15folders(path)
    #"""
main()
