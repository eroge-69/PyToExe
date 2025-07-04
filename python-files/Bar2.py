def checking():
    for i in age:
        if i < 21:
            print("sorry, you are under 21 years old, so I can't serve you! Please Next One...")
            break
    else:
         print('how can I help you?')

def allprog():
    print('hello')
    x = int(input('how many are you? '))
    print("How Old are you? ")
    global age
    age = list()
    for i in range(x):
        age.append(int(input('person' + str(i + 1) + '? ')))
    v = input("Is/are ages: " + str(age) + " correct?(Y/N) ")
    if v == 'Y' or v =='y':
        print('confirmed')
        checking()
        
    else:
        print(age)
        wrong = int(input('which one is wrong? '))
        for i in range(x):
            if wrong == age[i]:
                age[i] = int(input('correct age?'))
                checking()
                break
                
        else:
            print('NOT MATCH!')
existing = "Y"
while existing == 'Y' or existing == 'y':
    allprog()
    existing = input('Is there ANY?(Y/N)')
else:
    print("Good Luck!")