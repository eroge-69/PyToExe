import cv2
from pyzbar.pyzbar import decode
cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,180)
camera = True
while camera == True:
    suceess,frame = cap.read()
cv2.imshow("QRCODE SCANNER", frame)
cv2.waitKey(1)
