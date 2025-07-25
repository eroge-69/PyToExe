#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件  :ecloud_img_report.py
@说明  :定时扫描虚机中的clink等是否正常运行，websocket上报给业管
@时间  :2020/10/26 14:49:14
@作者  :dutianxing
@版本  :1.0
'''
import logging,time,websocket,hashlib,ctypes,json,random,os
from ctypes import *
import _thread as thread
from datetime import datetime
import datetime
from callpowershell import PowerShell

class ImgReport():
    def check_clink(self):
        # 判断进程clink_agent 和 clink_service是否存在
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-process clink_agent  -ErrorAction SilentlyContinue") 
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("get-process clink_service  -ErrorAction SilentlyContinue")
            if out2:
                logging.info("clink agent status is running.")
                return True
            else:
                logging.info("clink service status is unusual")
        else:
            logging.info("clink agent status is unusual")
        return False
            

    def check_cloudbase(self):
        #判断cloudbase服务和进程文件是否存在
        with PowerShell('GBK') as ps:
            out1, errs = ps.run("get-service cloudbase-init  -ErrorAction SilentlyContinue")
        if out1:
            with PowerShell('GBK') as ps:
                out2, errs = ps.run("Test-Path 'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\Python\Scripts\cloudbase-init.exe'")
            if out2.strip() == "True":
                logging.info("cloudbase is running")
                return True
            else:
                logging.info("cloudbase-init process file is unusual")
        else:
            logging.info("cloudbase-init service status is unusual")
        return False

    def check_cloudupdate(self):
        #判断补丁升级功能是否正常，通过判断all.log日志的日期和当前日期相差不超过48小时为准
        try:
            filetime=os.path.getmtime("C:\\Program Files (x86)\\ctyun\\clink\\Mirror\\CloudUpdate\\logs\\all.log")
            h=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(filetime))#再由中间格式转为字符串(str)
            y =datetime.datetime.strptime(h, '%Y-%m-%d %H:%M:%S')
            z = datetime.datetime.now()
            diff = z - y
            logging.info("log date time is "+str(y))
            logging.info("now date time is "+str(z))
            logging.info("the diff time between all.log and now is "+str(diff))
            if diff.seconds < 172800:
                logging.info("cloudupdate is running.")
                return True
            else:
                logging.info("cloudupdate is unusual.")
                return False
        except OSError:
            logging.info("[cloudupdate]cloudupdate's log is not exist.")
            reason="Cloudupdate日志文件不存在。"
            return False
        

def get_websocket_num():
    with PowerShell('GBK') as ps:
        out, errs = ps.run('(Get-ItemProperty -Path "HKLM:\\SOFTWARE\\ecloudsoft\\Mirror\\ClinkAgent" -Name "VersionCode").VersionCode')
    agent_ver=int(out.strip())
    if agent_ver > 101310000:
        logging.info("Agent version is bigger than 1.30, WEBSOCKET_DESK_REPORT is 9")
        return 9
    else:
        logging.info("Agent version is smaller than 1.30, WEBSOCKET_DESK_REPORT is 7")
        return 7

def open_web_socket():
    logging.info('open websocket')
    APP_ID = 1007
    local_time = time.time()
    current_time = int(local_time)
    #WEBSOCKET_DESK_REPORT = get_websocket_num()
    WEBSOCKET_DESK_REPORT = 7
    sign = compute_sign(APP_ID, current_time, WEBSOCKET_DESK_REPORT)
    if sign:
        with PowerShell('GBK') as ps:
            out, errs = ps.run("(Get-ItemProperty 'Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\ecloudsoft\\Mirror\\ClinkAgent' -Name 'WebSocketPort').WebSocketPort")
            logging.info(out)
            try:
                temp=int(out.strip())
            except ValueError:
                port=9002
            else:
                port=out.strip()
        format_string = "ws://127.0.0.1:"+str(port)+"?appid={0}&sign={1}&t={2}&type={3}"
        
        websocket_url = format_string.format(APP_ID, sign, current_time, WEBSOCKET_DESK_REPORT)
        logging.info(websocket_url)
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(websocket_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)#
        logging.info(ws.on_error)
        #ws.on_open = on_open
        logging.info('ws run forever')
        ws.run_forever()
    else:
        logging.error('cannot get sign')

def on_message(ws, message):
    logging.info('websocket on message: %s' % message)


def on_error(ws, error):
    logging.info('websocket on error:'+repr(error))


def on_close(ws):
    logging.info('websocket on close ')


def on_open(ws):
    def run(*args):
        message = Message(result, remark)
        report_data = ReportData(102, message)
        logging.info("report data is "+report_data.write())
        json_str = json.dumps(report_data, default=lambda o: o.__dict__, ensure_ascii=False)
        ws.send(json_str)
        logging.info('websocket send outter network info %s' % str(result))
        ws.close()
    thread.start_new_thread(run, ())

class Message(object):
    def __init__(self, result, remark):
        self.result = result
        self.remark = remark
        self.localtime = int(time.time())
    def write(self):
        return "{ result:"+str(self.result)+", remark:"+str(self.remark)+", time:"+str(self.localtime)+"}"

class ReportData(object):
    def __init__(self, bussType, message):
        self.bussType = bussType
        self.message = message
    def write(self):
        return "{ bussType:"+str(self.bussType)+", message:"+self.message.write()+"}"

def compute_sign(app_id, current_time, websocket_type):
    logging.info('compute sign')
    info = get_secret()
    if info and info.contents.data:
        secret = bytes.decode(info.contents.data)
        logging.info(secret)
        input_string = str(app_id) + secret + str(current_time) + str(websocket_type)
        logging.info(input_string)
        sign = hashlib.sha256(input_string.encode("utf8")).hexdigest()
        logging.info(sign)
        return sign
    else:
        return None

class Info(Structure):
    _fields_ = [("data", c_char_p), ("len", c_int)]

def get_secret():
    try:
        logging.info('get secret')
        # C:\\Program Files (x86)\\ctyun\\clink\\Mirror\\ScriptConfig
        folder = 'C:\\Program Files\\Cloudbase Solutions\\Cloudbase-Init\\exe'
        dll_path = folder + '\\communicate.dll'
        lib = ctypes.cdll.LoadLibrary(dll_path)
        #lib.InitLog()
        lib.GetInfo.argtypes = [c_int]
        lib.GetInfo.restype = POINTER(Info)
        INFO_SECRET = 5
        pInfo = lib.GetInfo(INFO_SECRET)
        return pInfo
    except WindowsError as e:
        logging.exception(e)
        return None
    except BaseException as e:
        logging.exception(e)
        return None

def execute(has_signal):
    try:
        logging.info("++++++++++++++++++++++++++++++++++++++++++Img Report Execute+++++++++++++++++++++++++++++++++++++++++++")
        if not has_signal:
            # 创建random
            n=random.randint(0,2*60*60)
            current_time=(datetime.datetime.now()+datetime.timedelta(seconds=n)).strftime("%H:%M")
            logging.info("Restart at "+current_time)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("$env:username")
            username=outs.strip()
            execmd=r"""'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe\ecloud_img_conf.exe' {'signalId':1,'command':25} """
            cmd='schtasks.exe /create /RU '+username+' /tn check_report_img_daily /tr "'+execmd+'" /SC ONCE /ST '+current_time+' /F /RL HIGHEST'
            logging.info(cmd)
            with PowerShell('GBK') as ps:
                out, errs = ps.run(cmd)
                logging.info(out)
            # 创建daily
            n=random.randint(0,12*60*60)
            current_time=(datetime.datetime.now()+datetime.timedelta(seconds=n)).strftime("%H:%M")
            logging.info("Create check_report_img_daily at "+current_time)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run("$env:username")
            username=outs.strip()
            execmd=r"""'C:\Program Files\Cloudbase Solutions\Cloudbase-Init\exe\ecloud_img_conf.exe' {'signalId':1,'command':25} """
            cmd='schtasks.exe /create /RU '+username+' /tn check_report_img_daily /tr "'+execmd+'" /SC DAILY /ST '+current_time+' /RI 5 /DU 9999:59 /F /RL HIGHEST'
            logging.info(cmd)
            with PowerShell('GBK') as ps:
                out, errs = ps.run(cmd)
                logging.info(out)
            return True
        global result
        global remark
        ir = ImgReport()
        if ir.check_clink():
            if ir.check_cloudbase() and ir.check_cloudupdate():
                result=1
                remark='success'
            else:
                result=3
                remark='failure'
        else:
            result=2
            remark='failure'
        logging.info("result is "+str(result)+" and remark is "+remark)
        open_web_socket()
    except Exception as e:
        logging.exception(e)
    except EOFError as e:
        logging.error(e)
    
if __name__ == '__main__':
    result=0
    remark=0
