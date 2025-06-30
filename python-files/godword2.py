
with open("godtongue.txt", "r", encoding="utf-8") as f:
    words = f.read().splitlines()

done = 0
while done == 0:
    keyphrase = input("Enter Question: ")
    time = input("Enter Time in format 00.00:  ")
    wordquestion = input ("Word Count, enter integer or R for random:  ")

    keyphraseconvert = [ord(letter) for letter in keyphrase]
    digits = 1
    for number in keyphraseconvert:
        digits= (digits * number) % 12345678
    keydigits = int((int(digits)  % 12345678)* float(time))
    glossary = words
    messagefromgod = []
    timesrepated = 0
    listofprimes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43]

    if wordquestion == "R":
        wordamount = keydigits % 99
    else:
        wordamount = wordquestion

    while timesrepated != int(wordamount):
        zekeydigits = keydigits * listofprimes[(timesrepated % len(listofprimes))] * (timesrepated + 1)
        timesrepated += 1
        modulokeydigits = round(zekeydigits) % len(glossary)
        messagefromgod.append(glossary[modulokeydigits])
    currentword = 0
    b = 0
    a = 0
    print("God says:")
    print(" ")
    while b <= len(messagefromgod):
        b = a + (((currentword* digits) % 12345678) * listofprimes[(currentword % len(listofprimes))]) % 7
        currentword += 1
        line1 = messagefromgod[a:b]
        a = b
        message = (" ".join(line1))
        print(message)



    if time == 0:
        print("god rests")
    print("   ")



