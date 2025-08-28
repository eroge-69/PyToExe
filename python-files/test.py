import os
import shutil
import sys

def create_huge_file():
    """
    สร้างไฟล์ว่างขนาดใหญ่เท่ากับพื้นที่ที่เหลือของ Drive C บน Desktop
    """
    print("--- คำเตือนที่สำคัญมาก ---")
    print("โปรแกรมนี้จะสร้างไฟล์ขนาดใหญ่จนเต็มพื้นที่ว่างบน Drive C:")
    print("การกระทำนี้อาจทำให้ระบบทำงานช้าลง, ไม่เสถียร หรือหยุดทำงานได้!")
    print("โปรดบันทึกงานทั้งหมดและปิดโปรแกรมที่ไม่จำเป็นก่อนดำเนินการต่อ")
    print("-" * 28)

    # ถามเพื่อยืนยันการทำงาน
    confirm = input("ต้องการดำเนินการต่อหรือไม่? (พิมพ์ 'y' เพื่อยืนยัน): ")
    if confirm.lower() != 'y':
        print("ยกเลิกการทำงาน")
        return

    try:
        # 1. หาพื้นที่ว่างที่เหลืออยู่บนไดรฟ์ C:
        print("\nกำลังตรวจสอบพื้นที่ว่างบน Drive C:...")
        # shutil.disk_usage จะให้ข้อมูลเป็น bytes
        total, used, free = shutil.disk_usage('C:\\')
        
        if free <= 0:
            print("ไม่มีพื้นที่ว่างเหลือบนดิสก์")
            return
            
        # แปลงเป็น GB เพื่อให้แสดงผลสวยงาม
        free_gb = free / (1024**3)
        print(f"พบพื้นที่ว่าง: {free_gb:.2f} GB")

        # 2. หาตำแหน่งของ Desktop
        # os.path.expanduser('~') จะได้ path ไปยัง home directory ของ user (เช่น C:\Users\YourUser)
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        file_path = os.path.join(desktop_path, 'random.txt')
        print(f"จะทำการสร้างไฟล์ที่: {file_path}")

        # 3. สร้างไฟล์ขนาดใหญ่ด้วยวิธีที่รวดเร็ว (Sparse file)
        print("กำลังสร้างไฟล์ขนาดใหญ่ โปรดรอสักครู่...")
        with open(file_path, 'wb') as f:
            # ย้าย cursor ไปยังตำแหน่งเกือบท้ายสุด
            f.seek(free - 1)
            # เขียนข้อมูล 1 byte ลงไปเพื่อให้ระบบจองพื้นที่ทั้งหมด
            f.write(b'\0')

        print("\nสร้างไฟล์ 'random.txt' สำเร็จ!")
        print("!!! โปรดลบไฟล์นี้ทิ้งโดยเร็วที่สุดเพื่อคืนพื้นที่ให้ระบบ !!!")

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}", file=sys.stderr)

if __name__ == "__main__":
    create_huge_file()