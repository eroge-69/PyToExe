import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter import filedialog
from fpdf import FPDF

def geometry(root,width,height):
    screen_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry("{}x{}+{}+{}".format(width,height,x,y))

def menu():    
    global main_menu,curr_font,header,spin,f_1,f_2,f_3,f_4,end
    main_menu = tk.Tk()
    main_menu.configure(bg='black')
    main_menu.title("main menu")
    header = tk.Label(main_menu,text="Please choose a function",font=("Arial",font_size+5),pady=10,bg='black',fg='white')
    header.grid(row=0,column=0,columnspan=2)
    spin = tk.Label(main_menu,text="Font size =",font=("Arial",font_size),bg='black',fg='white')
    spin.grid(row=0,column=1,sticky="s")
    main_menu.columnconfigure(0,weight=1)
    main_menu.columnconfigure(1,weight=1)
    main_menu.rowconfigure(0,weight=1)
    main_menu.rowconfigure((1,2),weight=2)
    geometry(main_menu,800,600)
    curr_font = tk.StringVar(value=font_size)
    spinbox = ttk.Spinbox(main_menu,from_=15,to=25,textvariable=curr_font,wrap=True,command=change_font_size,width=9,font=("Arial",15))
    spinbox.grid(row=0,column=1,sticky="se")
    f_1 = tk.Button(main_menu,text="Input Exam Detail",font=("Arial",font_size),command=lambda:input_(1),width=400, bg='gray', fg='white')
    f_1.grid(row=1,column=0,sticky="nesw")
    f_4 = tk.Button(main_menu,text="Searching",font=("Arial",font_size),command=lambda:input_(4),width=400, bg='gray', fg='white')
    f_4.grid(row=1,column=1,sticky="nesw")
    f_2 = tk.Button(main_menu,text="Import student info",font=("Arial",font_size),command=show_student_info,width=400, bg='gray', fg='white')
    f_2.grid(row=2,column=0,sticky="nesw")
    f_3 = tk.Button(main_menu,text="Generate seating plan",font=("Arial",font_size),command=lambda:input_(3),width=400, bg='gray', fg='white')
    f_3.grid(row=2,column=1,sticky="nesw")
    end = tk.Button(main_menu,text="End program",font=("Arial",font_size-5),command=exit,bg='gray',fg='white')
    end.grid(row=0,column=0,sticky="sw")
    main_menu.mainloop()
    
def change_font_size():
    global font_size
    font_size = int(curr_font.get())
    header.config(font=('Arial',font_size+5))
    spin.config(font=('Arial',font_size))
    f_1.config(font=('Arial',font_size))
    f_2.config(font=('Arial',font_size))
    f_3.config(font=('Arial',font_size))
    f_4.config(font=('Arial',font_size))
    end.config(font=('Arial',font_size-5))
    
def input_(func):
    global confirm, subject, paper, form, Class_input, time_start, time_end, date, venue, input_form,subject_2
    if exam_file == 0:
        import_file("exam")
        if exam_file == 0:
            return 0
    main_menu.destroy()
    Class_input = ["", False, False, False, False, False, "A", "B", "C", "D", "E"]
    input_form = tk.Tk()
    input_form.title("Input form"+str(func))
    input_form.configure(bg='black')
    input_form.rowconfigure((0,1,2,3,4,5,6),weight=1)
    input_form.columnconfigure((0,1),weight=1)
    geometry(input_form,1000,600)
    tk.Label(input_form, text="Subject:", font=("Arial", font_size), bg='black', fg='white').grid(row=1,column=0,padx=(50,0),sticky="w")
    subject = ttk.Combobox(input_form, state="readonly", values=subjects, font=("Arial", font_size),width=8)
    subject.grid(row=1,column=0,padx=(0,50),sticky="e")
    subject.bind("<<ComboboxSelected>>", lambda event: presence_check(func))
    tk.Label(input_form, text="Paper:", font=("Arial", font_size), bg='black', fg='white').grid(row=1,column=1,sticky="w")
    paper = ttk.Combobox(input_form, state="readonly", values=["1", "2", "3","None"], font=("Arial", font_size),width=5)
    paper.grid(row=1,column=1,padx=(120,0),sticky="w")
    paper.bind("<<ComboboxSelected>>", lambda event: presence_check(func))
    tk.Label(input_form, text="Form:", font=("Arial", font_size), bg='black', fg='white').grid(row=2,column=0,padx=(50,0),sticky="w")
    form = ttk.Combobox(input_form, state="readonly", values=["1", "2", "3", "4", "5", "6"], font=("Arial", font_size),width=2)
    form.grid(row=2,column=0,padx=(0,50),sticky="e")
    form.bind("<<ComboboxSelected>>", lambda event: presence_check(func))
    tk.Label(input_form, text="Class:", font=("Arial", font_size), bg='black', fg='white').grid(row=2,column=1,sticky="w")
    Class_input[1] = tk.BooleanVar()
    class_A = tk.Checkbutton(input_form,text="A",font=("Arial",font_size),variable=Class_input[1],command=lambda:presence_check(func),bg='black',fg='white',selectcolor='gray')
    class_A.grid(row=2,column=1,padx=(100,0),pady=0,sticky="w")
    Class_input[2] = tk.BooleanVar()
    class_B = tk.Checkbutton(input_form,text="B",font=("Arial",font_size),variable=Class_input[2],command=lambda:presence_check(func),bg='black',fg='white',selectcolor='gray')
    class_B.grid(row=2,column=1,padx=(170,0),pady=0,sticky="w")
    Class_input[3] = tk.BooleanVar()
    class_C = tk.Checkbutton(input_form,text="C",font=("Arial",font_size),variable=Class_input[3],command=lambda:presence_check(func),bg='black',fg='white',selectcolor='gray')
    class_C.grid(row=2,column=1,padx=(240,0),pady=0,sticky="w")
    Class_input[4] = tk.BooleanVar()
    class_D = tk.Checkbutton(input_form,text="D",font=("Arial",font_size),variable=Class_input[4],command=lambda:presence_check(func),bg='black',fg='white',selectcolor='gray')
    class_D.grid(row=2,column=1,padx=(310,0),pady=0,sticky="w")
    Class_input[5] = tk.BooleanVar()
    class_E = tk.Checkbutton(input_form,text="E",font=("Arial",font_size),variable=Class_input[5],command=lambda:presence_check(func),bg='black',fg='white',selectcolor='gray')
    class_E.grid(row=2,column=1,padx=(380,0),pady=0,sticky="w")
    tk.Label(input_form, text="Exam time (24-hour format):",font=("Arial",font_size),bg='black',fg='white').grid(row=3,column=0,padx=(50,0),sticky="w")
    time_start = ttk.Entry(input_form,font=("Arial",font_size),width=5)
    time_start.grid(row=3,column=1,sticky="w")
    time_start.bind("<Return>",lambda event: presence_check(func))
    tk.Label(input_form,text="~",font=("Arial", font_size),bg='black',fg='white').grid(row=3,column=1,padx=90,sticky="w")
    time_end = ttk.Entry(input_form,font=("Arial",font_size),width=5)
    time_end.grid(row=3,column=1,padx=120,sticky="w")
    time_end.bind("<Return>",lambda event: presence_check(func))
    tk.Label(input_form,text="Exam date:",font=("Arial", font_size),bg='black',fg='white').grid(row=4,column=0,padx=(50,0),sticky="w")
    date = DateEntry(input_form,date_pattern="yyyy-mm-dd",font=("Arial",font_size))
    date.delete(0, 'end')
    date.grid(row=4,column=1,sticky="w")
    date.bind("<Return>",lambda event: presence_check(func))
    tk.Label(input_form, text="Venue:",font=("Arial",font_size),bg='black',fg='white').grid(row=5,column=0,padx=(50,0),sticky="w")
    venue = ttk.Entry(input_form,font=("Arial",font_size),width=13)
    venue.grid(row=5,column=1,sticky="w")
    tk.Label(input_form, text="(Press enter)", font=("Arial", font_size), bg='black', fg='white').grid(row=5,column=1,padx=(0,50),sticky="e")
    venue.bind("<Return>", lambda event: presence_check(func))
    confirm = tk.Button(input_form, text="confirm", font=("Arial", font_size),command=lambda:validation(func),state="disabled",bg='gray',fg='white')
    confirm.grid(row=6,column=1,padx=80,sticky="w")
    tk.Button(input_form, text="back", font=("Arial", font_size),command=lambda:go_back(input_form),bg='gray',fg='white').grid(row=6,column=0,padx=80,sticky="e")
    tk.Label(input_form, text="Fields with * are mandatory", font=("Arial",15), bg='black', fg='red').grid(row=0,column=1,sticky="ne")
    if func == 4:
        tk.Label(input_form, text="Searching Form", font=("Arial", font_size+5), bg='black', fg='white').grid(row=0,column=0,columnspan=2)
        tk.Label(input_form, text="Input one or more field", font=("Arial", font_size-5), bg='black', fg='white').grid(row=0,column=0,sticky="nw")
    else:
        tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=1,column=0,padx=(30,0),sticky="w")
        tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=2,column=0,padx=(30,0),sticky="w")
        tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=2,column=0,sticky="e")
        tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=4,column=0,padx=30,sticky="w")
        if func == 1:
            tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=3,column=0,padx=30,sticky="w")
            tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=5,column=0,padx=30,sticky="w")
            tk.Label(input_form, text="*", font=("Arial", font_size), bg='black', fg='red').grid(row=1,column=0,sticky="e")
            tk.Label(input_form, text="Exam Input Form", font=("Arial", font_size+5), bg='black', fg='white').grid(row=0,column=0,columnspan=2)
        else:
            tk.Label(input_form, text="Seating Plan Input Form", font=("Arial", font_size+5), bg='black', fg='white').grid(row=0,column=0,columnspan=2)
            tk.Label(input_form, text="Subject 2:", font=("Arial", font_size-5), bg='black', fg='white').grid(row=1,column=0,rowspan=2,padx=(50,0),sticky="w")
            subject_2 = ttk.Combobox(input_form, state="readonly", values=subjects, font=("Arial", font_size-5),width=8)
            subject_2.grid(row=1,column=0,rowspan=2,padx=(0,50),sticky="e")
            subject_2.bind("<<ComboboxSelected>>", lambda event: presence_check(func)) 
        input_form.mainloop()
    
def presence_check(func):
    if func == 1:      
        if (subject.get() and form.get() and paper.get() and time_start.get() and time_end.get() and date.get() and venue.get()
       and (Class_input[1].get() or Class_input[2].get() or Class_input[3].get() or Class_input[4].get() or Class_input[5].get())):
            confirm.config(state='normal')
        else:
            confirm.config(state='disabled')
    elif func == 4:
        if (subject.get() or form.get() or paper.get() or time_start.get() or time_end.get() or date.get() or venue.get()
        or Class_input[1].get() or Class_input[2].get() or Class_input[3].get() or Class_input[4].get() or Class_input[5].get()):
            confirm.config(state='normal')
        else:
            confirm.config(state='disabled')
    else:
        if (subject.get() and form.get() and date.get()
        and (Class_input[1].get() or Class_input[2].get() or Class_input[3].get() or Class_input[4].get() or Class_input[5].get())):
            confirm.config(state='normal')
        else:
            confirm.config(state='disabled')

def go_back(x):
    x.destroy()
    menu()

def searching(func):
    global exams
    exams = []
    try:    
        f = open(exam_file,"r")
    except:
        f = open(exam_file,"x")
        showwarning(title="warning",message = "The file had just been created. Run the program again.")
        menu()    
    content = f.readlines()   
    for i in content:
        details = list(map(str,i.split()))
        exams.append(details)
    if len(exams)==0:
        showerror(message="You havn't inputted any data yet")
        input_form.destroy()
        return menu()
    i=0
    while i<len(exams):
        if len(exams[i]) > 8:
            exams[i][7] = " ".join(exams[i][7:])
            exams[i].pop(8)
        if subject.get() and subject.get()!=exams[i][0]:
            print(exams.pop(i),"s")
        elif paper.get() and paper.get()!=exams[i][1]:
            print(exams.pop(i),"p")
        elif form.get() and form.get()!=exams[i][2]:
            print(exams.pop(i),"f")
        elif Class and not(Class in exams[i][3] or exams[i][3] in Class):
            print(exams.pop(i),"c")
        elif time_start.get() and time_start.get()!=exams[i][4]:
            print(exams.pop(i),"ts")
        elif time_end.get() and time_end.get()!=exams[i][5]:
            print(exams.pop(i),"te")
        elif date.get() and exams[i][6]!=date.get():
            print(exams.pop(i),"d")
        elif venue.get() and venue.get()!=exams[i][7]:
            print(exams.pop(i),"v")
        else:
            i+=1
    if len(exams)==0:
        if func != 1:
            showerror(title="error",message="No such exam")
        return 0

def func_4():
    global result_root
    if searching(0) == 0:
        return 0   
    result_root = tk.Tk()
    result_root.configure(bg='black')
    geometry(result_root,900,500)
    header = ["subject","Paper","Form","Class","Starting Time","Ending Time","Date","Venue"]
    for i in range(8):
        label = tk.Label(result_root, text=header[i], width=14, bg="gray", fg="white", relief="solid").grid(row=0, column=i, padx=1, pady=1)
    for i in range(len(exams)):
        for j in range(len(header)):
            label = tk.Label(result_root, text=exams[i][j], width=14, bg='black', fg='white').grid(row=1+i, column=j, padx=1, pady=1)
    result_root.mainloop()

def double_check():    
    global double_check_root,Class
    double_check_root = tk.Tk()
    double_check_root.configure(bg='black')
    geometry(double_check_root,900,500)
    double_check_root.columnconfigure((0,1,2),weight=1)
    double_check_root.rowconfigure((0,1,2,3,4,5,6,7,8),weight=1)
    tk.Label(double_check_root,text="Please verify the following exam details",font=("Arial",font_size), bg='black', fg='white').grid(row=0,column=0,columnspan=3)
    tk.Label(double_check_root,text="Subject:",font=("Arial",font_size), bg='black', fg='white').grid(row=1,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=subject.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=1,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Paper",font=("Arial",font_size), bg='black', fg='white').grid(row=2,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=paper.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=2,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Form:",font=("Arial",font_size), bg='black', fg='white').grid(row=3,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=form.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=3,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Class:",font=("Arial",font_size), bg='black', fg='white').grid(row=4,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=Class,font=("Arial",font_size), bg='black', fg='white').grid(row=4,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Time:",font=("Arial",font_size), bg='black', fg='white').grid(row=5,column=1,padx=(100,0),sticky="w") 
    tk.Label(double_check_root,text=time_start.get()+"-"+time_end.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=5,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Date:",font=("Arial",font_size), bg='black', fg='white').grid(row=6,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=date.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=6,column=1,padx=(400,0),sticky="w")
    tk.Label(double_check_root,text="Venue:",font=("Arial",font_size), bg='black', fg='white').grid(row=7,column=1,padx=(100,0),sticky="w")
    tk.Label(double_check_root,text=venue.get(),font=("Arial",font_size), bg='black', fg='white').grid(row=7,column=1,padx=(400,0),sticky="w")
    tk.Button(double_check_root,text="edit",font=("Arial",font_size),command=double_check_root.destroy, bg='gray', fg='white').grid(row=8,column=1,padx=100,sticky="w")
    tk.Button(double_check_root,text="save",font=("Arial",font_size),command=store_data, bg='gray', fg='white').grid(row=8,column=1,padx=(0,200),sticky="e")
    double_check_root.mainloop()        

def validation(func):
    global Class
    if subject.get() and paper.get():
        if subject.get() in swnp and paper.get() != "None":            
            return showwarning(title="warning",message=subject.get()+" does not have paper "+paper.get())
        elif paper.get() == 3 and subject.get() != "ENG":
            return showwarning(title="warning",message="Only ENG has paper 3")
        elif paper.get() == "None" and subject.get() not in swnp:
            return showwarning(title="warning",message=subject.get()+" has separate papers")
    if time_start.get():
        if (time_start.get()<"0000" or time_start.get()>"2359" or len(time_start.get())!=4 or time_start.get()[2]>"5"):           
            return showerror(title="error",message="invalid starting time")
    if time_end.get():
        if time_end.get()<"0000" or time_end.get()>"2359" or len(time_end.get())!=4 or time_end.get()[2]>"5":           
            return showerror(title="error",message="invalid ending time")
    if time_start.get() and time_end.get():
        if time_end.get()<=time_start.get():
            return showerror(title="error",message="invalid duration")
    Class = ""
    if (Class_input[1].get() or Class_input[2].get() or Class_input[3].get() or Class_input[4].get() or Class_input[5].get()):    
        for i in range(1,6):
            if Class_input[i].get():
                Class += Class_input[i+5]
    if func == 1:
        if searching(1) != 0:
            showwarning(title="warning",message="Data already exist")
            return 0
        showinfo(title="info",message="Data validated")
        return double_check()
    elif func == 4:
        return func_4()
    return seating_plan()

def store_data():
    double_check_root.destroy()
    f = open(exam_file, "a")
    f.write(subject.get()+" ")
    f.write(paper.get()+" ")
    f.write(form.get()+" ")
    f.write(Class+" ")
    f.write(time_start.get()+" ")
    f.write(time_end.get()+" ")
    f.write(date.get()+" ")
    f.write(venue.get()+"\n")
    f.close()
    showinfo(title="info",message="data successfully stored")
    input_form.destroy()
    menu()

def import_file(file):
    global exam_file,stu_file
    root = tk.Tk()
    geometry(root,700,500)
    root.withdraw()
    path = filedialog.askopenfilename(title="Select a "+file+" file", initialdir="/", filetypes=(("All files", "*.txt"), ("All files", "*.*")))
    if path!= "":
        showinfo(title="success", message="File found")
        if file == "exam":
            exam_file = path
        else:
            stu_file = path
    else:
        showwarning(title="warning", message="No file found")
        path = 0

def read_student_info():
    global studentinfo, electives
    if stu_file == 0:    
        import_file("student")
    f = open(stu_file, "r")
    studentinfo = []
    content = f.readlines()
    for i in range(1,len(content)):
        stu = content[i]
        studentinfo.append(stu.split(","))
    electives = []
    for i in range(len(content)-1):
        if studentinfo[i][20] == "\n":
            studentinfo[i].pop(20)
        for j in range(3, len(studentinfo[i])):
            if studentinfo[i][j].strip() == "Y":
                studentinfo[i][j] = subjects[j-3]
            elif studentinfo[i][j] == "N":
                studentinfo[i][j] = "dropped"
        a = list(filter(None, studentinfo[i]))
        for i in range(4):
            a.pop(3)
        b = len(a) - 1
        if "M1" in a:
            a[a.index("M1")], a[b] = a[b], a[a.index("M1")]
        elif "M2" in a:
            a[a.index("M2")], a[b] = a[b], a[a.index("M2")]
        while len(a) < 7:
            a.append("-")
        electives.append(a)

def show_student_info():
    global show_stu_root
    if stu_file == 0:
        import_file("stu")
        if stu_file == 0:
            return 0
    read_student_info()
    show_stu_root = tk.Tk()
    geometry(show_stu_root,1005,810)
    show_stu_root.configure(bg='black')
    canvas = tk.Canvas(show_stu_root, bg='black')
    scroll = tk.Scrollbar(show_stu_root, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg='black')
    frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")   
    header = ["SID", "CLASS", "CLASSNUM", "ELECTIVE 1", "ELECTIVE 2", "ELECTIVE 3", "ELECTIVE 4"]
    for i in range(len(header)):
        label = tk.Label(frame, text=header[i], width=19, bg="gray", fg="white", relief="solid").grid(row=1, column=i, padx=1, pady=1)
    for i in range(len(electives)):
        for j in range(len(header)):
            if electives[i][j] == "dropped":
                label = tk.Label(frame, text=electives[i][j], width=19, bg="red").grid(row=2+i, column=j, padx=1, pady=1)
            else:                
                label = tk.Label(frame, text=electives[i][j], width=19, bg='black', fg='white').grid(row=2+i, column=j, padx=1, pady=1)
    tk.Button(frame,text="back",font=("Arial", font_size),command=show_stu_root.destroy,bg='gray',fg='white').grid(row=3+i,column=3)
    show_stu_root.mainloop()

def seating_plan():
    global filename
    if searching(0) == 0:
        return 0
    if len(electives) == 0:    
        read_student_info()
    eligible_stu = []
    takers = ["A",0,"B",0,"C",0,"D",0,"E",0]
    count = 0
    while 0 < len(studentinfo):
        if studentinfo[0][1][1] in Class and (subject.get() in electives[0] or subject_2.get() in electives[0]):
            studentinfo[0][2] = int(studentinfo[0][2])
            if subject.get() in electives[0]:
                studentinfo[0].append(subject.get())
                count+=1
            else:
                studentinfo[0].append(subject_2.get())
            studentinfo[0]
            studentinfo[0].append(" ")
            eligible_stu.append(studentinfo[0])
            x = takers.index(studentinfo[0][1][1])
            takers[x+1] += 1
        studentinfo.pop(0)
        electives.pop(0)
    i=1
    while i<=len(takers):
        if takers[i] == 0:
            takers.pop(i-1)
            takers.pop(i-1)
        else:
            i+=2
    if len(eligible_stu) == 0:
        showwarning(title="warning", message="no such exam")
        return 0
    elif len(eligible_stu) > 37:
        showwarning(title="warning",message="Too many exam takers")
    for i in range(1, len(eligible_stu)):
        curr = eligible_stu[i]
        j = i - 1
        while j >= 0 and (curr[20]<eligible_stu[j][20] or (curr[1] < eligible_stu[j][1] or (curr[1] == eligible_stu[j][1] and curr[2] < eligible_stu[j][2]))):
            eligible_stu[j+1] = eligible_stu[j]
            j -= 1
        eligible_stu[j + 1] = curr
    if subject_2.get():
        for i in range(count+1,len(eligible_stu)):
            curr = eligible_stu[i]
            j = i - 1
            while j >= 0 and (curr[1] < eligible_stu[j][1] or (curr[1] == eligible_stu[j][1] and curr[2] < eligible_stu[j][2])):
                eligible_stu[j+1] = eligible_stu[j]
                j -= 1
            eligible_stu[j + 1] = curr            
    order = []
    x = []
    curr = 0
    while curr < len(eligible_stu) and curr<36:
        x.append(eligible_stu[curr])
        if not(subject_2.get()) and (curr+1 < len(eligible_stu) and eligible_stu[curr][1] != eligible_stu[curr+1][1]):
            order.append(x)
            x=[]
        elif len(x) == 5:
            order.append(x)
            x=[]
        elif curr+1 == len(eligible_stu):
            order.append(x)
        curr += 1
    if len(eligible_stu)>35:
        order[5].insert(0,eligible_stu[35])
        if len(eligible_stu)>36:
            order[6].insert(0,eligible_stu[36])
    filename = "F6D21_"+form.get()+Class+subject.get()+subject_2.get()
    f = open(filename+".txt", "a")
    f.write(" "*21+"SKH Tsang Shiu Tim Secondary School\n")
    year,month,day = map(int,date.get().split("-"))
    if month<9 and month>4:
        f.write(" "*21+str(year-1)+"-"+str(year)+" Final Examination\n")
    elif month>8:
        f.write(" "*21+str(year)+"-"+str(year+1)+" Mid Term Examination\n")
    else:
        f.write(" "*21+str(year-1)+"-"+str(year)+" Mid Term Examination\n")
    f.write("\n")
    f.write("Subject: "+subject.get()+" "+subject_2.get()+"\n")
    for i in range(len(exams)):
        f.write("Paper "+str(i+1)+" Examination Time: "+exams[i][4]+"-"+exams[i][5]+"\n")
    f.write("Examination Date: "+date.get()+" "*43+"-"*8+"\n")
    f.write("Class:F"+form.get()+Class+" "*(63-len(Class))+"\ door |"+"\n")
    f.write("Number of students:")
    n=0
    for i in range(0,len(takers),2):
        f.write(" "+form.get()+str(takers[i])+":"+str(takers[i+1]))
        n+=4+len(str(takers[i+1]))
    f.write(" "*(53-n)+"\-----|"+"\n")
    f.write("Venue: "+exams[0][7]+"\n")
    if len(eligible_stu)>36:
        for i in range(5):
            if i == 0 or i == 4:
                f.write("="*10+"  "+"="*10+"\n")
            elif i == 1 or i == 3:
                f.write("|"+" "*8+"|"+"  "+"|"+" "*8+"|"+"\n")
            else:
                f.write("|"+ " "*(4-len(str(order[6][0][2]))) +order[6][0][1][1]+str(order[6][0][2]) +" "*3 +"|" +" "*2)
                f.write("|"+ " "*(4-len(str(order[5][0][2]))) +order[5][0][1][1]+str(order[5][0][2]) +" "*3 +"|"+"\n")
                order[6].pop(0)
                order[5].pop(0)
    elif len(eligible_stu)==36:
        for i in range(5):
            if i == 0 or i == 4:
                f.write(" "*12+"="*10+"\n")
            elif i == 1 or i == 3:
                f.write(" "*12+"|"+" "*8+"|"+"\n")
            else:
                f.write(" "*12+"|"+ " "*(4-len(str(order[5][0][2]))) +order[5][0][1][1]+str(order[5][0][2]) +" "*3 +"|"+"\n")
                order[5].pop(0)
    for k in range(5):    
        for i in range(5):
            if i == 0 or i == 4:
                f.write(("="*10+"  ")*(6)+"="*10+"\n")
            elif i == 1 or i == 3:
                f.write(("|"+" "*8+"|"+"  ")*6+("|"+" "*8+"|")+"\n")
            else:
                for j in range(7):
                    col = 6-j
                    if col < len(order) and k<len(order[col]):
                        space = 4-len(str(order[col][k][2]))
                        if j < 6 :
                            f.write("|"+ " "*space +order[col][k][1][1]+str(order[col][k][2]) +" "*3 +"|" +" "*2)
                        else:
                            f.write("|"+ " "*space +order[col][k][1][1]+str(order[col][k][2]) +" "*3 +"|" +"\n")
                    else:
                        f.write(("|"+" "*8+"|"+"  "))
    f.close()
    showinfo(title="success",message="text file saved")    

stu_file = 0
exam_file = 0
font_size = 20
electives = []
subjects = ["CHI","ENG","MATHS","CSD","BAFS","XBAFS","BIO","CHEM","CHIST","CLIT","ECON","ERS","GEOG","HIST","ICT","M1","M2","PHY"]
swnp = ["CSD","M1","M2"]
menu()