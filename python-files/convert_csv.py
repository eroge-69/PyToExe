import os
import csv

def convert_csv_to_ansi(file_path):
    # 讀取原始 CSV 文件
    with open(file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        data = list(reader)

    # 另存為 ANSI 編碼
    with open(file_path, mode='w', encoding='ansi', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)

if __name__ == "__main__":
    # 設定要轉換的 CSV 文件路徑
    csv_file_path = "your_file.csv"  # 請替換為你的文件路徑
    convert_csv_to_ansi(csv_file_path)
    print(f"{csv_file_path} 已成功轉換為 ANSI 編碼。")