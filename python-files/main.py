import sqlite3
import tkinter as tk
from tkinter import ttk,messagebox
from datetime import datetime

con=sqlite3.connect("school_gui.db")
cur=con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS guardians(guardian_id INTEGER PRIMARY KEY AUTOINCREMENT,guardian_name TEXT,phone TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS students(student_id INTEGER PRIMARY KEY AUTOINCREMENT,first_name TEXT,last_name TEXT,age INTEGER,grade TEXT,registration_date TEXT,guardian_id INTEGER,FOREIGN KEY(guardian_id) REFERENCES guardians(guardian_id))")
con.commit()

def load():
    for i in tree.get_children():tree.delete(i)
    cur.execute("SELECT s.student_id,s.first_name||' '||s.last_name,s.age,s.grade,s.registration_date,g.guardian_name||'('||g.phone||')' FROM students s LEFT JOIN guardians g ON s.guardian_id=g.guardian_id")
    for r in cur.fetchall():tree.insert("",'end',values=r)

def form(edit=False,sid=None):
    f=tk.Toplevel(root);f.geometry("400x300")
    e1=tk.Entry(f);e2=tk.Entry(f);e3=tk.Entry(f);e4=tk.Entry(f);e5=tk.Entry(f);e6=tk.Entry(f)
    tk.Label(f,text="First name").pack();e1.pack()
    tk.Label(f,text="Last name").pack();e2.pack()
    tk.Label(f,text="Age").pack();e3.pack()
    tk.Label(f,text="Grade").pack();e4.pack()
    tk.Label(f,text="Guardian name").pack();e5.pack()
    tk.Label(f,text="Guardian phone").pack();e6.pack()

    if edit:
        cur.execute("SELECT s.first_name,s.last_name,s.age,s.grade,g.guardian_name,g.phone FROM students s LEFT JOIN guardians g ON s.guardian_id=g.guardian_id WHERE s.student_id=?",(sid,))
        d=cur.fetchone()
        if d:
            e1.insert(0,d[0]);e2.insert(0,d[1]);e3.insert(0,d[2]);e4.insert(0,d[3]);e5.insert(0,d[4]);e6.insert(0,d[5])

    def save():
        fn,ln,ag,gr,gn,gp=e1.get(),e2.get(),e3.get(),e4.get(),e5.get(),e6.get()
        if not fn or not ln:messagebox.showerror("err","missing name");return
        cur.execute("SELECT guardian_id FROM guardians WHERE guardian_name=? AND phone=?",(gn,gp))
        g=cur.fetchone()
        if g:gid=g[0]
        else:
            cur.execute("INSERT INTO guardians(guardian_name,phone)VALUES(?,?)",(gn,gp))
            gid=cur.lastrowid
        if edit:
            cur.execute("UPDATE students SET first_name=?,last_name=?,age=?,grade=?,guardian_id=? WHERE student_id=?",(fn,ln,ag,gr,gid,sid))
        else:
            cur.execute("INSERT INTO students(first_name,last_name,age,grade,registration_date,guardian_id)VALUES(?,?,?,?,?,?)",(fn,ln,ag,gr,datetime.now().strftime("%Y-%m-%d"),gid))
        con.commit();load();f.destroy()

    tk.Button(f,text="Save",command=save).pack()

def add():form()
def edit():
    s=tree.selection()
    if not s:messagebox.showwarning("warn","select row");return
    sid=tree.item(s[0])["values"][0];form(True,sid)
def delete():
    s=tree.selection()
    if not s:return
    sid=tree.item(s[0])["values"][0]
    cur.execute("DELETE FROM students WHERE student_id=?",(sid,))
    con.commit();load()

root=tk.Tk();root.geometry("800x400");root.title("School System")
cols=("id","name","age","grade","date","guardian")
tree=ttk.Treeview(root,columns=cols,show="headings")
for c in cols:tree.heading(c,text=c)
tree.pack(fill="both",expand=True)

b1=tk.Button(root,text="Add",command=add);b2=tk.Button(root,text="Edit",command=edit);b3=tk.Button(root,text="Delete",command=delete);b4=tk.Button(root,text="Reload",command=load)
for b in (b1,b2,b3,b4):b.pack(side="left",padx=5,pady=5)

load()
root.mainloop()
con.close()
