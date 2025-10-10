import itertools
import os

# Configuration
min_letters = 1
max_letters = 12  # Reduce for testing
digits_range = range(100)  # Use 100 numbers instead of 10,000
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Use local disk for testing
base_path = r"S:/Students/Year 8's/Random stuff/passwords"
os.makedirs(base_path, exist_ok=True)

# Loop through letter lengths from 1 to max_letters
for letter_count in range(min_letters, max_letters + 1):
    filename = os.path.join(base_path, f"letter_amount_{letter_count}.txt")
    print(f"Generating {filename}...")

    try:
        with open(filename, 'w') as f:
            for letters in itertools.product(alphabet, repeat=letter_count):
                prefix = ''.join(letters)
                for number in digits_range:
                    formatted_number = f"{number:04d}"
                    f.write(f"{prefix}.{formatted_number}\n")
    except Exception as e:
        print(f"❌ Error writing {filename}: {e}")

print("✅ All files generated successfully.")
