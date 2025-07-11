import pyautogui
import time
# Function to check if an image exists on the screen
def exists_on_screen(image_path, confidence=0.9, grayscale=False, region=None):
    try:
        result = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale, region=region)
        return result is not None
    except Exception:  
        return False
# function to make sure a button becomes clickable
def make_sure_clickable():
    pyautogui.move(2, 2, duration=0.5)
    pyautogui.click()
#These are all the variables that give the location of the items based on the screen size
topBunLocationX = pyautogui.size().width / 1.16363636364
topBunLocationY = pyautogui.size().height / 3.375
onionLocationX = pyautogui.size().width / 1.1566265060240963
onionLocationY = pyautogui.size().height / 2.7411675127
cheeseLocationX = pyautogui.size().width / 1.1552346570397112
cheeseLocationY = pyautogui.size().height / 2.33766233766
burgerLocationX = pyautogui.size().width / 1.18811881188
burgerLocationY = pyautogui.size().height / 2.04933586338
vegBurgerLocationX = pyautogui.size().width / 1.1294117647058823
vegBurgerLocationY = pyautogui.size().height / 2.049335863377609
tomatoLocationX = pyautogui.size().width / 1.1566265060240963
tomatoLocationY = pyautogui.size().height / 1.8120805369127517
lettuceLocationX = pyautogui.size().width / 1.157323688969586
lettuceLocationY = pyautogui.size().height / (1080/671)
bottomBunLocationX = pyautogui.size().width / (1920/1663)
bottomBunLocationY = pyautogui.size().height / (1080/730)
sidesLocationX = pyautogui.size().width / (1920/1858)
sidesLocationY = pyautogui.size().height / (1080/465)
friesLocationX = pyautogui.size().width / (1920/1592)
friesLocationY = pyautogui.size().height / (1080/407)
drinkItemLocationX = pyautogui.size().width / (1920/1856)
drinkItemLocationY = pyautogui.size().height / (1080/580)
mozzSticksLocationX = pyautogui.size().width / (1920/1599)
mozzSticksLocationY = pyautogui.size().height / (1080/525)
onionRingsLocationX = pyautogui.size().width / (1920/1594)
onionRingsLocationY = pyautogui.size().height / (1080/645)
smallItemLocationX = pyautogui.size().width / (1920/1727)
smallItemLocationY = pyautogui.size().height / (1080/409)
mediumItemLocationX = pyautogui.size().width / (1920/1726)
mediumItemLocationY = pyautogui.size().height / (1080/526)
largeItemLocationX = pyautogui.size().width / (1920/1727)
largeItemLocationY = pyautogui.size().height / (1080/652)
sodaItemLocationX = pyautogui.size().width / (1920/1592)
sodaItemLocationY = pyautogui.size().height / (1080/407)
juiceItemLocationX = pyautogui.size().width / (1920/1599)
juiceItemLocationY = pyautogui.size().height / (1080/525)
shakeItemLocationX = pyautogui.size().width / (1920/1594)
shakeItemLocationY = pyautogui.size().height / (1080/645)
finishOrderLocationX = pyautogui.size().width / (1920/1855)
finishOrderLocationY = pyautogui.size().height / (1080/698)


# This is where it will check for what the Customer wants to order and then runs code based on that
pyautogui.moveTo(bottomBunLocationX, bottomBunLocationY, duration=0.1)
make_sure_clickable()
pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Burger1.png", confidence=0.9) :
    pyautogui.moveTo(burgerLocationX, burgerLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Burger2.png", confidence=0.9) :
    pyautogui.moveTo(burgerLocationX, burgerLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Cheese1.png", confidence=0.9) :
    pyautogui.moveTo(cheeseLocationX, cheeseLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Cheese2.png", confidence=0.9) :
    pyautogui.moveTo(cheeseLocationX, cheeseLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Veg1.png", confidence=0.9) :
    pyautogui.moveTo(vegBurgerLocationX, vegBurgerLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Veg2.png", confidence=0.9) :
    pyautogui.moveTo(vegBurgerLocationX, vegBurgerLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Onion1.png", confidence=0.9) :
    pyautogui.moveTo(onionLocationX, onionLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Onion2.png", confidence=0.9) :
    pyautogui.moveTo(onionLocationX, onionLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Tomato1.png", confidence=0.9) :
    pyautogui.moveTo(tomatoLocationX, tomatoLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Tomato2.png", confidence=0.9) :
    pyautogui.moveTo(tomatoLocationX, tomatoLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Lettuce1.png", confidence=0.9) :
    pyautogui.moveTo(lettuceLocationX, lettuceLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/Lettuce2.png", confidence=0.9) :
    pyautogui.moveTo(lettuceLocationX, lettuceLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.click()
pyautogui.moveTo(topBunLocationX, topBunLocationY, duration=0.1)
make_sure_clickable()   
pyautogui.click()
pyautogui.click()
pyautogui.moveTo(sidesLocationX, sidesLocationY, duration=0.1)
make_sure_clickable()   
pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/FryL.png", confidence=0.9) :
    pyautogui.moveTo(friesLocationX, friesLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/FryM.png", confidence=0.9) :
    pyautogui.moveTo(friesLocationX, friesLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click() 
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/FryS.png", confidence=0.9) :
    pyautogui.moveTo(friesLocationX, friesLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/MozzL.png", confidence=0.9) :
    pyautogui.moveTo(mozzSticksLocationX, mozzSticksLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click() 
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/MozzM.png", confidence=0.9) :
    pyautogui.moveTo(mozzSticksLocationX, mozzSticksLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/MozzS.png", confidence=0.9) :
    pyautogui.moveTo(mozzSticksLocationX, mozzSticksLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/OnionRingsL.png", confidence=0.9) :
    pyautogui.moveTo(onionRingsLocationX, onionRingsLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/OnionRingsM.png", confidence=0.9) :
    pyautogui.moveTo(onionRingsLocationX, onionRingsLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/OnionRingsS.png", confidence=0.9) :
    pyautogui.moveTo(onionRingsLocationX, onionRingsLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
pyautogui.moveTo(drinkItemLocationX, drinkItemLocationY, duration=0.1)
make_sure_clickable()
pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/SodaL.png", confidence=0.9) :
    pyautogui.moveTo(sodaItemLocationX, sodaItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click() 
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/SodaM.png", confidence=0.9) :
    pyautogui.moveTo(sodaItemLocationX, sodaItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/SodaS.png", confidence=0.9) :
    pyautogui.moveTo(sodaItemLocationX, sodaItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/JuiceL.png", confidence=0.9) :
    pyautogui.moveTo(juiceItemLocationX, juiceItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/JuiceM.png", confidence=0.9) :
    pyautogui.moveTo(juiceItemLocationX, juiceItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/JuiceS.png", confidence=0.9) :
    pyautogui.moveTo(juiceItemLocationX, juiceItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/ShakeL.png", confidence=0.9) :
    pyautogui.moveTo(shakeItemLocationX, shakeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(largeItemLocationX, largeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click() 
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/ShakeM.png", confidence=0.9) :
    pyautogui.moveTo(shakeItemLocationX, shakeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(mediumItemLocationX, mediumItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
if exists_on_screen("c:/Users/Naylor/VSPrograms/BloxBurg Cashier Order Screenshots/ShakeS.png", confidence=0.9) :
    pyautogui.moveTo(shakeItemLocationX, shakeItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()
    pyautogui.moveto(smallItemLocationX, smallItemLocationY, duration=0.1)
    make_sure_clickable()
    pyautogui.click()  
pyautogui.moveTo(finishOrderLocationX, finishOrderLocationY, duration=0.1)
make_sure_clickable()
pyautogui.click()






