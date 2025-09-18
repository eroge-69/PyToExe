
# -*- coding: utf-8 -*-
"""
AssortProcess — консольная версия без GUI.
Использование:
  python assort_cli_drop_v1.py "C:\path\file.xlsx" [имя_листа]
После сборки в .exe:
  1) Перетащи Excel-файл на AssortProcess.exe
  2) Или запусти из консоли: AssortProcess.exe "C:\path\file.xlsx" [лист]

Результат сохраняется рядом с исходным файлом: "Ассортимент_рекомендации.xlsx".
"""

import sys
import os
import pandas as pd
import numpy as np

# === Колонки ===
GROUP_COL           = "ГруппаТОВ"
SUBGROUP_COL        = "Подгруппа"
ID_COL              = "ID"
WRITE_OFF_PCT_COL   = "ЗЦ 40% + спис, %"
WRITE_OFF_RUB_COL   = "ЗЦ 40% + спис, руб"
SALES_QTY_COL       = "Кол-во продаж, шт"
SALES_RUB_COL       = "Продажи+ЮЛ сумма, руб"
IN_TA_COL           = "В ТА"
OUT_TA_COL          = "ИЗ ТА"
STOCKS_COL          = "Остатки"
MATRIX_COL          = "76+"
CLEAN_QTY_COL       = "Чистые продажи в штуках без ЗЦ, ТТ"

CATS_SHEET          = "Категории"
CATS_TOTAL_SALES    = "Весь период|Продажи+ЮЛ_Сумма"

# === Наборы ===
SPECIAL_CATEGORIES = {
    "Бакалея","Консервация","Напитки","Нон-Фуд","Сладости, кондитерские изделия",
    "Сухофрукты. Сушеные грибы, ягоды. Орехи","Алкоголь","Детское питание","Замороженные п/ф","Мороженое","Торты, десерты замороженные",
}
SPECIAL_SUBGROUPS = {
    "Замороженные моно овощи","Замороженные моно фрукты","Замороженные напитки и пюре","Замороженные смеси",
    "Готовые решения из рыбы и морепродуктов","Замороженная готовая рыба","Замороженная ДВ рыба","Замороженная премиальная рыба",
    "Замороженная рыба прочая","Замороженная треска","Замороженные котлеты и зразы","Замороженные креветки",
    "Замороженные медальоны","Замороженные минтай и пикша","Замороженные морепродукты прочие",
    "Замороженные ПФ в панировке","Замороженные семга и форель","Консервированная рыба",
    "Замороженное мясо и субпродукты","Мясная консервация","Баранки, сушки, сухари","Хлебцы",
}
EXCLUDED_GROUPS = {
    "Подписки на товары и услуги","Архив","Добрая полка (основная)","ВВ Праздник","Пространство ВкусВилл",
    "Напитки с собой","Мировые бренды","Микромаркет","Пекарня","ДаркКитчен","Мясная Витрина ВВ",
    "Отдел без упаковки","Индилавка","Собственное производство кафе","Рыбная витрина","Фрешбар","Детская полка",
    "ВВА_Вино","Дача Сад Огород","Чай и кофе. Проекты","Весовая кулинария","Проекты нон-фуд","Прочее, служебные товары",
    "БОРТПИТАНИЕ","Roots","Фруткорт. Готовая продукция","Проект Вкусвилл Красиво","Рационы","ДаркКитчен Сырье",
    "Интернет-магазин","В2В","ФС Общепит","Рестораны",
}
KAFE_GROUP = "Кафе"
KAFE_ALLOWED_SUBGROUPS = {
    "Батончики, снэки, пряники Кафе","Выпечка несладкая Кафе","Завтраки Кафе","Напитки в банке Кафе",
    "Основные блюда Кафе","Пирожки Кафе","Торты, десерты Кафе","Чиабатты, сэндвичи Кафе",
}
BANNED_SUBGROUP = "Десерты для праздников"

# === Утилиты ===
def to_number(x):
    if pd.isna(x): return np.nan
    try:
        s = str(x).replace(" ", "").replace(",", ".").strip()
        if s.endswith("%"): s = s[:-1]
        return float(s)
    except Exception:
        return np.nan

def to_fraction_percent(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    if "%" in s:
        try:
            v = float(s.replace("%","").replace(" ","").replace(",", "."))
            return v/100.0
        except Exception:
            pass
    v = to_number(x)
    if pd.isna(v): return np.nan
    if v > 10: return v/100.0
    return v

def parse_date(x):
    return pd.to_datetime(x, errors="coerce", dayfirst=True)

def status_from_events(v_ta, iz_ta):
    v = parse_date(v_ta); z = parse_date(iz_ta)
    if pd.isna(v) and pd.isna(z): return "none", v, z
    if pd.notna(v) and pd.notna(z): return ("in", v, z) if v >= z else ("out", v, z)
    if pd.notna(v): return "in", v, z
    return "out", v, z

# === Правила ===
def decide_other_groups(row, ctx):
    status = row["__status"]; wo = row["__wo"]; s_qty = row["__s_qty"]; s_rub = row["__s_rub"]
    cat = row[GROUP_COL]

    # п.2
    if pd.notna(wo) and (0.20 <= wo <= 0.30) and (s_rub > 2000):
        if (cat in ctx["top5_categories"]) and (wo < ctx["overall_cat_mean_wo"]):
            return ("Ввод", "п.2: 20–30% + выручка>2000, топ-5 по Категории, списания ниже среднего по всем категориям")

    # п.4 — три независимые проверки на ввод (только для НЕ в ТА)
    if pd.notna(wo) and status != "in":
        if wo <= 0.12:
            return ("Ввод", "п.4.1: списания ≤ 12%")
        if 0.12 < wo <= 0.20 and s_qty >= 10:
            return ("Ввод", "п.4.2: 12–20% и продажи ≥ 10 шт")
        if 0.12 < wo <= 0.20 and s_rub >= 1500:
            return ("Ввод", "п.4.3: 12–20% и выручка ≥ 1500")

    # Щит для обычных групп (не спецовые): если в ТА, низкие списания и есть продажи/выручка — не трогаем
    if status == "in" and pd.notna(wo) and (wo <= 0.12) and ((s_qty >= 1) or (s_rub >= 200)):
        return (None, "щит обычных: in, списания ≤ 12%, есть продажи/выручка")

    # дефолт
    return ("Вывод", "дефолт: товар в ТА, положительные условия не выполнены") if status == "in" else (None, None)

def decide_row(row, ctx):
    category = row[GROUP_COL]; subgroup = row.get(SUBGROUP_COL, None)
    status = row["__status"]; wo = row["__wo"]; s_qty = row["__s_qty"]; s_rub = row["__s_rub"]
    stocks = row["__stocks"]; in_matrix = row["__in_matrix"]

    # Сырье для сокомата — не трогаем/не вводим
    if subgroup == "Сырье для сокомата":
        return (None, "спец-правило: Сырье для сокомата — не трогаем/не вводим")

    # Запреты
    if subgroup == BANNED_SUBGROUP:
        return (None, "пропуск: запрещённая подгруппа")
    if category in EXCLUDED_GROUPS:
        return (None, "пропуск: исключённая категория")

    # п.9 — жёсткий вывод >30% если в ТА
    if pd.notna(wo) and (wo > 0.30) and status == "in":
        return ("Вывод", "п.9: списания > 30% и товар в ТА")

    # п.7 — Кафе: только если в топ-10 и в разрешённых подгруппах, дальше обычные правила
    if category == KAFE_GROUP:
        if not ctx["kafe_in_top10"]:
            return (None, "пропуск: Кафе вне топ-10 по Категории")
        if subgroup not in KAFE_ALLOWED_SUBGROUPS:
            return (None, "пропуск: подгруппа Кафе вне списка")
        return decide_other_groups(row, ctx)

    # п.3 — спецовые группы/подгруппы
    if (category in SPECIAL_CATEGORIES) or (subgroup in SPECIAL_SUBGROUPS):
        # СПЕЦ-ЩИТ 1: если товар в ТА, списания ≤ 5% и продажи ≥ 2 шт — оставляем
        if status == "in" and pd.notna(wo) and (wo <= 0.05) and (s_qty >= 2):
            return (None, "спец-щит: in, списания ≤ 5%, продажи ≥ 2 шт")
        # СПЕЦ-ЩИТ 2: если в ТА, в матрице, остатки ≥ 2 и списания ≤ 5% — оставляем
        if status == "in" and in_matrix and (pd.notna(stocks) and stocks >= 2) and pd.notna(wo) and (wo <= 0.05):
            return (None, "спец-щит: in, в матрице, остатки ≥ 2, списания ≤ 5%")

        if in_matrix and (pd.notna(stocks) and stocks >= 2) and (s_qty < 0.1) and (pd.notna(wo) and wo == 0) and status != "in":
            return ("Ввод", "п.3: спец, в матрице + остатки ≥2, 0 продаж, 0 списаний")
        if pd.notna(wo) and wo <= 0.05 and s_qty >= 0.1 and status != "in":
            return ("Ввод", "п.3: спец, списания ≤ 5% и есть продажи")
        return ("Вывод", "п.3: спец в ТА, условия ввода не выполнены") if status == "in" else (None, None)

    # Обычные группы
    return decide_other_groups(row, ctx)

def main():
    if len(sys.argv) < 2:
        print("Использование: AssortProcess.exe \"C:\\путь\\файл.xlsx\" [имя_листа]")
        sys.exit(2)

    excel_path = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) >= 3 else None

    if not os.path.isfile(excel_path):
        print("Файл не найден:", excel_path)
        sys.exit(1)

    print("[1/8] Читаю книгу:", excel_path)
    xls = pd.ExcelFile(excel_path)
    if sheet_name:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    else:
        base_sheet = "650" if "650" in xls.sheet_names else xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=base_sheet)

    print("[2/8] Беру лист Категории (если есть)...")
    categories_df = pd.read_excel(xls, sheet_name=CATS_SHEET) if (CATS_SHEET in xls.sheet_names) else pd.DataFrame(columns=[GROUP_COL, CATS_TOTAL_SALES])

    print("[3/8] Главная фильтрация по статусам...")
    if "Статус" in df.columns and "СтатусАктХар" in df.columns:
        st = df["Статус"].astype(str).str.lower()
        act = df["СтатусАктХар"].astype(str).str.lower()
        mask_status = st.str.contains("приостанов", na=False) | st.str.contains("на вывод", na=False)
        mask_act = act.str.contains("выведен", na=False)
        drop_mask = mask_status & mask_act
        if drop_mask.any():
            df = df.loc[~drop_mask].copy()

    required = [GROUP_COL, ID_COL, WRITE_OFF_PCT_COL, SALES_QTY_COL, SALES_RUB_COL, IN_TA_COL, OUT_TA_COL]
    miss = [c for c in required if c not in df.columns]
    if miss:
        print("В файле нет обязательных колонок:", ", ".join(miss))
        sys.exit(1)

    print("[4/8] Числовые поля...")
    df["__wo"]      = df[WRITE_OFF_PCT_COL].apply(to_fraction_percent)
    df["__wo_rub"]  = df[WRITE_OFF_RUB_COL].apply(to_number) if WRITE_OFF_RUB_COL in df.columns else np.inf
    df["__s_qty"]   = df[SALES_QTY_COL].apply(to_number).fillna(0.0)
    df["__s_rub"]   = df[SALES_RUB_COL].apply(to_number).fillna(0.0)
    df["__stocks"]  = df[STOCKS_COL].apply(to_number) if STOCKS_COL in df.columns else np.nan

    st_ev = df.apply(lambda r: status_from_events(r.get(IN_TA_COL), r.get(OUT_TA_COL)), axis=1)
    df["__status"]    = [t[0] for t in st_ev]
    df["В ТА (дата)"] = [t[1] for t in st_ev]
    df["ИЗ ТА (дата)"]= [t[2] for t in st_ev]

    if MATRIX_COL in df.columns:
        df["__in_matrix"] = df[MATRIX_COL].astype(str).str.strip().str.lower().eq("в матрице")
    else:
        df["__in_matrix"] = False

    print("[5/8] Средние и топы...")
    cat_means = df.groupby(GROUP_COL)["__wo"].mean()
    overall_cat_mean_wo = float(cat_means.mean()) if len(cat_means) else np.nan
    if not categories_df.empty and (GROUP_COL in categories_df.columns) and (CATS_TOTAL_SALES in categories_df.columns):
        tmp = categories_df[[GROUP_COL, CATS_TOTAL_SALES]].copy()
        tmp["__tot"] = tmp[CATS_TOTAL_SALES].apply(to_number).fillna(0.0)
        tmp = tmp.sort_values("__tot", ascending=False)
        top5_categories  = set(tmp.head(5)[GROUP_COL].astype(str))
        top10_categories = set(tmp.head(10)[GROUP_COL].astype(str))
    else:
        top5_categories, top10_categories = set(), set()

    ctx = {
        "top5_categories": top5_categories,
        "kafe_in_top10": (KAFE_GROUP in top10_categories),
        "overall_cat_mean_wo": overall_cat_mean_wo,
    }

    print("[6/8] Рекомендации по строкам...")
    df["__raw_tuple"] = df.apply(lambda r: decide_row(r, ctx), axis=1)
    df["__raw_reco"]   = df["__raw_tuple"].apply(lambda t: t[0])
    df["__reason"]     = df["__raw_tuple"].apply(lambda t: t[1])

    print("[7/8] Сглаживание...")
    if CLEAN_QTY_COL in df.columns:
        df["__clean_qty"] = df[CLEAN_QTY_COL].apply(to_number).fillna(0.0)
    else:
        df["__clean_qty"] = df["__s_qty"]

    def sort_key(df_):
        return df_.sort_values(["__clean_qty","__wo","__s_rub"], ascending=[False, True, False])

    def smooth_category(group):
        in_mask = group["__status"].eq("in")
        B_mask  = group["__raw_reco"].eq("Вывод")
        A = int(in_mask.sum())
        B = int((in_mask & B_mask).sum())
        if A == 0 or B == 0 or B / A < 0.40:
            return group

        cancel_cnt = B - (B // 2)

        keep_pool = group[in_mask & B_mask & (group["__wo"] <= 0.31) & (group["__clean_qty"] > 0)].copy()
        keep_pool = sort_key(keep_pool)
        cancel_ids = list(keep_pool.index[:cancel_cnt])
        if cancel_ids:
            group.loc[group.index.isin(cancel_ids), "__raw_reco"] = None
            for idx in cancel_ids:
                old_reason = group.at[idx, "__reason"] if "__reason" in group.columns else None
                reason = "п.11: сглаживание — отмена вывода (½ по категории); списания ≤ 31%"
                group.at[idx, "__reason"] = reason if pd.isna(old_reason) or not old_reason else old_reason

        add_pool_mask = (~in_mask & ~group["__raw_reco"].eq("Ввод") &
                         (group["__wo"] <= 0.31) & (group["__clean_qty"] > 0) &
                         (group[SUBGROUP_COL].astype(str) != "Сырье для сокомата"))
        add_pool  = group[add_pool_mask].copy()
        add_pool  = sort_key(add_pool)
        add_quota = cancel_cnt
        for idx in list(add_pool.index[:add_quota]):
            group.at[idx, "__raw_reco"] = "Ввод"
            group.at[idx, "__reason"] = "п.11: сглаживание — ввод по рейтингу; списания ≤ 31%"

        return group

    df = df.groupby(GROUP_COL, group_keys=False).apply(smooth_category)

    print("[8/8] Формирую итог...")
    df["Рекомендация"] = df["__raw_reco"]
    status_map = {"in": "В ассортименте", "out": "Выведен", "none": "Нет в ТА"}
    df["Статус ТА"] = df["__status"].map(status_map)

    def fmt_pct(x):
        v = to_fraction_percent(x)
        if pd.isna(v): return ""
        return f"{round(v*100, 1)}%"
    df["Списания, % (ТТ)"] = df[WRITE_OFF_PCT_COL].apply(fmt_pct)

    res = df[df["Рекомендация"].notna()].copy()
    rename_map = {GROUP_COL:"Категория", SUBGROUP_COL:"Подгруппа", ID_COL:"ID",
                  SALES_QTY_COL:"Продажи, шт", SALES_RUB_COL:"Продажи, руб"}
    res_out = res.rename(columns=rename_map)
    res_out["Причина"] = res["__reason"].fillna("")
    ordered_cols = [c for c in [
        "ID","Категория","Подгруппа","Рекомендация","Причина",
        "Списания, % (ТТ)","Продажи, шт","Продажи, руб",
        "Статус ТА","В ТА (дата)","ИЗ ТА (дата)"
    ] if c in res_out.columns]
    res_out = res_out[ordered_cols]

    # Итог_матрица
    def will_be_in(row):
        st = row["__status"]; reco = row["Рекомендация"]
        if st == "in":
            return False if reco == "Вывод" else True
        else:
            return True if reco == "Ввод" else False

    df["__will_be_in"] = df.apply(will_be_in, axis=1)
    df["__was_in"] = (df["__status"] == "in").astype(int)
    if MATRIX_COL in df.columns:
        df["__in_matrix_count"] = df[MATRIX_COL].astype(str).str.strip().str.lower().eq("в матрице").astype(int)
    else:
        df["__in_matrix_count"] = 0

    gb_cols = [GROUP_COL] + ([SUBGROUP_COL] if SUBGROUP_COL in df.columns else [])
    tmp = df.groupby(gb_cols).agg(
        in_matrix_76 = ("__in_matrix_count","sum"),
        was_in       = ("__was_in","sum"),
        after_reco   = ("__will_be_in","sum")
    ).reset_index()

    svod = tmp.rename(columns={
        GROUP_COL: "Категория",
        SUBGROUP_COL: "Подгруппа",
        "in_matrix_76": "В матрице (76+), шт",
        "was_in": "Было в ТА (до рекомендаций), шт",
        "after_reco": "После рекомендаций, шт"
    })

    out_path = os.path.join(os.path.dirname(os.path.abspath(excel_path)), "Ассортимент_рекомендации.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        res_out.to_excel(w, sheet_name="Рекомендации", index=False)
        svod.to_excel(w, sheet_name="Итог_матрица", index=False)

    # Короткая сводка в консоль
    total_was = int(svod["Было в ТА (до рекомендаций), шт"].sum())
    total_after = int(svod["После рекомендаций, шт"].sum())
    vc = res_out["Рекомендация"].value_counts()
    print("Готово:", out_path)
    print(f"Было в ТА: {total_was} | После: {total_after}")
    print("Разбивка:", dict(vc))

if __name__ == "__main__":
    main()
