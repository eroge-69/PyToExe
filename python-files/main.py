import time
import openpyxl
from datetime import datetime

# Funkcja do zapisania zeskanowanego kodu QR do pliku Excel
def save_to_excel(qr_content, filename="scanned_qr_codes.xlsx"):
    try:
        # Jeśli plik nie istnieje, utwórz nowy plik Excel
        try:
            wb = openpyxl.load_workbook(filename)
            sheet = wb.active
        except FileNotFoundError:
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet["A1"] = "Treść kodu QR"  # Nagłówek kolumny
            sheet["B1"] = "Ilość wystąpień"  # Nagłówek dla liczby
            sheet["C1"] = "Data zeskanowania"  # Nagłówek dla daty

        # Pobranie dzisiejszej daty (bez godziny)
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Szukaj, czy kod QR już istnieje w pliku
        found = False
        for row in range(2, sheet.max_row + 1):
            if sheet[f"A{row}"].value == qr_content:
                # Zwiększ liczbę wystąpień o 1
                sheet[f"B{row}"].value += 1
                found = True
                break

        if not found:
            # Jeśli kod QR nie został znaleziony, dodaj nowy wpis
            row = sheet.max_row + 1
            sheet[f"A{row}"] = qr_content
            sheet[f"B{row}"] = 1  # Liczba wystąpień to 1
            sheet[f"C{row}"] = current_date  # Dodanie daty

        # Zapisz plik
        wb.save(filename)
        print(f"Zapisano do pliku: {filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

def main():
    print("Czekam na zeskanowanie kodu QR...")

    while True:
        # Oczekiwanie na zeskanowanie danych przez skaner QR (np. przez skaner jako input z klawiatury)
        qr_content = input("Treść skanowanego kodu QR: ")

        if qr_content:
            # Zapisz treść do pliku Excel
            save_to_excel(qr_content)
            print(f"Zeskanowany kod QR zawiera treść: {qr_content}")

        # Możesz dodać warunek zakończenia programu, np. po wpisaniu 'exit'
        if qr_content.lower() == 'exit':
            print("Zakończenie programu.")
            break

        time.sleep(0.1)  # Drobne opóźnienie, by program nie działał zbyt szybko

if __name__ == "__main__":
    main()
