# Python encoder
import sys
# Text's style and color variables :
boldStyle = '\033[1m'
italicStyle = '\033[3m'
underLine = '\33[4m'
green = '\033[32m'
blue = '\033[34m'
red = '\033[31m'
reset = '\033[0m'
# Console's color variables :
greenBack = '\033[42m'
blueBack = '\033[44m'
redBack = '\033[41m'
# General variables
writingList = []
# Ciphering directories :
MorseCodeDirectory = {'A':'.- ', 'B':'-... ', 'C':'-.-. ', 'D':'-.. ', 'E':'. ', 'F':'..-. ', 'G':'--. ', 'H':'.... ', 'I':'.. ', 'J':'.--- ',
                      'K':'-.- ', 'L':'.-.. ', 'M':'-- ', 'N':'-. ', 'O':'--- ', 'P':'.--. ', 'Q':'--.- ', 'R':'.-. ', 'S':'... ', 'T':'- ',
                      'U':'..- ', 'V':'...- ', 'W':'.-- ', 'X':'-..- ', 'Y':'-.-- ', 'Z':'--.. ', '1':'.---- ', '2':'..--- ', '3':'...-- ', '4':'....- ',
                      '5':'..... ', '6':'-.... ', '7':'--... ', '8':'---.. ', '9':'----. ', '0':'---- ', ' ':'  '
                      }

BinaryCodeDirectory = {'A':'00000 ', 'B':'00001 ', 'C':'00010 ', 'D':'00011 ', 'E':'00100 ', 'F':'00101 ', 'G':'00110 ', 'H':'00111 ', 'I':'01000 ', 'J':'01001 ',
                      'K':'01010 ', 'L':'01011 ', 'M':'01100 ', 'N':'01101 ', 'O':'01110 ', 'P':'01111 ', 'Q':'10000 ', 'R':'10001 ', 'S':'10010 ', 'T':'10011 ',
                      'U':'10100 ', 'V':'10101 ', 'W':'10110 ', 'X':'10111 ', 'Y':'11000 ', 'Z':'11001 ', '1':'0001# ', '2':'0010# ', '3':'0011# ', '4':'0100# ',
                      '5':'0101# ', '6':'0110# ', '7':'0111# ', '8':'1000# ', '9':'1001# ', '0':'0000# ', ' ':'  '
                      }

CaesarCodeDirectory = {'A':'x', 'B':'y', 'C':'z', 'D':'a', 'E':'b', 'F':'c', 'G':'d', 'H':'e', 'I':'f', 'J':'g',
                      'K':'h', 'L':'i', 'M':'j', 'N':'k', 'O':'l', 'P':'m', 'Q':'n', 'R':'o', 'S':'p', 'T':'q',
                      'U':'r', 'V':'s', 'W':'t', 'X':'u', 'Y':'v', 'Z':'w', '1':'8', '2':'9', '3':'0', '4':'1',
                      '5':'2', '6':'3', '7':'4', '8':'5', '9':'6', '0':'7', ' ':'  '
                      }
# Introduction :
print("\t\t\t\t" + green + boldStyle + underLine +"Welcome " + reset)
print(boldStyle + blue + "This program is working as a text encoder ,\n it will transfer any data you enter into an encrypted code depending on what encryption method you have chosen " + reset)
print(red + boldStyle +'The text must be latin or numbers only' + reset)
print(red + boldStyle +'The text will be stored in a text file in a folder called Encrypted Files in your C: drive' + reset)
print(boldStyle + 'Enter the text you want to encrypt : \n' + reset)
# Taking the input :
userText = input()
userText_lowerCase = userText.upper()
print(boldStyle + 'Enter the number of the enctypting method you want : ' + reset)
print(boldStyle + green + '1 _' + reset + boldStyle + blue + ' Morse code :' + reset)
print('	The famous Morse code which convert letters and numbers into Dots and Dashes')
print(boldStyle + green + '2 _' + reset + boldStyle + blue + ' Binary code :' + reset)
print('	This one will covert the text into 0s and 1s according to premade directory')
print(boldStyle + green + '3 _' + reset + boldStyle + blue + ' Caesar cipher :' + reset)
print('	This one will code the text by shifting the letters and numbers by a fixed amount of steps')
userEncryptionMethodeNum = input()
# functionS to encrypt :
# Morse function
if userEncryptionMethodeNum == str(1) :
    def MorseEncrypter (inputText):
        for letter in range(len(inputText)) :
            for i in MorseCodeDirectory.keys() :
                if inputText[letter] == i :
                    print(boldStyle + green + MorseCodeDirectory.get(i,0) , end= ' ' + reset)
                    writingList.append(MorseCodeDirectory.get(i,0))
    print(boldStyle + '\n The Encrypted text is : \n')
    MorseEncrypter(userText_lowerCase)
# Binary function
if userEncryptionMethodeNum == str(2) :
    def BinaryEncrypter (inputText):
        for letter in range(len(inputText)) :
            for i in BinaryCodeDirectory.keys() :
                if inputText[letter] == i :
                    print(boldStyle + green + BinaryCodeDirectory.get(i,0) , end= ' ' + reset)
                    writingList.append(BinaryCodeDirectory.get(i,0))
    print(boldStyle + '\n The Encrypted text is : \n')
    BinaryEncrypter(userText_lowerCase)
# Caesar function
if userEncryptionMethodeNum == str(3) :
    def CaesarEncrypter (inputText):
        for letter in range(len(inputText)) :
            for i in CaesarCodeDirectory.keys() :
                if inputText[letter] == i :
                    print(boldStyle + green + CaesarCodeDirectory.get(i,0) , end= ' ' + reset)
                    writingList.append(CaesarCodeDirectory.get(i,0))
    print(boldStyle + '\n The Encrypted text is : \n')
    CaesarEncrypter(userText_lowerCase)
#print(writingList)

# Storing files in the PC :
print(boldStyle + ' \n Enter ' + green +  ' 1 ' + reset + boldStyle + ' if you want to store the encrypted text in a file , Enter ' + red + boldStyle + '0' + reset + boldStyle + ' if you do not \n' + reset)
userStoragePermission = input()
if userStoragePermission == str(1) :
    theEncryptedFile = open('C:\\Encrypted Files\\File.txt','a')
    theEncryptedFile.write('\n')
    theEncryptedFile.write(str(writingList))
    theEncryptedFile.close()
    print(boldStyle + 'The text has been stored in the C: drive in your pc' + reset)
else :
    print(boldStyle + 'Thank you for using the program !' + reset)
    sys.exit()