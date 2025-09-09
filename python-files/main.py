import json
import time
from datetime import datetime
import uuid
import base64

from tkinter import *
from tkinter import messagebox
import threading
import psycopg2         #pip install psycopg2
import win32com.client  #pip install pywin32
import pythoncom

import requests         #pip install requests

import os

# ================================================================================ vars

isClosed = False

str_msg = ''
str_sign = ''

is_configured = False

db_connected = False
# = None


step = 0

s = 0
m = 0
h = 0
d = 0

def logger(type,msg):
  now = datetime.now()
  year = now.year  # 2024 (int)
  month = now.month  # 5 (int)
  if month<10:
    month = '0'+str(month)
  file_name = 'LOG/'+type+'_'+str(year)+'_'+str(month)+'.txt'
  try:
    file_log = open(file_name, "r", encoding="utf-8")
    str_log = file_log.read()
    file_log.close()
  except:
    str_log = ''
  str_log = str_log+now.strftime("%d.%m.%Y %H:%M:%S : ")+msg+'\n'
  file_log = open(file_name, "w", encoding="utf8")
  file_log.write(str_log)
  file_log.close()

# ================================================================================ on_closing()
def on_closing():
  global isClosed
  if messagebox.askokcancel("Внимание", "Закрыть?"):
    isClosed = True
    root.destroy()

# ================================================================================ new step()
def next_step():
  global params_labels_code
  global step
  if step < parameters_count - 1:
    step += 1
  else:
    step = 0
  for i in range(parameters_count):
    params_labels_code[i].config(bg='white')
    params_labels_id[i].config(bg='white')
    params_labels_send[i].config(bg='white')
    params_labels_unsend[i].config(bg='white')
  params_labels_code[step].config(bg='#AAFFAA')
  params_labels_id[step].config(bg='#AAFFAA')
  params_labels_send[step].config(bg='#AAFFAA')
  params_labels_unsend[step].config(bg='#AAFFAA')

def logDB(msg, clr='cyan'):
  label_db_status.config(background=clr,text='DB: '+msg)

# ================================================================================ ticks2ts()
def ticks2ts(ticks):
  ticks_from2k_msk = int(ticks / 10000000) - 63113904000 + 50491134000 - (3600*3)  # 2001-01-01 00:00:00 + 1601-01-01 00:00:00
  dt_2k = datetime(2001, 1, 1)
  ts = dt_2k.timestamp() + ticks_from2k_msk
  return int(ts)

# ================================================================================ make_json()
def make_json(index, ticks, value):
  global str_msg
  v = int(float(value)*100)/100
  ts2 = ticks2ts(ticks)
  ts1 = ts2 - 1200
  timestamp = time.time()
  ts = str(round(timestamp))
  str_json = '{"onv":"'+str_onv+'","timestamp":' + ts + ',"sources":['
  str_json += '{"source_uuid":"'+json_config['params'][index]['source']+'","pniv":"'+json_config['params'][index]['pniv']+'","sensors":['
  str_json += '{"sensor_uuid":"'+json_config['params'][index]['sensor']+'","state":"OK","parameters":['
  str_json += '{"parameter_uuid":"'+json_config['params'][index]['param']+'","code":"'+json_config['params'][index]['code']+'","unit":"'+json_config['params'][index]['unit']+'","values":['
  str_json += '{"value_uuid":"' + str(uuid.uuid4()) + '","timestamp_start":' + str(ts1) + ',"timestamp_end":' + str(ts2) + ',"value":'+str(v)+' }]},'
  str_json += '{"parameter_uuid":"'+json_config['params'][index]['seal_state']+'","code":"ElectronicSealState","values":['
  str_json += '{"value_uuid":"' + str(uuid.uuid4()) + '","timestamp_start":' + str(ts1) + ',"timestamp_end":' + str(ts2) + ',"value":"OK"}]},'
  str_json += '{"parameter_uuid":"'+json_config['params'][index]['eqip_state']+'","code":"ControlledEquipmentState","values":['
  str_json += '{"value_uuid":"' + str(uuid.uuid4()) + '","timestamp_start":' + str(ts1) + ',"timestamp_end":' + str(ts2) + ',"value":"OK"}]},'
  str_json += '{"parameter_uuid":"'+json_config['params'][index]['ams_state']+'","code":"AmsState","values":['
  str_json += '{"value_uuid":"' + str(uuid.uuid4()) + '","timestamp_start":' + str(ts1) + ',"timestamp_end":' + str(ts2) + ',"value":"OK"}]}]}]}]}'
  str_msg = str_json.replace('П', r'\u041f')

  #file_json = open("msg.json", "w", encoding="utf8") #to_del
  #file_json.write(str_msg)
  #file_json.close()

# ========================================================================== sign_json()
def sign_json():
  global str_sign
  global str_msg

  pythoncom.CoInitialize()

  try:

    # hash ==========================================================================
    hasher = win32com.client.Dispatch("CAdESCOM.HashedData")
    hasher.Algorithm = 101
    hasher.DataEncoding = 1
    hasher.Hash(base64.b64encode(str_msg.encode("utf-8")).decode("ascii"))

    # sign ==========================================================================
    cades = win32com.client.Dispatch("CAdESCOM.CadesSignedData")
    pem = cades.SignHash(hasher, signer, 0xFFFF)

    signature = (pem.replace("\r", "").replace("\n", ""))

    #file_sign = open("sign64", "w", encoding="utf8") #to_del
    #file_sign.write(signature)
    #file_sign.close()

    str_sign = signature

    return True
  except:
    label_docker_status.config(bg='red', text='Ошибка подписи')
    logger('MAIN', 'Ошибка выполнения запроса к серверу РПН')
    return False
  finally:
    pythoncom.CoUninitialize()

# ========================================================================== send_json
def send_json(index):
  global str_msg
  global str_sign

  #json_file = open("msg.json", "r", encoding="utf8") #to_del
  #str_json = json_file.read()
  #json_file.close()

  #sign_file = open("sign64", "r")
  #sign64 = sign_file.read()
  #sign_file.close()

  str_json = str_msg
  sign64 = str_sign

  headers = {
    "Content-Type": "application/json",
    "accept": "application/json",
    "serial": cfg_serial,
    "signature": sign64
  }

  try:
    response = requests.post("https://uonvos.rpn.gov.ru/api/svc/onv/monitoring/devices/"+json_config['params'][index]['asi']+"/sources", headers=headers, data=str_json + ' ')
    if (str(response.json()['code']) == '200') or (str(response.json()['errors']).find('уже зафиксировано') > 0):
      label_post_status.config(text='POST status: OK')
      return True
      #print(response.json())
    else:
      label_post_status.config(text='POST status: ' + str(response.json()['code']))
      logger('POST', 'Ответ сервера РПН:'+response.json())
      #print(response.json())
      return False

  except:
    label_post_status.config(text='POST status: request.post() -> error')
    logger('POST', 'Ошибка выполнения запроса к серверу РПН')
    return False

# ========================================================================== send_ok mark
def send_ok_mark(time):
  global db_connection
  cursor = db_connection.cursor()
  str_itemid = json_config['params'][step]['itemid']
  try:
    str_sql = 'UPDATE '+str_db_table+' SET "send_ok"=True WHERE "itemid"='+str_itemid+' AND "Time"='+time+ ';'
    cursor.execute(str_sql)
    db_connection.commit()
    return True
  except:
    logger('DB', 'Ошибка редактирования БД')
    return False

# ================================================================================ ticker()
def ticker():
  global s, m, h, d
  global isClosed
  if not isClosed:
    threading.Timer(1, ticker).start()
    if s < 59:
      s += 1
    else:
      s = 0
      if m < 59:
        m += 1
      else:
        m = 0
        if h < 23:
          h += 1
        else:
          h = 0
          d += 1
    if h < 10:
      hh = '0' + str(h)
    else:
      hh = str(h)
    if m < 10:
      mm = '0' + str(m)
    else:
      mm = str(m)
    if s < 10:
      ss = '0' + str(s)
    else:
      ss = str(s)
    label_uptime.config(text='Uptime: ' + str(d) + 'd ' + hh + ':' + mm + ':' + ss)

# ================================================================================ DB connect
def db_connect():
  global db_connected
  global db_connection
  try:
    db_connection = psycopg2.connect(user=str_db_user, password=str_db_psw, host=str_db_addr, port=str_db_port, database=str_db_name)
    db_connected = True
    logDB('CONN OK','lime')
  except:
    db_connected = False
    logDB('CONN ERROR','red')
    logger('DB', 'Ошибка подключения к БД')
  if db_connected:
    cursor = db_connection.cursor()
    str_sql = 'ALTER TABLE '+str_db_table+' ADD COLUMN IF NOT EXISTS send_ok boolean default false;'
    cursor.execute(str_sql)
    db_connection.commit()

# ================================================================================ DB read
def db_read(step):
  global db_connected
  cursor = db_connection.cursor()
  str_itemid = json_config['params'][step]['itemid']
  #str_sql = 'SELECT '+str_db_time_column+','+str_db_value_column+' FROM '+str_db_table+' WHERE '+str_db_itemid_column+'='+str_itemid+' AND send_ok=false;'
  try:
    str_sql = 'SELECT COUNT(*) FROM '+str_db_table +' WHERE '+str_db_itemid_column+'='+str_itemid+' AND '+str_db_time_column+'>'+cfg_start_time+' AND layer=0 AND send_ok=false'
    cursor.execute(str_sql)
    sql_resp = cursor.fetchall()
    params_labels_unsend[step].config(text=sql_resp[0][0])
    logDB('READ OK', 'lime')

    str_sql = 'SELECT '+str_db_time_column+', '+str_db_value_column+' FROM '+str_db_table
    str_sql = str_sql + ' WHERE '+str_db_itemid_column+'='+str_itemid+' AND '+str_db_time_column+'>'+cfg_start_time+' AND layer=0 AND send_ok=False'
    str_sql = str_sql + ' ORDER BY '+str_db_time_column+' LIMIT 1;'
    cursor.execute(str_sql)
    sql_resp = cursor.fetchall()
    logDB('READ OK('+str(len(sql_resp))+')', 'lime')

  except:
    db_connection.close()
    db_connected = False
    logDB('READ ERROR', 'red')
    logger('DB', 'Ошибка чтения записей БД')

  if len(sql_resp)>0:

    make_json(step, sql_resp[0][0], sql_resp[0][1])

    if sign_json():
      label_docker_status.config(bg='lime')
      if send_json(step):
        label_post_status.config(bg='lime')
        if send_ok_mark(str(sql_resp[i][0])):
          params_labels_send[step].config(text=str(int(params_labels_send[step]["text"]) + 1))
        else:
          logDB('UPDATE fail','red')
      else:
        label_post_status.config(bg='red')
    else:
      label_docker_status.config(bg='red')

  next_step()

# ================================================================================ sender()
def sender():
  global step
  global isClosed
  if not isClosed:
    threading.Timer(cfg_main_period_sec, sender).start()
    if not db_connected:
      db_connect()
    else:
      db_read(step)











# ================================================================================ main ()

os.makedirs("LOG", exist_ok=True)
logger('MAIN', 'Приложение запущено')






# ================================================================================ tkinter

root = Tk()
root.title("Teracont УОНВОС регистратор v2.2.1 (КриптоПРО)")
root.geometry("800x480")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

for c in range(4): root.columnconfigure(index=c, weight=1)

label_config = Label(text='Конфигурация', bg='silver')
label_config.grid(row=0,column=0, padx=20, pady=20, ipady=20, sticky=EW)

label_db_status = Label(text='БД:', bg='silver')
label_db_status.grid(row=0,column=1, padx=20, pady=20, ipady=20, sticky=EW)

label_docker_status = Label(text='ЭЦП', bg='silver')
label_docker_status.grid(row=0,column=2, padx=20, pady=20, ipady=20, sticky=EW)

label_post_status = Label(text='HTTP:', bg='silver')
label_post_status.grid(row=0,column=3, padx=20, pady=20, ipady=20, sticky=EW)

label_uptime = Label(text='Uptime: ')
label_uptime.grid(row=1,column=0, columnspan=4, pady=5, sticky=EW)


# ========================================================================== load config
is_configured = False
try:
  file_config = open("config.json", "r", encoding='utf-8')
  str_config = file_config.read()
  file_config.close()

  json_config = json.loads(str_config)
  str_onv = json_config['onv']
  str_license = json_config['license']
  str_db_user = json_config['db_user']
  str_db_psw = json_config['db_psw']
  str_db_addr = json_config['db_addr']
  str_db_port = json_config['db_port']
  str_db_name = json_config['db_name']
  str_db_table = json_config['db_table']
  str_db_itemid_column = json_config['db_itemid_column']
  str_db_time_column = json_config['db_time_column']
  str_db_value_column = json_config['db_value_column']
  cfg_utc = json_config['utc']
  cfg_main_period_sec = json_config['main_period_sec']
  cfg_serial = json_config['serial']
  cfg_signer = json_config['signer']
  cfg_start_time = str(json_config['start_time'])
  #print(cfg_start_time)

  parameters_count = len(json_config['params'])
  if str_license == base64.b64encode(bytes([b ^ 0xED for b in str_onv.encode('utf-8')])).decode('utf-8'):
    label_config.config(background='lime')
    is_configured = True
  else:
    label_config.config(background='red', text='Отсутсвует лицензия для данного объекта. По всем вопросам info@teracont.ru')
    logger('MAIN', 'Отсутсвует лицензионный ключ')
except:
  label_config.config(background='red', text='Ошибка чтения файла конфигурации. По всем вопросам info@teracont.ru')


# find cert==========================================================================
is_cert_found = False
if is_configured:

    try:
      store = win32com.client.Dispatch("CAdESCOM.Store")
      store.Open(2, 'MY', 0)
      for cert in store.Certificates:
          if cfg_signer in cert.SubjectName:
              my_cert = cert
              is_cert_found = True
      if is_cert_found:
        signer = win32com.client.Dispatch("CAdESCOM.CPSigner")
        signer.Certificate = my_cert
        signer.Options = 2
      else:
        label_config.config(background='red', text='Не найден сертификат. По всем вопросам info@teracont.ru')
        logger('MAIN', 'Сертификат не найден')
    except:
      label_config.config(background='red', text='Установите КриптоПро. По всем вопросам info@teracont.ru')
      logger('MAIN', 'Ошибка подключения компонентов КриптоПро')


# ========================================================================== threats
if is_cert_found:

  label_grid1 = Label(text='Code', bg='gray')
  label_grid1.grid(row=2,column=0, sticky=EW)
  label_grid2 = Label(text='ID', bg='gray')
  label_grid2.grid(row=2, column=1, sticky=EW)
  label_grid3 = Label(text='Отправлено', bg='gray')
  label_grid3.grid(row=2, column=2, sticky=EW)
  label_grid4 = Label(text='В очереди', bg='gray')
  label_grid4.grid(row=2, column=3, sticky=EW)

  params_labels_code = []
  params_labels_id = []
  params_labels_send = []
  params_labels_unsend = []
  for i in range(parameters_count):
    params_labels_code.append(Label(background="white", text=json_config['params'][i]['code']))
    params_labels_id.append(Label(background="white", text=json_config['params'][i]['itemid']))
    params_labels_send.append(Label(background="white", text='0'))
    params_labels_unsend.append(Label(background="white", text='0'))
    params_labels_code[i].grid(row=3 + i, column=0, sticky=EW)
    params_labels_id[i].grid(row=3 + i, column=1, sticky=EW)
    params_labels_send[i].grid(row=3 + i, column=2, sticky=EW)
    params_labels_unsend[i].grid(row=3 + i, column=3, sticky=EW)
  sender()

ticker()
root.mainloop()