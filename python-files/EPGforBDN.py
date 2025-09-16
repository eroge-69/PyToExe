import pandas as pd
import os
import sys
import shutil
import zipfile
from zipfile import ZipFile
import pypdf
import time
import smtplib, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)

# Function definition:
def pdf_finder(srctxt,srcdir):
    if type(srctxt)==str:
        txtlst=[srctxt]
    else:
        txtlst=srctxt
    pdflist = []
    for (dirpath, dirnames, filenames) in os.walk(srcdir):
        for fn in filenames:
            if (os.path.join(dirpath,fn))[-4:]==".pdf":
                pdflist.append(os.path.join(dirpath,fn))
    for filepdf in pdflist:
        objpdf=pypdf.PdfReader(filepdf)
        txtpdf=objpdf.pages[0].extract_text()
        counts = 0
        for word in txtlst:
            if word in txtpdf:
                counts=counts+1
        if counts==len(txtlst):
            return filepdf
    return 0
    
def get_epg(traceID):
    if int(traceID[11:13])<94:
        year = "20"+traceID[11:13]
    else:
        year = "19"+traceID[11:13]
    folder = traceID[13:17].lstrip("0")
    specimen = traceID[17:20].lstrip("0")
    trace = traceID[20:22].lstrip("0")
    code = ["GeneMapper",year+"-"+folder+"-"+specimen+"-"+trace]
    srcdir = "z:\\"+year+"\\"+folder
    if os.path.isdir(srcdir)!=True:
        return 0
    if os.path.isdir(".\\epg")!=True:
        os.mkdir(".\\epg")
    if os.path.isdir(srcdir+"\\epg") and pdf_finder(code,srcdir+"\\epg")!=0:
        shutil.copy(pdf_finder(code,srcdir+"\\epg"),".\\epg\\"+traceID+".pdf")
        return 1
    elif os.path.isdir(srcdir+"\\profili") and pdf_finder(code,srcdir+"\\profili")!=0:
        shutil.copy(pdf_finder(code,srcdir+"\\profili"),".\\epg\\"+traceID+".pdf")
        return 1
    elif pdf_finder(code,srcdir)!=0:
        shutil.copy(pdf_finder(code,srcdir),".\\epg\\"+traceID+".pdf")
        return 1
    else:
        return 0
    
def man_get_epg(traceID):
    if int(traceID[11:13])<94:
        year = "20"+traceID[11:13]
    else:
        year = "19"+traceID[11:13]
    folder = traceID[13:17].lstrip("0")
    specimen=traceID[17:20].lstrip("0")
    trace=traceID[20:22].lstrip("0")
    srcdir = "z:\\"+year+"\\"+folder
    dst = os.path.join(".\\epg", traceID+".pdf")
    pdflist = []
    for (dirpath, dirnames, filenames) in os.walk(srcdir):
        for fn in filenames:
            if (os.path.join(dirpath,fn))[-4:]==".pdf":
                pdflist.append(os.path.join(dirpath,fn))
    if len(pdflist)==0:
        return 0
    else:
        for pdffile in pdflist:
            if specimen+"-"+trace in pdffile or specimen+"_"+trace in pdffile:
                ans=input("Is "+pdffile+" the right EPG for trace "+specimen+"-"+trace+" in case "+folder+" I.T. "+year+"? [y/n]\n")
                if ans=="y":
                    src = os.path.join(srcdir, pdffile)      
                    shutil.copy(src,dst)
                    return 1
    return 0

def OK_mk_zip(df, officer):
    dfS = df[df["EPG"]=="OK"]
    dfO = dfS[dfS["Operator"].str.contains(officer[2:])]
    num=len(dfO.get("National database trace ID"))
    if num==0:
        return 0
    else:
        zipO = zipfile.ZipFile(".\\epg\\"+officer+".zip","w")
        for i in dfO.get("National database trace ID"):
            zipO.write(".\\epg\\"+i+".pdf")
        dfO.to_csv(".\\epg\\"+officer+".txt",index=False,sep="\t" )
        zipO.write(".\\epg\\"+officer+".txt")
        zipO.close()
        os.remove(".\\epg\\"+officer+".txt")
        return num

def NO_mk_txt(df, officer):
    dfS = df[df["EPG"]=="NO"]
    dfO = dfS[dfS["Operator"].str.contains(officer[2:])]
    num=len(dfO.get("National database trace ID"))
    if num==0:
        return 0
    else:
        dfO.to_csv(".\\epg\\"+officer+".txt",index=False,sep="\t" )
        return num

def sendmail(officer):
    subject = "EPG per BDN da preparare"
    body = "Dati nel file allegato"
    sender_email = "A.Marino@mail.lan"
    receiver_email = officer+"@mail.lan"
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = sender_email
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    if os.isfile(".\\epg\\"+officer+".zip"):
        filename = ".\\epg\\"+officer+".zip"
    elif os.path.isfile(".\\epg\\"+officer+".txt"):
        filename = ".\\epg\\"+officer+".txt"
    else:
        return 0
    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    with smtplib.SMTP("10.56.76.131", 25) as server:
        server.sendmail(sender_email, receiver_email, text)
    return 1

# Officer names:
officials = ["C.Faccinetto","F.Gentile","N.Staiti","A.Marino"]
experts = ["M.Stabile","D.Capatti","S.Bozzi","C.Demerico","I.Ingletti","G.Margiotta","A.Passero","G.Costa","D.Di Maggio",
         "D.Colloca", "L.Palmaccio","D.Denari","R.Ciccotelli","D.Ferretti","M.Romano","D.Asaro"]
# Working database:
dbase = "DatiPratiche.csv"

# HERE THE PROGRAM BEGINS
print("Gli operatori registrati nel programma sono i seguenti:\n")
print("Ufficiali = "+"; ".join(officials)+"\n")
print("Tecnici = "+"; ".join(experts)+"\n")
print("Verifica che il database DatiPratiche.csv sia presente e aggiornato, con valori separati da virgole\n")
time.sleep(5)

fdocx=input("Inserisci il nome completo del file .docx:\n>")
fparts=fdocx.split(".")
ext=fparts[-1]
if ext.lower()!="docx":
    sys.exit("Filetype error, .docx expected")
with ZipFile(fdocx,'r') as zObject:
    zObject.extractall() 

# Local output directory .\epg is created:
if os.path.isdir(".\\epg")!=True:
    os.mkdir(".\\epg")
    
df=pd.read_csv("DatiPratiche.csv", usecols=["Anno","Pratica","Responsabile"], dtype={"Anno":int,"Pratica":int,"Responsabile":str}, encoding="cp1252",sep=",")

xml = open(".\\word\\document.xml","r")
txt = xml.readlines()
lines = txt[1].replace(">",">\n")

with open("dummy.txt","w") as dummy:
    dummy.write(lines)

xml.close()
dummy.close()

f = open("dummy.txt","r")
data = f.readlines()
dim = len(data)
f.close()


# Summary output file is created:
out=open("out.dat","w")
out.write("National database trace ID\tEPG\tYear\tFolder\tOperator\n")
out.close()
out=open("out.dat","a")

print("Analisi del file .docx in corso...\n")
print("National database trace ID\tEPG Y/N\tCase ID code\tOperator\n")
for i in range(dim):
    annosel="0000"
    pratsel="0000"
    if "FF0000" in data[i] and data[i+7][0]=="I":
        pratsel=data[i+7][13:17] 
        if int(data[i+7][11:13]) < 94:
            annosel="20"+data[i+7][11:13]
        else:
            annosel="19"+data[i+7][11:13]
        test=0
        for n in range(len(df)):
            if test==0 and (str(df.loc[n,"Pratica"]) == pratsel.lstrip("0") and str(df.loc[n,"Anno"]) == annosel):
                test=1
                if get_epg(data[i+7][:24]) == 1:
                    print(data[i+7][:24]+"\tEPG OK\t"+pratsel+" "+"I.T."+" "+annosel+"\t"+str(df.loc[n, "Responsabile"]))
                    newline=data[i+7][:24]+"\tOK\t"+annosel+"\t"+pratsel.lstrip("0")+"\t"+str(df.loc[n, "Responsabile"])+"\n"
                    out.write(newline)
                elif man_get_epg(data[i+7][:24]) == 1:
                    print(data[i+7][:24]+"\tEPG OK\t"+pratsel+" "+"I.T."+" "+annosel+"\t"+str(df.loc[n, "Responsabile"]))
                    newline=data[i+7][:24]+"\tOK\t"+annosel+"\t"+pratsel.lstrip("0")+"\t"+str(df.loc[n, "Responsabile"])+"\n"
                    out.write(newline)
                else:
                    print(data[i+7][:24]+"\tEPG NO\t"+pratsel+" "+"I.T."+" "+annosel+"\t"+str(df.loc[n, "Responsabile"]))
                    newline=data[i+7][:24]+"\tNO\t"+annosel+"\t"+pratsel.lstrip("0")+"\t"+str(df.loc[n, "Responsabile"])+"\n"
                    out.write(newline)                
        if test==0:
            if pratsel.lstrip("0")=="":
                print(data[i+7][:24]+"\tExternal data collected in "+data[i+7][22:24])
                newline=data[i+7][:24]+"\tNO\t0000\t0000\tExternal data collected in "+data[i+7][22:24]+"\n"
                out.write(newline)
            else:    
                print(data[i+7][:24]+"\tEPG NO\t"+pratsel+" "+"I.T."+" "+annosel+"\tNot loaded in ET2D")
                newline=data[i+7][:24]+"\tNO\t"+annosel+"\t"+pratsel.lstrip("0")+"\tNot loaded in ET2D\n"
                out.write(newline)
out.close()
os.remove("dummy.txt")

# Files to be sent by email are created:
print("Creazione dei file da spedire in corso...\n")
df1=pd.read_csv("out.dat",encoding="cp1252",sep="\t")
df1["Operator"].fillna("Unknown",inplace=True)

for name in officials:
    OK_mk_zip(df1,name)
    
for name in experts:
    NO_mk_txt(df1,name)

#All that remains is added to A.Marino.zip:
AllOffs=""
for name in officials:
    AllOffs=AllOffs+"|"+name[2:]
AllOffs=AllOffs.lstrip("|")

AllExps=""
for name in experts:
    AllExps=AllExps+"|"+name[2:]
AllExps=AllExps.lstrip("|")

dfS1 = df1[df1["EPG"]=="OK"]
dfO1 = dfS1[dfS1["Operator"].str.contains(AllOffs)==False]
num1=len(dfO1.get("National database trace ID"))
if num1!=0:
    zipO = zipfile.ZipFile(".\\epg\\A.Marino.zip","a")
    for i in dfO1.get("National database trace ID"):
        zipO.write(".\\epg\\"+i+".pdf")
    dfO1.to_csv(".\\epg\\OtherEPG.txt",index=False,sep="\t" )
    zipO.write(".\\epg\\OtherEPG.txt")
    os.remove(".\\epg\\OtherEPG.txt")
dfS2 = df1[df1["EPG"]=="NO"]
dfO2 = dfS2[dfS2["Operator"].str.contains(AllExps)==False]
num2=len(dfO2.get("National database trace ID"))
if num2!=0:
    dfO2.to_csv(".\\epg\\OtherToDo.txt",index=False,sep="\t" )
    zipO.write(".\\epg\\OtherToDo.txt")
    os.remove(".\\epg\\OtherToDo.txt")
zipO.close()

# Ask permission to send emails:
goon=input("Vuoi inviare i file per email? [y/n]\n>")
if goon=="y":
    print("Invio dei file per email\n")
    for name in officials:
        sendmail(name)
    for name in experts:
        sendmail(name)

