import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np

# Settings
FRAME_REDUCTION = 150
SMOOTHING = 5
CLICK_THRESHOLD = 35
PINKY_THRESHOLD = 100
CLICK_COOLDOWN = 0.8
ZOOM_SENSITIVITY = 1.5
ZOOM_COOLDOWN = 1.0
SWIPE_THRESHOLD = 40
SWIPE_COOLDOWN = 0.5

pyautogui.FAILSAFE = False

# Initialize
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not accessible")
    exit()

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

prev_x, prev_y = pyautogui.position()
click_cooldown = False
last_click_time = 0
last_zoom_time = 0
prev_hand_spread = 0
last_swipe_time = 0

print("=== Single Hand Controller ===")
print("Move index finger - Control cursor")
print("Thumb+Index - Left Click | Thumb+Middle - Right Click")
print("All 5 fingers open - Zoom in/out")
print("Index+Middle together - Photo Slides & Reels")
print("Press 'Q' to quit\n")

def calculate_fingertips_spread(fingertips):
    """Calculate average distance between all fingertips"""
    total_distance = 0
    count = 0
    for i in range(len(fingertips)):
        for j in range(i+1, len(fingertips)):
            total_distance += math.dist(fingertips[i], fingertips[j])
            count += 1
    return total_distance / count if count > 0 else 0

def are_all_fingers_open(lm_list):
    """Check if all fingers are open"""
    try:
        # Check if fingertips are above their respective MCP joints
        fingers_open = 0
        
        # Thumb (simplified check)
        if lm_list[4][1] < lm_list[3][1]:  # thumb tip above IP joint
            fingers_open += 1
        
        # Index finger
        if lm_list[8][1] < lm_list[5][1]:  # tip above MCP
            fingers_open += 1
        
        # Middle finger
        if lm_list[12][1] < lm_list[9][1]:
            fingers_open += 1
        
        # Ring finger
        if lm_list[16][1] < lm_list[13][1]:
            fingers_open += 1
        
        # Pinky finger
        if lm_list[20][1] < lm_list[17][1]:
            fingers_open += 1
        
        return fingers_open >= 4  # At least 4 fingers open
    
    except Exception as e:
        return False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Draw movement area
    cv2.rectangle(frame, (FRAME_REDUCTION, FRAME_REDUCTION), 
                 (w - FRAME_REDUCTION, h - FRAME_REDUCTION), (255, 200, 0), 2)

    # Handle cooldown
    current_time = time.time()
    if click_cooldown and (current_time - last_click_time) > CLICK_COOLDOWN:
        click_cooldown = False

    if results.multi_hand_landmarks:
        try:
            hand = results.multi_hand_landmarks[0]
            lm_list = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]
            
            # Get key points
            thumb_tip = lm_list[4]
            index_tip = lm_list[8]
            middle_tip = lm_list[12]
            ring_tip = lm_list[16]
            pinky_tip = lm_list[20]
            wrist = lm_list[0]

            # All fingertips
            fingertips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
            
            # Calculate distances
            thumb_index_dist = math.dist(thumb_tip, index_tip)
            thumb_middle_dist = math.dist(thumb_tip, middle_tip)
            index_middle_dist = math.dist(index_tip, middle_tip)

            # Check if all fingers are open for zoom gesture
            all_fingers_open = are_all_fingers_open(lm_list)
            
            # Check swipe gesture (index + middle fingers together, others closed)
            index_middle_close = index_middle_dist < 50
            ring_closed = ring_tip[1] > middle_tip[1]
            pinky_closed = pinky_tip[1] > ring_tip[1]
            thumb_closed = thumb_tip[1] > index_tip[1]

            swipe_gesture = (index_middle_close and ring_closed and pinky_closed and thumb_closed)

            if all_fingers_open:
                # Zoom mode with single hand
                current_hand_spread = calculate_fingertips_spread(fingertips)
                
                # Visual feedback for zoom mode
                for tip in fingertips:
                    cv2.circle(frame, tip, 8, (255, 165, 0), -1)
                
                # Draw connections between fingertips
                connections = [(0,1), (1,2), (2,3), (3,4)]
                for i, j in connections:
                    cv2.line(frame, fingertips[i], fingertips[j], (255, 165, 0), 3)
                
                cv2.putText(frame, f"ZOOM MODE", (w//2 - 80, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                
                # Perform zoom based on hand spread change
                if current_time - last_zoom_time > ZOOM_COOLDOWN:
                    if prev_hand_spread > 0:
                        spread_change = current_hand_spread - prev_hand_spread
                        
                        if abs(spread_change) > 10:
                            if spread_change > 0:
                                pyautogui.keyDown('ctrl')
                                pyautogui.scroll(100)
                                pyautogui.keyUp('ctrl')
                                print(f"ZOOM IN")
                            else:
                                pyautogui.keyDown('ctrl')
                                pyautogui.scroll(-100)
                                pyautogui.keyUp('ctrl')
                                print(f"ZOOM OUT")
                            
                            last_zoom_time = current_time
                    
                    prev_hand_spread = current_hand_spread

            elif swipe_gesture:
                # Swipe mode for photo slides and reels
                swipe_center = ((index_tip[0] + middle_tip[0]) // 2, (index_tip[1] + middle_tip[1]) // 2)
                
                # Calculate movement
                if current_time - last_swipe_time > SWIPE_COOLDOWN:
                    # Get movement direction
                    dx = index_tip[0] - middle_tip[0]  # Use relative position
                    dy = index_tip[1] - middle_tip[1]
                    
                    if abs(dx) > SWIPE_THRESHOLD or abs(dy) > SWIPE_THRESHOLD:
                        if abs(dx) > abs(dy):
                            # Horizontal swipe - for photo slides
                            if dx > 0:
                                pyautogui.press('right')
                                print("NEXT PHOTO/SLIDE")
                            else:
                                pyautogui.press('left')
                                print("PREVIOUS PHOTO/SLIDE")
                        else:
                            # Vertical swipe - for reels/shorts
                            if dy > 0:
                                pyautogui.press('pagedown')
                                print("NEXT REEL/SHORT")
                            else:
                                pyautogui.press('pageup')
                                print("PREVIOUS REEL/SHORT")
                        
                        last_swipe_time = current_time
                
                # Visual feedback for swipe mode
                cv2.circle(frame, index_tip, 8, (0, 255, 255), -1)
                cv2.circle(frame, middle_tip, 8, (0, 255, 255), -1)
                cv2.line(frame, index_tip, middle_tip, (0, 255, 255), 3)
                cv2.putText(frame, "SWIPE MODE", (swipe_center[0]-50, swipe_center[1]-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
            else:
                # Normal cursor control mode
                # Cursor movement
                ix = np.clip(index_tip[0], FRAME_REDUCTION, w - FRAME_REDUCTION)
                iy = np.clip(index_tip[1], FRAME_REDUCTION, h - FRAME_REDUCTION)
                
                target_x = np.interp(ix, (FRAME_REDUCTION, w - FRAME_REDUCTION), (0, screen_w))
                target_y = np.interp(iy, (FRAME_REDUCTION, h - FRAME_REDUCTION), (0, screen_h))
                
                curr_x = prev_x + (target_x - prev_x) / SMOOTHING
                curr_y = prev_y + (target_y - prev_y) / SMOOTHING
                
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                # Handle clicks
                if not click_cooldown:
                    if thumb_index_dist < CLICK_THRESHOLD:
                        pyautogui.click()
                        print(f"LEFT CLICK")
                        click_cooldown = True
                        last_click_time = current_time
                    
                    elif thumb_middle_dist < CLICK_THRESHOLD:
                        pyautogui.click(button='right')
                        print(f"RIGHT CLICK")
                        click_cooldown = True
                        last_click_time = current_time

                # Visual feedback for normal mode
                cv2.circle(frame, index_tip, 6, (0, 255, 0), -1)
                cv2.circle(frame, thumb_tip, 6, (0, 255, 255), -1)
                cv2.circle(frame, middle_tip, 6, (255, 0, 255), -1)
            
            # Display info
            mode_text = "Zoom Mode" if all_fingers_open else "Swipe Mode" if swipe_gesture else "Normal Mode"
            info_text = [
                f"Mode: {mode_text}",
                f"Thumb-Index: {int(thumb_index_dist)}",
                f"Index-Middle: {int(index_middle_dist)}"
            ]
            
            for i, text in enumerate(info_text):
                cv2.putText(frame, text, (10, 30 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        except Exception as e:
            print(f"Error in hand processing: {e}")
            continue

    # Reset tracking when no hands
    else:
        prev_hand_spread = 0

    # Instructions
    instructions = [
        "Thumb+Index = Left Click",
        "Thumb+Middle = Right Click", 
        "All 5 fingers open = Zoom in/out",
        "Index+Middle together = Photo Slides & Reels",
        f"Press 'Q' to quit"
    ]
    
    for i, text in enumerate(instructions):
        cv2.putText(frame, text, (10, h - 100 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    cv2.imshow("Hand Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n=== Controller Stopped ===")