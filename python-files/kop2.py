import random

#Vygeneruj náhodné číslo od 1 do 100
tajne_cislo = random.randit(1, 100)

print(Ahoj! Zkus Uhodnout číslo od 1 do 100.")

while True: hadani = int(input("Zadej své číslo: "))

if hadani < tajne_cislo:
    print("Příliš nízké!")
    elif hadani > tajne_cislo:
        print("Příliš vysoké!")
        else:
            print("Gratuluju! Uhodl jsi číslo!")
            break