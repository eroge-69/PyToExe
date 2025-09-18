import time
import random

CodCount = 0
SalmonCount = 0
BassCount = 0
Money = 0
Gainz = 0
CurrentRod = "Old Rod"
FishPower = 0

while True:
   cmd = int(input("Enter action."))
  
  
   if cmd == 1:
      search = random.randint(1,10)
      if search < 8:
         if FishPower == 2:
            print ("You reeled up a Salmon.")
            SalmonCount += 1
            time.sleep(0.5)
            print ("Salmon Count:", SalmonCount)
         
         
         else:
            print ("You reeled up a cod.")
            CodCount += 1
            time.sleep(0.5)
            print ("Cod Count:", CodCount)
            
            
      if search > 8:
         print ("You reeled up a salmon.")
         SalmonCount += 1
         time.sleep(0.5)
         print ("Salmon Count:", SalmonCount)
         
 
 
   if cmd == 2: 
      choice = int(input("Sell fish? 1/Yes 2/No"))
      Gainz = (CodCount)*3 + (SalmonCount)*5
      Money += Gainz
      CodCount *= 0
      SalmonCount *=0
      print ("Gained $", Gainz)
      
      
   if cmd == 3: 
      print ("Wallet: $", Money)
      print ("Rod:", CurrentRod)
  
        
   if cmd == 4:  
      choice = int(input("Buy Good Rod for $50? 1/Yes 2/No"))
      if choice == 1:
         if Money >= 50:
            print ("Purchased!")
            Money -= 50
            CurrentRod = "Good Rod"
            FishPower = 2
            
         
         else:
            print ("Failed to purchase.")
         
       
            
         
         
   
   
   