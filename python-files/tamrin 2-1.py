import colorama
na=input("enter name:  ")    
number=int(input("enter number:  "))  
r1=number
while True:
    if r1<11:
        print (("  "+na+"  ")*number)
        print(colorama.Fore.GREEN,"______"*5,colorama.Fore.RESET)
        r1=r1+number
    else: 
        print (("  "+na+"  ")*(10%number))
        break
    