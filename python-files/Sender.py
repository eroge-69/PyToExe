import random



key = int(random.randint(11, 29))
key2 = int(random.randint(11, 29))
msg = input("Enter message: ")
a = list(msg)

newmsg = []

newmsg.append(str(key * key2))
for x in a:
    match x:
        case 'a':
            newmsg.append(str(25 * key * key2))
        case 'b':
            newmsg.append(str(11 * key * key2))
        case 'c':
            newmsg.append(str(20 * key * key2))
        case 'd':
            newmsg.append(str(29 * key * key2))
        case 'e':
            newmsg.append(str(22 * key * key2))
        case 'f':
            newmsg.append(str(34 * key * key2))
        case 'g':
            newmsg.append(str(12 * key * key2))
        case 'h':
            newmsg.append(str(15 * key * key2))
        case 'i':
            newmsg.append(str(7 * key * key2))
        case 'j':
            newmsg.append(str(3 * key * key2))
        case 'k':
            newmsg.append(str(8 * key * key2))
        case 'l':
            newmsg.append(str(27 * key * key2))
        case 'm':
            newmsg.append(str(24 * key * key2))
        case 'n':
            newmsg.append(str(16 * key * key2))
        case 'o':
            newmsg.append(str(5 * key * key2))
        case 'p':
            newmsg.append(str(21 * key * key2))
        case 'q':
            newmsg.append(str(18 * key * key2))
        case 'r':
            newmsg.append(str(4 * key * key2))
        case 's':
            newmsg.append(str(2 * key * key2))
        case 't':
            newmsg.append(str(1 * key * key2))
        case 'u':
            newmsg.append(str(6 * key * key2))
        case 'v':
            newmsg.append(str(9 * key * key2))
        case 'w':
            newmsg.append(str(30 * key * key2))
        case 'x':
            newmsg.append(str(19 * key * key2))
        case 'y':
            newmsg.append(str(17 * key * key2))
        case 'z':
            newmsg.append(str(23 * key * key2))
        case ' ':
            newmsg.append('0')

print(" ".join(newmsg))
print("your key is: ", key* key2)
