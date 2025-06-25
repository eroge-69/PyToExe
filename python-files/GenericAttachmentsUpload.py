import os
import sys
import subprocess


def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    import pandas as pd
except:
    print('Installing pandas package' )
    install('pandas')
    import pandas as pd

try:
    import base64
except:
    print('Installing base64 package' )
    install('base64')
    import base64

try:
    import openpyxl
except:
    print('Installing openpyxl package' )
    install('openpyxl')
    import openpyxl

try:
    import xlrd
except:
    print('Installing xlrd package' )
    install('xlrd==1.2.0')
    import xlrd
	
try:
    import zeep
except:
    print('Installing zeep package' )
    install('zeep')
    import zeep
import time
from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
try:
    import threading
    import json
    import os
    import sys
    from queue import Queue
    import datetime
    from time import sleep
 
except Exception as e:
    print("Error :{} ".format(e))
    

import numpy as np
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cwd = os.getcwd()
cwd = os.getcwd()

print('Retrieving instance credentials...')
df4 = pd.read_csv(cwd+"\\Code\\InstanceDetails.csv")
df4.columns = ['Field','Value']
for index,row in df4.iterrows():
    if row['Field']=="Url":
        WSDL = row['Value']+'/crmService/ActivityService?wsdl'
    elif row['Field']=="Username":
        username = row['Value']
    elif row['Field']=="Password":
        password = row['Value']
		
print("WSDL :" + WSDL)
print("username :" + username)
print("password :" + '********')		
print ('initiating session')
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)
#WSDL = 'https://eewo-dev6.fa.us6.oraclecloud.com:443/fscmService/ErpObjectAttachmentService?wsdl'
clnt = Client(wsdl=WSDL , transport=Transport(session=session))

print ('Session connected')

print('****Initiating the Supplier Attachment upload process****')
df5 = pd.DataFrame(columns = ['PrimaryKeyValue1','ENTITY','TITLE','Status'])
df6 = pd.DataFrame(columns = ['PrimaryKeyValue1','ENTITY','TITLE','Error'])
xls = pd.ExcelFile(cwd+"\\InputFiles\Generic Attachment template.xlsx")
df2 = pd.read_excel(xls, 'Sample Data')
recordCountU=0
errorCountU=0
successCountU=0
folderpath=cwd+"\\Attachments"

for index, row in df2.iterrows():
    recordCountU= recordCountU+1
    PrimaryKeyValue1 = str(row['PrimaryKeyValue1'])
    title= str(row['ATTACHMENT_TITLE']).replace('#NULL','').replace('nan','')
    ENTITY=str(row['ENTITY'])
    AttachmentType=str(row['AttachmentType'])
    filename= str(row['FILE_TEXT_URL'])
    description = str(row['DESCRIPTION']).replace('#NULL','').replace('nan','')
    UNIQUEID1 = str(row['UNIQUEID1'])
    UNIQUEID2 = str(row['UNIQUEID2']).replace('nan','').replace('.0','')
    UNIQUEID3 = str(row['UNIQUEID3']).replace('nan','').replace('.0','')
    CategoryName = str(row['CategoryName'])
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    status = "Succeeded"
    #print(UNIQUEID2)
    if (AttachmentType=='FILE'):
        filepath = os.path.join(folderpath,ENTITY,filename)
        file = open(filepath,'rb')
        file_content = file.read()
        baseData = file_content
        request_Data = {
                     'attachmentRows' :[{
                                        'EntityName' : ENTITY,
					                    'Pk1Value' : UNIQUEID1,
                                        'Pk2Value' : UNIQUEID2,
                                        'Pk3Value' : UNIQUEID3,
                                        'DatatypeCode' : 'FILE',
                                        'FileName' : filename,
                                        'Title' : title,
                                        'DownloadStatus' : 'N',
                                        'CategoryName' : CategoryName,
                                        'Description' : description,
                                        'UploadedFile' : baseData
                                      }], 
                       'commitData':''
				   }
    elif (AttachmentType=='TEXT'):
              request_Data = {
                     'attachmentRows' :[{
                                        'EntityName' : ENTITY,
					                    'Pk1Value' : UNIQUEID1,
                                        'Pk2Value' : UNIQUEID2,
                                        'Pk3Value' : UNIQUEID3,
                                        'DatatypeCode' : 'TEXT',
                                        'FileName' : filename,
                                        'Title' : title,
                                        'DownloadStatus' : 'N',
                                        'CategoryName' : CategoryName,
                                        'Description' : description,
                                        'UploadedText' : filename
                                      }], 
                       'commitData':''
				   }
    elif (AttachmentType=='URL'):
              request_Data = {
                     'attachmentRows' :[{
                                        'EntityName' : ENTITY,
					                    'Pk1Value' : UNIQUEID1,
                                        'Pk2Value' : UNIQUEID2,
                                        'Pk3Value' : UNIQUEID3,
                                        'DatatypeCode' : 'WEB_PAGE',
                                        'FileName' : title,
                                        'Title' : title,
                                        'DownloadStatus' : 'N',
                                        'CategoryName' : CategoryName,
                                        'Description' : description,
                                        'URL' : filename
                                      }], 
                       'commitData':''
				   }
    else:        
        print(AttachmentType)
    try:
       print(str(index+1)+' '+'ExecustionTime: '+ current_time +'**** Initiating webservice call '+'Object: '+ENTITY+' '+PrimaryKeyValue1 +' '+ title +' ****')
       response = clnt.service.createAttachment(**request_Data)
       #print(response)
       if response.find("SUCCESS") == -1 :
          status = "SUCCESS"
          errorCountU=errorCountU+1
       newdf5 = pd.DataFrame([{'PrimaryKeyValue1':PrimaryKeyValue1,'ENTITY':ENTITY,'TITLE':title,'Status':status}])
       df5 = pd.concat([df5,newdf5],ignore_index=True)
    except Exception as eU:
       #print('Exception')
       status = "Failed"
       errorCountU=errorCountU+1
       newdf6 = pd.DataFrame([{'PrimaryKeyValue1':PrimaryKeyValue1,'ENTITY':ENTITY,'TITLE':title,'Error':eU}])
       df6 = pd.concat([df6,newdf6],ignore_index=True)
print('***********************************')
print('Attachment upload process completed')
print('Total number of records: '+str(recordCountU))
print('Number of successful records: '+str(recordCountU-errorCountU))
print('Writing status into output file: GenericAttachment-UploadStatus.csv')
df5.to_csv(cwd+"\\OutputFiles\GenericAttachment-UploadStatus.csv",index = False)
if errorCountU>0:
   print('Number of records failed to upload: '+str(errorCountU))
   print('Writing failed records into error file')
   df6.to_excel(cwd+"\\OutputFiles\GenericAttachment-Errors.xlsx",index = False)  
sys. exc_info()