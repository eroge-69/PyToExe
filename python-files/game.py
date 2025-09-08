pip install auto-py-to-exe
# imports
from random import *
from time import sleep
import os
# setting all the variable
Health = 30
Max_health = 30
bandages = 5
Xp = 5
fight = 0
Skeleton_health = 15
Zombie_health = 20
wins = 0
skeleton = False
zombie = False
# entrance
print("Welcome to my dungeon, in order to progress you can defeat enemies, once you die the game will end, once you die your achivments will be displayed")

while Health > 0: # loop/ death check
  fight = randint(1,Xp) #who wil you fight (increases the licklyhood of a boss as you go along) 
  if fight in range (1, 6): #spawns a skeli and sets health based on lvl
      Skeleton_health = 15
      Skeleton_health = Skeleton_health + Xp
      skeleton = True
  else: #spawns a big skeli (called Zombie becuase i count find any ascii art for a Zombie) and sets health based on lvl
      Zombie_health = 20
      Zombie_health = Zombie_health + Xp
      skeleton = False
      zombie = True
  while skeleton == True: #Skeli fight
      sleep(2)
      hit_increase = Xp * 1.25
      Max_health = Xp * 6
      if Health > Max_health:
          Health = Max_health
      os.system('cls')#shows health + bandages with a bossbar of sorts
      print("Health " + str(Health))
      print("bandages " + str(bandages))
      print('█' * Skeleton_health )
      print(r"""      .-.
     (o.o)
      |=|
     __|__
   //.=|=.\\
  // .=|=. \\
  \\ .=|=. //
   \\(_=_)//
    (:| |:)
     || ||
     () ()
     || ||
     || ||
l42 ==' '==""")
      print("1: Fight, 2: Heal") #what action fight or heal
      action = input("what will you do ")
      if action == "1": #checking if attack hits
          hit = randint(1,20)
          hit = hit + hit_increase
          if hit >= 10: # rolling damage
              damage = randint(1,Xp+10)

              Skeleton_health = Skeleton_health - damage
              print(f"the attack hits dealing {damage} damage")
          elif hit  <= 10:
              print("the attack misses dealing no damage")
      elif action == "2":
        if bandages > 0:
                bandages = bandages - 1
                heal = randint(Xp, Xp+15)
                Health = Health + heal
                print(f"you heal for {heal} health")
                if Health > Max_health: #to stop player from healing more than their health
                  print(f"you heal to full health")
                else:
                  print(f"you are now at {Health} health")  
        else:
            print("no more bandages")
      else: # to stop miss inputs
        print("that won't work")
      if Skeleton_health > 0:
          print("THe Skeleton attacks")
          Bad_attack = randint(1,20)
          if Bad_attack > 10:
               Bad_damage = randint(1,Xp*2)
               Health = Health - Bad_damage
               print(f"The Skeleton hits you dealing {Bad_damage} damage")
          if Health <= 0:
              skeleton = False
          
      else: #kills the skeli
          print("the skeleton dies")
          skeleton = False
          gifts = randint(0,Xp)
          gifts  = gifts + 2
          bandages = bandages + gifts
          print(f"you defeat the skeleton and recive {gifts} more bandages")
          print("prepare for your next battle")
          Health = Health + 5
          wins = wins + 1
          Xp = Xp + 1
          sleep(0.5)





  while zombie == True: #mostly the same as small skeli just with different numbers and art, gives more xp and bandages in return for a more difficult fight
      sleep(2)
      hit_increase = Xp * 1.25
      Max_health = Xp * 6
      if Health > Max_health:
          Health = Max_health
      os.system('cls')
      print("Health " + str(Health))
      print("bandages " + str(bandages))
      print('█' * Zombie_health )
      print(r"""
                              _.--""-._
  .                         ."         ".
 / \    ,^.         /(     Y             |      )\
/   `---. |--'\    (  \__..'--   -   -- -'""-.-'  )
|        :|    `>   '.     l_..-------.._l      .'
|      __l;__ .'      "-.__.||_.-'v'-._||`"----"
 \  .-' | |  `              l._       _.'
  \/    | |                   l`^^'^^'j
        | |                _   \_____/     _
        j |               l `--__)-'(__.--' |
        | |               | /`---``-----'"1 |  ,-----.
        | |               )/  `--' '---'   \'-'  ___  `-.
        | |              //  `-'  '`----'  /  ,-'   I`.  \
      _ L |_            //  `-.-.'`-----' /  /  |   |  `. \
     '._' / \         _/(   `/   )- ---' ;  /__.J   L.__.\ :
      `._;/7(-.......'  /        ) (     |  |            | |
      `._;l _'--------_/        )-'/     :  |___.    _._./ ;
        | |                 .__ )-'\  __  \  \  I   1   / /
        `-'                /   `-\-(-'   \ \  `.|   | ,' /
                           \__  `-'    __/  `-. `---'',-'
                              )-._.-- (        `-----'
                             )(  l\ o ('..-.
                       _..--' _'-' '--'.-. |
                __,,-'' _,,-''            \ \
               f'. _,,-'                   \ \
              ()--  |                       \ \
                \.  |                       /  \
                  \ \                      |._  |
                   \ \                     |  ()|
                    \ \                     \  /
                     ) `-.                   | |
                    // .__)                  | |
                 _.//7'                      | |
               '---'                         j_| `
                                            (| |
                                             |  \
                                             |lllj
                                             ||||| """)
      print("1: Fight, 2: Heal")
      action = input("what will you do ")
      if action == "1":
          hit = randint(4,20)
          hit = hit + hit_increase
          if hit >= 12: # note the higher ac 
              damage = randint(1,Xp+10)
              Zombie_health = Zombie_health - damage
              print(f"the attack hits dealing {damage} damage")
              print("")
          elif hit  <= 10:
              print("the attack misses dealing no damage")
              print("")
      elif action == "2":
        if bandages > 0:
                bandages = bandages - 1
                heal = randint(Xp, Xp+15)
                Health = Health + heal
                print(f"you heal for {heal} health")
                if Health > Max_health:
                  print(f"you heal to full health")
                else:
                  print(f"you are now at {Health} health") 
        else:
            print("no more bandages")
      else:
        print("that won't work")
      if Zombie_health > 0:
          print("THe big skeleton attacks")
          Bad_attack = randint(Xp,15)
          if Bad_attack >= 10:
               Bad_damage = randint(1,Xp*3)
               Health = Health - Bad_damage
               print(f"The big skeleton hits you dealing {Bad_damage} damage")
          if Health <= 0:
              zombie = False
          
      else:
          print("the big skeleton dies")
          zombie = False
          gifts = randint(1,Xp)
          gifts  = gifts + 4
          bandages = bandages + gifts
          print(f"you defeat the big skeleton and recive {gifts} more bandages")
          print("prepare for your next battle")
          Xp = Xp + 2
          wins = wins + 1
          Health = Health + 10
          sleep(0.5)
else: #lose screen, shows what you did and how much bandages left
    sleep(1)
    os.system('cls')
    print(f"you died after killing {wins} enemies")
    print(f"you were level {Xp-5}")
    print(f"you had {bandages} bandages left")
    if Xp >= 5:
        print("That was not bad")
    elif Xp <= 2:
        print("that was terrible")
    elif Xp >= 10:
        print("very well done")
    else:
        print("i don't have a response to your skill")
    print("please play again")