import calendar
from datetime import datetime, timedelta
import random
from collections import defaultdict
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def generate_duty_schedule(people, day_duty_count, night_duty_count, months_count=1):

    if len(people) < 20:
        raise ValueError("Список людей должен содержать минимум 20 человек")

    if months_count < 1 or months_count > 12:
        raise ValueError("Количество месяцев должно быть от 1 до 12")

    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # Определяем начало и конец периода
    start_date = today.replace(day=1)
    all_dates = []

    for month_offset in range(months_count):
        month = current_month + month_offset
        year = current_year
        if month > 12:
            month -= 12
            year += 1

        # Получаем количество дней в месяце
        _, num_days = calendar.monthrange(year, month)
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, num_days)

        # Добавляем все дни месяца в список
        current_day = month_start
        while current_day <= month_end:
            all_dates.append(current_day)
            current_day += timedelta(days=1)

    # Инициализируем структуры для отслеживания дежурств
    schedule = defaultdict(dict)
    weekend_night_schedule = defaultdict(list)
    weekly_duties = defaultdict(lambda: defaultdict(int))
    last_weekend_night_duty = defaultdict(lambda: None)
    day_duty_counts = defaultdict(int)
    night_duty_counts = defaultdict(int)
    last_duty_day = defaultdict(lambda: None)

    def get_week_key(date):
        return f"{date.year}-{date.isocalendar()[1]}"

    # Рассчитываем целевое количество дежурств на человека
    total_day_duties = len(all_dates) * day_duty_count
    total_night_duties = len(all_dates) * night_duty_count
    target_day_per_person = total_day_duties // len(people)
    target_night_per_person = total_night_duties // len(people)
    day_remainder = total_day_duties % len(people)
    night_remainder = total_night_duties % len(people)

    target_day_counts = {p: target_day_per_person + (1 if i < day_remainder else 0)
                         for i, p in enumerate(people)}
    target_night_counts = {p: target_night_per_person + (1 if i < night_remainder else 0)
                           for i, p in enumerate(people)}

    def select_duty_people(date, needed, duty_type):
        is_weekend = date.weekday() >= 5
        week_key = get_week_key(date)
        is_night = duty_type == 'night'

        available = []

        for person in people:
            # Проверяем, что человек не дежурил вчера
            if last_duty_day[person] == date - timedelta(days=1):
                continue

            # Для ночных выходных проверяем 2-недельный интервал
            if is_night and is_weekend:
                if last_weekend_night_duty[person] and (date - last_weekend_night_duty[person]).days <= 13:
                    continue

            # Не более 3 дежурств в неделю
            if weekly_duties[week_key][person] >= 3:
                continue

            # Для ночных выходных - только одно дежурство в выходные за неделю
            if is_night and is_weekend:
                week_dates = [d for d in weekend_night_schedule if get_week_key(d) == week_key]
                if any(person in weekend_night_schedule[d] for d in week_dates):
                    continue

            # Проверяем, что человек еще не достиг целевого количества дежурств
            if (duty_type == 'day' and day_duty_counts[person] >= target_day_counts[person]) or \
                    (duty_type == 'night' and night_duty_counts[person] >= target_night_counts[person]):
                continue

            available.append(person)

        # Если не хватает доступных людей, ослабляем некоторые ограничения
        if len(available) < needed:
            # Разрешаем дежурить два дня подряд, если иначе не получается
            extra = [p for p in people
                     if p not in available and
                     ((duty_type == 'day' and day_duty_counts[p] < target_day_counts[p]) or
                      (duty_type == 'night' and night_duty_counts[p] < target_night_counts[p]))]

            # Сортируем по количеству текущих дежурств (чтобы выбирать тех, у кого меньше)
            extra.sort(key=lambda x: day_duty_counts[x] if duty_type == 'day' else night_duty_counts[x])

            available.extend(extra[:needed - len(available)])

        if not available:
            return []

        # Взвешенный случайный выбор с предпочтением тем, у кого меньше дежурств
        if duty_type == 'day':
            counts = day_duty_counts
        else:
            counts = night_duty_counts

        # Создаем веса обратно пропорциональные количеству уже назначенных дежурств
        max_count = max(counts.values()) if counts.values() else 1
        weights = [(max_count - counts[p] + 1) for p in available]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        try:
            selected = np.random.choice(available, size=min(needed, len(available)),
                                        replace=False, p=weights)
        except:
            # Если веса не работают, используем простой случайный выбор
            selected = random.sample(available, min(needed, len(available)))

        return list(selected)

    # Генерируем график
    for date in all_dates:
        is_weekend = date.weekday() >= 5
        week_key = get_week_key(date)

        day_duty_people = select_duty_people(date, day_duty_count, 'day')
        night_duty_people = select_duty_people(date, night_duty_count, 'night')

        # Убедимся, что нет пересечений между дневными и ночными дежурными
        common = set(day_duty_people) & set(night_duty_people)
        while common:
            for person in common:
                # Ищем замену среди тех, кто еще не дежурит в этот день
                available = [p for p in people
                             if p not in day_duty_people and
                             p not in night_duty_people and
                             ((person in day_duty_people and day_duty_counts[p] < target_day_counts[p]) or
                              (person in night_duty_people and night_duty_counts[p] < target_night_counts[p]))]

                if available:
                    if person in day_duty_people:
                        # Выбираем замену с минимальным количеством дневных дежурств
                        replacement = min(available, key=lambda x: day_duty_counts[x])
                        day_duty_people.remove(person)
                        day_duty_people.append(replacement)
                    else:
                        # Выбираем замену с минимальным количеством ночных дежурств
                        replacement = min(available, key=lambda x: night_duty_counts[x])
                        night_duty_people.remove(person)
                        night_duty_people.append(replacement)

            common = set(day_duty_people) & set(night_duty_people)

        schedule[date]['day'] = day_duty_people
        schedule[date]['night'] = night_duty_people

        # Обновляем счетчики
        for person in day_duty_people:
            day_duty_counts[person] += 1
            weekly_duties[week_key][person] += 1
            last_duty_day[person] = date

        for person in night_duty_people:
            night_duty_counts[person] += 1
            weekly_duties[week_key][person] += 1
            last_duty_day[person] = date

            if is_weekend:
                weekend_night_schedule[date].append(person)
                last_weekend_night_duty[person] = date

    # Проверяем и корректируем распределение ночных дежурств
    total_night_assigned = sum(night_duty_counts.values())
    if total_night_assigned != total_night_duties:
        # Находим людей с наименьшим количеством дежурств
        sorted_people = sorted(people, key=lambda x: night_duty_counts[x])

        # Добавляем недостающие дежурства
        for _ in range(total_night_duties - total_night_assigned):
            person = sorted_people[0]
            night_duty_counts[person] += 1
            sorted_people.sort(key=lambda x: night_duty_counts[x])

    return schedule, day_duty_counts, night_duty_counts


def save_to_excel(schedule, day_counts, night_counts, filename="График_дежурств.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "График дежурств"

    # Настройки печати
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    # Стили
    header_font = Font(bold=True, size=12)
    night_font = Font(bold=True)
    border = Border(left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin'))

    weekdays = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}

    # Группируем даты по неделям
    weeks = {}
    for date in sorted(schedule.keys()):
        year, week_num, _ = date.isocalendar()
        week_key = f"{year}-{week_num}"
        weeks.setdefault(week_key, []).append(date)

    # Сначала определяем максимальное количество колонок
    max_columns = max(len(week_dates) for week_dates in weeks.values())

    # Главный заголовок (растягиваем только по фактическим колонкам)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_columns)
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = "График дежурств подразделения"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')

    current_row = 2  # Начинаем данные со 2 строки

    for week_num, week_dates in weeks.items():
        # Заголовок недели (растягиваем по колонкам этой недели)
        ws.merge_cells(start_row=current_row, start_column=1,
                       end_row=current_row, end_column=len(week_dates))

        week_title = ws.cell(row=current_row, column=1)
        week_title.value = f"Неделя {week_num.split('-')[1]}"
        week_title.font = Font(bold=True)
        week_title.alignment = Alignment(horizontal='center')
        current_row += 1

        # Даты
        for col_num, date in enumerate(week_dates, 1):
            cell = ws.cell(row=current_row, column=col_num)
            cell.value = f"{date.strftime('%d.%m')}\n{weekdays[date.weekday()]}"
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            ws.column_dimensions[get_column_letter(col_num)].width = 15

        # Ночные дежурные
        current_row += 1
        for col_num, date in enumerate(week_dates, 1):
            if schedule[date]['night']:
                cell = ws.cell(row=current_row, column=col_num)
                cell.value = "\n".join(schedule[date]['night'])
                cell.font = night_font
                cell.alignment = Alignment(wrap_text=True, vertical='top')
                cell.border = border

        # Дневные дежурные
        current_row += 1
        for col_num, date in enumerate(week_dates, 1):
            if schedule[date]['day']:
                cell = ws.cell(row=current_row, column=col_num)
                cell.value = "\n".join(schedule[date]['day'])
                cell.alignment = Alignment(wrap_text=True, vertical='top')
                cell.border = border

        current_row += 2  # Отступ между неделями

    # Устанавливаем область печати
    last_column = get_column_letter(max_columns)
    last_row = current_row - 1  # Последняя заполненная строка
    ws.print_area = f'A1:{last_column}{last_row}'

    # Статистика
    ws_stats = wb.create_sheet("Статистика")
    ws_stats.page_setup.orientation = ws_stats.ORIENTATION_LANDSCAPE

    wb.save(filename)
def print_statistics(day_counts, night_counts):
    print("\nСтатистика дневных дежурств:")
    for person, count in sorted(day_counts.items(), key=lambda x: x[1]):
        print(f"{person}: {count} дежурств")

    print("\nСтатистика ночных дежурств:")
    for person, count in sorted(night_counts.items(), key=lambda x: x[1]):
        print(f"{person}: {count} дежурств")

with open("lica.txt", 'r', encoding='utf-8') as file:
    people = [line.strip() for line in file if line.strip()]

day_duty_count = 4
night_duty_count = 2

schedule, day_counts, night_counts = generate_duty_schedule(people, day_duty_count, night_duty_count)
save_to_excel(schedule, day_counts, night_counts)
print_statistics(day_counts, night_counts)
print("\nГрафик дежурств сохранен в файл 'График_дежурств.xlsx'")