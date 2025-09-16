def analyze_message(msg):
    letters = [ch for ch in msg if ch.isalpha()]
    digits = [int(ch) for ch in msg if ch.isdigit()]

    # Count frequency of each letter
    from collections import Counter
    letter_counts = dict(Counter(letters))

    # Sum of all digits
    digit_sum = sum(digits)

    # Check uppercase vs lowercase count
    upper_count = sum(1 for ch in letters if ch.isupper())
    lower_count = sum(1 for ch in letters if ch.islower())

    # Filter letters based on condition
    if upper_count > lower_count:
        filtered_letters = ''.join(ch for ch in letters if ch.isupper())
    else:
        filtered_letters = ''.join(letters)

    return letter_counts, digit_sum, filtered_letters

# Example usage:
msg = "A4bB7cC9a1D2"
counts, total, filtered = analyze_message(msg)
print("Letter frequencies:", counts)
print("Sum of digits:", total)
print("Filtered letters:", filtered)