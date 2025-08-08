import cv2
from pyzbar.pyzbar import decode
import pandas as pd
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

# Archivo Excel
archivo_excel = "datos_qr.xlsx"
if os.path.exists(archivo_excel):
    df = pd.read_excel(archivo_excel)
else:
    df = pd.DataFrame(columns=["Contenido QR", "Fecha", "Hora"])

ultimo_qr = ""

class LectorQRApp(App):
    def build(self):
        self.img = Image()
        self.cap = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # 30 FPS
        return self.img

    def update(self, dt):
        global ultimo_qr, df
        ret, frame = self.cap.read()
        if not ret:
            return

        # Decodificar QR
        for qr in decode(frame):
            data = qr.data.decode('utf-8')
            if data != ultimo_qr:
                fecha = datetime.now().strftime("%Y-%m-%d")
                hora = datetime.now().strftime("%H:%M:%S")
                print(f"QR detectado: {data}")
                df = pd.concat([df, pd.DataFrame({"Contenido QR": [data], "Fecha": [fecha], "Hora": [hora]})], ignore_index=True)
                df.to_excel(archivo_excel, index=False)
                ultimo_qr = data

        # Convertir a textura para Kivy
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = texture

    def on_stop(self):
        self.cap.release()

if __name__ == '__main__':
    LectorQRApp().run()
