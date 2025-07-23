import os
import requests

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพ ถ้ายังไม่มี
os.makedirs('images', exist_ok=True)

# --- ส่วนที่เพิ่มเข้ามา: แมพ Content-Type กับ นามสกุลไฟล์ ---
# แมพชนิดของข้อมูล (MIME Type) กับนามสกุลไฟล์ที่ต้องการ
MIME_TYPE_MAP = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/bmp': '.bmp',
}
# --------------------------------------------------------

# อ่าน URL จากไฟล์ link.txt
try:
    with open('link.txt', 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("!!! ไม่พบไฟล์ link.txt กรุณาสร้างไฟล์และใส่ลิงก์ที่ต้องการดาวน์โหลด !!!")
    links = []

success_count = 0
fail_count = 0
fail_details = []

try:
    if not links:
        print("\nไม่มีลิงก์ในไฟล์ link.txt ให้ดาวน์โหลด")
    else:
        for idx, url in enumerate(links, 1):
            print(f"[{idx}/{len(links)}] กำลังประมวลผล: {url}")
            try:
                # ส่ง request เพื่อดาวน์โหลด โดยตั้ง timeout ไว้ 30 วินาที
                response = requests.get(url, timeout=30)
                # หากมีข้อผิดพลาด (เช่น 404 Not Found, 500 Server Error) จะโยน exception
                response.raise_for_status()

                # --- ส่วนที่แก้ไข: การกำหนดชื่อและนามสกุลไฟล์ ---
                # 1. ดึงชื่อไฟล์พื้นฐานจาก URL
                base_filename = url.split('/')[-1].split('?')[0] # ลบ query string ออกไปด้วย

                # 2. ตรวจสอบว่าชื่อไฟล์จาก URL มีนามสกุลอยู่แล้วหรือไม่
                _, ext_from_url = os.path.splitext(base_filename)

                if ext_from_url.lower() in MIME_TYPE_MAP.values():
                    # ถ้ามีนามสกุลที่รู้จักอยู่แล้ว ก็ใช้ชื่อนั้นเลย
                    filename = base_filename
                else:
                    # ถ้าไม่มีนามสกุล หรือนามสกุลไม่เป็นที่รู้จัก ให้ตรวจสอบจาก Content-Type
                    content_type = response.headers.get('Content-Type')
                    if content_type:
                        # ทำความสะอาด Content-Type (เช่น 'image/jpeg; charset=utf-8' -> 'image/jpeg')
                        mime_type = content_type.split(';')[0].strip()
                        # ค้นหานามสกุลจากแมพที่เราสร้างไว้
                        extension = MIME_TYPE_MAP.get(mime_type)

                        if extension:
                            # ถ้าพบนามสกุล ให้ประกอบชื่อไฟล์ใหม่
                            filename = base_filename + extension
                            print(f"  > ตรวจพบ Content-Type: {mime_type}, กำหนดนามสกุลเป็น {extension}")
                        else:
                            # ถ้าไม่รู้จัก Content-Type ให้ใช้ชื่อเดิมและแจ้งเตือน
                            filename = base_filename
                            print(f"  > คำเตือน: ไม่รู้จัก Content-Type ({mime_type}), บันทึกโดยไม่มีนามสกุล")
                    else:
                        # หากไม่มี Content-Type header ให้ใช้ชื่อเดิมและแจ้งเตือน
                        filename = base_filename
                        print("  > คำเตือน: ไม่พบ Content-Type header, บันทึกโดยไม่มีนามสกุล")
                # ----------------------------------------------------

                # กำหนด path ที่จะบันทึกไฟล์
                save_path = os.path.join('images', filename)

                # เขียนข้อมูลลงไฟล์
                with open(save_path, 'wb') as img_file:
                    img_file.write(response.content)

                print(f"  ✔ ดาวน์โหลดสำเร็จ: {filename}\n")
                success_count += 1

            except requests.exceptions.RequestException as e:
                # จัดการกับข้อผิดพลาดที่เกิดจากการ request โดยเฉพาะ
                filename = url.split('/')[-1]
                print(f"  ✖ ดาวน์โหลดไม่สำเร็จ: {filename} ({e})\n")
                fail_count += 1
                fail_details.append((filename, str(e)))

except KeyboardInterrupt:
    print("\n\n*** หยุดการทำงานโดยผู้ใช้ (KeyboardInterrupt) ***\n")
finally:
    # ส่วนสรุปผลจะทำงานเสมอ ไม่ว่าจะจบปกติ, error, หรือโดน прерывание
    print(f"\nสรุปผลการดาวน์โหลด:")
    print(f"  สำเร็จ: {success_count} ไฟล์")
    print(f"  ล้มเหลว: {fail_count} ไฟล์")
    if fail_details:
        print("\nรายละเอียดไฟล์ที่ล้มเหลว:")
        for fname, err in fail_details:
            print(f"  - {fname}: {err}")