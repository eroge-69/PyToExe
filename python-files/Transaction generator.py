import pandas as pd
import random
import string
import calendar
import os
from datetime import datetime, timedelta

# Input prompts
print("Enter transaction breakdown parameters:")
print("Note: Transaction amounts will vary realistically, favoring amounts ending in 0 or 5.")
total_transactions = int(input("Total number of sale transactions (e.g., 84756): "))
months_input = input("Months (e.g., 11/2024,12/2024,01/2025): ").split(',')
months = [month.strip() for month in months_input]
monthly_counts_input = input("Monthly sale transaction counts (e.g., 11761,12128,12574): ").split(',')
monthly_volumes_input = input("Monthly sale volumes in EUR (e.g., 645799,668293,694614): ").split(',')
min_amount = int(input("Minimum sale transaction amount (e.g., 10): "))
max_amount = int(input("Maximum sale transaction amount (e.g., 1000): "))
max_per_month = int(input("Number of max-amount sale transactions per month (e.g., 3): "))
total_chargebacks = int(input("Total number of chargebacks (e.g., 100): "))
chargeback_fee = float(input("Chargeback fee per transaction (e.g., -5.00): "))
monthly_chargeback_counts_input = input("Monthly chargeback counts (e.g., 33,33,34): ").split(',')
monthly_chargeback_volumes_input = input("Monthly chargeback volumes in EUR (e.g., 1650,1650,1700): ").split(',')
total_refunds = int(input("Total number of refunds (e.g., 150): "))
refund_fee = float(input("Refund fee per transaction (e.g., -2.00): "))
monthly_refund_counts_input = input("Monthly refund counts (e.g., 50,50,50): ").split(',')
monthly_refund_volumes_input = input("Monthly refund volumes in EUR (e.g., 2500,2500,2500): ").split(',')
transaction_fee = float(input("Transaction fee per sale transaction (e.g., 0.50): "))
company_name = input("Company name for the first column (e.g., Marsley LTD): ")
output_file = input("Output Excel file name (e.g., Transaction_History.xlsx): ")

# Ensure output file has .xlsx extension
if not output_file.lower().endswith('.xlsx'):
    output_file += '.xlsx'

# Validate inputs
if not (len(months) == len(monthly_counts_input) == len(monthly_volumes_input) == 
        len(monthly_chargeback_counts_input) == len(monthly_chargeback_volumes_input) == 
        len(monthly_refund_counts_input) == len(monthly_refund_volumes_input)):
    raise ValueError("Number of months must match the number of monthly counts and volumes for sales, chargebacks, and refunds.")

monthly_counts = {month: int(count) for month, count in zip(months, monthly_counts_input)}
monthly_volumes = {month: int(volume) for month, volume in zip(months, monthly_volumes_input)}
monthly_chargeback_counts = {month: int(count) for month, count in zip(months, monthly_chargeback_counts_input)}
monthly_chargeback_volumes = {month: int(volume) for month, volume in zip(months, monthly_chargeback_volumes_input)}
monthly_refund_counts = {month: int(count) for month, count in zip(months, monthly_refund_counts_input)}
monthly_refund_volumes = {month: int(volume) for month, volume in zip(months, monthly_refund_volumes_input)}

if sum(monthly_counts.values()) != total_transactions:
    raise ValueError("Sum of monthly sale counts does not equal total sale transactions.")
if sum(monthly_chargeback_counts.values()) != total_chargebacks:
    raise ValueError("Sum of monthly chargeback counts does not equal total chargebacks.")
if sum(monthly_refund_counts.values()) != total_refunds:
    raise ValueError("Sum of monthly refund counts does not equal total refunds.")

for month in months:
    if monthly_chargeback_counts[month] > monthly_counts[month]:
        raise ValueError(f"Chargeback count for {month} exceeds sale count.")
    if monthly_refund_counts[month] > monthly_counts[month]:
        raise ValueError(f"Refund count for {month} exceeds sale count.")

# Helper functions
def generate_dates(month_str, count):
    month, year = map(int, month_str.split('/'))
    num_days = calendar.monthrange(year, month)[1]
    daily_count = count // num_days
    remainder = count % num_days
    dates = []
    for day in range(1, num_days + 1):
        day_count = daily_count + (1 if day <= remainder else 0)
        date_str = f"{day:02d}/{month:02d}/{year}"
        dates.extend([date_str] * day_count)
    return dates

def generate_operation_id():
    length = random.randint(10, 16)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_arn(card_scheme):
    return f"{card_scheme.lower()}-{''.join(random.choices(string.digits, k=23))}"

def add_random_days(date_str, min_days=5, max_days=9):
    date = datetime.strptime(date_str, "%d/%m/%Y")
    month, year = date.month, date.year
    days_in_month = calendar.monthrange(year, month)[1]
    additional_days = random.randint(min_days, max_days)
    new_date = date + timedelta(days=additional_days)
    if new_date.month != month:
        new_date = datetime(year, month, days_in_month)
    return new_date.strftime("%d/%m/%Y")

def generate_amounts(count, volume, min_amount, max_amount, max_per_month):
    amounts = [max_amount] * min(max_per_month, count)
    remaining_count = count - len(amounts)
    remaining_volume = volume - sum(amounts)
    if remaining_count <= 0:
        return amounts
    target_avg = remaining_volume / remaining_count
    width = 50
    low = max(min_amount, int(target_avg - width))
    high = min(max_amount, int(target_avg + width))
    possible_amounts = list(range(low, high + 1))
    weights = [5 if a % 10 == 0 else 3 if a % 5 == 0 else 1 for a in possible_amounts]
    remaining_amounts = random.choices(possible_amounts, weights=weights, k=remaining_count)
    current_sum = sum(remaining_amounts)
    discrepancy = remaining_volume - current_sum
    adjustable_indices = list(range(remaining_count))
    iterations = 0
    max_iterations = 10000 * remaining_count
    while discrepancy != 0 and adjustable_indices and iterations < max_iterations:
        idx = random.choice(adjustable_indices)
        if discrepancy > 0 and remaining_amounts[idx] < max_amount:
            remaining_amounts[idx] += 1
            discrepancy -= 1
        elif discrepancy < 0 and remaining_amounts[idx] > min_amount:
            remaining_amounts[idx] -= 1
            discrepancy += 1
        else:
            adjustable_indices.remove(idx)
        iterations += 1
    if discrepancy != 0:
        raise ValueError(f"Cannot adjust amounts to match volume: discrepancy {discrepancy}")
    return amounts + remaining_amounts

# Generate transactions
data = []
total_sales = 0
total_chargebacks_generated = 0
total_refunds_generated = 0

for month in months:
    # Sale transactions
    sale_count = monthly_counts[month]
    sale_volume = monthly_volumes[month]
    sale_dates = generate_dates(month, sale_count)
    sale_amounts = generate_amounts(sale_count, sale_volume, min_amount, max_amount, max_per_month)
    random.shuffle(sale_amounts)  # Shuffle sale amounts to avoid sequences
    month_data = []
    sale_transactions = {}
    for date, amount in zip(sale_dates, sale_amounts):
        operation_id = generate_operation_id()
        card_type = "debit" if random.random() < 0.88 else "credit"
        card_scheme = "visa" if (card_type == "credit" and random.random() < 0.81) or (card_type == "debit" and random.random() < 0.53) else "mastercard"
        total_fee = -transaction_fee
        net_amount = amount + total_fee
        tx = {
            "Merchant Id": company_name,
            "Operation": "Sale",
            "Tx Date": date,
            "Operation Id": operation_id,
            "Amount": amount,
            "Authorization Currency": "EUR",
            "Total Fee": round(total_fee, 2),
            "Reserved": 0.00,
            "Net Amount": round(net_amount, 2),
            "Card Type": card_type,
            "Card Scheme": card_scheme,
            "Arn": generate_arn(card_scheme)
        }
        month_data.append(tx)
        sale_transactions[operation_id] = tx
        total_sales += 1

    # Chargeback transactions
    cb_count = monthly_chargeback_counts[month]
    cb_volume = monthly_chargeback_volumes[month]
    if cb_count > 0:
        cb_avg = cb_volume / cb_count
        cb_low = max(min_amount, int(cb_avg - 50))
        cb_high = min(max_amount, int(cb_avg + 50))
        cb_possible = list(range(cb_low, cb_high + 1))
        cb_weights = [5 if a % 10 == 0 else 3 if a % 5 == 0 else 1 for a in cb_possible]
        cb_amounts = random.choices(cb_possible, weights=cb_weights, k=cb_count)
        cb_sum = sum(cb_amounts)
        cb_discrepancy = cb_volume - cb_sum
        cb_indices = list(range(cb_count))
        cb_iterations = 0
        while cb_discrepancy != 0 and cb_indices and cb_iterations < 10000 * cb_count:
            idx = random.choice(cb_indices)
            if cb_discrepancy > 0 and cb_amounts[idx] < max_amount:
                cb_amounts[idx] += 1
                cb_discrepancy -= 1
            elif cb_discrepancy < 0 and cb_amounts[idx] > min_amount:
                cb_amounts[idx] -= 1
                cb_discrepancy += 1
            else:
                cb_indices.remove(idx)
            cb_iterations += 1
        if cb_discrepancy != 0:
            raise ValueError(f"Cannot adjust chargeback amounts for {month}: discrepancy {cb_discrepancy}")
        cb_sales = random.sample(list(sale_transactions.keys()), cb_count)
        for op_id, amount in zip(cb_sales, cb_amounts):
            sale = sale_transactions[op_id]
            new_date = add_random_days(sale["Tx Date"])
            month_data.append({
                "Merchant Id": company_name,
                "Operation": "Chargeback",
                "Tx Date": new_date,
                "Operation Id": op_id,
                "Amount": -amount,
                "Authorization Currency": "EUR",
                "Total Fee": chargeback_fee,
                "Reserved": 0.00,
                "Net Amount": round(-amount + chargeback_fee, 2),
                "Card Type": sale["Card Type"],
                "Card Scheme": sale["Card Scheme"],
                "Arn": sale["Arn"]
            })
            total_chargebacks_generated += 1

    # Refund transactions
    rf_count = monthly_refund_counts[month]
    rf_volume = monthly_refund_volumes[month]
    if rf_count > 0:
        rf_avg = rf_volume / rf_count
        rf_low = max(min_amount, int(rf_avg - 50))
        rf_high = min(max_amount, int(rf_avg + 50))
        rf_possible = list(range(rf_low, rf_high + 1))
        rf_weights = [5 if a % 10 == 0 else 3 if a % 5 == 0 else 1 for a in rf_possible]
        rf_amounts = random.choices(rf_possible, weights=rf_weights, k=rf_count)
        rf_sum = sum(rf_amounts)
        rf_discrepancy = rf_volume - rf_sum
        rf_indices = list(range(rf_count))
        rf_iterations = 0
        while rf_discrepancy != 0 and rf_indices and rf_iterations < 10000 * rf_count:
            idx = random.choice(rf_indices)
            if rf_discrepancy > 0 and rf_amounts[idx] < max_amount:
                rf_amounts[idx] += 1
                rf_discrepancy -= 1
            elif rf_discrepancy < 0 and rf_amounts[idx] > min_amount:
                rf_amounts[idx] -= 1
                rf_discrepancy += 1
            else:
                rf_indices.remove(idx)
            rf_iterations += 1
        if rf_discrepancy != 0:
            raise ValueError(f"Cannot adjust refund amounts for {month}: discrepancy {rf_discrepancy}")
        available_sales = [op_id for op_id in sale_transactions if op_id not in cb_sales]
        rf_sales = random.sample(available_sales, rf_count)
        for op_id, amount in zip(rf_sales, rf_amounts):
            sale = sale_transactions[op_id]
            new_date = add_random_days(sale["Tx Date"])
            month_data.append({
                "Merchant Id": company_name,
                "Operation": "Refund",
                "Tx Date": new_date,
                "Operation Id": op_id,
                "Amount": -amount,
                "Authorization Currency": "EUR",
                "Total Fee": refund_fee,
                "Reserved": 0.00,
                "Net Amount": round(-amount + refund_fee, 2),
                "Card Type": sale["Card Type"],
                "Card Scheme": sale["Card Scheme"],
                "Arn": sale["Arn"]
            })
            total_refunds_generated += 1

    # Shuffle transactions within the month to make the order more chaotic
    random.shuffle(month_data)
    data.extend(month_data)

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
try:
    df.to_excel(output_file, index=False, engine="xlsxwriter")
    print(f"Generated {os.path.abspath(output_file)} with {len(data)} transactions: {total_sales} sales, {total_chargebacks_generated} chargebacks, {total_refunds_generated} refunds.")
except Exception as e:
    print(f"Error saving Excel file: {e}")