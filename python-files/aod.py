import numpy as np
import cv2
from collections import Counter, defaultdict
import time

# For camera input

# first_frame = cv2.VideoCapture(0)
# ret, frame = first_frame.read()
# time.sleep(5)
# cv2.imwrite('img1.png', frame)

# first_frame.release()

# firstframepath = 'img1.png'
# first_frame = cv2.imread(firstframepath)

# firstframe_path = 'FrameNo0.png'
# first_frame = cv2.imread(firstframe_path)

# ------------------------------------------------------------------------

vid_path = 'input.mp4'
cap = cv2.VideoCapture(vid_path)
res, image = cap.read()
print(image.shape)

if res:
    image = cv2.resize(image, (640, 360))
    cv2.imwrite("ref_frame.jpg", image)

# ------------------------------------------------------------------------

reference_frame = cv2.imread("ref_frame.jpg")

# Blur ?
reference_frame = cv2.GaussianBlur(reference_frame, (5, 5), 0)

cap = cv2.VideoCapture(vid_path)
# cap = cv2.VideoCapture(0)
consecutive_frames = 100

frameno = 0

track_temp = []
track_master = []
track_temp2 = []

top_contour_dict = defaultdict(int)
obj_detected_dict = defaultdict(int)


while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        print(ret)
        print("Error reading frame")
        break

    if frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
        # cv2.imshow('main', frame)
        pass

    if not ret:
        print("End")
        break

    frame = cv2.resize(frame, (640, 360))
    frameno += 1

    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    
    frame_diff = cv2.absdiff(reference_frame, blurred)


    # Increase contrast in difference image
    contrast = 1.5
    adjusted = cv2.addWeighted(frame_diff, contrast, frame_diff, 0, 0)

    edge_det = cv2.Canny(adjusted, 150, 225)

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(edge_det, cv2.MORPH_CLOSE, kernel, iterations=2)

    # All output images
    # cv2.imshow("Abs Diff", frame_diff)
    # cv2.imshow("Increased contrast", adjusted)
    # cv2.imshow("Edge Detection", edge_det)
    # cv2.imshow("Morph_Close", thresh)

    line1 = np.concatenate((frame_diff, adjusted), axis=1)
    line2 = np.concatenate((edge_det, thresh), axis=1)

    cv2.imshow("Abs diff", line1)
    cv2.imshow("Edge detection", line2)

    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    my_contours = []

    for c in contours:
        M = cv2.moments(c)

        # To get centroid of contour
        if M['m00'] == 0:
            pass
        else:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # Setting criteria for contour
            # if cv2.contourArea(c) < 200 or cv2.contourArea(c)>20000:
            #     pass
        
            if M['m00'] < 200 or M['m00'] > 2000:
                pass
            else:
                my_contours.append(c)

                (x, y, w, h) = cv2.boundingRect(c)
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
        # ------------------------------------------------------------------
                sumcxcy = (cx, cy)

                track_temp.append([sumcxcy, frameno])
                track_master.append([sumcxcy, frameno])

                countUniqueFrames = set(j for i, j in track_master)

                if len(countUniqueFrames) > consecutive_frames:
                    minFrameNo = min(countUniqueFrames)
                    for i, j in track_master:
                        if j != minFrameNo:
                            track_temp2.append([i, j])
                    
                    track_master = list(track_temp2)
                    track_temp2 = []

                countcxcy = Counter(i for i, j in track_master)

                for i, j in countcxcy.items():
                    if j >= consecutive_frames:
                        top_contour_dict[i] += 1

                if sumcxcy in top_contour_dict:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
                    cv2.putText(frame,'%s'%('CheckObject'), (cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
                    print ('Detected : ', sumcxcy,frameno, obj_detected_dict)

                    obj_detected_dict[sumcxcy] = frameno
                
            keys_to_remove = []

            for i, j in obj_detected_dict.items():
                if frameno - j > 200:
                    # print('PopBefore', i, j, frameno, obj_detected_dict)
                    print('Remove contour: ', i, j, frameno, obj_detected_dict)
                    keys_to_remove.append(i)

            # Remove keys outside the loop
            for key in keys_to_remove:
                obj_detected_dict.pop(key)

            # Set the count for each key to zero
            for key in keys_to_remove:
                top_contour_dict[key] = 0

    cv2.imshow("Bag Detect", frame)

    # Hotkeys for playback
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('p'):
        cv2.waitKey(-1)

        
cap.release()
cv2.destroyAllWindows()