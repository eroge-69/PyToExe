def th_to_green(th_hex):
    """
    Zamienia ciąg hex (o długości <= 10 znaków, jeśli obcięto zera) 
    na (FC, ID) w schemacie 40-bit: [20b FC][19b ID][1b].
    """
    val = int(th_hex, 16)
    fc = val >> 20
    id_ = (val >> 1) & 0x7FFFF
    return fc, id_

def green_to_th(fc, id_):
    """
    Układa FC (20 bitów) i ID (19 bitów) w 40-bit [FC<<20 | ID<<1 | parity_bit].
    Zwraca 10-znakowy ciąg hex (wielkie litery),
    przy czym parity_bit jest wyliczany tak, żeby łącznie 40 bitów miało parzystą liczbę '1'.
    """
    # 1) Składamy 39 bitów (FC i ID)
    val_39 = (fc << 19) | id_

    # 2) Sprawdzamy liczbę jedynek
    ones_count = bin(val_39).count('1')

    # 3) Dla even parity – jeśli jest nieparzysta liczba jedynek, dajemy bit = 1, w przeciwnym razie 0
    if ones_count % 2 == 0:
        parity_bit = 0
    else:
        parity_bit = 1

    # 4) Układamy w 40-bit: przesuwamy val_39 o 1 bit i dodajemy parity_bit
    val = (val_39 << 1) | parity_bit

    # 5) Zwracamy 10-znakowy ciąg hex
    return f"{val:010X}"

def convert_code(code_str):
    """
    Rozpoznaje, czy 'code_str' to TH (hex) czy Green (FC-ID).
    Zwraca string z wynikiem konwersji.
    """
    code_str = code_str.strip().upper()

    # Rozpoznanie: jeśli mamy myślnik '-', to traktujemy jako Green
    if '-' in code_str:
        try:
            fc_str, id_str = code_str.split('-', 1)
            fc = int(fc_str)
            cid = int(id_str)
        except ValueError:
            return f"BŁĄD: niepoprawny format Green: '{code_str}'"
        th_hex = green_to_th(fc, cid)
        return f"Green '{code_str}' → TH = {th_hex}"

    else:
        # W przeciwnym razie traktujemy to jako TH (hex)
        # Sprawdzamy, czy to jest poprawny hex
        try:
            _ = int(code_str, 16)
        except ValueError:
            return f"BŁĄD: niepoprawny ciąg (ani TH, ani Green): '{code_str}'"
        fc, cid = th_to_green(code_str)
        # Formatowanie Green – 5 cyfr dla FC, 6 cyfr dla ID (jak w oryg. przykładach)
        return f"TH '{code_str}' → Green = {fc:05d}-{cid:06d}"

def main():
    print(" \n")
    print("Program konwertuje kody między TH (hex) a Green (FC-ID).")
    print("Możesz podać wiele kodów naraz, rozdzielonych przecinkami.\n")
    print("Przykłady jednego kodu:")
    print("  TH: 0068737284 (lub 68737284)")
    print("  Green: 01671-112962\n")
    print("Przykład wielu kodów po przecinku:")
    print("  0068737284,01671-112962,68737284\n")

    while True:
        # Wczytujemy linię z ewentualnie wieloma kodami
        codes_line = input("Podaj kod(y) rozdzielone przecinkami (lub pusty, żeby zakończyć): ")
        codes_line = codes_line.strip()
        if not codes_line:
            # jeśli pusty – zakończ
            print("Koniec programu (pusty wiersz).")
            break

        # Rozdzielamy po przecinku
        codes = codes_line.split(',')
        # Przetwarzamy każdy kod osobno
        for code in codes:
            result = convert_code(code)
            print(result)

        # Pytamy, czy chcemy kolejną partię kodów
        kont = input("\nChcesz sprawdzić kolejną partię kodów? (T/N): ").strip().upper()
        if kont != 'T':
            print("Koniec programu.")
            break

if __name__ == "__main__":
    main()
