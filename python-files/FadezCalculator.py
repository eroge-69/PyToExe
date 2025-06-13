print("1. Basic Plan (€5.50/sec)")
print("2. Advanced Plan (€7.50/sec)")
print("3. Premium Plan (€5.50/sec)")
print("4. Special Plan (€X/sec)")
planOptions = [1, 2, 3, 4]

try:
    animationPlan = (int(input("What animation plan do you want? (1-4): ")))
    if animationPlan not in planOptions:
        print("Invalid plan option, try again.")
        exit()
except ValueError:
    print("Please enter a number between 1-4.")
    exit()

try:
    duration = int(input("How many seconds long is the animation?: "))
except ValueError:
    print("Please enter a valid number.")
    exit()

if animationPlan == 1:
    rate = 5.50
elif animationPlan == 2:
    rate = 7.50
elif animationPlan == 3:
    rate = 10.50
elif animationPlan == 4:
    try:
        rate = float(input("Enter your custom rate per second (€): "))
    except ValueError:
        print("Invalid custom rate.")
        exit()

addons = {
    "Foliage Movement": 10,
    "Facial Expressions": 15,
    "SFX": 10,
    "VFX & Editing": 15
}

addonTotal = 0

print("\nAddons:")
for name, price in addons.items():
    response = input(f"Do you want `{name}` for €{price}? (y/n): ").strip().lower()
    if response in ["yes", "y"]:
        addonTotal += price
    elif response in ["no", "n"]:
        print("Addon not added.")
    else:
        print("Invalid response. Skipping addons.")

print("\nRendering: ")
renderTrue = input("Do you want rendering (€10) to be calculated as well? (y/n): ").strip().lower()
renderCharge = 10 if renderTrue in ["yes", "y"] else 0
if renderCharge == 0:
    print("Render charge not added.")
    
print("\nDiscount: ")
discountResponse = input("Do you want to calculate with a discount? (y/n): ").strip().lower()
if discountResponse in ["yes", "y"]:
    try:
        discountRate = float(input("What percentage discount do you want to calculate? (0-100): "))
    except ValueError:
        print("Invalid discount value. No discount applied.")
else:
    print("Discount not added.")

baseCost = rate * duration
totalBeforeDiscount = baseCost + addonTotal + renderCharge
totalAfterDiscount = totalBeforeDiscount * (1 - discountRate/100)

print("\n--- Price Summary ---")
print(f"Base Animation Cost: €{baseCost:.2f}")
print(f"Addon Total: €{addonTotal:.2f}")
print(f"Render Charge: €{renderCharge:.2f}")
print(f"Subtotal before discount: €{totalBeforeDiscount:.2f}")
if discountRate > 0:
    print(f"Discount applied: {discountRate}%")
    print(f"\nFinal total after discount: €{totalAfterDiscount:.2f}")
else:
    print(f"\nFinal total: €{totalBeforeDiscount:.2f}")