#!/usr/local/bin/python3
from itertools import permutations
import pickle
import os.path as thefile
if thefile.isfile("allrelicperms.text"):
	print("File found")
else:
	print("Creating relic permutation file")
	counter = 0
	prepermslist = [[0],[1],[2],[3]]
	for x in range(4):
		biprepermslist = []
		for y in prepermslist:
			for z in range(4):
				w=list(i for i in y)
				w.append(z)
				biprepermslist.append(list(i for i in w))
			prepermslist = list(i for i in biprepermslist)
		if x == 2:
			genericfourperms=list(i for i in prepermslist)
	genericfiveperms=list(i for i in prepermslist)
	allfiveperms = []
	for perm in genericfiveperms:
		laststat = [[0,0,0,0]]
		for stat in perm:
			bufferlist = []
			for x in range(3):
				for thing in laststat:
					thing[stat] += 1
					bufferlist.append(list(i for i in thing))
			laststat = list(i for i in bufferlist)
			print(laststat)
		allfiveperms.extend(list(i for i in laststat))
	allfourperms = []
	for perm in genericfourperms:
		laststat = [[0,0,0,0]]
		for stat in perm:
			bufferlist = []
			for x in range(3):
				for thing in laststat:
					thing[stat] += 1
					bufferlist.append(list(i for i in thing))
			laststat = list(i for i in bufferlist)
			print(laststat)
		allfourperms.extend(list(i for i in laststat))

	allstuff = (len(allfourperms),allfourperms, len(allfiveperms),allfiveperms)
	with open("allrelicperms.text", "wb") as allperms:
		allperms.write(pickle.dumps(allstuff))
	
with open("allrelicperms.text", "rb") as allperms:
	fourpermtally, allfourperms, fivepermtally, allfiveperms = pickle.loads(allperms.read())
print("{} four-upgrade permutations found. {} five-upgrade permutations found.".format(fourpermtally, fivepermtally))

toggle = False
while not toggle:
	response = input("Does the relic have (4) or (5) upgrades? \n")
	if not response.isnumeric():
		print("Type 4 or 5.")
		continue
	if int(response) == 4:
		tally = fourpermtally
		perms = allfourperms
		upgrades = 4
		toggle = True
		continue
	if int(response) == 5:
		tally = fivepermtally
		perms = allfiveperms
		upgrades = 5
		toggle = True
		continue
	else:
		print("Wrong number. Try again.")

toggle = False
firststatupgrades = 0
secondstatupgrades = 0
thirdstatupgrades = 0
fourthstatupgrades = 0
firststat = 0
secondstat = 0
thirdstat = 0
fourthstat = 0
firstweight = 0
secondweight = 0
thirdweight = 0
fourthweight = 0
while not toggle:
	response = input("How many upgrades does the first stat have?\n")
	if not response.isnumeric():
		print("Type a number between 0 and {a}".format(upgrades))
		continue
	if int(response) > upgrades:
		print("Too big. Try again.")
		continue
	firststatupgrades = int(response)
	upgrades -= int(response)
	toggle = True
toggle = upgrades < 1
while not toggle:
	response = input("How many upgrades does the second stat have?\n")
	if not response.isnumeric():
		print("Type a number between 0 and {}".format(upgrades))
		continue
	if int(response) > upgrades:
		print("Too big. Try again.")
		continue
	secondstatupgrades = int(response)
	upgrades -= int(response)
	toggle = True
toggle = upgrades < 1
while not toggle:
	response = input("How many upgrades does the third stat have?\n")
	if not response.isnumeric():
		print("Type a number between 0 and {}".format(upgrades))
		continue
	if int(response) > upgrades:
		print("Too big. Try again.")
		continue
	thirdstatupgrades = int(response)
	upgrades -= int(response)
	toggle = True
	toggle = upgrades < 1
	fourthstatupgrades = upgrades
	toggle = True
toggle = False
while not toggle:
	if firststatupgrades>0:
		num = input("How many high rolls into the first stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(firststatupgrades))
			continue
		if int(num)>firststatupgrades:
			print("Too big. Try again.")
			continue
		firststatupgrades -= int(num)
		firststat +=int(num)*3
	toggle = True
toggle = firststatupgrades<1
while not toggle:
	if firststatupgrades>0:
		num = input("How many mid rolls into the first stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(firststatupgrades))
			continue
		if int(num)>firststatupgrades:
			print("Too big. Try again.")
			continue
		firststatupgrades -= int(num)
		firststat +=int(num)*2 + firststatupgrades
	toggle = True
toggle = False
while not toggle:
	if secondstatupgrades>0:
		num = input("How many high rolls into the second stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(secondstatupgrades))
			continue
		if int(num)>secondstatupgrades:
			print("Too big. Try again.")
			continue
		secondstatupgrades -= int(num)
		secondstat +=int(num)*3
	toggle = True
toggle = secondstatupgrades<1
while not toggle:
	if secondstatupgrades>0:
		num = input("How many mid rolls into the second stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(secondstatupgrades))
			continue
		if int(num)>secondstatupgrades:
			print("Too big. Try again.")
			continue
		secondstatupgrades -= int(num)
		secondstat +=int(num)*2 + secondstatupgrades
	toggle = True
toggle = False
while not toggle:
	if thirdstatupgrades>0:
		num = input("How many high rolls into the third stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(thirdstatupgrades))
			continue
		if int(num)>thirdstatupgrades:
			print("Too big. Try again.")
			continue
		thirdstatupgrades -= int(num)
		thirdstat +=int(num)*3
	toggle = True
toggle = thirdstatupgrades<1
while not toggle:
	if thirdstatupgrades>0:
		num = input("How many mid rolls into the third stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(thirdstatupgrades))
			continue
		if int(num)>thirdstatupgrades:
			print("Too big. Try again.")
			continue
		thirdstatupgrades -= int(num)
		thirdstat +=int(num)*2 + thirdstatupgrades
	toggle = True
toggle = False
while not toggle:
	if fourthstatupgrades>0:
		num = input("How many high rolls into the fourth stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(fourthstatupgrades))
			continue
		if int(num)>fourthstatupgrades:
			print("Too big. Try again.")
			continue
		fourthstatupgrades -= int(num)
		fourthstat +=int(num)*3
	toggle = True
toggle = fourthstatupgrades<1
while not toggle:
	if fourthstatupgrades>0:
		num = input("How many mid rolls into the fourth stat?\n")
		if not num.isnumeric():
			print("Type a number between 0 and {}".format(fourthstatupgrades))
			continue
		if int(num)>fourthstatupgrades:
			print("Too big. Try again.")
			continue
		fourthstatupgrades -= int(num)
		fourthstat +=int(num)*2 + fourthstatupgrades
	toggle = True
toggle = False
while not toggle:
	firstweight = input("Weight of first stat?\n")
	if not firstweight.isnumeric():
		print("Type a number.")
		continue
	firstweight= float(firstweight)
	toggle= True
toggle = False
while not toggle:
	secondweight = input("Weight of second stat?\n")
	if not secondweight.isnumeric():
		print("Type a number.")
		continue
	secondweight= float(secondweight)
	toggle= True
toggle = False
while not toggle:
	thirdweight = input("Weight of third stat?\n")
	if not thirdweight.isnumeric():
		print("Type a number.")
		continue
	thirdweight= float(thirdweight)
	toggle= True
toggle = False
while not toggle:
	fourthweight = input("Weight of fourth stat?\n")
	if not fourthweight.isnumeric():
		print("Type a number.")
		continue
	fourthweight= float(fourthweight)
	toggle= True
print("Weight of current relic is determined to be:")
counterweight = firststat*firstweight+secondstat*secondweight+thirdstat*thirdweight+fourthstat*fourthweight
print(counterweight)
input("Calculations will begin upon pressing enter.")

good=0
best=0
grandsum=0
for perm in perms:
	weight = perm[0]*firstweight+perm[1]*secondweight+perm[2]*thirdweight+perm[3]*fourthweight
	if counterweight<weight:
		good +=1
	if weight>best:
		best=weight
	grandsum+=weight
print("Calculations complete. Total relics tested: {}. \nAverage weight possibilities: {}\nPercent chance of higher relic: {}\nPercent chance of similar or worse relic: {}\nHighest possible weight: {}".format(tally,round(grandsum/tally, 2), round(good*100/tally, 2), round((1-good/tally)*100,2), best))
input("Press enter to complete.")
