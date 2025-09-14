#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jordan Unlawful Termination Calculator
--------------------------------------
Calculates compensation components under Jordanian Labour Law.

References (key rules used):
- Notice period: 1 month for unlimited contracts. (Labour Law; Better Work Guide)
- Arbitrary/Unfair dismissal compensation: 0.5 month's wage per year of service,
  with a minimum of 2 months' wages; plus notice pay and other entitlements. 
  (Better Work Labour Law Guide, p. 23)
- Overtime: 125% of normal hourly wage for regular overtime; 150% for weekly rest
  day (Friday) and official/religious holidays. (Better Work Labour Law Guide, p. 28)
- Annual leave: at least 14 days/year, rising to 21 days after 5 years; unused leave
  is paid at termination. (Better Work Labour Law Guide, p. 29)
- End-of-service gratuity (EOS): For workers NOT covered by Social Security, 1 month
  wage for every year of service, pro rata. (Better Work Labour Law Guide, p. 25)

This script works in two modes:
1) Interactive console prompts.
2) Non-interactive via CLI flags and optional export to CSV/XLSX.

Example:
    python jordan_unlawful_termination_calculator.py
    python jordan_unlawful_termination_calculator.py --monthly-wage 800 --years 3 --months 6 \
        --unused-leave-days 10 --missed-wage-months 2 --regular-ot-hours 12 --holiday-ot-hours 8 \
        --no-notice --contract unlimited --covered-by-ssc --export results.xlsx

Author: The Monarch
"""
import argparse
from dataclasses import dataclass, asdict
from typing import Dict, Tuple
from datetime import datetime

# Defaults commonly used in Jordan
DEFAULT_WORKING_HOURS_PER_WEEK = 48
DEFAULT_WEEKS_PER_MONTH = 52/12  # ~4.3333
DEFAULT_MONTHLY_HOURS = DEFAULT_WORKING_HOURS_PER_WEEK * DEFAULT_WEEKS_PER_MONTH  # ≈ 208
DEFAULT_DAYS_IN_MONTH_FOR_DAILY_RATE = 30  # Common payroll convention

@dataclass
class Inputs:
    monthly_wage: float
    years_of_service: int
    months_of_service: int
    contract_type: str  # 'unlimited' or 'fixed'
    notice_given: bool
    unused_leave_days: float
    missed_wage_months: float
    regular_ot_hours: float
    holiday_ot_hours: float  # Fridays + public/religious holidays
    monthly_hours: float = DEFAULT_MONTHLY_HOURS
    daily_divisor: float = DEFAULT_DAYS_IN_MONTH_FOR_DAILY_RATE
    covered_by_social_security: bool = True  # If False, EOS gratuity applies
    fixed_contract_months_remaining: float = 0.0  # Only for fixed-term early termination

@dataclass
class Results:
    hourly_rate: float
    daily_rate: float
    notice_pay: float
    arbitrary_dismissal_comp: float
    eos_gratuity: float
    unused_leave_comp: float
    unpaid_wages: float
    overtime_regular: float
    overtime_holiday: float
    fixed_term_remaining_comp: float
    subtotal_entitlements: float
    total_due: float
    generated_at: str

def compute_rates(inp: Inputs) -> Tuple[float, float]:
    hourly = inp.monthly_wage / inp.monthly_hours
    daily = inp.monthly_wage / inp.daily_divisor
    return hourly, daily

def compute_notice_pay(inp: Inputs) -> float:
    # One month wage if notice not given for unlimited contracts.
    if inp.contract_type.lower() == 'unlimited' and not inp.notice_given:
        return inp.monthly_wage
    return 0.0

def compute_arbitrary_comp(inp: Inputs) -> float:
    # Applies typically to unfair dismissal cases found by the court (unlimited contracts).
    # 0.5 month wage per year of service (pro rata), min 2 months. Based on last wage.
    if inp.contract_type.lower() != 'unlimited':
        return 0.0
    total_years = inp.years_of_service + inp.months_of_service / 12.0
    comp = 0.5 * total_years * inp.monthly_wage
    return max(comp, 2 * inp.monthly_wage) if total_years > 0 else 2 * inp.monthly_wage

def compute_eos_gratuity(inp: Inputs) -> float:
    # Only if NOT covered by Social Security (per law). 1 month wage per year (pro rata).
    if inp.covered_by_social_security:
        return 0.0
    total_years = inp.years_of_service + inp.months_of_service / 12.0
    return total_years * inp.monthly_wage

def compute_unused_leave(inp: Inputs, daily_rate: float) -> float:
    return inp.unused_leave_days * daily_rate

def compute_unpaid_wages(inp: Inputs) -> float:
    return inp.missed_wage_months * inp.monthly_wage

def compute_overtime(inp: Inputs, hourly_rate: float) -> Tuple[float, float]:
    ot_regular = inp.regular_ot_hours * hourly_rate * 1.25
    ot_holiday = inp.holiday_ot_hours * hourly_rate * 1.50
    return ot_regular, ot_holiday

def compute_fixed_term_remaining(inp: Inputs) -> float:
    # If a fixed-term contract is terminated early by employer, generally employee is owed
    # wages for the remaining term. Here we compute remaining months * monthly wage if provided.
    if inp.contract_type.lower() == 'fixed' and inp.fixed_contract_months_remaining > 0:
        return inp.fixed_contract_months_remaining * inp.monthly_wage
    return 0.0

def calculate_all(inp: Inputs) -> Results:
    hourly_rate, daily_rate = compute_rates(inp)
    notice_pay = compute_notice_pay(inp)
    arbitrary_comp = compute_arbitrary_comp(inp)
    eos_gratuity = compute_eos_gratuity(inp)
    unused_leave = compute_unused_leave(inp, daily_rate)
    unpaid = compute_unpaid_wages(inp)
    ot_regular, ot_holiday = compute_overtime(inp, hourly_rate)
    fixed_term_comp = compute_fixed_term_remaining(inp)

    subtotal = (notice_pay + arbitrary_comp + eos_gratuity +
                unused_leave + unpaid + ot_regular + ot_holiday + fixed_term_comp)
    return Results(
        hourly_rate=hourly_rate,
        daily_rate=daily_rate,
        notice_pay=notice_pay,
        arbitrary_dismissal_comp=arbitrary_comp,
        eos_gratuity=eos_gratuity,
        unused_leave_comp=unused_leave,
        unpaid_wages=unpaid,
        overtime_regular=ot_regular,
        overtime_holiday=ot_holiday,
        fixed_term_remaining_comp=fixed_term_comp,
        subtotal_entitlements=subtotal,
        total_due=subtotal,
        generated_at=datetime.now().isoformat(timespec="seconds")
    )

def results_to_rows(inp: Inputs, res: Results) -> Dict[str, float]:
    return {
        "Monthly Wage": inp.monthly_wage,
        "Hourly Rate": res.hourly_rate,
        "Daily Rate": res.daily_rate,
        "Notice Pay": res.notice_pay,
        "Arbitrary Dismissal Compensation": res.arbitrary_dismissal_comp,
        "EOS Gratuity (if no SSC)": res.eos_gratuity,
        "Unused Leave Compensation": res.unused_leave_comp,
        "Unpaid Wages (Missed Months)": res.unpaid_wages,
        "Overtime - Regular (125%)": res.overtime_regular,
        "Overtime - Holiday/Friday (150%)": res.overtime_holiday,
        "Fixed-term Remaining Compensation": res.fixed_term_remaining_comp,
        "Total Due": res.total_due,
    }

def export_results(inp: Inputs, res: Results, path: str) -> str:
    import csv, os
    rows = results_to_rows(inp, res)
    # Always write CSV
    base, ext = os.path.splitext(path)
    csv_path = path if ext.lower() == ".csv" else base + ".csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Amount (JOD)"])
        for k, v in rows.items():
            writer.writerow([k, f"{v:.3f}"])
    # Try to write XLSX as well if user asked for .xlsx or .xls
    if ext.lower() in [".xlsx", ".xls"]:
        try:
            import pandas as pd
            df = pd.DataFrame(list(rows.items()), columns=["Item", "Amount (JOD)"])
            xlsx_path = base + ".xlsx"
            df.to_excel(xlsx_path, index=False)
            return xlsx_path
        except Exception:
            # If pandas/openpyxl isn't available, fall back to CSV only
            return csv_path
    return csv_path

def print_breakdown(inp: Inputs, res: Results):
    print("\n=== Jordan Unlawful Termination Compensation Breakdown ===")
    print(f"Generated at: {res.generated_at}")
    print(f"Monthly wage: {inp.monthly_wage:.3f} JOD")
    print(f"Hourly rate (monthly_hours={inp.monthly_hours:.2f}): {res.hourly_rate:.4f} JOD")
    print(f"Daily rate (divisor={inp.daily_divisor:.0f}): {res.daily_rate:.4f} JOD")
    print(f"Contract type: {inp.contract_type} | Notice given: {inp.notice_given}")
    print(f"Covered by Social Security: {inp.covered_by_social_security}")
    if inp.contract_type.lower() == "fixed" and inp.fixed_contract_months_remaining > 0:
        print(f"Fixed-term months remaining: {inp.fixed_contract_months_remaining}")
    print("\n-- Entitlements --")
    print(f"Notice pay: {res.notice_pay:.3f}")
    print(f"Arbitrary/Unfair dismissal compensation: {res.arbitrary_dismissal_comp:.3f}")
    print(f"End-of-service gratuity (if no SSC): {res.eos_gratuity:.3f}")
    print(f"Unused annual leave compensation ({inp.unused_leave_days} days): {res.unused_leave_comp:.3f}")
    print(f"Unpaid wages ({inp.missed_wage_months} months): {res.unpaid_wages:.3f}")
    print(f"Overtime (regular, 125%): {res.overtime_regular:.3f}")
    print(f"Overtime (holiday/Friday, 150%): {res.overtime_holiday:.3f}")
    print(f"Fixed-term remaining compensation: {res.fixed_term_remaining_comp:.3f}")
    print("-----------------------------------------------------------")
    print(f"TOTAL DUE: {res.total_due:.3f} JOD\n")

def interactive_prompts() -> Inputs:
    def ffloat(prompt, default=None):
        while True:
            s = input(prompt + (f" [{default}] " if default is not None else " ")).strip()
            if s == "" and default is not None:
                return float(default)
            try:
                return float(s)
            except ValueError:
                print("Please enter a number.")
    def fint(prompt, default=None):
        while True:
            s = input(prompt + (f" [{default}] " if default is not None else " ")).strip()
            if s == "" and default is not None:
                return int(default)
            try:
                return int(s)
            except ValueError:
                print("Please enter an integer.")
    def fbool(prompt, default=None):
        while True:
            s = input(prompt + (f" [{default}] " if default is not None else " ")).strip().lower()
            if s == "" and default is not None:
                return str(default).lower() in ("y", "yes", "true", "1")
            if s in ("y", "yes", "true", "1"):
                return True
            if s in ("n", "no", "false", "0"):
                return False
            print("Please answer y/n.")
    monthly_wage = ffloat("Monthly wage (JOD):")
    years = fint("Years of service:", 0)
    months = fint("Additional months of service:", 0)
    contract_type = input("Contract type [unlimited/fixed] [unlimited]: ").strip().lower() or "unlimited"
    notice_given = fbool("Was proper notice (1 month) given? [y/n] [n]:", "n")
    unused_leave_days = ffloat("Unused annual leave days:", 0)
    missed_wage_months = ffloat("Unpaid wages (months):", 0)
    regular_ot_hours = ffloat("Regular overtime hours (125%):", 0)
    holiday_ot_hours = ffloat("Holiday/Friday overtime hours (150%):", 0)
    monthly_hours = ffloat(f"Monthly working hours (default {DEFAULT_MONTHLY_HOURS:.2f}):", DEFAULT_MONTHLY_HOURS)
    daily_divisor = ffloat(f"Daily divisor for day rate (default {DEFAULT_DAYS_IN_MONTH_FOR_DAILY_RATE}):", DEFAULT_DAYS_IN_MONTH_FOR_DAILY_RATE)
    covered_by_ssc = fbool("Covered by Social Security? [y/n] [y]:", "y")
    fixed_remaining = 0.0
    if contract_type == "fixed":
        fixed_remaining = ffloat("Fixed-term months remaining (if terminated early):", 0)
    return Inputs(
        monthly_wage=monthly_wage,
        years_of_service=years,
        months_of_service=months,
        contract_type=contract_type,
        notice_given=notice_given,
        unused_leave_days=unused_leave_days,
        missed_wage_months=missed_wage_months,
        regular_ot_hours=regular_ot_hours,
        holiday_ot_hours=holiday_ot_hours,
        monthly_hours=monthly_hours,
        daily_divisor=daily_divisor,
        covered_by_social_security=covered_by_ssc,
        fixed_contract_months_remaining=fixed_remaining
    )

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Jordan Unlawful Termination Calculator")
    p.add_argument("--monthly-wage", type=float, help="Monthly wage in JOD")
    p.add_argument("--years", type=int, default=0, help="Years of service")
    p.add_argument("--months", type=int, default=0, help="Additional months of service (0-11)")
    p.add_argument("--contract", type=str, choices=["unlimited", "fixed"], default="unlimited", help="Contract type")
    p.add_argument("--notice-given", action="store_true", help="Set if proper notice was given")
    p.add_argument("--unused-leave-days", type=float, default=0.0, help="Unused annual leave days to be paid")
    p.add_argument("--missed-wage-months", type=float, default=0.0, help="Unpaid wage months")
    p.add_argument("--regular-ot-hours", type=float, default=0.0, help="Overtime hours at 125%%")
    p.add_argument("--holiday-ot-hours", type=float, default=0.0, help="Overtime hours at 150%% (Fridays/holidays)")
    p.add_argument("--monthly-hours", type=float, default=DEFAULT_MONTHLY_HOURS, help="Monthly working hours (default ~208)")
    p.add_argument("--daily-divisor", type=float, default=DEFAULT_DAYS_IN_MONTH_FOR_DAILY_RATE, help="Daily wage divisor (default 30)")
    p.add_argument("--covered-by-ssc", action="store_true", help="Set if worker is covered by Social Security (default True)")
    p.add_argument("--no-covered-by-ssc", dest="covered_by_ssc", action="store_false", help="Set if NOT covered by Social Security")
    p.set_defaults(covered_by_ssc=True)
    p.add_argument("--fixed-months-remaining", type=float, default=0.0, help="For fixed-term: months remaining if terminated early")
    p.add_argument("--export", type=str, help="Path to export results (CSV or XLSX). Example: results.xlsx")
    return p.parse_args()

def main():
    args = parse_args()
    if args.monthly_wage is None:
        # Interactive mode
        inp = interactive_prompts()
    else:
        inp = Inputs(
            monthly_wage=args.monthly_wage,
            years_of_service=args.years,
            months_of_service=args.months,
            contract_type=args.contract,
            notice_given=args.notice_given,
            unused_leave_days=args.unused_leave_days,
            missed_wage_months=args.missed_wage_months,
            regular_ot_hours=args.regular_ot_hours,
            holiday_ot_hours=args.holiday_ot_hours,
            monthly_hours=args.monthly_hours,
            daily_divisor=args.daily_divisor,
            covered_by_social_security=args.covered_by_ssc,
            fixed_contract_months_remaining=args.fixed_months_remaining,
        )
    res = calculate_all(inp)
    print_breakdown(inp, res)
    if args.export:
        out_path = export_results(inp, res, args.export)
        print(f"Exported results to: {out_path}")

if __name__ == "__main__":
    main()
