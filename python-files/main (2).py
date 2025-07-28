import time
import sys

def generate_activation(chip_id: str) -> str:
    s = chip_id.zfill(8)
    d = [int(ch) for ch in s]
    a, b = d[1], d[2]
    s_digit = (d[4] + d[5] + d[6]) % 10
    l = abs(d[7] - s_digit)
    return f"{a}{b}0{s_digit}{l}"

def perform_effects_and_calculations(chip_id: str):
    print("\nProcessing", end="")
    for _ in range(5):
        print(".", end="")
        sys.stdout.flush()
        time.sleep(0.2)
    value = int(chip_id)
    print(f"\nBinary representation: {value:032b}")
    print(f"Hex representation: 0x{value:08X}\n")

def main():
    print("Activation Code Generator with Binary & Hex Effects")
    print("Designed by: Eng. Ahmad +972595951849\n")
    while True:
        user_input = input("Enter chip ID: ").strip()
        if user_input.lower() == 'exit':
            print("Exiting. Goodbye!")
            break
        if not user_input.isdigit():
            print("Error: Input must be numeric.\n")
            continue
        perform_effects_and_calculations(user_input)
        code = generate_activation(user_input)
        print(f"Activation Code: {code}\n")

if __name__ == "__main__":
    main()
