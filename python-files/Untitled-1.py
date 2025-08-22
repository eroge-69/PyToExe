from tkinter import *
from tkinter import ttk 
from tkinter import END
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.section import WD_ORIENTATION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docxtpl import DocxTemplate
import os
from docx2pdf import convert
from tkcalendar import DateEntry, Calendar
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from tkinter import messagebox
import jinja2
import sqlite3


conn = sqlite3.connect("database1.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Users ( id INTEGER PRIMARY KEY AUTOINCREMENT,nombreofident INTEGER   ,fullname TEXT ,fathername TEXT ,dateofbirth DATE ,placeofbirth TEXT ,born TEXT ,adresse TEXT ,age TEXT,alive TEXT,resident_name TEXT)")


conn.commit()





root=Tk()
root.title("تسجيل الدخول ")
root.configure(bg="white")
root.geometry("800x550+350+50")
root.resizable( False ,False )
root.iconbitmap("Ellipse-8.ico")



img_path = "youcef1.jpg"
original_image = Image.open(img_path)
image111 = ImageTk.PhotoImage(original_image)


users = {
  "a": "a",
  "عزيز": "عزيز",
  "admin": "admin123",
  "youcef": "secret"
}


def login():
  username = cal.get()
  password = cal1.get()

  if username in users and users[username] == password:
           			 
    root2()



def root2():
    root.destroy()
    root2=Tk()
    root2.title(" Home")
    root2.geometry(f"{root2.winfo_screenwidth()}x{root2.winfo_screenheight()}")
    root2.state("zoomed")
    root2.minsize(800, 600)
    root2.iconbitmap("Ellipse-8.ico")


    


    def display_Data(event):
        
        for item in tree00.get_children():
            tree00.delete(item)

        c.execute("SELECT alive, age, adresse, born, placeofbirth, dateofbirth, fathername, fullname, nombreofident,rowid FROM Users ORDER BY id")
        
        for i, row in enumerate(c.fetchall(), start=1):
        # row[1:] تستثني العمود الأول (ID) وتضيف الترتيب في النهاية
            tree00.insert("", "end", values=(row[0], row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8], i),tags=(row[9],))
        conn.commit()
        tree00.update_idletasks()
        
    root2.bind("<Map>", display_Data)

        


    def display_secndtable_data():
        selected_item = tree00.selection()
        user_id = tree00.item(selected_item[0], 'tags')[0]
        table_name = f"user_{user_id}_data"
            
        for item in tree01.get_children():
            tree01.delete(item)
        c.execute(f"SELECT  confirmed, place_of_vaccine , vaccine_date, vaccine_name   FROM {table_name} ORDER BY id")
        for i, row in enumerate(c.fetchall(), start=1):
        # row[1:] تستثني العمود الأول (ID) وتضيف الترتيب في النهاية
            tree01.insert("", "end", values=row[0:] + (i,))
        conn.commit()
        




    def update_label(clear=False):
                selected_items = tree00.selection()
                if clear or not selected_items:
                    labeltextVar.config(text="")  # تفريغ النص
                    return
                if selected_items:
                    fullname = tree00.item(selected_items[0], 'values')[7]
                    labeltextVar.config(text=fullname)



        

    def show_data_in_Edit():
                        # الحصول على العنصر المحدد
            selected_item = tree00.selection()
            if not selected_item:
                return
            item_row= tree00.item(selected_item[0],"values")
            selected_rowid = tree00.item(selected_item[0], 'tags')[0]

            c.execute("SELECT resident_name FROM Users WHERE id=?",(selected_rowid,))
            result = c.fetchone()
            

            resident_name =  result[0] if result else ""          
            
            item_data = (
                item_row[0],  # nombreofident
                result[0] if result else "" ,  # resident_name
                item_row[2],  # fathername
                item_row[3],  # dateofbirth
                item_row[4],  # placeofbirth
                item_row[5],  # born
                item_row[6],  # adresse
                item_row[7],  # age
                item_row[8],  # age
        )
            entries = (entry_edit019, entry_edit018, entry_edit017, entry_edit016, entry_edit015, entry_edit014,entry_edit013, entry_edit012, entry_edit011)
        
            for entry, value in zip(entries, item_data):            # ملء كل حقل بالقيمة المقابلة
                if isinstance(entry, ttk.Combobox):  # إذا كان الحقل Combobox
                    entry.set(value)  # الطريقة الصحيحة لـ Combobox
                elif hasattr(entry, 'delete') and hasattr(entry, 'insert'):  # إذا كان Entry عادي
                    entry.delete(0, END)
                    entry.insert(0, value)
                elif hasattr(entry, 'set_date'):  # إذا كان DateEntry من tkcalendar
                    entry.set_date(value)
            
    

    def show_data_in_Edit2():
            selected_item = tree01.selection()
        
            if not selected_item:
                return
            
                            # الحصول على بيانات العنصر
            item_data1 = tree01.item(selected_item[0], 'values')[1]
            item_data2 = tree01.item(selected_item[0], 'values')[2]
            item_data3 = tree01.item(selected_item[0], 'values')[3]

                

            entries = (comb_Add0111, entry_edit0121, comb_Add0121,) 
            values =(item_data1,item_data2,item_data3)
            
                            # ملء كل حقل بالقيمة المقابلة
            for entry, value in zip(entries,values):  
                if isinstance(entry, ttk.Combobox):
                    entry.set(value)  # لـ Combobox
                else:
                    entry.delete(0, END)  # لـ Entry
                    entry.insert(0, value) 
    
            
    




    def toplevel00():


        toplvl00=Toplevel(root2,)
        toplvl00.title("تعديل ")
        toplvl00.geometry("550x450+450+100")
        toplvl00.resizable(False,False)
        toplvl00.iconbitmap("Ellipse-8.ico")
        toplvl00.grab_set()

        def update_selected():
            required_fields = [
                (entry_edit011, "رقم الهوية"),
                (entry_edit012, "الاسم الكامل"),
                (entry_edit013, "اسم الأب"),
                (entry_edit014, "تاريخ الميلاد"),
                (entry_edit015, "مكان الميلاد"),
                (entry_edit016, "مكان الولادة"),
                (entry_edit017, "العنوان"),
                (entry_edit018, "مكان الاقامة"),
                (entry_edit019, "على قيد الحياة")
            ]
            missing_fields = []
            for field, name in required_fields:
                    if isinstance(field, ttk.Combobox) or hasattr(field, 'get'):
                        value = field.get().strip() if hasattr(field, 'get') else field.get()
                        if not value:
                            missing_fields.append(name)
                    elif hasattr(field, 'get_date'):
                        if not field.get_date():
                            missing_fields.append(name)
            
            if missing_fields:
                    message = "يجب ملء الحقول التالية:\n" + "\n".join(f" - {field}" for field in missing_fields)
                    messagebox.showerror("حقول مطلوبة", message)
                    return


            selected_item = tree00.selection()
            user_id = tree00.item( selected_item[0], 'tags')[0]
            

            selected_date = entry_edit014.get_date()
            birth_date_str = selected_date.strftime("%Y-%m-%d")
            

            today = datetime.now().date()
            age_years = today.year - selected_date.year
            age_months = today.month - selected_date.month
            broken_age = f"{age_years}سنوات{0}أشهر"  

            if age_months < 0 or (age_months == 0 and today.day < selected_date.day):
                age_years -= 1
                age_months += 12

            broken_age = f"{age_years}سنوات{age_months}أشهر"

            new_values = (
                    entry_edit019.get(),  # alive
                    broken_age,           # age
                    entry_edit018.get(),  # resident
                    entry_edit017.get(),  # adresse
                    entry_edit016.get(),  # born
                    entry_edit015.get(),  # placeofbirth
                    birth_date_str,  # dateofbirth
                    entry_edit013.get(),  # fathername
                    entry_edit012.get(),  # fullname
                    entry_edit011.get(),  # nombreofident
            )

            c.execute("UPDATE Users SET alive=?, age=?, resident_name=?, adresse=?, born=?, placeofbirth=?, dateofbirth=?, fathername=?, fullname=?, nombreofident=?  WHERE id=?", (*new_values, user_id))
            conn.commit()

            toplvl00.destroy()
            display_Data(Event)




        # اطار نص
        lbl_toplvl00=Label(toplvl00,text="التعديل في معلومات المولود")
        lbl_toplvl00.pack(pady=5)
        
        # اطار المداخل والنصوص

        global entry_edit019, entry_edit018, entry_edit017, entry_edit016, entry_edit015, entry_edit014,entry_edit013, entry_edit012, entry_edit011
        
        entry_edit011=Entry(toplvl00,justify="right",width=28)
        entry_edit011.place(x=200,y=50)
        lbl_entry_edit011=Label(toplvl00,text=": رقم شهادة الميلاد ")
        lbl_entry_edit011.place(x=420,y=50)

        entry_edit012=Entry(toplvl00,justify="right",width=28)
        entry_edit012.place(x=200,y=80)
        lbl_entry_edit012=Label(toplvl00,text=": الإسم واللقب")
        lbl_entry_edit012.place(x=420,y=80)
        
        
        entry_edit013=Entry(toplvl00,justify="right",width=28)
        entry_edit013.place(x=200,y=110)
        lbl_entry_edit013=Label(toplvl00,text=": إسم الاب")
        lbl_entry_edit013.place(x=420,y=110)

        
        entry_edit014=DateEntry(toplvl00,selectmode='day',date_pattern="yyyy-MM-dd")
        entry_edit014.place(x=240,y=140)
        lbl_entry_edit014=Label(toplvl00,text=": تاريخ الميلاد")
        lbl_entry_edit014.place(x=420,y=140)

        
        entry_edit015=ttk.Combobox(toplvl00,width=25,justify="right",values=("الإدريسية","البيرين","الجلفة","دار الشيوخ","حاسي بحبح","حد صحاري","الشارف","سيدي لعجال","عين الابل","عين وسارة","فيض البطمة","مسعد"),cursor="hand2",state="readonly")
        entry_edit015.place(x=200,y=170)
        lbl_entry_edit015=Label(toplvl00,text=": مكان الميلاد")
        lbl_entry_edit015.place(x=420,y=170)

        
        entry_edit016=ttk.Combobox(toplvl00,width=25,justify="right",values=("المستشفى","البيت "),cursor="hand2",state="readonly")
        entry_edit016.place(x=200,y=200)
        lbl_entry_edit016=Label(toplvl00,text=": الولادة")
        lbl_entry_edit016.place(x=420,y=200)

        
        entry_edit017=Entry(toplvl00,justify="right",width=28)
        entry_edit017.place(x=200,y=230)
        lbl_entry_edit017=Label(toplvl00,text=": العنوان")
        lbl_entry_edit017.place(x=420,y=230)

        
        entry_edit018=Entry(toplvl00,justify="right",width=28)
        entry_edit018.place(x=200,y=260)
        lbl_entry_edit018=Label(toplvl00,text=" : مكان الإقامة")
        lbl_entry_edit018.place(x=420,y=260)

        
        entry_edit019=Entry(toplvl00,justify="right",width=28)
        entry_edit019.place(x=200,y=290)
        lbl_entry_edit019=Label(toplvl00,text=" : على قيد الحياة ")
        lbl_entry_edit019.place(x=420,y=290)


        # اطار زرين حفظ و الغاء
        
        btn_save00=Button(toplvl00,text="حفظ",width=20,cursor="hand2",bg="#4CAF50",fg="#FFFFFF",command= update_selected)
        btn_save00.place(x=320,y=380)
        btn_anuller00=Button(toplvl00,text="إلغاء",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl00.destroy)
        btn_anuller00.place(x=80,y=380)


    def toplevel01():
        toplvl01=Toplevel(root2,)
        toplvl01.title("حذف ")
        toplvl01.geometry("450x200+450+100")
        toplvl01.resizable(False,False)
        toplvl01.iconbitmap("Ellipse-8.ico")
        toplvl01.grab_set()

        def delete_selected():
            selected_items = tree00.selection()
            selected_values= selected_items[0]
            user_id = tree00.item( selected_values, 'tags')[0]
            table_name = f"user_{user_id}_data"
    
                    
            c.execute(f"DROP TABLE IF EXISTS {table_name}")
            c.execute("DELETE FROM Users WHERE id=?", (user_id,))
                
            conn.commit()
                            
            # حذف العنصر من Treeview
            tree00.delete(selected_items) 

            update_label(clear=True)

            for item in tree01.get_children():
                tree01.delete(item) 
           
            
            toplvl01.destroy()
            display_Data(Event)
            





             
        lbl_toplevel01=Label(toplvl01,text=" هل تريد حذف المولود ؟")
        lbl_toplevel01.place(x=160,y=50)

        btn_save01=Button(toplvl01,text="نعم",width=20,cursor="hand2",bg="#4CAF50",fg="#FFFFFF",command=delete_selected)
        btn_save01.place(x=255,y=130)
        btn_anuller01=Button(toplvl01,text="لا",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl01.destroy)
        btn_anuller01.place(x=40,y=130)
        

    def toplevel02():
        toplvl02=Toplevel(root2,)
        toplvl02.title("إضافة")
        toplvl02.geometry("550x450+450+100")
        toplvl02.resizable(False,False)
        toplvl02.iconbitmap("Ellipse-8.ico")
        toplvl02.grab_set()

        def add_born():  
            required_fields = [
            (entry_edit21, "رقم الهوية"),
            (entry_edit22, "الاسم الكامل"),
            (entry_edit23, "اسم الأب"),
            (entry_edit24, "تاريخ الميلاد"),
            (entry_edit25, "مكان الميلاد"),
            (entry_edit26, "مكان الولادة"),
            (entry_edit27, "العنوان"),
            (entry_edit28, "مكان الاقامة"),
            (entry_edit29, "على قيد الحياة")
        ]
            missing_fields = []
            for field, name in required_fields:
                if isinstance(field, ttk.Combobox) or hasattr(field, 'get'):
                    value = field.get().strip() if hasattr(field, 'get') else field.get()
                    if not value:
                        missing_fields.append(name)
                elif hasattr(field, 'get_date'):
                    if not field.get_date():
                        missing_fields.append(name)
        
            if missing_fields:
                message = "يجب ملء الحقول التالية:\n" + "\n".join(f" - {field}" for field in missing_fields)
                messagebox.showerror("حقول مطلوبة", message)
                return



            selected_date = entry_edit24.get_date()
            birth_date_str = selected_date.strftime("%Y-%m-%d")

            today = datetime.now().date()
            age_years = today.year - selected_date.year
            age_months = today.month - selected_date.month
            broken_age = f"{age_years}سنوات{0}أشهر"  

            if age_months < 0 or (age_months == 0 and today.day < selected_date.day):
                age_years -= 1
                age_months += 12

            broken_age = f"{age_years}سنوات{age_months}أشهر"

		    
            nombreofident = int(entry_edit21.get())
            c.execute("INSERT INTO Users ( nombreofident, fullname, fathername, dateofbirth, placeofbirth, born, adresse, age, resident_name, alive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (entry_edit21.get(), entry_edit22.get().strip(), entry_edit23.get().strip(), birth_date_str, entry_edit25.get().strip(), entry_edit26.get().strip(), entry_edit27.get().strip(), broken_age, entry_edit28.get().strip(),entry_edit29.get().strip()))
            user_id = c.lastrowid
        
            entry_edit21.delete(0, END)
            entry_edit22.delete(0, END)
            entry_edit23.delete(0, END)
            entry_edit24.set_date(None)
            entry_edit25.set('')
            entry_edit26.set('')
            entry_edit27.delete(0, END)
            entry_edit28.delete(0, END)
            entry_edit29.delete(0, END)
            
        
            table_name = f"user_{user_id}_data"
            c.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, vaccine_name TEXT, vaccine_date INTEGER, place_of_vaccine TEXT, confirmed TEXT)""")

            display_Data(Event)
            conn.commit()
            
            
            
        

        # اطار نص
        lbl_toplvl01=Label(toplvl02,text="إضافة مولود")
        lbl_toplvl01.pack(pady=5)
            
        # اطار المداخل والنصوص
            
        entry_edit21=Entry(toplvl02,justify="right",width=28)
        entry_edit21.place(x=100,y=50)
        lbl_entry_edit21=Label(toplvl02,text=": رقم شهادة الميلاد")
        lbl_entry_edit21.place(x=350,y=50)

        entry_edit22=Entry(toplvl02,justify="right",width=28)
        entry_edit22.place(x=100,y=80)
        lbl_entry_edit22=Label(toplvl02,text=":الإسم واللقب ")
        lbl_entry_edit22.place(x=350,y=80)
            
            
        entry_edit23=Entry(toplvl02,justify="right",width=28)
        entry_edit23.place(x=100,y=110)
        lbl_entry_edit23=Label(toplvl02,text=":إسم الاب ")
        lbl_entry_edit23.place(x=350,y=110)

            
        entry_edit24=DateEntry(toplvl02,selectmode='day',date_pattern="yyyy-MM-dd",locale='ar_SA')
        entry_edit24.place(x=140,y=140)
        lbl_entry_edit24=Label(toplvl02,text=": تاريخ الميلاد")
        lbl_entry_edit24.place(x=350,y=140)

            
        entry_edit25=ttk.Combobox(toplvl02,width=25,justify="right",values=("الإدريسية","البيرين","الجلفة","دار الشيوخ","حاسي بحبح","حد صحاري","الشارف","سيدي لعجال","عين الابل","عين وسارة","فيض البطمة","مسعد"),cursor="hand2",state="readonly")
        entry_edit25.place(x=100,y=170)
        lbl_entry_edit25=Label(toplvl02,text=": مكان الميلاد")
        lbl_entry_edit25.place(x=350,y=170)

            
        entry_edit26=ttk.Combobox(toplvl02,width=25,justify="right",values=("المستشفى","البيت "),cursor="hand2",state="readonly")
        entry_edit26.place(x=100,y=200)
        lbl_entry_edit26=Label(toplvl02,text=": الولادة")
        lbl_entry_edit26.place(x=350,y=200)

            
        entry_edit27=Entry(toplvl02,justify="right",width=28)
        entry_edit27.place(x=100,y=230)
        lbl_entry_edit27=Label(toplvl02,text=": العنوان")
        lbl_entry_edit27.place(x=350,y=230)

            
        entry_edit28=Entry(toplvl02,justify="right",width=28)
        entry_edit28.place(x=100,y=260)
        lbl_entry_edit28=Label(toplvl02,text=" :مكان الإقامة  ")
        lbl_entry_edit28.place(x=350,y=260)

            
        entry_edit29=Entry(toplvl02,justify="right",width=28)
        entry_edit29.place(x=100,y=290)
        lbl_entry_edit29=Label(toplvl02,text=" :على قيد الحياة  ")
        lbl_entry_edit29.place(x=350,y=290)


        # اطار زرين حفظ و الغاء
            
        btn_save02=Button(toplvl02,text="حفظ",width=20,bg="#4CAF50",fg="#FFFFFF",cursor="hand2",command=add_born)
        btn_save02.place(x=320,y=380)
        btn_anuller02=Button(toplvl02,text="إلغاء",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl02.destroy)
        btn_anuller02.place(x=80,y=380)





    def toplevel10():
        toplvl10=Toplevel(root2,)
        toplvl10.title("التعديل ")
        toplvl10.geometry("550x450+450+100")
        toplvl10.resizable(False,False)
        toplvl10.iconbitmap("Ellipse-8.ico")
        toplvl10.grab_set()

        global comb_Add0121,comb_Add0111,entry_edit0121

        def Edit_vaccine():
            

            selected_item = tree00.selection()
            user_id = tree00.item(selected_item[0], 'tags')[0]
            table_name = f"user_{user_id}_data"

            selected_row = tree01.selection()
            if selected_row:
                item_id = tree01.item(selected_row[0], "values")[4]
                new_values =("تمت",comb_Add0111.get(),entry_edit0121.get_date(),comb_Add0121.get())
                c.execute(f"UPDATE {table_name} SET confirmed=?, place_of_vaccine=?, vaccine_date=?, vaccine_name=? WHERE id=?", (*new_values, item_id))
                conn.commit()

            tree01.item(selected_row[0], values=new_values)
            toplvl10.destroy()
            display_secndtable_data()



            


        lbl_toplvl121=Label(toplvl10,text="تعديل التطعيم")
        lbl_toplvl121.pack(pady=5)

        comb_Add0121=ttk.Combobox(toplvl10,width=30,values=("BCG","VPO","HBV","HEXA","PCV","ROR","Dtca-VPi","dt-adulte"),state="readonly")
        comb_Add0121.place(x=200,y=50)
        lbl_entry_Add0121=Label(toplvl10,text=":  نوع الحقنة ")
        lbl_entry_Add0121.place(x=420,y=50)

        entry_edit0121=DateEntry(toplvl10,selectmode='day',date_pattern="yyyy-MM-dd",locale='ar_SA')
        entry_edit0121.place(x=250,y=110)
        lbl_entry_edit0121=Label(toplvl10,text=":  تاريخ الحقن")
        lbl_entry_edit0121.place(x=420,y=110)
            
            
        comb_Add0111=ttk.Combobox(toplvl10,width=30,values=("قاعة العلاج حي العطري ","قاعة العلاج حي بوعافية","قاعة العلاج  حي  540","قاعة العلاج حي القندوز بن حنة","قاعة العلاج المناضلين","قاعة العلاج الحي الاداري","العيادة متعددة الخدمات حي رحال","العيادة متعددة الخدمات  حي 75 مسكن"),state="readonly")
        comb_Add0111.place(x=200,y=170)
        lbl_entry_Add0111=Label(toplvl10,text=":  مكان الحقن ")
        lbl_entry_Add0111.place(x=420,y=170)

            
        
        btn_save011=Button(toplvl10,text="حفظ",width=20,cursor="hand2",bg="#4CAF50",fg="#FFFFFF",command= Edit_vaccine)
        btn_save011.place(x=320,y=380)
        btn_anuller011=Button(toplvl10,text="إلغاء",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl10.destroy)
        btn_anuller011.place(x=80,y=380)


    def toplevel11():
        toplvl11=Toplevel(root2,)
        toplvl11.title("حذف ")
        toplvl11.geometry("450x200+450+100")
        toplvl11.resizable(False,False)
        toplvl11.iconbitmap("Ellipse-8.ico")
        toplvl11.grab_set()

        def delete_vaccine(): 
            selected_item = tree00.selection()
            user_id = tree00.item(selected_item[0], 'tags')[0]
            table_name = f"user_{user_id}_data"

            selected_row = tree01.focus()
            if selected_row:
                selected_values = tree01.item(selected_row)['values']
                if selected_values:
                    c.execute(f"DELETE FROM {table_name} WHERE id=?", (selected_values[4],))
                    conn.commit()
            tree01.delete(selected_row)
            toplvl11.destroy()
            display_secndtable_data()




        lbl_toplevel11=Label(toplvl11,text=" هل تريد حذف التطعيمة ؟")
        lbl_toplevel11.place(x=160,y=50)

        btn_save11=Button(toplvl11,text="نعم",width=20,cursor="hand2",bg="#4CAF50",fg="#FFFFFF",command=delete_vaccine)
        btn_save11.place(x=255,y=130)
        btn_anuller11=Button(toplvl11,text="لا",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl11.destroy)
        btn_anuller11.place(x=40,y=130)


    def toplevel12():
        toplvl12=Toplevel(root2,)
        toplvl12.title("إضافة")
        toplvl12.geometry("550x450+450+100")
        toplvl12.resizable(False,False)
        toplvl12.iconbitmap("Ellipse-8.ico")
        toplvl12.grab_set()

        def add_vaccine():
            required_fields = [
                (comb_Add011, "مكان إجراء الحقن"),
                (entry_edit012, "تاريخ الحقن"),
                (comb_Add012, "إسم الحقنة"),
            ]
            missing_fields = []
            for field, name in required_fields:
                if isinstance(field, ttk.Combobox) or hasattr(field, 'get'):
                    value = field.get().strip() if hasattr(field, 'get') else field.get()
                    if not value:
                        missing_fields.append(name)
                elif hasattr(field, 'get_date'):
                    if not field.get_date():
                        missing_fields.append(name)
        
            if missing_fields:
                message = "يجب ملء الحقول التالية:\n" + "\n".join(f" - {field}" for field in missing_fields)
                messagebox.showerror("حقول مطلوبة", message)
                return


            selected_item = tree00.selection()
            user_id = tree00.item(selected_item[0], 'tags')[0]
            table_name = f"user_{user_id}_data"
                
            c.execute(f"INSERT INTO {table_name} (  vaccine_name, vaccine_date, place_of_vaccine, confirmed) VALUES (?, ?, ?, ?)",
            (comb_Add012.get(),entry_edit012.get_date(),comb_Add011.get(),"تمت"))

            tree01.insert("", "end",  values=("تمت", comb_Add011.get(), entry_edit012.get_date(),comb_Add012.get()))
            conn.commit()
            toplvl12.destroy()
            display_secndtable_data()
             





        lbl_toplvl12=Label(toplvl12,text="إضافة   التطعيم")
        lbl_toplvl12.pack(pady=5)

        comb_Add012=ttk.Combobox(toplvl12,width=30,values=("BCG","VPO","HBV","HEXA","PCV","ROR","Dtca-VPi","dt-adulte"),state="readonly")
        comb_Add012.place(x=200,y=50)
        lbl_entry_Add012=Label(toplvl12,text=":  نوع الحقنة ")
        lbl_entry_Add012.place(x=420,y=50)

        entry_edit012=DateEntry(toplvl12,selectmode='day',date_pattern="yyyy-MM-dd",locale='ar_SA')
        entry_edit012.place(x=250,y=110)
        lbl_entry_edit012=Label(toplvl12,text=":  تاريخ الحقن")
        lbl_entry_edit012.place(x=420,y=110)
            
            
        comb_Add011=ttk.Combobox(toplvl12,width=30,values=("قاعة العلاج حي العطري ","قاعة العلاج حي بوعافية","قاعة العلاج  حي  540","قاعة العلاج حي القندوز بن حنة","قاعة العلاج المناضلين","قاعة العلاج الحي الإداري","العيادة متعددة الخدمات حي رحال","العيادة متعددة الخدمات  حي 75 مسكن"),state="readonly")
        comb_Add011.place(x=200,y=170)
        lbl_entry_Add011=Label(toplvl12,text=":  مكان الحقن ")
        lbl_entry_Add011.place(x=420,y=170)

            
        
        btn_save01=Button(toplvl12,text="حفظ",width=20,cursor="hand2",bg="#4CAF50",fg="#FFFFFF",command=add_vaccine)
        btn_save01.place(x=320,y=380)
        btn_anuller01=Button(toplvl12,text="إلغاء",width=20,cursor="hand2",bg="#F44336", fg="white",command=toplvl12.destroy)
        btn_anuller01.place(x=80,y=380)
    


    






    photo10=PhotoImage(file="Union 9.png")
    
    
    
    
    
    
    
    photo11=PhotoImage(file="Union 8.png")
    photo12=PhotoImage(file="Union 10.png")
    photo13=PhotoImage(file="label.png")

    
       

    # اطار نص العريض
    lbl_ground_title=Label(root2,text=" برنامج التلقيح للمؤسسة العمومية للصحة الجوارية بحاسي بحبح ",font=("deco",18,"bold"))
    lbl_ground_title.place(relwidth=1,y=4)

    # اطار قوائم البحث 
    frame0=Frame(root2,)
    frame0.place(x=20,y=50,width=900,height=620)
    # "عنوان  "قائمة المواليد المحقونين
    lbl_littel_title01=Label(frame0,text="قائمة المواليد المحقونين",font=("deco",13,"bold"))
    lbl_littel_title01.pack(fill=X)



    
    # اطار قائمة البحث عن المولود 
    frame01=Frame(frame0,bg="orange",)
    frame01.place(y=25,height=250,width=900)
    # scroooooooooooooooooolls الممرات الافقية و الشاقولية
    scrlv=Scrollbar(frame01,orient="vertical",bd=0,)
    scrlv.pack(side=LEFT,fill=Y)
    scrlh=Scrollbar(frame01,orient="horizontal",)
    scrlh.pack(side=BOTTOM,fill=X)
    #    treeeeeeeeeeeeevieeeeeeeeeww
    tree00=ttk.Treeview(frame01,columns=("Column1","Column2","Column3","Column4","Column5","Column6","Column7","Column8","Column9","Column10"),show="headings",xscrollcommand=scrlh.set,yscrollcommand=scrlv.set)
    tree00.heading("Column1",text="على قيد الحياة")
    tree00.heading("Column2",text="العمر")
    tree00.heading("Column3",text="العنوان")
    tree00.heading("Column4",text="الولادة")
    tree00.heading("Column5",text="مكان الميلاد")
    tree00.heading("Column6",text="تاريخ الميلاد")
    tree00.heading("Column7",text="إسم الأب")
    tree00.heading("Column8",text="الإسم و اللقب")
    tree00.heading("Column9",text="رقم الشهادة")
    tree00.heading("Column10",text="الرقم ")
    

    tree00.column("Column1", width=40, anchor="center")
    tree00.column("Column2", width=50, anchor="center")
    tree00.column("Column3", width=80, anchor="center")
    tree00.column("Column4", width=60, anchor="center")
    tree00.column("Column5", width=50, anchor="center")
    tree00.column("Column6", width=45, anchor="center")
    tree00.column("Column7", width=50, anchor="center")
    tree00.column("Column8", width=80, anchor="center")
    tree00.column("Column9", width=30, anchor="center")
    tree00.column("Column10", width=30, anchor="center")
    
    

    tree00.place(x=15,width=885,height=233)

    

    

    scrlv.configure(command=tree00.yview)
    scrlh.configure(command=tree00.xview)

    # ازرار التعديل 
    res10=photo12.subsample(10,10)
    btn_add00=Button(frame0,text="تعديل مولود ",image=res10,compound="right",cursor="hand2",command=lambda : [toplevel00(),show_data_in_Edit()])
    btn_add00.place(x=270,y=274,width=120,height=30)
    res11=photo11.subsample(10,10)
    btn_remove00=Button(frame0,text="حذف مولود ",image=res11,compound="right",cursor="hand2",command=toplevel01)
    btn_remove00.place(x=390,y=274,width=120,height=30)
    res12=photo10.subsample(10,10)
    btn_edit00=Button(frame0,text="إضافة مولود ",image=res12,compound="right",cursor="hand2",command=toplevel02)
    btn_edit00.place(x=510,y=274,width=120,height=30)


    # عنوان لجدول التطعيمات 
    lbl_littel_title02=Label(frame0,text=": قائمة التطعيمات للمولود ",font=("deco",13,"bold"),)
    lbl_littel_title02.place(x=0,y=304,relwidth=1)

    labeltextVar = Label(frame0, text="",font=("deco",11,"bold"))
    labeltextVar.place(x=260,y=305)
    

    #
    frame11=Frame(frame0,bg="silver",)
    frame11.place(y=329,height=250,width=900)
    # scroooooooooooooooooolls الممرات الافقية و الشاقولية
    scrlv1=Scrollbar(frame11,orient="vertical",bd=0)
    scrlv1.pack(side=LEFT,fill=Y)
    scrlh1=Scrollbar(frame11,orient="horizontal")
    scrlh1.pack(side=BOTTOM,fill=X)
    #    treeeeeeeeeeeeevieeeeeeeeeww
    tree01=ttk.Treeview(frame11,columns=("C1","C2","C3","C4","C5"),show="headings",xscrollcommand=scrlh1.set,yscrollcommand=scrlv1.set)
    tree01.heading("C1",text="تم الحقن ",)
    tree01.heading("C2",text="قاعة العلاج ",)
    tree01.heading("C3",text="تاريخ الحقن",)
    tree01.heading("C4",text="إسم الحقنة",)
    tree01.heading("C5",text="الرقم ",)

    tree01.column("C1", width=160, anchor="center")
    tree01.column("C2", width=160, anchor="center")
    tree01.column("C3", width=160, anchor="center")
    tree01.column("C4", width=160, anchor="center")
    tree01.column("C5", width=1, anchor="center")

    tree01.place(x=15,width=885,height=232)
    scrlv1.configure(command=tree01.yview)
    scrlh1.configure(command=tree01.xview)

    # ازرار التعديل 
    res13=photo12.subsample(10,10)
    btn_add01=Button(frame0,text="تعديل تطعيم ",image=res13,cursor="hand2",compound="right",command=lambda :[toplevel10(),show_data_in_Edit2()])
    btn_add01.place(x=270,y=579,width=120,height=30)
    res14=photo11.subsample(10,10)
    btn_remove01=Button(frame0,text="حذف تطعيم ",image=res14,cursor="hand2",compound="right",command=toplevel11)
    btn_remove01.place(x=390,y=579,width=120,height=30)
    res15=photo10.subsample(10,10)
    btn_edit01=Button(frame0,text="إضافة تطعيم ",image=res15,cursor="hand2",compound="right",command=toplevel12)
    btn_edit01.place(x=510,y=579,width=120,height=30)






    def search_births():
        """بحث المواليد في قاعدة البيانات"""
        
        
        # بناء استعلام البحث
        search_text = entry_search.get().strip()  # إزالة المسافات الزائدة
        search_column = comb_search.get()

        if not search_text:
            messagebox.showwarning("تحذير", "الرجاء إدخال نص للبحث")
            return
        if not search_column:
            messagebox.showwarning("تحذير", "الرجاء اختيار عمود البحث")
            return
        
            # تحويل خيار البحث إلى اسم العمود في قاعدة البيانات
        column_map = {
                "رقم الشهادة": "nombreofident",
                "اسم و لقب المولود": "fullname",
                "عام الميلاد": "dateofbirth",
                "مكان الميلاد": "placeofbirth",
                "الحي": "adresse"
        }
        
        db_column = column_map.get(search_column)
        
        # مسح البيانات الحالية
        for item in tree00.get_children():
            tree00.delete(item)
        
        # تنفيذ الاستعلام  
        c.execute(f"SELECT alive, age, adresse, born, placeofbirth, dateofbirth, fathername, fullname, nombreofident,rowid FROM Users WHERE {db_column} LIKE ?", (f"%{search_text}%",))
        results=c.fetchall()
        if not results:
            messagebox.showinfo("تنبيه", "لا توجد نتائج مطابقة للبحث")
            return  
        else: 
            for i, row in enumerate(results, start=1):
        # row[1:] تستثني العمود الأول (ID) وتضيف الترتيب في النهاية
                tree00.insert("", "end", values=(row[0], row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8], i),tags=(row[9],))
        conn.commit()
                


        for item in tree01.get_children():
            tree01.delete(item)

            
            
        
                       
        

        #tree00.insert("", "end", values=row[0:] + (i,))

    def reset_search():
        """إعادة ضبط البحث وعرض جميع البيانات الأصلية"""
    
    # مسح البيانات الحالية في treeview
        for item in tree00.get_children():
            tree00.delete(item)
    
        for item in tree01.get_children():
            tree01.delete(item)
    
    # جلب وعرض جميع البيانات الأصلية
        c.execute("SELECT alive, age, adresse, born, placeofbirth, dateofbirth, fathername, fullname, nombreofident, rowid FROM Users")
        results = c.fetchall()
    
        if results:
            for i, row in enumerate(results, start=1):
                tree00.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], i), tags=(row[9],))
    
        conn.commit()


    # اطار البحث و الطباعة
    frame02=Frame(root2,)
    frame02.place(x=950,y=50,width=400,height=620)

        # اطار البحث لوحده
    lbl_search=Label(frame02,text="البحث",font=("arial",15),)
    lbl_search.place(relwidth=1,y=35)

    comb_search=ttk.Combobox(frame02,width=25,text="البحث حسب...",values=("اسم و لقب المولود","رقم الشهادة","عام الميلاد","مكان الميلاد","الحي "),cursor="hand2",state="readonly")
    comb_search.place(x=113,y=85)
    entry_search=Entry(frame02,width=28,justify="right")
    entry_search.place(x=113,y=135)
    btn_search=Button(frame02,text="الــبحــث",width=23,cursor="hand2",bg="#0078D7",fg="white",relief="groove",command=search_births)
    btn_search.place(x=113,y=185)
    btn_cancel_search=Button(frame02,text="إلغاء البحث/عرض البيانات",width=23,cursor="hand2",bg="#F74242",fg="white",relief="groove",command=reset_search)
    btn_cancel_search.place(x=113,y=235)
    
















    def create_word_document():

        

        selected_item = tree00.selection()
        selected_value = tree00.item(selected_item,"values")
        user_id = tree00.item(selected_item[0], 'tags')[0]

        table_name = f"user_{user_id}_data"

        c.execute(f"SELECT confirmed, vaccine_date, vaccine_name FROM {table_name} ORDER BY id")
        records = c.fetchall()


        doc = DocxTemplate("template.docx")

        vaccines = []
        for confirmed, date, name in records:
            vaccines.append({
                'confirmed': confirmed,
                'date': date,
                'name': name
            })

        date_str = selected_value[5]
        date_obj = datetime.strptime(date_str,"%Y-%m-%d")
        dateofbirth = date_obj.strftime("%d-%m-%Y")

        context = {
            "nombreofident": selected_value[8],
            "fullname": selected_value[7],
            "fathername": selected_value[6],
            "dateofbirth": dateofbirth,
            "placeofbirth": selected_value[4],
            "adresse": selected_value[2],
            "vaccines": vaccines,
            "user_id": user_id
        }
        
        doc.render(context)

        doc.save("output1.docx")

        #output_pdf = r"C:\Users\yocef\Desktop\output1.pdf"
        #convert(r"C:\Users\yocef\Desktop\output1.docx", output_pdf)
    
        if os.name == 'nt':  # ويندوز
            os.startfile("output1.docx")






        # اطار الطباعة لوحده
    
    
    def create_word_document_1():
        selected_item = tree00.selection()
        selected_value = tree00.item(selected_item,"values")
        selected_rowid = tree00.item(selected_item[0], 'tags')[0]

        c.execute(f"SELECT resident_name FROM Users WHERE id=?",(selected_rowid,))
        result=c.fetchone()
        resident_name = result[0] if result else ""

        today = datetime.now()


        doc = DocxTemplate("template1.docx")

        context = {
            "fathername": selected_value[6],
            "fullname": selected_value[7],
            "resident_name": resident_name,
            "date_now": today.strftime("%d-%m-%Y"),
               
        }

        
        doc.render(context)
        doc.save("output2.docx")
    
        if os.name == 'nt':  # ويندوز
            os.startfile("output2.docx")




    def toplevel_annexe_2():
        toplvl_annexe_2=Toplevel(root2,)
        toplvl_annexe_2.title("annexe_2")
        toplvl_annexe_2.geometry("350x250+450+100")
        toplvl_annexe_2.resizable(False,False)
        toplvl_annexe_2.iconbitmap("Ellipse-8.ico")
        toplvl_annexe_2.grab_set()

        def annexe_2():
            selected_year = entry_annexe_2.get()
            selected_month = combo_annexe_2.get()
    
            month_map = {
                'جانفي': '01', 'فيفري': '02', 'مارس': '03', 'أفريل': '04',
                'ماي': '05', 'جوان': '06', 'جويلية': '07', 'أوت': '08',
                'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
            }
    
            target_month = month_map.get(selected_month)
            report_data = []
    
            # جلب جميع الأشخاص
            c.execute("SELECT id, fullname, fathername, dateofbirth, adresse, placeofbirth, alive FROM Users")
            persons = c.fetchall()
    
            for row in persons:
                # تحقق من تاريخ الميلاد
                birth_date = row[3]  # تاريخ الميلاد في العمود الرابع
                date_time = datetime.strptime(birth_date, '%Y-%m-%d')
            # إذا تطابق السنة والشهر
            if date_time.year == int(selected_year) and date_time.month == target_month:
                user_id = row[0]
                table_name = f"user_{user_id}_data"
                
                # جلب أول 3 تواريخ تطعيم
                c.execute(f"SELECT vaccine_date FROM {table_name} ORDER BY vaccine_date LIMIT 3")
                results = c.fetchall()
                
                # تحضير بيانات الشخص
                person_data = {
                    'fullname': row[1],
                    'fathername': row[2],
                    'dateofbirth': row[3],
                    'adresse': row[4],
                    'placeofbirth': row[5],
                    'vacc01': results[0][0] if len(results) > 0 else None,
                    'vacc02': results[1][0] if len(results) > 1 else None,
                    'vacc03': results[2][0] if len(results) > 2 else None,
                    'alive': row[6]
                }
                
                report_data.append(person_data)
                
        
            # تحضير بيانات القالب
            template_data = {
                'report_date': datetime.now().strftime("%Y-%m-%d"),
                'selected_month': selected_month,
                'selected_year': selected_year,
                'persons': report_data
            }
    
                # توليد التقرير
            doc = DocxTemplate("template3.docx")
            doc.render(template_data)

            doc.save("output4.docx")
    
                # فتح التقرير
            if os.name == 'nt':  # ويندوز
                os.startfile("output4.docx")





        lbl_annexe_2_00=Label(toplvl_annexe_2,text=": شهر الميلاد")
        lbl_annexe_2_00.place(y=25,x=260)
        combo_annexe_2=ttk.Combobox(toplvl_annexe_2,values=["جانفي","فيفيري","مارس","افريل","ماي","جوان","جويلية","أوت","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],state="readonly")
        combo_annexe_2.place(y=65,x=100,width=150)

        lbl_annexe_3_01=Label(toplvl_annexe_2,text=": سنة الميلاد ")
        lbl_annexe_3_01.place(y=105,x=260)
        entry_annexe_2=Entry(toplvl_annexe_2,width=24)
        entry_annexe_2.place(y=145,x=100)

        btn_annexe_2=Button(toplvl_annexe_2,text="طباعة",width=15,command=annexe_2)
        btn_annexe_2.place(y=200,relx=0.32)



    def toplevel_annexe_3():
        toplvl_annexe_3=Toplevel(root2,)
        toplvl_annexe_3.title("annexe_3")
        toplvl_annexe_3.geometry("350x250+450+100")
        toplvl_annexe_3.resizable(False,False)
        toplvl_annexe_3.iconbitmap("Ellipse-8.ico")
        toplvl_annexe_3.grab_set()

        def annexe_3():
            
            # الحصول على المدخلات
            selected_year = entry_annexe_3_01.get().strip()
            selected_local = combo_annexe_3_00.get().strip()
            selected_month = combo_annexe_3_02.get().strip()
            
            # خرائط التحويل
            month_map = {
                'جانفي': '01', 'فيفري': '02', 'مارس': '03', 'أفريل': '04',
                'ماي': '05', 'جوان': '06', 'جويلية': '07', 'أوت': '08',
                'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
            }
            
            local_map = {
                'قاعة العلاج حي القندوز بن حنة': 'قاعة العلاج حي القندوز بن حنة',
                'قاعة العلاج حي 540': 'قاعة العلاج حي 540',
                'قاعة العلاج حي بوعافية': 'قاعة العلاج حي بوعافية',
                'قاعة العلاج حي العطري': 'قاعة العلاج حي العطري',
                'العيادة متعددة الخدمات حي رحال': 'العيادة متعددة الخدمات حي رحال',
                'قاعة العلاج الحي الاداري': 'قاعة العلاج الحي الاداري',
                'قاعة العلاج المناضلين': 'قاعة العلاج المناضلين',
                'العيادة متعددة الخدمات حي 75 مسكن': 'العيادة متعددة الخدمات حي 75 مسكن'
            }
            
            # التحقق من صحة المدخلات
            target_month = month_map.get(selected_month)
            target_local = local_map.get(selected_local)
            
            if not target_month or not target_local:
                messagebox.showerror("خطأ", "المدخلات غير صحيحة")
                return

            report_data = []
            
            # جلب جميع الأشخاص
            c.execute("SELECT id, fullname, fathername, dateofbirth, adresse, placeofbirth FROM Users")
            persons = c.fetchall()
            
            for row in persons:
                # التحقق من سنة الميلاد
                birth_date = row[3]  # تاريخ الميلاد
                if not birth_date:
                    continue
                    
                try:
                    birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                    if birth_date_obj.year != int(selected_year):
                        continue
                except ValueError:
                    continue
                    
                # جلب بيانات التطعيم
                user_id = row[0]
                table_name = f"user_{user_id}_data"
                
                c.execute(f"SELECT vaccine_date, place_of_vaccine FROM {table_name} ORDER BY vaccine_date DESC, place_of_vaccine")
                vaccinations = c.fetchall()
                
                if not vaccinations:
                    continue
                    
                matching_vaccination = None
                for vaccine_date_str, vaccine_place in vaccinations:
                        try:
                            vaccine_date = datetime.strptime(vaccine_date_str, '%Y-%m-%d')
                            if vaccine_date.month == target_month and vaccine_place == target_local:
                                matching_vaccination = (vaccine_date_str, vaccine_place)
                                break  # نأخذ أول تطابق (أحدث تطعيم يطابق الشروط)
                        except ValueError:
                            continue
                    
                if not matching_vaccination:
                    continue
                vacc_fields = {}
                for i in range(1, 10):
                    if i <= len(vaccinations):
                        vacc_fields[f'vacc{i}'] = vaccinations[i-1][0]  # تاريخ التطعيم فقط
                    else:
                        vacc_fields[f'vacc{i}'] = '/'
                    
                    # إضافة بيانات الشخص
                    person_data = {
                        'fullname': row[1],
                        'fathername': row[2],
                        'dateofbirth': row[3],
                        'placeofbirth': row[5],
                        'adresse': row[4],
                        **vacc_fields
                    }
                    report_data.append(person_data)
            
            # تحضير بيانات القالب
            template_data = {
                'report_date': datetime.now().strftime("%Y-%m-%d"),
                'selected_month': selected_month,
                'selected_local': selected_local,
                'selected_year': selected_year,
                'persons': report_data
            }
            
            if not report_data:
                messagebox.showinfo("تنبيه", "لا توجد بيانات متطابقة")
                return
            
            # توليد التقرير
            doc = DocxTemplate("template4.docx")
            doc.render(template_data)
            
            doc.save("output3.docx")
            
            if os.name == 'nt':
                os.startfile("output3.docx")




        lbl_annexe_3_00=Label(toplvl_annexe_3,text=": قاعة العلاج ")
        lbl_annexe_3_00.place(y=10,x=240)
        combo_annexe_3_00=ttk.Combobox(toplvl_annexe_3,values=("قاعة العلاج حي العطري ","قاعة العلاج حي بوعافية","قاعة العلاج  حي  540","قاعة العلاج حي القندوز بن حنة","قاعة العلاج المناضلين","قاعة العلاج الحي الإداري","العيادة متعددة الخدمات حي رحال","العيادة متعددة الخدمات  حي 75 مسكن"),state="readonly")
        combo_annexe_3_00.place(y=35,x=35,width=200)


        lbl_annexe_3_01=Label(toplvl_annexe_3,text=": سنة الميلاد")
        lbl_annexe_3_01.place(y=65,x=240)
        entry_annexe_3_01=Entry(toplvl_annexe_3,)
        entry_annexe_3_01.place(y=90,x=35)


        lbl_annexe_3_02=Label(toplvl_annexe_3,text=": شهر آخر  تطعيمة ")
        lbl_annexe_3_02.place(y=120,x=240)
        combo_annexe_3_02=ttk.Combobox(toplvl_annexe_3,values=["جانفي","فيفيري","مارس","افريل","ماي","جوان","جويلية","أوت","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],state="readonly")
        combo_annexe_3_02.place(y=145,x=35)

        btn_annexe_3=Button(toplvl_annexe_3,text="طباعة",width=15,command=annexe_3)
        btn_annexe_3.place(y=200,relx=0.32)



    def toplevel_fich_d_laison():
        toplvl_fich_d_laison=Toplevel(root2,)
        toplvl_fich_d_laison.title("fich_d_laison")
        toplvl_fich_d_laison.geometry("350x250+450+100")
        toplvl_fich_d_laison.resizable(False,False)
        toplvl_fich_d_laison.iconbitmap("Ellipse-8.ico")
        toplvl_fich_d_laison.grab_set() 

        def fich_d_laison():
    
            selected_month = combo_print_fich.get()
            month_map = {
                'جانفي': '01', 'فيفري': '02', 'مارس': '03', 'أفريل': '04',
                'ماي': '05', 'جوان': '06', 'جويلية': '07', 'أوت': '08',
                'سبتمبر': '09', 'أكتوبر': '10', 'نوفمبر': '11', 'ديسمبر': '12'
            }
            target_month = month_map.get(selected_month)
            

            c.execute("SELECT id, fullname, fathername, dateofbirth, placeofbirth, adresse FROM Users WHERE placeofbirth='حاسي بحبح'")
            persons = c.fetchall()

            report_data = []

            
            
            for row in persons:
                user_id = row[0]
                table_name = f"user_{user_id}_data"


                c.execute(f"SELECT vaccine_date FROM {table_name} ORDER BY vaccine_date DESC")
                vaccination_dates = [row[0] for row in c.fetchall()]

                if not vaccination_dates:  # إذا لم يكن هناك تطعيمات
                    continue

                last_date = vaccination_dates[0]
                try:
                    last_vaccine_date = datetime.strptime(last_date, '%Y-%m-%d')
                except ValueError:
                    continue  # إذا كان تاريخ التطعيم غير صالح

                if last_vaccine_date.month == int(target_month) :
                    vaccinations = vaccination_dates[:8]  # أول 9 تطعيمات
                    vacc_fields = {}
                    for i in range(1, 9):
                        vacc_fields[f'vacc{i}'] = vaccinations[i-1] if i <= len(vaccinations) else '/'

                    person_data = {
                        'fullname': row[1],  # استخدام row بدل persons
                        'fathername': row[2],
                        'dateofbirth': row[3],
                        'placeofbirth': row[4],
                        'adresse': row[5],
                        **vacc_fields
                    }
                    report_data.append(person_data)

            # تعريف template_data بغض النظر عن وجود بيانات
            template_data = {
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'selected_month': selected_month,
                'persons': report_data if report_data else []  # تجنب القيم الفارغة
            }

            if not report_data:
                messagebox.showinfo("تنبيه", "لا توجد بيانات متطابقة")
                return

            doc = DocxTemplate("template2.docx")
            doc.render(template_data)
            doc.save("output5.docx")
            if os.name == 'nt':
                os.startfile("output5.docx")

            



        lbl_print_fich=Label(toplvl_fich_d_laison,text=": شهر آخر  تطعيمة ")
        lbl_print_fich.place(y=60,x=240)
        combo_print_fich=ttk.Combobox(toplvl_fich_d_laison,values=["جانفي","فيفيري","مارس","افريل","ماي","جوان","جويلية","أوت","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],state="readonly")
        combo_print_fich.place(y=100,x=60)
        btn_print_fich=Button(toplvl_fich_d_laison,text="طباعة",width=15,command=fich_d_laison)
        btn_print_fich.place(y=200,relx=0.32)
        








    lbl_print=Label(frame02,text="الطباعة",font=("arial",15),)
    lbl_print.place(relwidth=1,y=330)
    frame_print=Frame(frame02,width=400,height=230)
    frame_print.place(anchor="s",relx=0.5,rely=0.97)

    res16=photo13.subsample(5,5)
    btn_print1=Button(frame_print,width=80,height=70,text="annexe2",cursor="hand2",relief="flat",image=res16,compound="top",command=toplevel_annexe_2)
    btn_print1.place(relx=0.05,rely=0.1)
    res17=photo13.subsample(5,5)
    btn_print2=Button(frame_print,width=80,height=70,text="annexe3",cursor="hand2",relief="flat",image=res17,compound="top",command=toplevel_annexe_3)
    btn_print2.place(relx=0.39,rely=0.1)
    
    res19=photo13.subsample(5,5)
    btn_print4=Button(frame_print,width=80,height=70,text="fiche.d.laison",cursor="hand2",relief="flat",image=res19,compound="top",command=toplevel_fich_d_laison)
    btn_print4.place(relx=0.73,rely=0.1)
    res20=photo13.subsample(5,5)
    btn_print5=Button(frame_print,width=80,height=70,text="شهادة تلقيح",cursor="hand2",relief="flat",image=res20,compound="top",command=create_word_document)
    btn_print5.place(relx=0.22,rely=0.6)
    res21=photo13.subsample(5,5)
    btn_print6=Button(frame_print,width=80,height=70,text="إستدعاء",cursor="hand2",relief="flat",image=res21,compound="top",command=create_word_document_1)
    btn_print6.place(relx=0.56,rely=0.6)




    # ازرار الكيبورد 
        
    tree00.bind('<<TreeviewSelect>>', lambda event: [update_label(), display_secndtable_data()])

    root2.bind('<Delete>', lambda event: toplevel01())

    

    root2.mainloop()












# اطار عريض بجانب الصورة 
bigframe = Frame(root,width=450,height=550,bg="white")
bigframe.place(x=350,y=0)

# عنوان عريض 
TXT_label = Label(bigframe,text="تسجيل الدخول",font=("arial",20,"bold"),bg="white")
TXT_label.place(relwidth=1,y=100)

# حقول الادخال
TXT_label1 = Label(bigframe,text="إسم المستخدم",font=("arial",12,"bold"),bg="white")
TXT_label1.place(x=279,y=180)
cal = Entry(bigframe,width=40,justify="right")
cal.place(x=110,y=220,height=25)
TXT_label2 = Label(bigframe,text="رقم السري",font=("arial",12,"bold"),bg="white")
TXT_label2.place(x=290,y=260)
cal1 = Entry(bigframe,width=40,justify="right",show="*")
cal1.place(x=110,y=300,height=25)
# زر الادخال
button_login = Button(bigframe,text="تسجيل الدخول",bg="#8DCAF6",fg="black",width=34,height=1,command=login)
button_login.place(x=110,y=370)


# الصورة الرئيسية 
image_label = Label(root,image=image111)
image_label.place(x=0, y=0, width=380, height=550)























       
root.bind("<<Enter>>",login())
root.mainloop()
conn.close()












root.mainloop()
