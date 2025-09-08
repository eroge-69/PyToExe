# Словарь с вашими кодами и никнеймами
nicknames = {
    "RRNX": "чиба",
    "SNIEZ": "клюв",
    "PO_LN": "магмуст",
    "E7OZX": "Винсери",
    "HRQMJ": "градиент",
    "EDZKY": "элвин",
    "W5HTU": "Оля",
    "9KFTN": "пупи",
    "RHQJB": "вак макак",
    "AKGQU": "кавкин",
    "FCQWN": "утка",
    "-YU0J": "говернед",
    "UK0RC": "опти",
    "HEWZH": "мафинев",
    "4P9G9": "севетян",
    "-3I4J": "нагибайка",
    "IKWEL": "клюв 2 акк",
}


def find_nickname():
    print("Программа поиска никнейма по коду")
    print("Доступные коды:", ", ".join(nicknames.keys()))

    while True:
        code = input("\nВведите код (или 'выход' для завершения): ").strip().upper()

        if code in ["ВЫХОД", "EXIT", "QUIT"]:
            print("Программа завершена.")
            break

        if code in nicknames:
            print(f"Код: {code} → Никнейм: {nicknames[code]}")
        else:
            print(f"Код '{code}' не найден в списке.")


# Запуск программы
if __name__ == "__main__":
    find_nickname()
