import random
import time


leaderboard = {}


def loop():
    return input("Do you want to repeat? (Y/n) ").upper().strip()

def average_and_total(total_time, n):
    print(f"You took {total_time} seconds to answer {n} questions")
    print(f"Average time: {total_time / n} seconds")


def dict_to_list(sorted_leatherboard):
    return list(sorted_leatherboard.keys())

def ordinal_indicator(rank):
    if rank == 11:
        return "th"

    elif rank == 1 or rank % 10 == 1:
        return "st"

    elif rank == 2 or rank % 10 == 2:
        return "nd"

    elif rank == 3 or rank % 10 == 3:
        return "rd"

    else:
        return "th"

def leaderboard_updater(username, percent):
    if username in leaderboard:
        if leaderboard[username] < percent:
            leaderboard[username] = percent

    else:
        leaderboard[username] = percent

    sorted_leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[1]))

    print(f"                     Leaderboard                       ")
    print(f"-------------------------------------------------------")
    print(f"    Username                             Percentage    ")
    print()
    for user, score in sorted_leaderboard.items():
        print(f"    {user}:                             {score:.2f}% ")
    print(f"-------------------------------------------------------")
    leaderboard_name_list = dict_to_list(sorted_leaderboard)
    rank = leaderboard_name_list.index(username) + 1
    number_suffix = ordinal_indicator(rank)
    print(f"You are ranked {rank}{number_suffix}")
    print()


def username_input():
    username = input("Enter Username: ")
    return username


def ProcessResults(number_of_correct_answer, n, username):
    print(f"-------------------------------------------------------")
    print(f"                        RESULT                         ")
    print()
    print(f"                      {username}                       ")
    print(f"-------------------------------------------------------")
    print(f"You got {number_of_correct_answer} out of {n} questions")
    print(f"Your score    :  {number_of_correct_answer / n * 100:.2f}%")
    print(f"-------------------------------------------------------")

    return(number_of_correct_answer / n * 100)

def check_answer(user_input_answer, answer):
    if user_input_answer == answer:
        return True

    else:
        return False


def TestOnSums(n):
    number_of_correct_answer = 0
    total_time = 0
    for x in range(n):
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        answer = num1 + num2
        while True:
            try:
                start_timer = time.time()
                user_input_answer = int(input(f"{num1} + {num2} = ?: "))
                marker = check_answer(user_input_answer, answer)
                if marker:
                    print(f"{num1} + {num2} = {answer}")
                    print(f"CORRECT!!!")
                    number_of_correct_answer += 1
                    end_timer = time.time()
                    print(f"You took {end_timer - start_timer:.2f} seconds")
                    total_time =+ end_timer - start_timer
                    break


                else:
                    print(f"{num1} + {num2} = {user_input_answer} WRONG!!!")
                    print(f"The correct answer is: {num1} + {num2} = {answer}")
                    end_timer = time.time()
                    total_time =+ end_timer - start_timer
                    break

            except ValueError:
                print(f"Please enter a number, try again")

    average_and_total(total_time, n)
    return(number_of_correct_answer)


def user_input_questions():
    while True:
        try:
            number_of_questions = int(input(f"Please enter the number of questions you wish to answer: "))
            if number_of_questions < 1:
                raise ValueError

            return number_of_questions

        except ValueError:
            print(f"Please enter a valid integer, try again")
            continue


def main():
    while True:
        username = username_input()
        n = user_input_questions()
        number_of_correct_answer = TestOnSums(n)
        percent = ProcessResults(number_of_correct_answer, n, username)
        ranking = leaderboard_updater(username, percent)
        repeat = loop()
        if repeat == "Y":
            continue

        elif repeat == "N":
            break

        else:
            print(f"User entered an invalid prompt, defaulting to yes")
            continue


if __name__ == "__main__":
    main()