import time
import random
print('Try to add same number of tops and bottoms for better experience')
time.sleep(0.2)
#List of Tops
print('How Many Tops You have?')
time.sleep(0.2)
topc=int(input(":"))
count=1
topl=[]
while count<=topc:
    print('Enter your',count,'st Top:')
    time.sleep(0.2)
    top=input(':')
    topl.append(top)
    count+=1
time.sleep(0.2)
#--------------------------------------
time.sleep(0.2)


#List of Bottoms

print("How Many Bottoms You have?")
time.sleep(0.2)
botc = int(input(": "))
count = 1
botl = []
while count <= botc:
    print("Enter your", count, "Bottom:")
    time.sleep(0.2)
    bot = input(": ")
    botl.append(bot)
    count += 1
time.sleep(0.2)

#--------------------------------------
setn=1
random.shuffle(topl)
random.shuffle(botl)
print('Here are your sets')
for topp,bott in zip(topl, botl): 
    time.sleep(0.2)
    print('Set:',setn)
    setn+=1
    time.sleep(0.2)
    print('Top:',topp,'+','Bottom:', bott)
    time.sleep(0.2)


time.sleep(1000000)
print('Thnx')

