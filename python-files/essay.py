import time
import random

name = "Her"  # Replace with her name if you want to personalize

# Sections for realism
emotional_intros = [
    "When I think about her, a rush of emotions overwhelms me.",
    "Every moment spent pondering her essence feels like a journey into my soul.",
    "From the depths of my heart, I attempt to articulate what she means to me.",
    "Perception is complex, especially when it's about someone so... unique."
]

core_phrase = ["you are dumb", "you're dumb", "ur dumb", "YOU. ARE. DUMB."]
transitions = [
    "Moreover,", "Furthermore,", "Interestingly,", "Needless to say,", "Undoubtedly,"
]
citations = [
    "(Smith, 2024)", "(Journal of Emotional Dumbness)", "(Cognitive Sciences Review)", "(Wikipedia, probably)"
]

def write_essay(repetitions=500):
    print("[LOG] Initiating Emotional Analysis...")
    time.sleep(1)
    print("[LOG] Simulating deep thought patterns...")
    time.sleep(1)
    print(f"[INFO] Topic: How I feel about {name} and my perception of her.\n")
    time.sleep(1)

    essay = f"\n--- THE INTELLECTUAL MASTERPIECE STARTS ---\n\n"
    essay += f"Title: An Introspective Analysis of My Perception of {name}\n\n"
    
    essay += random.choice(emotional_intros) + "\n\n"

    for i in range(1, repetitions + 1):
        transition = random.choice(transitions)
        phrase = random.choice(core_phrase)
        citation = random.choice(citations)
        
        sentence = f"{transition} {phrase}. {citation}"
        essay += sentence + " "

        # Logs
        if i % 50 == 0:
            print(f"[PROGRESS] {i}/{repetitions} sentences added...")
            time.sleep(0.3)

    essay += "\n\nIn conclusion, despite the depth of my emotions, my final perception remains clear: you are dumb. (Final Study, 2025)"
    print("\n[LOG] Emotional essay complete.")
    return essay

if __name__ == "__main__":
    final_text = write_essay(1000)
    print("\n--- FINAL ESSAY ---\n")
    print(final_text)
    input("\n[LOG] Press Enter to exit...")

