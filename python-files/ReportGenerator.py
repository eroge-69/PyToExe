import os, sys, time, pandas as pd  #, ctypes, subprocess
from PIL import Image
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from os.path import exists
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Pt

encodings = ['utf-8', 'utf-16', 'windows-1250', 'windows-1252']
wdir = os.getcwd()
print(len(sys.argv))
if len(sys.argv) == 3:
    configDir = sys.argv[1]
    openDir = sys.argv[2]
else:
    configDir = sys.argv[1]
    openDir = "C:\\"

print(configDir)
print(openDir)
#configDir = 'X:\\test Dir'
imgDir = ''

#print(configDir)
#print(wdir)
#print(sys.argv)

lines = []
context = {}
msg = {}
doc = ''
popup = True


logday = datetime.now().strftime('%Y%m%d')

if exists(configDir + '\\log'):
    log = open(configDir + '\\log\\LOG_' + logday + '.txt', 'w')
else:
    logDir = configDir + '\\log'
    os.makedirs(logDir)
    log = open(configDir + '\\log\\LOG_' + logday + '.txt', 'w')

if exists(configDir + '\\docs'):
    pass
else:
    docsDir = configDir + '\\docs'
    os.makedirs(docsDir)

if exists(wdir + '\\PDFconverter'):
    pass
else:
    logNow = datetime.now().strftime('%H:%M:%S')
    log.write(logNow+' - PDFconverter not found'+'\n')
    messagebox.showerror("Fatal Error", "PDFconverter not found")
    log.close()
    sys.exit()

try:
    print(configDir + '\\config_file.txt')
    f = open(configDir + '\\config_file.txt', 'r')
    lines = f.readlines()
    f.close()
except:
    logNow = datetime.now().strftime('%H:%M:%S')
    log.write(logNow+' - config_file.txt not found'+'\n')
    messagebox.showerror("Fatal Error", "config_file.txt not found")
    log.close()
    sys.exit()

for line in lines[1:]:
    line.strip()
    splitted = line.split('\t')

    tag_name = splitted[0]
    tag_type = splitted[1]
    tag_value = str(splitted[2].rstrip('\n'))

    if 'POP' in tag_type:
        if ('Y' in tag_value) or ('True' in tag_value):
            popup = True
        elif ('N' in tag_value) or ('False' in tag_value):
            popup = False
        else:
            popup = True

    elif 'LEN' in tag_type:
        language = tag_value
        for e in encodings:
            try:
                L = pd.read_csv(wdir+'\\languages.txt' ,delimiter='\t', encoding=e)
                for index, row in L.iterrows():
                    msg[row['errCode']] = row[str(language)]
            except UnicodeDecodeError:
                print('Opening Language file: got unicode error with %s , trying different encoding' % e)
            except FileNotFoundError:
                logNow = datetime.now().strftime('%H:%M:%S')
                log.write(logNow + ' - Language file not found in '+wdir+"\\languages.txt"+ ', popups disabled'+'\n')
                if popup:
                    messagebox.showerror("Fatal Error", "Language file not found, popups disabled")
                    popup = False

    elif 'TMPL' in tag_type:
        template = tag_value
        try:
            T = open(tag_value, 'r')
            T.close()
        except FileNotFoundError:
            logNow = datetime.now().strftime('%H:%M:%S')
            log.write(logNow + ' - ' + msg[1]+'\n')
            if popup:
                messagebox.showerror("Fatal Error", msg[1])
            log.close()
            sys.exit()
        doc = DocxTemplate(template)

    elif 'IMG' in tag_type:
        print('image')
        if exists(tag_value):
            doc.replace_pic(tag_name, tag_value)
        else:
            logNow = datetime.now().strftime('%H:%M:%S')
            log.write(logNow + ' - '+msg[5]+'\n')

    elif 'SIM' in tag_type:
        print('image string')
        if exists(tag_value):
            im = Image.open(tag_value)
            W,H = im.size
            im.close()
            imgObj = InlineImage(doc, tag_value, width=Pt(W*(72/96)), height=Pt(H*(72/96))) #*(72/96) pixel -> points
            context[tag_name] = imgObj
        else:
            logNow = datetime.now().strftime('%H:%M:%S')
            log.write(logNow + ' - '+msg[5]+'\n')

    elif 'STR' in tag_type:
        print('string')
        context[tag_name] = tag_value

    elif 'TABLE' in tag_type:
        table = pd.DataFrame()
        for e in encodings:
            try:
                T = open(tag_value, 'r')
                T.close()
                table = pd.read_csv(tag_value, delimiter="\t", encoding=e)
            except UnicodeDecodeError:
                print('Opening Table file: got unicode error with %s , trying different encoding' % e)
            except FileNotFoundError:
                logNow = datetime.now().strftime('%H:%M:%S')
                log.write(logNow + ' - ' + msg[2]+'\n')
                if popup:
                    messagebox.showerror("Fatal Error", msg[2])
                log.close()
                sys.exit()
        list = []
        for index, row in table.iterrows():
            dict = {}
            for key in table.keys():
                if pd.isna(row[key]):
                    #print(key+" is nan")
                    dict[str(key)] = ''
                else:
                    dict[str(key)] = row[key]
            list.append(dict)
        context[tag_name] = list

    else:
        print('boh')

doc.render(context)

retry_loop = 1
while retry_loop:
    dir = asksaveasfilename(initialdir=openDir, initialfile="nome_file", title="Save Report", filetypes=[("PDF","*.pdf")], defaultextension=".pdf")

    if dir:
        fileDir = ''
        dir = dir.split("/")
        for folder in dir[0:len(dir)-1]:
            fileDir += folder +'/'
        dir.reverse()
        fileName = dir[0]
        reportPath = configDir + '\\docs\\'+ fileName.rstrip('.pdf') +'.docx'
        print(reportPath)
        doc.save(reportPath)
        print(fileDir)
        if exists(fileDir):
            retry_loop = 0
            print('printo')

            os.system("\"\""+str(wdir)+"\PDFconverter\LibreOfficeWriterPortable.exe\" --headless --convert-to pdf \"" + reportPath + "\" --outdir \""+ fileDir +"\"\"" +'\n')
            fileFindingloop=1
            while(fileFindingloop):
                try:
                    today = datetime.now()
                    now = today.strftime("%Y-%m-%d %H:%M")
                    nowS = today.strftime('%S')

                    mod = datetime.fromtimestamp(os.stat(fileDir + fileName).st_mtime)
                    modif = mod.strftime("%Y-%m-%d %H:%M")
                    modifS = mod.strftime('%S')
                    if exists(fileDir + fileName):
                        """print('ECCOLO')
                        print(modif)
                        print(now)
                        print(modifS)
                        print(nowS)"""

                        if modif == now and modifS <= nowS:
                            print('CONVERTITO')
                            logNow = datetime.now().strftime('%H:%M:%S')
                            filePath = (fileDir + '\\' + fileName).replace("/","\\")
                            log.write(logNow + ' - GENERAZIONE REPORT GENERATA CON SUCCESSO IN: ' + filePath +'\n')
                            """if popup:
                                text = msg[999]
                                title = msg[998]
                                risp = ctypes.windll.user32.MessageBoxExW(None, text, title, 0x40000|4) ############ MESSAGE BOX ON TOP OF EVERYTHING
                                if risp == 6:
                                    subprocess.Popen([fileDir + '\\' + fileName], shell=True)
                                    log.close()
                                    sys.exit()
                                else:
                                    log.close()
                                    sys.exit()
                            else:
                                os.system(fileDir+'\\'+fileName)"""
                            complete = open(configDir+"\\ReportGenerator.txt", 'w')
                            complete.write(filePath)
                            complete.close()
                            log.close()
                            sys.exit()
                except FileNotFoundError:
                    pass
                time.sleep(1)
        else:
            logNow = datetime.now().strftime('%H:%M:%S')
            log.write(logNow + ' - ' + msg[3]+'\n')
            if popup:
                messagebox.showwarning("Fatal Error", msg[3])
    else:
        complete = open(configDir + "\\ReportGenerator.txt", 'w')
        complete.write('')
        complete.close()
        logNow = datetime.now().strftime('%H:%M:%S')
        log.write(logNow + ' - ' + msg[6]+'\n')
        if popup:
            messagebox.showwarning("Fatal Error", msg[6])
        log.close()
        sys.exit()

