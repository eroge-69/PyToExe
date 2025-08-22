import random

def generate_numbers(include_double=True, count=10):
    """
    สร้างเลขสองหลัก จำนวน count ตัว
    include_double = True : รวมเลขเบิ้ล (เช่น 11, 22)
    include_double = False : ไม่รวมเลขเบิ้ล
    """
    results = []
    while len(results) < count:
        num = random.randint(0, 99)
        str_num = f"{num:02d}"  # แปลงเป็นเลขสองหลัก เช่น 07, 23
        if not include_double and str_num[0] == str_num[1]:
            continue  # ข้ามเลขเบิ้ลถ้าไม่เอา
        if str_num not in results:
            results.append(str_num)
    return results

def main():
    print("โปรแกรมจับเลขวิน (สองหลัก)")
    choice = input("ต้องการรวมเลขเบิ้ลหรือไม่? (y=รวม / n=ไม่รวม): ").lower()
    include_double = choice == 'y'
    
    while True:
        try:
            count = int(input("ต้องการจำนวนเลขกี่ตัว?: "))
            if count < 1 or count > 100:
                print("กรุณาใส่จำนวนเลขระหว่าง 1-100")
                continue
            break
        except ValueError:
            print("กรุณาใส่ตัวเลขจำนวนเต็ม")

    numbers = generate_numbers(include_double, count)
    print("เลขที่จับได้:")
    print(", ".join(numbers))

if __name__ == "__main__":
    main()
