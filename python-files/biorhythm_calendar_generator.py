#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор PDF-календаря биоритмов.
- На вход: дата рождения и год прогноза
- Результат: PDF по месяцам (таблица-календарь + мини-график за месяц)
- Поддержка кириллицы через подключение TTF-шрифта (рекомендуется DejaVuSans или Consolas).

Пример запуска:
    python biorhythm_calendar_generator.py --birth 1997-06-16 --year 2025 \
        --font ./Consolas.ttf --outfile biorhythms_2025.pdf

Зависимости:
    pip install reportlab matplotlib pandas numpy

Примечания:
- Вставляйте шрифт с поддержкой кириллицы (TTF), иначе возможны квадраты.
- Цвета: красный — критический, зелёный — высокий, синий — низкий, чёрный — нейтральный.
"""
import math
import argparse
from datetime import date, timedelta, datetime
from calendar import monthrange
from io import BytesIO

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----- ReportLab -----
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------- Параметры биоритмов --------------------
PERIODS = {
    "Физический (23 дня)": 23,
    "Эмоциональный (28 дней)": 28,
    "Интеллектуальный (33 дня)": 33,
}

WEEKDAYS_RU = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

def biorhythm_value(birth_date: date, d: date, period: int) -> float:
    delta_days = (d - birth_date).days
    return math.sin(2 * math.pi * delta_days / period)

def compute_dataframe(birth_date: date, year: int) -> pd.DataFrame:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    days = (end - start).days + 1
    dates = [start + timedelta(days=i) for i in range(days)]
    data = {"Дата": dates}
    for name, period in PERIODS.items():
        data[name] = [biorhythm_value(birth_date, d, period) for d in dates]
    df = pd.DataFrame(data)
    return df

def classify_label_and_hex(val: float):
    """Возвращает (ярлык, HEX-цвет)."""
    if abs(val) < 0.1:
        return "кр", "#FF0000"   # критический
    elif val > 0.5:
        return "выс", "#008000"  # высокий
    elif val < -0.5:
        return "низ", "#0000FF"  # низкий
    else:
        return "нейт", "#000000" # нейтральный

def register_font(font_path: str | None) -> str:
    """
    Регистрирует шрифт и возвращает имя шрифта для использования в стилях.
    Если font_path=None, пытается подключить DejaVuSans из matplotlib, иначе fallback: Helvetica.
    """
    styles = getSampleStyleSheet()  # просто для гарантии инициализации
    font_name = "Helvetica"
    if font_path:
        pdfmetrics.registerFont(TTFont("CustomTTF", font_path))
        font_name = "CustomTTF"
    else:
        # Пытаемся найти DejaVuSans через matplotlib (чаще всего доступен локально)
        try:
            import matplotlib
            from matplotlib import font_manager
            candidates = [f for f in font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
                          if "DejaVuSans.ttf" in f or "DejaVu Sans" in f]
            if candidates:
                pdfmetrics.registerFont(TTFont("DejaVuSans", candidates[0]))
                font_name = "DejaVuSans"
        except Exception:
            pass
    return font_name

def build_pdf(birth_date: date, year: int, outfile: str, font_path: str | None,
              include_plots: bool = True):
    df = compute_dataframe(birth_date, year)
    df["Дата"] = pd.to_datetime(df["Дата"])

    font_name = register_font(font_path)

    # Стили
    styles = getSampleStyleSheet()
    style_month = ParagraphStyle("MonthTitle", parent=styles["Heading1"], fontName=font_name, alignment=1)
    style_day = ParagraphStyle("DayCell", parent=styles["Normal"], fontName=font_name, fontSize=7, leading=8)

    doc = SimpleDocTemplate(outfile, pagesize=A4)
    elements = []

    for month in range(1, 13):
        # Заголовок
        month_title = f"{MONTHS_RU[month]} {year}"
        elements.append(Paragraph(month_title, style_month))
        elements.append(Spacer(1, 6))

        # Шапка дней недели
        table_data = [[Paragraph(d, style_day) for d in WEEKDAYS_RU]]

        # Раскладка по неделям
        first_weekday, days_in_month = monthrange(year, month)  # 0=Пн, ... 6=Вс
        row = [""] * first_weekday

        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            row_df = df[df["Дата"] == pd.Timestamp(current_date)]
            if not row_df.empty:
                r = row_df.iloc[0]
                phys, color_p = classify_label_and_hex(r["Физический (23 дня)"])
                emot, color_e = classify_label_and_hex(r["Эмоциональный (28 дней)"])
                intel, color_i = classify_label_and_hex(r["Интеллектуальный (33 дня)"])

                # Короткая форма: Ф/Э/И
                txt = (
                    f"{day}<br/>"
                    f"<font color='{color_p}'>Ф:{phys}</font> "
                    f"<font color='{color_e}'>Э:{emot}</font> "
                    f"<font color='{color_i}'>И:{intel}</font>"
                )
                row.append(Paragraph(txt, style_day))
            else:
                row.append("")

            if len(row) == 7:
                table_data.append(row)
                row = []

        if row:
            while len(row) < 7:
                row.append("")
            table_data.append(row)

        # Таблица месяца
        from reportlab.lib.units import cm
        table = Table(table_data, colWidths=[2.5*cm]*7, rowHeights=1.7*cm)
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("FONTNAME", (0,0), (-1,-1), font_name),
        ]))
        elements.append(table)

        # График за месяц
        if include_plots:
            elements.append(Spacer(1, 10))
            month_df = df[(df["Дата"].dt.month == month) & (df["Дата"].dt.year == year)]
            plt.figure(figsize=(6, 2))
            # ВНИМАНИЕ: не задаём кастомных цветов — используем дефолтные
            plt.plot(month_df["Дата"], month_df["Физический (23 дня)"], label="Физический")
            plt.plot(month_df["Дата"], month_df["Эмоциональный (28 дней)"], label="Эмоциональный")
            plt.plot(month_df["Дата"], month_df["Интеллектуальный (33 дня)"], label="Интеллектуальный")
            plt.axhline(0, linewidth=0.5)
            plt.legend(fontsize=6)
            plt.xticks(rotation=45, fontsize=6)
            plt.yticks(fontsize=6)
            plt.tight_layout()

            img_buf = BytesIO()
            plt.savefig(img_buf, format="PNG")
            plt.close()
            img_buf.seek(0)
            elements.append(Image(img_buf, width=15*cm, height=5*cm))

        elements.append(PageBreak())

    doc.build(elements)

def main():
    parser = argparse.ArgumentParser(description="Генератор PDF-календаря биоритмов на год.")
    parser.add_argument("--birth", required=True, help="Дата рождения в формате YYYY-MM-DD (например, 1997-06-16).")
    parser.add_argument("--year", type=int, required=True, help="Год прогноза, например 2025.")
    parser.add_argument("--font", default=None, help="Путь к TTF-шрифту с поддержкой кириллицы (например, DejaVuSans.ttf или Consolas.ttf).")
    parser.add_argument("--outfile", default="biorhythms_calendar.pdf", help="Имя выходного PDF-файла.")
    parser.add_argument("--no-plots", action="store_true", help="Не добавлять графики за месяц.")
    args = parser.parse_args()

    try:
        birth_date = datetime.strptime(args.birth, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("Неверный формат даты рождения. Используйте YYYY-MM-DD, например: 1997-06-16.")

    build_pdf(
        birth_date=birth_date,
        year=args.year,
        outfile=args.outfile,
        font_path=args.font,
        include_plots=not args.no_plots
    )
    print(f"Готово! PDF сохранён в: {args.outfile}")

if __name__ == "__main__":
    main()
