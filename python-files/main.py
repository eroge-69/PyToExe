import pytesseract,pyautogui,re,subprocess,os,sys
from PIL import Image
from time import sleep
from pyautogui import moveTo
from pynput import keyboard
from PIL import ImageDraw
from configparser import ConfigParser

CoordinatesEditing = [
    [None, None, None, None], #0
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],  #4 Baldi notebook only
    [None, None, None, None]  #5 Equasion
]

CoordinatesDefault = [
    [783, 365, 60, 45], #0
    [783, 421, 60, 45],
    [783, 478, 60, 45],
    [783, 537, 60, 45],
    [783, 595, 60, 45],  #4 Baldi notebook only
    [736, 265, 190, 50]  #5 Equasion
]

Coordinates = [
    [None, None, None, None], #0
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],  #4 Baldi notebook only
    [None, None, None, None]  #5 Equasion
]

MouseCoordinatesDefault = [
    [752, 386],
    [752, 442],
    [752, 497],
    [752, 557],
    [752, 613]  # Baldi mode only
]

MouseCoordinatesEditing = [
    [None, None],
    [None, None],
    [None, None],
    [None, None],
    [None, None]

]

MouseCoordinates = [
    [None, None],
    [None, None],
    [None, None],
    [None, None],
    [None, None]

]


cycle = 3
imgFiller = Image.open("fillerImage.png")
test4 = 0.25

test5 = 0.05

##########################################################################################
# READING DATA FROM SAVED FILE

#in case of empty file

if Coordinates == [None]:
    Coordinates = MouseCoordinatesDefault
if MouseCoordinates == [None]:
    MouseCoordinates = MouseCoordinatesDefault

try:
    with open('coordinates.txt', 'r') as file:
        lines = [line.strip() for line in file]
        for i in range(0, 6):
            temp1 = lines[i]
            temp1 = temp1.replace("[", "")  # BOX COORDINATES
            temp1 = temp1.replace("]", "")
            temp1 = list(map(int, temp1.split(',')))
            Coordinates[i] = temp1
except FileNotFoundError:
    print("Coordinates file not found, loaded data from default list")
except ValueError:
    print("Coordinates file contains different type of data or empty, loaded data from default list")

try:
    with open('mouseCoordinates.txt', 'r') as file1:
        lines1 = [line1.strip() for line1 in file1]
        for i in range(0, 5):
            temp2 = lines1[i]  # MOUSE CLICKS COORDINATES
            temp2 = temp2.replace("[", "")
            temp2 = temp2.replace("]", "")
            temp2 = list(map(int, temp2.split(',')))
            MouseCoordinates[i] = temp2
except FileNotFoundError:
    print("Mouse coordinates file not found or empty, loaded data from default list")
except ValueError:
    print("Mouse coordinates file contains different type of data or empty, loaded data from default list")

with open('SavedSettings.ini', 'r') as file:
    config = ConfigParser()
    config.read('SavedSettings.ini')
    BaldiMode = config.getboolean('SavedSettings', 'baldimode')
    DoNotebookDupe = config.getboolean('SavedSettings', 'donotebookdupe')
    Range = config.getint('SavedSettings', 'range')
###############################################################################################################
# TEST SCREENSHOT

def help():
    print('back / b - RETURN BACK 1 STEP')
    print("")
    print('inside of "help... "')
    print("     default / de - Set saved files to default in case of corruption or if they are missing")
    print(
        "     testss / ss - Show current place where screenshots for Optical Character Recognition, and coordinates to press correct answer (futher OCR, box - screenshot boxes, dot - places to click correct answer) \n     COLORED AS: 0 - ROYGBV - 5 ")
    print("     baldi / ba - Toggle baldi mode aka 5th answer")
    print(
        "     notebookdupe / dupe / du - Toggle dropping notebook right before answering last question so you can get items and save notebook")
    print("     status / stat / st - Show current settings applied")
    print("")
    print("refresh / re - IMPORTANT to apply changes from saved files in running script, use this command(?)")
    print(
        r'save / sa - IMPORTANT to save edited values in "edit" OR other settings such as baldi or notebookdupe mode inside of file - you need to save them here')
    print("     box > coordinates.txt")
    print("     dot > mouseCoordinates.txt")
    print("     settings > SavedSettings.ini")
    print("")
    print("edit / ed - Simple editor to adjust boxes and dots")
    print(
        '     Choose box or dot (box - Places where screenshots of equasion/answers are took, dot - places to click correct answer)')
    print('         inside of "Which (dot OR box) IN RANGE OF 0-4!: "')
    print('             box - 0, 1, 2, 3, 4, 5')
    print("             4 - BaldiMode only, 5 - EQUASION ")
    print('             dot - 0, 1, 2, 3, 4')
    print('')
    print('             inside of "x/y/w/h > +- > int "')
    print('                 testss / ss - COLORED AS: 0 - ROYGBV - 5')
    print('')
    print('                 box variant = X, Y, W-width, H-height | + OR - | Value')
    print('                 dot variant = X, Y | + / - | Value')
    print('                example: x-10, x+123, h+1000, w-100 and ext')

Color = ["red", "orange", "yellow", "green", "blue", "violet"]
def TestScreenshot():
    tempss = pyautogui.screenshot()
    img = Image.new("RGB", (tempss.width, tempss.height))
    img.paste(tempss)
    img1 = ImageDraw.Draw(img)

    for i in range(0, 6):
        x, y = Coordinates[i][0:2:]
        if i == 5:
            xx = x + 190
            yy = y + 50
        else:
            Wtest = Coordinates[i][2:3:]
            Htest = Coordinates[i][3:4:]
            Wtest = Wtest[0]
            Htest = Htest[0]                    #Screenshot boxes
            xx = x + Wtest
            yy = y + Htest

            AnswerTemp1 = MouseCoordinates[i][0:1:]
            AnswerTemp2 = MouseCoordinates[i][1:2:]
            AnswerX = AnswerTemp1[0]
            AnswerY = AnswerTemp2[0]
            AnswerXX = AnswerX + 2              #Answer dots
            AnswerYY = AnswerY + 2
            AnswerShape = [AnswerX, AnswerY, AnswerXX, AnswerYY]


        shape = [x, y, xx, yy]
        img1.rectangle(shape, outline=Color[i], width=1)
        if i < 5:
            img1.rectangle(AnswerShape, outline=Color[i], width=1)

    img.show()

def TestScreenshotEditing():

    tempss = pyautogui.screenshot()
    img = Image.new("RGB", (tempss.width, tempss.height))
    img.paste(tempss)
    img1 = ImageDraw.Draw(img)

    for i in range(0, 6):
        Editingx, Editingy = CoordinatesEditing[i][0:2:]
        if i == 5:
            TempEditingEqW = CoordinatesEditing[5][2:3:]
            TempEditingEqH = CoordinatesEditing[5][3:4:]

            EditingEqW = TempEditingEqW[0]
            EditingEqH = TempEditingEqH[0]

            Editingxx = Editingx + EditingEqW
            Editingyy = Editingy + EditingEqH
        else:
            EditingWtest = CoordinatesEditing[i][2:3:]
            EditingHtest = CoordinatesEditing[i][3:4:]
            EditingWtest = EditingWtest[0]
            EditingHtest = EditingHtest[0]                    #Screenshot boxes
            Editingxx = Editingx + EditingWtest
            Editingyy = Editingy + EditingHtest

            EditingAnswerTemp1 = MouseCoordinatesEditing[i][0:1:]
            EditingAnswerTemp2 = MouseCoordinatesEditing[i][1:2:]
            EditingAnswerX = EditingAnswerTemp1[0]
            EditingAnswerY = EditingAnswerTemp2[0]
            EditingAnswerXX = EditingAnswerX + 2              #Answer dots
            EditingAnswerYY = EditingAnswerY + 2
            AnswerShape = [EditingAnswerX, EditingAnswerY, EditingAnswerXX, EditingAnswerYY]


        shape = [Editingx, Editingy, Editingxx, Editingyy]
        img1.rectangle(shape, outline=Color[i], width=1)
        if i < 5:
            img1.rectangle(AnswerShape, outline=Color[i], width=1)

    img.show()
##################################################################################################
# AHK V2
PathToAhkExecutable = sys.prefix + r"/v2/AutoHotkey64.exe"
print(PathToAhkExecutable)

ahk_exe_path = PathToAhkExecutable
ahk_script_path = r"notebook dupe v1 simple.ahk"
if not os.path.exists(ahk_exe_path):
    print(f"Error: AutoHotkey executable not found at {ahk_exe_path}")
elif not os.path.exists(ahk_script_path):
    print(f"Error: AHK script not found at {ahk_script_path}")          ###RUNNING AHKV2 PROGRAM
process = subprocess.Popen([ahk_exe_path, ahk_script_path])

pytesseract.pytesseract.tesseract_cmd = sys.prefix + R"\Tesseract OCR\tesseract.exe"


##################################################################################################
#SETTINGS

while True:
    userInput = input("\"help\"... ").lower()

    if userInput == "help":
        help()

    elif userInput == "default" or userInput == "de":
        userInput = input("Set to default: \nbox / dot ").lower()
        if userInput == "box":
            with open('coordinates.txt', 'w') as file:
                for i in CoordinatesDefault:
                    file.write(str(i) + "\n")
                print("\"coordinates.txt\" set to default ",)
        elif userInput == "dot":
            with open('mouseCoordinates.txt', 'w') as file:
                for i in MouseCoordinatesDefault:
                    file.write(str(i) + "\n")
                print("\"mouseCoordinates.txt\" set to default ",)
        elif userInput == "settings":
            config = ConfigParser()
            config["SavedSettings"] = {
                'BaldiMode': False,
                "DoNotebookDupe": False,
                "Range": 3
            }
            with open("SavedSettings.ini", "w") as f:
                config.write(f)
            print("\"SavedSettings.ini\" set to default ", )

    elif userInput == "testss" or userInput == "ss":
        TestScreenshot()

    elif userInput == "baldi" or userInput == "ba":
        if BaldiMode == False:
            BaldiMode = True
            Range = 5
            print("Baldi mode: ", BaldiMode)
            continue
        elif BaldiMode == True:
            BaldiMode = False
            Range = 4
            print("Baldi mode: ", BaldiMode)
            continue

    elif userInput == "notebookdupe" or userInput == "dupe" or userInput == "du":
        if DoNotebookDupe == True:
            DoNotebookDupe = False
            print("DoNotebookDupe mode: ", DoNotebookDupe)
        elif DoNotebookDupe == False:
            DoNotebookDupe = True
            print("DoNotebookDupe mode: ", DoNotebookDupe)

    elif userInput == "status" or userInput == "st" or userInput == "stat":
        print("Baldi mode: ", BaldiMode)
        print("DoNotebookDupe: ", DoNotebookDupe)
        print("Solve equasion times per activation: ", cycle)

    elif userInput == "save" or userInput == "sa":
        userInput = input("Are you sure? y/n: ").lower()
        if userInput == "y":
            with open('SavedSettings.ini', 'w') as file:
                config["SavedSettings"]['BaldiMode'] = str(BaldiMode)
                config["SavedSettings"]['doNotebookDupe'] = str(DoNotebookDupe)
                config["SavedSettings"]["Range"] = str(Range)
                config.write(file)
            print("Saved options to \"SavedSettings.ini\" ",end="")
            file.close()

            with open('coordinates.txt', 'w') as file:
                if Coordinates[0][0] == None:
                    for i in CoordinatesEditing:
                        file.write(str(i) + "\n")
                    print("Saved \"CoordinatesEditing\" ",end="")
                else :
                    for i in Coordinates:
                        file.write(str(i) + "\n")
                    print("Saved \"Coordinates\" ", end="")
                file.close()

            with open('mouseCoordinates.txt', 'w') as file:
                if MouseCoordinates[0][0] == None:
                    for i in MouseCoordinatesEditing:
                        file.write(str(i) + "\n")
                    print("\"MouseCoordinatesEditing\" ")

                else:
                    for i in MouseCoordinates:
                        file.write(str(i) + "\n")
                    print("Saved \"MouseCoordinates\" ")
                file.close()
                print("Don't forget to refresh to apply chnges to already running script")
        else:
            print("Reverted")
            continue

    elif userInput == "edit" or userInput == "ed":
        while True:
            userInput = input("box, dot >>> ").lower()
            CoordinatesEditing = Coordinates
            MouseCoordinatesEditing = MouseCoordinates

            if userInput == "back" or userInput == "b":
                break

            elif userInput == "help":
                help()

            elif userInput == "dot":
                with open('mouseCoordinates.txt', 'r') as file:
                    lines = [line.strip() for line in file]
                    for i in range(0, 5):
                        temp1 = lines[i]
                        temp1 = temp1.replace("[", "")
                        temp1 = temp1.replace("]", "")
                        temp1 = list(map(int, temp1.split(',')))
                        MouseCoordinatesEditing[i] = temp1

                    while True:
                        userInputInt = input("Which dot IN RANGE OF 0-4!: ")

                        if userInputInt == "back" or userInputInt == "b":
                            break

                        elif userInputInt == "help":
                            help()
                            continue

                        try:
                            userInputInt = int(userInputInt)
                        except ValueError:
                            print("ValueError")
                            continue
                        except TypeError:
                            print("TypeError")
                            continue

                        try:
                            MouseCoordinatesEditing[userInputInt] = MouseCoordinatesEditing[userInputInt]
                        except IndexError:
                            print("IndexError")
                            continue
                        xDot = MouseCoordinatesEditing[userInputInt][0]
                        yDot = MouseCoordinatesEditing[userInputInt][1]

                        while True:
                            print(MouseCoordinatesEditing[userInputInt])
                            userInput = input("x/y > +- > int ").lower()

                            if userInput == "back" or userInput == "b":
                                break
                            elif userInput == "testss" or userInput == "ss":
                                TestScreenshotEditing()

                            elif userInput == "help":
                                help()
                                continue

                            try:

                                ValidationDirection = userInput[0:1:]
                                ValidationOperation = userInput[1:2:]
                                ValidationValue = userInput[2:6:]

                                ValidationDirection = str(ValidationDirection)
                                ValidationOperation = str(ValidationOperation)
                                ValidationValue = int(ValidationValue)
                            except ValueError:
                                print("ValueError")
                                continue

                            else:
                                DirectionD = userInput[0:1:]
                                OperationD = userInput[1:2:]
                                ValueD = userInput[2:6:]

                                ValueD = int(ValueD)

                                if DirectionD == "x":
                                    if OperationD == "-":
                                        xDot = xDot - ValueD
                                        MouseCoordinatesEditing[userInputInt][0] = xDot
                                    elif OperationD == "+":
                                        xDot = xDot + ValueD
                                        MouseCoordinatesEditing[userInputInt][0] = xDot
                                    else:
                                        print("Something went wrong, double check everything1")
                                        continue

                                elif DirectionD == "y":
                                    if OperationD == "-":
                                        yDot = yDot - ValueD
                                        MouseCoordinatesEditing[userInputInt][1] = yDot
                                    elif OperationD == "+":
                                        yDot = yDot + ValueD
                                        MouseCoordinatesEditing[userInputInt][1] = yDot
                                    else:
                                        print("Something went wrong, double check everything2")
                                        continue


            elif userInput == "box":

                with open('coordinates.txt', 'r') as file:
                    lines = [line.strip() for line in file]
                    for i in range(0, 6):
                        temp1 = lines[i]
                        temp1 = temp1.replace("[", "")
                        temp1 = temp1.replace("]", "")
                        temp1 = list(map(int, temp1.split(',')))
                        CoordinatesEditing[i] = temp1

                    while True:
                        userInputInt = input("Which box IN RANGE OF 0-5!: ")

                        if userInputInt == "back" or userInputInt == "b":
                            break

                        elif userInputInt == "help":
                            help()
                            continue

                        try:
                            userInputInt = int(userInputInt)
                        except ValueError:
                            print("ValueError")
                            continue
                        except TypeError:
                            print("TypeError")
                            continue

                        try:
                            CoordinatesEditing[userInputInt] = CoordinatesEditing[userInputInt]
                        except IndexError:
                            print("IndexError")
                            continue
                        xBox = CoordinatesEditing[userInputInt][0]
                        yBox = CoordinatesEditing[userInputInt][1]
                        wBox = CoordinatesEditing[userInputInt][2]
                        hBox = CoordinatesEditing[userInputInt][3]

                        while True:
                            print(CoordinatesEditing[userInputInt])
                            userInput = input("x/y/w/h > +- > int ").lower()

                            if userInput == "back" or userInput == "b":
                                break
                            elif userInput == "testss" or userInput == "ss":
                                TestScreenshotEditing()

                            elif userInput == "help":
                                help()
                                continue

                            try:
                                ValidationDirection = userInput[0:1:]
                                ValidationOperation = userInput[1:2:]
                                ValidationValue = userInput[2:6:]

                                ValidationDirection = str(ValidationDirection)
                                ValidationOperation = str(ValidationOperation)
                                ValidationValue = int(ValidationValue)
                            except ValueError:
                                print("ValueError")
                                continue

                            else:
                                Direction = userInput[0:1:]
                                Operation = userInput[1:2:]
                                Value = userInput[2:6:]

                                Value = int(Value)

                                if Direction == "x":
                                    if Operation == "-":
                                        xBox = xBox - Value
                                        CoordinatesEditing[userInputInt][0] = xBox
                                    elif Operation == "+":
                                        xBox = xBox + Value
                                        CoordinatesEditing[userInputInt][0] = xBox
                                    else:
                                        print("Something went wrong, double check everything1")
                                        continue

                                elif Direction == "y":
                                    if Operation == "-":
                                        yBox = yBox - Value
                                        CoordinatesEditing[userInputInt][1] = yBox
                                    elif Operation == "+":
                                        yBox = yBox + Value
                                        CoordinatesEditing[userInputInt][1] = yBox
                                    else:
                                        print("Something went wrong, double check everything2")
                                        continue

                                elif Direction == "w":
                                    if Operation == "-":
                                        wBox = wBox - Value
                                        CoordinatesEditing[userInputInt][2] = wBox
                                    elif Operation == "+":
                                        wBox = wBox + Value
                                        CoordinatesEditing[userInputInt][2] = wBox
                                    else:
                                        print("Something went wrong, double check everything3")
                                        continue

                                elif Direction == "h":
                                    if Operation == "-":
                                        hBox = hBox - Value
                                        CoordinatesEditing[userInputInt][3] = hBox
                                    elif Operation == "+":
                                        hBox = hBox + Value
                                        CoordinatesEditing[userInputInt][3] = hBox
                                    else:
                                        print("Something went wrong, double check everything4")
                                        continue
                                else:
                                    print("Something went wrong, double check everything5")
                                    continue

    elif userInput == "refresh" or userInput == "re":

        with open('coordinates.txt', 'r') as file:
            lines = [line.strip() for line in file]
            for i in range(0, 6):
                temp1 = lines[i]
                temp1 = temp1.replace("[", "")  # BOX COORDINATES
                temp1 = temp1.replace("]", "")
                temp1 = list(map(int, temp1.split(',')))
                Coordinates[i] = temp1

        with open('mouseCoordinates.txt', 'r') as file1:
            lines1 = [line1.strip() for line1 in file1]
            for i in range(0, 5):
                temp2 = lines1[i]  # MOUSE CLICKS COORDINATES
                temp2 = temp2.replace("[", "")
                temp2 = temp2.replace("]", "")
                temp2 = list(map(int, temp2.split(',')))
                MouseCoordinates[i] = temp2

        config = ConfigParser()
        config.read('SavedSettings.ini')
        BaldiMode = bool(config["SavedSettings"]['BaldiMode'])
        doNotebookDupe = bool(config["SavedSettings"]['doNotebookDupe'])
        Range = int(config["SavedSettings"]['Range'])
        print("Refreshed")

    ############################################################################################
    # SCRIPT

    elif userInput == "":
        print("press F3 to run script")

        COMBINATIONS = [
            {keyboard.Key.f3}
        ]
        current = set()


        def execute():

            cycle = 3

            pyautogui.press("F22")
            while cycle > 0:
                imgsMergedResult = [None, None, None, None]
                imgsMerged = [None, None, None, None]
                imgs = [None, None, None, None]

                if BaldiMode:
                    imgsMergedResult.append(None)
                    imgsMerged.append(None)
                    imgs.append(None)
                    # print("!1")

                ##############################################################################################

                for i in range(0, Range):
                    imgs[i] = pyautogui.screenshot(region=(Coordinates[i]))


                if BaldiMode:
                    imgs[4] = pyautogui.screenshot("img4.jpg", region=(Coordinates[4]))

                for i in range(0, Range):
                    # print("!4")
                    # imgs[i].show()
                    imgsMerged[i] = Image.new('RGB', (imgFiller.width + imgs[i].width, imgFiller.height))
                    imgsMerged[i].paste(imgFiller, (0, 0))
                    imgsMerged[i].paste(imgs[i], (imgFiller.width, 0))
                    imgsMerged[i] = imgsMerged[i].convert("L")
                    # imgsMerged[i].show()

                for i in range(0, Range):
                    # imgsMerged[i].show()
                    temp = pytesseract.image_to_string(imgsMerged[i], lang='arimo')  # ,config = custom_oem)
                    temp = temp.replace("6", "", 1)
                    temp = temp.replace(" ", "")

                    try:
                        imgsMergedResult[i] = int(temp)
                    except ValueError:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!error")

                ##########################################################################################################################################

                imgEquasionTemp = pyautogui.screenshot(region=(Coordinates[5]))

                imgEquasion = Image.new('RGB', (imgFiller.width + imgEquasionTemp.width, imgFiller.height))
                imgEquasion.paste(imgFiller, (0, 0))
                imgEquasion.paste(imgEquasionTemp, (imgFiller.width, 0))
                # imgEquasion.show()

                eqTemp = pytesseract.image_to_string(imgEquasion, lang='arimo')  # ,config = custom_oem)
                eqTemp = eqTemp.replace("6", "", 1)

                # imgEquasion.show()
                # equasionNum1 = re.match("/.{1-2}+?(?=X/+/-)", imgEquasionResultTemp)

                eqTemp = eqTemp[:-3]

                if eqTemp[0:1] == "-":
                    eqTemp = eqTemp.replace("-", "_", 1)

                EquasionNumTemp = re.match("^[^X/+/-]*", eqTemp)
                Num1Result = EquasionNumTemp[0]

                if Num1Result[0:1] == "_":
                    Num1Result = Num1Result.replace("_", "-", 1)

                start, end = EquasionNumTemp.span()  # get useful info
                end1 = end + 1
                ######################################################################################################################################
                if eqTemp[end:end1] == "X":
                    operation = "X"
                elif eqTemp[end:end1] == "+":
                    operation = "+"
                elif eqTemp[end:end1] == "-":
                    operation = "-"
                else:
                    operation = None

                slice1 = slice(end1, 100)
                Num2Result = eqTemp[slice1]
                # print(imgsMerged[0])

                try:
                    Num1Result = int(Num1Result)
                    Num2Result = int(Num2Result)
                except ValueError:
                    print("ValueError, program stopped")
                    cycle = 0
                    continue

                if operation == "+":
                    CorrectAnswer = Num1Result + Num2Result
                elif operation == "-":
                    CorrectAnswer = Num1Result - Num2Result
                elif operation == "X":
                    CorrectAnswer = Num1Result * Num2Result
                else:
                    print("No match with operation sign")
                int(CorrectAnswer)

                print("Raw data: ", eqTemp, "\nAnswers: ", imgsMergedResult, "\n Recognized with OCR: ", Num1Result,
                      operation, Num2Result, "=", CorrectAnswer)

                if CorrectAnswer == imgsMergedResult[0]:
                    moveTo(MouseCoordinates[0])
                    if DoNotebookDupe:
                        if cycle == 1:
                            pyautogui.press("F21")
                            pyautogui.press("F20")
                            sleep(test4)
                            pyautogui.click()
                        else:
                            pyautogui.press("F21")
                            pyautogui.click()
                    else:
                        pyautogui.press("F21")
                        pyautogui.click()



                elif CorrectAnswer == imgsMergedResult[1]:
                    moveTo(MouseCoordinates[1])
                    if DoNotebookDupe:
                        if cycle == 1:
                            pyautogui.press("F21")
                            pyautogui.press("F20")
                            sleep(test4)
                            pyautogui.click()
                        else:
                            pyautogui.press("F21")
                            pyautogui.click()
                    else:
                        pyautogui.press("F21")
                        pyautogui.click()


                elif CorrectAnswer == imgsMergedResult[2]:
                    moveTo(MouseCoordinates[2])
                    if DoNotebookDupe:
                        if cycle == 1:
                            pyautogui.press("F21")
                            pyautogui.press("F20")
                            sleep(test4)
                            pyautogui.click()
                        else:
                            pyautogui.press("F21")
                            pyautogui.click()
                    else:
                        pyautogui.press("F21")
                        pyautogui.click()



                elif CorrectAnswer == imgsMergedResult[3]:
                    moveTo(MouseCoordinates[3])
                    if DoNotebookDupe:
                        if cycle == 1:
                            pyautogui.press("F21")
                            pyautogui.press("F20")
                            sleep(test4)
                            pyautogui.click()
                        else:
                            pyautogui.press("F21")
                            pyautogui.click()
                    else:
                        pyautogui.press("F21")
                        pyautogui.click()


                elif BaldiMode:
                    if CorrectAnswer == imgsMergedResult[4]:
                        moveTo(MouseCoordinates[4])
                        if DoNotebookDupe:
                            if cycle == 1:
                                pyautogui.press("F21")
                                pyautogui.press("F20")
                                sleep(test4)
                                pyautogui.click()
                            else:
                                pyautogui.press("F21")
                                pyautogui.click()
                        else:
                            pyautogui.press("F21")
                            pyautogui.click()

                else:
                    print("No match with equasion answer and offered answers")
                cycle -= 1
                sleep(0.5)

                imgsMergedResult.clear()
                imgsMerged.clear()
                imgs.clear()


        def on_press(key):
            if any([key in COMBO for COMBO in COMBINATIONS]):
                current.add(key)
                if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
                    execute()


        def on_release(key):
            if any([key in COMBO for COMBO in COMBINATIONS]):
                current.remove(key)


        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


    else:
        print("Unknown input")