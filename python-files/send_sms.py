import pandas as pd
import serial
import time
import os

def send_sms(modem_port, phone_number, message):
    try:
        modem = serial.Serial(modem_port, 9600, timeout=1)
        time.sleep(2)
        
        modem.write(b'AT\r')
        time.sleep(1)
        modem.write(b'AT+CMGF=1\r')  # SMS текстовый режим
        time.sleep(1)
        modem.write(f'AT+CMGS="{phone_number}"\r'.encode())
        time.sleep(1)
        modem.write(f'{message}\r'.encode())
        time.sleep(1)
        modem.write(bytes([26]))  # Ctrl+Z (SMS жўнатиш)
        time.sleep(2)
        modem.close()
        return True
    except Exception as e:
        print(f"Хатолик: {e}")
        return False

def main():
    print("SMS Жўнатиш Дастурига Хуш келибсиз!")
    excel_file = input("Excel файл номи (sms_data.xlsx): ") or "sms_data.xlsx"
    modem_port = input("Модем порти (COM3, COM4): ") or "COM3"
    
    if not os.path.exists(excel_file):
        print(f"Файл топилмади: {excel_file}")
        return
    
    try:
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            phone = str(row.iloc[0])  # 1-устун (телефон)
            msg = str(row.iloc[1])   # 2-устун (хабар)
            print(f"{phone} га SMS жўнатилмоқда...")
            if send_sms(modem_port, phone, msg):
                print(f"✅ {phone} га SMS жўнатилди!")
            else:
                print(f"❌ {phone} га SMS жўнатилмади!")
    except Exception as e:
        print(f"Хатолик: {e}")

if __name__ == "__main__":
    main()
    input("Давом этиш учун ENTER босинг...")

