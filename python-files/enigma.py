import random
import string

# Set a fixed seed for consistency across runs
random.seed(42)

# Create a list of lowercase letters
letters = list(string.ascii_lowercase)

# Shuffle the list randomly with the fixed seed
random.shuffle(letters)

# Create a mapping by pairing adjacent letters as swaps
mapping = {}
for i in range(0, 26, 2):
    x = letters[i]
    y = letters[i+1]
    mapping[x] = y
    mapping[y] = x
# Get user input
input_str = input("Enter a string: ")

# Transform the input based on the mapping
output = []
for c in input_str: