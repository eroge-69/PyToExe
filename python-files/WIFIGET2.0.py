import os
import sys
import subprocess

def run_vbscript():
    vbscript_content = '''
Set objShell = CreateObject("WScript.Shell")
Set objExec = objShell.Exec("netsh wlan show profiles")

Dim cmdOutput
Dim outputText

outputText = ""

Do Until objExec.StdOut.AtEndOfStream
    cmdOutput = objExec.StdOut.ReadLine
    outputText = outputText & cmdOutput & vbCrLf
Loop

WScript.Echo outputText
    '''

    vbscript_path = 'show_profiles.vbs'
    
    try:
        with open(vbscript_path, 'w') as file:
            file.write(vbscript_content)
        
        output = subprocess.check_output(['cscript', '//NoLogo', vbscript_path], text=True, encoding='utf-8', errors='ignore')
        print("Rohdaten vom VBScript:")
        print(output)
        return output
    
    except subprocess.CalledProcessError as e:
        print(f"VBScript-Ausführung fehlgeschlagen: {e}")
        return None
    
    finally:
        if os.path.exists(vbscript_path):
            os.remove(vbscript_path)

def update_vbscript(network_name):
    if not network_name:
        print("Netzwerkname darf nicht leer sein.")
        return

    vbscript_content = f'''
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

Dim notepadFileName
notepadFileName = "WIFIINFO.txt"

strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strFilePath = objFSO.BuildPath(strScriptDir, notepadFileName)

If Not objFSO.FileExists(strFilePath) Then
    Set objFile = objFSO.CreateTextFile(strFilePath)
    objFile.WriteLine "WLAN-Profile und Passwörter:"
    objFile.Close
End If

Set objExec = objShell.Exec("netsh wlan show profile name=""" & WScript.Arguments(0) & """ key=clear")

Dim cmdOutput
Dim outputText

outputText = ""

Do Until objExec.StdOut.AtEndOfStream
    cmdOutput = objExec.StdOut.ReadLine
    outputText = outputText & cmdOutput & vbCrLf
Loop

WScript.Echo "Profil: " & WScript.Arguments(0) & vbCrLf & "------------------------" & vbCrLf & outputText

Set objFile = objFSO.OpenTextFile(strFilePath, 8, True)
objFile.WriteLine "Profil: " & WScript.Arguments(0)
objFile.WriteLine "------------------------"
objFile.WriteLine outputText
objFile.Close
    '''

    vbscript_path = 'update_network.vbs'
    
    try:
        with open(vbscript_path, 'w') as file:
            file.write(vbscript_content)
        print("Die VBScript-Datei wurde erfolgreich aktualisiert!")
        
        profile_info = subprocess.check_output(['cscript', '//NoLogo', vbscript_path, network_name], text=True, encoding='utf-8', errors='ignore')
        print("\nProfilinformationen:\n")
        print(profile_info)
    
    except subprocess.CalledProcessError as e:
        print(f"VBScript-Ausführung fehlgeschlagen: {e}")
    
    finally:
        if os.path.exists(vbscript_path):
            os.remove(vbscript_path)

def main():
    print(r"""
  _______________________________________________________________________
____|___|_____|____|____|_____|____|____|____|_____|____|____|_____|___
_|____|__|_____|_____|____|____|____|_____|___|______|___|____|_____|__
/  \|___/  \|   |\_   _____/|   |__|___/  _____/_\    _____/\_      __/
\   \/\/   /|   ||_|  ___)__|   |_|___/   \_______|    __)____|    |_|_
_\        /_|   |__|  \___|_|   |___|_\    \_\  \_|        \|_|    |___
__\__/\  /__|___|_/___  /|__|___||_____\______  //_______  /__|____|_|_
___|___\/_____|_______\/__|___|_____|_____|___\/____|____\/____|_____|_
_____|____|__|_____|_____|___|____|____|_____|____|____|______|_____|__     
  

Haftungsausschluss:

Dieses Programm dient der Wiederherstellung von WLAN-Passwörtern auf einem PC.
Es ist für rechtliche und ethische Anwendungen gedacht. Unbefugter Zugriff auf Netzwerke ist illegal.

Verantwortung:

Sie sind verantwortlich, sicherzustellen, dass Ihre Nutzung allen geltenden Gesetzen entspricht.

Keine Garantie:

Es gibt keine Garantie für erfolgreiche Ergebnisse.

Haftungsbeschränkung:

Die Ersteller haften nicht für Schäden aus der Nutzung des Programms.

Benutzervereinbarung:

Sie stimmen zu, die Ersteller von Ansprüchen freizustellen, die aus der Nutzung des Programms entstehen.
""")
    print()

    agree = input("Stimmen Sie dem obigen Haftungsausschluss zu? (j/n): ").strip().lower()
    if agree != 'j':
        print("Sie haben dem Haftungsausschluss nicht zugestimmt. Das Programm wird beendet.")
        sys.exit()

    print("\nBitte warten Sie, während wir die verfügbaren WLAN-Profile abrufen...\n")
    profiles_output = run_vbscript()

    if profiles_output:
        profiles = []
        lines = profiles_output.splitlines()
        for line in lines:
            if "Profil für alle Benutzer" in line or "Profil f?r alle Benutzer" in line:
                profile_name = line.split(":")[1].strip()
                profiles.append(profile_name)
        
        if profiles:
            print("Verfügbare WLAN-Profile:")
            for idx, profile in enumerate(profiles, 1):
                print(f"{idx}: {profile}")
            
            try:
                profile_choice = int(input("\nWelches Netzwerk? Geben Sie die entsprechende Nummer ein: "))
                if 1 <= profile_choice <= len(profiles):
                    selected_profile = profiles[profile_choice - 1]
                    update_vbscript(selected_profile)
                else:
                    print("Ungültige Auswahl. Das Programm wird beendet.")
                    sys.exit()
            except ValueError:
                print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein, die dem Profil entspricht. Das Programm wird beendet.")
                sys.exit()
        else:
            print("Keine WLAN-Profile gefunden. Das Programm wird beendet.")
            sys.exit()
    else:
        print("Fehler beim Abrufen der WLAN-Profile. Das Programm wird beendet.")
        sys.exit()

    input("\nDrücken Sie die Eingabetaste, um das Programm zu beenden...")

if __name__ == "__main__":
    main()
