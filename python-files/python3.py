#!/usr/bin/env python3
# AutoKeyMouse v2 - Final
# Features:
# - ช่องใส่จำนวนรอบ (99 = ทำงานไม่หยุด)
# - กด F2 เพื่อจับตำแหน่งเมาส์
# - Hotkeys: F7 = Pause/Resume, F8 = Stop
# - รองรับรหัสพิเศษ (^ ! + {TAB} ฯลฯ)
# - คลิก / กดปุ่ม / พิมพ์ข้อความ + ตั้งดีเลย์ได้

import threading, time, re
import PySimpleGUI as sg
import pyautogui, keyboard

pyautogui.FAILSAFE = True

SPECIAL_KEYS = {
    'ENTER':'enter','ESC':'esc','TAB':'tab','SPACE':'space','BACKSPACE':'backspace','BS':'backspace',
    'DELETE':'delete','DEL':'delete','INS':'insert','INSERT':'insert',
    'HOME':'home','END':'end','PGUP':'pageup','PGDN':'pagedown',
    'UP':'up','DOWN':'down','LEFT':'left','RIGHT':'right',
    'F1':'f1','F2':'f2','F3':'f3','F4':'f4','F5':'f5','F6':'f6','F7':'f7','F8':'f8','F9':'f9',
    'F10':'f10','F11':'f11','F12':'f12',
}

def parse_hotkey_syntax(s):
    events, i, text_buffer = [], 0, []
    def flush_text():
        if text_buffer:
            events.append({'type':'text','text': ''.join(text_buffer)}); text_buffer.clear()
    while i < len(s):
        ch = s[i]
        if ch in '^!+':
            mod = {'^':'ctrl','!':'alt','+':'shift'}[ch]; i+=1
            if i>=len(s): text_buffer.append(ch); break
            if s[i]=='{':
                m = re.match(r'\{([A-Za-z0-9]+)(?:\s+(\d+))?\}', s[i:])
                if not m: text_buffer.append(ch); continue
                key, rep = SPECIAL_KEYS.get(m.group(1).upper(), m.group(1).lower()), int(m.group(2)) if m.group(2) else 1
                flush_text(); [events.append({'type':'press','keys':[mod,key]}) for _ in range(rep)]
                i += m.end()
            else:
                flush_text(); events.append({'type':'press','keys':[mod,s[i].lower()]}); i+=1
        elif ch=='{':
            m = re.match(r'\{([A-Za-z0-9]+)(?:\s+(\d+))?\}', s[i:])
            if not m: text_buffer.append('{'); i+=1; continue
            key, rep = SPECIAL_KEYS.get(m.group(1).upper(), m.group(1).lower()), int(m.group(2)) if m.group(2) else 1
            flush_text(); [events.append({'type':'press','keys':[key]}) for _ in range(rep)]
            i += m.end()
        else:
            text_buffer.append(ch); i+=1
    flush_text(); return events

def perform_hotkey_events(events, delay_between=0.01):
    for ev in events:
        if ev['type']=='text': pyautogui.write(ev['text'])
        elif ev['type']=='press': pyautogui.hotkey(*ev['keys']) if len(ev['keys'])>=2 else pyautogui.press(ev['keys'][0])
        time.sleep(delay_between)

class Runner:
    def __init__(self): self.stop_event, self.pause_event = threading.Event(), threading.Event()
    def stop(self): self.stop_event.set(); self.pause_event.clear()
    def toggle_pause(self): self.pause_event.clear() if self.pause_event.is_set() else self.pause_event.set()
    def run(self, actions, loop_count):
        count=0
        while (loop_count==99 or count<loop_count) and not self.stop_event.is_set():
            for a in list(actions):
                while self.pause_event.is_set() and not self.stop_event.is_set(): time.sleep(0.05)
                if self.stop_event.is_set(): break
                t, d = a['type'], int(a.get('delay',0))
                if t=='click': pyautogui.click(*a['position'],button=a.get('button','left'))
                elif t=='keypress': perform_hotkey_events(a['sequence'])
                elif t=='type': pyautogui.write(a['text'])
                time.sleep(d/1000.0) if d>0 else None
            count+=1

runner=Runner()
keyboard.add_hotkey('f7', runner.toggle_pause)
keyboard.add_hotkey('f8', runner.stop)

sg.theme('SystemDefault'); click_btns=['left','right','middle']
layout=[
 [sg.Text('จำนวนรอบ (99=ไม่หยุด):'), sg.Input('1',key='-LOOP-',size=(6,1))],
 [sg.Frame('คำสั่ง',[
   [sg.Text('ประเภท'), sg.Combo(['click','keypress','type'],default_value='click',key='-TYPE-',size=(10,1)),
    sg.Text('รายละเอียด'), sg.Input(key='-DETAIL-',size=(28,1)),
    sg.Text('ดีเลย์(ms)'), sg.Input('1000',key='-DELAY-',size=(7,1)), sg.Button('เพิ่ม',key='-ADD-')],
   [sg.Text('ปุ่มคลิก'), sg.Combo(click_btns,default_value='left',key='-BTN-',size=(8,1)),
    sg.Text('Tips: กด F2 เพื่อจับพิกัดเมาส์')]
 ])],
 [sg.Listbox(values=[],size=(70,12),key='-ACTIONS-',enable_events=True)],
 [sg.Button('เริ่มทำงาน',key='-START-',button_color=('white','green')),
  sg.Button('หยุด/ล้าง',key='-STOP-'), sg.Button('ลบรายการ',key='-DEL-'),
  sg.Text('Hotkey: F7=Pause, F8=Stop',text_color='blue')]
]
window=sg.Window('AutoKeyMouse v2 Final',layout,finalize=True); window.bind('<F2>','F2')
actions, worker_thread=[],None

def preview(): return [f'Click {a.get("button")}@{a["position"]} d={a["delay"]}ms' if a['type']=='click'
    else f'KeySeq: {a["raw"]} d={a["delay"]}ms' if a['type']=='keypress'
    else f'Type: \"{a["text"]}\" d={a["delay"]}ms' for a in actions]

try:
    while True:
        e,v=window.read(timeout=100)
        if e in (sg.WIN_CLOSED,None): runner.stop(); break
        if e=='F2': pos=pyautogui.position(); window['-DETAIL-'].update(f'{pos.x},{pos.y}')
        if e=='-ADD-':
            try: d=int(v['-DELAY-'])
            except: sg.popup('ดีเลย์ต้องเป็นตัวเลข'); continue
            t,detail=v['-TYPE-'],v['-DETAIL-'].strip()
            if t=='click':
                try: x,y=map(int,detail.split(',')); actions.append({'type':'click','position':(x,y),'button':v['-BTN-'],'delay':d})
                except: sg.popup('Click ต้องกรอก x,y เช่น 512,300 หรือกด F2'); continue
            elif t=='keypress':
                if not detail: sg.popup('กรอกรหัส เช่น ^a{TAB 4}!b'); continue
                seq=parse_hotkey_syntax(detail); actions.append({'type':'keypress','raw':detail,'sequence':seq,'delay':d})
            elif t=='type': actions.append({'type':'type','text':detail,'delay':d})
            window['-ACTIONS-'].update(preview()); window['-DETAIL-'].update('')
        if e=='-DEL-':
            idx=window['-ACTIONS-'].get_indexes(); 
            [actions.pop(i) for i in idx]; window['-ACTIONS-'].update(preview())
        if e=='-STOP-': runner.stop(); actions.clear(); window['-ACTIONS-'].update([])
        if e=='-START-':
            if worker_thread and worker_thread.is_alive(): sg.popup('กำลังทำงานอยู่ (กด F8 เพื่อหยุด)'); continue
            try: loop=int(v['-LOOP-']); 
            except: sg.popup('จำนวนรอบต้องเป็นตัวเลข หรือ 99=ไม่หยุด'); continue
            runner.stop_event.clear(); runner.pause_event.clear()
            worker_thread=threading.Thread(target=runner.run,args=(actions,loop),daemon=True); worker_thread.start()
            sg.popup_no_wait('เริ่มทำงานแล้ว! Hotkey: F7=Pause, F8=Stop')
finally: window.close()
