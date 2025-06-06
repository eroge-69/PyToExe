kwota = float(input("Podaj kwotę: "))
procent_input = float(input("Podaj procent (-x/x): "))
procent = float(procent_input) / 100
dzwignia = float(input("Podaj dźwignię (x:1): "))

wynik = kwota * dzwignia * procent

if wynik < 0:
    print(f"Straciłeś: {abs(wynik)}")
else:
    print(f"Zyskałeś: {wynik}")