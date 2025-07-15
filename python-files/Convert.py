def inch_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54

def cm_to_inch(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm / 2.54

def main():
    print("Choose conversion type:")
    print("1: Inches to Centimeters")
    print("2: Centimeters to Inches")
    
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        try:
            inches = float(input("Enter length in inches: "))
            cm = inch_to_cm(inches)
            print(f"{inches} in = {cm:.2f} cm")
        except ValueError:
            print("Please enter a valid number.")
    elif choice == "2":
        try:
            cm = float(input("Enter length in centimeters: "))
            inches = cm_to_inch(cm)
            print(f"{cm} cm = {inches:.2f} in")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
