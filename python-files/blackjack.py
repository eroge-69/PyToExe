from enum import EnumMeta
import random
import time
mano=0
manoene=0
game=True 
n=0
num=0.3
print("MY OWN VERSION OF BLACKJACK")
time.sleep(num)
print("you can only not take four times")

while game==True:
  def blackjack():
    global mano
    global num
    accion=input("what are you gonna do?")
    time.sleep(num)
    take=["Take","take","TAKE","TAKE A CARD","I TAKE A CARD","I take a card","I Take A Card"]
    time.sleep(num)
    st=["STAND","stand","Stand","Take a card"]
    time.sleep(num)
    if accion in take:
     carta=random.randint(1,13)
     mano+=carta
     time.sleep(num)
     print("p: ",mano)
    if accion in st:
      print("you don,t take a card")
      time.sleep(num)
      global n
      n+=1
      if n==5:
        time.sleep(num)
        print("You lose ,you didn,t took cards three times")
  blackjack()
  def benemy():
   global manoene 
   accionenemiga=random.randint(1,2)
   if accionenemiga==1:
      carta=random.randint(1,13)
      manoene+=carta
      time.sleep(num)
      print("e: ",manoene)
   else:
     time.sleep(num)
     print("he doesn,t take a card")
  benemy()
  def win():
   if mano<=21:
      if manoene>=21:
         time.sleep(num)
         print("You win")
         global game
         game=False
         pass
   else:  
      if mano>=21:
         time.sleep(num)
         print("You lose")
         game=False
         pass 
      else:
         blackjack()
  win()
  pass
      
      
   
