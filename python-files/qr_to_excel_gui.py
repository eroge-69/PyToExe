import cv2
from pyzbar.pyzbar import decode
import xlwings as xw
import os
import tkinter as tk
from tkinter import messagebox

EXCEL_FILE = 'مطلوب.xlsx'

def scan_qr_and_save():
    cap = cv2.VideoCapture(0)
    found = False

    while True:
        ret, frame = cap.read()
        for barcode in decode(frame):
            data = barcode.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            found = True
            fields = data.split(";")

            if len(fields) < 6:
                messagebox.showerror("خطأ", "QR Code لا يحتوي على كل البيانات المطلوبة.")
                return

            ordered_fields = [
                fields[3],  # Project Name
                fields[0],  # المستفيد
                fields[2],  # بند الأعمال
                fields[4],  # رقم المستخلص
                fields[1],  # المبلغ المستحق شيك
                fields[5],  # تاريخ الاستلام
                ""          # نوع المستخلص (فارغ)
            ]

            save_to_excel(ordered_fields)
            return

        cv2.imshow("Scan QR - اضغط Q للخروج", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if not found:
        messagebox.showinfo("تم", "لم يتم التقاط QR.")
    cap.release()
    cv2.destroyAllWindows()

def save_to_excel(data):
    try:
        # نحاول نوصل لأي Excel مفتوح فيه الملف
        for app in xw.apps:
            for book in app.books:
                if EXCEL_FILE in book.name:
                    sht = book.sheets[0]
                    last_row = sht.range("A" + str(sht.cells.last_cell.row)).end('up').row + 1
                    sht.range(f"A{last_row}").value = data
                    messagebox.showinfo("تم", "✅ تم إدخال البيانات بنجاح.")
                    return

        # لو الملف مش مفتوح، نفتح Excel ونحفظ
        app = xw.App(visible=True)
        if not os.path.exists(EXCEL_FILE):
            wb = app.books.add()
            sht = wb.sheets[0]
            sht.range("A1").value = [
                ["Project Name", "المستفيد", "بند الأعمال", "رقم المستخلص", "المبلغ المستحق شيك", "تاريخ الاستلام", "نوع المستخلص"]
            ]
        else:
            wb = app.books.open(EXCEL_FILE)
            sht = wb.sheets[0]

        last_row = sht.range("A" + str(sht.cells.last_cell.row)).end('up').row + 1
        sht.range(f"A{last_row}").value = data
        wb.save(EXCEL_FILE)
        wb.close()
        app.quit()
        messagebox.showinfo("تم", "✅ تم حفظ البيانات في ملف جديد.")

    except Exception as e:
        messagebox.showerror("خطأ", f"⚠️ حدث خطأ أثناء الحفظ:\n\n{str(e)}")

# واجهة المستخدم
root = tk.Tk()
root.title("🟢 QR إلى Excel")
root.geometry("300x150")

scan_btn = tk.Button(root, text="📷 مسح QR", font=("Arial", 14), command=scan_qr_and_save)
scan_btn.pack(pady=40)

root.mainloop()
