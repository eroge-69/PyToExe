#Importing nessary libaries
from tkinter import *
import math

#Defining codes for colours that will be used
BLACK = '#000000'
WHITE = '#ffffff'
CREAM = '#fffdd0'
BROWN = '#633311'
RED = '#620014'
DARKGREY = '#6c6c6c'
LIGHTGREY = '#A9A9A9'
GREEN = '#006400'

lColour = WHITE
dColour = BLACK
mColour = DARKGREY
backGroundColour = LIGHTGREY

#Defining contants which will be used in drawing the board and other graphics
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 750

QCANVAS_WIDTH = 700
QCANVAS_HEIGHT = 120

WCANVAS_WIDTH = 400
WCANVAS_HEIGHT = 150

CELL_SIDE = 38
CELL_WIDTH = 2 * CELL_SIDE
CELL_HEIGHT = math.sqrt(3)/2 * CELL_WIDTH

ODD_COLS = 5
TOTAL_COLS = (2*ODD_COLS) - 1
ODD_ROWS = 7
TOTAL_ROWS = (2*ODD_ROWS) - 1

OFF_SETX = (CANVAS_WIDTH/2) - ((ODD_COLS/2 * CELL_WIDTH) + (((ODD_COLS-1)/2) * CELL_SIDE))
OFF_SETY = (CANVAS_HEIGHT/2) - (ODD_ROWS/2 * CELL_HEIGHT)
CIRCLE_RADIUS = 10

#Canvas set up
mainWindow = Tk()
mainWindow.title("Hexdame")
tk = Canvas(mainWindow, width = CANVAS_WIDTH, height = CANVAS_HEIGHT, bg= backGroundColour)
tk.pack()

blMan = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\blackMan.png')
wMan = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\whiteMan.png')
cMan = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\creamMan.png')
rMan = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\redMan.png')
brMan = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\brownMan.png')
crown = PhotoImage(file = 'C:\\Users\\albcr\\OneDrive\\Documents\\pythonStuff\\games\\hexDame\\crownSymbol.png')

dMan = blMan
lMan = wMan

#Other declarances
selectType = 0
pieceType = 0
canBeMoved = 0
turnState = 0

noJumpCount = 0
DRAW_THRESHOLD = 20
gX, gY = 0, 0
ngX, ngY = 0, 0


takenPieceXL,takenPieceYL = 0, 0
takenPieceXR,takenPieceYR = 0, 0
lPRemaining, dPRemaining = 14, 14
boardArray = []

def drawHexagon(centerX, centerY, size, colour):
    colour = str(colour)
    fillColour = ""
    x = []
    y = []

    #Adds zero to the empty lists defined above
    for i in range(0, 6, 1):
        x.append(0)
        y.append(0)

    #Woking out the coordinates of each of the hexagon's edges
    for i in range(0, 6, 1):
        angleDeg = 60 * i
        angleRad = (math.pi)/180 * angleDeg
        x[i] = centerX + size * math.cos(angleRad)
        y[i] = centerY + size * math.sin(angleRad)

    #Deciding which colour to paint hexagon in
    if(colour == '1'):
        fillColour = lColour
    elif(colour == '3'):
        fillColour = mColour
    elif(colour == '2'):
        fillColour = dColour
    else:
        fillColour = colour

    #This will make the perimeter of the hexagon clealy visible
    if(fillColour == BLACK):
        outLineColour = WHITE
    else:
        outLineColour = BLACK

    #This actually creates the hexagon once all the paramters have been worked out 
    tk.create_polygon(x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3], x[4], y[4], x[5], y[5], fill=fillColour, outline = outLineColour, width = 1)
    

#This procedure draws the board on the tk canvas
def boardCreate():
    tk.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill = backGroundColour)
    #Drawing the columns of hexagons with an even column number
    colourNum = 2
    currentY = CELL_HEIGHT/2 + OFF_SETY
    for i in range(0,ODD_ROWS,1):
    #Initilising the intial x and y positions
        currentX = CELL_SIDE+OFF_SETX
        
        for j in range(0, ODD_COLS, 1):
            drawHexagon(currentX, currentY, CELL_SIDE, colourNum)
            manArrangement(currentX, currentY)
            currentX += (1.5*CELL_WIDTH)

            
        currentY += CELL_HEIGHT
        colourNum +=1
        if(colourNum > 3):
            colourNum = 1

    #Drawing the columns with odd column numbers
    colourNum = 1
    currentY = CELL_HEIGHT + OFF_SETY
    for i in range(0, ODD_ROWS-1,1):
        #Initilising the intial x and y positions
        currentX = (CELL_SIDE*2.5) + OFF_SETX
        
        #The number of rows is reduced by one for these columns
        for j in range(0, ODD_COLS-1, 1):
            drawHexagon(currentX, currentY, CELL_SIDE, colourNum)
            manArrangement(currentX, currentY)
            currentX += (1.5*CELL_WIDTH)
            
        currentY += CELL_HEIGHT
        colourNum +=1
        if(colourNum > 3):
            colourNum = 1
    if(turnState == 0):
        tk.create_text(130, 30, text="White player's turn", fill="white", font=('Arial 20'))
    elif(turnState == 1):
        tk.create_text(130, 30, text="Black player's turn", fill="black", font=('Arial 20'))
        

#Procedure has been changed to use array data structure to draw the men is
#appropriate postions
def manArrangement(pCanvasX, pCanvasY):
    global lPRemaining, dPRemaining
    gridX, gridY = getGridCoords(pCanvasX, pCanvasY)
    centerX, centerY = getCanvasCoords(gridX-1, gridY-1)
    #If piece is a king then a crown is drawn ontop of the man

    if(boardArray[gridY-1][gridX-1] == 1):
        tk.create_image(centerX,centerY, image = lMan)
        
    elif(boardArray[gridY-1][gridX-1] == 2):
        tk.create_image(centerX,centerY, image = lMan)
        tk.create_image(centerX,centerY, image = crown)
        
    elif(boardArray[gridY-1][gridX-1] == 3):
        tk.create_image(centerX,centerY, image = dMan)
        
    elif(boardArray[gridY-1][gridX-1] == 4):
        tk.create_image(centerX,centerY, image = dMan)
        tk.create_image(centerX,centerY, image = crown)

    elif(boardArray[gridY-1][gridX-1] == 5 or boardArray[gridY-1][gridX-1] == 6):
        tk.create_oval(centerX-CIRCLE_RADIUS, centerY-CIRCLE_RADIUS, centerX+CIRCLE_RADIUS, centerY+CIRCLE_RADIUS, outline = "BLACK", fill = "GREEN", width = 1)

  
#This data structure will be used to store the status of each space
def arrayCreate():
    global boardArray
    for row in range (0, ODD_ROWS, 1):
        rowArray = []
        columnRange = TOTAL_COLS

            
        for column in range(0, columnRange, 1):
            #0 means space is empty
            #1 means space is occupied by light man
            #2 means space is occupied by light king
            #3 means space is occupied by dark man
            #4 means space is occupied by dark king
            #5 means space is occupied by a non-jumper dot
            #6 means space is occupied by a jumper dot
            
            if(row == 0):
                #3 should normally be passed as a parameter
                rowArray.append(3)
            elif(row == 1) and (column % 2 == 0):
                #3 should normaly be passed as a parameter
                rowArray.append(3)
                
            elif(row == ODD_ROWS-2):
                #1 should normally be passed as a parameter
                rowArray.append(1)
            elif(row == ODD_ROWS-1) and (column % 2 == 0):
                #1 should normally be passed as a parameter
                rowArray.append(1)
            else:
                #0 should normally be passed as a parameter
                rowArray.append(0)
                
        boardArray.append(rowArray)

#This procedure displays the array to see if it is being used as intended
def printArray():
    global boardArray
    for rowArray in boardArray:
        print(rowArray)

#This procedure will clear every 5 or 6 representing a green dot
def clearDots():
    global boardArray
    for i in range(1, TOTAL_COLS + 1, 1):
        for j in range(1, ODD_ROWS+1, 1):
            if(boardArray[j-1][i-1] == 5 or boardArray[j-1][i-1] == 6):
                boardArray[j-1][i-1] = 0


#The functions takes in a row and column number and returns the center x-y grid coordiants of the corrosponding space
def getCanvasCoords(colNum, rowNum):
    if((rowNum < 0) or (rowNum >= TOTAL_ROWS)):
        return -1, -1
    if(colNum % 2 == 0):
        LIMIT = ODD_ROWS
    else:
        LIMIT = ODD_ROWS-1
    if((rowNum < 0) or (rowNum >= LIMIT)):
        return -1000, -1000
    #Checks if colNum is even
    if(colNum % 2 == 0):
        xPos = OFF_SETX + (CELL_WIDTH/2) + (colNum/2 * 3 * CELL_SIDE)
        yPos = OFF_SETY + (CELL_HEIGHT/2) + (rowNum * CELL_HEIGHT)
    else:
        xPos = OFF_SETX + (1.25*CELL_WIDTH) + ((colNum-1)/2 * 3 * CELL_SIDE)
        yPos = OFF_SETY + CELL_HEIGHT + (rowNum * CELL_HEIGHT)
        
    return int(xPos), int(yPos) 

#This function take the x y coordents of a mouse click and returns the x-y grid coordinates of coorisponding space
def getGridCoords(pX,pY):
    gridX=-1000
    gridY=-1000
    for i in range(0, TOTAL_COLS, 1):
        lowerLimitX = OFF_SETX + (0.5*CELL_SIDE) + (i*0.75*CELL_WIDTH)
        upperLimitX = OFF_SETX +  (1.5*CELL_SIDE) + (i*0.75*CELL_WIDTH)
        if(pX < upperLimitX) and (pX > lowerLimitX):
            gridX = i

    if(gridX != -1000):
        if(gridX % 2 == 0):
            for i in range(0, ODD_ROWS, 1):
                lowerLimitY = OFF_SETY + (i*CELL_HEIGHT)
                upperLimitY = OFF_SETY + CELL_HEIGHT + (i*CELL_HEIGHT)
                if(pY < upperLimitY) and (pY > lowerLimitY):
                    #breaks out of loop when the click y value is in the valid range for that space
                    gridY = i
                    break
                
        else:
            for i in range(0, ODD_ROWS-1, 1):
                lowerLimitY = OFF_SETY + (0.5*CELL_HEIGHT) + (i*CELL_HEIGHT)
                upperLimitY = OFF_SETY + (1.5*CELL_HEIGHT) + (i*CELL_HEIGHT)
                if(pY < upperLimitY) and (pY > lowerLimitY):
                    #breaks out of loop when the click y value is in the valid range for that space
                    gridY = i
                    break

    if(gridY == -1000):
        return -1000, -1000
    return gridX+1, gridY+1

#This procedure calculates the spaces that a selected piece could move to
def findLegalCells(gX, gY, pieceType):
    global takenPieceXL, takenPieceYL
    global takenPieceXR, takenPieceYR
    global canBeMoved

    if(gX != -1000):
        if(boardArray[gY-1][gX-1] != 0):
            
            if(boardArray[gY-1][gX-1] == 1 or boardArray[gY-1][gX-1] == 2 or boardArray[gY-1][gX-1] == 4):
                #right move forward 1
                if(gX < TOTAL_COLS):
                    if(gX % 2 == 0):
                        if(boardArray[gY-1][gX+1-1] == 0):
                            boardArray[gY-1][gX+1-1] = 5
                            canBeMoved = 1
                                               
                    elif(gY > 1):
                        if(boardArray[gY-1-1][gX+1-1] == 0):
                            boardArray[gY-1-1][gX+1-1] = 5
                            canBeMoved = 1
                            
                #left move forward 1
                if(gX > 1):
                    if(gX % 2 == 0):
                        if(boardArray[gY-1][gX-1-1] == 0):
                            boardArray[gY-1][gX-1-1] = 5
                            canBeMoved = 1
                                                   
                    elif(gY > 1):
                        if(boardArray[gY-1-1][gX-1-1] == 0):
                            boardArray[gY-1-1][gX-1-1] = 5
                            canBeMoved = 1
                                                   

                #right move forward 2
                if(gX < TOTAL_COLS-1):
                    if(gX % 2 == 0):
                        if((boardArray[gY-1-1][gX+2-1] == 0 and (boardArray[gY-1][gX+1-1] == 3 or boardArray[gY-1][gX+1-1] == 4))\
                        or(boardArray[gY-1][gX-1] == 4 and (boardArray[gY-1][gX+1-1] == 1 or boardArray[gY-1][gX+1-1] == 2))):
                            boardArray[gY-1-1][gX+2-1] = 6
                            canBeMoved = 1
                            takenPieceXR, takenPieceYR = gX+1-1, gY-1

                            
                    elif(gY > 1):
                        if((boardArray[gY-1-1][gX+2-1] == 0 and (boardArray[gY-1-1][gX+1-1] == 3 or boardArray[gY-1-1][gX+1-1] == 4))\
                        or(boardArray[gY-1][gX-1] == 4 and (boardArray[gY-1-1][gX+1-1] == 1 or boardArray[gY-1-1][gX+1-1] == 2))):
                            boardArray[gY-1-1][gX+2-1] = 6
                            canBeMoved = 1
                            takenPieceXR, takenPieceYR = gX+1-1, gY-1-1

                                                
                #left move forward 2
                if(gX > 2):
                    if(gX % 2 == 0):
                        if((boardArray[gY-1-1][gX-2-1] == 0 and (boardArray[gY-1][gX-1-1] == 3 or boardArray[gY-1][gX-1-1] == 4))\
                        or(boardArray[gY-1][gX-1] == 4 and (boardArray[gY-1][gX-1-1] == 1 or boardArray[gY-1][gX-1-1] == 2))):
                            boardArray[gY-1-1][gX-2-1] = 6
                            canBeMoved = 1
                            takenPieceXL, takenPieceYL = gX-1-1, gY-1

                                                    
                    elif(gY > 1):
                        if((boardArray[gY-1-1][gX-2-1] == 0 and (boardArray[gY-1-1][gX-1-1] == 3 or boardArray[gY-1-1][gX-1-1] == 4))\
                        or(boardArray[gY-1][gX-1] == 4 and (boardArray[gY-1-1][gX-1-1] == 1 or boardArray[gY-1-1][gX-1-1] == 2))):
                            boardArray[gY-1-1][gX-2-1] = 6
                            canBeMoved = 1
                            takenPieceXL, takenPieceYL = gX-1-1 , gY-1-1
                            

                                         

            if(boardArray[gY-1][gX-1] == 3 or boardArray[gY-1][gX-1] == 4 or boardArray[gY-1][gX-1] == 2):            
                #right move backward 1
                if(gX < TOTAL_COLS):
                    if(gX % 2 == 0):
                        if(boardArray[gY+1-1][gX+1-1] == 0):
                            boardArray[gY+1-1][gX+1-1] = 5
                            canBeMoved = 1
                                                    
                    elif(gY < TOTAL_COLS):
                        if(boardArray[gY-1][gX+1-1] == 0):
                            boardArray[gY-1][gX+1-1] = 5
                            canBeMoved = 1

                #left move backward 1
                if(gX > 1):
                    if(gX % 2 == 0):
                        if(boardArray[gY+1-1][gX-1-1] == 0):
                            boardArray[gY+1-1][gX-1-1] = 5
                            canBeMoved = 1
                                                   
                    elif(gY < TOTAL_COLS):
                        if(boardArray[gY-1][gX-1-1] == 0):
                            boardArray[gY-1][gX-1-1] = 5
                            canBeMoved = 1
                            
                #right move backward 2
                if(gX < TOTAL_COLS-1):
                    if(gX % 2 == 0):
                        if((boardArray[gY-1][gX+2-1] == 0 and (boardArray[gY+1-1][gX+1-1] == 1 or boardArray[gY+1-1][gX+1-1] == 2))
                        or (boardArray[gY-1][gX-1] == 2 and (boardArray[gY+1-1][gX+1-1] == 3 or boardArray[gY+1-1][gX+1-1] == 4))):
                            boardArray[gY+1-1][gX+2-1] = 6
                            canBeMoved = 1
                            takenPieceXR, takenPieceYR = gX+1-1 ,gY+1-1
                                                   
                    elif(gY < TOTAL_COLS):
                        if((boardArray[gY-1][gX+2-1] == 0 and (boardArray[gY-1][gX+1-1] == 1 or boardArray[gY-1][gX+1-1] == 2))
                        or(boardArray[gY-1][gX-1] == 2 and (boardArray[gY-1][gX+1-1] == 3 or boardArray[gY-1][gX+1-1] == 4))):
                            boardArray[gY+1-1][gX+2-1] = 6
                            canBeMoved = 1
                            takenPieceXR, takenPieceYR = gX+1-1, gY-1
                                                    
                #left move backward 2
                if(gX > 2):
                    if(gX % 2 ==  0):
                        if(boardArray[gY-1][gX-2-1] == 0 and (boardArray[gY+1-1][gX-1-1] == 1 or boardArray[gY+1-1][gX-1-1] == 2))\
                        or(boardArray[gY-1][gX-1] == 2 and (boardArray[gY+1][gX-1-1] == 3 or boardArray[gY+1-1][gX-1-1] == 4)):
                            boardArray[gY+1-1][gX-2-1] = 6
                            canBeMoved = 1
                            takenPieceXL, takenPieceYL = gX-1-1,  gY+1-1
                        
                    elif(gY < TOTAL_COLS):
                        if(boardArray[gY-1][gX-2-1] == 0 and (boardArray[gY-1][gX-1-1] == 1 or boardArray[gY-1][gX-1-1] == 2))\
                        or(boardArray[gY-1][gX-1] == 2 and (boardArray[gY-1][gX-1-1] == 3 or boardArray[gY-1-1][gX-1-1] == 4)):
                            boardArray[gY+1-1][gX-2-1] = 6
                            canBeMoved = 1
                            takenPieceXL, takenPieceYL = gX-1-1, gY-1
                print(takenPieceXL, takenPieceYL)
                print(takenPieceXR, takenPieceYR)
    boardCreate()

def closeGame():
    global questionWindow
    mainWindow.destroy()
    questionWindow.destroy()

#Creates a window which will display buttons so the user can choose if they want to end the game or not
def createQuestion():
    questionWindow = Tk()
    questionWindow.focus_force()
    questionWindow.title("Question")  

    #draws the text
    canvas2 = Canvas(questionWindow, width= QCANVAS_WIDTH, height= QCANVAS_HEIGHT, bg=LIGHTGREY)
    canvas2.create_text(350, 15, text="Do you want to continue playing, since many turns have passed without any piece being taken?", fill="black", font=('Helvetica 10 bold'))

    #draws the buttons
    yesButton = Button(questionWindow, text='No, we are as good as each other, lets declare this a draw', width=50, height=1, bd='1', command=lambda: closeGame())
    yesButton.place(x=140, y=30)

    noButton = Button(questionWindow, text='Yes! We will not back down, we will fight to the end!', width=50, height=1, bd='1', command=lambda: questionWindow.destroy())
    noButton.place(x=140, y=70)
    
    canvas2.pack()

#Creates a window which will display who has won the game
def createWinner():
    winnerWindow = Tk()
    winnerWindow.title("Winner")  

    #draws the text
    canvas3 = Canvas(winnerWindow, width= WCANVAS_WIDTH, height= WCANVAS_HEIGHT, bg=LIGHTGREY)
    if(dPRemaining <= 0):
        canvas3.create_text(200, 15, text = "Congratulations to: light player", fill="black", font=('Helvetica 10 bold'))

    if(lPRemaining <= 0):
        canvas3.create_text(200, 15, text = "Congratulations to: dark player", fill="black", font=('Helvetica 10 bold'))
    
    canvas3.create_text(200, 30, text = "for taking all the pieces of the other player.", fill="black", font=('Helvetica 10 bold'))
    canvas3.create_text(200, 45, text = "You are the winner!", fill="black", font=('Helvetica 10 bold'))


    canvas3.pack()

#This procedure will move a given piece from one space to another
def movePiece(event):
    global selectType, pieceType
    global takenPieceX, takenPieceY
    global canBeMoved
    global lPRemaining, dPRemaining
    global turnState
    global noJumpCount
    global pgX, pgY
    global gX, gY


    #Checks if I have previouly slected a piece or selecgted a new position
    if(selectType == 0):
        gX, gY = getGridCoords(event.x, event.y)
        if(gX != -1000):
            if(boardArray[gY-1][gX-1] != 0 and boardArray[gY-1][gX-1] != 5 and boardArray[gY-1][gX-1] != 6):
                if((turnState == 0 and (boardArray[gY-1][gX-1] == 1 or boardArray[gY-1][gX-1] == 2)) or (turnState == 1 and (boardArray[gY-1][gX-1] == 3 or boardArray[gY-1][gX-1] == 4))): 
                    #Stores the number of the piece type
                    pieceType = boardArray[gY-1][gX-1]
                    findLegalCells(gX, gY, pieceType)
                
                    if(canBeMoved == 1):    
                        #Remove piece
                        selectType = 1
                        canBeMoved = 0
                        

    #Checks to see if I've clicked a dot
    elif(selectType == 1):
        ngX, ngY = getGridCoords(event.x, event.y)
        if(ngX != -1000):
            if(boardArray[ngY-1][ngX-1] == 5 or boardArray[ngY-1][ngX-1] == 6):
                boardArray[gY-1][gX-1] = 0
                
                #Keeps track of how many pieces each player has remaining
                if(boardArray[ngY-1][ngX-1] == 6):
                    if(ngX < gX):
                        if(boardArray[takenPieceYL][takenPieceXL] == 1 or boardArray[takenPieceYL][takenPieceXL] == 2):
                            lPRemaining -= 1
                            noJumpCount = 0
                        elif(boardArray[takenPieceYL][takenPieceXL] == 3 or boardArray[takenPieceYL][takenPieceXL] == 4):
                            dPRemaining -= 1
                            noJumpCount = 0
                        boardArray[takenPieceYL][takenPieceXL] = 0

                    else:
                        if(boardArray[takenPieceYR][takenPieceXR] == 1 or boardArray[takenPieceYR][takenPieceXR] == 2):
                            lPRemaining -= 1
                            noJumpCount = 0
                        elif(boardArray[takenPieceYR][takenPieceXR] == 3 or boardArray[takenPieceYR][takenPieceXR] == 4):
                            dPRemaining -= 1
                            noJumpCount = 0
                        boardArray[takenPieceYR][takenPieceXR] = 0
                gX = ngX
                gY = ngY

                if((lPRemaining <= 0) or (dPRemaining <= 0)):
                    createWinner()
                        
                        
                    
                else:
                    noJumpCount += 1
                    if(noJumpCount == DRAW_THRESHOLD):
                        
                        #Displays windows asking player if they want to continue
                        createQuestion()
                        noJumpCount = 0
                        #pass
                     
                #Changes men to kings
                if((pieceType == 1) and (gY == 1) and (gX % 2 != 0)):
                    pieceType = 2

                if((pieceType == 3) and (gY == ODD_ROWS)):
                    pieceType = 4

                #Moves selected piece to selected space and updates board
                boardArray[ngY-1][ngX-1] = pieceType
                boardCreate()
                
                #Removes green dots and update board
                clearDots()
                boardCreate()
                selectType = 0
                
                if(turnState == 0):
                    turnState = 1
                elif(turnState == 1):
                    turnState = 0
                boardCreate()
                    
            else:
                clearDots()
                pieceType = boardArray[gY-1][gX-1]
                findLegalCells(gX, gY, pieceType)
                

    
#Calls all subroutines   
arrayCreate()
#printArray()
boardCreate()
clearDots()

#This line binds a mouse click to the getArrayCoords function
tk.bind("<Button-1>", movePiece)
tk.mainloop()

