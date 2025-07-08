
import cv2
import numpy as np
import keyboard

tracking = False

def toggle_tracking():
    global tracking
    tracking = not tracking
    print("Tracking ENABLED" if tracking else "Tracking DISABLED")

keyboard.add_hotkey('F2', toggle_tracking)

# Start capturing from webcam (or change to screen capture)
cap = cv2.VideoCapture(0)

# Size of the output view
view_width, view_height = 400, 400

while True:
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    if not ret:
        break

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if tracking:
        max_area = 0
        target = None

        # Find largest moving object
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500 and area > max_area:
                max_area = area
                target = contour

        if target is not None:
            (x, y, w, h) = cv2.boundingRect(target)
            center_x = x + w // 2
            center_y = y + h // 2

            # Define the new view area around the target
            x1 = max(center_x - view_width // 2, 0)
            y1 = max(center_y - view_height // 2, 0)
            x2 = min(x1 + view_width, frame1.shape[1])
            y2 = min(y1 + view_height, frame1.shape[0])

            cropped_frame = frame1[y1:y2, x1:x2]
            cv2.rectangle(cropped_frame, (w // 2 - w // 4, h // 2 - h // 4),
                          (w // 2 + w // 4, h // 2 + h // 4), (0, 255, 0), 2)

            cv2.imshow('Lock-On Camera View', cropped_frame)
        else:
            cv2.imshow('Lock-On Camera View', frame1)
    else:
        cv2.imshow('Lock-On Camera View', frame1)

    if cv2.waitKey(10) == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
