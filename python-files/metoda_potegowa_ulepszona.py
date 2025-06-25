# biblioteka do obliczeń numerycznych
import numpy as np
# biblioteka do tworzenia wykresów
import matplotlib.pyplot as plt


def metoda_potegowa_ulepszona(macierz, maks_iteracje=1000, tolerancja=1e-8, uzyj_aitkena=True):
    rozmiar = macierz.shape[0] # ile wierszy
    wektor = np.random.rand(rozmiar) # wygenerowanie wektora
    wektor = wektor / np.linalg.norm(wektor) # normalizacja wektora
    przyblizenia_lambda = [] # inicjalizacja tablicy do przechowywania kolejnych przybliżeń

    for krok in range(maks_iteracje):
        x = macierz @ wektor # mnożenie macierzy przez wektor
        wektor = x / np.linalg.norm(x) # zastąpienie wektora innym, znormalizowanym
        lambda_k = wektor.T @ macierz @ wektor # obliczenie lambdy
        przyblizenia_lambda.append(lambda_k) # zapisanie przybliżenia lambdy

        # użycie Aitkena po trzech iteracjach
        if krok >= 2 and uzyj_aitkena:
            lam0, lam1, lam2 = przyblizenia_lambda[-3:] # wzięcie trzech ostatnich przybliżeń
            mianownik = lam2 - 2 * lam1 + lam0
            if mianownik != 0:
                lambda_aitken = lam0 - ((lam1 - lam0) ** 2) / mianownik # zastosowanie wzoru Aitkena
                # Standardowe kryterium zbieżności
                if abs(lambda_aitken - lam2) < tolerancja:
                    return lambda_aitken, wektor, krok + 1, przyblizenia_lambda

        # Standardowe kryterium zbieżności
        if krok > 0 and abs(przyblizenia_lambda[-1] - przyblizenia_lambda[-2]) < tolerancja:
            return przyblizenia_lambda[-1], wektor, krok + 1, przyblizenia_lambda

    return przyblizenia_lambda[-1], wektor, maks_iteracje, przyblizenia_lambda

def podsumowanie(macierz):
    print("Analiza macierzy:\n", macierz)
    # Uruchomienie głównej metody
    lambda_dominujaca, wektor_wlasny, liczba_iteracji, historia_lambda = metoda_potegowa_ulepszona(macierz)
    # Wyniki
    print("=================================================================")
    print("Dominująca wartość własna:", lambda_dominujaca)
    print("Wektor własny (znormalizowany):", wektor_wlasny)
    print("Liczba iteracji:", liczba_iteracji)
    print("=================================================================")
    # Wykres zbieżności
    plt.figure(figsize=(8, 5))
    plt.plot(historia_lambda, marker='o', label="λ (kolejne przybliżenia)")
    plt.axhline(y=lambda_dominujaca, color='red', linestyle='--', label=f"λ ≈ {lambda_dominujaca:.6f}")
    plt.title("Zbieżność dominującej wartości własnej")
    plt.xlabel("Numer iteracji")
    plt.ylabel("Przybliżenie λ")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Przykładowa macierz symetryczna
macierz_testowa_jak_w_pliku = np.array([[2, 1],[1, 3]])
# Wywołanie funkcji podsumowującej, w tym liczącej
podsumowanie(macierz_testowa_jak_w_pliku)

#Inne, przykładowe wywołania
macierz_2 = np.array([[4,1],[2,3]])
podsumowanie(macierz_2)
macierz_3 = np.array([[10,-7,5], [1,2,-3], [0,5,8]])
podsumowanie(macierz_3)
macierz_symetryczna = np.array([[1,-2,3],[-2,2,5],[3,5,3]])
podsumowanie(macierz_symetryczna)

while True:
    odpowiedz = input("\nCzy chcesz wprowadzić własną macierz? (tak/nie): ").strip().lower()

    if odpowiedz == "nie":
        print("Zakończono działanie programu.")
        break
    elif odpowiedz == "tak":
        try:
            rozmiar = int(input("Podaj rozmiar macierzy (liczba całkowita > 1): "))
            if rozmiar < 2:
                print("Rozmiar macierzy musi być większy niż 1.")
                continue

            print(f"Podaj {rozmiar} wiersze macierzy. Każdy wiersz to {rozmiar} liczby oddzielonych spacją.")
            wiersze = []
            for i in range(rozmiar):
                while True:
                    wiersz_str = input(f"Wiersz {i+1}: ").strip()
                    wiersz = [float(x) for x in wiersz_str.split()]
                    if len(wiersz) != rozmiar:
                        print(f"Błąd: wiersz musi zawierać dokładnie {rozmiar} liczb.")
                    else:
                        wiersze.append(wiersz)
                        break

            macierz_uzytkownika = np.array(wiersze)
            podsumowanie(macierz_uzytkownika)

        except ValueError:
            print("Błąd: podano nieprawidłowe dane. Spróbuj ponownie.")
    else:
        print("Proszę odpowiedzieć 'tak' lub 'nie'.")