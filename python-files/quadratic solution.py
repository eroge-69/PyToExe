import math

a = float(input("co-efficient (a≠0), a: "))
b = float(input("co-efficient, b: "))
c = float(input("co-efficient, c: "))
print()

# Re-prompt until a is not zero
while a == 0:
    print("ERROR: (a≠0). Input a non-zero value for 'a'.\n")
    a = float(input("co-efficient (a≠0), a: "))
print()

print(f"Co-efficient, a: {a:.2f}")
print(f"Co-efficient, b: {b:.2f}")
print(f"Co-efficient, c: {c:.2f}\n")

# Discriminant
D = b**2 - 4*a*c
print(f"Solution of {a}x² + {b}x + {c} = 0")
print("Here, x = (-b ± √(b² - 4ac)) / 2a\n")

if D > 0:
    # Two real roots
    i = math.sqrt(D)
    x1 = (-b + i) / (2 * a)
    x2 = (-b - i) / (2 * a)
    print(f"Discriminant (D): {D:.2f} > 0 → Two distinct real roots")
    print(f"x₁ = {x1:.2f}, x₂ = {x2:.2f}")
elif D == 0:
    # One real root
    x = -b / (2 * a)
    print(f"Discriminant (D): {D:.2f} = 0 → One repeated real root")
    print(f"x = {x:.2f}")
else:
    # Complex roots (without cmath module)
    real_part = -b/(2*a)
    imaginary_part = math.sqrt(abs(D))/(2*a)
    
    print(f"Discriminant (D): {D:.2f} < 0 → Two complex roots")
    print(f"x₁ = {real_part:.2f}+{imaginary_part:.2f}i, x₂ = {real_part:.2f}-{imaginary_part:.2f}i")

print("\nPress Enter to exit.")