import os
from datetime import datetime

# Files for saving counter and data
counter_file = "counter.txt"
data_file = "data.txt"

# Current year
current_year = datetime.now().year

# Load last saved year and counter
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        saved_year, saved_count = f.read().strip().split(",")
        saved_year = int(saved_year)
        saved_count = int(saved_count)
else:
    saved_year, saved_count = current_year, 0

# If the year has changed, reset the counter
if saved_year != current_year:
    saved_count = 0

# Increment counter
saved_count += 1

# Create article number in format YEAR.NUMBER
article_number = f"{current_year}.{saved_count}"

# Ask user for name
name = input("Enter your name: ")

# Save entry to data file
with open(data_file, "a") as f:
    f.write(f"{name}, Article Number: {article_number}\n")

# Save updated year and counter
with open(counter_file, "w") as f:
    f.write(f"{current_year},{saved_count}")

print(f"✅ Saved! {name} got Article Number {article_number}")
