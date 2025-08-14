categories = {
    "TO 0 EXEI NA VGEI": (0, 0),
    "H 6ADA 1-6 EXEI NA VGEI": (1, 6),
    "H 6ADA 4-9 EXEI NA VGEI": (4, 9),
    "H 6ADA 7-12 EXEI NA VGEI": (7, 12),
    "H 6ADA 10-15 EXEI NA VGEI": (10, 15),
    "H 6ADA 13-18 EXEI NA VGEI": (13, 18),
    "H 6ADA 16-21 EXEI NA VGEI": (16, 21),
    "H 6ADA 19-24 EXEI NA VGEI": (19, 24),
    "H 6ADA 22-27 EXEI NA VGEI": (22, 27),
    "H 6ADA 25-30 EXEI NA VGEI": (25, 30),
    "H 6ADA 28-33 EXEI NA VGEI": (28, 33),
    "H 6ADA 31-36 EXEI NA VGEI": (31, 36),
    "H 6ADA 1-3 + 34-36 EXEI NA VGEI": (1, 3),
    "H 6ADA 1-3 KAI 34-36 EXEI NA VGEI": (34, 36),
}

category_values = {category: 0 for category in categories}

while True:
    user_input = int(input("EPOMENOS ARITHMOS: "))
    
    if user_input == 666:
        break
    
    for category, (low, high) in categories.items():
        if low <= user_input <= high:
            category_values[category] = 0
        else:
            category_values[category] += 1

    print("\nOK, TWRA:")
    for category, value in category_values.items():
        print(f"{category}: {value}")
