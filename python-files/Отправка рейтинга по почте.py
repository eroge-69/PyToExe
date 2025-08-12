#!/usr/bin/env python
# coding: utf-8

# In[6]:


#Импорт библиотек, pandas - для работы с датафреймом, pyodbc - для подключения к hadoop из odbc, warnings - для отключения
#предупреждений, datatime - для работы с функциями времени.
import pandas as pd
import pyodbc
import warnings
warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:,.2f}'.format
from datetime import datetime, timedelta


# In[7]:


#Название источника (DSN)
data_source_name = 'Cloud' 


# In[8]:


#Подключение к источнику
pyodbc.autocommit = True
cursor = pyodbc.connect(f"DSN={'Cloud'}",autocommit=True)


# In[9]:


query = """
WITH counts AS (
  SELECT 
    rt.material AS UPC,
    rt.zabc AS rate,
    rt.loaddate AS loaddate,
    COUNT(*) AS counts
  FROM bw.abc_cv01_hrcp rt
  WHERE rt.plant IN (
    '0002','0003','0004','0005','0006','0007','0008','0009','0010',
    '0011','0012','0013','0014','0015','0016','0017','0018','0019',
    '0020','0021','0022','0023','0024','0025','0026','0027','0028',
    '0029','0030','0031','0032','0033','0034','0035','0036','0037',
    '0038','0039','0040','0041','0042','0044','0045','0046','0047',
    '0048','0049','0050','0051','0052','0054','0055','0056','0057',
    '0058','0059','0060','0061','0062','0063','0065','0066','0067',
    '0068','0069','0071','0072','0073','0074','0075','0076','0077',
    '0078','0079','0080','0081','0082','0083','0084','0085','0086',
    '0087','0088','0089','0091','0092','0093','0094','0095','0096',
    '0097','0098','0099','0100','0106','0107','0108','0109','0110',
    '0111','0112','0113','0114','0115','0116','0117','0118','0119',
    '0121','0122','0123','0124','0126','0127','0128','0130','0131',
    '0132','0134','0135','0136','0137','0139','0140','0141','0142',
    '0144','0146','0147','0148','0149','0150','0151','0152','0153',
    '0154','0155','0156','0157','0158','0160','0161','0163','0164',
    '0165','0166','0167','0168','0169','0171','0172','0173','0175',
    '0176','0177','0178','0179','0180','0182','0183','0184','0185',
    '0188','0191','0192','0194','0196','0199','0200','0201','0202',
    '0203','0204','0206','0207','0208','0209','0210','0211','0212',
    '0213','0214','0215','0216','0217','0218','0219','0220','0221',
    '0223','0224','0225','0226','0227','0228','0229','0230','0233',
    '0235','0236','0237','0238','0240','0241','0242','0244','0245',
    '0246','0247','0248','0260','0262','0263','0264','0265','0266',
    '0267','0268','0269','0270','0271','0272','0273','0277','0279',
    '0284','0285','0286','0291','0292','0293','0294','0295','0296',
    '0297','0298','0299','0300','0302','0303','0304','0306','0307',
    '0309','0311','0312','0316','0317','0318','0319','0320','0321',
    '0323','0324','0325','0326','0327','0328','0329'
  )
  GROUP BY rt.material, rt.zabc, rt.loaddate
),
ranked AS (
  SELECT 
    UPC, rate, loaddate, counts,
    ROW_NUMBER() OVER (PARTITION BY UPC ORDER BY counts DESC) AS rn
  FROM counts
)
SELECT UPC, rate
FROM ranked
WHERE rn = 1
"""


# In[10]:


#Присвоение результата запроса переменной df и чтение результата запроса
df = pd.read_sql(query, cursor)


# In[11]:


#Записываем результат в Excel-файл. При каждом следующем запуске файл будет перезаписываться.
df.to_excel(r"R:\Office\Marketing Department\Мониторинги\Timur\rate.xlsx", index = False)


# In[12]:


import win32com.client as win32
import os
from datetime import datetime

OUTLOOK_SUBJECT = "Ежедневный отчёт Рейтинг"
OUTLOOK_BODY = "Добрый день!\nОтправляю обновлённый файл rate.xlsx."
FILE_PATH = r"R:\Office\Marketing Department\Мониторинги\Timur\rate.xlsx"

TO = ["nataliya.matveeva@lenta.com", "anna.kusurova@lenta.com", "anastasia.sannikova@lenta.com"]
FROM = "timur.tulyakov@lenta.com"  # ваш основной ящик в Outlook-профиле

def send_via_outlook():
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(FILE_PATH)

    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # olMailItem
    mail.To = "; ".join(TO)
    mail.Subject = OUTLOOK_SUBJECT
    mail.Body = OUTLOOK_BODY
    mail.Attachments.Add(FILE_PATH)

    # Если у вас несколько почтовых ящиков в Outlook и нужно строго «От кого»
    try:
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, FROM))  # PR_SENT_REPRESENTING_EMAIL_ADDRESS
    except Exception:
        # Если не сработало — Outlook возьмёт почту по умолчанию
        pass

    mail.Send()
    print(f"Отправлено: {datetime.now()}")

if __name__ == "__main__":
    send_via_outlook()

