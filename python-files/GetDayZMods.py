import os
import shutil

def FindAndCopyModKeys(directoryPath):
    for root, folder, files in os.walk(directoryPath):
        if IsModKeyFolder(root):
            CopyModKey(root)
            
def CopyModKey(sourcePath):
    for file in os.listdir(sourcePath):
        filePath = os.path.join(sourcePath, file)
        if os.path.isfile(filePath):
            shutil.copyfile(filePath, os.path.join(os.getcwd() + "\\Keys", file))

def IsModKeyFolder(folderPath):
    rootList = str(folderPath).split("\\")
    rootList.reverse()
    keyFolder = rootList[0]
    modFolder = rootList[1]
    
    return str(modFolder).startswith("@") and str(keyFolder).lower() == "keys"

def GetFolders(directoryPath):
    folders = []
    
    for entry in os.listdir(directoryPath):
        if str(entry).startswith("@"):
            if os.path.isdir(os.path.join(directoryPath, entry)):
                folders.append(entry)
            
    return folders

def CreateStringFromFolderList(folders):
    textString = '"-mod='
    
    for folder in folders:
        textString += folder + ";"
        
    textString += '"'
    
    return textString
  
  
FindAndCopyModKeys(os.getcwd())    
folders = GetFolders(os.getcwd())
print(folders)
textString = CreateStringFromFolderList(folders)
print(textString)

if folders.count != 0:
    try:
        with open("ModParameter.txt", "w") as file:
            file.write(textString)
    finally:
        file.close()