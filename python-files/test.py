import random
val = random.random()
print(val)
print(f"{(random.random() * 8 + 10)/100:.2%}")

instrukcja = input("\nWprowadź polecenie (wielkosc znakow nie ma znaczenia): \n\n 1. Lista przedmiotow: i, albo inventory\n 2. Dodaj przedmiot: add \n 3. Weź zeby uzyc: use, consume, take. Mozesz od razu podac ID przedmiotu, np. 'use 3' \n 4. Wyjdz i zapisz: quit lub q. \n")

parts = instrukcja.split()
command = parts[0].lower()
dlugosc_polecenia = len(parts)
if dlugosc_polecenia > 1:
    item = int(parts[1])

print(f"instrukcja: {instrukcja}, parts: {parts}, długość polecenia {dlugosc_polecenia}")