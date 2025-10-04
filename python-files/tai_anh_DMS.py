from sshtunnel import SSHTunnelForwarder
from pyhive import hive
import pandas as pd
import os
from minio import Minio
from minio.error import S3Error
import tkinter as tk
from tkinter import simpledialog

# === Tạo SSH Tunnel giống lệnh ssh -L ===
tunnel = SSHTunnelForwarder(
    ssh_address_or_host=("27.66.108.46", 22),   
    ssh_username="vpn",                        
    ssh_password="RD@2025",              
    remote_bind_address=("10.12.4.80", 10016),  
    local_bind_address=("127.0.0.1", 10016)
)

tunnel.start()

print(f"🚀 Tunnel started at {tunnel.local_bind_host}:{tunnel.local_bind_port}")

# === Kết nối Hive thông qua tunnel ===
conn = hive.Connection(
    host=tunnel.local_bind_host,
    port=tunnel.local_bind_port,
    username='ral01',   # user Hive
    database='whs'
)


# # ==== 3. Cấu hình khoảng ngày ====
# start_date = "2025-09-20"
# end_date   = "2025-09-26"

# # Nếu muốn nhập từ bàn phím
# start_date = input("Nhập ngày bắt đầu (yyyy-mm-dd): ")
# end_date = input("Nhập ngày kết thúc (yyyy-mm-dd): ")

root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính

start_date = simpledialog.askstring("Input", "Nhập Start Date (YYYY-MM-DD):")
end_date = simpledialog.askstring("Input", "Nhập End Date (YYYY-MM-DD):")

print("Start:", start_date)
print("End:", end_date)

print(f"Chạy dữ liệu từ {start_date} đến {end_date}")

query = f"""
SELECT 
    ROW_NUMBER() OVER (ORDER BY mp.Code ASC) AS STT,
    so.Name AS `Tên đơn vị`,
    mp.Code AS `Mã vấn đề`,
    ma.Username AS `Mã nhân viên`,
    ma.DisplayName AS `Tên nhân viên`,
    DATE_FORMAT(FROM_UTC_TIMESTAMP(mp.NoteAt, 'Asia/Bangkok'), 'yyyy-MM-dd') AS `Ngày`,
    md.Code AS `Mã đại lý`,
    md.Name AS `Tên đại lý`,
    md.Address AS `Địa chỉ`,
    mp2.Name AS `Tỉnh/TP`,
    md2.Name AS `Quận/huyện`,
    mp.Content AS `Nội dung vấn đề`,
    mp3.Name AS `Loại vấn đề`,
    mp4.Name AS `Trạng thái`,
    mp5.`Số lượng ảnh`,
    mp5.`Danh sách RowId`
FROM whs.masterdata_problem mp
LEFT JOIN whs.masterdata_dmsstore md ON mp.StoreId = md.Id AND md.EndDate = '9999-12-31'
LEFT JOIN whs.masterdata_appuser ma ON mp.CreatorId = ma.Id 
LEFT JOIN whs.salechannel_organization so ON md.OrganizationId = so.Id
LEFT JOIN whs.masterdata_province mp2 ON md.ProvinceId = mp2.Id 
LEFT JOIN whs.masterdata_district md2 ON md.DistrictId = md2.Id 
LEFT JOIN whs.masterdata_problemtype mp3 ON mp.ProblemTypeId = mp3.Id
LEFT JOIN whs.masterdata_problemstatus mp4 ON mp.ProblemStatusId = mp4.Id
LEFT JOIN (
    SELECT  
        ProblemId, 
        COUNT(ImageId) AS `Số lượng ảnh`, 
        CONCAT_WS(',', COLLECT_SET(pi.RowId)) AS `Danh sách RowId`
    FROM whs.masterdata_problemimagemapping mp5 
    LEFT JOIN whs.product_image pi ON mp5.ImageId = pi.Id 
    GROUP BY ProblemId
) mp5 ON mp.Id = mp5.ProblemId
WHERE DATE_FORMAT(FROM_UTC_TIMESTAMP(mp.NoteAt, 'Asia/Bangkok'), 'yyyy-MM-dd')
      BETWEEN '{start_date}' AND '{end_date}'
ORDER BY mp.Code ASC
"""

df = pd.read_sql(query, conn)

# ==== 4. Kết nối MinIO ====
client = Minio(
    "192.168.21.175:9000",
    access_key="admin",
    secret_key="123@123AErp@1234",
    secure=False
)

bucket = "rdproduction"
base_prefix = "file/ShortTerm"

# ==== 5. Thư mục lưu ảnh ====
download_dir = f"{start_date.replace('-','')}_{end_date.replace('-','')}"
os.makedirs(download_dir, exist_ok=True)

# ==== 6. Vòng lặp tải ảnh ====
for _, row in df.iterrows():
    raw_date = row["Ngày"]
    if pd.isna(raw_date):
        continue
    date_str = pd.to_datetime(raw_date).strftime("%Y%m%d")

    row_ids_str = row.get("Danh sách RowId")
    if pd.isna(row_ids_str) or str(row_ids_str).strip() == "":
        continue

    row_ids = [rid.strip() for rid in str(row_ids_str).split(",") if rid.strip()]
    for rid in row_ids:
        rid_lower = rid.lower()
        object_name = f"{base_prefix}/{date_str}/{rid_lower}.jpg"
        local_path = os.path.join(download_dir, f"{rid_lower}.jpg")
        try:
            client.fget_object(bucket, object_name, local_path)
            print(f"✅ Đã tải {object_name} -> {local_path}")
        except S3Error as e:
            print(f"⚠️ Lỗi khi tải {object_name}: {e}")

# Đóng kết nối
conn.close()
tunnel.stop()
