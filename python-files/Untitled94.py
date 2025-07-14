#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import random

# Input team name, batsman names, and initial match details
team_name = input("Write team name: ")
print(" -----------------------------------")
batsman1 = input("Enter the name of Batsman 1: 🏏 ")
print("-------------------------------------")
batsman2 = input("Enter the name of Batsman 2: 🏏 ") 
print("-------------------------------------")
total_runs = int(input("Enter initial runs: 🥎 ")) 
print("-------------------------------------")
total_balls = int(input("Enter total number of balls faced so far: ")) 
print("-------------------------------------")

# Audience reactions
audience_reactions = [
    "The crowd goes wild! 🎉",
    "What a brilliant shot! 👏",
    "Boo! Not good enough! 👎",
    "The crowd is on their feet! 🏟️",
    "A massive six! Amazing! 🌟",
    "Ooooh! Close call! 😱",
    "The batsman is looking confident! 💪",
    "Oh no! What a miss! 😢",
    "Wicket! Silence falls over the crowd... 😮"
]

# Start the match
x = 1  # Control for the while loop
while x > 0:
    # Calculate overs
    overs = total_balls // 6
    balls_in_over = total_balls % 6

    # Display score
    print("_______________________________________________________")
    print("        ---🏆 CRICKET MATCH SCORE 🏆---")
    print("_______________________________________________________")
    print("                  TEAM: ", team_name)
    print("  🏏 Batsman 1: ", batsman1, "         🏏 Batsman 2: ", batsman2)
    print("_______________________________________________________")
    print("Run: ", total_runs, "    Overs: ", overs, ".", balls_in_over, "   Balls: ", total_balls)
    print("_______________________________________________________")

    # Ask user if they want to continue or stop
    x = int(input("Enter 1 to continue or 0 to stop: ")) 
    print("_______________________________________________________")
    
    # If user wants to continue, update the total runs and balls
    if x > 0:
        runs_scored = int(input("Enter runs scored in the last ball (or enter -1 for Wicket): "))
        
        if runs_scored == -1:  # Handle wicket scenario
            print(f"WICKET! {batsman1 if total_balls % 2 == 0 else batsman2} is out! Silence falls over the crowd... 😮")
            print(random.choice(audience_reactions[-1:]))  # Response for a wicket
        else:
            total_runs += runs_scored
            total_balls += 1
            
            # Check if the runs are odd, change the batsman
            if runs_scored % 2 != 0:
                batsman1, batsman2 = batsman2, batsman1  # Swap the batsmen

            # Simulate audience response based on runs scored
            if runs_scored > 0:
                print(random.choice(audience_reactions[:5]))  # Positive reactions for runs
            elif runs_scored == 0:
                print(random.choice(audience_reactions[5:]))  # Neutral reactions for dot balls

    print("_______________________________________________________")

print("Match Ended!")


# In[ ]:


q1="""Who invented Python?
a. Steve Jobs
b. Guido van Rossum
c. Bill Gates
d. Tim Cook"""
q2="""In which year was Python Invented?
a. 1995
b. 1991
c. 1899
d. 1998"""
q3="""Is Pyhton case sensitive when dealing with Identifiers?
a. Yes
b. No
c. Machine Dependent
d. None of the above"""
q4="""Which of the following is the correct extension of the Python File?
a. .python
b. .py
c. .pl
d. .p"""
q5="""Is Python code compiled or interpreted?
a. Both Compiled and interpreted
b. Neither Compiled nor Interpreted
c. Only Compiled
d. Only Interpreted"""

questions = {q1:"Guido van Rossum",q2:"1991",q3:"Yes",q4:".py",q5:"Only Interpreted"}
print("---- PYTHON BASED QUIZ ----\n")
name=input("Enter your name: ")
print("******************************************")
print("Hello",name,"Welcome to the PYTHON BASED QUIZ desgined by Saad A.")
score=0
for i in questions:
    print(i)
    ans=input("Enter the answer: ")
    if ans==questions[i]:
        print("Correct Answer, you got 1 POINT HURRAY!!")
        print("******************************************")
        score=score+1
    else:
        print("Wrong Answer, you lost 1 POINT!!")
        print("***************************************************************")
        score=score-1
print("Final Score is:",score)
print("****************************************************")
print("\n")
print("----- THANKS FOR PLAYING -----")


# In[ ]:




