import pandas as pd
import re
from datetime import datetime
import os

def extract_data(source_file, dest_file):
    # ตรวจสอบว่าไฟล์ต้นทางมีอยู่จริง
    if not os.path.exists(source_file):
        print(f"ไฟล์ต้นทาง '{source_file}' ไม่พบ!")
        print("โปรดตรวจสอบว่าไฟล์อยู่ในตำแหน่งที่ถูกต้อง")
        return
    
    try:
        # อ่านไฟล์ต้นทางโดยไม่กำหนด header
        df_source = pd.read_excel(source_file, header=None)
        
        # ดึงข้อมูลปีและเดือนจาก H3 (row=2, column=7)
        date_str = df_source.iloc[2, 7]
        try:
            date_obj = datetime.strptime(str(date_str), '%d.%m.%Y')
            year = date_obj.year
            month = date_obj.month
        except:
            year = None
            month = None
        
        # ดึง Import_Date จาก H7 (row=6, column=7)
        import_date = df_source.iloc[6, 7]
        
        # Forward fill สำหรับ Category (column E) และ Subcategory (column D)
        df_source[4] = df_source[4].ffill()  # column E (index=4)
        df_source[3] = df_source[3].ffill()  # column D (index=3)
        
        # เตรียมลิสต์สำหรับเก็บข้อมูลที่จะบันทึก
        data = []
        
        # วนลูปทุกแถวในไฟล์ต้นทาง
        for idx, row in df_source.iterrows():
            # ตรวจสอบเฉพาะแถวที่มีข้อมูลในคอลัมน์ I (index 8)
            if pd.isna(row[8]):
                continue
                
            # ดึงข้อมูลจากคอลัมน์ I
            cell_value = str(row[8]).strip()
            
            # ค้นหาบัญชี 10 หลัก
            account_match = re.search(r'(\d{10})', cell_value)
            
            if account_match:
                # กรณีพบตัวเลข 10 หลัก
                account_code = account_match.group(1)
                
                # แยกชื่อบัญชีโดยลบตัวเลข 10 หลักออก
                account_name = re.sub(r'\d{10}\s*', '', cell_value).strip()
            else:
                # กรณีไม่พบตัวเลข 10 หลัก
                account_code = cell_value  # ใช้ข้อความทั้งหมดเป็น Account_Code
                account_name = cell_value  # ใช้ข้อความทั้งหมดเป็น Account_Name
            
            # ดึง Amount จากคอลัมน์ M (index 12)
            amount = row[12]
            
            # ตั้งค่าเริ่มต้นสำหรับ Status
            status = "DONE"
            
            # ตรวจสอบข้อมูลที่จำเป็น
            if (
                pd.isna(year) or 
                pd.isna(month) or 
                pd.isna(amount) or 
                pd.isna(row[4]) or  # Category
                pd.isna(row[3])     # Subcategory
            ):
                status = "Error"
            else:
                try:
                    # พยายามแปลง amount เป็น float
                    amount = float(amount)
                except:
                    status = "Error"
            
            # เพิ่มข้อมูลลงในลิสต์
            data.append({
                'Account_Code': account_code,
                'Account_Name': account_name,
                'Year': year,
                'Month': month,
                'Amount': amount,
                'Category': row[4],
                'Subcategory': row[3],
                'Data_Source': 'ERP',
                'Import_Date': import_date,
                'Status': status
            })
        
        # สร้าง DataFrame ใหม่
        result_df = pd.DataFrame(data)
        
        # บันทึกลงไฟล์ปลายทาง
        result_df.to_excel(dest_file, index=False)
        print(f"บันทึกข้อมูลสำเร็จที่: {dest_file}")
        print(f"พบข้อมูลทั้งหมด {len(data)} แถว")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะประมวลผล: {str(e)}")

if __name__ == "__main__":
    # ระบุตำแหน่งไฟล์แบบเต็ม
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    source_file = os.path.join(desktop_path, "MU01.xlsx")
    dest_file = os.path.join(desktop_path, "Book1.xlsx")
    
    print("="*50)
    print(f"กำลังประมวลผลไฟล์ต้นทาง: {source_file}")
    print(f"ไฟล์ผลลัพธ์จะถูกบันทึกที่: {dest_file}")
    print("="*50)
    
    # เรียกใช้งานฟังก์ชัน
    extract_data(source_file, dest_file)
    
    # รอผู้ใช้กด Enter ก่อนปิดหน้าต่าง (สำหรับ .exe)
    input("\nกด Enter เพื่อปิดโปรแกรม...")