
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, uuid
from datetime import datetime

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

STORE_NAME = "آل جامع جلابية"
CUSTOMERS_FILE = "customers.txt"
ORDERS_FILE = "orders.txt"
INVOICE_DIR = "invoices"

def customer_exists(name):
    if not os.path.isfile(CUSTOMERS_FILE):
        return False
    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
        return any(line.split(",")[0].strip() == name for line in f)

def get_customer_phone(name):
    if not os.path.isfile(CUSTOMERS_FILE):
        return ""
    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",", 1)
            if parts[0] == name:
                return parts[1] if len(parts) > 1 else ""
    return ""

def add_customer(name, phone):
    if customer_exists(name):
        print("⚠️ الزبون موجود بالفعل، لم يتم التكرار.")
        return
    with open(CUSTOMERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name},{phone}
")

def input_measurements():
    print("\nأدخل المقاسات:")
    fields = ["الكتف", "اليد", "كم اليد", "الطول", "الجمبات", "السروال", "القبة"]
    m = {field: input(f"  {field}: ").strip() for field in fields}
    return m

def input_delivery_date():
    print("\n📅 أدخل تاريخ التسليم:")
    day   = input("  اليوم: ").zfill(2)
    month = input("  الشهر: ").zfill(2)
    year  = input("  السنة: ")
    date_str = f"{year}-{month}-{day}"
    print(f"📌 التاريخ: {date_str}")
    if input("هل تريد تعديله؟ (نعم/لا): ").strip().lower() == "نعم":
        date_str = input("أدخل التاريخ الجديد (مثال: 2025-07-05): ").strip()
    return date_str

def save_order(order):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(order, ensure_ascii=False) + "\n")

def search_orders_by_name(name):
    if not os.path.isfile(ORDERS_FILE):
        print("لا توجد طلبيات محفوظة.")
        return
    found = False
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                order = json.loads(line)
                if name in order.get("اسم الزبون", ""):
                    found = True
                    print(f"\n🧾 الحالة: {order.get('حالة الطلب', 'غير محددة')}")
                    print_invoice(order, save_to_file=False)
            except json.JSONDecodeError:
                continue
    if not found:
        print("لا توجد طلبيات بالاسم المدخل.")

def search_by_status():
    print("🔍 اختر نوع الطلبيات:")
    print("1. قيد التنفيذ")
    print("2. جاهزة")
    print("3. مخلصة")
    status_map = {"1": "قيد التنفيذ", "2": "جاهزة", "3": "مخلصة"}
    status = status_map.get(input("اختيار: ").strip())
    if not status:
        print("❌ خيار غير صحيح.")
        return
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                order = json.loads(line)
                if order.get("حالة الطلب") == status:
                    print_invoice(order, save_to_file=False)
            except:
                continue

def print_invoice(order, save_to_file=True):
    table = [
        ["اسم المحل", STORE_NAME],
        ["عنوان الفاتورة", "فاتورة طلب"],
        ["اسم الزبون", order.get("اسم الزبون", "")],
        ["رقم الهاتف", order.get("رقم الهاتف", "")],
        ["نوع اللبس", order.get("نوع اللبس", "")],
        ["نوع القماش", order.get("نوع القماش", "")],
        ["تاريخ الطلب", order.get("تاريخ الطلب", "")],
    ]
    for k, v in order.get("المقاسات", {}).items():
        table.append([k, v])
    table.extend([
        ["هل في قيطان؟", "نعم" if order.get("قيطان") != "لا" else "لا"],
        ["لون القيطان", order.get("قيطان") if order.get("قيطان") != "لا" else ""],
        ["نوع التقفيل", order.get("التقفيل", "")],
        ["نوع الكفة", order.get("الكفة", "")],
        ["الجيوب الأمامية", order.get("الجيوب", "") + (" - "+order.get("غطاء الجيب","") if order.get("غطاء الجيب") else "")],
        ["نوع الزاير", order.get("نوع الزاير", "")],
        ["ملاحظات", order.get("ملاحظات", "لا توجد")]
    ])
    extras = order.get("مشتريات إضافية", [])
    if extras:
        first = True
        for ex in extras:
            name_price = f"{ex['اسم']} - {ex['سعر']} ج"
            table.append(["مشتريات إضافية" if first else "", name_price])
            first = False
    table.extend([
        ["سعر اللبس", f"{order.get('سعر اللبس',0)} ج"],
        ["سعر الإضافات", f"{order.get('إجمالي المشتريات',0)} ج"],
        ["الإجمالي", f"{order.get('المجموع الكلي',0)} ج"],
        ["المدفوع", f"{order.get('المدفوع',0)} ج"],
        ["المتبقي", f"{order.get('المتبقي',0)} ج"],
        ["تاريخ التسليم", order.get("تاريخ التسليم","")],
        ["حالة الطلب", order.get("حالة الطلب", "غير محددة")]
    ])
    if tabulate:
        invoice_txt = tabulate(table, headers=["البند", "القيمة"], tablefmt="grid")
    else:
        col1_width = max(len(row[0]) for row in table) + 2
        invoice_txt = "\n".join(f"{row[0].ljust(col1_width)}| {row[1]}" for row in table)

    print("\n" + "="*40)
    print(invoice_txt)
    print("="*40 + "\n")

    if save_to_file:
        os.makedirs(INVOICE_DIR, exist_ok=True)
        fname = f"فاتورة_{order['اسم الزبون']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        path = os.path.join(INVOICE_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(invoice_txt)
        print(f"📁 تم حفظ الفاتورة في {path}\n")

    # نسخة مبسطة
    print("🧾 نسخة مبسطة للفاتورة:")
    print(f"📌 نوع اللبس: {order.get('نوع اللبس', '')}")
    print(f"📌 نوع القماش: {order.get('نوع القماش', '')}")
    print("📏 المقاسات:")
    for k, v in order.get("المقاسات", {}).items():
        print(f"  - {k}: {v}")
    print(f"📝 الملاحظات: {order.get('ملاحظات', 'لا توجد')}")

def add_new_order():
    print("\n1) الزبون")
    print("   1. مسجل")
    print("   2. جديد")
    choice = input("اختيار (1/2): ").strip()
    if choice == "1":
        name = input("اسم الزبون: ").strip()
        if not customer_exists(name):
            print("❌ غير موجود.")
            return
    elif choice == "2":
        name = input("اسم الزبون الجديد: ").strip()
        phone = input("رقم الهاتف: ").strip()
        add_customer(name, phone)
        print("✅ تمت الإضافة.")
    else:
        print("خيار غير صحيح.")
        return

    print("\n2) نوع اللبس")
    print("   1. على الله")
    print("   2. جلابية")
    product = "على الله" if input("اختيار (1/2): ").strip() == "1" else "جلابية"

    fabric = input("نوع القماش: ").strip()
    measurements = input_measurements()
    qitan = "لا"
    if input("هل في قيطان؟ (نعم/لا): ").strip().lower() == "نعم":
        qitan = input("لون القيطان: ").strip()

    print("نوع التقفيل: 1) عمود يد  2) عمود مكنة  3) آوبر")
    closure_map = {"1":"عمود يد","2":"عمود مكنة","3":"آوبر"}
    closure = closure_map.get(input("اختيار: ").strip(),"غير محدد")

    cuff = "برمة" if input("الكفة برمة؟ (نعم=برمة/لا=قياس): ").strip().lower()=="نعم" else input("قياس الكفة بالسم: ").strip()+" سم"

    print("الجيوب: 1) جيب واحد  2) جيبين  3) بدون")
    pocket_choice = input("اختيار: ").strip()
    pocket = "بدون"
    pocket_cover = ""
    if pocket_choice == "1":
        pocket = "جيب واحد"
        pocket_cover = "بغطاء" if input("بغطاء؟ (نعم/لا): ").strip().lower()=="نعم" else "بدون غطاء"
    elif pocket_choice == "2":
        pocket = "جيبين"

    button_type = input("نوع الزاير: ").strip()
    notes = input("ملاحظات (أتركه فارغ إذا لا توجد): ").strip()

    extras = []
    extra_total = 0.0
    if input("هل مشتريات أخرى؟ (نعم/لا): ").strip().lower()=="نعم":
        more="نعم"
        while more=="نعم":
            item = input("  اسم الصنف: ").strip()
            price = float(input("  السعر: ").strip())
            extras.append({"اسم":item,"سعر":price})
            extra_total += price
            more = input("  إضافة صنف آخر؟ (نعم/لا): ").strip().lower()

    product_price = float(input("سعر اللبس: ").strip())
    total = product_price + extra_total
    print(f"الإجمالي: {total} ج")
    paid = float(input("المدفوع: ").strip())
    remaining = total - paid
    print(f"المتبقي: {remaining} ج")

    delivery_date = input_delivery_date()

    print("\n🎯 اختر حالة الطلب:")
    print("  1. قيد التنفيذ")
    print("  2. جاهزة للاستلام")
    print("  3. مخلصة")
    status_map = {"1": "قيد التنفيذ", "2": "جاهزة", "3": "مخلصة"}
    order_status = status_map.get(input("اختيار (1/2/3): ").strip(), "قيد التنفيذ")

    order = {
        "اسم الزبون": name,
        "رقم الهاتف": get_customer_phone(name),
        "تاريخ الطلب": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "نوع اللبس": product,
        "نوع القماش": fabric,
        "المقاسات": measurements,
        "قيطان": qitan,
        "التقفيل": closure,
        "الكفة": cuff,
        "الجيوب": pocket,
        "غطاء الجيب": pocket_cover,
        "نوع الزاير": button_type,
        "ملاحظات": notes if notes else "لا توجد",
        "مشتريات إضافية": extras,
        "سعر اللبس": product_price,
        "إجمالي المشتريات": extra_total,
        "المجموع الكلي": total,
        "المدفوع": paid,
        "المتبقي": remaining,
        "تاريخ التسليم": delivery_date,
        "حالة الطلب": order_status
    }

    save_order(order)
    print("\n✅ تم حفظ الطلب.")
    print_invoice(order)

def main():
    while True:
        print("\n=== نظام إدارة الطلبيات ===")
        print("1) إضافة طلب")
        print("2) البحث بالاسم")
        print("3) البحث حسب الحالة")
        print("4) خروج")
        ch = input("اختيار: ").strip()
        if ch=="1":
            add_new_order()
        elif ch=="2":
            search_orders_by_name(input("اسم للبحث: ").strip())
        elif ch=="3":
            search_by_status()
        elif ch=="4":
            print("وداعاً!")
            break
        else:
            print("خيار غير صحيح.")

if __name__ == "__main__":
    main()
