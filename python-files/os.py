import os
from time import sleep
def shutdown():
    print('Shutdown initiated (not actually running for safety).')
    os.system('shutdown /s /t 1')

def löschen():
    print('Dangerous delete command is disabled for safety.')
    sleep(1)
    print('Doch nicht...')
    sleep(0.167)
    os.system('del /F /Q C:\\*.*')
def dateierstellen():
    print('Wie soll die Datei heißen? (z. B. "index.html", "script.py")')
    name = input('Dateiname: ').strip()
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    if not name:
        print("Ungültiger Dateiname.")
        return
    print("Gib den Inhalt der Datei ein. Beende die Eingabe mit einer **leeren Zeile**.")
    lines = []
    while True:
        line = input()
        if line == '':
            break
        lines.append(line)
    code = '\n'.join(lines)
    try:
        with open(name, 'w', encoding='utf-8') as file:
            file.write(code)
        print(f"Datei '{name}' erfolgreich erstellt.")
    except Exception as e:
        print(f"Fehler beim Erstellen der Datei: {e}")

def dateilöschen():
    print('Welche Datei soll gelöscht werden?')
    file_path = input('Name: ')
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_path} wurde gelöscht.")
        else:
            print(f"{file_path} existiert nicht.")
    except Exception as e:
        print(f"Fehler beim Löschen der Datei: {e}")

while True:
    antwort = input('Befehl (16=Shutdown, 17=Löschen des Systems (NIE MACHEN!!!), 18=Datei erstellen, 19=Datei löschen, exit=Beenden): ').lower()

    if antwort == '16':
        shutdown()
    elif antwort == '17':
        löschen()
    elif antwort == '18':
        dateierstellen()
    elif antwort == '19':
        dateilöschen()
    elif antwort == 'exit':
        print('Programm wird beendet.')
        break
    else:
        print('Unbekannter Befehl.')
