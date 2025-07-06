import pandas as pd
import re
import os

def extract_parking(value):
    if not isinstance(value, str):
        value = str(value)
    for part in re.findall(r'\d+', value):
        if int(part) > 1000:
            return int(part)
    return None

def is_kgt(value):
    return isinstance(value, str) and ("СЦ Ростов2 КГТ" in value or "СЦ Ростов2 КС5" in value)

def format_date(d):
    try:
        return pd.to_datetime(d).strftime("%d.%m")
    except:
        return "??.??"

def main():
    input_file = input("Перетащи сюда Excel-файл и нажми Enter: ").strip('"')
    if not os.path.exists(input_file):
        print("Файл не найден.")
        return

    df = pd.read_excel(input_file)
    df = df.drop_duplicates(subset=df.columns[0], keep='first')

    col_gofra = df.columns[0]
    col_name = df.columns[4]
    col_parking = df.columns[8]
    col_check = df.columns[9]
    col_date = df.columns[-2]

    grouped = {}
    for _, row in df.iterrows():
        parking = extract_parking(row[col_parking])
        if not parking:
            continue

        gofra = str(row[col_gofra]).strip()
        name = str(row[col_name]).strip()
        date = format_date(row[col_date])
        kind = "КГТ" if is_kgt(row[col_check]) else "короб"

        entry = f"{gofra} {name} {date} КГТ" if kind == "КГТ" else f"{gofra} короб {date}"
        grouped.setdefault(parking, []).append(entry)

    output_path = os.path.join(os.path.dirname(input_file), "результат.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        for parking in sorted(grouped):
            f.write(f"\n🅿️ Парковка {parking}\n")
            for line in grouped[parking]:
                f.write(f"   • {line}\n")

    print(f"\n✅ Готово! Результат сохранён в:\n{output_path}")

if __name__ == "__main__":
    main()
