from tkinter import*
from tkinter.messagebox import*

font=('Verdana',22)

#important functions

import zipfile

def py_to_zip(py_file, zip_file):
    # Create a new ZIP file
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        # Add the Python file to the ZIP archive
        zipf.write(py_file, arcname=py_file)


def clear():
    ex=textField.get()
    ex=ex[0:len(ex)-1]
    textField.delete(0,END)
    textField.insert(0,ex)
    

def all_clear():
    textField.delete(0,END)
    

def click_btn_function(event):
    print("btn clicked")
    b=event.widget
    text=b['text']
    print(text)

    if text=='x':
        textField.insert(END,"*")
        return

    if text=='=':
        try:
            
           ex=textField.get()
           anser=eval(ex)
           textField.delete(0,END)
           textField.insert(0, anser)
        except Exception as e:
            print("Error..",e)
            showerror("Error",e)
        return
    




    
    textField.insert(END, text)

window=Tk()
window.title('calculator')
window.geometry('500x520')
#picture
pic=PhotoImage(file='D:/Calc1.png')
headingLabel= Label(window,image=pic)
headingLabel.pack(side=TOP)



#headking label
heading=Label(window,text='My Calculator',font=font)
heading.pack(side=TOP)

#textfiled
textField=Entry(window,font=font,justify=CENTER)
textField.pack(side=TOP, pady=10,fill=X,padx=10)
#buttons

buttonFrame=Frame(window)
buttonFrame.pack(side=TOP)

#adding button
temp=1
for i in range(0,3):
    for j in range(0,3):
        btn=Button(buttonFrame,text=str(temp), font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
        btn.grid(row=i, column=j, padx=3, pady=3)
        temp=temp+1
        btn.bind('<Button-1>', click_btn_function)


        
zerobtn=Button(buttonFrame,text='0', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
zerobtn.grid(row=3, column=0, padx=3, pady=3)

dotbtn=Button(buttonFrame,text='.', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
dotbtn.grid(row=3, column=1, padx=3, pady=3)

equalbtn=Button(buttonFrame,text='=', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
equalbtn.grid(row=3, column=2, padx=3, pady=3)

plusbtn=Button(buttonFrame,text='+', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
plusbtn.grid(row=0, column=3, padx=3, pady=3)

plusbtn=Button(buttonFrame,text='+', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
plusbtn.grid(row=0, column=3, padx=3, pady=3)

minusbtn=Button(buttonFrame,text='-', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
minusbtn.grid(row=1, column=3, padx=3, pady=3)

multbtn=Button(buttonFrame,text='x', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
multbtn.grid(row=2, column=3, padx=3, pady=3)

dividebtn=Button(buttonFrame,text='/', font=font, width=6,relief='ridge',activebackground='BLACK',activeforeground='white')
dividebtn.grid(row=3, column=3, padx=3, pady=3)

clearbtn=Button(buttonFrame,text='<--', font=font, width=13,relief='ridge',activebackground='BLACK',activeforeground='white',command=clear)
clearbtn.grid(row=4, column=0, padx=3, pady=3,columnspan=2)

allclearbtn=Button(buttonFrame,text='AC', font=font, width=13,relief='ridge',activebackground='BLACK',activeforeground='white',command=all_clear)
allclearbtn.grid(row=4, column=2, padx=3, pady=3,columnspan=2)


#binding all button

plusbtn.bind('<Button-1>', click_btn_function)
minusbtn.bind('<Button-1>', click_btn_function)
multbtn.bind('<Button-1>', click_btn_function)
dividebtn.bind('<Button-1>', click_btn_function)
zerobtn.bind('<Button-1>', click_btn_function)
dotbtn.bind('<Button-1>', click_btn_function)
equalbtn.bind('<Button-1>', click_btn_function)


window.mainloop()



  
