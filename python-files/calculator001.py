def calculate_values():
    """
    From User HP, LP, EP input P, R1, R2, R3 Calculator to Screen
    Values devide (,)
    """
    try:
        # Input
        hp = float(input("Input HP : "))
        lp = float(input("Input LP : "))
        ep = float(input("Input EP : "))

        # P Calculate
        p = (hp + lp + ep) / 3

        # R1, R2, R3 Calculate
        r1 = (2 * p) - hp
        r2 = p + (hp - lp)
        r3 = 2 * (p - lp) + hp

        # Print Result (with ,)
        print("\n--- Result ---")
        print(f"P = {p:,.2f}")
        print(f"R1 = {r1:,.2f}")
        print(f"R2 = {r2:,.2f}")
        print(f"R3 = {r3:,.2f}")

    except ValueError:
        print("Input Right Value.")
    except ZeroDivisionError:
        print("Divide Fail. Check the Value.")

# Exe Script
if __name__ == "__main__":
    calculate_values()