from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
import mysql.connector
import cv2
from datetime import datetime
from pyzbar.pyzbar import decode
from kivy.clock import Clock
from kivy.graphics.texture import Texture
db = mysql.connector.connect(host = 'localhost' , password = '19Dhanya83@' , user = 'root',database = 'dataforproject')
layout = FloatLayout()

class MyApp(App):
    def build(self):
        self.button1 = Button(text = "IN ",size_hint = (0.3,0.2),pos_hint={'center_x':0.3 , 'center_y':0.2})
        self.button2 = Button(text = "OUT",size_hint = (0.3,0.2),pos_hint={'center_x':0.7 , 'center_y':0.2})
        self.button1.bind(on_press = in_function)
        self.button2.bind(on_press = out_function)
        layout.add_widget(self.button1)
        layout.add_widget(self.button2)
        return layout
    
def in_function(self):
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
    buf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
    image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
    image_texture.blit_buffer(buf.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
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


def out_function(self):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open the camera. Please check if it's connected and not in use.")
        return
    success, image_frame = camera.read()

    if success:
        print("Photo captured successfully.")
        camera.release()
        

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"captured_photo_{timestamp}.png"

        cv2.imwrite(filename, image_frame)
        print(f"Image saved as '{filename}' in the current directory.")

        cv2.waitKey(0) 
        cv2.destroyAllWindows()
    else:
        print("Error: Failed to capture the image.")
        camera.release()
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

if __name__ == '__main__':
    MyApp().run()

