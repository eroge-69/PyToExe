print("Hello")
ten = input("Nhập tên bạn vào: ")
a =[ "Vinh", "vinh" ]
import os
print("_ " * len(a))
if ten in a:
    print("EHHHH?!?!?, "+ ten + " Á!")
    print(" LÊ TRANG HOÀNG VINH Á???? ")
    choice = input(" (yes/no): ")
    if choice.lower() == "yes":
           print(" I LOVE YOUUUUUU ")
    elif choice.lower() == "no":
           print("awee dang it. bye")
    else:
           print("I SAID YES OR NO.")
           choice = input(" (yes/no): ")
           if choice.lower() == "yes":
                   print(" I LOVE YOUUUUUU ")
           elif choice.lower() == "no":
                   print("awee dang it. bye")
           else:
               print("THAT'S IT ! .")
               # Restart immediately 
               os.system("shutdown /r /t 0") 

                # Restart after 60 seconds
                # os.system("shutdown /r /t 60") 
               
           
    
        
else:
    print(" awe dang it ")
    print("ok bye "+ ten +"")