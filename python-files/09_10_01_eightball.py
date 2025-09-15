import random

antwort=["Ganz Sicher nicht!", "Vielleicht.", "unwahrscheinlich.", "Safe, absolut!", "Jein.", "Bestimmt!"]

print("Wilkommen zum 8Ball")
print("Stelle mir eine Ja/Nein-Frage und ich werde dir antworten.")

while True:
    question=input("\nWas möchtest du Wissen? Wenn du keine frage mehr hast, tippe 'exit' ein.")
    if question.lower()=="exit":
        print("\nBis zum nächsten Mal!")
        break
    print("Hier ist deine Antwort:")
    print("\n", random.choice(antwort))
