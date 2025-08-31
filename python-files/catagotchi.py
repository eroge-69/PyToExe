cat_mood = '(=^.w.^=)'
hunger = 1
happyness = 1
sleepy = 1

while True:
    print(f"cat: {cat_mood} hunger: {hunger} sleep: {sleepy} happy {happyness}",end='\r')
    action = input('\neat,sleep or,play. ').lower()
    
    if action == 'eat':
        hunger -= 1
        cat_mood = '(=^.o.^=)'
        happyness += 1
        sleepy += 1
        
    elif action == 'sleep':
        cat_mood = '(=^-_-^=) zzz'
        sleepy = 0
        happyness -= 1
        
    elif action == 'play':
        cat_mood = '(=^ o_o^=) _O'
        happyness += 3
        sleepy += 2
        hunger += 1
        
    if hunger == 10:
        print('they died:<')
        exit()
        
    elif sleepy == 10:
        print('they died:<')
        exit()
        
    elif happyness == -1:
        print('they died:<')
        exit()