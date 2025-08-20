import cv2, numpy as np, PySimpleGUI as sg, threading, time, socket, struct, os, subprocess, json
from ultralytics import YOLO
from pynput import mouse
import serial

# ====== 配置 ======
STREAM_IP = "0.0.0.0"
STREAM_PORT = 5005
DEFAULT_MODEL = "model_v8.pt"
UDP_MAX = 65536
CONFIG_FILE = "game_profiles.json"

# ====== MAKCU 接口 ======
class MakcuInterface:
    def __init__(self, prefer='serial', com='COM3', baud=115200, exe_path='makcu.exe', dry=True, udp_addr=('127.0.0.1',5006)):
        self.prefer = prefer
        self.com = com
        self.baud = baud
        self.exe_path = exe_path
        self.dry = dry
        self.udp_addr = udp_addr
        self.ser = None
        if self.prefer=='serial':
            try:
                self.ser = serial.Serial(self.com,self.baud,timeout=0.05)
                time.sleep(0.05)
            except: self.ser=None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def send_move(self, dx, dy):
        dx_i = int(round(dx))
        dy_i = int(round(dy))
        cmd = f"M {dx_i} {dy_i}\n".encode()
        if self.dry: return
        if self.prefer=='serial' and self.ser: self.ser.write(cmd)
        elif self.prefer=='exe' and os.path.exists(self.exe_path):
            subprocess.Popen([self.exe_path,"M",str(dx_i),str(dy_i)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else: self.sock.sendto(cmd, self.udp_addr)

makcu = MakcuInterface(dry=True)

# ====== 游戏方案管理 ======
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE,'r') as f:
        game_profiles = json.load(f)
else:
    game_profiles = {}

def load_profile(name, window):
    if name in game_profiles:
        profile = game_profiles[name]
        for k,v in profile.items():
            if k in window.AllKeysDict: window[k].update(v)
        return profile
    return {}

def save_profile(name, window):
    profile = {k:window[k].get() for k in ['-EN-','-CONF-','-KP-','-KD-','-SM-','-MAX-','-ACTKEY-','-ACTMODE-','-MODEL-']}
    game_profiles[name] = profile
    with open(CONFIG_FILE,'w') as f:
        json.dump(game_profiles,f,indent=4)

# ====== UDP 接收线程 ======
latest_frame = None
running = True
def recv_thread():
    global latest_frame
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((STREAM_IP,STREAM_PORT))
    sock.settimeout(0.5)
    while running:
        try:
            data,_ = sock.recvfrom(UDP_MAX)
            t_sent,l = struct.unpack('dI', data[:12])
            jpg = data[12:12+l]
            arr = np.frombuffer(jpg,np.uint8)
            latest_frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except: continue
threading.Thread(target=recv_thread,daemon=True).start()

# ====== 鼠标按键激活 ======
aim_enabled = False
ACT_KEY = '右键'
ACT_MODE = '切换'
btn_map = {'左键':mouse.Button.left,'右键':mouse.Button.right,'侧键1':mouse.Button.x1,'侧键2':mouse.Button.x2}
def on_click(x,y,button,pressed):
    global aim_enabled
    if button != btn_map.get(ACT_KEY,None): return
    if ACT_MODE=='切换' and pressed:
        aim_enabled = not aim_enabled
        print(f"自动瞄准 {'启用' if aim_enabled else '禁用'}")
    elif ACT_MODE=='长按':
        aim_enabled = pressed
        print(f"自动瞄准 {'启用' if pressed else '禁用'}")
listener = mouse.Listener(on_click=on_click)
listener.start()

# ====== GUI ======
games = list(game_profiles.keys()) if game_profiles else ["默认游戏"]
layout = [
    [sg.Text("选择游戏"), sg.Combo(games,key='-GAME-',enable_events=True)],
    [sg.Button("保存方案")],
    [sg.Text("模型"), sg.Input(DEFAULT_MODEL,key='-MODEL-'), sg.Button("加载")],
    [sg.Checkbox("启用自动瞄准",default=True,key='-EN-')],
    [sg.Text("置信度"), sg.Slider(range=(0,100),default_value=40,orientation='h',key='-CONF-')],
    [sg.Text("KP"), sg.Slider(range=(0,500),default_value=80,orientation='h',key='-KP-'),
     sg.Text("KD"), sg.Slider(range=(0,200),default_value=12,orientation='h',key='-KD-')],
    [sg.Text("平滑"), sg.Slider(range=(0,100),default_value=60,orientation='h',key='-SM-')],
    [sg.Text("最大移动"), sg.Slider(range=(10,500),default_value=60,orientation='h',key='-MAX-')],
    [sg.Text("激活按键"), sg.Combo(['左键','右键','侧键1','侧键2'],default_value='右键',key='-ACTKEY-'),
     sg.Text("模式"), sg.Combo(['切换','长按'],default_value='切换',key='-ACTMODE-')],
    [sg.Checkbox("模拟模式(不发送鼠标)",default=True,key='-DRY-'),
     sg.Combo(['serial','exe','udp'], default_value='serial',key='-PREF-'),
     sg.Input('COM3',key='-COM-'), sg.Input('makcu.exe',key='-EXE-'), sg.Input('127.0.0.1:5006',key='-UDP-')],
    [sg.Image(filename='',key='-IMG-')],
    [sg.Text("",key='-STAT-')],
    [sg.Button("紧急停止",button_color=('white','red'))]
]
window = sg.Window("AI辅助瞄准副机", layout,location=(100,50),finalize=True)

# ====== 加载模型 ======
model = YOLO(DEFAULT_MODEL)

# ====== 简易卡尔曼 + PD ======
kalman = cv2.KalmanFilter(4,2)
kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]],np.float32)
kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]],np.float32)
last_error = np.array([0.0,0.0])
last_time = time.time()
smoothed_move = np.array([0.0,0.0])

# ====== 主循环 ======
while True:
    event, values = window.read(timeout=20)
    if event in (sg.WIN_CLOSED,): break
    if event=="紧急停止": values['-EN-']=False
    if event=='-GAME-': 
        profile = load_profile(values['-GAME-'],window)
        ACT_KEY = profile.get('-ACTKEY-',ACT_KEY)
        ACT_MODE = profile.get('-ACTMODE-',ACT_MODE)
    if event=='保存方案':
        game_name = values['-GAME-'] or "默认游戏"
        save_profile(game_name,window)
        if game_name not in games:
            games.append(game_name)
            window['-GAME-'].update(values=games,value=game_name)
        ACT_KEY = values['-ACTKEY-']
        ACT_MODE = values['-ACTMODE-']
    if event=="加载":
        try: model = YOLO(values['-MODEL-'])
        except: pass

    # 更新 MAKCU 设置
    makcu.dry = values['-DRY-']
    makcu.prefer = values['-PREF-']
    makcu.com = values['-COM-']
    makcu.exe_path = values['-EXE-']
    h,p = values['-UDP-'].split(':')
    makcu.udp_addr = (h,int(p))
    ACT_KEY = values['-ACTKEY-']
    ACT_MODE = values['-ACTMODE-']

    if latest_frame is None: continue
    frame = latest_frame.copy()
    h,w = frame.shape[:2]
    center = np.array([w/2,h/2])
    conf = values['-CONF-']/100.0

    # 推理
    boxes=[]
    try:
        res = model.predict(frame,conf=conf)
        for r in res:
            for b in r.boxes:
                x1,y1,x2,y2 = b.xyxy[0]
                cx,cy = (x1+x2)/2,(y1+y2)/2
                boxes.append([cx,cy])
    except: pass

    if boxes and values['-EN-'] and aim_enabled:
        target = np.array(boxes[0])
        # 卡尔曼
        measured = np.array([target[0],target[1]],np.float32)
        kalman.correct(measured)
        pred = kalman.predict()
        error = pred - center
        dt = max(time.time()-last_time,1e-3)
        dx = error[0]*values['-KP-']/100 - last_error[0]*values['-KD-']/100
        dy = error[1]*values['-KP-']/100 - last_error[1]*values['-KD-']/100
        dx = np.clip(dx, -values['-MAX-'], values['-MAX-'])
        dy = np.clip(dy, -values['-MAX-'], values['-MAX-'])
        last_error[:] = error
        last_time = time.time()
        makcu.send_move(dx,dy)

    # 更新 GUI 图像
    for cx,cy in boxes:
        cv2.circle(frame,(int(cx),int(cy)),5,(0,255,0),-1)
    imgbytes = cv2.imencode('.png',frame)[1].tobytes()
    window['-IMG-'].update(data=imgbytes)
    window['-STAT-'].update(f"目标数量: {len(boxes)}   自动瞄准: {'启用' if values['-EN-'] and aim_enabled else '禁用'}")

running = False
window.close()
