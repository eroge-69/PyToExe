

from datetime import datetime
import random

print("Hello! I am Frutech AI. How can I help you today?")

while True:
    user_input = input("You: ").lower()

    if "hello" in user_input or "hi" in user_input:
        print("Frutech AI: Hello there! How are you?")

    elif "how are you" in user_input:
        print("Frutech AI: I am just a bunch of code, but I am doing great! How about you?")

    elif "bye" in user_input or "goodbye" in user_input:
        print("Frutech AI: Goodbye! Have a great day!")
        break

    elif "your name" in user_input:
        print("Frutech AI: My name is Frutech AI. Nice to meet you!")

    elif "help" in user_input:
        print("Frutech AI: Sure! I can answer simple questions. Try saying hello, ask my name, time, date, joke, motivation, help, how are you or say goodbye!")

    
    elif "time" in user_input:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Frutech AI: The current time is {current_time}.")

    
    elif "date" in user_input:
        current_date = datetime.now().strftime("%B %d, %Y")
        print(f"Frutech AI: Today's date is {current_date}.")

    
    elif "joke" in user_input:
        jokes = [
            "Why did the computer go to the doctor? Because it had a virus!",
            "Why don't robots ever panic? Because they have nerves of steel.",
            "Why did the AI cross the road? To optimize the route!"
        ]
        print(f"Frutech AI: {random.choice(jokes)}")

    
    elif "motivate" in user_input or "motivation" in user_input:
        print("Frutech AI: Believe in yourself. Every expert was once a beginner!")

    
    else:
        print("Frutech AI: I'm not sure how to respond to that. Can you try asking something else?")
