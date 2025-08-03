while True:
    passwordinput = input("Make a password: ")

    # Check for number
    has_number = any(char.isdigit() for char in passwordinput)
    if has_number:
        print("✅ Has a number")
    else:
        print("❌ No number found")

    # Check length
    if len(passwordinput) < 6:
        print("❌ PASSWORD TOO SHORT")
    else:
        print("✅ Valid length")

    # Check uppercase
    has_upper = any(char.isupper() for char in passwordinput)
    if has_upper:
        print("✅ Upper case letter")
    else:
        print("❌ No uppercase letter")

    # All conditions passed
    if has_number and has_upper and len(passwordinput) >= 6:
        print("🎉 Password accepted!")
        break
    else:
        print("⚠️ Please try again.\n")
