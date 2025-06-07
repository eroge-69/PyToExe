import random
import phonenumbers
from phonenumbers import carrier, geocoder
import os

# Function to validate and clean prefixes
def get_valid_prefixes():
    while True:
        prefixes_input = input("Enter comma-separated 2-5 digit prefixes: ").strip()
        prefixes = [p.strip() for p in prefixes_input.split(",") if p.strip()]
        invalid_prefixes = [p for p in prefixes if not (2 <= len(p) <= 5 and p.isdigit())]
        if invalid_prefixes:
            print(f"Invalid prefixes found: {', '.join(invalid_prefixes)}. Please enter valid prefixes.")
        elif not prefixes:
            print("No prefixes entered. Try again!")
        else:
            return prefixes

# Function to distribute total numbers across prefixes randomly
def distribute_numbers(prefixes, total_count):
    distribution = {}
    remaining = total_count
    for i, prefix in enumerate(prefixes[:-1]):
        # Assign a random count to each prefix (at least 1)
        max_for_this_prefix = remaining - (len(prefixes) - i - 1)
        count = random.randint(1, max_for_this_prefix)
        distribution[prefix] = count
        remaining -= count
    # Assign the rest to the last prefix
    distribution[prefixes[-1]] = remaining
    return distribution

# Main script logic
def main():
    # Get valid prefixes
    prefixes = get_valid_prefixes()

    # Get total number count
    while True:
        try:
            total_count = int(input("How many numbers do you want to generate in total? "))
            if total_count > 0:
                break
            print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Distribute numbers across prefixes randomly
    number_distribution = distribute_numbers(prefixes, total_count)

    # Generate and validate numbers
    all_generated_numbers = []
    seen_numbers = set()
    for prefix, count in number_distribution.items():
        remaining_digits = 10 - len(prefix)
        if remaining_digits <= 0:
            print(f"Skipping invalid prefix '{prefix}': It must be shorter than 10 digits.")
            continue

        generated_numbers = []
        while len(generated_numbers) < count:
            random_suffix = ''.join(str(random.randint(0, 9)) for _ in range(remaining_digits))
            full_number = prefix + random_suffix

            # Ensure no duplicates
            if full_number in seen_numbers:
                continue

            seen_numbers.add(full_number)
            number_with_code = f"+91{full_number}"

            try:
                parsed_num = phonenumbers.parse(number_with_code)
                if phonenumbers.is_possible_number(parsed_num) and phonenumbers.is_valid_number(parsed_num):
                    carrier_name = carrier.name_for_number(parsed_num, "en") or "Unknown Carrier"
                    generated_numbers.append(f"{full_number}:{carrier_name}")
                else:
                    generated_numbers.append(f"{full_number}:Unverified")
            except phonenumbers.NumberParseException:
                generated_numbers.append(f"{full_number}:Unverified")

        # Shuffle the generated numbers for this prefix
        random.shuffle(generated_numbers)
        all_generated_numbers.extend(generated_numbers)

    # Shuffle all generated numbers globally
    random.shuffle(all_generated_numbers)

    # Determine state for filename from the first valid number
    state_for_filename = "Unknown"
    for num in all_generated_numbers:
        try:
            parsed = phonenumbers.parse(f"+91{num.split(':')[0]}")
            state = geocoder.description_for_number(parsed, "en")
            if state:
                state_for_filename = state.replace(" ", "_")
                break
        except:
            continue

    # Save results to a file
    output_dir = r"C:\Users\kv094\OneDrive\Desktop\results77\gen"
    os.makedirs(output_dir, exist_ok=True)
    prefixes_str = "_".join(prefixes)
    filename = f"{prefixes_str}_{state_for_filename}_gen.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        for num in all_generated_numbers:
            f.write(num + "\n")

    print(f"Generated {total_count} numbers and saved them to {filepath}.")

if __name__ == "__main__":
    main()