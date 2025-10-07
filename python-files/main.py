# TO BE WORKED ON: Better cutoff, timer system that calculates WPM




import turtle
from time import sleep, perf_counter
from random import choice
wn = turtle.Screen()
wn.bgcolor("black")
trtl = turtle.Turtle(visible=False)
trtl.pencolor("white")
helper = turtle.Turtle(visible=False)
helper.pencolor("white")
written = ""
bank = [
    'A long black shadow slid across the pavement near their feet and the five Venusians, very much startled, looked overhead. They were barely in time to see the huge gray form of the carnivore before it vanished behind a sign atop a nearby building which bore the mystifying information PepsiCola.    '
] # Paragraphs from https://randomwordgenerator.com/paragraph.php
true = choice(bank)
extra = [] # Remove the rearmost letters to make room for the newest ones so that the written does not go offscreen
over = False

start:float = perf_counter();


count = -1
helper.pu()
helper.goto(0, 200)


def divide(paragraph:str, cutoff_char_lim:int):
   
    quotient:str = ""
    line:int = 1
    i:int = 0
    while i < len(paragraph):
        if (i+1 <= cutoff_char_lim*line):
            quotient += paragraph[i]
        else:
            j:int = i
            while paragraph[j] != " ": # upon reaching the char lim per line, backtrack to the last seen space
               
                j-=1
                quotient = quotient[0:j]
            quotient += "\n" # once reached, add a newline and adjust the
            i = j
            line+=1
        i+=1
    return quotient


#print(divide(true, 100))


# Divide each sentence in to 3 parts in order to be visible. Must work on better cutoffs
'''helper.write(true[0:len(true)//3], align="center", font=("Arial", 15, "normal")) # 2yrs later: WTF IS THIS MATH WHATS GOING ON
helper.goto(0, 180)
helper.write(true[len(true)//3:2*(len(true)//3)], align="center", font=("Arial", 15, "normal"))
helper.goto(0, 160)
helper.write(true[2*(len(true)//3):-1], align="center", font=("Arial", 15, "normal"))'''

helper.write(divide(true, 100), align="center", font=("Arial", 15, "normal"))


def check():
    global written, extra
    if ''.join(extra) + written[0:count+1] == true[0:count+1]: # To ensure proper comparison, add the invisible letters to the written as well
        trtl.pencolor("lime")
    else:
        trtl.pencolor("red")
        
    if(len(written) > 31): # 31 here is the number of typed characters we can display before they get pushed before they get sliced off. May need to change based off of a scale in the future because of the new paragraph divider
        extra.append(written[0])
        written = written[1:len(written)]
        
    if ''.join(extra) + written == true:
      print("shfdshkjd")
      wn.textinput(f"Your typing speed: {len(true.split(' '))/((perf_counter() - start)/60) }")




def char(c:str):
    global written, count
    written += c
    count+=1
    check()
    trtl.clear()
    trtl.write(written, align="center", font=("Arial", 30, "normal"))




def clear():
    global written, count


    count = 0
    written = ""
    trtl.clear()
    trtl.write(written, align="center", font=("Arial", 30, "normal"))




def backspace():
    global written, count
    if not len(written) == 0:
        written = written[0:len(written)-1]
        count-=1
    try: # Re-add old characters
        written = extra[-1] + written
        extra.pop()
    except:pass
    check()
    trtl.clear()
    trtl.write(written, align="center", font=("Arial", 30, "normal"))




wn.listen()




wn.onkeypress(lambda: char("a"),"a")
wn.onkeypress(lambda: char("b"),"b")
wn.onkeypress(lambda: char("c"),"c")
wn.onkeypress(lambda: char("d"),"d")
wn.onkeypress(lambda: char("e"),"e")
wn.onkeypress(lambda: char("f"),"f")
wn.onkeypress(lambda: char("g"),"g")
wn.onkeypress(lambda: char("h"),"h")
wn.onkeypress(lambda: char("i"),"i")
wn.onkeypress(lambda: char("j"),"j")
wn.onkeypress(lambda: char("k"),"k")
wn.onkeypress(lambda: char("l"),"l")
wn.onkeypress(lambda: char("m"),"m")
wn.onkeypress(lambda: char("n"),"n")
wn.onkeypress(lambda: char("o"),"o")
wn.onkeypress(lambda: char("p"),"p")
wn.onkeypress(lambda: char("q"),"q")
wn.onkeypress(lambda: char("r"),"r")
wn.onkeypress(lambda: char("s"),"s")
wn.onkeypress(lambda: char("t"),"t")
wn.onkeypress(lambda: char("u"),"u")
wn.onkeypress(lambda: char("v"),"v")
wn.onkeypress(lambda: char("w"),"w")
wn.onkeypress(lambda: char("x"),"x")
wn.onkeypress(lambda: char("y"),"y")
wn.onkeypress(lambda: char("z"),"z")
wn.onkeypress(lambda: char("A"),"A")
wn.onkeypress(lambda: char("B"),"B")
wn.onkeypress(lambda: char("C"),"C")
wn.onkeypress(lambda: char("D"),"D")
wn.onkeypress(lambda: char("E"),"E")
wn.onkeypress(lambda: char("F"),"F")
wn.onkeypress(lambda: char("G"),"G")
wn.onkeypress(lambda: char("H"),"H")
wn.onkeypress(lambda: char("I"),"I")
wn.onkeypress(lambda: char("J"),"J")
wn.onkeypress(lambda: char("K"),"K")
wn.onkeypress(lambda: char("L"),"L")
wn.onkeypress(lambda: char("M"),"M")
wn.onkeypress(lambda: char("M"),"M")
wn.onkeypress(lambda: char("O"),"O")
wn.onkeypress(lambda: char("P"),"P")
wn.onkeypress(lambda: char("Q"),"Q")
wn.onkeypress(lambda: char("R"),"R")
wn.onkeypress(lambda: char("S"),"S")
wn.onkeypress(lambda: char("T"),"T")
wn.onkeypress(lambda: char("U"),"U")
wn.onkeypress(lambda: char("V"),"V")
wn.onkeypress(lambda: char("W"),"W")
wn.onkeypress(lambda: char("X"),"X")
wn.onkeypress(lambda: char("Y"),"Y")
wn.onkeypress(lambda: char("Z"),"Z")
wn.onkeypress(lambda: char(" "), "space")
wn.onkeypress(lambda: char(","), "comma")
wn.onkeypress(lambda: char("."), "period")


wn.onkeypress(clear, "Tab")
wn.onkeypress(backspace, "BackSpace")




wn.mainloop()










