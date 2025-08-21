# presentation_controller.py
import os
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from tkinter import Tk, filedialog, messagebox
from pptx import Presentation
from PIL import Image
import win32com.client
import tempfile
import comtypes.client
import time

# Handle PyInstaller's temporary directory
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set desired OpenCV window size
display_width, display_height = 1280, 720

def show_error(message):
    """Show error message in a popup window"""
    root = Tk()
    root.withdraw()
    messagebox.showerror("Error", message)
    root.destroy()

def convert_pptx_to_images(file_path):
    """Convert PowerPoint slides to images using PowerPoint COM object"""
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = True
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            presentation = powerpoint.Presentations.Open(file_path)
            image_files = []
            
            for i in range(1, presentation.Slides.Count + 1):
                image_path = os.path.join(temp_dir, f'slide_{i}.jpg')
                presentation.Slides(i).Export(image_path, "JPG", display_width, display_height)
                image_files.append(image_path)
                
            presentation.Close()
            return image_files
            
        except Exception as e:
            show_error(f"Error converting slides: {str(e)}")
            return []
            
        finally:
            powerpoint.Quit()
            
    except Exception as e:
        show_error("Error: Microsoft PowerPoint is required to run this application.")
        return []

def start_slideshow(file_path):
    if not file_path.endswith(".pptx"):
        show_error("Selected file is not a PowerPoint (.pptx) file.")
        return

    print("Converting slides to images...")
    image_files = convert_pptx_to_images(file_path)
    
    if not image_files:
        return
        
    # Load slides
    slides = []
    for image_file in image_files:
        slide_img = cv2.imread(image_file)
        if slide_img is not None:
            slide_img = cv2.resize(slide_img, (display_width, display_height))
            slides.append(slide_img)
        os.remove(image_file)  # Clean up temporary files

    # Camera Setup
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        show_error("Error: Could not access webcam. Please check your camera connection.")
        return
        
    cap.set(3, display_width)
    cap.set(4, display_height)

    # Variables
    imgNumber = 0
    hs, ws = int(150), int(200)  # height and width of small webcam feed
    gestureThreshold = 300
    buttonPressed = False
    buttonCounter = 0
    buttonDelay = 30
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False

    # Hand Detector
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    # Instructions window
    cv2.namedWindow("Instructions")
    instructions_img = np.zeros((400, 400, 3), np.uint8)
    instructions = [
        "Controls:",
        "Thumb up: Previous slide",
        "Pinky up: Next slide",
        "Index + Middle up: Pointer",
        "Index up: Draw",
        "Last 3 fingers up: Erase",
        "Press 'q' to quit"
    ]
    for i, text in enumerate(instructions):
        cv2.putText(instructions_img, text, (10, 50 + i*40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("Instructions", instructions_img)

    while True:
        success, img = cap.read()
        if not success:
            show_error("Error: Failed to capture webcam frame.")
            break
            
        img = cv2.flip(img, 1)
        imgCurrent = slides[imgNumber].copy()

        hands, img = detector.findHands(img)
        cv2.line(img, (0, gestureThreshold), (display_width, gestureThreshold), (0, 255, 0), 10)

        if hands and not buttonPressed:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cx, cy = hand['center']
            lmList = hand['lmList']

            xVal = int(np.interp(lmList[8][0], [display_width//2, display_width], [0, display_width]))
            yVal = int(np.interp(lmList[8][1], [150, display_height-150], [0, display_height]))
            indexFinger = xVal, yVal

            if cy <= gestureThreshold:
                annotationStart = False
                if fingers == [1, 0, 0, 0, 0]:  # Left
                    if imgNumber > 0:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNumber = -1
                        imgNumber -= 1

                if fingers == [0, 0, 0, 0, 1]:  # Right
                    if imgNumber < len(slides) - 1:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNumber = -1
                        imgNumber += 1

            if fingers == [0, 1, 1, 0, 0]:  # Pointer
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                annotationStart = False

            if fingers == [0, 1, 0, 0, 0]:  # Drawing
                if not annotationStart:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                annotations[annotationNumber].append(indexFinger)
            else:
                annotationStart = False

            if fingers == [0, 0, 1, 1, 1]:  # Erase
                if annotations and annotationNumber > -1:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        else:
            annotationStart = False

        if buttonPressed:
            buttonCounter += 1
            if buttonCounter > buttonDelay:
                buttonCounter = 0
                buttonPressed = False

        for i in range(len(annotations)):
            for j in range(1, len(annotations[i])):
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)

        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w-ws:w] = imgSmall

        cv2.imshow("Slides", imgCurrent)
        cv2.imshow("Webcam", img)

        key = cv2.waitKey(1)
        if key == ord('q') or cv2.getWindowProperty("Slides", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

def select_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PowerPoint files", "*.pptx")])
    if file_path:
        file_path = os.path.abspath(file_path)
        start_slideshow(file_path)

if __name__ == "__main__":
    try:
        select_file()
    except Exception as e:
        show_error(f"An unexpected error occurred: {str(e)}")                         
 









    












