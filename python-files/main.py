import pandas as pd #کتابخونه برای فایل اکسل
import tkinter as tk
from tkinter import ttk, messagebox
import os
#############################################################################################
def Final_CALC(AIO, MNT, CASE, CLASS, SW):
    CASEAIO = (CASE * 180) / 225
    CASEMNT = (CASE * 180) /135     #تبدیلات CASE به MNT, AIO
    SW *= 12                # معدال سازی تعداد سوییچ به AIO
    SWMNT = (SW * 225) / 135    #تبدیل تعداد ٌُ بر حسب MNT
    CLASSAIO = (CLASS * 60 ) / 225          #تبدیل تایم آموزش به AIO
    CLASSMNT = (CLASS * 60 ) / 135          #تبدیل تایم آموزش به MNT
    def AIOCACL(): # تابع محاسبه AIO در صورت بیشتر بودن تولید AIO
        nonlocal AIO, MNT, SW, CLASSAIO, CASEAIO
        AIOMONEY = int(((AIO - 100) + SW + CLASSAIO + CASEAIO) * 20000)
        if MNT > 0:
            AIOMONEY += MNT * 12000
        return AIOMONEY
    def MNTCACL():  #تابع محاسبه تولید MNT در صورت بیشتر بودن MNT
        nonlocal AIO, MNT, SWMNT, CLASSMNT, CASEMNT
        MNTMONEY = int((MNT - 180) + SWMNT + CLASSMNT + CASEMNT) * 12000
        if AIO > 0:
            MNTMONEY += AIO * 20000
        return MNTMONEY
    def AIOdeficit_function():  #تابع تبدیل AIO به MNT در صورت کمبود AIO بیشتر بودن تولید آن نسبت به MNT
        nonlocal AIO, MNT, SW, SWMNT, CLASSAIO, CLASSMNT, CASEAIO, CASEMNT
        AIOdeficit = 100 - AIO
        MNT_required_by_AIO = (AIOdeficit * 225) / 135
        MNT -= MNT_required_by_AIO
        AIO += AIOdeficit
        return AIOCACL()
    def MNTdefivit_function():  #تابع تبدیل MNT به AIO در صورت کمبود MNT و بیشتر بودن نسبت به AIO
        nonlocal AIO, MNT, SW, SWMNT, CLASSAIO, CLASSMNT, CASEAIO, CASEMNT
        MNTdeficit = 180 - MNT
        AIO_required_by_MNT = (MNTdeficit * 135) / 225
        AIO -= AIO_required_by_MNT
        MNT += MNTdeficit
        return MNTCACL()
    if AIO >= 100 and MNT < 180:
        return AIOCACL()
    elif MNT >= 180 and AIO < 100:
        return MNTCACL()
    elif AIO < 100 and MNT < 180:
        if AIO > MNT:
            return AIOdeficit_function()
        else:
            return MNTdefivit_function()
def GUI_CALC():
    try:
        AIO = int(entry_AIO.get())
        MNT = int(entry_MNT.get())
        CASE = int(entry_CASE.get())
        SW = int(entry_SW.get())
        CLASS = int(entry_CLASS.get())
        money = Final_CALC(AIO, MNT, CASE, CLASS, SW)
        line_name = combo_line.get()
        save_to_excel(line_name, money)
        label_result.config(text=f"{money:,}")
        
    except ValueError:
        label_result.config(text="ERROR !")
###############################################################################################
def save_to_excel(line, money):
    File_name = 'Money.xlsx'
    if os.path.exists(File_name):
        df = pd.read_excel(File_name)
    else:
        df = pd.DataFrame(columns=["Date", "Line 1", "Line 2", "Line 3", "Line 4"])
    # سطر جدیدی که میخوای اضافه کنی
    new_row = {"Date": '', "Line 1": None, "Line 2": None, "Line 3": None, "Line 4": None}
    new_row[line] = money

    # جستجو برای اولین ردیف خالی در ستون خط انتخاب شده
    empty_row_indices = df[df[line].isna()].index

    if len(empty_row_indices) > 0:
        # اگر ردیف خالی وجود داشت، اولین ردیف خالی رو انتخاب کن و مقدار رو اونجا بگذار
        first_empty = empty_row_indices[0]
        df.at[first_empty, line] = money
    else:
        # اگر هیچ ردیف خالی نبود، ردیف جدید اضافه کن (پایین)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_excel(File_name, index=False)
###############################################################################################
root = tk.Tk()
root.title("CALC Money")

# لیبل و ورودی‌ها
tk.Label(root, text="AIO:").grid(row=0, column=0)
entry_AIO = tk.Entry(root)
entry_AIO.grid(row=0, column=1)

tk.Label(root, text="MNT:").grid(row=1, column=0)
entry_MNT = tk.Entry(root)
entry_MNT.grid(row=1, column=1)

tk.Label(root, text="CASE:").grid(row=2, column=0)
entry_CASE = tk.Entry(root)
entry_CASE.grid(row=2, column=1)

tk.Label(root, text="SW:").grid(row=3, column=0)
entry_SW = tk.Entry(root)
entry_SW.grid(row=3, column=1)

tk.Label(root, text="CLASS (minute):").grid(row=4, column=0)
entry_CLASS = tk.Entry(root)
entry_CLASS.grid(row=4, column=1)

# منوی کشویی انتخاب خط
tk.Label(root, text="Line:").grid(row=5, column=0)
combo_line = ttk.Combobox(root, values=["Line 1", "Line 2", "Line 3", "Line 4"])
combo_line.grid(row=5, column=1)
combo_line.current(0)

# دکمه محاسبه
btn_calc = tk.Button(root, text="CALC & Save", command=GUI_CALC)
btn_calc.grid(row=6, column=0, columnspan=2, pady=10)

# نمایش نتیجه
label_result = tk.Label(root, text="")
label_result.grid(row=7, column=0, columnspan=2)
###############################################################################################
root.mainloop()