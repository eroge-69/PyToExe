import pymysql
import os
import getpass

# بيانات الاتصال بقاعدة البيانات
connection = pymysql.connect(
    host='sql12.freesqldatabase.com',
    user='sql12785364',
    password='2V27lVa27P',
    database='sql12785364',
    port=3306
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT Active FROM Activation WHERE Id = 1")
        result = cursor.fetchone()

        if result and result[0] == 1:
            username = getpass.getuser()
            folder_path = f"C:\\Users\\{username}\\Desktop\\TestFolder"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print("✅ تم إنشاء المجلد.")
            else:
                print("📁 المجلد موجود مسبقاً.")
        else:
            print("⛔️ قيمة Active ليست 1. لم يتم عمل شيء.")
finally:
    connection.close()