import random

seatplan = [i for i in range(1,34)]

def display(seatplan):
    k = 0
    empty = 0
    for j in range(5):
        for i in range(7):

            print("------", end=" ")
            if i == 0 or i == 2 or i == 4:
                print(end="   ")

        print()
        
        for i in range(7):
            buffer = "  "
            currnetStudent = seatplan[k - empty]

            if currnetStudent >= 10:
                buffer = " "
            if k == 0 or k == 7: 
                print("|    |", end=" ")
                empty += 1
            else:
                print("| "+str(currnetStudent)+buffer+"|", end=" ")
            k += 1
            if i == 0 or i == 2 or i == 4:
                print(end="   ")
        print()
        for i in range(7):
            print("------", end=" ")
            if i == 0 or i == 2 or i == 4:
                print(end="   ")
        print()


    print("             -----------------------")
    print("             |      Blackboard     |")
    print("             -----------------------")
random.shuffle(seatplan)
display(seatplan)
