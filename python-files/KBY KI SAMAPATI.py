print("\\033[1mKon banega yash ki sampati\\033[0m")
print("\\033[1mLets see how much yk YASH\\033[0m")




questions = [
    ["What was Yash's first love?", "Study", "Maa", "You", "Woh", 2],
    ["What is Yash’s second love?", "Study", "Maa", "You", "Woh", 1],
    ["Yash’s social code (numeric)?", "9318", "0968", "6666", "None", 2],
    ["How will Yash get married?", "Love Marriage", "Arranged Marriage", "None", "Both", 3],
    ["What will Yash do after B.Tech?", "M.Tech", "Stall", "UPSC", "Marriage", 3],
    ["Yash’s favorite country?", "USA", "India", "Germany", "Russia", 3],
    ["Yash at 2AM is doing?", "Emotional drama", "Coding", "Eating Maggi", "All of the Above", 4],
    ["What’s Yash’s secret superpower?", "Sad Songs", "Tea = Motivation", "Jugaad Mind", "All of these", 3],
    ["What is Yash's biggest fear?", "Compiler Errors", "Wrong Repo Push", "Mom in the saas mood", "Marriage before UPSC", 3],
    ["If Yash had 1 crore, he would?", "Buy Mech Arm", "momos for all", "khuli moj", "Invest & Regret", 2]
]

prizes = [100001, 200001, 300001, 400001, 500001, 600000, 1000000, 1200000, 1400000, 15000000]

total = 0
i = 0

for question in questions:
    print("\n" + question[0])
    print(f"a. {question[1]}")
    print(f"b. {question[2]}")
    print(f"c. {question[3]}")
    print(f"d. {question[4]}")

    try:
        answer = int(input("Enter your answer (1 for a, 2 for b, 3 for c, 4 for d): "))
    except ValueError:
        print("Invalid input. Please enter a number from 1 to 4.")
        break

    if question[5] == answer:
        print("✅ Correct Answer!")
        total += prizes[i]
        print(f"💰 You won ₹{prizes[i]} YSH")
        i += 1
    else:
        print(f"❌ Incorrect! The correct answer was option {question[5]}: {question[question[5]]}")
        print("😢 Better luck next time!")
        break

print(f"\n🏁 Game Over! You won a total of ₹{total} YSH")

if total == sum(prizes):
    print("\n🎉 CONGRATS! You just won the full Sampatti 🏆")
    print("💸 Total Amount: 60,00,000 YSH 💸")
    print("⚠️ For exchange bata diyo yr{1 YSH =0.000000004₹} 😏")
