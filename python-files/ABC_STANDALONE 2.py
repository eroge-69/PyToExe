import os
import csv
from datetime import datetime

print("ABC - Tao bang mau Excel")
print("=" * 30)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"ABC_BangMau_{timestamp}.csv"

data = [
    ["Ten", "Cot_B", "Cot_C", "Cot_D", "Cot_E", "Cot_F"],
    ["So met", "XANH", "VANG", "XANH", "VANG", "XANH"],
    ["KTC", "XANH", "VANG", "XANH", "VANG", "XANH"],
    ["PCS", "XANH", "VANG", "XANH", "VANG", "XANH"],
    ["So cay", "XANH", "DO", "DO", "DO", "DO"]
]

try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"Da tao file: {filename}")
    print(f"Vi tri: {os.path.abspath(filename)}")
    print("Mo bang Excel de xem ket qua")
    print("THANH CONG!")
    
    try:
        os.startfile(filename)
    except:
        pass

except Exception as e:
    print(f"Loi: {e}")

print("Nhan phim bat ky de thoat...")
try:
    input()
except:
    pass