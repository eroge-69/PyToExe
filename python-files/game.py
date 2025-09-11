#ROCK PAPER SCISSORS USING PYTHON WITH OPENCV

#IMPORT PACKAGES
import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

#CAPTURE VIDEO USING OPENCV-->CV2

cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

detector=HandDetector(maxHands=1)   #Only one player can play with AI

# Load the background image once
imgBgOriginal = cv2.imread("Resources/BG.png")

# Game State Variables
stateResult=False
startGame=False
score=[0,0]  #Starting score will be 0
result_display_end_time = 0 # Timer to reset the game after a round
quit_gesture_start_time = 0 # Timer for the quit gesture


while True:
    # Create a fresh copy of the background for each frame
    imgbg = imgBgOriginal.copy()
    success,img=cap.read()

    if not success:
        print("Failed to capture image")
        break

    imgscale=cv2.resize(img,(0,0),None,0.875,0.875)
    imgscale=imgscale[:,80:480]

    #Find Hands
    hands,img=detector.findHands(imgscale)

    # Universal Quit Gesture with 2-second hold
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        if fingers == [0, 1, 1, 1, 0]: # User-defined Quit Gesture
            if quit_gesture_start_time == 0:
                quit_gesture_start_time = time.time() # Start timer
            elif time.time() - quit_gesture_start_time > 2:
                break # Held for 2s, so quit
        else:
            quit_gesture_start_time = 0 # Reset timer if gesture changes
    else:
        quit_gesture_start_time = 0 # Also reset if no hand is visible

    if startGame:
        if stateResult:
            # State: Showing Result
            if time.time() > result_display_end_time:
                # Reset for the next round
                startGame = False
                stateResult = False
            else:
                cv2.putText(imgbg, "Round Over", (450, 500), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        else:
            # State: Playing
            timer=time.time()-initialTime
            # Display a 3, 2, 1 countdown
            cv2.putText(imgbg,str(3 - int(timer)),(605,435),cv2.FONT_HERSHEY_PLAIN,6,(255,0,255),4)
            
            if timer>3:
                stateResult=True
                result_display_end_time = time.time() + 3
                playerMove=0 #Default player move

                # AI always makes a move
                randomNumber=random.randint(1,3)
                imgAi=cv2.imread(f'Resources/{randomNumber}.png',cv2.IMREAD_UNCHANGED)

                if hands:
                    if fingers==[0,0,0,0,0]: playerMove=1 #ROCK
                    if fingers ==[1,1,1,1,1]: playerMove=2   #PAPER
                    if fingers ==[0,1,1,0,0]: playerMove=3  #SCISSORS

                #GAME RESULT
                if (playerMove==1 and randomNumber==3) or (playerMove==2 and randomNumber==1) or (playerMove==3 and randomNumber==2): score[1]+=1
                if (playerMove==3 and randomNumber==1) or (playerMove==1 and randomNumber==2) or (playerMove==2 and randomNumber==3): score[0]+=1
    else:
        # State: Waiting to Start
        if hands:
            if fingers == [0, 0, 1, 1, 1]:
                startGame = True
                initialTime = time.time()
                stateResult = False # Explicitly reset state


    imgbg[234:654,795:1195]=imgscale

    if stateResult:
        imgbg=cvzone.overlayPNG(imgbg,imgAi,(149,310))

    cv2.putText(imgbg,str(score[0]),(410,215),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),6)
    cv2.putText(imgbg,str(score[1]),(1112,215),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),6)

    cv2.imshow("BG",imgbg)

    key=cv2.waitKey(1)
    if key==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#DECLARE THE RESULT

if score[0]>score[1]:
    print("AI WINS")
elif score[1]>score[0]:
    print("PLAYER WINS")
else:
    print("TIE")
