import mysql.connector
import cv2
from datetime import datetime
from pyzbar.pyzbar import decode
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
db = mysql.connector.connect(host = 'localhost' , password = '19Dhanya83@' , user = 'root',database = 'dataforproject')


def main():
    global filename
    global root
    root = tk.Tk()
    root.title("QR CODE SCANNER")
    root.geometry("800x600")
    button1 = Button(text = "IN" , padx = 50 , pady = 25 , command=in_function)
    button2 = Button(text = "OUT" , padx = 50 , pady = 25 , command=out_function)
    button1.place(relx = 0.5 , rely = 0.8)
    button2.place(relx = 0.3 , rely = 0.8)
    root.mainloop()

def camera():
    global filename 
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open the camera. Please check if it's connected and not in use.")
        return
    success, frame = camera.read()

    if success:
        print("Photo captured successfully.")
        camera.release()
        

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"captured_photo_{timestamp}.png"

        cv2.imwrite(filename,frame)
        print(f"Image saved as '{filename}' in the current directory.")

        cv2.waitKey(0) 
        cv2.destroyAllWindows()
    else:
        print("Error: Failed to capture the image.")
        camera.release()
    filename

def in_function():
    camera()
    image = filename
    img = cv2.imread(image)
    for code in decode(img):
        name_rollno = code.data.decode('utf-8')
    datas = name_rollno.split(';')
    name = datas[0]
    rollno = datas[1]
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    time_string = current_time.strftime("%H:%M:%S")
    date_string = current_date.strftime("%Y-%m-%d") 
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    time_string =current_time.strftime("%H:%M:%S")
    date_string =current_date.strftime("%Y-%m-%d")
    mycurser = db.cursor()
    query = "INSERT INTO DATA VALUES(%s,%s,%s,%s,%s)"
    val = (name,rollno,date_string,time_string,"IN")
    mycurser.execute(query,val)
    db.commit()


def out_function():
    camera()
    image = filename
    img = cv2.imread(image)
    for code in decode(img):
        name_rollno = code.data.decode('utf-8')
    datas = name_rollno.split(';')
    name = datas[0]
    rollno = datas[1]
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    time_string = current_time.strftime("%H:%M:%S")
    date_string = current_date.strftime("%Y-%m-%d") 
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    time_string =current_time.strftime("%H:%M:%S")
    date_string =current_date.strftime("%Y-%m-%d")
    mycurser = db.cursor()
    query = "INSERT INTO DATA VALUES(%s,%s,%s,%s,%s)"
    val = (name,rollno,date_string,time_string,"OUT")
    mycurser.execute(query,val)
    db.commit()

main()