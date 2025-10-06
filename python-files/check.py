import pandas as pd
from datetime import datetime, timedelta
from itertools import combinations

# Вспомогательные функции
def parse_amount(val):
    if pd.isna(val) or val == '':
        return 0.0
    try:
        return float(str(val).replace('\xa0', ' ').replace(' ', '').replace(',', '.'))
    except:
        return 0.0

def parse_date(val, fmt='%d.%m.%Y'):
    if pd.isna(val):
        return None
    try:
        return pd.to_datetime(val, format=fmt).date()
    except:
        return None

def get_possible_check_dates(payment_date):
    return {payment_date - timedelta(days=1), payment_date, payment_date + timedelta(days=1)}

# -------------------------------
# Загрузка данных
# -------------------------------

# 1. Кассовые чеки
checks_df = pd.read_csv('Список.TXT', sep='\t', dtype=str, encoding='utf-8-sig')
checks_df.columns = checks_df.columns.str.strip()
checks_df['Дата чека ККМ'] = checks_df['Дата чека ККМ'].apply(parse_date)
checks_df['Сумма, руб.'] = checks_df['Сумма, руб.'].apply(parse_amount)
checks_df = checks_df.dropna(subset=['Дата чека ККМ', 'Сумма, руб.']).reset_index(drop=True)

# 2. Банковская выписка (СБП)
bank_df = pd.read_excel('Рублёвая выписка.xlsx', skiprows=8)
bank_df.columns = bank_df.columns.str.strip()
bank_df = bank_df[bank_df['Назначение платежа'].astype(str).str.contains('Зачисление средств по платежу СБП', na=False)].copy()
bank_df['Дата операции'] = bank_df['Дата операции'].apply(parse_date)
bank_df['Приход'] = bank_df['Приход'].apply(parse_amount)
bank_df = bank_df.dropna(subset=['Дата операции', 'Приход']).reset_index(drop=True)

# 3. CRM
crm_df = pd.read_excel('finance.xlsx', sheet_name=0)
crm_df.columns = crm_df.columns.str.strip()
crm_df = crm_df[crm_df['Тип'] == 'Доход'].copy()
crm_df['Дата'] = crm_df['Дата'].apply(parse_date)
crm_df['Сумма'] = crm_df['Сумма'].apply(parse_amount)
crm_df = crm_df.dropna(subset=['Дата', 'Сумма']).reset_index(drop=True)

# -------------------------------
# Подготовка: группировка по дате
# -------------------------------

from collections import defaultdict

checks_by_date = defaultdict(list)
for idx, row in checks_df.iterrows():
    checks_by_date[row['Дата чека ККМ']].append({'idx': idx, 'row': row, 'used': False})

crm_by_date = defaultdict(list)
for idx, row in crm_df.iterrows():
    crm_by_date[row['Дата']].append({'idx': idx, 'row': row, 'used': False})

# -------------------------------
# Этап 1: Точные совпадения (1:1)
# -------------------------------

for date in set(checks_by_date.keys()) | set(crm_by_date.keys()):
    checks = checks_by_date[date]
    crm_list = crm_by_date[date]
    
    # Сопоставление 1:1 по сумме
    for c in crm_list:
        if c['used']:
            continue
        for ch in checks:
            if ch['used']:
                continue
            if abs(c['row']['Сумма'] - ch['row']['Сумма, руб.']) < 0.01:
                c['used'] = True
                ch['used'] = True
                break

# -------------------------------
# Этап 2: Комбинированные совпадения (N CRM → 1 чек)
# -------------------------------

for date in checks_by_date:
    checks = checks_by_date[date]
    crm_list = crm_by_date.get(date, [])
    
    # Берём только неиспользованные CRM и чеки
    unused_crm = [c for c in crm_list if not c['used']]
    unused_checks = [ch for ch in checks if not ch['used']]
    
    # Для каждого неиспользованного чека пробуем найти комбинацию CRM
    for ch in unused_checks:
        target = ch['row']['Сумма, руб.']
        crm_sums = [c['row']['Сумма'] for c in unused_crm]
        crm_objs = unused_crm
        
        n = len(crm_objs)
        found = False
        # Перебираем комбинации от 2 до n элементов
        for r in range(2, min(n + 1, 6)):  # ограничим до 5 для производительности
            for combo in combinations(range(n), r):
                s = sum(crm_sums[i] for i in combo)
                if abs(s - target) < 0.01:
                    # Помечаем как использованные
                    ch['used'] = True
                    for i in combo:
                        crm_objs[i]['used'] = True
                    found = True
                    break
            if found:
                break

# -------------------------------
# Сбор несопоставленных записей
# -------------------------------

mismatches_crm_no_check = []
mismatches_check_no_crm = []

for date, crm_list in crm_by_date.items():
    for c in crm_list:
        if not c['used']:
            mismatches_crm_no_check.append(c['row'])

for date, checks in checks_by_date.items():
    for ch in checks:
        if not ch['used']:
            mismatches_check_no_crm.append(ch['row'])

# Сортировка по дате
mismatches_crm_no_check.sort(key=lambda x: x['Дата'])
mismatches_check_no_crm.sort(key=lambda x: x['Дата чека ККМ'])

# -------------------------------
# Сверка СБП ↔ Чеки (±1 день)
# -------------------------------

# Индекс чеков по сумме → множество дат
checks_by_sum = defaultdict(set)
for _, row in checks_df.iterrows():
    s = round(row['Сумма, руб.'], 2)
    d = row['Дата чека ККМ']
    checks_by_sum[s].add(d)

mismatches_sbp_no_check = []

for _, bank_row in bank_df.iterrows():
    bank_date = bank_row['Дата операции']
    bank_sum = round(bank_row['Приход'], 2)
    possible_dates = get_possible_check_dates(bank_date)
    found = False
    if bank_sum in checks_by_sum:
        for d in possible_dates:
            if d in checks_by_sum[bank_sum]:
                found = True
                break
    if not found:
        mismatches_sbp_no_check.append(bank_row)

# -------------------------------
# Вывод результатов
# -------------------------------

output_lines = []

def add_section(title, data, cols):
    output_lines.append(f"\n{'='*60}\n{title}\n{'='*60}")
    if not data:
        output_lines.append("✅ Нет несоответствий.")
    else:
        df = pd.DataFrame(data)
        output_lines.append(df[cols].to_string(index=False))

add_section(
    "CRM-платежи без соответствующего кассового чека",
    mismatches_crm_no_check,
    ['Дата', 'Сумма', 'Комментарий', 'Ученик']
)

add_section(
    "Кассовые чеки без соответствующего CRM-платежа",
    mismatches_check_no_crm,
    ['Дата чека ККМ', 'Сумма, руб.', 'Кассир', 'Номер чека ККМ']
)

add_section(
    "СБП-платежи без кассового чека (в пределах ±1 дня)",
    mismatches_sbp_no_check,
    ['Дата операции', 'Приход', 'Назначение платежа']
)

with open('результат_сверки.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("✅ Сверка завершена. Результат сохранён в файл 'результат_сверки.txt'")
