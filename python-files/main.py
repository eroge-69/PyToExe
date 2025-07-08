# Healthy Habits Quiz Game
print("Welcome to the Healthy Habits Quiz!")
print("Answer these questions to test your health knowledge.")
print("Choose the correct option (1, 2, 3, or 4). Let's start!\n")

# Initialize score
score = 0
total_questions = 3

# Question 1
print("Question 1: How many hours of sleep are recommended for adults per night?")
print("1. 4-5 hours\n2. 6-7 hours\n3. 7-9 hours\n4. 10-12 hours")
answer1 = input("Your answer (1-4): ")

if answer1 == "3":
    print("Correct! Adults need 7-9 hours of sleep for good health.")
    score += 1
else:
    print("Oops! The correct answer is 7-9 hours.")

# Question 2
print("\nQuestion 2: How much water should you drink daily (approx.)?")
print("1. 1 liter\n2. 2-3 liters\n3. 4-5 liters\n4. 6 liters")
answer2 = input("Your answer (1-4): ")

if answer2 == "2":
    print("Great job! 2-3 liters is recommended for most adults.")
    score += 1
else:
    print("Not quite! The correct answer is 2-3 liters.")

# Question 3
print("\nQuestion 3: What is a normal resting pulse rate for adults?")
print("1. 40-50 bpm\n2. 60-100 bpm\n3. 100-120 bpm\n4. 120-140 bpm")
answer3 = input("Your answer (1-4): ")

if answer3 == "2":
    print("Well done! A normal resting pulse is 60-100 beats per minute.")
    score += 1
else:
    print("Incorrect. The correct answer is 60-100 bpm.")

# Final Score
print("\nQuiz complete!")
print(f"You scored {score} out of {total_questions}!")
if score == total_questions:
    print("Perfect! You're a health habits expert!")
elif score >= 1:
    print("Good effort! Keep learning about healthy habits!")
else:
    print("Don't worry, try again to boost your health knowledge!")

# BUHSC-inspired message
print("Inspired by BUHSC, keep promoting health and wellness!")