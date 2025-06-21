import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2


MARGIN = -1  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
rect_color=(255,0,255)
TEXT_COLOR = (255, 0, 0)  # red
cap=cv2.VideoCapture(0)
base_options = python.BaseOptions(model_asset_path='best.tflite')
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)
while True:
    ret,frame=cap.read()
    cv2.flip(frame,1)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    
   
    detection_result = detector.detect(mp_image)
    for detection in detection_result.detections:
    # Get bounding box
        bbox = detection.bounding_box
        x = int(bbox.origin_x)
        y = int(bbox.origin_y)
        w = int(bbox.width)
        h = int(bbox.height)
    
    # Draw rectangle
        start_point = (x, y)
        end_point = (x + w, y + h)
        cv2.rectangle(frame, start_point, end_point, rect_color, 3)  # Assuming TEXT_COLOR is (0, 255, 0)
    
    # Get category and probability
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = f"{category_name} ({probability})"
    
    # Set text location above the rectangle
        text_location = (x, y - 10)  # Adjust if necessary
    
    # Put text on the image
        cv2.putText(frame, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)
    
    cv2.imshow("test window", frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()
    
