import tkinter
import os
import tkinter.messagebox

hostsPath = "C:\\Windows\\System32\\drivers\\etc\\hosts"
linksData = "D:\\data.txt"

Wblock_Window = tkinter.Tk()

labelFile = tkinter.Label(Wblock_Window, text = "Enter domain", font = ("Arial", 10, "bold"))
labelFile.pack()

InputText = tkinter.Entry(Wblock_Window, font = ("Arial", 10, "bold"), width = 25, bd = 2)
InputText.pack()

count = 0
def Save_Event():
    val = InputText.get()

    if not val or val == None:
        tkinter.messagebox.showwarning("Error", "Please enter correct domain")
    else:
        try:
            with open(hostsPath, "a+") as HostFile:
                fullstring = "\n127.0.0.1   www.%s" % val
                HostFile.write(fullstring)
                tkinter.messagebox.showinfo("", "Domain blocked")

                InputText.delete(0, tkinter.END)

            with open(linksData, "a+") as fd:
                fd.write(str("\nwww.%s" % val))

        except IOError as err:
            if err:
                tkinter.messagebox.showwarning("OError", "File open permission denied")

def Clear():
    if not str(InputText.get()) or str(InputText.get()) == None:
        tkinter.messagebox.showwarning("", "Domain must be entered")
    else:
        InputText.delete(0, tkinter.END) 

saveBtn = tkinter.Button(Wblock_Window, text = "Save", width = 25, font = ("Arial", 10, "bold"), command = Save_Event)
saveBtn.pack()

clearBtn = tkinter.Button(Wblock_Window, text = "Clear", width = 25, font = ("Arial", 10, "bold"), command = Clear)
clearBtn.pack()

listBox = tkinter.Listbox(Wblock_Window, width = 64, height = 17)
listBox.pack()

try:
    if os.path.exists(linksData):
        with open(linksData, "r+") as fd:
            for data in range(0, 100):
                listBox.insert(data, fd.readline())
    else:
        open(linksData, "a+")
except OSError as fne:
    open(linksData, "a+")

def createF(event):
    open(linksData, "a+")

Wblock_Window.bind("<Map>", createF)

#Wblock_Window.iconbitmap("favicon.ico")
Wblock_Window.title("Wblock")
Wblock_Window.geometry("400x400")
Wblock_Window.minsize(400, 400)
Wblock_Window.maxsize(400, 400)
Wblock_Window.mainloop()