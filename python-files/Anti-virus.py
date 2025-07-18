#Virus scan program
import glob, re, os, tkinter as tk
from tkinter import Menu
from tkinter import simpledialog, filedialog
import tkinter.messagebox
from tkinter import ttk #ttk for progress bar


def click():
    folder_path = filedialog.askdirectory(title="Chosse a folder to scan")
    if folder_path: #only allows scan when folder or directory is picked
        checkForSignatures(folder_path)

    
    #tkinter.messagebox.showinfo("Ready", f"Scan complete. Progress: {progress_bar['value']}%")

window = tkinter.Tk()
window.title=("Anti-Virus")
window.geometry("600x600")
window.resizeable=(False, False)
#button start
button = tk.Button(window, text="Start Scan", command=click, bg="green", fg="white", font=("Arial", 12), height=2, width=15)
button.place(x=200, y=100)
#button close

result_box = tk.Text(window, height=20, width=70, bg="black", fg="lime", font=("Courier", 10))
result_box.place(x=10, y=220)

window.configure(bg="black")

#text = tkinter.Text(window)
#text.pack()


#add menu
menu_bar = Menu(window)

#add a tab menu
file_menu = Menu(menu_bar, tearoff = 0)
window.config(menu=menu_bar)

#add button tab menu
file_menu.add_command(label="file")#, command=)

# scan for signatures just like any other anti-virus software

def checkForSignatures(folderpath):
    global result_box
    print("##### checking for virus signatures")
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"###### checking for virus: {folder_path}\n\n")

    # get all programs in the directory
    programs = glob.glob("*.py")
    thisProgram = os.path.basename(__file__)
    
    for p in programs:
        if p == thisProgram: # skip scanning this file
            continue
        thisFileInfected = False
        #file = open(p, "r") # open then read the file
        file = open(p, "r", encoding="utf-8", errors="ignore")
        lines = file.readlines()
        file.close()


        for line in lines:
            if(re.search("virusFile.close()",line)):
                #found a virus
                print("Virus Found!!! in file " + p)
                result_box.insert(tk.END, "Virus Found!!! in file " + p + "\n")
                thisFileInfected = True #this is a boolean (it's true false stuff like that)
        
        if(thisFileInfected == False):
            print(p + " appears to be clean")
            result_box.insert(tk.END, p + " appears to be clean\n")



    print("##### End Section #####")


#checkForSignatures(answer)
window.mainloop()
