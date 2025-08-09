import datetime

def main():
    try:
        days = int(input("Введіть кількість днів від сьогодні: "))
    except ValueError:
        print("Будь ласка, введіть ціле число.")
        return

    today = datetime.date.today()
    future_date = today + datetime.timedelta(days=days)

    days_of_week = {
        0: "Понеділок",
        1: "Вівторок",
        2: "Середа",
        3: "Четвер",
        4: "П'ятниця",
        5: "Субота",
        6: "Неділя"
    }

    months_ua = {
        1: "Січня",
        2: "Лютого",
        3: "Березня",
        4: "Квітня",
        5: "Травня",
        6: "Червня",
        7: "Липня",
        8: "Серпня",
        9: "Вересня",
        10: "Жовтня",
        11: "Листопада",
        12: "Грудня"
    }

    print(f"Через {days} днів буде: {future_date.day} {months_ua[future_date.month]} {future_date.year} року, {days_of_week[future_date.weekday()]}")

if __name__ == "__main__":
    main()
