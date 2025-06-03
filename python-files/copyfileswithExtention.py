from tkinter import filedialog
import shutil
import os

#os.chdir("C:\\Users\\Sthe0\\Downloads\\")



#foldersearch = "C:\\" --> V.1 plan
foldersearch = str = filedialog.askdirectory(title="Pick Source Directory")

print(f"Source Folder is {foldersearch}\n")

#dstfolder = "F:\\dest\\" -->  V1. plan  
dstfolder = str = filedialog.askdirectory(title="Pick Destination Directory")

foldersrc = os.listdir(foldersearch)

test = input("Choose whitch type of file/s do you want to copy: ")
print("\n")

if test == "txt" or test == "pdf" or test == "docx" or test == "mp3":

    for files in foldersrc:
        if files.endswith((test)):
            file = foldersearch+files
            shutil.copy2(file,dstfolder)
            print(file, "MOVED to the destination")
            
else:
    print("Give an apropriate File Extention\n")

#last = print(file[3:],"\n")

#print(f"The file {file} MOVED")


