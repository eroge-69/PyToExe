import requests, os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def download(link, name):
    output_file = name + ".mp4"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        response = requests.get(link, stream=True, verify=False)
        response.raise_for_status()
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Tải xuống thành công: {output_file}")
        return "OK"
    except requests.exceptions.RequestException as e:
        print(f"Có lỗi xảy ra khi tải xuống: {e}")
        return "Not OK"

excel_file = input("Nhập tên file Excel: ")
df = pd.read_excel(excel_file)

base_name = os.path.splitext(os.path.basename(excel_file))[0]
if base_name.startswith("DS_"):
    base_name = base_name[3:]
folder = base_name
os.makedirs(folder, exist_ok=True)

def download_and_update(idx, video_link, output_path):
    status = download(video_link, output_path)
    df.at[idx, 'Trạng Thái'] = status

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for idx, row in df.iterrows():
        video_name = str(row['STT'])
        video_link = str(row['VIDEO'])
        output_path = os.path.join(folder, video_name)
        future = executor.submit(download_and_update, idx, video_link, output_path)
        futures.append(future)
    for future in futures:
        future.result()

df.to_excel(excel_file, index=False)
print(f"Kết quả đã được lưu vào {excel_file}")
