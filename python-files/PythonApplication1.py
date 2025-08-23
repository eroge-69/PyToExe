group1 = [ "IT 1101", "IT 1102", "IT 1103", "IT 1104", "IT 1105", "IT 1106", "IT 1107", "IT 1108"]
group2 = ["IT 2101", "IT 2102", "IT 2103", "IT 2104", "IT 2105", "IT 2106", "IT 2107"]
group3 = ["IT 3101BA", "IT 3102BA", "IT 3103BA"]
group4 = ["IT 3101NT", "IT 3102NT"]
group5 = ["IT 4101BA", "IT 4102BA", "IT 4101NT"]

print("======== GROUP1 ========\n", group1)
print("\n======== GROUP2 ========\n", group2)
print("\n======== GROUP3 ========\n",group3)
print("\n======== GROUP4 ========\n",group4)
print("\n======== GROUP5 ========\n",group5)

userinput = input("\nWhat block are you bro? : ")
if userinput in group1:
    if userinput == "IT 1106":
        print("WOIII WAHHAHAHHAH WATATAPS MGA HATDOGSHEESH *teka nonchalant nga pala ako ya.*\nAnyways, Welcome to BatStateU!")
    else:
        print(f"\nyou are in block {userinput} of Group 1. Welcome to BatStateU!")
elif userinput in group2:
    print(f"\nyou are in block {userinput} of Group 2. Welcome to BatStateU!")
elif userinput in group3:
    print(f"\nyou are in block {userinput} of Group 3. Welcome to BatStateU!")
elif userinput in group4:
    print(f"\nyou are in block {userinput} of Group 4. Welcome to BatStateU!")
elif userinput in group5:
    print(f"\nyou are in block {userinput} of Group 5. Welcome to BatStateU!")
else:
    print(f"\nYour block '{userinput}' do not exist.")
