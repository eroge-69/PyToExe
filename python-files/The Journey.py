# [The Journey]
# [Version 1.0]
# [Author: R3dm45k]
# [Created & Modified:03/2022 - 7/25/25]
# [Instructions: Make sure the most up to date version of python is installed. Make sure the program file and the images are in the same folder.]
# [Instructions: You play by selecting one of two options by clicking a the corresponding button. Enjoy!]
# button1["command"]= restart
# button2["command"]= root.destroy
# button1["text"]= "Retry"
# button2["text"]= "Quit"
# photo["file"]= ""


from tkinter import *

import os

#Sword/Shield Check
invcheck = ["sword", "shield"]

#Coin/No Coin Check
invcheck2 = ["coin", "nocoin"]

#Window & Background
root = Tk()
root.title('The Journey')
photo = PhotoImage(file = "title.gif")
w = Label(root, image=photo)
root.configure(background="tan") 
w.pack()

#Restarts Program
def restart():
    root.destroy()
    os.startfile("Game.py")
    
#Text, Background & Command Changes
      
def textchange1(): 
    button3["text"]= "You find yourself looking up at an endless blue sky. You sit up, squinting from the sunlight. It seems you have woken up in a field with no recollection of why you are there. You see the distinctive glint of metal."
    button1["command"]= textchange2
    button2["command"]= textchange3
    button1["text"]= "Investigate"
    button2["text"]= "Wait"
    photo["file"]= "field1.gif"


def textchange2():
    button3["text"]= "Moving closer to the glint, you see a sword and a shield on the ground. You realize you are only able to carry one of these. Choose one: "
    button1["command"]= textchange4
    button2["command"]= textchange5
    button1["text"]= "Sword"
    button2["text"]= "Shield"
    photo["file"]= "objects.gif"

  
def textchange3(): 
    button3["text"]= "There are too many unknowns. Where are you, how did you get here and why? You decide it is safest to wait. After some time, you feel comfortable enough to investigate the glint. "
    button1["command"]= textchange2
    button2["command"]= textchange2
    button1["text"]= "Investigate"
    button2["text"]= "Investigate"
    photo["file"]= "field1.gif"

# sword
def textchange4():
    button3["text"]= "You lift the sword up out of it's nest of grass. You feel the hilt in your hand yet, surprisingly, there is no weight. You give it a practice swing, SWOOSH. " 
    button1["command"]= textchange6
    button2["command"]= textchange6
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "field1.gif"
    invcheck.remove("shield")

# shield
def textchange5():
    button3["text"]= "You pick the shield up and slide your arm through the straps on the back. It fits perfectly, as if it was designed for your arm. Oddly, all the armor feels weightless. "
    button1["command"]= textchange6
    button2["command"]= textchange6
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "field1.gif"
    invcheck.remove("sword")

def textchange6():
    button3["text"]= "You suddenly notice there is a forest nearby. It actually looks inviting. Do you: "
    button1["command"]= textchange7
    button2["command"]= textchange8
    button1["text"]= "Enter"
    button2["text"]= "Wait"
    photo["file"]= "field1.gif"

def textchange7():
    button3["text"]= "You decide to enter the woods and quickly notice a path. Do you follow it? "
    button1["command"]= textchange10
    button2["command"]= textchange9
    button1["text"]= "Follow"
    button2["text"]= "Wait"
    photo["file"]= "woods1.gif"
    
def textchange8():
    button3["text"]= "You wait. After a while it starts to get dark. You realize there is a sheer rock face all the way around you- except for the woods. Do you enter the woods? "
    button1["command"]= textchange9
    button2["command"]= textchange9
    button1["text"]= "Enter"
    button2["text"]= "I guess"
    photo["file"]= "field2.gif"
    
def textchange9():
    button3["text"]= "Man, it's really dark. However, you can see the path. Do you follow it?"
    button1["command"]= textchange10
    button2["command"]= textchange11
    button1["text"]= "Follow"
    button2["text"]= "Wait"
    photo["file"]= "woods2.gif"

#fork    
def textchange10():
    button3["text"]= "You follow the path until there is a fork in the road. To the left you hear drumming. To the right you hear nothing. Which way do you go?"
    button1["command"]= textchange16
    button2["command"]= textchange23
    button1["text"]= "Left" 
    button2["text"]= "Right"
    photo["file"]= "fork1.gif"

def textchange11():
    button3["text"]= "You see something coming out of the woods. Do you:"
    button1["command"]= textchange12
    button2["command"]= textchange13
    button1["text"]= "Run"
    button2["text"]= "Wait"
    photo["file"]= "wolf1.gif"

def textchange12():
    button3["text"]= "You run away!"
    button1["command"]= textchange10
    button2["command"]= textchange10
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "wolf1.gif"
    
def textchange13():
    button3["text"]= "You wait. You can now clearly see that a wolf is headed your way. Do you: "
    button1["command"]= textchange12
    button2["command"]= textchange14
    button1["text"]= "Run"
    button2["text"]= "Wait"
    photo["file"]= "wolf2.gif"
    
def textchange14():
    button3["text"]= "The wolf is almost on top of you now. Do you: "
    button1["command"]= textchange15
    button2["command"]= textchange12
    button1["text"]= "Use Item"
    button2["text"]= "Run"
    photo["file"]= "wolf3.gif"

def textchange15():
    if "shield" in invcheck:
        button3["text"]= "You raise your shield. The wolf slams into it with all of it's might. It falls to the ground stunned. Time to go"
        button1["command"]= textchange10
        button2["command"]= textchange10
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "woods2.gif"
    else:
        button3["text"]= "You raise your sword out infront of you. The wolf slams into the blade; piercing it's own chest. It falls to the ground dead. Time to go."
        button1["command"]= textchange10
        button2["command"]= textchange10
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "woods2.gif"
        
#cult
def textchange16():
    button3["text"]= "You go left. You come upon the entrance to a shrine. The drumming is much louder now. Do you: "
    button1["command"]= textchange17
    button2["command"]= textchange23
    button1["text"]= "Continue On"
    button2["text"]= "Go Back"
    photo["file"]= "shrine1.gif"

def textchange17():
    button3["text"]= "You see three shady figures around a fire. They speak to you, 'How dare you interrupt us!' Do you: "
    button1["command"]= textchange18
    button2["command"]= textchange23
    button1["text"]= "Use Item"
    button2["text"]= "Leave"
    photo["file"]= "cult.gif"    

def textchange18():
    if "shield" in invcheck:
        button3["text"]= "You raise your shield to defend yourself. The cultists suddenly flee."
        button1["command"]= textchange19
        button2["command"]= textchange19
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "cult.gif"
    else:
        button3["text"]= "You fiercely swing your sword. Slaughtering all three cultists."
        button1["command"]= textchange19
        button2["command"]= textchange19
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "cult.gif"
        
def textchange19():
    button3["text"]= "While you're at this shrine you could have a look around. Do you:"
    button1["command"]= textchange20
    button2["command"]= textchange23
    button1["text"]= "Look"
    button2["text"]= "Leave"
    photo["file"]= "Shrine1.gif"

def textchange20():
    button3["text"]= "You find a pair of coins. Do you:"
    button1["command"]= textchange21
    button2["command"]= textchange23
    button1["text"]= "Take"
    button2["text"]= "Leave"
    photo["file"]= "coins.gif"
    
# coin
def textchange21():
    button3["text"]= "You pocket the coins then leave."
    button1["command"]= textchange23
    button2["command"]= textchange23
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "coins.gif"
    invcheck2.remove("nocoin")
    
# no coin
def textchange22():
    button3["text"]= "You do not pick up the coins and you leave."
    button1["command"]= textchange23
    button2["command"]= textchange23
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "coins.gif"
    invcheck2.remove("coin")

#stream    
def textchange23():
    button3["text"]= "You find yourself standing in front of a stream. You see stepping stones leading across. Do you:"
    button1["command"]= textchange24
    button2["command"]= textchange25
    button1["text"]= "Cross"
    button2["text"]= "Look Around"
    photo["file"]= "stream.gif"
   
def textchange24():
    button3["text"]= "You nearly make it across. You suddenly slip on a mossy stone and fall into the water. The current is too strong, you get washed down stream!"
    button1["command"]= textchange26
    button2["command"]= textchange26
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "stream.gif"

def textchange25():
    button3["text"]= "You look survey your surroundings. In the distance you can see a well. Do you: "
    button1["command"]= textchange28
    button2["command"]= textchange24
    button1["text"]= "Investigate"
    button2["text"]= "Cross"
    photo["file"]= "stream.gif"

def textchange26():
    button3["text"]= "You wake up laying on the shore of the river."
    button1["command"]= textchange27
    button2["command"]= textchange27
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "stream.gif"
    
def textchange27():
    button3["text"]= "You find yourself at the base of a large mountain. Do you: "
    button1["command"]= textchange30
    button2["command"]= textchange28
    button1["text"]= "Climb"
    button2["text"]= "Go Back"
    photo["file"]= "base.gif"

#well
def textchange28():
    button3["text"]= "You have found an old well. Do you want to make a wish? "
    button1["command"]= textchange29
    button2["command"]= textchange23
    button1["text"]= "Wish"
    button2["text"]= "Go Back"
    photo["file"]= "well.gif"

def textchange29():
    if "coin" in invcheck:
        button3["text"]= "You rummage through your pockets and grab the coin from earlier. You toss it in the well. Make a wish (say it out loud)."
        button1["command"]= textchange23
        button2["command"]= textchange23
        button1["text"]= "Leave"
        button2["text"]= "Leave"
        photo["file"]= "well.gif"
    else:
        button3["text"]= "Sadly, you don't have a coin to throw in the well."
        button1["command"]= textchange23
        button2["command"]= textchange23
        button1["text"]= "Leave"
        button2["text"]= "Leave"
        photo["file"]= "well.gif"

#mountain
def textchange30():
    button3["text"]= "You climb a short distance. Suddenly a mountain lion leaps out in front of you. Do you: "
    button1["command"]= textchange31
    button2["command"]= textchange32
    button1["text"]= "Use Item"
    button2["text"]= "Run"
    photo["file"]= "lion.gif"

def textchange31():
    if "shield" in invcheck:
        button3["text"]= "You raise your shield. The mountain lion leaps at you, bounces off the shield and tumbles down a cliff."
        button1["command"]= textchange35
        button2["command"]= textchange35
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "lion.gif"
    else:
        button3["text"]= "You swing your sword. You leave a trail of crimson across the mountain lion's eye. It flees."
        button1["command"]= textchange35
        button2["command"]= textchange35
        button1["text"]= "Continue"
        button2["text"]= "Continue"
        photo["file"]= "lion.gif"
        
def textchange32():
    button3["text"]= "You find yourself back at the base of the mountain. You can still see the mountain lion standing up there. Do you: "
    button1["command"]= textchange34
    button2["command"]= textchange33
    button1["text"]= "Climb Again"
    button2["text"]= "Wait"
    photo["file"]= "base.gif"

def textchange33():
    button3["text"]= "You wait for some time, finally the mountain lion leaves."
    button1["command"]= textchange35
    button2["command"]= textchange35
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "base.gif"

def textchange34():
    button3["text"]= "You decide to face the mountain lion once more. This time you're serious."
    button1["command"]= textchange31
    button2["command"]= textchange31
    button1["text"]= "Use Item"
    button2["text"]= "Use Item"
    photo["file"]= "lion.gif"
    
def textchange35():
    button3["text"]= "You continue your ascent. Suddenly all of your memories come rushing back..."
    button1["command"]= textchange36
    button2["command"]= textchange36
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "base.gif"

#end
def textchange36():
    button3["text"]= "As you climb you contemplate your past. (please do so now)"
    button1["command"]= textchange37
    button2["command"]= textchange37
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain1.gif"

def textchange37():
    button3["text"]= "As you climb you contemplate your present. (please do so now)"
    button1["command"]= textchange38
    button2["command"]= textchange38
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain2.gif"
    
def textchange38():
    button3["text"]= "As you climb you contemplate your future. (please do so now)"
    button1["command"]= textchange39
    button2["command"]= textchange39
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain3.gif"

def textchange39():
    button3["text"]= "You finally reach the peak of the mountain. You have a sudden realization:"
    button1["command"]= textchange40
    button2["command"]= textchange40
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain4.gif"

def textchange40():
    button3["text"]= "We are, quite literally, a collection of experiences. All of our thoughts, concepts and opinions are based off of these experiences."
    button1["command"]= textchange41
    button2["command"]= textchange41
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain4.gif"

def textchange41():
    button3["text"]= "Although our past may not be pleasant. It made us who we are today. All we have is the present moment- the current experience. "
    button1["command"]= textchange42
    button2["command"]= textchange42
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain4.gif"

def textchange42():
    button3["text"]= "And, although the future is not certain. We can find comfort in the present- in creating new experiences and continuing to develop as a person."
    button1["command"]= textchange43
    button2["command"]= textchange43
    button1["text"]= "Continue"
    button2["text"]= "Continue"
    photo["file"]= "mountain4.gif"

def textchange43():
    button3["text"]= "Thank you for playing my little game. :)"
    button1["command"]= root.destroy
    button2["command"]= root.destroy
    button1["text"]= "Quit"
    button2["text"]= "Quit"
    photo["file"]= "mountain4.gif"
    
#Option Buttons
button1 = Button(root, fg="red", text = "Begin",height = 20, width = 20, bg = "wheat", command = textchange1)
button1.pack(fill='none',side = "left")

button2 = Button(root, fg="red", text = "Begin", height = 20, width = 20, bg = "wheat", command = textchange1)
button2.pack(fill='none',side = "right")

#Third Button [functions as a text box]
button3 = Button(root, text = "Welcome to 'The Journey.' YOUR journey. The path ahead may be difficult, but be patient and remember that your choices have consequences. Click 'Begin' when you're ready to start.", height = 20, width = 200, bg = "tan")
button3.pack(fill='none',side = "bottom")

    
root.mainloop()
