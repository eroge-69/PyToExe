import random
str = ["weak", "strong", "average"]
stren = random.choice(str)
namw = ["bowen", "bob", "joe", "shelly", "flak", "pegg", "betty"]
name = random.choice(namw)
deff = random.randint(1, 6)
defff = round(deff)
run = random.randint(0, 1)
runn = round(run)
att = random.randint(1, 6)
attt = round(att)
print(f'a {stren} zombey named {name} approaches!')
print('type 1 to attack, type 2 to escape, type 3 to defend, type 4 to do nothing.')
action = int(input('what do you choose: '))
if action == int(1):
   print (f'you punched the zombie and did {attt} dammage!')
else:
    if action == int(2):
        if runn == int(1):
            print ('escaped!')
        else:
            print ('the zombie got you.')
            if action == int(3):
                if defff >= int(3):
                    print('deffended all damage!')
                else:
                    print('the zombie got you.')
                    if action == int(4):
                        if run == int(1):
                            print('you slept through the encounter')
                        else:
                            print('you died from lack of sleep.')