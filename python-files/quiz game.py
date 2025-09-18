def main_menu():
    """
    Displays the main menu and handles user input.
    """
    while True:
        print("\n--- Main Menu ---")
        print("1. Play")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            option_a()
        elif choice == '2':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 or 2.")

def option_a():
    """
    Function for Option A.
    """
    print("\nYou have decided to play. Choose your difficulty.")
    difficultymenu()

def difficultymenu():
    while True:
        print("\n-----Difficulty Menu--------")
        print("1. Hardcore")
        print("2. Hard")
        print("3. Medium")
        print("4. Easy")
        
        difficulty_choice = input("Enter your difficulty choice: ")
        
        if difficulty_choice == '1':
            print("You've chosen Hardcore.")
            option_b()
            break
        elif difficulty_choice == '2':
            print("You've chosen Hard.")
            option_c()
            break
        elif difficulty_choice == '3':
            print("You've chosen Medium.")
            option_d()
            break
        elif difficulty_choice == '4':
            print("You've chosen Easy.")
            option_e()
            break
        else:
            print("Invalid choice. Please choose a number from 1 to 4.")

def are_you_sure_menu():
    """
    Asks the user to confirm their choice and handles input.
    """
    while True:
        print("\nAre you sure you want to continue?")
        print("1. Continue")
        print("2. Exit")
        
        sure_choice = input("Enter your choice: ")
        
        if sure_choice == '1':
            print("\nProceeding...")
            return True
        elif sure_choice == '2':
            print("\nReturning to main menu.")
            return False
        else:
            print("Invalid choice. Please enter 1 or 2.")

def run_hardcore_quiz():
    """
    Runs the Hardcore quiz with all questions and displays the score.
    """
    questions = [
        {
            "question": "What is the fundamental difference between a fermion and a boson?",
            "options": "a) Fermions carry a charge, while bosons are neutral.\nb) Fermions obey the Pauli Exclusion Principle, while bosons do not.\nc) Fermions are elementary particles, while bosons are composite.\nd) Fermions have integer spin, while bosons have half-integer spin.",
            "answer": "b",
            "explanation": "Fermions obey the Pauli Exclusion Principle, while bosons do not. The Pauli Exclusion Principle states that no two identical fermions can occupy the same quantum state simultaneously, which is why fermions are known as matter particles. Bosons, the force-carrying particles, can occupy the same quantum state."
        },
        {
            "question": "In the context of quantum computing, what does 'superposition' mean?",
            "options": "a) A qubit can be either a 0 or a 1 at any given time.\nb) A qubit is a classical bit that is faster than a regular bit.\nc) A qubit can exist as a combination of 0 and 1 simultaneously until measured.\nd) A qubit is a particle that has been entangled with another qubit.",
            "answer": "c",
            "explanation": "This unique property of superposition allows a quantum computer to perform multiple calculations at once."
        },
        {
            "question": "What is the main reason for the exceptionally high melting point of diamond?",
            "options": "a) The strong ionic bonds between carbon atoms.\nb) The formation of a metallic lattice structure.\nc) The strong covalent network bonds in a tetrahedral structure.\nd) The presence of delocalized electrons.",
            "answer": "c",
            "explanation": "The strong covalent network bonds in a tetrahedral structure. Diamond is an allotrope of carbon where each carbon atom is bonded to four others in a rigid, three-dimensional network, requiring a massive amount of energy to break."
        },
        {
            "question": "What is a singularity in the context of a black hole?",
            "options": "a) A point in spacetime where the gravitational pull is zero.\nb) The outer boundary of a black hole's event horizon.\nc) A point of infinite density and zero volume at the center of a black hole.\nd) A region where light can temporarily escape the black hole's gravity.",
            "answer": "c",
            "explanation": "A point of infinite density and zero volume at the center of a black hole. According to general relativity, all the mass of a black hole is compressed into this one-dimensional point."
        },
        {
            "question": "What is the Hubble Constant (H0) used to measure in cosmology?",
            "options": "a) The speed of light in a vacuum.\nb) The rate at which the universe is expanding.\nc) The age of the solar system.\nd) The distance to a celestial body.",
            "answer": "b",
            "explanation": "The Hubble Constant describes how fast an object is moving away from us due to the expansion of the universe, with its speed proportional to its distance from us."
        }
    ]

    score = 0
    total_questions = len(questions)

    for q in questions:
        print("\n" + q["question"])
        print(q["options"])
        
        user_answer = input("Your answer: ").strip().lower()

        if user_answer == q["answer"]:
            print("Correct! ✅")
            score += 1
        else:
            print("Incorrect. ❌")

        print("The correct answer is: " + q["answer"] + ") " + q["explanation"])
        input("\nPress Enter to continue to the next question...")

    print("\n--- Quiz Finished! ---")
    print(f"You got {score} out of {total_questions} questions correct.")
    
    percentage = 0
    if total_questions > 0:
        percentage = (score / total_questions) * 100
        print(f"Your score is: {percentage:.2f}%")
    
    print("\nReturning to main menu.")

def run_medium_quiz():
    """
    Runs the Medium quiz and allows the user to continue to Hard mode if they pass.
    """
    questions = [
        {
            "question": "What is the process by which a solid turns directly into a gas, without passing through a liquid phase?",
            "options": "a) Condensation\nb) Evaporation\nc) Sublimation\nd) Freezing",
            "answer": "c",
            "explanation": "Sublimation. An example is dry ice (solid carbon dioxide) turning into a gas at room temperature."
        },
        {
            "question": "Which part of the human eye is responsible for focusing light onto the retina?",
            "options": "a) Iris\nb) Cornea\nc) Pupil\nd) Lens",
            "answer": "d",
            "explanation": "The lens changes shape to focus light on the retina, allowing for clear vision at different distances."
        },
        {
            "question": "What does the term 'pH neutral' mean in chemistry?",
            "options": "a) The solution has a pH of 0.\nb) The solution is highly acidic.\nc) The solution has a pH of 7.\nd) The solution is highly basic.",
            "answer": "c",
            "explanation": "A pH of 7 indicates that the solution is neither acidic nor basic."
        },
        {
            "question": "What is the main characteristic of a dwarf planet that distinguishes it from a regular planet?",
            "options": "a) It has a non-spherical shape.\nb) It orbits a different star.\nc) It has not cleared its orbital neighborhood of other objects.\nd) It is smaller than Earth's moon.",
            "answer": "c",
            "explanation": "This is the official definition that distinguishes dwarf planets like Pluto from the eight major planets."
        },
        {
            "question": "What type of energy is stored in an object due to its position in a gravitational field?",
            "options": "a) Kinetic energy\nb) Thermal energy\nc) Chemical energy\nd) Gravitational potential energy",
            "answer": "d",
            "explanation": "Gravitational potential energy. An object held high above the ground has more potential energy than one on the ground because of its position."
        }
    ]

    score = 0
    total_questions = len(questions)

    for q in questions:
        print("\n" + q["question"])
        print(q["options"])
        
        user_answer = input("Your answer: ").strip().lower()

        if user_answer == q["answer"]:
            print("Correct! ✅")
            score += 1
        else:
            print("Incorrect. ❌")

        print("The correct answer is: " + q["answer"] + ") " + q["explanation"])
        input("\nPress Enter to continue to the next question...")

    print("\n--- Quiz Finished! ---")
    print(f"You got {score} out of {total_questions} questions correct.")
    
    percentage = 0
    if total_questions > 0:
        percentage = (score / total_questions) * 100
        print(f"Your score is: {percentage:.2f}%")
    
    if percentage >= 50:
        print("\nCongratulations! You've passed the Medium mode with a score of 50% or higher.")
        continue_choice = input("Would you like to continue to Hard mode? (yes/no): ").strip().lower()
        if continue_choice == 'yes':
            print("\nStarting Hard mode...")
            option_c()
            return # This is the crucial line to add
        else:
            print("\nReturning to main menu.")
    else:
        print("\nYour score is below 50%. You need to pass the Medium mode to proceed.")
        print("Returning to main menu.")


def run_hard_quiz():
    """
    Runs the Hard quiz and allows the user to continue to Hardcore mode if they pass.
    """
    questions = [
        {
            "question": "What is the fundamental difference between a fermion and a boson?",
            "options": "a) Fermions carry a charge, while bosons are neutral.\nb) Fermions obey the Pauli Exclusion Principle, while bosons do not.\nc) Fermions are elementary particles, while bosons are composite.\nd) Fermions have integer spin, while bosons have half-integer spin.",
            "answer": "b",
            "explanation": "Fermions obey the Pauli Exclusion Principle, while bosons do not. The Pauli Exclusion Principle states that no two identical fermions can occupy the same quantum state simultaneously, which is why fermions are known as matter particles. Bosons, the force-carrying particles, can occupy the same quantum state."
        },
        {
            "question": "In the context of quantum computing, what does 'superposition' mean?",
            "options": "a) A qubit can be either a 0 or a 1 at any given time.\nb) A qubit is a classical bit that is faster than a regular bit.\nc) A qubit can exist as a combination of 0 and 1 simultaneously until measured.\nd) A qubit is a particle that has been entangled with another qubit.",
            "answer": "c",
            "explanation": "This unique property of superposition allows a quantum computer to perform multiple calculations at once."
        },
        {
            "question": "What is the main reason for the exceptionally high melting point of diamond?",
            "options": "a) The strong ionic bonds between carbon atoms.\nb) The formation of a metallic lattice structure.\nc) The strong covalent network bonds in a tetrahedral structure.\nd) The presence of delocalized electrons.",
            "answer": "c",
            "explanation": "The strong covalent network bonds in a tetrahedral structure. Diamond is an allotrope of carbon where each carbon atom is bonded to four others in a rigid, three-dimensional network, requiring a massive amount of energy to break."
        },
        {
            "question": "What is a singularity in the context of a black hole?",
            "options": "a) A point in spacetime where the gravitational pull is zero.\nb) The outer boundary of a black hole's event horizon.\nc) A point of infinite density and zero volume at the center of a black hole.\nd) A region where light can temporarily escape the black hole's gravity.",
            "answer": "c",
            "explanation": "A point of infinite density and zero volume at the center of a black hole. According to general relativity, all the mass of a black hole is compressed into this one-dimensional point."
        },
        {
            "question": "What is the Hubble Constant (H0) used to measure in cosmology?",
            "options": "a) The speed of light in a vacuum.\nb) The rate at which the universe is expanding.\nc) The age of the solar system.\nd) The distance to a celestial body.",
            "answer": "b",
            "explanation": "The Hubble Constant describes how fast an object is moving away from us due to the expansion of the universe, with its speed proportional to its distance from us."
        }
    ]

    score = 0
    total_questions = len(questions)

    for q in questions:
        print("\n" + q["question"])
        print(q["options"])
        
        user_answer = input("Your answer: ").strip().lower()

        if user_answer == q["answer"]:
            print("Correct! ✅")
            score += 1
        else:
            print("Incorrect. ❌")

        print("The correct answer is: " + q["answer"] + ") " + q["explanation"])
        input("\nPress Enter to continue to the next question...")

    print("\n--- Quiz Finished! ---")
    print(f"You got {score} out of {total_questions} questions correct.")
    
    percentage = 0
    if total_questions > 0:
        percentage = (score / total_questions) * 100
        print(f"Your score is: {percentage:.2f}%")

    if percentage >= 50:
        print("\nCongratulations! You've passed the Hard mode with a score of 50% or higher.")
        continue_choice = input("Would you like to continue to Hardcore mode? (yes/no): ").strip().lower()
        if continue_choice == 'yes':
            print("\nStarting Hardcore mode...")
            option_b()
            return # This is the crucial line to add
        else:
            print("\nReturning to main menu.")
    else:
        print("\nYour score is below 50%. You need to pass the Hard mode to proceed.")
        print("Returning to main menu.")

def run_easy_quiz():
    """
    Runs the Easy quiz and allows the user to continue to Medium mode if they pass.
    """
    questions = [
        {
            "question": "Which planet is known as the \"Red Planet\"?",
            "options": "a) Jupiter\nb) Mars\nc) Venus\nd) Neptune",
            "answer": "b",
            "explanation": "Mars. Its reddish appearance is due to iron oxide (rust) on its surface."
        },
        {
            "question": "What is the chemical symbol for water?",
            "options": "a) O2\nb) CO2\nc) H2O\nd) NaCl",
            "answer": "c",
            "explanation": "H2O. It's composed of two hydrogen atoms and one oxygen atom."
        },
        {
            "question": "What's the process by which plants make their own food?",
            "options": "a) Respiration\nb) Transpiration\nc) Photosynthesis\nd) Germination",
            "answer": "c",
            "explanation": "Photosynthesis. Plants use sunlight, water, and carbon dioxide to create energy."
        },
        {
            "question": "What force keeps us on the ground and objects from floating away?",
            "options": "a) Friction\nb) Gravity\nc) Magnetism\nd) Buoyancy",
            "answer": "b",
            "explanation": "Gravity. It's the force that attracts a body toward the center of the earth."
        },
        {
            "question": "What's the boiling point of water in Celsius?",
            "options": "a) 0°C\nb) 50°C\nc) 100°C\nd) 212°C",
            "answer": "c",
            "explanation": "100°C. Water boils and turns into steam at this temperature at sea level."
        }
    ]

    score = 0
    total_questions = len(questions)

    for q in questions:
        print("\n" + q["question"])
        print(q["options"])
        
        user_answer = input("Your answer: ").strip().lower()

        if user_answer == q["answer"]:
            print("Correct! ✅")
            score += 1
        else:
            print("Incorrect. ❌")

        print("The correct answer is: " + q["answer"] + ") " + q["explanation"])
        input("\nPress Enter to continue to the next question...")

    print("\n--- Quiz Finished! ---")
    print(f"You got {score} out of {total_questions} questions correct.")
    
    percentage = 0
    if total_questions > 0:
        percentage = (score / total_questions) * 100
        print(f"Your score is: {percentage:.2f}%")
    
    if percentage >= 50:
        print("\nCongratulations! You've passed the Easy mode with a score of 50% or higher.")
        continue_choice = input("Would you like to continue to Medium mode? (yes/no): ").strip().lower()
        if continue_choice == 'yes':
            print("\nStarting Medium mode...")
            option_d()
            return # This is the crucial line to add
        else:
            print("\nReturning to main menu.")
    else:
        print("\nYour score is below 50%. You need to pass the Easy mode to proceed.")
        print("Returning to main menu.")

def option_b():
    print("\nSomebody wants a challenge, huh?")
    if are_you_sure_menu():
        run_hardcore_quiz()

def option_c():
    print("\nToo scared to take Hardcore, huh? Anyway...")
    if are_you_sure_menu():
        run_hard_quiz()

def option_d():
    print("\nMedium, huh? Alright...")
    if are_you_sure_menu():
        run_medium_quiz()

def option_e():
    print("\nHaha, Dumbo! Here are your easy questions.")
    if are_you_sure_menu():
        run_easy_quiz()

# This is crucial for the program to run.
if __name__ == "__main__":
    main_menu()
