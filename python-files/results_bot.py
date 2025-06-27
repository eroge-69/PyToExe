import requests
from bs4 import BeautifulSoup
import openpyxl
import time

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "نتائج كلية العلوم"
ws.append(["رقم الجلوس", "اسم الطالب", "المجموع"])
results = []

url = "https://services.aun.edu.eg/results/public/ar/exam-result"

for seat in range(1, 1252):
    payload = {
        "academic_year_id": "4",
        "faculty_id": "9",
        "level_id": "1",
        "search_type": "seat",
        "search_value": str(seat)
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        name_tag = soup.find("td", string="اسم الطالب")
        total_tag = soup.find("td", string="المجموع")

        if name_tag and total_tag:
            name = name_tag.find_next("td").text.strip()
            total = total_tag.find_next("td").text.strip().split()[0]
            total_val = int(total)
            results.append((seat, name, total_val))
            ws.append([seat, name, total_val])
            print(f"{seat}: {name} — {total_val}")
        else:
            print(f"{seat}: لا توجد نتيجة")
        time.sleep(0.8)
    except Exception as e:
        print(f"خطأ عند {seat}: {e}")

wb.save("نتائج_علوم_فرقة_أولى.xlsx")
top10 = sorted(results, key=lambda x: x[2], reverse=True)[:10]
wb2 = openpyxl.Workbook()
ws2 = wb2.active
ws2.title = "الأوائل"
ws2.append(["الترتيب", "رقم الجلوس", "اسم الطالب", "المجموع"])
for i, (s, n, t) in enumerate(top10, 1):
    ws2.append([i, s, n, t])
wb2.save("أوائل_علوم_فرقة_أولى.xlsx")
print("✅ تم إنشاء الملفات بنجاح!")
