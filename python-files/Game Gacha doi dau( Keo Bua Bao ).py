print("Nhập Kéo Búa Bao")
while True:
    from random import randint
    a = input()
    maytinh = randint(0,2)
    print("Người chơi chọn " + a)
    if maytinh == 0:
        maytinh = "Kéo"
    if maytinh == 1:
        maytinh = "Búa"
    if maytinh == 2:
        maytinh = "Bao"
    print( "Máy tính chọn " + maytinh)
    if a == maytinh:
        print("Hòa")
    elif a == "Kéo":
        if maytinh == "Búa":
            print("gà vãi lon")
        else:
            print("chỉ là nhường thôi")
    elif a == "Búa":
        if maytinh == "Kéo":
            print("chỉ là nhường thôi")
        else:
            print("gà vãi lon")
    elif a == "Bao":
        if maytinh == "Kéo":
            print("gà vãi lon")
        else:
            print("chỉ là nhường thôi")
    elif "bye" in a:
        break
    else:
        print("Nhap lai")