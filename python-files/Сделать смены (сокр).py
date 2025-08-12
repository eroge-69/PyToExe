import random
from collections import defaultdict
from datetime import datetime, timedelta
import sys
import os

# входные данные
groups = {
    "Группа 1": 10,
    "Группа 2": 5,
    "Группа 3": 6,
    "Группа 4": 9,
    "Группа 5": 8,
    "Группа 6": 10,
}

shifts = {
    "А": 1,
    "ДО": 4,
    "Ф": 1,
    "П": 2,
    "49": 2
}


class Logger:
    def __init__(self, month, year):
        self.terminal = sys.stdout
        self.log = open(f"Смены на {month}.{year} (сокр).txt", "w", encoding="utf-8")
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def close(self):
        self.log.close()


def input_days(prompt):
    while True:
        try:
            days_input = input(prompt).strip()
            if not days_input:
                return []
            days = list(map(int, days_input.split(',')))
            if all(1 <= day <= 31 for day in days):
                return sorted(days)
            print("Ошибка: дни должны быть числами от 1 до 31")
        except ValueError:
            print("Ошибка: введите числа через запятую (например, 1,5,10,15,28)")


def select_month_and_year():
    now = datetime.now()
    while True:
        choice = input("Выберите месяц (1 - текущий, 2 - следующий): ").strip()
        if choice == '1':
            return now.month, now.year
        elif choice == '2':
            next_month = now.month % 12 + 1
            next_year = now.year if now.month < 12 else now.year + 1
            return next_month, next_year
        else:
            print("Некорректный ввод данных. Введите 1 или 2.")


def input_group_exceptions(groups):
    exceptions = defaultdict(list)
    print("\nВвод исключений для групп (оставьте пустым, если нет исключений):")
    for group in groups:
        while True:
            days_input = input(f"Дни, когда {group} не доступна (через запятую): ").strip()
            if not days_input:
                break
            try:
                days = list(map(int, days_input.split(',')))
                if all(1 <= day <= 31 for day in days):
                    exceptions[group] = days
                    break
                print("Ошибка: дни должны быть числами от 1 до 31")
            except ValueError:
                print("Ошибка: введите числа через запятую")
    return exceptions


def distribute_shifts():
    
    # ввод данных
    month, year = select_month_and_year()
    
    # Перенаправляем вывод в файл и консоль
    logger = Logger(month, year)
    sys.stdout = logger
    
    try:
       
        print()
        group_exceptions = input_group_exceptions(groups)
        print()

        shift_days = {}
        for shift in shifts:
            prompt = f"Введите дни для смены {shift} (через запятую, если смен нет, оставьте пустое поле): "
            days = input_days(prompt)
            if days:
                shift_days[shift] = days

        if not shift_days:
            print("Нет ни одной смены для распределения!")
            return

        print()
        # создаем список всех дат смен
        all_dates = []
        input_shift_counts = defaultdict(int)  # для статистики
        for shift, days in shift_days.items():
            for day in days:
                try:
                    date = datetime(year, month, day)
                    all_dates.append((date, shift))
                    input_shift_counts[shift] += 1
                except ValueError:
                    print(f"Предупреждение: {day}.{month}.{year} - некорректная дата. Пропускаем.")

        if not all_dates:
            print("Нет корректных дат для распределения смен!")
            return

        # сортируем даты
        all_dates.sort()

        # инициализация данных
        group_people = {group: list(range(1, count + 1)) for group, count in groups.items()}
        group_usage = {group: 0 for group in groups}
        group_relative_usage = {group: 0 for group in groups}
        person_usage = {group: defaultdict(int) for group in groups}
        shift_counts = {group: defaultdict(int) for group in groups}
        weekend_shifts = defaultdict(int)  # для балансировки выходных
        schedule = []
        distributed_shift_counts = defaultdict(int)  # для статистики

        for date, shift_type in all_dates:
            day_of_week = date.weekday()
            is_weekend = day_of_week >= 5  # 5 - суббота, 6 - воскресенье

            # проверка для смены Ф (не воскресенье)
            if shift_type == "Ф" and day_of_week == 6:
                print(f"Предупреждение: смена Ф не может быть в воскресенье ({date.strftime('%d.%m.%Y')}). Пропускаем.")
                continue

            # проверка исключений для групп
            def is_group_available(group, day):
                return day not in group_exceptions.get(group, [])

            people_needed = shifts[shift_type]
            selected_groups = []
            selected_people = []

            for _ in range(people_needed):
                found = False
                # Первый приоритет - свободные люди с учетом выходных баланса
                candidate_groups = [
                    g for g in groups 
                    if group_people[g] and is_group_available(g, date.day)
                ]

                if candidate_groups:
                    # Балансировка выходных
                    if is_weekend:
                        min_weekend = min(weekend_shifts.get(g, 0) for g in candidate_groups)
                        candidate_groups = [g for g in candidate_groups if weekend_shifts.get(g, 0) == min_weekend]

                    # Минимизация нагрузки
                    min_rel_usage = min(group_relative_usage[g] for g in candidate_groups)
                    candidate_groups = [g for g in candidate_groups if group_relative_usage[g] == min_rel_usage]

                    # Убедимся, что группа еще не выбрана для этой смены
                    candidate_groups = [g for g in candidate_groups if g not in selected_groups]

                    if candidate_groups:
                        selected_group = random.choice(candidate_groups)
                        selected_person = group_people[selected_group].pop(0)
                        found = True

                # Если не нашли свободных, ищем среди всех людей
                if not found:
                    available_groups = [
                        g for g in groups 
                        if is_group_available(g, date.day) and g not in selected_groups
                    ]
                    if not available_groups:
                        print(f"Ошибка: нет доступных групп для смены {shift_type} {date.strftime('%d.%m.%Y')}")
                        continue

                    # Выбираем группу с минимальной нагрузкой
                    selected_group = min(
                        available_groups,
                        key=lambda g: (group_relative_usage[g], weekend_shifts.get(g, 0) if is_weekend else 0)
                    )

                    # Выбираем человека с минимальной нагрузкой в группе
                    min_person_load = min(person_usage[selected_group].values()) if person_usage[selected_group] else 0
                    candidates = [
                        p for p in range(1, groups[selected_group]+1)
                        if person_usage[selected_group].get(p, 0) == min_person_load
                    ]
                    selected_person = random.choice(candidates) if candidates else 1

#                     print(f"Повторное назначение: {selected_group} (чел {selected_person}) на {date.strftime('%d.%m.%Y')}")

                selected_groups.append(selected_group)
                selected_people.append(selected_person)

                # обновляем статистику
                hours = 24 if shift_type != "П" else 2
                group_usage[selected_group] += hours
                group_relative_usage[selected_group] = group_usage[selected_group] / groups[selected_group]
                person_usage[selected_group][selected_person] += hours
                shift_counts[selected_group][shift_type] += 1
                distributed_shift_counts[shift_type] += 1
                if is_weekend:
                    weekend_shifts[selected_group] = weekend_shifts.get(selected_group, 0) + 1

            # добавляем в расписание
            schedule.append({
                "date": date.strftime("%d.%m.%Y"),
                "day_of_week": date.strftime("%A"),
                "shift": shift_type,
                "groups": selected_groups.copy(),
                "people": selected_people.copy()
            })

        # вывод результатов
        print("\nРасписание смен:")
        print("Дата     | День недели   | Смена | Группы (люди)")
        print("-" * 50)
        for entry in schedule:
            groups_people = []
            for group, person in zip(entry["groups"], entry["people"]):
                groups_people.append(f"{group}")
            print(
                f"{entry['date']}     | {entry['day_of_week'].ljust(10)}  | {entry['shift'].ljust(5)} | {', '.join(groups_people).replace('Группа ','')}")

        # статистика по группам
        print("\nСтатистика по группам:")
        print("Группа   | Всего   | В сменах    | Нагрузка (часы)    | Нагрузка/чел | Выходные | Распределение смен")
        print("-" * 110)
        for group in groups:
            total_people = groups[group]
            people_in_shifts = total_people - len(group_people[group])
            total_hours = group_usage[group]
            hours_per_person = total_hours / total_people if total_people > 0 else 0
            shift_dist = ", ".join(f"{k}:{v}" for k, v in shift_counts[group].items() if v > 0)
            weekend_count = weekend_shifts.get(group, 0)
            print(
                f"{group.ljust(7)} | {str(total_people).ljust(6)} | {str(people_in_shifts).ljust(9)} | {str(round(total_hours, 1)).ljust(15)} | {str(round(hours_per_person, 2)).ljust(12)} | {str(weekend_count).ljust(7)}  | {shift_dist}")

        # статистика по нагрузке на людей
        print("\nСтатистика нагрузки на людей:")
        for group in groups:
            print(f"\n{group}:")
            for person in sorted(person_usage[group].keys()):
                print(f"Чел {person}: {person_usage[group][person]} часов")

        # статистика по распределенным сменам
        print("\nСтатистика по сменам:")
        print("Тип смены | Запрошено | Распределено")
        print("-" * 30)
        for shift in input_shift_counts:
            print(f"{shift.ljust(8)} | {str(input_shift_counts[shift]).ljust(8)} | {distributed_shift_counts.get(shift, 0)}")
        
        # нераспределенные смены
        print("\nНераспределенные смены:")
        has_unassigned = False
        for shift in input_shift_counts:
            if input_shift_counts[shift] > distributed_shift_counts.get(shift, 0):
                print(f"{shift}: {input_shift_counts[shift] - distributed_shift_counts.get(shift, 0)} из {input_shift_counts[shift]}")
                has_unassigned = True
        if not has_unassigned:
            print("Все смены распределены успешно!")

        print("\nИспользованные типы смен:", ", ".join(shift_days.keys()))
        unused_shifts = set(shifts.keys()) - set(shift_days.keys())
        if unused_shifts:
            print("Не использованные типы смен в этом месяце:", ", ".join(unused_shifts))
            
        # Информируем пользователя о сохранении файла
        datePath = f"Смены на {month}.{year} (сокр).txt"
        file_path = os.path.join(os.getcwd(), datePath)
        print(f"\nРезультаты сохранены в файл: {file_path}")

    finally:
        # Восстанавливаем стандартный вывод и закрываем файл
        sys.stdout = logger.terminal
        logger.close()


if __name__ == "__main__":
    distribute_shifts()