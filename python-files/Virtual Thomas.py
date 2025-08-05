words = [["is", "is not"], ["can", "cannot"], ["does", "does not"],
         ["will", "will not"], ["do", "don't"], ["like", "don't like"]]

youSay = ""
heSays = ""

while youSay !="X":

    youSay=input("Enter the phrase you want to say to Thomas\n\n")

    for word in range (0,len(words)):
        if (youSay.find (words[word][0])!=-1):
            heSays = youSay.replace (words[word][0], words[word][1])
            break
        
    heSays = heSays.upper ()

    print("\nSo you're saying " + heSays)
    print ("\n")