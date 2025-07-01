import tkinter as tk
from tkinter import messagebox, Frame, Canvas, Scrollbar
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import datetime
import os
import requests

def load_invoice_number():
    try:
        with open("invoice_number.txt", "r") as f:
            return int(f.read())
    except:
        return 1

def save_invoice_number(num):
    with open("invoice_number.txt", "w") as f:
        f.write(str(num))

pdfmetrics.registerFont(TTFont("Arabic", "arabic.ttf"))

def reshape(text):
    return get_display(arabic_reshaper.reshape(text))



def draw_text(c, text, x, y, size=12, color=HexColor("#000000"), align="right"):
    c.setFillColor(color)
    c.setFont("Arabic", size)
    try:
        text_str = str(text).strip()
        if "د.ع" in text_str or all(ch.isdigit() or ch in ".," for ch in text_str.replace("د.ع", "").strip()):
            bidi_text = text_str
        elif any('؀' <= ch <= 'ۿ' for ch in text_str):
            reshaped = arabic_reshaper.reshape(text_str)
            bidi_text = get_display(reshaped)
        else:
            bidi_text = text_str

        if align == "left":
            c.drawString(x, y, bidi_text)
        elif align == "center":
            c.drawCentredString(x, y, bidi_text)
        else:
            c.drawRightString(x, y, bidi_text)
    except:
        c.drawRightString(x, y, str(text))

def حفظ_pdf(رقم, زبون, عنوان, تاريخ, منتجات, ملاحظات, المجموع):
    path = f"فاتورة_{رقم}.pdf"
    c = pdfcanvas.Canvas(path, pagesize=A4)
    w, h = A4

    def format_currency(value):
        try:
            return f"{float(value):,.2f} د.ع"
        except:
            return "0.00 د.ع"

    draw_text(c, "فاتورة مبيعات", w/2, h - 45, 22, white, align="center")

    c.setFillColor(HexColor("#0d47a1"))
    c.rect(0, h - 90, w, 90, fill=1)
    draw_text(c, f"الرقم التلقائي: {entry_رقم_تلقائي.get()}", 60, h - 110, 12, HexColor("#000000"), align="left")
    draw_text(c, f"الرقم اليدوي: {entry_رقم_يدوي.get()}", 60, h - 130, 12, HexColor("#000000"), align="left")
    draw_text(c, f"رقم هاتف الزبون: {عنوان}", w - 60, h - 130, 12, HexColor("#000000"))

    y = h - 170
    c.setFillColor(HexColor("#eeeeee"))
    c.rect(40, y - 5, w - 80, 25, fill=1)
    draw_text(c, "م", 60, y + 5, 12, HexColor("#000000"), align="left")
    draw_text(c, "الوصف", 130, y + 5, 12, HexColor("#000000"), align="left")
    draw_text(c, "الكمية", 300, y + 5, 12, HexColor("#000000"), align="left")
    draw_text(c, "السعر", 400, y + 5, 12, HexColor("#000000"), align="left")
    draw_text(c, "الإجمالي", 500, y + 5, 12, HexColor("#000000"), align="left")

    y -= 30
    total = 0
    for i, row in enumerate(منتجات, 1):
        if not row[0].strip():
            continue
        اسم, كمية, سعر, مجموع = row
        try:
            مجموع = float(كمية) * float(سعر)
        except:
            مجموع = 0
        total += مجموع

        رقم_م = str(i)
        الاسم_منسق = reshape(اسم)
        الكمية_منسقة = str(كمية)
        السعر_منسق = format_currency(سعر)
        الاجمالي_منسق = format_currency(مجموع)

        draw_text(c, رقم_م, 60, y, 11, HexColor("#000000"), align="left")
        draw_text(c, الاسم_منسق, 130, y, 11, HexColor("#000000"), align="left")
        draw_text(c, الكمية_منسقة, 300, y, 11, HexColor("#000000"), align="left")
        draw_text(c, السعر_منسق, 400, y, 11, HexColor("#000000"), align="left")
        draw_text(c, الاجمالي_منسق, 500, y, 11, HexColor("#000000"), align="left")
        y -= 22

    y -= 20
    draw_text(c, "المجموع الكلي:", w * 0.25, y, 13, HexColor("#0d47a1"), align="left")
    draw_text(c, format_currency(total), w * 0.4, y, 13, HexColor("#0d47a1"), align="left")

    c.setFillColor(HexColor("#0d47a1"))
    c.rect(0, 0, w, 30, fill=1)
    draw_text(c, "توقيع المستلم:", w - 60, 45, 12, HexColor("#000000"), align="right")
    c.save()
    return path

def حساب_المجموع():
    المجموع = 0
    for row in rows:
        try:
            كمية = int(row[2].get())
            سعر = float(row[3].get())
            المجموع += كمية * سعر
        except:
            continue
    entry_المجموع.delete(0, tk.END)
    entry_المجموع.insert(0, str(round(المجموع, 2)))

def حفظ():
    رقم = entry_رقم_يدوي.get() or entry_رقم_تلقائي.get()
    زبون = entry_زبون.get()
    عنوان = entry_عنوان.get()
    تاريخ = entry_تاريخ.get()
    ملاحظات = entry_ملاحظات.get()
    المجموع = float(entry_المجموع.get())
    منتجات = []
    for row in rows:
        وصف = row[1].get()
        كمية = row[2].get()
        سعر = row[3].get()
        if وصف and كمية and سعر:
            try:
                إجمالي = int(كمية) * float(سعر)
            except:
                إجمالي = 0
            منتجات.append((وصف, كمية, سعر, إجمالي))
    path = حفظ_pdf(رقم, زبون, عنوان, تاريخ, منتجات, ملاحظات, المجموع)
    send_pdf_to_telegram(path)
    messagebox.showinfo("تم", f"✅ تم حفظ الفاتورة في:\n{path}")
    رقم_جديد = int(entry_رقم_تلقائي.get()) + 1
    entry_رقم_تلقائي.delete(0, tk.END)
    entry_رقم_تلقائي.insert(0, str(رقم_جديد))
    save_invoice_number(رقم_جديد)


# شاشة تحميل
def show_loading_screen():
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.configure(bg="white")

    width, height = 400, 300
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")

    img = Image.open("dnc_logo.png")
    img = img.resize((200, 200))
    logo = ImageTk.PhotoImage(img)
    label_img = tk.Label(splash, image=logo, bg="white")
    label_img.image = logo
    label_img.pack(pady=20)

    label_text = tk.Label(splash, text="جارٍ التحميل...", font=("Arial", 16), bg="white")
    label_text.pack()

    win.withdraw()
    win.after(2000, lambda: [splash.destroy(), win.deiconify()])


win = tk.Tk()




win.title("دار الناشر - برنامج الفواتير")
win.state('zoomed')
win.configure(bg="#f2f2f2")
font = ("Arial", 14)

main_frame = Frame(win, bg="#f2f2f2")
main_frame.pack(fill="both", expand=True)

canvas = Canvas(main_frame, bg="#f2f2f2")
scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#f2f2f2")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

from PIL import Image, ImageTk

# تحميل الشعار
logo_img = Image.open("dnc_logo.png")
logo_img = logo_img.resize((120, 120))
logo_tk = ImageTk.PhotoImage(logo_img)

logo_label = tk.Label(scrollable_frame, image=logo_tk, bg="#f2f2f2")
logo_label.image = logo_tk
logo_label.pack(pady=10)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=win.winfo_screenwidth())
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def make_labeled_entry(text):
    frame = Frame(scrollable_frame, bg="white")
    frame.pack(fill="x", padx=80, pady=5)
    lbl = tk.Label(frame, text=text, font=font, bg="#F4F6F8", fg="#2C3E50")
    lbl.pack(anchor="w")
    ent = tk.Entry(frame, font=font, bg="#E8F0F7", fg="#2C3E50", insertbackground="#7A2048")
    ent.pack(fill="x")
    return ent

entry_رقم_يدوي = make_labeled_entry("رقم فاتورة البيع")
entry_رقم_تلقائي = make_labeled_entry("رقم الفاتورة (تلقائي)")
entry_رقم_تلقائي.insert(0, str(load_invoice_number()))
entry_زبون = make_labeled_entry("اسم الزبون")
entry_عنوان = make_labeled_entry("رقم هاتف الزبون")
entry_تاريخ = make_labeled_entry("التاريخ")
entry_تاريخ.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
entry_ملاحظات = make_labeled_entry("ملاحظات")

rows = []

def add_product_row():
    frame = Frame(scrollable_frame, bg="white")
    frame.pack(fill="x", padx=80, pady=10)
    subframe = Frame(frame, bg="white")
    subframe.pack()
    tk.Label(subframe, text="الوصف", font=font, bg="#F4F6F8", fg="#2C3E50").grid(row=0, column=0, padx=20)
    tk.Label(subframe, text="الكمية", font=font, bg="#F4F6F8", fg="#2C3E50").grid(row=0, column=1, padx=20)
    tk.Label(subframe, text="السعر", font=font, bg="#F4F6F8", fg="#2C3E50").grid(row=0, column=2, padx=20)
    وصف = tk.Entry(subframe, font=font, width=40, bg="#E8F0F7", fg="#2C3E50", insertbackground="#7A2048")
    وصف.grid(row=1, column=0, padx=20)
    كمية = tk.Entry(subframe, font=font, width=10, bg="#E8F0F7", fg="#2C3E50", insertbackground="#7A2048")
    كمية.grid(row=1, column=1, padx=20)
    سعر = tk.Entry(subframe, font=font, width=10, bg="#E8F0F7", fg="#2C3E50", insertbackground="#7A2048")
    سعر.grid(row=1, column=2, padx=20)
    rows.append((frame, وصف, كمية, سعر))
    win.after(100, lambda: canvas.yview_moveto(1.0))

for _ in range(5):
    add_product_row()

footer = Frame(win, bg="#f2f2f2")
footer.pack(fill="x", side="bottom")

entry_المجموع = tk.Entry(footer, font=font)
entry_المجموع.pack(padx=80, pady=10, fill="x")
entry_المجموع.insert(0, '0.00')

tk.Button(footer, text="➕ إضافة حقل", command=add_product_row, bg="#F39C12", fg="white", font=font).pack(pady=5)
def remove_product_row():
    if rows:
        last_row = rows.pop()
        last_row[0].destroy()

tk.Button(footer, text="➖ إزالة حقل", command=remove_product_row, bg="#E74C3C", fg="white", font=font).pack(pady=5)
tk.Button(footer, text="🧮 احسب المجموع", command=حساب_المجموع, bg="#0074B7", fg="white", font=font).pack(pady=5)
tk.Button(footer, text="💾 حفظ كـ PDF", command=حفظ, bg="#27AE60", fg="white", font=font).pack(pady=5)


def remove_product_row():
    if rows:
        last_row = rows.pop()
        last_row[0].destroy()



def send_pdf_to_telegram(file_path):
    token = "7886388376:AAGpLGtQDuXdSO0fVc3-5Wm5xrBXsSSi2lw"
    chat_id = "-4874267618"
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    رقم_تلقائي = entry_رقم_تلقائي.get()
    رقم_يدوي = entry_رقم_يدوي.get() or "—"
    الوقت = datetime.datetime.now().strftime("%Y-%m-%d ⏰ %I:%M:%S %p")  # نظام 12 ساعة

    caption = f"""
	 *تم اصدار هذه الفاتورة من قبل محمد سلمان* 
📦 *تم إنشاء فاتورة جديدة* 🧾
• الرقم التلقائي: *{رقم_تلقائي}*
• الرقم اليدوي: *{رقم_يدوي}*
• التاريخ والوقت: {الوقت}

✅ *يرجى التأكيد عند تجهيز الطلب*
    """

    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, files=files)
    return response.ok


show_loading_screen()


def عرض_الفواتير():
    import glob
    import subprocess
    نافذة = tk.Toplevel(win)
    نافذة.title("قائمة الفواتير المحفوظة")
    نافذة.geometry("600x500")
    نافذة.configure(bg="white")

    tk.Label(نافذة, text="🔍 بحث عن فاتورة:", font=font, bg="white").pack(pady=10)
    مدخل_بحث = tk.Entry(نافذة, font=font)
    مدخل_بحث.pack(fill="x", padx=20)

    الإطار = tk.Frame(نافذة, bg="white")
    الإطار.pack(fill="both", expand=True, padx=20, pady=10)

    قائمة = tk.Listbox(الإطار, font=font)
    قائمة.pack(side="left", fill="both", expand=True)
    شريط_تمرير = tk.Scrollbar(الإطار, orient="vertical", command=قائمة.yview)
    شريط_تمرير.pack(side="right", fill="y")
    قائمة.config(yscrollcommand=شريط_تمرير.set)

    def تحديث_القائمة(فلتر=""):
        قائمة.delete(0, tk.END)
        for ملف in sorted(glob.glob("فاتورة_*.pdf"), reverse=True):
            if فلتر in ملف:
                قائمة.insert(tk.END, ملف)

    تحديث_القائمة()

    def عند_البحث(event=None):
        فلتر = مدخل_بحث.get().strip()
        تحديث_القائمة(فلتر)

    مدخل_بحث.bind("<KeyRelease>", عند_البحث)

    def فتح_الفاتورة():
        اختيار = قائمة.curselection()
        if اختيار:
            اسم_الملف = قائمة.get(اختيار[0])
            try:
                os.startfile(اسم_الملف)
            except:
                subprocess.Popen(["xdg-open", اسم_الملف])  # لأنظمة لينكس/ماك

    tk.Button(نافذة, text="📂 فتح الفاتورة", command=فتح_الفاتورة, font=font, bg="#3498db", fg="white").pack(pady=10)


tk.Button(footer, text="📁 عرض الفواتير", command=عرض_الفواتير, bg="#2980B9", fg="white", font=font).pack(pady=5)

win.mainloop()