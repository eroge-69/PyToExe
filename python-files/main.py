# Importing libs
import os
import sys
import locale
import os.path
import platform
from pathlib import Path
from datetime import datetime, timedelta


# Imposta la localizzazione italiana
if "linux" in platform.system().lower():
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')  # Linux
else:
    locale.setlocale(locale.LC_TIME, 'Italian_Italy')  # Windows

# Setting version
VER = "2.1"

# Setting current date
currentDate = datetime.now()
lastDate = currentDate - timedelta(days=30)

# Setting flex vars
flexpos = 0
flexneg = 0
partoins = 0
has700 = False

#Setting files var
lastMonth = lastDate.strftime("%m%y")
currentMonth = currentDate.strftime("%m%y")
filenameLastMonth = None
filanameCurrentMonth = None
lastMonth_time = 0
currentMonth_time = 0
downloads_path = Path.home() / "Downloads"

# Searching for last and current month files
for filename_temp in os.listdir(downloads_path):
    if filename_temp.startswith('clkcard') and filename_temp.endswith(".txt"):
        file_path = downloads_path / filename_temp
        file_time = file_path.stat().st_mtime  # Tempo di modifica
        
        if lastMonth in filename_temp:
            if file_time > lastMonth_time:
                filenameLastMonth = filename_temp
                lastMonth_time = file_time
                
        elif currentMonth in filename_temp:
            if file_time > currentMonth_time:
                filanameCurrentMonth = filename_temp
                currentMonth_time = file_time

if not filenameLastMonth is None and not filanameCurrentMonth is None:
    if not os.path.isfile(downloads_path / filenameLastMonth) or not os.path.isfile(downloads_path / filanameCurrentMonth):
        print("File cartellino non trovati")
        sys.exit()

# Meme
print(f"Marcianise, Italia - E' da tanto che non flexo - V{VER}")

# Asking for data
dayLastMonth = int(input(f"Inserisci il giorno di INIZIO flex di {currentDate.strftime("%B").capitalize()} (X {lastDate.strftime("%B").capitalize()}): "))
dayCurrentMonth = int(input(f"Inserisci il giorno di FINE flex di {currentDate.strftime("%B").capitalize()}: "))

# Reading last month
with open(downloads_path / filenameLastMonth, 'r') as file:
    for line in file:
        line = line.strip()
        line = ' '.join(line.split())
        
        if "Flex" in line and not any(x in line for x in ["Saldo", "HHLAV", "HHFLP", "PSERV", "HLAVO", "GLAVO", "DELTA", "Permesso", "Fruizione"]) and int(line[0]) >= dayLastMonth:
            elements = line.split()
            flexindex = elements.index("Flex")
            flex = elements[flexindex - 1]
            flexsplit = flex.split('.')
            flexmins = int(flexsplit[-1])
            flexhours = int(flexsplit[0]) * 60
            flex = flexmins + flexhours
            
            if "Flex -" in line:
                flexneg = flexneg + flex
            if "Flex +" in line:
                flexpos = flexpos + flex

# Reading current month
with open(downloads_path / filanameCurrentMonth, 'r') as file:
    for line in file:
        line = line.strip()
        line = ' '.join(line.split())
        
        if "Flex" in line and not any(x in line for x in ["Saldo", "HHLAV", "HHFLP", "PSERV", "HLAVO", "GLAVO", "DELTA", "Permesso", "Fruizione"]) and int(line[0]) <= dayCurrentMonth:
            elements = line.split()
            flexindex = elements.index("Flex")
            flex = elements[flexindex - 1]
            flexsplit = flex.split('.')
            flexmins = int(flexsplit[-1])
            flexhours = int(flexsplit[0]) * 60
            flex = flexmins + flexhours
            
            if "Flex -" in line:
                flexneg = flexneg + flex
            if "Flex +" in line:
                flexpos = flexpos + flex

        # Additional logic to prevent "SOLDINI IN MENOOOOO"
        if line.startswith("700"):
            elements = line.split()
            findex = elements.index("(F")
            par = elements[findex + 1]
            parsplit = par.split('.')
            parmins = int(parsplit[-1])
            parhours = int(parsplit[0]) * 60
            partoins = partoins + (parmins + parhours)
            has700 = True

# Check flex
if flexpos == 0 and flexneg == 0:
    print('Non ci sono flex da mostrare. Controlla i file cartellino.')
    sys.exit()

# Print flex
print(f"Flex accumulato: {flexpos} minuti\nFlex usufruito: {flexneg} minuti")

# Calculate positive and negative
flexrim = flexpos-flexneg

# Print
if(flexrim < 0):
    flexrim = abs(flexrim)
    print(f"Sei in negativo di: {flexrim} minuti")
else:
    print(f"Flex rimanente: {flexrim} minuti")

# Fuck, soldini in meno!
if has700:
    print(f"ATTENZIONE! Hai da inserire {partoins} minuti di PAR per flex non retribuito!")