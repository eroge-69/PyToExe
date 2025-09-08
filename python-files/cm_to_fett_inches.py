cm = float(input("Enter in CM: "))  # convert input to number

in_inches = cm * 0.393701
feet = int(in_inches // 12)        # whole feet
inches = in_inches % 12            # remaining inches

print(f"{feet}' {inches:.2f}\"")
