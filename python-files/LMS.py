import os;
import sys;
filePathSrc="J:\Translations\QM_Translations\Human\Dateien\Sonstige\CS\UTF-8_Konvertierung"
for root, dirs, files in os.walk(filePathSrc):
    for fn in files:
      if fn[-4:] == '.xml':
        notepad.open(root + "\\" + fn)
        console.write(root + "\\" + fn + "\r\n")
        notepad.runMenuCommand("Encoding", "Convert to UTF-8")
        notepad.save()
        notepad.close()