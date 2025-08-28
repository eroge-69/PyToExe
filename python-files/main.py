while True:
    q1 = input("Do you want to a. Add a new student or b. Search for a student? (enter a or b) ")

    if q1.lower() == "a":
        student = input("Enter Student Full Name: ")
        agreement = input("Do they consent to the Marketing Agreement? (enter y or n): ")
        with open("MarketingAgreement.txt", 'a') as file:  # open in append mode only when adding
            file.write(student + ": " + agreement + "\n")

    elif q1.lower() == "b":
        student = input("Enter Student Full Name: ")
        with open("MarketingAgreement.txt", 'r') as file:  # open in read mode when searching
            found = False
            for line in file:
                curr = line.strip().split(":")
                if curr[0] == student:
                    print(curr[1].strip())
                    found = True
                    break
            if not found:
                print("Student not found.")

    q2 = input("Run again (y or n)? ")
    if q2.lower() != "y":
        break
