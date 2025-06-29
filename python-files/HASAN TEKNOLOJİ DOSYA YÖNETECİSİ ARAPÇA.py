from tkinter import *
from tkinter import messagebox, filedialog
import os
import shutil

root = Tk()
root.geometry("1200x550+100+30")
root.title("مدير ملفات حسن للتكنولوجيا")
root.config(background="black")


def open_file():
    file = filedialog.askopenfilename()
    os.startfile(file)
    messagebox.showinfo('ملف مفتوح', file+" فتحت :D")


def delete_file():
    file = filedialog.askopenfilename()
    os.remove(file)
    messagebox.showinfo('حذف الملف', file+" تم الحذف :P")


def rename_file():
    global filename, file, f1, path
    file = filedialog.askopenfilename()
    path = os.path.abspath(file)
    f1 = Frame(root, background="grey")
    f1.grid(row=6, column=2)
    Label(f1, text="اكتب اسم الملف :3").grid(row=0, column=1, padx=10, pady=10)
    filename = Entry(f1)
    filename.grid(row=1, column=1, padx=10, pady=10)
    Button(f1, text='Rename file', command=change_name).grid(row=2, column=1, padx=10, pady=10)
    Button(f1, text='cancel', command=f1.destroy).grid(row=2, column=2)
    f1.mainloop()



def change_name():
    newName = filename.get()
    dir = os.path.dirname(path)
    renamed = os.path.join(dir,newName)
    os.rename(path, renamed)
    f1.destroy()
    messagebox.showinfo('إعادة تسمية الملف', file + " تم تغيير الاسم ^_^")


def deletefolder():
    delFolder = filedialog.askdirectory()
    os.rmdir(delFolder)
    messagebox.showinfo('confirmation', "تم حذف المجلد!")


def create_folder():
    global name_entry, dir, f
    dir = filedialog.askdirectory()
    f = Frame(root, background="white")
    f.grid(row=6,column=0)
    Label(f, text="اكتب اسم المجلد",bg='white',font="bold").grid(row=0, column=0,padx=10,pady=10)
    name_entry = Entry(f,bd=4,width=25,relief=SUNKEN)
    name_entry.grid(row=1, column=0,padx=10,pady=10)
    Button(f, text='إنشاء مجلد',font="bold",bg='dark green',fg='white', command=makeFolder).grid(row=2, column=0,padx=10,pady=10)
    Button(f, text='cancel',font="bold",bg='red2',fg='white', command=f.destroy).grid(row=2, column=1)
    f.mainloop()


def makeFolder():
    name = name_entry.get()
    os.chdir(dir)
    os.makedirs(name)
    f.destroy()
    messagebox.showinfo('إنشاء مجلد', " klasör oluşturuldu ;)")


def rename_folder():
    global dir, folder_name, f1,path
    dir = filedialog.askdirectory()
    path = os.path.abspath(dir)
    f1 = Frame(root, background="grey")
    f1.grid(row=6, column=2)
    Label(f1, text="اكتب اسم المجلد").grid(row=0, column=1, padx=10, pady=10)
    folder_name = Entry(f1)
    folder_name.grid(row=1, column=1, padx=10, pady=10)
    Button(f1, text='إعادة تسمية المجلد', command=change_folder).grid(row=2, column=1, padx=10, pady=10)
    Button(f1, text='cancel', command=f1.destroy).grid(row=2, column=2)
    f1.mainloop()


def change_folder():
    newName = folder_name.get()
    dir = os.path.dirname(path)
    renamed = os.path.join(dir,newName)
    os.rename(path, renamed)
    f1.destroy()
    messagebox.showinfo('إعادة تسمية المجلد', path + " تم تغيير اسم المجلد")


def view_folder():
    dir = filedialog.askdirectory()
    f1=Frame(root)
    f1.grid(row=5, column=2)
    listbox = Listbox(f1,width=30)
    listbox.grid(row=0,column=0)
    files = os.listdir(dir)
    for name in files:
        listbox.insert('end', name)
    exit_button = Button(f1, text='نعم', bg='dark green',fg='white',font="bold", command=f1.destroy)
    exit_button.grid(row=1, column=0)


def copy_move_file():
    global sourceText, destinationText, destination_location, f1
    f1 = Frame(root, width=350, height=300, background="lavender")
    f1.grid(row=5, column=0, columnspan=4)

    source_location = StringVar()
    destination_location = StringVar()

    link_Label = Label(f1, text="العثور على الملف الذي تريد نسخه ", font="bold", bg='lavender')
    link_Label.grid(row=0, column=0, pady=5, padx=5)

    sourceText = Entry(f1, width=50, textvariable=source_location, font="12")
    sourceText.grid(row=0, column=1, pady=5, padx=5)
    source_browseButton = Button(f1, text="bak",bg='cyan2', command=source_browse, width=15, font="bold")
    source_browseButton.grid(row=0, column=2, pady=5, padx=5)

    destinationLabel = Label(f1, text="العثور على الملف لنقله", bg="lavender", font="bold")
    destinationLabel.grid(row=1, column=0, pady=5, padx=5)

    destinationText = Entry(f1, width=50, textvariable=destination_location, font=12)
    destinationText.grid(row=1, column=1, pady=5, padx=5)
    dest_browseButton = Button(f1, text="bak", bg='cyan2', command=destination_browse, width=15, font="12")
    dest_browseButton.grid(row=1, column=2, pady=5, padx=5)

    copyButton = Button(f1, text="نسخ الملف", bg='dark green',fg='white',command=copy_file, width=15, font=('bold',12))
    copyButton.grid(row=2, column=0, pady=10, padx=10)

    moveButton = Button(f1, text="dosya taşı", bg='dark green',fg='white',command=move_file, width=15, font=('bold',12))
    moveButton.grid(row=2, column=1, pady=10, padx=10)

    cancelButton = Button(f1, text="kapat",bg='red2',fg='white', command= f1.destroy, width=15, font=('bold',12))
    cancelButton.grid(row=2, column=2, pady=10, padx=10)


def source_browse():
    global files_list
    files_list = list(filedialog.askopenfilenames())
    sourceText.insert('1', files_list)


def destination_browse():
    destinationdirectory = filedialog.askdirectory()
    destinationText.insert('1', destinationdirectory)


def copy_file():
    dest_location = destination_location.get()
    for f in files_list:
        shutil.copy(f, dest_location)
    messagebox.showinfo('نسخ الملف', 'تم نسخ الملف ^.^')
    f1.destroy()


def move_file():
    dest_location = destination_location.get()
    for f in files_list:
        shutil.move(f, dest_location)
    messagebox.showinfo('نقل ملف',"dكان الملف ممتلئا")
    f1.destroy()


lbl_heading = Label(root, text="مدير ملفات حسن للتكنولوجيا",font=("bold",18),fg="#0022ff",bg='dark blue')
lbl_heading.grid(row=1, column=1, pady=20, padx=20)

open_btn = Button(root, text="ملف مفتوح",command=open_file, width=15,font=('bold',14))
open_btn.grid(row=2, column=0,pady=20, padx=20)

delete_btn = Button(root, text="حذف الملف",command=delete_file, width=15,font=('bold',14))
delete_btn.grid(row=2, column=1,pady=20, padx=20)

rename_btn = Button(root, text="تغيير اسم الملف", command=rename_file, width=15,font=('bold',14))
rename_btn.grid(row=2, column=2,pady=20, padx=20)

copy_move_btn = Button(root, text="نسخ/نقل الملف", command=copy_move_file, width=15,font=('bold',14))
copy_move_btn.grid(row=2, column=3,pady=20, padx=20)

create_folder_btn = Button(root, text="إنشاء مجلد", command=create_folder, width=15,font=('bold',14))
create_folder_btn.grid(row=3, column=0, pady=20, padx=20)

deletefolder_btn = Button(root, text="حذف المجلد", command=deletefolder, width=15,font=('bold',14))
deletefolder_btn.grid(row=3, column=1, pady=20, padx=20)

rename_folder_btn = Button(root, text="حذف المجلد", command=rename_folder, width=15,font=('bold',14))
rename_folder_btn.grid(row=3, column=2,pady=20, padx=20)

view_btn = Button(root, text="انظر إلى الملف", command=view_folder, width=15,font=('bold',14))
view_btn.grid(row=3, column=3, pady=20, padx=20)

exit_btn = Button(root, text="اخرج", command=root.destroy, width=12,font=('bold',14))
exit_btn.grid(row=4, column=1, pady=20, padx=20)

root.mainloop()
