# agent.py
import os, sys, json, time, uuid, platform, socket
import psutil
import requests
from datetime import datetime

AGENT_KEY = '#$@GFDGDFg546t$trgktrgmnrt5%T^%#$#$123134'
SERVER_URL = 'https://vinay.whserver.in/api/report.php'
REGISTER_URL = 'https://vinay.whserver.in/api/register.php'

# try import screenshot lib
try:
    if platform.system() == 'Windows':
        from PIL import ImageGrab
        def take_screenshot(path):
            img = ImageGrab.grab()
            img.save(path)
    else:
        import pyscreenshot as ImageGrab
        def take_screenshot(path):
            img = ImageGrab.grab()
            img.save(path)
except Exception as e:
    def take_screenshot(path):
        return False

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def smart_info():
    # try using smartctl if present
    try:
        out = os.popen('smartctl --scan-open && smartctl -H /dev/sda').read()
        return out
    except Exception as e:
        return None

def collect():
    info = {}
    info['ts'] = datetime.utcnow().isoformat()+'Z'
    info['agent_id'] = str(uuid.getnode())
    info['hostname'] = platform.node()
    info['platform'] = platform.platform()
    info['os'] = platform.system()
    info['ip'] = get_ip()
    info['cpu_percent'] = psutil.cpu_percent(interval=1)
    info['cpu_count'] = psutil.cpu_count()
    mem = psutil.virtual_memory()
    info['mem_total'] = mem.total
    info['mem_used'] = mem.used
    # disks
    disks = []
    for p in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({'device':p.device,'mount':p.mountpoint,'fstype':p.fstype,'total':usage.total,'used':usage.used,'free':usage.free})
        except:
            pass
    info['disks'] = disks
    # top processes
    procs = []
    for p in psutil.process_iter(['pid','name','username','cpu_percent','memory_info']):
        try:
            d = p.info
            procs.append({'pid':d['pid'],'name':d['name'],'user':d.get('username'),'cpu':d.get('cpu_percent')})
        except:
            pass
    # sort by cpu and take top 10
    procs = sorted(procs, key=lambda x: x.get('cpu',0), reverse=True)[:10]
    info['top_processes'] = procs
    info['smart'] = smart_info()
    return info

def register():
    payload = {'agent_key':AGENT_KEY,'name':platform.node(),'os':platform.system()}
    try:
        r = requests.post(REGISTER_URL, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        print("Register failed:", e)
        return None

def send_report(payload):
    # try to attach screenshot as multipart
    screenshot_file = f"/tmp/screenshot_{int(time.time())}.png"
    ok = False
    try:
        take_screenshot(screenshot_file)
        if os.path.exists(screenshot_file):
            files = {'screenshot': open(screenshot_file,'rb')}
            data = {'payload': json.dumps(payload)}
            headers = {'X-AGENT-KEY': AGENT_KEY}
            r = requests.post(SERVER_URL, files=files, data=data, headers=headers, timeout=15, verify=True)
            ok = r.status_code == 200
            files['screenshot'].close()
            os.remove(screenshot_file)
        else:
            # send JSON only
            headers = {'X-AGENT-KEY': AGENT_KEY, 'Content-Type':'application/json'}
            r = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers, timeout=15, verify=True)
            ok = r.status_code == 200
    except Exception as e:
        print("Send error:", e)
        ok = False
    return ok

if __name__=='__main__':
    # register once
    print("Registering agent...")
    print(register())
    # main collect and send loop (single-run)
    data = collect()
    print("Collected:", json.dumps({'hostname':data['hostname'],'ip':data['ip']},ensure_ascii=False))
    ok = send_report(data)
    print("Sent:", ok)
