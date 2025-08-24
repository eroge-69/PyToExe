import cv2
import os
import time

while 1:
    img_path = r'C:\Users\Admin\Documents\hello\captured.jpg'
    img = cv2.imread(img_path)

    cascade_path = r'C:\Users\Admin\Documents\hello\haarcascade_frontalface_default.xml'
    human_cascade = cv2.CascadeClassifier(cascade_path)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    humans = human_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in humans:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    save_path = r'C:\Users\Admin\Documents\hello'
    os.chdir(save_path)

    cv2.imwrite('output.jpg', img)

    print('.')
    time.sleep(0.5)