canvey = [
    (7, 3),    
    (99, 98), 
    (13, 49),  
    (39, 35),  
    (36, 91),  
    (10, 143), 
    (49, 13),  
    (7, 11),   
    (1, 2),    
    (91, 1)    
]

s_num = input("enter your number: ")
try:
    num = int(s_num)
except ValueError:
    num = 5

s_steps = input("enter your max step: ")
try:
    steps = int(s_steps)
except ValueError:
    steps = 30

def run_fractran(start, max_steps=200):
    n = start
    history = [n]
    for step in range(max_steps):
        changed = False
        for p, q in canvey:           
            if (n * p) % q == 0:         
                n = (n * p) // q
                history.append(n)
                changed = True
                break
        if not changed:
            break
    return history

seq = run_fractran(num, max_steps=steps)
print(" -> ".join(str(x) for x in seq))