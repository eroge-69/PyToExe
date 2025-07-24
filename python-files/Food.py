# Define VAT and tip percentages
vat_per = 18 / 100
tip_per = 10 / 100

# Get the base price of the meal from the user
try:
    price = float(input("🍽️ Enter the price of your meal (LKR): "))
except ValueError:
    print("❌ Invalid input. Please enter a number.")
    exit()

# Calculate VAT
vat_amount = price * vat_per
total_vat = price + vat_amount

# Show the price with VAT
print(f"✅ Price with 18% VAT: {total_vat:.2f} LKR")

# Ask the user if they want to add a 10% tip
choice = input("💁 Would you like to add a 10% tip? (Y/N): ").strip().upper()

if choice == "Y":
    tip_amount = total_vat * tip_per
    total = total_vat + tip_amount
    print(f"👍 Tip added: {tip_amount:.2f} LKR")
elif choice == "N":
    total = total_vat
    print("✅ No tip added.")
else:
    print("⚠️ Invalid choice. Proceeding without tip.")
    total = total_vat

# Final total output
print(f"\n🍴 Total amount to pay: {total:.2f} LKR\nThank you! Happy dining! 🎉")
