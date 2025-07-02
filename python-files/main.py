import os
import json

DATA_FILE = "data.json"

cases = []
clients = []

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def load_data():
    global cases, clients
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            cases = data.get("cases", [])
            clients = data.get("clients", [])
    else:
        cases = []
        clients = []

def save_data():
    data = {
        "cases": cases,
        "clients": clients
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def display_menu():
    clear_screen()
    print("\n--- نظام إدارة مكتب المحاماة المبسط ---")
    print("1. إدارة القضايا")
    print("2. إدارة العملاء")
    print("3. خروج")
    print("--------------------------------------")

def case_menu():
    while True:
        clear_screen()
        print("\n--- إدارة القضايا ---")
        print("1. إضافة قضية جديدة")
        print("2. عرض جميع القضايا")
        print("3. البحث عن قضية")
        print("4. تحديث تفاصيل قضية")
        print("5. حذف قضية")
        print("6. العودة للقائمة الرئيسية")
        print("----------------------")
        choice = input("أدخل اختيارك: ")

        if choice == '1':
            add_case()
        elif choice == '2':
            view_cases()
        elif choice == '3':
            search_case()
        elif choice == '4':
            update_case()
        elif choice == '5':
            delete_case()
        elif choice == '6':
            break
        else:
            print("اختيار غير صالح. يرجى المحاولة مرة أخرى.")
        input("اضغط Enter للمتابعة...")

def add_case():
    clear_screen()
    print("\n--- إضافة قضية جديدة ---")
    case_id = input("أدخل رقم القضية: ")
    case_type = input("أدخل نوع القضية: ")
    court = input("أدخل المحكمة: ")
    opponents = input("أدخل الخصوم: ")
    client_name = input("أدخل اسم الموكل: ")
    case_number = input("أدخل رقم الدعوى: ")
    
    case = {
        "id": case_id,
        "type": case_type,
        "court": court,
        "opponents": opponents,
        "client": client_name,
        "case_number": case_number,
        "sessions": []
    }
    cases.append(case)
    print("تمت إضافة القضية بنجاح.")
    save_data()

def view_cases():
    clear_screen()
    print("\n--- جميع القضايا ---")
    if not cases:
        print("لا توجد قضايا مسجلة.")
        return
    for case in cases:
        print(f"رقم القضية: {case['id']}")
        print(f"النوع: {case['type']}")
        print(f"المحكمة: {case['court']}")
        print(f"الخصوم: {case['opponents']}")
        print(f"الموكل: {case['client']}")
        print(f"رقم الدعوى: {case['case_number']}")
        if case['sessions']:
            print("  الجلسات:")
            for session in case['sessions']:
                print(f"    - التاريخ: {session['date']}, الحالة: {session['status']}, ملاحظات: {session['notes']}")
        print("----------------------")

def search_case():
    clear_screen()
    print("\n--- البحث عن قضية ---")
    search_id = input("أدخل رقم القضية للبحث: ")
    found = False
    for case in cases:
        if case['id'] == search_id:
            print(f"رقم القضية: {case['id']}")
            print(f"النوع: {case['type']}")
            print(f"المحكمة: {case['court']}")
            print(f"الخصوم: {case['opponents']}")
            print(f"الموكل: {case['client']}")
            print(f"رقم الدعوى: {case['case_number']}")
            if case['sessions']:
                print("  الجلسات:")
                for session in case['sessions']:
                    print(f"    - التاريخ: {session['date']}, الحالة: {session['status']}, ملاحظات: {session['notes']}")
            found = True
            break
    if not found:
        print("القضية غير موجودة.")

def update_case():
    clear_screen()
    print("\n--- تحديث تفاصيل قضية ---")
    case_id = input("أدخل رقم القضية لتحديثها: ")
    found = False
    for case in cases:
        if case['id'] == case_id:
            print("القضية موجودة. أدخل التفاصيل الجديدة (اترك فارغًا للاحتفاظ بالقيمة الحالية):")
            new_type = input(f"النوع ({case['type']}): ")
            if new_type: case['type'] = new_type
            new_court = input(f"المحكمة ({case['court']}): ")
            if new_court: case['court'] = new_court
            new_opponents = input(f"الخصوم ({case['opponents']}): ")
            if new_opponents: case['opponents'] = new_opponents
            new_client = input(f"الموكل ({case['client']}): ")
            if new_client: case['client'] = new_client
            new_case_number = input(f"رقم الدعوى ({case['case_number']}): ")
            if new_case_number: case['case_number'] = new_case_number
            
            add_session_choice = input("هل تريد إضافة جلسة جديدة لهذه القضية؟ (ن/ل): ").lower()
            if add_session_choice == 'ن':
                session_date = input("تاريخ الجلسة: ")
                session_status = input("حالة الجلسة: ")
                session_notes = input("ملاحظات الجلسة: ")
                case['sessions'].append({"date": session_date, "status": session_status, "notes": session_notes})

            print("تم تحديث القضية بنجاح.")
            found = True
            save_data()
            break
    if not found:
        print("القضية غير موجودة.")

def delete_case():
    clear_screen()
    print("\n--- حذف قضية ---")
    case_id = input("أدخل رقم القضية لحذفها: ")
    global cases
    initial_len = len(cases)
    cases = [case for case in cases if case['id'] != case_id]
    if len(cases) < initial_len:
        print("تم حذف القضية بنجاح.")
        save_data()
    else:
        print("القضية غير موجودة.")

def client_menu():
    while True:
        clear_screen()
        print("\n--- إدارة العملاء ---")
        print("1. إضافة عميل جديد")
        print("2. عرض جميع العملاء")
        print("3. البحث عن عميل")
        print("4. تحديث تفاصيل عميل")
        print("5. حذف عميل")
        print("6. العودة للقائمة الرئيسية")
        print("----------------------")
        choice = input("أدخل اختيارك: ")

        if choice == '1':
            add_client()
        elif choice == '2':
            view_clients()
        elif choice == '3':
            search_client()
        elif choice == '4':
            update_client()
        elif choice == '5':
            delete_client()
        elif choice == '6':
            break
        else:
            print("اختيار غير صالح. يرجى المحاولة مرة أخرى.")
        input("اضغط Enter للمتابعة...")

def add_client():
    clear_screen()
    print("\n--- إضافة عميل جديد ---")
    client_id = input("أدخل رقم العميل: ")
    name = input("أدخل اسم العميل: ")
    workplace = input("أدخل جهة العمل: ")
    contact_info = input("أدخل معلومات الاتصال: ")
    
    client = {
        "id": client_id,
        "name": name,
        "workplace": workplace,
        "contact_info": contact_info,
        "transactions": []
    }
    clients.append(client)
    print("تمت إضافة العميل بنجاح.")
    save_data()

def view_clients():
    clear_screen()
    print("\n--- جميع العملاء ---")
    if not clients:
        print("لا توجد عملاء مسجلون.")
        return
    for client in clients:
        print(f"رقم العميل: {client['id']}")
        print(f"الاسم: {client['name']}")
        print(f"جهة العمل: {client['workplace']}")
        print(f"معلومات الاتصال: {client['contact_info']}")
        if client['transactions']:
            print("  التعاملات:")
            for transaction in client['transactions']:
                print(f"    - الوصف: {transaction['description']}, المبلغ: {transaction['amount']}")
        print("----------------------")

def search_client():
    clear_screen()
    print("\n--- البحث عن عميل ---")
    search_id = input("أدخل رقم العميل للبحث: ")
    found = False
    for client in clients:
        if client['id'] == search_id:
            print(f"رقم العميل: {client['id']}")
            print(f"الاسم: {client['name']}")
            print(f"جهة العمل: {client['workplace']}")
            print(f"معلومات الاتصال: {client['contact_info']}")
            if client['transactions']:
                print("  التعاملات:")
                for transaction in client['transactions']:
                    print(f"    - الوصف: {transaction['description']}, المبلغ: {transaction['amount']}")
            found = True
            break
    if not found:
        print("العميل غير موجود.")

def update_client():
    clear_screen()
    print("\n--- تحديث تفاصيل عميل ---")
    client_id = input("أدخل رقم العميل لتحديثه: ")
    found = False
    for client in clients:
        if client['id'] == client_id:
            print("العميل موجود. أدخل التفاصيل الجديدة (اترك فارغًا للاحتفاظ بالقيمة الحالية):")
            new_name = input(f"الاسم ({client['name']}): ")
            if new_name: client['name'] = new_name
            new_workplace = input(f"جهة العمل ({client['workplace']}): ")
            if new_workplace: client['workplace'] = new_workplace
            new_contact_info = input(f"معلومات الاتصال ({client['contact_info']}): ")
            if new_contact_info: client['contact_info'] = new_contact_info
            
            add_transaction_choice = input("هل تريد إضافة تعامل جديد لهذا العميل؟ (ن/ل): ").lower()
            if add_transaction_choice == 'ن':
                description = input("وصف التعامل: ")
                amount = input("المبلغ: ")
                client['transactions'].append({"description": description, "amount": amount})

            print("تم تحديث العميل بنجاح.")
            found = True
            save_data()
            break
    if not found:
        print("العميل غير موجود.")

def delete_client():
    clear_screen()
    print("\n--- حذف عميل ---")
    client_id = input("أدخل رقم العميل لحذفها: ")
    global clients
    initial_len = len(clients)
    clients = [client for client in clients if client['id'] != client_id]
    if len(clients) < initial_len:
        print("تم حذف العميل بنجاح.")
        save_data()
    else:
        print("العميل غير موجود.")

# Main program loop
def main():
    load_data() # Load data at the start
    while True:
        display_menu()
        choice = input("أدخل اختيارك: ")

        if choice == '1':
            case_menu()
        elif choice == '2':
            client_menu()
        elif choice == '3':
            print("شكرًا لاستخدامك نظام إدارة مكتب المحاماة المبسط. إلى اللقاء!")
            save_data() # Save data before exiting
            break
        else:
            print("اختيار غير صالح. يرجى المحاولة مرة أخرى.")
        input("اضغط Enter للمتابعة...")

if __name__ == "__main__":
    main()


