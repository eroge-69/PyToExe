import random

########### Funktionen ################

def getAugenzahl(x, y):
    z = random.randint(x, y)
    return z

def isPasch (a, b, c):
    if a == b == c:
        k = 2
        print("Pasch")
    else:
        k = 1
    return k

def getAugensumme (a, b, c, d):
    sum = (a+b+c)*d
    return sum


############# Hauptporgramm #############
punktestand = 0
runde = 1

nutzereingabe = nutzereingabe = input("Bereit für die nächste Runde (a zum Abbrechen, beliebige Eingabe zum fortfahren)? ")

while nutzereingabe != 'a':
    print("++++ Runde", runde,"++++")

    # Würfelzahlen zufällig bestimmen
    wuerfel1 = getAugenzahl(1, 6)
    wuerfel2 = getAugenzahl(1,6)
    wuerfel3 = getAugenzahl(1,6)
    print("Würfelzahl 1:",wuerfel1)
    print("Würfelzahl 2:",wuerfel2)
    print("Würfelzahl 3:",wuerfel3)
    pasch = isPasch(wuerfel1, wuerfel2, wuerfel3)
    augensumme = getAugensumme(wuerfel1, wuerfel2, wuerfel3, pasch,)
    print(augensumme)
    

    # # Neuen Punktestand berechnen
    # punktestand = punktestand + getAugensumme(wuerfel1, wuerfel2, wuerfel3)
    # print("Dein Punktestand:", punktestand)

    # Vorbereitung der nächsten Runde
    nutzereingabe = input("Bereit für die nächste Runde (a zum Abbrechen, beliebige Eingabe zum fortfahren)? ")
    runde = runde + 1

print("Spielende")