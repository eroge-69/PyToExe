l=list(input('Enter your list:').split(','))
opt=input(('-Menue\n1-append\n2-extend\n3-insert\n4-accend\n5-decend\nEnter your option:'))
if opt=='1':
    n=input('enter the item to append:')
    l.append(n)
    print(l)
elif opt=="2":
    n=list(input('enter the list to extend:').split(','))
    l.extend(n)
    print(l)
elif opt=="3":
    i=int(input("enter the index:"))
    n=input('enter the item to insert:')
    l.insert(i,n)
    print(l)
elif opt=="4":
    l.sort()
    print(l)
elif opt=="5":
    l.sort(reverse=True)
    print(l)