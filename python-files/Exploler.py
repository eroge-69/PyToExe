import os
print("RvCat ©1995")
print("Если вы украли это с моего компютера то вы плохой человек")
def mainwin() :
    print("╒══════════════════════════════╕")
    print("│        RvNet alpha 0.1       │")
    print("│                              │")
    print("│ s - искать сайты             │")
    print("│ e - выйти                    │")
    print("│                              │")
    print("│                   RvCat ©1995│")
    print("└──────────────────────────────┘")
    use = str(input())
    if use == "s" :
        search = input()
        os.system("cls")
        os.startfile("C:\\Users\\Rvcat\\Desktop\\Rvnet\\Server" + "\\" + search + ".py")
    elif use == "e" :
        exit
    else :
        os.system("cls")
        mainwin()
mainwin()