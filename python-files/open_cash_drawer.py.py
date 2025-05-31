import serialimport time
# กำหนดพอร์ต COM ที่เครื่องพิมพ์เชื่อมต่อport = 'USB001'
# เปลี่ยนเป็นพอร์ตที่คุณใช้จริงbaudrate = 9600
# อัตราการส่งข้อมูล
# สร้างการเชื่อมต่อtry:    ser = serial.Serial(port, baudrate, timeout=1)    time.sleep(2)
# รอให้การเชื่อมต่อเสร็จสมบูรณ์
# คำสั่งเปิดลิ้นชัก (ตัวอย่างคำสั่ง)    open_drawer_command = b'\x1B\x70\x00\x19\xFA'
# คำสั่ง ASCII เพื่อเปิดลิ้นชัก
# ส่งคำสั่งไปยังลิ้นชัก    ser.write(open_drawer_command)    print("ลิ้นชักเก็บเงินเปิดแล้ว!")except serial.SerialException as e:    print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")finally:    if 'ser' in locals() and ser.is_open:        ser.close()
