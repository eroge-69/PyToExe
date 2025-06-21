#!/usr/bin/env python3
"""
ระบบแปลงข้อมูลจากไฟล์ ERP ต้นฉบับ ไปยัง IPSR Analysis System
โดย MiniMax Agent

ระบบนี้จะ:
1. อ่านข้อมูลจากไฟล์ต้นฉบับ (รูปแบบ ERP Report)
2. แยกข้อมูล Account Code, Account Name, และ Amount
3. แปลงให้อยู่ในรูปแบบที่ IPSR Analysis System ต้องการ
4. บันทึกลงไฟล์ IPSR Analysis System โดยอัตโนมัติ
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os

class ERPToIPSRConverter:
    def __init__(self):
        self.source_file = "/workspace/user_input_files/ต้นฉบับ.xlsx"
        self.target_file = "/workspace/user_input_files/IPSR Analysis System.xlsx"
        self.output_file = "/workspace/data/IPSR_Analysis_System_Updated.xlsx"
        
        # กำหนด category mapping สำหรับการจำแนกประเภท
        self.category_mapping = {
            # สินทรัพย์
            '11': {'category': 'สินทรัพย์', 'subcategory': 'สินทรัพย์หมุนเวียน'},
            '12': {'category': 'สินทรัพย์', 'subcategory': 'สินทรัพย์ไม่หมุนเวียน'},
            '13': {'category': 'สินทรัพย์', 'subcategory': 'สินทรัพย์อื่น'},
            
            # หนี้สิน  
            '21': {'category': 'หนี้สิน', 'subcategory': 'หนี้สินหมุนเวียน'},
            '22': {'category': 'หนี้สิน', 'subcategory': 'หนี้สินไม่หมุนเวียน'},
            
            # ทุน
            '31': {'category': 'ทุน', 'subcategory': 'ทุนและกำไรสะสม'},
            
            # รายได้
            '41': {'category': 'รายได้', 'subcategory': 'รายได้หลัก'},
            '42': {'category': 'รายได้', 'subcategory': 'รายได้อื่น'},
            
            # ค่าใช้จ่าย
            '51': {'category': 'ค่าใช้จ่าย', 'subcategory': 'ค่าใช้จ่ายบุคลากร'},
            '52': {'category': 'ค่าใช้จ่าย', 'subcategory': 'ค่าใช้จ่ายดำเนินงาน'},
            '53': {'category': 'ค่าใช้จ่าย', 'subcategory': 'ค่าใช้จ่ายอื่น'}
        }
    
    def extract_financial_data(self):
        """แยกข้อมูลทางการเงินจากไฟล์ต้นฉบับ"""
        print("🔍 อ่านและแยกข้อมูลจากไฟล์ต้นฉบับ...")
        
        # อ่านไฟล์ต้นฉบับ
        df = pd.read_excel(self.source_file, sheet_name='test system')
        
        extracted_data = []
        current_date = datetime.now()
        
        print(f"📊 พบข้อมูล {len(df)} แถว กำลังประมวลผล...")
        
        # สร้าง pattern สำหรับหา Account Code และ Amount
        account_pattern = r'(\d{10})'  # รหัสบัญชี 10 หลัก
        amount_pattern = r'([-]?\d{1,3}(?:,?\d{3})*\.?\d*)'  # จำนวนเงิน
        
        for idx, row in df.iterrows():
            # รวมข้อมูลทั้งแถวเป็น string
            row_text = ' '.join([str(val) for val in row.values if pd.notna(val)])
            
            if not row_text or row_text.strip() == '':
                continue
                
            # ค้นหา Account Code
            account_matches = re.findall(account_pattern, row_text)
            
            if account_matches:
                account_code = account_matches[0]
                
                # หา Account Name (ข้อความหลัง Account Code)
                account_name_match = re.search(f'{account_code}\s+(.+?)(?:\s+{amount_pattern}|$)', row_text)
                account_name = ""
                if account_name_match:
                    account_name = account_name_match.group(1).strip()
                    # ทำความสะอาด Account Name
                    account_name = re.sub(r'[=]+>', '', account_name).strip()
                
                # หาจำนวนเงิน
                amounts = re.findall(amount_pattern, row_text)
                if amounts:
                    # เอาจำนวนเงินตัวสุดท้าย (มักจะเป็นยอดคงเหลือ)
                    amount_str = amounts[-1].replace(',', '')
                    try:
                        amount = float(amount_str)
                        
                        # จำแนกประเภทตาม Account Code
                        category_key = account_code[:2]
                        category_info = self.category_mapping.get(category_key, {
                            'category': 'อื่นๆ', 
                            'subcategory': 'ไม่ระบุ'
                        })
                        
                        # เพิ่มข้อมูลลงในรายการ
                        extracted_data.append({
                            'Account_Code': account_code,
                            'Account_Name': account_name,
                            'Year': 2567,  # ปีงบประมาณ
                            'Month': 10,   # เดือนจากรายงาน (31.10.2024)
                            'Amount': amount,
                            'Category': category_info['category'],
                            'Subcategory': category_info['subcategory'],
                            'Data_Source': 'ERP',
                            'Import_Date': current_date.strftime('%d.%m.%Y'),
                            'Status': 'Imported'
                        })
                        
                    except ValueError:
                        continue
        
        print(f"✅ แยกข้อมูลได้ {len(extracted_data)} รายการ")
        return pd.DataFrame(extracted_data)
    
    def update_ipsr_system(self, financial_data):
        """อัปเดตข้อมูลใน IPSR Analysis System"""
        print("🔄 อัปเดตข้อมูลใน IPSR Analysis System...")
        
        # สร้างหรือคัดลอกไฟล์ IPSR
        if not os.path.exists("/workspace/data"):
            os.makedirs("/workspace/data")
        
        # คัดลอกไฟล์ต้นฉบับ IPSR
        import shutil
        shutil.copy2(self.target_file, self.output_file)
        
        # อัปเดต Monthly_Data sheet
        with pd.ExcelWriter(self.output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            financial_data.to_excel(writer, sheet_name='Monthly_Data', index=False)
        
        print(f"✅ บันทึกข้อมูลลงไฟล์: {self.output_file}")
        return self.output_file
    
    def generate_summary_report(self, financial_data):
        """สร้างรายงานสรุปผลการแปลงข้อมูล"""
        print("📋 สร้างรายงานสรุป...")
        
        summary = {
            'จำนวนรายการทั้งหมด': len(financial_data),
            'ยอดรวมสินทรัพย์': financial_data[financial_data['Category'] == 'สินทรัพย์']['Amount'].sum(),
            'ยอดรวมหนี้สิน': financial_data[financial_data['Category'] == 'หนี้สิน']['Amount'].sum(),
            'ยอดรวมรายได้': financial_data[financial_data['Category'] == 'รายได้']['Amount'].sum(),
            'ยอดรวมค่าใช้จ่าย': financial_data[financial_data['Category'] == 'ค่าใช้จ่าย']['Amount'].sum(),
        }
        
        # สร้างรายงานแยกตามประเภท
        category_summary = financial_data.groupby('Category').agg({
            'Amount': ['count', 'sum'],
            'Account_Code': 'nunique'
        }).round(2)
        
        return summary, category_summary
    
    def convert(self):
        """ฟังก์ชันหลักสำหรับแปลงข้อมูล"""
        print("🚀 เริ่มการแปลงข้อมูลจาก ERP ไปยัง IPSR Analysis System")
        print("="*70)
        
        try:
            # 1. แยกข้อมูลจากไฟล์ต้นฉบับ
            financial_data = self.extract_financial_data()
            
            if financial_data.empty:
                print("❌ ไม่พบข้อมูลทางการเงินที่สามารถแยกได้")
                return None
            
            # 2. อัปเดต IPSR System
            output_file = self.update_ipsr_system(financial_data)
            
            # 3. สร้างรายงานสรุป
            summary, category_summary = self.generate_summary_report(financial_data)
            
            # 4. แสดงผลสรุป
            print("\n📊 สรุปผลการแปลงข้อมูล")
            print("="*50)
            for key, value in summary.items():
                print(f"• {key}: {value:,.2f}")
            
            print(f"\n📈 สรุปแยกตามประเภท:")
            print(category_summary)
            
            print(f"\n💾 ไฟล์ผลลัพธ์: {output_file}")
            print(f"✅ การแปลงข้อมูลเสร็จสมบูรณ์!")
            
            return {
                'output_file': output_file,
                'data': financial_data,
                'summary': summary,
                'category_summary': category_summary
            }
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            raise

def main():
    """ฟังก์ชันหลักสำหรับรันระบบ"""
    converter = ERPToIPSRConverter()
    result = converter.convert()
    
    if result:
        print(f"\n🎉 สำเร็จ! ไฟล์ที่อัปเดตแล้ว: {result['output_file']}")
        
        # แสดงตัวอย่างข้อมูลที่แปลงแล้ว
        print(f"\n📋 ตัวอย่างข้อมูลที่แปลงแล้ว (5 รายการแรก):")
        print(result['data'].head().to_string(index=False))

if __name__ == "__main__":
    main()
