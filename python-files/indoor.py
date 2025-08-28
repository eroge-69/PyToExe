from pedalboard import Pedalboard, Gain, Reverb, LowShelfFilter
from pedalboard.io import AudioFile
from pathlib import Path
import os
import sys
import json
import shutil
import time

file_path = Path(__file__).parents[0].__str__()

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    file_path = Path(sys.executable).parents[0].__str__()

sndType = ["shoot","shoot_actor","silncer_shot","silncer_shot_actor","reload","reload_empty","draw","holster"]
sndTypeSetting = ["shoot","shoot","shoot","shoot","action","action","action","action"]
extraSndList = ["bolt","pump"]

print("Commands :")
print("[none or anything else] - Add more sounds, wont delete anything")
print("delete - Delete all sounds, uninstall the mod")
print("reset - Delete and then regenerate sounds, do this when you change the settings")

config = json.load(open("indoor_config.json","r"))

cmd = input("Type command: ")

def getFileName(stri):
    return stri.split("\\")[len(stri.split("\\"))-1]

def genSound(input, name, setting):
    try:
        # Normalize and resolve paths completely
        input_parent = Path(input).resolve().parent
        output_dir = Path(convDir(input_parent.__str__()))
        
        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct full output path
        output_path = output_dir / name
        
        # Rest of your existing processing logic...
        with AudioFile(str(input).replace("\n", "")) as f:
            with AudioFile(str(output_path), "w", f.samplerate, f.num_channels) as o:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)
    
    except Exception as e:
        print(f"Error processing sound {name}: {e}")
        import traceback
        traceback.print_exc()

def getSndName(i):
    return sndType[i]

def getFullSndName(i):
    return "snd_"+sndType[i]

def getLayersCount(dirs,sound_type):
    for i in range(len(dirs)):
        if dirs[i].find("snd_"+sound_type)!=-1:
            return int(dirs[i][len(dirs[i])-1]),i+1


def createBlankArray(type):
    a = []
    for i in range(len(sndType)):
        if type == "num":
            a.append(0)
        if type == "str":
            a.append("")
        if type == "array":
            a.append([])
    return a

def getExtraName(dir):
    for i in range(len(extraSndList)):
        if getFileName(dir).find(extraSndList[i])!=-1:
            return "_"+extraSndList[i]
    return ""

def bRange(ar,m = -1):
    if type(ar) is list:
        i = 0
        a = []
        while i < len(ar):
            a.append(i)
            i += 1
        return a
    if type(ar) is int:
        i = ar
        a = []
        while i < m:
            a.append(i)
            i += 1
        return a

def convDir(stri):
    try:
        # Normalize the path first
        normalized_path = os.path.normpath(stri)
        
        # Find the gamedata\sounds part of the path
        sounds_index = normalized_path.lower().find("\\gamedata\\sounds\\")
        if sounds_index != -1:
            # Construct the new path with indoor_gen
            new_path = (
                normalized_path[:sounds_index+17] + 
                "indoor_gen\\" + 
                normalized_path[sounds_index+17:]
            )
            return os.path.normpath(new_path)
        
        return normalized_path
    except Exception as e:
        print(f"Error in convDir: {e}")
        return stri

def checkPath(path):
    if not path:
        return False
    
    try:
        # Use pathlib for more robust path handling
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        print(f"Permission denied when creating directory: {path}")
    except OSError as e:
        print(f"Error creating directory {path}: {e}")
    
    return False

if cmd == "delete" or cmd == "reset":
    remove_list = []
    if os.path.exists(file_path+"\\gamedata\\sounds\\indoor_gen"):
        shutil.rmtree(file_path+"\\gamedata\\sounds\\indoor_gen")
        print("Wiped indoor gen folder")
    for root, dir, files in os.walk(file_path+"\\gamedata\\sounds"):
        for f in files:
            if f.find("indoor_gunsnd_bak")!=-1:
                remove_list.append(root + "\\" + f)
    if len(remove_list) > 0:
        print("Old Sounds Detected, Removing")
        for i in range(len(remove_list)):
            print("Remove ", i, " Files")
            if os.path.isdir(remove_list[i]):
                os.rmdir(remove_list[i])
            else:
                os.remove(remove_list[i])

if cmd != "delete":
    for m in range(len(output)):
        dirs = output[m].split("..")
        dirs[len(dirs)-1] = dirs[len(dirs)-1].replace("\n","") # clean up
        wp_name = dirs[0]
        sndDirs = createBlankArray("array")
        sndFiles = createBlankArray("array")
        sndLayerStart = createBlankArray("num")
        sndLayerCount = createBlankArray("num")
        for i in range(len(sndType)):
            sndLayerCount[i],sndLayerStart[i] = getLayersCount(dirs,getSndName(i))
            for k in bRange(sndLayerStart[i],sndLayerStart[i]+sndLayerCount[i]):
                sndDirs[i].append(dirs[k])
                sndFiles[i].append(Path(file_path+"\\gamedata\\sounds\\"+dirs[k]+".ogg"))
        if sndFiles[0] and sndFiles[0][0].is_file():
            print("File found.")
            config_file.write(";-------"+wp_name+"---------"+"\n")
            config_file.write("!["+wp_name+"]"+"\n")
            #######
            sndProcessedFiles = createBlankArray("array")
            for i in range(len(sndType)):
                if sndDirs[i]:
                    for j in bRange(sndDirs[i]):
                        if sndFiles[i][j] and sndFiles[i][j].is_file() and sndFiles[i][j].__str__().lower().find("\\gamedata\\sounds\\")!=-1 and sndFiles[i][j].resolve().__str__().lower().find("\\gamedata\\sounds\\")!=-1:
                            extraName = getExtraName(sndDirs[i][j])
                            fileName = getFullSndName(i)+extraName+str(j)+".ogg"
                            if not Path(convDir(sndFiles[i][j].parents[0].__str__()+"\\"+fileName)).is_file():
                                genSound(sndFiles[i][j],fileName,sndTypeSetting[i])
                            sndProcessedFiles[i].append(convDir(sndFiles[i][j].parents[0].__str__()+"\\"+fileName).replace(".ogg",""))
                    if sndProcessedFiles[i]:
                        config_file.write(getFullSndName(i)+"_indoor = "+wp_name+"_"+getFullSndName(i)+"_gen\n")
            for i in range(len(sndType)):
                if sndDirs[i] and sndProcessedFiles[i]:
                    config_file.write("@["+wp_name+"_"+getFullSndName(i)+"_gen]"+"\n")
                    extraNameLayer = {}
                    extraLayersCount = 2
                    for j in bRange(sndProcessedFiles[i]):
                        extraed = False
                        for extra in extraSndList:
                            if getFileName(sndProcessedFiles[i][j]).find(extra)!=-1:
                                if extra not in extraNameLayer:
                                    extraNameLayer[extra] = [extraLayersCount,0]
                                    extraLayersCount+=1
                                index = extraNameLayer[extra][1]
                                if index == 0: 
                                    index = "" 
                                config_file.write("snd_"+str(extraNameLayer[extra][0])+"_layer"+str(index)+" = "+sndProcessedFiles[i][j].__str__().replace(file_path+"\\gamedata\\sounds\\","")+"\n")
                                extraed = True
                                extraNameLayer[extra][1] +=1
                        if not extraed:
                            num = j
                            if j==0: 
                                num = ""
                            config_file.write("snd_1_layer"+str(num)+" = "+sndProcessedFiles[i][j].__str__().replace(file_path+"\\gamedata\\sounds\\","")+"\n")
                    config_file.write("\n")
        print("Processing: ",s,"/",len(output))
        s+=1

    ### Setup commenter
    # convert to config file to .txt then back to .ini in order support break line :/, im gonna kms
    Path(file_path+"\\caco\\config.ini").rename(Path(file_path+"\\caco\\config.ini").with_suffix(".txt"))
    with open(file_path+"\\caco\\config.txt","r") as cacoConfigFile:
        cacoConfig = cacoConfigFile.readlines()
        cacoConfig[0] = "GamedataDir="+file_path+"\\gamedata"+"\n"
        cacoConfig[1] = "FfmpegBinDir="+file_path+"\\caco\\fffmpeg-bin"+"\n"
        cacoConfig[2] = "InputDir="+file_path+"\\gamedata\\sounds\\indoor_gen"+"\n"
        cacoConfig[3] = "OutputDir="+file_path+"\\gamedata\\sounds\\indoor_gen"+"\n"
        open(file_path+"\\caco\\config.txt","w").writelines(cacoConfig)
    Path(file_path+"\\caco\\config.txt").rename(Path(file_path+"\\caco\\config.txt").with_suffix(".ini"))
    open(file_path+"\\caco\\runner.bat","w").write(file_path+"\\caco\\caco.exe\nPause")
    print("Openning CACO commenter..........")
    time.sleep(5)
    os.startfile(file_path+"\\caco\\runner.bat")
config_file.close()
