#!/usr/bin/env python3
"""
Gold Master – Retro Console Edition (single-file, .DAT storage)
================================================================

Goals
-----
• Faithful DOS-style menus and labels
• Uses plain `.DAT` text files (CSV-like), no database, no 3rd‑party packages
• Packable into a single Windows .exe with PyInstaller

Files written in the same folder as the EXE/py:
  RATE.DAT         # rates history (date, price/g, test_fee, refine_fee/g, less/g, less/tola, notes)
  REFINING.DAT     # refining jobs log
  ROLL.DAT         # daily Sales & Purchase entries
  TELINDEX.DAT     # telephone index

Run (Python):  python gold_master_retro.py
Build EXE:     pyinstaller --onefile --console gold_master_retro.py

"""
from __future__ import annotations

import os
import sys
from decimal import Decimal, getcontext, ROUND_HALF_UP
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Tuple, List

# High precision money/weights
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

# ---- Constants (units) ----
G_PER_TOLA = Decimal("11.6638038")
ANA_PER_TOLA = Decimal(16)
RATTI_PER_ANA = Decimal(6)        # 96 ratti / tola
RATTI_PER_TOLA = ANA_PER_TOLA * RATTI_PER_ANA
G_PER_RATTI = (G_PER_TOLA / RATTI_PER_TOLA)
CARAT_FULL = Decimal(24)
THOUSAND = Decimal(1000)
HUNDRED = Decimal(100)

# ---- Data paths ----
RATE_PATH = "RATE.DAT"
REFINING_PATH = "REFINING.DAT"
ROLL_PATH = "ROLL.DAT"
TEL_PATH = "TELINDEX.DAT"

# ---- Helpers ----
def d(x) -> Decimal:
    return Decimal(str(x))

def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places))


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "Press ENTER to continue..."):
    try:
        input("\n" + msg)
    except EOFError:
        pass


def box(title: str):
    print("\n" + "="*72)
    print(title)
    print("="*72)


def prompt_decimal(label: str, default: Optional[Decimal] = None) -> Decimal:
    while True:
        raw = input(f"{label}{' ['+str(default)+']' if default is not None else ''}: ").strip()
        if not raw and default is not None:
            return Decimal(default)
        try:
            return Decimal(raw)
        except Exception:
            print("  >> Invalid number, try again.")


def prompt_date(label: str, default_today: bool = True) -> date:
    raw = input(f"{label} (YYYY-MM-DD){' [today]' if default_today else ''}: ").strip()
    if not raw and default_today:
        return date.today()
    return date.fromisoformat(raw)


# -------------------- Calculations --------------------

def carat_to_ppt(k: Decimal) -> Decimal:
    return q(Decimal(k) / CARAT_FULL * THOUSAND, "0.01")

def ppt_to_carat(ppt: Decimal) -> Decimal:
    return q(Decimal(ppt) / THOUSAND * CARAT_FULL, "0.01")


def assay_fraction(carat: Optional[Decimal], ppt: Optional[Decimal]) -> Decimal:
    if carat is not None:
        return Decimal(carat) / CARAT_FULL
    if ppt is not None:
        return Decimal(ppt) / THOUSAND
    raise ValueError("Assay not provided")


def grams_to_tola_ana_ratti_decompose(g: Decimal) -> Tuple[int, int, Decimal]:
    t_int = int((g / G_PER_TOLA).to_integral_value(rounding=ROUND_HALF_UP))
    rem = g - (Decimal(t_int) * G_PER_TOLA)
    ana_dec = (rem / G_PER_TOLA) * ANA_PER_TOLA
    a_int = int(ana_dec.to_integral_value(rounding=ROUND_HALF_UP))
    if a_int > 15:
        a_int = 15
    rem2 = rem - (Decimal(a_int) / ANA_PER_TOLA) * G_PER_TOLA
    r = q((rem2 / G_PER_RATTI), "0.01")
    return t_int, a_int, r


def tola_ana_ratti_to_grams(tola: Decimal=Decimal(0), ana: Decimal=Decimal(0), ratti: Decimal=Decimal(0)) -> Decimal:
    g = tola * G_PER_TOLA
    g += (ana / ANA_PER_TOLA) * G_PER_TOLA
    g += ratti * G_PER_RATTI
    return q(g, "0.0001")


def compute_refining_outcomes(
    weight_in_gram: Decimal,
    assay_carat: Optional[Decimal],
    assay_ppt: Optional[Decimal],
    tested_weight_gram: Decimal,
    sample_return_pct: Decimal,
    price_per_gram: Decimal,
    test_fee: Decimal,
    refining_fee_per_gram: Decimal,
    less_per_gram: Decimal = Decimal(0),
    less_per_tola: Decimal = Decimal(0),
) -> dict:
    w = Decimal(weight_in_gram)
    tested_w = Decimal(tested_weight_gram)
    sample_pct = Decimal(sample_return_pct)

    f = assay_fraction(assay_carat, assay_ppt)

    pure_gold = q(w * f, "0.0001")
    impurity = q(w - pure_gold, "0.0001")
    sample_return = q(tested_w * sample_pct / HUNDRED, "0.0001")

    refining_charge = q(w * Decimal(refining_fee_per_gram), "0.01")
    less_g_charge = q(w * Decimal(less_per_gram), "0.01") if less_per_gram else Decimal(0)
    less_tola_charge = q((w / G_PER_TOLA) * Decimal(less_per_tola), "0.01") if less_per_tola else Decimal(0)
    total_charges = q(Decimal(test_fee) + refining_charge + less_g_charge + less_tola_charge, "0.01")

    price_of_sample = q(sample_return * Decimal(price_per_gram) * f, "0.01")

    return {
        "assay_fraction": q(f, "0.0001"),
        "pure_gold_gram": pure_gold,
        "impurity_gram": impurity,
        "sample_return_gram": sample_return,
        "charges_total": total_charges,
        "price_of_sample": price_of_sample,
    }


def settle_transaction(pure_gold_gram: Decimal, price_per_gram: Decimal,
                        total_charges: Decimal, price_of_sample: Decimal,
                        payment_cash: Decimal, payment_gold_gram: Decimal) -> Tuple[Decimal, Decimal]:
    value_pure = Decimal(pure_gold_gram) * Decimal(price_per_gram)
    payments_value = Decimal(payment_cash) + (Decimal(payment_gold_gram) * Decimal(price_per_gram))
    net_value = q(value_pure - Decimal(total_charges) + Decimal(price_of_sample) - payments_value, "0.01")
    if net_value >= 0:
        net_gold_to_give = q(net_value / Decimal(price_per_gram), "0.0001") if price_per_gram else Decimal(0)
        return net_gold_to_give, Decimal(0)
    else:
        return Decimal(0), abs(net_value)


# -------------------- .DAT storage (CSV-like) --------------------
# We use simple pipe-delimited lines for human-readable files.
# Avoid commas to reduce locale pains.

def _ensure_file(path: str, header: Optional[str] = None):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            if header:
                f.write("# " + header + "\n")

# RATE.DAT: date|price_per_g|test_fee|refine_fee_g|less_g|less_tola|notes

def rate_add(rate_date: date, price_per_g: Decimal, test_fee: Decimal, refine_fee_g: Decimal, less_g: Decimal, less_tola: Decimal, notes: str=""):
    _ensure_file(RATE_PATH, "rate_date|price_per_g|test_fee|refine_fee_g|less_g|less_tola|notes")
    line = f"{rate_date.isoformat()}|{price_per_g}|{test_fee}|{refine_fee_g}|{less_g}|{less_tola}|{notes}\n"
    with open(RATE_PATH, "a", encoding="utf-8", newline="") as f:
        f.write(line)


def rate_list() -> List[str]:
    if not os.path.exists(RATE_PATH):
        return []
    with open(RATE_PATH, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def rate_get_for(day: date):
    rows = rate_list()
    # pick exact date if exists else last one
    exact = None
    for ln in rows:
        parts = ln.split("|")
        if parts and parts[0] == day.isoformat():
            exact = parts; break
    if not exact and rows:
        exact = rows[-1].split("|")
    if not exact:
        return None
    price, testf, refg, lg, lt, notes = exact[1], exact[2], exact[3], exact[4], exact[5], (exact[6] if len(exact) > 6 else "")
    return (Decimal(price), Decimal(testf), Decimal(refg), Decimal(lg), Decimal(lt), notes)

# REFINING.DAT: job_date|customer|weight_g|assay_carat|assay_ppt|tested_w|sample_%|pure_g|imp_g|charges|price_sample|pay_cash|pay_gold_g|net_gold_give|net_cash_due

def refining_save(**kw):
    _ensure_file(REFINING_PATH, "job_date|customer|weight_g|assay_carat|assay_ppt|tested_w|sample_%|pure_g|imp_g|charges|price_sample|pay_cash|pay_gold_g|net_gold_give|net_cash_due")
    fields = [
        kw.get("job_date"), kw.get("customer"), kw.get("weight_g"), kw.get("assay_carat"), kw.get("assay_ppt"),
        kw.get("tested_w"), kw.get("sample_pct"), kw.get("pure_g"), kw.get("imp_g"), kw.get("charges"),
        kw.get("price_sample"), kw.get("pay_cash"), kw.get("pay_gold_g"), kw.get("net_gold_give"), kw.get("net_cash_due"),
    ]
    line = "|".join(str(x) if x is not None else "" for x in fields) + "\n"
    with open(REFINING_PATH, "a", encoding="utf-8", newline="") as f:
        f.write(line)

# TELINDEX.DAT: id|name|phone

def tel_add(name: str, phone: str=""):
    _ensure_file(TEL_PATH, "id|name|phone")
    nxt = 1
    if os.path.exists(TEL_PATH):
        with open(TEL_PATH, "r", encoding="utf-8") as f:
            for ln in f:
                if ln.startswith("#") or not ln.strip():
                    continue
                parts = ln.strip().split("|")
                if parts and parts[0].isdigit():
                    nxt = max(nxt, int(parts[0]) + 1)
    with open(TEL_PATH, "a", encoding="utf-8", newline="") as f:
        f.write(f"{nxt}|{name}|{phone}\n")


def tel_list():
    if not os.path.exists(TEL_PATH):
        return []
    out = []
    with open(TEL_PATH, "r", encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            out.append(ln.strip().split("|"))
    return out


def tel_search(q: str):
    ql = q.lower()
    return [rec for rec in tel_list() if ql in rec[1].lower()]


def tel_delete(id_str: str):
    rows = tel_list()
    kept = [r for r in rows if r[0] != id_str]
    with open(TEL_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("# id|name|phone\n")
        for r in kept:
            f.write("|".join(r) + "\n")

# ROLL.DAT: date|c.no|name|cash_paid|gold_paid_g|rec_impure_g|notes

def roll_add(entry_date: date, cno: int, name: str, cash_paid: Decimal, gold_paid_g: Decimal, rec_impure_g: Decimal, notes: str=""):
    _ensure_file(ROLL_PATH, "date|c.no|name|cash_paid|gold_paid_g|rec_impure_g|notes")
    line = f"{entry_date.isoformat()}|{cno}|{name}|{cash_paid}|{gold_paid_g}|{rec_impure_g}|{notes}\n"
    with open(ROLL_PATH, "a", encoding="utf-8", newline="") as f:
        f.write(line)


def roll_list_for(day: date):
    if not os.path.exists(ROLL_PATH):
        return []
    out = []
    with open(ROLL_PATH, "r", encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            parts = ln.strip().split("|")
            if parts and parts[0] == day.isoformat():
                out.append(parts)
    return out


# -------------------- Flows (Retro screens) --------------------

def flow_rates():
    while True:
        clear(); box("CURRENT RATES")
        print("1. SET / UPDATE RATE")
        print("2. VIEW RATES")
        print("B. BACK")
        ch = input("Select: ").strip().lower()
        if ch == "1":
            try:
                d = prompt_date("DATE")
                price = prompt_decimal("GOLD RATE / GRAM")
                test_fee = prompt_decimal("TEST FEE", Decimal(0))
                ref_fee = prompt_decimal("REFINING CHARGES / GRAM", Decimal(0))
                less_g = prompt_decimal("Less / Gram", Decimal(0))
                less_tola = prompt_decimal("Less / Tola", Decimal(0))
                notes = input("Notes: ")
                rate_add(d, price, test_fee, ref_fee, less_g, less_tola, notes)
                print("Saved.")
            except Exception as e:
                print("Error:", e)
            pause()
        elif ch == "2":
            clear(); box("RATES LIST")
            rows = rate_list()
            if not rows:
                print("No rates yet.")
            else:
                print(f"{'DATE':<12} {'/g':>10} {'TEST':>8} {'REF/g':>8} {'LESS/g':>8} {'LESS/T':>8}  NOTES")
                for ln in rows:
                    p = ln.split("|")
                    print(f"{p[0]:<12} {p[1]:>10} {p[2]:>8} {p[3]:>8} {p[4]:>8} {p[5]:>8}  {p[6] if len(p)>6 else ''}")
            pause()
        elif ch == "b":
            return


def _prompt_assay() -> Tuple[Optional[Decimal], Optional[Decimal]]:
    mode = input("Assay input: (1) Carat  (2) Parts/Thousand (ppt): ").strip()
    if mode == '2':
        ppt = prompt_decimal("Assay (ppt, e.g. 916 for 22k)")
        return None, ppt
    else:
        carat = prompt_decimal("Assay (carat, 0-24)")
        return carat, None


def flow_refining():
    clear(); box("GOLD MASTER REFINING SYSTEM")
    try:
        d = prompt_date("DATE")
        customer = input("Name => ").strip()
        w = prompt_decimal("Total Weight     =>  (grams)")
        rate = rate_get_for(d)
        if not rate:
            print("No rates found. Set rates first."); pause(); return
        price_per_g, test_fee, ref_fee_g, less_g, less_t, _ = rate

        carat_in, ppt_in = _prompt_assay()
        tested_w = prompt_decimal("WEIGHT FOR TEST  =>  (g)", Decimal(0))
        sample_pct = prompt_decimal("SAMPLE WT RETURN =>   %", Decimal(0))

        calc = compute_refining_outcomes(
            weight_in_gram=w,
            assay_carat=carat_in,
            assay_ppt=ppt_in,
            tested_weight_gram=tested_w,
            sample_return_pct=sample_pct,
            price_per_gram=price_per_g,
            test_fee=test_fee,
            refining_fee_per_gram=ref_fee_g,
            less_per_gram=less_g,
            less_per_tola=less_t,
        )

        print("\nQUALITY / PRICE / PERCENTAGE ANALYSIS")
        print(f"  Percentage Analysis  => {calc['assay_fraction']}")
        print(f"  Total impurity   => {calc['impurity_gram']} g")
        print(f"  Net Weight       => {calc['pure_gold_gram']} g (Pure)")
        print(f"  Price Analysis")
        print(f"  Price of Sample  => {calc['price_of_sample']}")
        print(f"  TOTAL CHARGES    => {calc['charges_total']}")

        pay_cash = prompt_decimal("Payment  => (cash)", Decimal(0))
        pay_gold = prompt_decimal("Payment for Gold  => (g)", Decimal(0))

        net_gold_give, net_cash_due = settle_transaction(
            pure_gold_gram=calc['pure_gold_gram'],
            price_per_gram=price_per_g,
            total_charges=calc['charges_total'],
            price_of_sample=calc['price_of_sample'],
            payment_cash=pay_cash,
            payment_gold_gram=pay_gold,
        )

        print("\nSETTLEMENT")
        print(f"  Pure Gold Given => {net_gold_give} g")
        print(f"  Cash Due        => {net_cash_due}")

        if input("Save this job (Y/N)? ").strip().lower() == 'y':
            refining_save(
                job_date=d.isoformat(), customer=customer, weight_g=w,
                assay_carat=carat_in, assay_ppt=ppt_in,
                tested_w=tested_w, sample_pct=sample_pct,
                pure_g=calc['pure_gold_gram'], imp_g=calc['impurity_gram'],
                charges=calc['charges_total'], price_sample=calc['price_of_sample'],
                pay_cash=pay_cash, pay_gold_g=pay_gold,
                net_gold_give=net_gold_give, net_cash_due=net_cash_due,
            )
            print("Saved.")
    except Exception as e:
        print("Error:", e)
    pause()


def flow_quick_scan():
    clear(); box("GOLD MASTER QUICK SCAN")
    if not rate_get_for(date.today()):
        print("No rates set. Use TODAY'S FRESH RATE first."); pause(); return
    try:
        w = prompt_decimal("Total Weight (g)")
        carat_in, ppt_in = _prompt_assay()
        tested_w = prompt_decimal("WEIGHT FOR TEST (g)", Decimal(0))
        sample_pct = prompt_decimal("SAMPLE WT RETURN %", Decimal(0))
        price_per_g, test_fee, ref_fee_g, less_g, less_t, _ = rate_get_for(date.today())
        calc = compute_refining_outcomes(w, carat_in, ppt_in, tested_w, sample_pct, price_per_g, test_fee, ref_fee_g, less_g, less_t)
        for k, v in calc.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print("Error:", e)
    pause()


def flow_mixing_master():
    clear(); box("MIXING MASTER")
    w = prompt_decimal("GOLD WEIGHT => (g)")
    k_in = prompt_decimal("GOLD CARAT  =>")
    k_target = prompt_decimal("CARATS TO MAKE =>")
    print("DEFAULT COPPER = 75% & SILVER = 25%.")
    cu_pct = prompt_decimal("COPPER RATIO => %", Decimal(75)) / HUNDRED
    ag_pct = prompt_decimal("SILVER RATIO => %", Decimal(25)) / HUNDRED

    gold_mass = q(w * (k_in / CARAT_FULL), "0.0001")
    desired_total = q(gold_mass / (k_target / CARAT_FULL), "0.0001")
    alloy_to_add = q(desired_total - w, "0.0001")
    if alloy_to_add < 0:
        print("Target higher than input carat — refining required (cannot add negative alloy).")
        pause(); return
    total_ratio = cu_pct + ag_pct
    if total_ratio == 0:
        print("Copper/Silver cannot both be zero."); pause(); return
    copper = q(alloy_to_add * (cu_pct / total_ratio), "0.0001")
    silver = q(alloy_to_add * (ag_pct / total_ratio), "0.0001")

    print("\nResult:")
    print(f"  PURE GOLD          => {gold_mass} g")
    print(f"  ALLOY TO ADD       => {alloy_to_add} g  (Cu {copper} g, Ag {silver} g)")
    print(f"  TOTAL WEIGHT       => {desired_total} g")
    pause()


def flow_calculator():
    while True:
        clear(); box("CALCULATOR")
        print("1) GRAMS  => TOLA / ANA / RATTI")
        print("2) T/A/R  => GRAMS")
        print("3) CARAT  <=>  PPT")
        print("B) BACK")
        ch = input("Select: ").strip().lower()
        if ch == '1':
            g = prompt_decimal("Enter grams")
            t, a, r = grams_to_tola_ana_ratti_decompose(g)
            print(f"Tola: {t}   Ana: {a}   Ratti: {r}")
            pause()
        elif ch == '2':
            t = prompt_decimal("Tola", Decimal(0))
            a = prompt_decimal("Ana", Decimal(0))
            r = prompt_decimal("Ratti", Decimal(0))
            g = tola_ana_ratti_to_grams(t, a, r)
            print(f"Total grams: {g}")
            pause()
        elif ch == '3':
            sub = input("(1) carat→ppt  (2) ppt→carat: ").strip()
            if sub == '1':
                k = prompt_decimal("Carat (0-24)")
                print(f"{k}k ≈ {carat_to_ppt(k)} ppt")
            else:
                p = prompt_decimal("Parts per thousand")
                print(f"{p} ppt ≈ {ppt_to_carat(p)}k")
            pause()
        elif ch == 'b':
            return


def flow_tel():
    while True:
        clear(); box("TELEPHONE INDEX")
        print("1) DATA ENTRY")
        print("2) VIEW RECORDS")
        print("3) SEARCH")
        print("4) DELETE")
        print("5) MAIN MENU")
        ch = input("Select: ").strip()
        if ch == '1':
            name = input("Name: ").strip()
            phone = input("Phone No: ").strip()
            if name:
                tel_add(name, phone)
                print("Saved.")
            pause()
        elif ch == '2':
            rows = tel_list()
            if not rows:
                print("No records.")
            else:
                print(f"{'ID':>4}  {'NAME':<28} PHONE")
                for r in rows:
                    print(f"{r[0]:>4}  {r[1]:<28} {r[2]}")
            pause()
        elif ch == '3':
            q = input("ENTER A NAME TO SEARCH => ")
            res = tel_search(q)
            if not res:
                print("Record not found.")
            else:
                for r in res:
                    print(f"{r[0]:>4}  {r[1]}  {r[2]}")
            pause()
        elif ch == '4':
            did = input("ID to delete: ").strip()
            tel_delete(did)
            print("Deleted (if existed).")
            pause()
        else:
            return


def flow_roll():
    while True:
        clear(); box("TODAY'S SALES & PURCHASE")
        print("1) ADD ENTRY")
        print("2) VIEW RECORDS FOR DATE")
        print("B) BACK")
        ch = input("Select: ").strip().lower()
        if ch == '1':
            try:
                d = prompt_date("DATE")
                cno_raw = input("C.NO => ").strip()
                cno = int(cno_raw) if cno_raw.isdigit() else 0
                name = input("NAME => ").strip()
                cash = prompt_decimal("CASH PAID", Decimal(0))
                gold_paid = prompt_decimal("GOLD PAID (g)", Decimal(0))
                rec_imp = prompt_decimal("REC. IMPURE (g)", Decimal(0))
                notes = input("Notes: ")
                roll_add(d, cno, name, cash, gold_paid, rec_imp, notes)
                print("Saved.")
            except Exception as e:
                print("Error:", e)
            pause()
        elif ch == '2':
            try:
                d = prompt_date("DATE")
                rows = roll_list_for(d)
                if not rows:
                    print("No entries.")
                else:
                    tot_cash = Decimal(0); tot_gold = Decimal(0); tot_imp = Decimal(0)
                    print(f"DATE {d.isoformat()}\n")
                    print(f"{'C.NO':>6} {'NAME':<22} {'CASH':>12} {'GOLD(g)':>10} {'REC.IMP(g)':>12}  NOTES")
                    for p in rows:
                        cno, name, cash, goldg, impg, notes = p[1], p[2], Decimal(p[3]), Decimal(p[4]), Decimal(p[5]), (p[6] if len(p)>6 else "")
                        tot_cash += cash; tot_gold += goldg; tot_imp += impg
                        print(f"{cno:>6} {name:<22} {cash:>12} {goldg:>10} {impg:>12}  {notes}")
                    print("-"*70)
                    print(f"TOTALS: CASH={tot_cash}  GOLD(g)={tot_gold}  REC.IMP(g)={tot_imp}")
            except Exception as e:
                print("Error:", e)
            pause()
        elif ch == 'b':
            return


# -------------------- Main Menu --------------------

def main_menu():
    while True:
        clear(); box("MAIN MENU")
        print("1. GOLD MASTER REFINING SYSTEM")
        print("2. GOLD MASTER QUICK SCAN")
        print("3. OLD GOLD MASTER SYSTEM  (n / a)")
        print("4. TODAYS FRESH RATE")
        print("5. MIXING MASTER")
        print("6. CALCULATOR")
        print("7. TELEPHONE INDEX")
        print("8. TODAYS SALES & PURCHASE")
        print("F10. EXIT")
        ch = input("Select: ").strip().upper()
        if ch == '1':
            flow_refining()
        elif ch == '2':
            flow_quick_scan()
        elif ch == '3':
            print("(n/a)"); pause()
        elif ch == '4':
            flow_rates()
        elif ch == '5':
            flow_mixing_master()
        elif ch == '6':
            flow_calculator()
        elif ch == '7':
            flow_tel()
        elif ch == '8':
            flow_roll()
        elif ch in ('F10', 'Q', 'QUIT', 'EXIT'):
            print("Goodbye!")
            break
        else:
            print("Invalid option."); pause()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n*Break*")
