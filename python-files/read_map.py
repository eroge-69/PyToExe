
import os
import cv2
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from pytesseract import Output
import time

def read(lower_arr,higher_arr,janein:bool=False,rec_bounds:tuple=(0,0,0,0)):
    
    Pfad = f"{os.getcwd()}\\"
    pytesseract.tesseract_cmd = f'{Pfad}\\Tesseract-OCR\\tesseract.exe'
    
    time.sleep(1)
    file_name = f'C:\\Users\\Lukas\\curseforge\\minecraft\\Instances\\Sever\\screenshots\\neu.png'
    image = cv2.imread(file_name)

    x1,y1,x2,y2 = rec_bounds
    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
       image = cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), -1)


    width,height = image.shape[1::-1]
    lower_blue = np.array(lower_arr) 
    upper_blue = np.array(higher_arr)
    ressourcen_arr = ["0"]
    #x,y,w,h = point
    #cropped = image[y:y+h,x:x+w]
    blau = cv2.inRange(image, lower_blue, upper_blue) 
    cropped = cv2.bitwise_and(image, image, mask = blau)

    

    #if w < 100 and h < 100:
        #cropped = cv2.resize(cropped ,(w*2,h*2))
    #cv2.imshow("test",cropped)
    #cv2.waitKey(0)
        
    results = pytesseract.image_to_data(image=cropped,output_type=Output.DICT)
    replace_arr = [".","“~"," ","oF","‘"]
    for i in range(0, len(results["text"])):
        x_neu = results["left"][i]
        y_neu = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        text = results["text"][i]
        text = text.replace("%","0")
        if janein:
            text = text.replace("o","0")
            text = text.replace("g","9")
        text = text.replace(" ","")
        text = text.replace("l","1")
        with open(r"C:\Users\Lukas\curseforge\minecraft\Instances\Sever\minescript\map_text.txt", "w", encoding="utf-8", errors="replace") as file:
            file.write(f"{text}")
        
    return text

read((0,205,0),(200,255,255))