import random


def main():
    keep_running = "y"
    while keep_running == "y":
        try:
            message()
            choice = int(input("Enter from the above options: "))
            if choice == 1:
                six_out_of_fourtynine()
            elif choice == 2:
                five_out_of_thirtysix()
            elif choice == 3:
                seven_out_of_fifty()
            else:
                print("Invalid choice. Please try again")
        except Exception as error:
            print(f"An error occured: {error}")
        keep_running = input("Do you want to create random numbers again? press(y/n): ").strip().lower()


def message():
    print("\nWelcome to the lotto prediction system!")
    print("Select a lotto type")
    print("1. 6/49")
    print("2. 3/26")
    print("3. 7/50")


def six_out_of_fourtynine():
    my_list = []
    for i in range(6):
        numbers = random.randint(1, 49)
        my_list.append(numbers)
    print("\nHere is the list of 6 possible numbers from 1 up to 49")
    print(my_list)


def five_out_of_thirtysix():
    my_list2 = []
    for i in range(3):
        numbers2 = random.randint(1, 26)
        my_list2.append(numbers2)
    print("\nHere is the list of 3 possible numbers from 1 up to 26")
    print(my_list2)


def seven_out_of_fifty():
    my_list3 = []
    for i in range(7):
        numbers3 = random.randint(1, 50)
        my_list3.append(numbers3)
    print("\nHere is the list of 7 possible numbers from 1 up to 50")
    print(my_list3)


if __name__ == "__main__":
    main()
