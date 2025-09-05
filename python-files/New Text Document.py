import serial
import datetime
import time

# عدل المنفذ COM حسب جهازك (مثلاً COM3 في Windows أو /dev/ttyUSB0 في Linux)
ser = serial.Serial("COM3", 9600)
time.sleep(2)  # انتظار الأردوينو يجهز

# الحصول على الوقت الحالي
now = datetime.datetime.now()
time_str = now.strftime("%Y/%m/%d %H:%M:%S")

# إرساله للأردوينو
ser.write((time_str + "\n").encode("utf-8"))
ser.close()
