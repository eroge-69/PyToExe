```python
import time
import random

# Sample texts for typing practice
texts = [
    "The quick brown fox jumps over the lazy dog.",
    "Python is an interpreted, high-level, general-purpose programming language.",
    "Typing speed is measured in words per minute.",
    "Gaming has become an essential form of entertainment.",
]

def get_random_text():
    return random.choice(texts)

def typing_test():
    print("Welcome to the Typing Game!")
    input("Press Enter to start...")
    
    # Get a random text to type
    text_to_type = get_random_text()
    print("\nType the following text as fast as you can:\n")
    print(f"{text_to_type}\n")

    start_time = time.time()
    
    # User input
    user_input = input("Your typing: ")
    
    end_time = time.time()
    time_taken = end_time - start_time
    wpm = (len(user_input) / 5) / (time_taken / 60) if time_taken > 0 else 0
    
    # Check accuracy
    correct_chars = sum(1 for a, b in zip(user_input, text_to_type) if a == b)
    accuracy = (correct_chars / len(text_to_type)) * 100

    # Display results
    print("\nResults:")
    print(f"Time taken: {time_taken:.2f} seconds")
    print(f"Words per minute: {wpm:.2f} wpm")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    typing_test()
```