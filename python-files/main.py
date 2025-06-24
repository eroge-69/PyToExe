"""
Welcome to GDB Online.
GDB online is an online compiler and debugger tool for C, C++, Python, Java, PHP, Ruby, Perl,
C#, OCaml, VB, Swift, Pascal, Fortran, Haskell, Objective-C, Assembly, HTML, CSS, JS, SQLite, Prolog.
Code, Compile, Run and Debug online from anywhere in world.

"""

import random
import os

#random.seed(2) #debug

shipTypes = (1, 2, 3, 4, 5)

shipNames = ("", "Aircraft Carrier", "Battleship", "Submarine", "Cruiser", "Destroyer")

shipLengths = {
    1: 5,
    2: 4,
    3: 3,
    4: 3,
    5: 2
}

shipLengthsByID = {
    "A": 5,
    "B": 4,
    "S": 3,
    "C": 3,
    "D": 2
}

rowHeadings = (" ", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J")

validRows = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")

validColumns = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")

shipIdentifiers = ("A", "B", "S", "C", "D")

rowIndexes = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "I": 9,
    "J": 10,
}

class Row:
    def __init__(self):
        self.columns = ["", "", "", "", "", "", "", "", "", "", ""]
        self.columnsInt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def render(self):
        for column in self.columns:
            print(column + " ", end="")

    def renderInt(self):
        for column in self.columnsInt:
            print(str(column) + " ", end="")

class Board:
    def __init__(self):
        self.remainingShips = [1, 2, 3, 4, 5]
        self.rows = [
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
            Row(),
        ]
        for rowIndex in range(len(self.rows)):
            # print("initializing: rowIndex = " + str(rowIndex))
            for columnIndex in range(len(self.rows[rowIndex].columns)):
                # print("initializing: columnIndex = " + str(columnIndex))
                if columnIndex == 0:
                    # print("setting rowHeadings (columnIndex == 0)")
                    self.rows[rowIndex].columns[columnIndex] = rowHeadings[rowIndex]
                elif rowIndex == 0:
                    # print ("setting column headings (rowIndex == 0)")
                    self.rows[rowIndex].columns[columnIndex] = str(columnIndex)
                else:
                    # print ("setting row contents")
                    self.rows[rowIndex].columns[columnIndex] = "~"

    def render(self):
        # print("entering render function")
        for rowIndex in range(len(self.rows)):
            self.rows[rowIndex].render()
            print("")

    def placeShip(self, shipType, verticalOrientation, row, column):
        length = 0
        identifier = ""
        if shipType == 1:  # Aircraft Carrier
            length = 5
            identifier = "A"
        elif shipType == 2:  # Battleship
            length = 4
            identifier = "B"
        elif shipType == 3:  # Submarine
            length = 3
            identifier = "S"
        elif shipType == 4:  # Cruiser
            length = 3
            identifier = "C"
        elif shipType == 5:  # Destroyer
            length = 2
            identifier = "D"
        else:
            print("Error: Invalid Ship Type")

        if verticalOrientation == True:
            if rowIndexes[row] + length > len(self.rows):
                print("Error: ship won't fit")
            else:
                for i in range(length):
                    self.rows[rowIndexes[row] + i].columns[column] = identifier
        else:
            if column + length > len(self.rows[0].columns):
                print("Error: ship won't fit")
            else:
                for i in range(length):
                    self.rows[rowIndexes[row]].columns[column + i] = identifier

    def customPlacement(self):
        print("Player Ship Placement:")
        self.render()
        for shipType in shipTypes:
            orientationIsVertical = False
            vOrH = ""
            print("Ship " + str(shipType) + " of 5:")
            print(shipNames[shipType] + ":")
            print("Orientation:")
            inputValid = False
            while not inputValid:
                vOrH = input("V - vertical, H - horizontal: ")
                if vOrH.upper() == "V":
                    orientationIsVertical = True
                    inputValid = True
                elif vOrH.upper() == "H":
                    orientationIsVertical = False
                    inputValid = True
                else:
                    print("Invalid Input")

            inputValid = False
            while not inputValid:
                if orientationIsVertical:
                    inputString = input("Enter coordinates of ship's uppermost point: ")
                else:
                    inputString = input("Enter coordinates of ship's leftmost point: ")
                inputString = inputString.upper()

                if len(inputString) == 2:
                    if (inputString[0] in validRows) and (
                        inputString[1] in validColumns
                    ):
                        shotRow = inputString[0]
                        shotRowIndex = rowIndexes[shotRow]
                        shotColumn = int(inputString[1])
                        if (
                            orientationIsVertical
                            and shotRowIndex + shipLengths[shipType] - 1 <= 10
                        ):
                            collision = False
                            for i in range(shipLengths[shipType]):
                                if (
                                    self.rows[shotRowIndex + i].columns[shotColumn]
                                    != "~"
                                ):
                                    collision = True
                            if not collision:
                                inputValid = True
                            else:
                                print("Collision")
                        elif (not orientationIsVertical) and shotColumn + shipLengths[
                            shipType
                        ] - 1 <= 10:
                            collision = False
                            for i in range(shipLengths[shipType]):
                                if (
                                    self.rows[shotRowIndex].columns[shotColumn + i]
                                    != "~"
                                ):
                                    collision = True
                            if not collision:
                                inputValid = True
                            else:
                                print("Collision")
                        else:
                            print("Invalid Input - Boundary Error")
                    else:
                        print("Invalid Input")
                elif len(inputString) == 3:
                    if (
                        (inputString[0] in validRows)
                        and (inputString[1] == "1")
                        and (inputString[2] == "0")
                    ):
                        shotRow = inputString[0]
                        shotRowIndex = rowIndexes[shotRow]
                        shotColumn = 10
                        if (
                            orientationIsVertical
                            and shotRowIndex + shipLengths[shipType] - 1 <= 10
                        ):
                            inputValid = True
                        else:
                            print("Invalid Input - Boundary Error")
                    else:
                        print("Invalid Input")
                else:
                    print("invalid input")

            self.placeShip(shipType, orientationIsVertical, shotRow, shotColumn)
            os.system("clear")
            print("Entry Accepted - Ship Placement")
            self.render()

    def randomize(self):

        rowNumber = 0
        column = 0

        for shipType in shipTypes:
            orientationIsVertical = False

            shipLength = shipLengths[shipType]

            randomInteger = random.randint(1, 100)
            # print("Random Integer: " + str(randomInteger))

            if randomInteger % 2 == 1:  # odd means vertical, even means horizontal
                orientationIsVertical = True
                # print("Orientation is vertical")
            # else:
            # print("Orientation is horizontal")

            # set the row and column
            validResult = False
            while not validResult:
                insideBoundary = False
                avoidsCollisions = True
                column = random.randint(1, 10)
                rowNumber = random.randint(1, 10)
                # print("rowNumber: " + str(rowNumber))
                # print("Column: " + str(column))

                if orientationIsVertical:  # vertical orientation
                    if rowNumber + shipLength <= 10:
                        insideBoundary = True
                        for i in range(shipLength):
                            # print(self.rows[rowNumber + i].columns[column])
                            if self.rows[rowNumber + i].columns[column] != "~":
                                avoidsCollisions = False
                    # else:
                    # print("out of bounds")
                else:
                    if column + shipLength <= 10:
                        insideBoundary = True
                        for i in range(shipLength):
                            if self.rows[rowNumber].columns[column + i] != "~":
                                avoidsCollisions = False
                    # else:
                    # print("out of bounds")

                if insideBoundary and avoidsCollisions:
                    validResult = True

            # print(orientationIsVertical)
            self.placeShip(
                shipType, orientationIsVertical, rowHeadings[rowNumber], column
            )
            # self.render()

    def shipCount(self):
        remainingShipIDs = ""
        remainingShipCount = 0
        for rowIndex in range(1, 11):
            for columnIndex in range(1, 11):
                target = self.rows[rowIndex].columns[columnIndex]
                if target in shipIdentifiers:
                    if target not in remainingShipIDs:
                        remainingShipIDs = remainingShipIDs + target
        # print(remainingShipIDs)
        remainingShipCount = len(remainingShipIDs)

        # print("remaining ship count: " + str(remainingShipCount))

        return remainingShipCount

    def shortestLengthRemaining(self):
        remainingShipIDs = ""
        shortestLength = 5
        for rowIndex in range(1, 11):
            for columnIndex in range(1, 11):
                target = self.rows[rowIndex].columns[columnIndex]
                if target in shipIdentifiers:
                    if target not in remainingShipIDs:
                        remainingShipIDs = remainingShipIDs + target
        # print(remainingShipIDs)
        for char in remainingShipIDs:
            if shipLengthsByID[char] < shortestLength:
                shortestLength = shipLengthsByID[char]

        return shortestLength

    def longestLengthRemaining(self):
        remainingShipIDs = ""
        longestLength = 2
        for rowIndex in range(1, 11):
            for columnIndex in range(1, 11):
                target = self.rows[rowIndex].columns[columnIndex]
                if target in shipIdentifiers:
                    if target not in remainingShipIDs:
                        remainingShipIDs = remainingShipIDs + target
        # print(remainingShipIDs)
        for char in remainingShipIDs:
            if shipLengthsByID[char] > longestLength:
                longestLength = shipLengthsByID[char]

        return longestLength

class Game:
    def __init__(self):
        self.playerOffensiveBoard = Board()
        self.playerDefensiveBoard = Board()
        self.enemyOffensiveBoard = Board()
        self.enemyDefensiveBoard = Board()
        #self.enemyStrategicHeatmap = Board()
        
        self.playerShipsRemaining = 5
        self.enemyShipsRemaining = 5
        self.inCluster = False
        self.clusterHomeRow = 0
        self.clusterHomeColumn = 0
        self.strandedHits = []
        self.chain = False
        self.reachedChainEnd = False
        self.chainDirection = ""
        self.searchDirection = ""
        self.lastHitRow = 0
        self.lastHitColumn = 0
        self.playerLastShotRow = ""
        self.playerLastShotColumn = ""
        self.playerLastTurnHit = False

    def playerTurn(self):
        inputValid = False
        self.playerLastTurnHit = False
        while not inputValid:
            inputString = input("Call your shot: ") #comment for debug
            #input("press enter to continue") #debug
            #inputString = "A1" #debug
            inputString = inputString.upper()
            if len(inputString) == 2:
                if (inputString[0] in validRows) and (inputString[1] in validColumns):
                    inputValid = True
                    shotRow = inputString[0]
                    shotColumn = int(inputString[1])
                    self.playerLastShotRow = shotRow
                    self.playerLastShotColumn = inputString[1]
                else:
                    print("Invalid Input")
            elif len(inputString) == 3:
                if (
                    (inputString[0] in validRows)
                    and (inputString[1] == "1")
                    and (inputString[2] == "0")
                ):
                    inputValid = True
                    shotRow = inputString[0]
                    shotColumn = 10
                    self.playerLastShotRow = shotRow
                    self.playerLastShotColumn = "10"
                else:
                    print("Invalid Input")
            else:
                print("invalid input")

        target = self.enemyDefensiveBoard.rows[rowIndexes[shotRow]].columns[shotColumn]
        if target in shipIdentifiers:
            print("Hit!")
            self.enemyDefensiveBoard.rows[rowIndexes[shotRow]].columns[
                shotColumn
            ] = target.lower()
            self.playerOffensiveBoard.rows[rowIndexes[shotRow]].columns[
                shotColumn
            ] = "X"
            self.playerLastTurnHit = True
        else:
            print("Miss!")
            self.playerOffensiveBoard.rows[rowIndexes[shotRow]].columns[
                shotColumn
            ] = "O"

    def enemyTurn(self):

        validResult = False
        iterationCount = 0
        while not validResult:
            if iterationCount > 10:
                validResult = True
                print("timing out")

            if not self.inCluster:  # if not in cluster choose randomly--optimize later
                if len(self.strandedHits) == 0:
                    row = random.randint(1, 10)
                    column = random.randint(1, 10)
    
                    # could add code to check all directions for clearance
                    if self.enemyOffensiveBoard.rows[row].columns[column] == "~":
                        validResult = True
                        self.clusterHomeRow = row
                        self.clusterHomeColumn = column
                else:
                    self.inCluster = True
                    self.clusterHomeRow = self.strandedHits[len(self.strandedHits) - 1][0]
                    self.clusterHomeColum = self.strandedHits[len(self.strandedHits) - 1][0]
            else:
                if not self.chain:  # not in a chain, checking from cluster home

                    aboveClear = True
                    rightClear = True
                    belowClear = True
                    leftClear = True

                    #determine clearance above
                    aboveClearance = 0
                    reachedBoundaryOrObstacle = False
                    checkRow = self.clusterHomeRow
                    while not reachedBoundaryOrObstacle:
                        checkRow = checkRow - 1
                        if checkRow < 1:
                            reachedBoundaryOrObstacle = True
                        elif self.enemyOffensiveBoard.rows[checkRow].columns[self.clusterHomeColumn] != "~":
                            reachedBoundaryOrObstacle = True
                        else:
                            aboveClearance += 1
                    
                    #determine clearance below
                    belowClearance = 0
                    reachedBoundaryOrObstacle = False
                    checkRow = self.clusterHomeRow
                    while not reachedBoundaryOrObstacle:
                        checkRow = checkRow + 1
                        if checkRow > 10:
                            reachedBoundaryOrObstacle = True
                        elif self.enemyOffensiveBoard.rows[checkRow].columns[self.clusterHomeColumn] != "~":
                            reachedBoundaryOrObstacle = True
                        else:
                            belowClearance += 1

                    #determine clearance to the right
                    rightClearance = 0
                    reachedBoundaryOrObstacle = False
                    checkColumn = self.clusterHomeColumn
                    while not reachedBoundaryOrObstacle:
                        checkColumn = checkColumn + 1
                        if checkColumn > 10:
                            reachedBoundaryOrObstacle = True
                        elif self.enemyOffensiveBoard.rows[self.clusterHomeRow].columns[checkColumn] != "~":
                            reachedBoundaryOrObstacle = True
                        else:
                            rightClearance += 1
                            
                    #determine clearance to the left
                    leftClearance = 0
                    reachedBoundaryOrObstacle = False
                    checkColumn = self.clusterHomeColumn
                    while not reachedBoundaryOrObstacle:
                        checkColumn = checkColumn - 1
                        if checkColumn < 1:
                            reachedBoundaryOrObstacle = True
                        elif self.enemyOffensiveBoard.rows[self.clusterHomeRow].columns[checkColumn] != "~":
                            reachedBoundaryOrObstacle = True
                        else:
                            leftClearance += 1

                    verticalClearance = aboveClearance + belowClearance
                    horizontalClearance = rightClearance + leftClearance
                    
                    if not self.reachedChainEnd:
                        if verticalClearance >= (self.playerDefensiveBoard.shortestLengthRemaining() - 1):
                            if aboveClearance > 0:
                                row = self.clusterHomeRow - 1
                                column = self.clusterHomeColumn
                                self.searchDirection = "up"
                                validResult = True
                            elif belowClearance > 0:
                                row = self.clusterHomeRow + 1
                                column = self.clusterHomeColumn
                                self.searchDirection = "down"
                                validResult = True
                            else:
                                print("unexpected execution - check above and below clearance")
                        elif horizontalClearance >= (self.playerDefensiveBoard.shortestLengthRemaining() - 1):
                            if leftClearance > 0:
                                row = self.clusterHomeRow
                                column = self.clusterHomeColumn - 1
                                self.searchDirection = "left"
                                validResult = True
                            elif rightClearance > 0:
                                row = self.clusterHomeRow
                                column = self.clusterHomeColumn + 1
                                self.searchDirection = "right"
                                validResult = True
                            else:
                                print("unexpected execution - check right and left clearance")
                        else:
                            print("FIX THIS - no vertical or horizontal clearance - going back to random guessing")
                            self.inCluster = False  # go back to random guesses
                    else: #if we just reached the end of chain, continue from home in the opposite direction
                        self.reachedChainEnd = False
                        if self.chainDirection == "up":
                            if self.clusterHomeRow != 10 and self.enemyOffensiveBoard.rows[self.clusterHomeRow + 1].columns[self.clusterHomeColumn] == "~":
                                row = self.clusterHomeRow + 1
                                column = self.clusterHomeColumn
                                self.searchDirection = "down"
                                validResult = True
                            else:
                                print("declining to continue chain down")
                        elif self.chainDirection == "down":
                            if self.clusterHomeRow != 1 and self.enemyOffensiveBoard.rows[self.clusterHomeRow - 1].columns[self.clusterHomeColumn] == "~":
                                row = self.clusterHomeRow - 1
                                column = self.clusterHomeColumn
                                self.searchDirection = "up"
                                validResult = True
                            else:
                                print("declining to continue chain down")
                        elif self.chainDirection == "right":
                            if self.clusterHomeColumn != 1 and self.enemyOffensiveBoard.rows[self.clusterHomeRow].columns[self.clusterHomeColumn - 1] == "~":
                                row = self.clusterHomeRow
                                column = self.clusterHomeColumn - 1
                                self.searchDirection = "left"
                                validResult = True
                            else:
                                print("declining to continue chain left")
                        elif self.chainDirection == "left":
                            if self.clusterHomeColumn != 10 and self.enemyOffensiveBoard.rows[self.clusterHomeRow].columns[self.clusterHomeColumn + 1] == "~":
                                row = self.clusterHomeRow
                                column = self.clusterHomeColumn + 1
                                self.searchDirection = "right"
                                validResult = True
                            else:
                                print("declining to continue chain right")
                        else:
                            print ("unexpected chain direction")

                else:  # contuing a chain after a hit
                    # print("continuing along chain")
                    if self.chainDirection == "up":
                        if self.lastHitRow > 1 and self.enemyOffensiveBoard.rows[self.lastHitRow - 1].columns[self.lastHitColumn] == "~":
                            row = self.lastHitRow - 1
                            column = self.lastHitColumn
                            validResult = True
                        else:
                            self.chain = False
                    elif self.chainDirection == "down":
                        if self.lastHitRow < 10 and self.enemyOffensiveBoard.rows[self.lastHitRow + 1].columns[self.lastHitColumn] == "~":
                            row = self.lastHitRow + 1
                            column = self.lastHitColumn
                            validResult = True
                        else:
                            self.chain = False
                    elif self.chainDirection == "left":
                        if self.lastHitColumn > 1 and self.enemyOffensiveBoard.rows[self.lastHitRow].columns[self.lastHitColumn - 1] == "~":
                            row = self.lastHitRow
                            column = self.lastHitColumn - 1
                            validResult = True
                        else:
                            self.chain = False
                    elif self.chainDirection == "right":
                        if self.lastHitColumn < 10 and self.enemyOffensiveBoard.rows[self.lastHitRow].columns[self.lastHitColumn + 1] == "~":
                            row = self.lastHitRow
                            column = self.lastHitColumn + 1
                            validResult = True
                        else:
                            self.chain = False
                    else:
                        print("unexpected chain direction")
            # end else
            interationCount = iterationCount + 1
        # end while

        target = self.playerDefensiveBoard.rows[row].columns[column]
        if target in shipIdentifiers:
            self.playerDefensiveBoard.rows[row].columns[column] = target.lower()
            self.enemyOffensiveBoard.rows[row].columns[column] = "X"
            self.strandedHits.append((row,column))

            print("Player Ships Remaining: " + str(game.playerDefensiveBoard.shipCount()))
            print("Player Ship Layout")
            self.playerDefensiveBoard.render()
            print("Enemy Shot Tracker")
            self.enemyOffensiveBoard.render()
            print("Target: " + rowHeadings[row], end="")
            print(column)
            print("Hit!")

            if self.inCluster:
                self.chain = True
            self.chainDirection = self.searchDirection
            self.inCluster = True
            self.lastHitRow = row
            self.lastHitColumn = column
        else:
            if target == "~":
                self.enemyOffensiveBoard.rows[row].columns[column] = "O"
            
            print("Player Ships Remaining: " + str(game.playerDefensiveBoard.shipCount()))
            print("Player Ship Layout")
            self.playerDefensiveBoard.render()
            print("Enemy Shot Tracker")
            self.enemyOffensiveBoard.render()
            print("Target " + rowHeadings[row], end="")
            print(column)
            print("Miss!")
            if self.chain:
                self.reachedChainEnd = True
            self.chain = False


game = Game()
game.enemyDefensiveBoard.randomize()

#print("Enemy Ship Locations:") #debug
#game.enemyDefensiveBoard.render() #debug
#input("Press Enter to Continue") #debug

print("Welcome to Battleship!")
"""
game.playerDefensiveBoard.randomize()
print("Here is your ship layout: ")
game.playerDefensiveBoard.render()
input("Press Enter to Continue")
os.system("clear")
"""

inputValid = False
while not inputValid:
    rOrC = input("Random or Custom Ship Placement? ")
    if rOrC.upper() == "R":
        inputValid = True
        game.playerDefensiveBoard.randomize()
        print("Player Ship Layout")
        game.playerDefensiveBoard.render()
    elif rOrC.upper() == "C":
        inputValid = True
        game.playerDefensiveBoard.customPlacement()
    else:
        print("Invalid Input")

while game.playerShipsRemaining > 0 and game.enemyShipsRemaining > 0:
    input("Press Enter to Continue")
    os.system("clear")
    print("Your Turn")
    print("Enemy Ships Remaining: " + str(game.enemyShipsRemaining))
    print("Player Shot Tracker")
    game.playerOffensiveBoard.render()
    game.playerTurn()
    os.system("clear")
    print("Your Turn")
    print("Enemy Ships Remaining: " + str(game.enemyDefensiveBoard.shipCount()))
    print("Player Shot Tracker")
    game.playerOffensiveBoard.render()
    print("Target: " + game.playerLastShotRow + game.playerLastShotColumn)
    if game.playerLastTurnHit:
        print("Hit!")
    else:
        print("Miss!")
        
    if game.enemyShipsRemaining == game.enemyDefensiveBoard.shipCount() + 1:
        game.enemyShipsRemaining = game.enemyDefensiveBoard.shipCount() #comment for debug
        #game.enemyShipsRemaining = 0 #debug

        for shipType in game.enemyDefensiveBoard.remainingShips:
            remove = True
            # print("check if shiptype" + str(shipType) + " was sunk")
            for row in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                for column in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    # print(game.playerDefensiveBoard.rows[row].columns[column])
                    if (game.enemyDefensiveBoard.rows[row].columns[column] == shipIdentifiers[shipType - 1]):
                        remove = False
                        # print("negating remove")
            if remove == True:
                game.enemyDefensiveBoard.remainingShips.remove(shipType)
                print("You sunk the enemy's " + shipNames[shipType] + "!")

    elif game.enemyShipsRemaining == game.enemyDefensiveBoard.shipCount():
        "no change to enemy ship count"
    else:
        print("unexpected change in enemy ships remaining")
       
    if game.enemyShipsRemaining != 0: 
        input("Press Enter to Continue")
        os.system("clear")
        print("Enemy Turn")
        #print("Player Ships Remaining: " + str(game.playerDefensiveBoard.shipCount())) moving into enemyTurn
        game.enemyTurn()

        if game.playerShipsRemaining == game.playerDefensiveBoard.shipCount() + 1:
            game.playerShipsRemaining = game.playerDefensiveBoard.shipCount() #comment for debug
            #game.playerShipsRemaining = 0 #debug
            game.chain = False
            game.inCluster = False
            game.reachedChainEnd = False
            

            for shipType in game.playerDefensiveBoard.remainingShips:
                remove = True
                # print("check if shiptype" + str(shipType) + " was sunk")
                for row in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    for column in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                        # print(game.playerDefensiveBoard.rows[row].columns[column])
                        if (game.playerDefensiveBoard.rows[row].columns[column] == shipIdentifiers[shipType - 1]):
                            remove = False
                            # print("negating remove")
                if remove == True:
                    game.playerDefensiveBoard.remainingShips.remove(shipType)
                    print("Enemy sunk your " + shipNames[shipType] + "!")
                    for i in range(shipLengths[shipType]):
                        if game.searchDirection == "up":
                            game.strandedHits.remove((game.lastHitRow + i, game.lastHitColumn))
                        elif game.searchDirection == "down":
                            game.strandedHits.remove((game.lastHitRow - i, game.lastHitColumn))
                        elif game.searchDirection == "right":
                            game.strandedHits.remove((game.lastHitRow, game.lastHitColumn - i))
                        elif game.searchDirection == "left":
                            game.strandedHits.remove((game.lastHitRow, game.lastHitColumn + i))

        elif game.playerShipsRemaining == game.playerDefensiveBoard.shipCount():
            "no change to player ship count"
        else:
            print("unexpected change in player ships remaining")

print("Game Over")
if game.enemyShipsRemaining == 0:
    print("You Win!")
elif game.playerShipsRemaining == 0:
    print("You Lose!")
print("Enemy Ships")
game.enemyDefensiveBoard.render()