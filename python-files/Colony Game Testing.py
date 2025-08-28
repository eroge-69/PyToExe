import random
import sys
import time
import os
import itertools
import threading
import itertools

#-------------------------------------------- Wait Input Start
def wait_input(prompt="\tInput Command: "):
    stop_event = threading.Event()
    result = {"value": None}

    def animate():
        frames = [".   ", "..  ", "... "]
        while not stop_event.is_set():
            for f in frames:
                if stop_event.is_set():
                    break
                sys.stdout.write("\r" + prompt + f)  # redraws same line
                sys.stdout.flush()
                time.sleep(0.5)

    t = threading.Thread(target=animate, daemon=True)
    t.start()
    try:
        # input() will overwrite whatever is there when user types
        result["value"] = input("\r" + prompt)
    finally:
        stop_event.set()
        t.join()
    return result["value"]
#-------------------------------------------- Wait Input End


#-------------------------------------------- Table Printer Start
def print_table(title, rows, delay=0.5):
    num_cols = max(len(row) - 1 for row in rows)
    
    label_w = max(len(str(row[0])) for row in rows)
    col_widths = [
    	max(len(str(row[i+1])) for row in rows if len(row) > i+1)
    	for i in range(num_cols)
    ]
    	
    print("\n\n" + title)
    print("-"*len(title))
    		
    for row in rows:
    	label = row[0]
    	values = row[1:]
    	line = f"{label:<{label_w}}"
    	
    	for i, val in enumerate(values):
    		w = col_widths[i]
    		
    		if isinstance(val, (int, float)):
    			line += f" {val:>{w}}"
    		else:
    			line += f" {str(val):<{w}}"
    			
    	print(line)
    	time.sleep(delay)
#-------------------------------------------- Table Printer End


#-------------------------------------------- Reset Values Start
def reset_game():
    return dict(
        h2=0, o2=0, rat=0, day=0,
        expanding=False, searching=False, mining=False, resting=False, repairing=False, event=False,
        searchingVal=0, gameRunning=True,
        h2in=0, h2out=0, o2in=0, o2out=0, ratin=0, ratout=0,
        iceFound=False, baseDamage=0, hydroponicsSize=1, hydroponicsActingSize=1,
        h2independent=" ", o2independent=" ", ratindependent=" ",
    )
#-------------------------------------------- Reset Values End


#-------------------------------------------- Actual Code Start

state = reset_game()
globals().update(state)

#Storage Values

h2=0
o2=0
rat=0

day=0

searchingVal=0

gameRunning = True

#Situational
iceFound=False
expanding = False
searching = False
mining = False
resting = False
repairing = False
event = False
baseDamage=0
hydroponicsSize=1
hydroponicsActingSize=1

#Input/Output Values

#h2
h2in=0
h2out=0

#o2
o2in=hydroponicsSize
o2out=0

#Rations
ratin=hydroponicsSize
ratout=0


#-------------------------------------------- Difficulty Setting Start

print("Select Difficulty \nEasy \nNormal \nHard\n")

dif = wait_input().strip().lower()

while dif not in ("easy", "normal", "hard"):
	print("Invalid Input. Please Try Again.")
	dif = wait_input().strip().lower()

if dif == "easy":
	print("Difficulty Selected: \"Easy\"")
	h2=5
	o2=50
	rat=50
	
	#h2
	h2in=0
	h2out=0
	h2independent=" "
	
	#o2
	o2in=hydroponicsActingSize
	o2out=5
	o2independent=" "

	#Rations
	ratin=hydroponicsActingSize
	ratout=5
	ratindependent=" "
	

elif dif == "normal":
	print("Difficulty Selected: \"Normal\"")
	h2=3
	o2=50
	rat=30
	
	#h2
	h2in=0
	h2out=0
	h2independent=" "
	
	#o2
	o2in=hydroponicsActingSize
	o2out=5
	o2independent=" "
	
	#Rations
	ratin=hydroponicsActingSize
	ratout=5
	ratindependent=" "
	
	
elif dif == "hard":
	print("Difficulty Selected: \"Hard\"")
	
	hydroponicsSize = 0
	hydroponicsActingSize = 0
	
	h2=3
	o2=30
	rat=20
	
	#h2
	h2in=0
	h2out=0
	h2independent=" "

	#o2
	o2in=hydroponicsActingSize
	o2out=5
	o2independent=" "

	#Rations
	ratin=hydroponicsActingSize
	ratout=5
	ratindependent=" "
	
#-------------------------------------------- Difficulty Setting End

#-------------------------------------------- Intro Interaction Start
print("\n\nWelcome. Patching you through to colony")
time.sleep(1)
print("Connected.")
print("Awaiting Confirmation, please input \"enter\" to connect")

userinput = wait_input().lower()
while userinput != 'enter':
	print("Invalid Input.")
	time.sleep(1)
	print("Please input \"enter\" to access colony systems")
	userinput = wait_input().lower()
	
	
print("Confirmation Recived. Welcome Commander.")

#-------------------------------------------- Intro Interaction End

#-------------------------------------------- Game Start

while gameRunning == True:
	expanding = iceFound = mining = searching = resting = repairing = False

	print("Running System Diagnostics...\n")
	time.sleep(2)
	
	if baseDamage < 1:
		print("Colony Status: OK")
		time.sleep(0.25)
		print("Colony Systems: OK")
	elif baseDamage >= 1:
		print("Colony Status: DAMAGED")
		time.sleep(0.25)
		print("Colony Systems: CRITICAL")
		
	time.sleep(0.25)
	print("Base Damage: ",baseDamage)
	time.sleep(0.25)
	print("Hydroponics Bay Size: ",hydroponicsSize)
	time.sleep(0.25)
	print("Days since arrival: ", day)
	time.sleep(0.25)
	print("Fetching Inventory Information")

	time.sleep(1)

	rows = [
		("Hydrogen: ", h2,"kL"),
		("Oxygen: ",o2,"kL"),
		("Rations: ",rat," Days"),
		]
	print_table("Querying Colony Stores...", rows)

	rows = [
		("Hydrogen In/Out: ", h2in, h2out, h2independent),
		("Oxygen In/Out:", o2in, o2out, o2independent),
		("Rations In/Out:",ratin, ratout, ratindependent),
	]
	print_table("Querying Colony Input/Output...", rows) 

	print("\n\n\n")


#-------------------------------------------- Selection Start
	if iceFound == True and baseDamage > 0:
		rows = [
			("1 - Expand Hydroponics Bay - \nCost: 2 Rations, 2 Oxygen. \nYield: +1 Rations Per Day, +1 O2 Per Day.\n",),
			("2 - Rest. \nCost: Nothing.\n",),
			("3 - Mine Ice - \nCost: 2 Rations. \nYield: +30 Oxygen, +10 Hydrogen.\n",),
			("4 - Repair Base - \nCost: 2 Rations. \nYield: Remove 1 Point of Damage.\n",),
		]
		tasklist=2
	
	elif iceFound == True:
		rows = [
			("1 - Expand Hydroponics Bay - \nCost: 2 Rations, 2 Oxygen. \nYield: +1 Rations Per Day, +1 O2 Per Day.\n",),
			("2 - Rest. \nCost: Nothing.\n",),
			("3 - Mine Ice - \nCost: 2 Rations. \nYield: +30 Oxygen, +10 Hydrogen.\n",),
		]
		
		tasklist=1
		
	elif iceFound == False and baseDamage > 0:
		rows = [
			("1 - Expand Hydroponics Bay - \nCost: 2 Rations, 2 Oxygen. \nYield: +1 Rations Per Day, +1 O2 Per Day.\n",),
			("2 - Rest. \nCost: Nothing.\n",),
			("3 - Search For Ice - 50% Chance of Finding Ice \nCost: 2 Rations, 2 Hydrogen. \nYield: On Success Unlock \"Mine Ice: +30 Oxygen, +10 Hydrogen\".\n",),
			("4 - Repair Base - \nCost: 2 Rations. \nYield: Remove 1 Point of Damage.\n",),
		]
		tasklist=3
		
	else:

		rows = [
			("1 - Expand Hydroponics Bay - \nCost: 2 Rations, 2 Oxygen. \nYield: +1 Rations Per Day, +1 O2 Per Day.\n",),
			("2 - Rest. \nCost: Nothing.\n",),
			("3 - Search For Ice - 50% Chance of Finding Ice \nCost: 2 Rations, 2 Hydrogen. \nYield: On Success Unlock \"Mine Ice: +30 Oxygen, +10 Hydrogen\".\n",),
		]
		tasklist=4

	print_table("Please Choose Operation.", rows)

	userinput = wait_input()
#-------------------------------------------- Selection End



#-------------------------------------------- Selection Action End
	if userinput == "1":
		print("\nCommand Recived. Expanding Hydroponics Bay.")
		expanding=True
	
	elif userinput == "2":
		print("\nCommand Recived. Crew Is Resting.")
		resting=True
	
	else:
		if tasklist == 1:
			if userinput == "3":
				print("\nCommand Recived. Mining Ice.")
				mining=True
		
		elif tasklist == 2:
			if userinput == "3":
				print("\nCommand Recived. Mining Ice.")
				mining=True
			
			if userinput == "4":
				print("\nCommand Recived. Repairing Base Systems.")
				repairing=True
				
		elif tasklist == 3:
			if userinput == "3":
				print("\nCommand Recived. Deploying Rover To Search For Ice.")
				searching=True
			elif userinput == "4":
				print("\nCommand Recived. Repairing Base Systems.")
				repairing = True
				
		elif tasklist == 4:
			if userinput == "3":
				print("\nCommand Recived. Deploying Rover To Search For Ice.")
				searching=True
	#-------------------------------------------- Selection Action End



	#-------------------------------------------- Set Income Start
	
	#-------------------------------------------- Ice Handling
	if searching == True:
		searchingVal = random.randint(1,2)
		
		time.sleep(0.5)
		
		if searchingVal == 2:
			print("\nSEARCH UNSUCCESSFUL. Returning to Base.")
			iceFound = False
			
		elif searchingVal == 1:
			print("\nSEARCH SUCCESSFUL. Returning to Base.")
			iceFound = True
		
		else:
			print("\nIce Search Error. Invalid Random.")
	
	#-------------------------------------------- Hydroponics Handling
	if expanding == True:
		hydroponicsSize = hydroponicsSize + 1
		hydroponicsActingSize = hydroponicsActingSize + 1
		
	elif expanding == False:
		hydroponicsSize = hydroponicsSize
		hydroponicsActingSize = hydroponicsActingSize
		
	else:
		print("\nHydroponics Handling Error")
		continue
		
	#-------------------------------------------- Oxygen Handling	
	if mining == True:
		o2 = o2 + 30
	elif mining == False:
		o2 = o2
	else:
		print("\nOxygen Handling Error (Mining)")
		continue
	
	o2in = hydroponicsActingSize
	
	o2 = o2 - (o2out - o2in)
	
	if o2in > o2out:
		o2independent = "Self Sufficient"
	
	elif o2in <= o2out:
		o2independent = " "

	else:
		print("\nOxygen Handling Error (Self Sufficient)")
		continue
		
	#-------------------------------------------- Ration Handling
	
	ratin = hydroponicsActingSize	
		
	rat = rat - (ratout - ratin)
	
	if ratin > ratout:
		ratindependent = "Self Sufficient"
		
	elif ratin <= ratout: 
		ratindependent = " "
	
	else:
		print("\nRation Handling Error (Self Sufficient)")
		continue
	
	#-------------------------------------------- Hydrogen Handling	
	if mining == True:
		h2 = h2 + 10
		
	elif mining == False:
		h2 = h2
		
	else:
		print("\nHydrogen Handling Error (Mining)")
		continue
		
	#-------------------------------------------- Hydrogen Handling	

	time.sleep(2)
	print("\n\n")	
	
	#-------------------------------------------- Event Creation Start	
	
	event_roll = random.randint(1,10)
	
	if event_roll in (1, 2):
		print("\nAsteroid Impact Nearby! Fragments Incoming!")
		time.sleep(1)
		print("\nFragments Missed Us. No Base Damage")
		
	elif event_roll in (3, 4):
		print("\nTremors Detected. Base Systems Undamaged.")
		
	elif event_roll in (5, 6):
		print("\nSolar Flare Incoming. Systems Shutting Down.")
		time.sleep(1)
		print("\nSolar Flare Subsided. Systems Rebooted and Undamaged.")
		
	elif event_roll in (7, 8):
		print("\nNo Events to Report. Colony Out.")
		
	elif event_roll == 9:
		print("\nAsteroid Impact Nearby! Fragments Incoming!")
		time.sleep(1)
		print("\nMultiple Impacts! Base Damaged.")
		baseDamage += 1
		
	elif event_roll == 10:
		print("\nSolar Flare Incoming. Systems Shutting Down.")
		time.sleep(1)
		
		print("\nSolar...", end="", flush=True)
		time.sleep(0.25)

		print(" F... lare...", end="", flush=True)
		time.sleep(0.25)

		print(" Subsided.", end="", flush=True)
		time.sleep(0.25)

		print(" Systems Reboot...", end="", flush=True)
		time.sleep(0.25)

		print(" Base Systems Damaged.")
		baseDamage += 1
		
	else:
		print("Event Creation Error.")
	 
	
	#-------------------------------------------- Event Creation End	
	
	time.sleep(1)
	
	#-------------------------------------------- Base Damage Use Start	
	if baseDamage > 0:
		hydroponicsActingSize = hydroponicsSize
		hydroponicsActingSize = max(0, hydroponicsSize - baseDamage)
		
	elif baseDamage == 0:
		hydroponicsActingSize = hydroponicsSize
	
	else:
		print("Base Damage Handling Error")
	
	#-------------------------------------------- Base Damage Use Start
	
				
				
	#-------------------------------------------- Loss Condition Start
	
	if rat < 0 or o2 < 0:
		if rat < 0:
			print("GAME OVER. Colony Starved.")
		
	
		if o2 < 0:
			print("GAME OVER. Colony Ran Out Of Oxygen.")
		
		print("Would you like to 'Reset Game' or 'End Game'?")
		userinput = wait_input().lower().strip()
	
		while userinput not in ("reset", "resetgame", "end", "endgame"):
			print("Invalid Input. Check your spelling. \nAcceptible Inputs: Reset, Reset Game, End, End Game. \nSystem is NOT case or space sensitive.")
			userinput = wait_input().lower().strip()
	
		if userinput in ("reset", "resetgame"):
			print("Resetting Game.")
			state = reset_game()
			globals().update(state)
			continue
			
		elif userinput in ("end", "endgame"):
			print("Ending Game.")
			gameRunning = False
							
	#-------------------------------------------- Victory Condition Start
	if ratindependent == "Self Sufficient" and o2independent == "Self Sufficient":
		print("Running System Diagnostics...\n")
		time.sleep(2)
	
		if baseDamage < 1:
			print("Colony Status: OK")
			time.sleep(0.25)
			print("Colony Systems: OK")
		elif baseDamage >= 1:
			print("Colony Status: DAMAGED")
			time.sleep(0.25)
			print("Colony Systems: CRITICAL")
		
		time.sleep(0.25)
		print("Base Damage: ",baseDamage)
		time.sleep(0.25)
		print("Hydroponics Bay Size: ",hydroponicsSize)
		time.sleep(0.25)
		print("Days since arrival: ", day)
		time.sleep(0.25)
		print("Fetching Inventory Information")
	
		time.sleep(1)

		rows = [
			("Hydrogen: ", h2,"kL"),
			("Oxygen: ",o2,"kL"),
			("Rations: ",rat," Days"),
			]
		print_table("Querying Colony Stores...", rows)

		rows = [
			("Hydrogen In/Out: ", h2in, h2out),
			("Oxygen In/Out:", o2in, o2out, o2independent),
			("Rations In/Out:",ratin, ratout, ratindependent),
		]
		print_table("Querying Colony Input/Output...", rows) 
		
		print("Colony Is Self Sufficient!")
		print("Excellent Work Commander.\n")
		userinput = wait_input("Would you like to 'Continue', 'Reset', or 'Enjoy Victory'?").lower().strip()
		
		while userinput not in ("continue", "reset", "enjoyvictory"):
			print("Invalid Input. Please check your spelling.\nAcceptable Inputs: 'Continue', 'Reset', 'Enjoy Victory'.\nSystem is NOT case or space sensitive")
			userinput = wait_input().lower().strip()	
				
		if userinput == "continue":
			print("Understood! Continuing.")
			gameRunning = True
			
		elif userinput == "reset":
			print("Understood. Resetting Game.")
			state = reset_game()
			globals().update(state)
			continue
			
		
		elif userinput == "enjoyvictory":
			print("Congratulations Commander.")
			gameRunning = False
		
		else:
			print("Victory Condition Error.")

	#-------------------------------------------- Victory Condition End
	time.sleep(1)
	print("Please enter 'enter' once you are ready to move to the next day.")
	userinput = wait_input().lower().strip()
	
	while userinput != "enter":
		print("Invalid Input. Please input 'enter'.\nSystem is not case or space sensitive.")
		wait_input().lower().strip()
	
	time.sleep(1)	
	print("Moving to next day.")
	time.sleep(2)
	
	day += 1

