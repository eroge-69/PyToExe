
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout

class HeadshotTrackerApp(App):
    def build(self):
        self.img = Image()
        layout = BoxLayout()
        layout.add_widget(self.img)
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # 30 FPS
        return layout

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            head_x = x + w // 2
            head_y = y + int(h * 0.25)  # Forehead area
            cv2.circle(frame, (head_x, head_y), 5, (255, 0, 255), -1)  # Purple dot
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert image to texture
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = texture

    def on_stop(self):
        self.capture.release()

if __name__ == '__main__':
    HeadshotTrackerApp().run()
