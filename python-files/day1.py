import random
Ur_choice =int(input ("chosse between 0 for rock 1 fo paper 2 for scissors: "))
if Ur_choice ==0:
    print("u r choice ")
    print("""
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
""")
elif Ur_choice ==1:
    print("u r choice")
    print("""
     _______
---'    ____)____
           ______)
          _______)
         _______)
---.__________)
""")
elif Ur_choice ==2:
    print("u r choice ")
    print("""
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
""")
    
choice = ["rock", "paper", "scissors"]
TheChoice = random.choice(choice)
print("PC is choice "+TheChoice)
if TheChoice=="rock":
   print("""
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
""")
elif TheChoice=="paper":
    print("""
     _______
---'    ____)____
           ______)
          _______)
         _______)
---.__________)
""")
elif TheChoice=="scissors":
    print("""
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
""")

if Ur_choice==0 and TheChoice=="rock":
    print("it is a draw")
elif Ur_choice==1 and TheChoice=="paper":
    print("it is a draw")
elif Ur_choice==2 and TheChoice=="scissors":
    print("it is a draw")
elif Ur_choice==0 and TheChoice=="scissors":
    print("u win")
elif Ur_choice==1 and TheChoice=="rock":
    print("u win")
elif Ur_choice==2 and TheChoice=="paper":
    print("u win") 
elif Ur_choice==2 and TheChoice=="rock":
    print("u lost")