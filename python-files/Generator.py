# Dieses Programm ist ein Generator
# 03.08.2025
# nach test.xml

# Definition der Variablen
dienst = ''
ausgabestring = ''
nato = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot',
        'golf', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike',
        'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango',
        'uniform', 'victor', 'whiskey', 'xray', 'yankee', 'zulu']

#Programm
print('Dienstnamen eingeben:')
dienst = input()
dienst = dienst.lower()

# Berechnung
i=0
laenge = len(dienst)

if laenge < 4:
    laenge = len(dienst)-1
else:
    laenge = 3

while i < 26:
    nator = nato[i] 
    if nator[0] == dienst[laenge]:
        i=26
        nator = nator[0] + nator[1].upper() + nator[2:]
    else:
        i=i+1
       
# Ausgabe
ausgabestring = 'Ka..' + nator + '?fEr2!0' + dienst[0]
print('Das Ergebnis lautet', ausgabestring)
dienst = input()
