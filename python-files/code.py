print("1:Encrypt/2:Decrypt")
option=input("Enter 1 or 2:")

while option != "1" and option != "2":
    print("Invalid option! Please enter 1 or 2.")
    print("1:Encrypt/2:Decrypt")
    option=input("Enter 1 or 2:")
    
if option=="1":
     print("Enter the message for encryption:")
     message=input()
     print("Enter the length of the message:")
     length = input()
     print("Each letter of the normal alphabet will be displayed.Then you must enter the coresponding letter in the depryption alphabet:")
     A = input("A")
     B = input("B")
     C = input("C")
     D = input("D")
     E = input("E")
     F = input("F")
     G = input("G")
     H = input("H")
     I = input("I")
     J = input("J")
     K = input("K")
     L = input("L")
     M = input("M")
     N = input("N")
     O = input("O")
     P = input("P")
     Q = input("Q")
     R = input("R")
     S = input("S")
     T = input("T")
     U = input("U")
     V = input("V")
     W = input("W")
     X = input("X")
     Y = input("Y")
     Z = input("Z")
     llist = list(message)
     for letter in llist:
        if letter == "A":
            print(A)
        elif letter == "B":
            print(B)
        elif letter == "C": 
            print(C)
        elif letter == "D": 
            print(D)
        elif letter == "E": 
            print(E)
        elif letter == "F": 
            print(F)
        elif letter == "G": 
            print(G)
        elif letter == "H": 
            print(H)
        elif letter == "I": 
            print(I)
        elif letter == "J": 
            print(J)
        elif letter == "K": 
            print(K)
        elif letter == "L": 
            print(L)
        elif letter == "M": 
            print(M)
        elif letter == "N": 
            print(N)
        elif letter == "O": 
            print(O)
        elif letter == "P": 
            print(P)
        elif letter == "Q": 
            print(Q)
        elif letter == "R":
            print(R)
        elif letter == "S": 
            print(S)
        elif letter == "T": 
            print(T)
        elif letter == "U": 
            print(U)
        elif letter == "V": 
            print(V)
        elif letter == "W": 
            print(W)
        elif letter == "X": 
            print(X)
        elif letter == "Y":
            print(Y)
        elif letter == "Z": 
            print(Z)
            
elif option=="2":
    print("Enter the coced message:")
    message=input()
    print("Each letter of the depryption alphabet will be displayed.Then you must enter the coresponding letter in the normal alphabet:")
    A = input("A")
    B = input("B")
    C = input("C")
    D = input("D")
    E = input("E")
    F = input("F")
    G = input("G")
    H = input("H")
    I = input("I")
    J = input("J")
    K = input("K")
    L = input("L")
    M = input("M")
    N = input("N")
    O = input("O")
    P = input("P")
    Q = input("Q")
    R = input("R")
    S = input("S")
    T = input("T")
    U = input("U")
    V = input("V")
    W = input("W")
    X = input("X")
    Y = input("Y")
    Z = input("Z")
    llist = list(message)
    for letter in llist:
       if letter == "A":
           print(A)
       elif letter == "B":
           print(B)
       elif letter == "C": 
           print(C)
       elif letter == "D": 
           print(D)
       elif letter == "E": 
           print(E)
       elif letter == "F": 
           print(F)
       elif letter == "G": 
           print(G)
       elif letter == "H": 
           print(H)
       elif letter == "I": 
           print(I)
       elif letter == "J": 
           print(J)
       elif letter == "K": 
           print(K)
       elif letter == "L": 
           print(L)
       elif letter == "M": 
           print(M)
       elif letter == "N": 
           print(N)
       elif letter == "O": 
           print(O)
       elif letter == "P": 
           print(P)
       elif letter == "Q": 
           print(Q)
       elif letter == "R":
           print(R)
       elif letter == "S": 
           print(S)
       elif letter == "T": 
           print(T)
       elif letter == "U": 
           print(U)
       elif letter == "V": 
           print(V)
       elif letter == "W": 
           print(W)
       elif letter == "X": 
           print(X)
       elif letter == "Y":
           print(Y)
       elif letter == "Z": 
           print(Z)