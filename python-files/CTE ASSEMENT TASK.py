print("""
   __                              __              ____   ______               
   / /   ___  ____ ____  ____  ____/ /____   ____  / __/  / ____/___ ___  __  __
  / /   / _ \/ __ `/ _ \/ __ \/ __  / ___/  / __ \/ /_   / __/ / __ `__ \/ / / /
 / /___/  __/ /_/ /  __/ / / / /_/ (__  )  / /_/ / __/  / /___/ / / / / / /_/ / 
/_____/\___/\__, /\___/_/ /_/\__,_/____/   \____/_/    /_____/_/ /_/ /_/\__, /  
           /____/                                                      /____/   
""")
#used the triple quote function to print the ASC2 art 
print('Welcome to Legends of Emy')
NAME = input('What is your name?')
#using the input function to ask for the users name and used NAME variable to conduct further relative purposes
print('Welcome,',NAME)
#linked with the above line with the stored NAME variable
print(NAME,',You have been chosen to conduct a quest ordered by the king')
#refer to line 15
Q1 = input('Would you like to conduct the dangerous quest to find the Crystal of Dreams, to stop the ongoing war? (Yes/No)')
#used Q1 as the stored variable and used the input function to ask the players option of Yes or No
if Q1 in ["yes","Yes","YES","Y"]:
  #Used the If and in function to show the possible answers of the player and the if function would then print out the next line.
  print('You have chosen to conduct the quest')
else: 
  #Else function is used to print line 25 as the player puts anything other than yes
 quit('You have been sent to jail (GAME OVER)')
#Killed the player using the quit function (also prints the string )and has to restart the game by pressing run
import time
#imports the time function and sleeps the strings for the according seconds
print('You have then packed your bags to start the journey of finding the Crystal of Dreams')
time.sleep(5)
print('You walked out the palace and said goodbye to your friends and family "Bye" ')
time.sleep(5)
print("""
 _   |~  _
[_]--'--[_]
|'|""`""|'|
| | /^\ | |
|_|_|I|_|_|
""")
time.sleep(5)
#used the triple quote function to print the ASC2 art 
print('You walked along the old stone paved path and suddenly you have met a furious cyberplaygun')
Q2 = input('what would you do (Fight or Run)')
#using Q2 as stored variable
if Q2 in ["Fight","fight","FIGHT"]:
#used the if and in function related to line 21
  print("You have chosen to fight the furious Cyberplaygun, You defeated him with ease")

else:
  print('You have chosen to outrun the furious Cyberplaygun, You have escaped as you are faster than him')
#used else function related to line 24
print('You continued along the paved path, you have crossed rivers, lakes and mountains')
time.sleep(5)
print('You then have reached the mythical forest')
time.sleep(2)
print("""
          /
         /**
        /****\   /
       /      \ /**
      /  /\    /    \        /\    /\  /\      /\            /\/\/\  /
     /  /  \  /      \      /  \/\/  \/  \  /\/  \/\  /\  /\/ / /  \/  
    /  /    \/ /\     \    /    \ \  /    \/ /   /  \/  \/  \  /    \   
   /  /      \/  \/\   \  /      \    /   /    
__/__/_______/___/__\___\__________________________________________________
""")
time.sleep(2)
print('"Crack" you have realised that you are not alone, someone else is around!')
time.sleep(4)
print('suddenly someone came out in the dark, "Put your weapon on the floor"')
time.sleep(3)
print('"What are you doing here?" said the stranger')
print('"have to cross this forest to find the crystal of dreams." you said')
time.sleep(3)
print('"My name is Jake, from the royal palace" "I guess you from there too from the look of the armour" said jake ')
time.sleep(2)
print('Nice to meet you my name is,',NAME)
time.sleep(2)
print('"since we both going to find the crystal of dreams, not mind if I can have some help"')
time.sleep(3)
print('"why not having an extra pair of hands" you said')
print('all of a sudden a group of Cyberplayguns were in front of you')
#line 67-82 used the time and print function to give context to the story.
Q3 = input('You have the choice to Run or fight the furious Cyberplayguns, (Run/fight)')
if Q3 in ["Fight","FIGHT","fight"]:
  print('You and Jake have worked alongside really well with cooperation you and Jake have defeated the Cyberplayguns.')
  # line 84-89 related to line 21-24 (if and in function)
else:
  print('You and Jack have chosen to run, you found a cave big enough for you and Jake to hide in you have escaped the Cyberplayguns.')
print('END OF CHAPTER ONE')
time.sleep (2)



print('CHAPTER 2: AHHH Caveman')
time.sleep (2)
print('You and Jake have come across to a large lake')
Q4 = input('would you like to swim across or take the longer route on foot (Swim/Walk)')
if Q4 in ["Swim","SWIM","swim"]:
  print('you have failed to swim across the lake, you have swam back and chose the longer route')
#line 95-100 related to line 84-89 (if and in function)
else:
  print('You have made it to the other side of the lake')
time.sleep(3)
print('you and jake have found a good camp site to rest for the night')
time.sleep(2)
print("""
        ______
       /     /
      /     /  
     /_____/----\_    (  
    "     "          ).  
   _ ___          o (:') o   
  (@))_))        o ~/~~\~ o   
                  o  o  o
                            """)
time.sleep(3) 
print('The next morning you and Jake have woke up and continued the journey')
print('You and Jake have headed into the deep caves of the mountains')
time.sleep(3)
print('You and Jake have come across to face a broken bridge')
time.sleep(3)
Q5 = input('You have the options to jump across or find materials that can possibly fix the bridge. (Jump/fix)')
#Used the input function and sttored Q5 as the variable.
if Q5 in ["JUMP","jump","Jump"]:
  quit('You have failed to jump over the bridge and fell. (GAME OVER)')
#Line 120-125 (used the if,and else function) line 122(used the quit function to kill the game)
else:
  print('You and Jake have found metal boards that can support your weights, you have made it over safely')
print('You and Jack have headed deeper into the cave')
time.sleep(3)
print('"It is beautiful, said Jake" "Ye it sure is,you replied"')
time.sleep(2)
print(NAME,',I think we have a problem')
print('Ye what is it')
print('The man cave seems to be in our way')
time.sleep(3)
print("""
⠀⠀         ⢸⣿⠽⠿⡛⢿⣿⣷⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⣀⢀⠀⢿⣯⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠛⠁⠀⣼⣿⡷⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠭⣄⠀⠀⣰⣼⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣄⠠⠴⡞⢸⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⠄⠾⢡⠄⢠⢃⠞⣷⢄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡰⠊⡉⠀⠀⠀⠈⢂⡑⣃⠅⠊⠀⠀⠉⠛⠲⢤⠀
⠀⠀⠀⠀⢰⢇⠀⡎⠀⠀⠀⠀⠀⠏⠀⠀⠀⠀⠀⢸⣸⠀⢸⡇
⠀⠀⠀⢠⠃⠻⣟⢧⡀⠀⠀⠀⢸⠀⠀⠀⠀⠀⣀⡼⠁⠀⢸⡇
⠀⠀⠀⢸⠀⢀⡻⠦⠵⠤⢄⣀⣀⡠⠄⢤⣀⣰⣿⠁⠀⠀⠘⡅
⠀⠀⠀⢸⡀⠋⠀⠀⠀⠀⠀⠈⠀⠈⣅⣸⠀⠤⢾⣄⠀⠀⡰⡇
⠀⠀⠀⠘⢧⣀⠀⠀⢀⣀⣠⣴⣞⡉⠁⠀⠀⠀⠈⠉⠀⠐⣿⠀
⠀⠀⠀⠀⠀⠈⢹⣿⡏⠀⣩⠉⠉⠙⠓⠻⠵⢾⣶⣶⣶⠞⠁⠀
⠀⠀⠀⠀⠀⠀⠈⠚⠛⠿⠅⠒⢊⣽⣛⡩⠤⠖⠒⠚⠋⠀⠀⠀
""")
#Used the triple quote function to print out the ASC2 art.
time.sleep(2)
Q6 = input('Seems like he is not gonna move out of our way, would you fight or Run (fight/run)')
#Used the input function and stored Q6 as variable
if Q6 in ["Fight","FIGHT","fight"]:
 print('You have made it out alive, you and Jake had fought for your lives')
# if and else function used 
else:
  print('You have chosen to outrun the cave man, however you and Jake are not as fast as him, you and Jake have fought back and made it out alive')
  #used the else function
time.sleep(3)
print('END OF CHAPTER 2')


time.sleep(3)
print('CHAPTER 3: A new helper?')
time.sleep(2)
print('"Finaly frostlands, we are halfway through" said Jake')
time.sleep(3)
print('The snow falls like small feathers, they are light and beautiful')
time.sleep(3)
print('You and Jack have followed the small trail that can barely be seen ')
time.sleep(3)
#line 167-175 used the time and print functions to give context to the story
Q7 = input('As you and Jack walked you saw Cyberplaygun soilders holding heavey weapons (Fight/run)')
if Q7 in ["FIGHT","fight","Fight"]:
    quit('Unfortunetly You and Jack had lost to the furious Cyberplayguns (GAME OVER)')
# in lines 177-182 I haved used input,if and quit function to perform the killing of the player 
else:
    print('You have choosen to run, luckily the cyberplayguns did not notice you and Jack')
time.sleep(3)
print('Following along the fadded trail You and Jack have reached the greater rocks')
time.sleep(3)
print('"Our maps said that we are not far from the Crystal of dreams." said Jake')
time.sleep(3)
print('Following along the smooth lime stones, you and Jake have found an injured deer.')
time.sleep(3)
print('You and Jacke have helped the deer and helped it to get back its strength.')
time.sleep(2)
print('"Stop what you are doing and put down your weapons" stranger siad')
time.sleep(3)
print('"Are you also been sent to find the crystal of dreams?" she said')
time.sleep(3)
print('"Yes I and Jake are both from the Royal palce, nice to meet you" you said')
time.sleep(3)
print('"Nice to meet you i am Athena, from frostlands, do you mine if I join" she said')
time.sleep(3)
print('"Sure we all have one common goal, to defeat the Cyberplayguns." said Jake')
time.sleep(3)
#line 183-201 used time and print function to add more story lins
Q8 = input('suddenly a group of cyberplaygun soilders rushed at you (fight/run/hide)')
if Q8 in ["FIGHT","Fight","fight"]:
  print('You, Jake and Athena had shown high cooperation and fighting skills, you made it out alive.')
elif Q8 in ["RUN","run","Run"]:
  #Used the elif statement to support extra answers/paths
  print('You, Jake and Athena have run in seperate path and lost them.')
else:
  quit('You have been caught by the Cyberplayguns (GAME OVER)')
print('You, Jake and Athena have headed back on the way to finding the Crystal of Dreams')
time.sleep(3)
print('Map says it should be 3Km until the rocks')
time.sleep(3)
print('you followed behind Jake and Athena along the small rock trials')
time.sleep(3)
print('"Here it is, Crystal of Dreams" Athena said')
time.sleep(3)
print('The rock was then dug up')
time.sleep(3)
print('"Now lets take this rock back to the Royal Palace and end the war." said Jake')
time.sleep(3)
print('END OF CHAPTER 3')


time.sleep(3)
print('CHAPTER 4: Home coming')
time.sleep(3)
print('You, Jake and Athena have started your journey back to the Royal palace.')
time.sleep(3)
print('You followed along the yellow limestone mark that you have left to guide you back to the palace')
time.sleep(3)
print('soon you have made it out of the greater rocks')
time.sleep(3)
#used the time function to sleep the lines in lines 226-234
Q9 = input('suddenly a troop of Cyberplaygun soilders came in your way (Fight/Run)')
if Q9 in ["FIGHT","Fight","fight"]:
 print('you made it out alive, however you are injured')
else:
  print('You have outrun the Cyberplaygun soilders, you are not harmed')
time.sleep(3)
print("""  |\                |\                |\                |
   || .---.          || .---.          || .---.          || .---.
   ||/_____\         ||/_____\         ||/_____\         ||/_____
   ||( '.' )         ||( '.' )         ||( '.' )         ||( '.' )
   || \_-_/_         || \_-_/_         || \_-_/_         || \_-_/_
   :-"`'V'//-.       :-"`'V'//-.       :-"`'V'//-.       :-"`'V'//-.
  / ,   |// , `\    / ,   |// , `\    / ,   |// , `\    / ,   |// , `
 / /|Ll //Ll|| |   / /|Ll //Ll|| |   / /|Ll //Ll|| |   / /|Ll //Ll|| |
/_/||__//   || |  /_/||__//   || |  /_/||__//   || |  /_/||__//   || |
\ \/---|[]==|| |  \ \/---|[]==|| |  \ \/---|[]==|| |  \ \/---|[]==|| |
 \/\__/ |   \| |   \/\__/ |   \| |   \/\__/ |   \| |   \/\__/ |   \| |
 /\|_   | Ll_\ |   /|/_   | Ll_\ |   /|/_   | Ll_\ |   /|/_   | Ll_\ |
    |   |   ||/       |   |   ||/       |   |   ||/       |   |   ||/
    |   |   |         |   |   |         |   |   |         |   |   |
    |   |   |         |   |   |         |   |   |         |   |   |
    |   |   |         |   |   |         |   |   |         |   |   |
    L___l___J         L___l___J         L___l___J         L___l___J
     |_ | _|           |_ | _|           |_ | _|           |_ | _|
    (___|___)         (___|___)         (___|___)         (___|___)
     ^^^ ^^^           ^^^ ^^^           ^^^ ^^^           ^^^ ^^^
     """)
print('You have continued your journey')
time.sleep(3)
print('You followed the narrow path that was fading away')
time.sleep(3)
print('Following the past trail soon had lead you to frostlands')
time.sleep(3)
print('The deep snows have slowed you down, but you kept going')
time.sleep(3)
print('You followed along the deep snow coverd trail')
time.sleep(3)
print('that will lead you back to the royal palace.')
time.sleep(3)
print('You have made it across forst lands.')
time.sleep(3)
Q10 = input('You have come across to a wooden bridge, it seems a bit loose would u walk a longer route or cross it? (cross/walk)')
if Q10 in ("WALK","Walk","walk"):
 print('YOu have choosen the long route and made it saftly')
else:
  quit('The bridge was not strong enough, you have died (Game over)')
time.sleep(3)
print('You followed along the paved roads that leads to the royal palace')
time.sleep(3)
print('Afther long days of journey, the large castle once again apeared from distance')
time.sleep(3)
print('You, Jake and Athena hurried each other and went for the royal palace')
time.sleep(3)
print('You walked into the grand hall where the king have been waiting.')
time.sleep(3)
print('The king holds the knight swords and marked each of us, means we are now being granted the highest level of achivement')
time.sleep(3)
print('You slowly handed the crystal of dreams to the king.')
time.sleep(3)
print('You have completed the game')
print("""________                        ___________           .___       
 /  _____/_____    _____   ____   \_   _____/ ____    __| _/______ 
/   \  ___\__  \  /     \_/ __ \   |    __)_ /    \  / __ |/  ___/ 
\    \_\  \/ __ \|  Y Y  \  ___/   |        \   |  \/ /_/ |\___ \  
 \______  (____  /__|_|  /\___  > /_______  /___|  /\____ /____  > 
        \/     \/      \/     \/          \/     \/      \/    \/  
""")