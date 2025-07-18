import os
from datetime import datetime, timedelta
import pandas as pd
folder = r"\\avrasya\THY_BSK_KURUMSAL_EMNIYET\SFLK_UVAY\HAT_BAKIM_DATA_TRANSFER\AIRBUS_DATA\kodum"
output_folder = r"Q:\Users\E_Aydogdu6\Desktop\SPI"
today = datetime.now()
thirty_days_ago = today - timedelta(days=30)
data = []
with os.scandir(folder) as entries:
   for entry in entries:
       if entry.is_file() and entry.name.endswith(".csv"):
           stat = entry.stat()
           modified_time = datetime.fromtimestamp(stat.st_mtime)
           if modified_time >= thirty_days_ago:
               data.append({
                   "Dosya Adı": entry.name,
                   "Değiştirilme": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                   "Boyut (KB)": round(stat.st_size / 1024, 2)
               })
df = pd.DataFrame(data)
if not df.empty:
   df = df.sort_values(by="Değiştirilme", ascending=False)
   output_file = os.path.join(output_folder, "csv_son_30gun_liste.xlsx")
   df.to_excel(output_file, index=False)
   print("\n📋 Son 30 gün içinde oluşturulan / değiştirilen CSV dosyaları:")
   print(df.to_string(index=False))
   print(f"\n✅ Excel dosyası kaydedildi: {output_file}")
else:
   print("\n⚠️ Son 30 gün içinde yeni CSV dosyası bulunamadı.")