def estimate_taxable_income(tax_deducted):
    # Define tax slabs in reverse for easier computation
    slabs = [
        (700000, 4100000, 0.35),
        (430000, 3200000, 0.30),
        (180000, 2200000, 0.25),
        (30000, 1200000, 0.15),
        (0, 600000, 0.05),
        (0, 0, 0.00)  # For income up to 600,000
    ]

    if tax_deducted == 0:
        return 600000

    # Iterate through the slabs
    for base_tax, base_income, rate in slabs:
        if tax_deducted > base_tax:
            # Calculate the excess tax over the base
            excess_tax = tax_deducted - base_tax
            # Calculate the excess income that caused this tax
            excess_income = excess_tax / rate if rate > 0 else 0
            # Add to the base income to get taxable income
            taxable_income = base_income + excess_income
            return round(taxable_income)

    return "Taxable income could not be estimated."

# Example usage:
tax_deducted = float(input("Enter total tax deducted (₹): "))
income = estimate_taxable_income(tax_deducted)
print(f"Estimated Taxable Income: ₹{income:,}")

