

class Room:
  def __init__ (self, typ, count, price):
    self.typ = typ
    self.count = count
    self.price = price
roomList = [Room("Single",1,1), Room("Double",2,2), Room("Suite",3,3)]
def get_rooms():

  alignment = 20
  print("Room Type".ljust(alignment), "Count".center(alignment), "Price".rjust(alignment))
  for room in roomList:
    print(room.typ.ljust(alignment), str(room.count).center(alignment), str(room.price).rjust(alignment))
def book_rooms():

  name = input("What is your name? ")
  print("Hello", name , "Here are your options:\n1) Single \n2) Double\n3) Suite")
  choice = int(input("\n Choose your room (1/2/3): "))
  if(choice<1 or choice>3):
    print("Invalid option")
    return
  if(roomList[choice-1].count>0):
    print("Room is avaliable at the price of", roomList[choice-1].price)
    confirm = input("Please enter \"confirm\" to book:").strip().upper()
    if (confirm == "confirm"):
      roomList[choice-1].count-=1
      print("Thank you for your booking. Here is your reciept:\nName:", name,"\nRoom booked:", roomList[choice-1].typ)
    else:
      print("Booking cancelled")
  else:
    print("Room is not avaliable. Please try another option.")



while(True):
  choice = int(input("Options:\n1) Check room availability and prices\n2) Book room\n3) Exit \nInput (1/2/3):"))
  if (choice != 1 and choice !=2 and choice !=3):
    print("Invalid option")
    continue
  if(choice ==3):
    break
  if (choice == 1):
    get_rooms()
  else:
    book_rooms()

