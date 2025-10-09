Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> # Vraag de USB-stick locatie
... usb_stick_path = input("Typ de letter van je USB-stick (bijv. E) en druk Enter: ").strip().upper() + ":\\"
... 
... # Naam van het bestand
... bestand_naam = "disable_family_link.py"
... 
... # De code die je wilt opslaan
... tekst = """import subprocess
... 
... def disable_family_link():
...     subprocess.run(["adb","shell","am","force-stop","com.google.android.familylinks"])
...     subprocess.run(["adb","shell","pm","disable-user","-user", "0","com.google.android.familylinks"])
... 
... # USB stick insteken detecteren
... while True:
...     try:
...         subprocess.run(["adb","devices"], check=True)
...         disable_family_link()
...         break
...     except subprocess.CalledProcessError:
...         pass
... 
... # Familie Link blijft uitgeschakeld totdat de USB stick wordt verwijderd
... while True:
...     try:
...         subprocess.run(["adb","devices"], check=True)
...     except subprocess.CalledProcessError:
...         break
... """
... 
... # Bestand opslaan
... volledige_pad = usb_stick_path + bestand_naam
... with open(volledige_pad, "w", encoding="utf-8") as f:
...     f.write(tekst)
... 
... print(f"Bestand succesvol opgeslagen op {volledige_pad}")
