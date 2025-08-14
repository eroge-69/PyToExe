Codes =input("Enter message to decode")
newmsg = []
a = Codes.split()
#print(int(x) / Key )

Key = float(a[0])
a.pop(0)

newletter = float()
for x in a:
    newletter = float(x) / Key
    newletter = newletter 
    match newletter:
        case 25:
            newmsg.append('a')
        case 11:
            newmsg.append('b')
        case 20:
            newmsg.append('c')
        case 29:
            newmsg.append('d')
        case 22:
            newmsg.append('e')
        case 34:
            newmsg.append('f')
        case 12:
            newmsg.append('g')
        case 15:
            newmsg.append('h')
        case 7:
            newmsg.append('i')
        case 3:
            newmsg.append('j')
        case 8:
            newmsg.append('k')
        case 27:
            newmsg.append('l')
        case 24:
            newmsg.append('m')
        case 16:
            newmsg.append('n')
        case 5:
            newmsg.append('o')
        case 21:
            newmsg.append('p')
        case 18:
            newmsg.append('q')
        case 4:
            newmsg.append('r')
        case 2:
            newmsg.append('s')
        case 1:
            newmsg.append('t')
        case 6:
            newmsg.append('u')
        case 9:
            newmsg.append('v')
        case 30:
            newmsg.append('w')
        case 19:
            newmsg.append('x')
        case 17:
            newmsg.append('y')
        case 23:
            newmsg.append('z')
        case 0:
            newmsg.append(' ')
print("".join(newmsg))
