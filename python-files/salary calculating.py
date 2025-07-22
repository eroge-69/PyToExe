def calculate_income(base_salary, child_allowance, food_allowance, mariage_allowance, home_allowance):
    total_salary = base_salary + child_allowance + food_allowance + mariage_allowance + home_allowance

    # Tax calculated only on base_salary + home_allowance
    taxable_salary = base_salary + home_allowance

    tax_deduction = 0
    if taxable_salary > 66:
        tax_deduction += (taxable_salary - 66) * 0.30
    if taxable_salary > 50:
        tax_deduction += (min(taxable_salary, 66) - 50) * 0.25
    if taxable_salary > 38:
        tax_deduction += (min(taxable_salary, 50) - 38) * 0.20
    if taxable_salary > 30:
        tax_deduction += (min(taxable_salary, 38) - 30) * 0.15
    if taxable_salary > 24:
        tax_deduction += (min(taxable_salary, 30) - 24) * 0.10

    insurance_deduction = total_salary * 0.07  # 7% of total salary

    total_deduction = tax_deduction + insurance_deduction
    income = total_salary - total_deduction

    return income, insurance_deduction, tax_deduction


try:
    base_salary = float(input("Enter base salary: "))
    child_allowance = float(input("Enter child allowance: "))
    food_allowance = float(input("Enter food allowance: "))
    mariage_allowance = float(input("Enter mariage allowance: "))
    home_allowance = float(input("Enter home allowance: "))

    income, insurance, tax = calculate_income(base_salary, child_allowance, food_allowance, mariage_allowance,
                                              home_allowance)

    print(f"Income after deductions: {income:.2f}")
    print(f"Insurance deduction: {insurance:.2f}")
    print(f"Tax deduction: {tax:.2f}")
except ValueError:
    print("Please enter valid numbers for all inputs.")

input("Press Enter to exit...")