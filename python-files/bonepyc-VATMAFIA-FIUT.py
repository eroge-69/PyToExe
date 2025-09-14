global found  # inserted # CRACKED BY VXTMAFIA Sep 14 21:03
global c  # inserted # CRACKED BY VXTMAFIA Sep 14 21:03
global nwdone  # inserted # CRACKED BY VXTMAFIA Sep 14 21:03
global bot_active  # inserted # CRACKED BY VXTMAFIA Sep 14 21:03
global afterIDs  # inserted # CRACKED BY VXTMAFIA Sep 14 21:03
import hashlib
import sys
import json
import requests
import io
import contextlib
import time
import random
import os
import difflib
import webbrowser

from flask import Flask
# from keyauth import api  # comment out if unavailable

import pyautogui
from pyautogui import ImageNotFoundException
import easyocr
import numpy as np
import cv2

import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, BooleanVar, CENTER
import tkinter.font as tkFont

# Globals
bot_active = False
found = False
c = 0
nwdone = 0
afterIDs = []

app = Flask(__name__)

def getchecksum():
    md5_hash = hashlib.md5()
    script_path = sys.argv[0] if len(sys.argv) > 0 else __file__
    try:
        with open(script_path, 'rb') as f:
            md5_hash.update(f.read())
            return md5_hash.hexdigest()
    except Exception:
        return ''

# If keyauth is available, uncomment and use it
# keyauthapp = api(name='bonelzbot', ownerid='1G2HSbhoJL', secret='ec2ab983460bdd4248b60174008ea5f950238e4c9aed615b426995b823b181e0', version='1.1', hash_to_check=getchecksum())
# config = json.load(open('config.json', encoding='utf-8'))
# keyauthapp.license(config['key'])


def resourcePath(relativePath):
    """Return path to resource, compatible with dev and PyInstaller."""
    try:
        basePath = sys._MEIPASS
    except AttributeError:
        basePath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basePath, relativePath)


def schedule(delay_ms, func):
    """Schedule a tkinter after call and remember its id."""
    try:
        afterID = root.after(delay_ms, func)
        afterIDs.append(afterID)
        return afterID
    except Exception:
        return None


def cancelAllAfter():
    global afterIDs
    for afterID in list(afterIDs):
        try:
            root.after_cancel(afterID)
        except Exception:
            pass
    afterIDs = []


def startBot():
    global bot_active
    if bot_active:
        return
    bot_active = True
    writelog('Bot: on')
    startbutton.config(state='disabled')
    stopbutton.config(state='normal')
    if not initConfig():
        writelog('Initialization failed, stopping bot')
        stopBot()
    else:
        runBot()


def stopBot():
    global bot_active
    bot_active = False
    cancelAllAfter()
    writelog('Bot: off')
    try:
        startbutton.config(state='normal')
        stopbutton.config(state='disabled')
    except Exception:
        pass


def toggleBot(event=None):
    if bot_active:
        stopBot()
    else:
        startBot()


def writelog(*messages):
    line = ' '.join((str(m) for m in messages))
    try:
        logwidget.config(state='normal')
        logwidget.insert('end', line + '\n')
        logwidget.see('end')
        logwidget.config(state='disabled')
    except Exception:
        print(line)


def buttonDetectorRandomizer(bpath):
    try:
        buttonlocation = pyautogui.locateOnScreen(bpath, confidence=0.8)
    except ImageNotFoundException:
        buttonlocation = None
    except Exception:
        buttonlocation = None

    if buttonlocation:
        x = random.randint(buttonlocation.left, buttonlocation.left + buttonlocation.width)
        y = random.randint(buttonlocation.top, buttonlocation.top + buttonlocation.height)
        duration = random.uniform(0.2, 0.8)
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.click()
        writelog('Clicked button at', x, y)
    else:
        writelog('error: button not found', bpath)


def regionClickRandomizer(x, y, w, h):
    try:
        rx = random.randint(x, x + max(0, w))
        ry = random.randint(y, y + max(0, h))
        duration = random.uniform(0.2, 0.8)
        pyautogui.moveTo(rx, ry, duration=duration)
        pyautogui.click()
    except Exception as e:
        writelog('error: exception during region click', str(e))
        stopBot()


def scrollRandomizer(steps=None, delay_ms=200, finished=None):
    if steps is None:
        steps = random.randint(5, 8)
    step_amount = random.randint(19, 22)
    state = {'count': 0}

    def _step():
        if not bot_active:
            return
        pyautogui.scroll(-step_amount)
        state['count'] += 1
        if state['count'] >= steps:
            writelog('scroll ended')
            if finished:
                try:
                    finished()
                except Exception as e:
                    writelog('error in finished callback', e)
        else:
            schedule(delay_ms, _step)

    schedule(0, _step)


def numbersIdentifier(x, y, w, h):
    try:
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        img_np = np.array(screenshot)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
        resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        results = reader.readtext(resized, detail=0)
        for raw_text in results:
            raw_text = raw_text.replace(' ', '')
            digits = ''.join(filter(str.isdigit, raw_text))
            if len(digits) >= 1:
                try:
                    return int(digits)
                except ValueError:
                    continue
    except Exception:
        pass
    return 0


def waitForButtonAsync(bpath, callback):
    try:
        location = pyautogui.locateOnScreen(bpath, confidence=0.9)
    except Exception:
        location = None
    if location is not None:
        writelog('button found async')
        try:
            callback()
        except Exception as e:
            writelog('callback error', e)
    else:
        schedule(200, lambda: waitForButtonAsync(bpath, callback))


def clickWhiteResource(bpath, on_success):
    def is_white_text(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv, (0, 0, 215), (180, 30, 255))
        white_pixels = np.count_nonzero(white_mask)
        total_pixels = img.shape[0] * img.shape[1]
        return white_pixels > total_pixels * 0.02

    def is_red_text(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_pixels = np.count_nonzero(red_mask)
        total_pixels = img.shape[0] * img.shape[1]
        return red_pixels > total_pixels * 0.02

    try:
        found_btn = pyautogui.locateOnScreen(bpath, confidence=0.9)
    except Exception:
        found_btn = None

    if found_btn:
        regions = [{'name': 'Case2_Left', 'coords': (974, 811, 109, 22)},
                   {'name': 'Case2_Right', 'coords': (1132, 810, 108, 22)}]
        writelog('wall ring detected, changing search regions')
    else:
        regions = [{'name': 'Case1_Left', 'coords': (1053, 810, 108, 22)},
                   {'name': 'Case1_Right', 'coords': (1212, 809, 106, 22)}]
        writelog('no wall ring detected')

    def attempt():
        try:
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            for r in regions:
                x, y, w, h = r['coords']
                region_img = screenshot_cv[y:y + h, x:x + w]
                if region_img.size == 0:
                    continue
                if is_white_text(region_img) and (not is_red_text(region_img)):
                    cx = x + w // 2
                    cy = y + h // 2
                    pyautogui.moveTo(cx, cy, duration=0.2)
                    pyautogui.click()
                    writelog(f"Clicked on {r['name']} (white number)")
                    if on_success:
                        on_success()
                    return
            writelog('No white number found, retrying...')
            schedule(300, attempt)
        except Exception as e:
            writelog('clickWhiteResource error', e)
            schedule(500, attempt)

    attempt()


def upgradeWalls():
    global found, c
    c = 0
    found = False
    searchWallButton()


def searchWallButton():
    global c, nwdone, found
    writelog("Searching for 'Wall' word")
    if not bot_active:
        stopBot()
        return
    upgraderegion = (605, 114, 366, 577)
    try:
        screenshot = pyautogui.screenshot(region=upgraderegion)
        screenshot_np = np.array(screenshot)
        gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=0)
        results = reader.readtext(gray, detail=1)
    except Exception:
        results = []

    target = 'wall'
    for item in results:
        if isinstance(item, tuple) and len(item) >= 2:
            bbox, text = item[0], item[1]
        elif isinstance(item, list) and len(item) >= 2:
            bbox, text = item[0], item[1]
        else:
            continue
        cleaned_word = text.strip().lower()
        if not cleaned_word:
            continue
        words_to_check = [cleaned_word] + cleaned_word.split()
        match_found = False
        for w in words_to_check:
            if w == target or (difflib.get_close_matches(target, [w], n=1, cutoff=0.8) and (not w.startswith('h'))):
                match_found = True
                break
        if match_found:
            writelog(f'Match found: {cleaned_word}')
            try:
                tl, tr, br, bl = bbox
                x = int((tl[0] + br[0]) / 2)
                y = int((tl[1] + br[1]) / 2)
            except Exception:
                x, y = 0, 0
            center_x = upgraderegion[0] + x
            center_y = upgraderegion[1] + y
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            pyautogui.click()
            found = True
            schedule(700, lambda: clickWhiteResource(resourcePath('img/ringbutton.png'), lambda: schedule(1700, lambda: buttonDetectorRandomizer(resourcePath('img/confirmbutton.png')))))
            nwdone += 1
            schedule(5000, checkStorages)
            return

    if not found:
        if c >= 40:
            writelog("Error: 'wall' button not found after many attempts. Aborting.")
            stopBot()
            return
        if c == 0:
            try:
                pyautogui.moveTo(979, 151, duration=0.3)
            except Exception:
                pass
        try:
            pyautogui.scroll(-150)
        except Exception:
            pass
        c += 1
        writelog(f"Attempt {c}: 'wall' button not found, scrolling...")
        schedule(2000, searchWallButton)


def checkStorages():
    global nwdone
    try:
        if nwdone < nwvalue:
            writelog('checking storages')
            gstorage = numbersIdentifier(1628, 36, 197, 30)
            estorage = numbersIdentifier(1618, 122, 208, 30)
            writelog(gstorage, estorage)
            if estorage is None or gstorage is None:
                writelog('error: read failed, proceed attacking')
                runBot()
                return
            if estorage >= wcvalue * 2 or gstorage >= wcvalue * 2:
                writelog('enough resources to upgrade walls, proceed')
                buttonDetectorRandomizer(resourcePath('img/builderbutton.png'))
                schedule(1200, upgradeWalls)
            else:
                writelog('not enough resources to upgrade walls, proceed attacking')
                schedule(500, runBot)
        else:
            writelog(nwdone, ' walls done, turning off the bot...')
            stopBot()
    except Exception:
        writelog('checkStorages error')


def starBonusCheck():
    writelog('checking for star bonus')
    try:
        presence = pyautogui.locateOnScreen(resourcePath('img/starbonusok.png'), confidence=0.8)
    except Exception:
        presence = None
    if presence:
        buttonDetectorRandomizer(resourcePath('img/starbonusok.png'))
        writelog('star bonus collected')
    else:
        writelog('no star bonus to collect')


def waitBackHomeAndCheck(bpath):
    if not bot_active:
        stopBot()
        return
    try:
        match = pyautogui.locateOnScreen(bpath, confidence=0.8)
    except Exception:
        match = None
    if match:
        writelog('back home')
        schedule(1000, starBonusCheck)
        if wupcheck.get():
            if nwdone <= nwvalue:
                schedule(3500, checkStorages)
            else:
                writelog(nwdone, ' walls done, turning off the bot...')
                stopBot()
        else:
            schedule(5000, runBot)
    else:
        schedule(1000, lambda: waitBackHomeAndCheck(bpath))


def waitForButtonAndProceed(bpath):
    if not bot_active:
        stopBot()
        return
    try:
        match = pyautogui.locateOnScreen(bpath, confidence=0.8)
    except Exception:
        match = None
    if match:
        writelog('return button found, atk ended')
        click_x = random.randint(match.left + match.width // 4, match.left + 3 * match.width // 4)
        click_y = random.randint(match.top + 3 * match.height // 4, match.top + match.height - 2)
        pyautogui.moveTo(click_x, click_y, duration=0.2)
        pyautogui.click()
        waitBackHomeAndCheck(resourcePath('img/infobutton.png'))
    else:
        schedule(1000, lambda: waitForButtonAndProceed(bpath))


def clickInLine(x0, y0, x1, y1, p):
    interval = 0.1
    if p >= len(countsar):
        return
    if countsar[p] < 1:
        return
    if countsar[p] == 1:
        pyautogui.click(x=round(x0), y=round(y0))
    else:
        for i in range(countsar[p]):
            t = i / (countsar[p] - 1) if countsar[p] > 1 else 0
            xi = x0 + (x1 - x0) * t
            yi = y0 + (y1 - y0) * t
            pyautogui.click(x=round(xi), y=round(yi))
            time.sleep(interval)


def troopsPlacer():
    screenwidth, screenheight = pyautogui.size()
    center_x = screenwidth // 2
    center_y = screenheight // 2
    pyautogui.moveTo(center_x, center_y)

    def afterscroll():
        pyautogui.dragRel(0, -260, duration=0.5, button='left')
        writelog('start placing troops')
        x = 321
        for i in range(slotsvalue):
            pyautogui.moveTo(x, 1000, duration=0.2)
            pyautogui.click()
            x += 130
            if i + 1 == spellslotvalue:
                clickInLine(406, 223, 997, 621, i)
            clickInLine(225, 336, 866, 812, i)

    scrollRandomizer(finished=afterscroll)


def trophyDrop():
    screenwidth, screenheight = pyautogui.size()
    center_x = screenwidth // 2
    center_y = screenheight // 2
    pyautogui.moveTo(center_x, center_y)

    def afterscroll():
        pyautogui.dragRel(0, -260, duration=0.5, button='left')
        writelog('start placing a troop to drop')
        pyautogui.moveTo(321, 1000, duration=0.2); pyautogui.click()
        pyautogui.moveTo(219, 297, duration=0.4); pyautogui.click()
        regionClickRandomizer(29, 828, 166, 44)
        schedule(1000, lambda: regionClickRandomizer(1002, 623, 265, 85))
        schedule(2000, lambda: regionClickRandomizer(842, 879, 236, 89))

        def checkBackHome():
            bpath = resourcePath('img/infobutton.png')
            if not bot_active:
                stopBot()
                return
            try:
                match = pyautogui.locateOnScreen(bpath, confidence=0.8)
            except Exception:
                match = None
            if match:
                writelog('back home')
                runBot()
            else:
                schedule(1000, checkBackHome)
        schedule(2200, checkBackHome)

    scrollRandomizer(finished=afterscroll)


def scanLoop(gvalue, evalue, dvalue, timeout=10, stable_required=2):
    if not bot_active:
        return
    writelog('waiting clouds (OCR detection)')
    start_time = time.time()
    stable_reads = {'count': 0}

    def waitCloudsGone():
        if not bot_active:
            return
        g_read = numbersIdentifier(78, 125, 130, 30)
        e_read = numbersIdentifier(78, 173, 130, 30)
        d_read = numbersIdentifier(78, 219, 130, 30)
        if g_read > 0 or e_read > 0 or d_read > 0:
            stable_reads['count'] += 1
            if stable_reads['count'] >= stable_required:
                writelog('clouds gone, resources detected')
                doScan()
                return
        else:
            stable_reads['count'] = 0
        if time.time() - start_time > timeout:
            writelog('timeout waiting clouds, forcing scan')
            doScan()
            return
        schedule(500, waitCloudsGone)

    def doScan():
        if not bot_active:
            return
        g_read = numbersIdentifier(78, 125, 130, 30)
        e_read = numbersIdentifier(78, 173, 130, 30)
        d_read = numbersIdentifier(78, 219, 130, 30)
        writelog(f'gold: {g_read}\nelixir: {e_read}\ndark: {d_read}')
        if g_read >= gvalue and e_read >= evalue and d_read >= dvalue:
            writelog('enough resources to atk')
            troopsPlacer()
            schedule(8000, lambda: waitForButtonAndProceed(resourcePath('img/returnhomebutton.png')))
        else:
            writelog('not enough resources to atk, skipping')
            regionClickRandomizer(1658, 772, 232, 93)
            schedule(2000, lambda: scanLoop(gvalue, evalue, dvalue, timeout, stable_required))

    waitCloudsGone()


def startAttackSequence(gvalue, evalue, dvalue):
    writelog('starting attack sequence...')
    regionClickRandomizer(30, 904, 148, 142)
    schedule(1000, lambda: regionClickRandomizer(1257, 581, 246, 92))
    schedule(3000, lambda: scanLoop(gvalue, evalue, dvalue))


def runBot():
    global spellslotvalue, countsar, slotsvalue
    if not bot_active:
        return
    try:
        gvalue = int(ginput.get())
        evalue = int(einput.get())
        dvalue = int(dinput.get())
        if gvalue < 0 or dvalue < 0 or evalue < 0:
            writelog('error: a value is negative')
            stopBot()
            return
    except Exception:
        writelog('error: invalid loot thresholds')
        stopBot()
        return

    try:
        s_counts = countsslotinput.get().strip()
        countsar = [int(x) for x in s_counts.split()] if s_counts else []
    except Exception:
        writelog('error: counts per slot not valid')
        stopBot()
        return

    try:
        slotsvalue = int(slotsinput.get())
        if slotsvalue <= 0:
            writelog('error: slots value is negative or 0')
            stopBot()
            return
    except Exception:
        writelog('error: slots value invalid')
        stopBot()
        return

    try:
        spellslotvalue = int(spellslotinput.get())
        if spellslotvalue < 0:
            writelog('error: spell-slot value is negative')
            stopBot()
            return
    except Exception:
        spellslotvalue = 0

    try:
        if tdropcheck.get():
            trophies = numbersIdentifier(117, 139, 67, 28)
            if 4900 < trophies < 5000:
                writelog('starting to drop trophies')
                regionClickRandomizer(30, 904, 148, 142)
                schedule(1000, lambda: regionClickRandomizer(1257, 581, 246, 92))
                start_time = time.time()
                stable_reads = {'count': 0}
                stable_required = 2
                def waiter():
                    if not bot_active:
                        return
                    g_read = numbersIdentifier(78, 125, 130, 30)
                    e_read = numbersIdentifier(78, 173, 130, 30)
                    d_read = numbersIdentifier(78, 219, 130, 30)
                    if g_read > 0 or e_read > 0 or d_read > 0:
                        stable_reads['count'] += 1
                        if stable_reads['count'] >= stable_required:
                            trophyDrop()
                            return
                    else:
                        stable_reads['count'] = 0
                    schedule(500, waiter)
                writelog('waiting clouds (OCR detection)')
                waiter()
                return
    except Exception:
        pass

    startAttackSequence(gvalue, evalue, dvalue)


def initConfig():
    global wcvalue, nwvalue, nwdone
    nwdone = 0
    try:
        if wupcheck.get():
            wcvalue = int(wcinput.get())
            if wcvalue <= 0:
                writelog('error: wall upgrade cost value is negative or 0')
                stopBot()
                return False
    except Exception:
        wcvalue = 0
    try:
        val = nwinput.get().strip()
        nwvalue = int(val) if val != '' else 500
        if nwvalue <= 0:
            writelog('error: n. walls value is negative')
            return False
    except Exception:
        nwvalue = 500
    return True


def showWallCostInfo():
    messagebox.showinfo('Wall Cost Info', 'Insert the cost of a wall upgrade')


def showNumbWallInfo():
    messagebox.showinfo('n. Walls info', 'Insert the number of walls you want to upgrade\n\n(IF LEFT EMPTY IT WILL UPGRADE EVERY WALL)')


def showSlotsInfo():
    messagebox.showinfo('Slots info', 'Insert the number of slots you are using in your army to a max of 11')


def showCountsSlotInfo():
    messagebox.showinfo('Counts per Slot info', 'Insert the counts of every slot')


def showSpellSlotInfo():
    messagebox.showinfo('Spell-Slot info', 'Insert the spell slot')


def showGoldInfo():
    messagebox.showinfo('Gold Threshold info', 'Insert the minimum amount of gold you want to attack for')


def showElixirInfo():
    messagebox.showinfo('Elixir Threshold info', 'Insert the minimum amount of elixir you want to attack for')


def showDarkInfo():
    messagebox.showinfo('Dark Elixir Threshold info', 'Insert the minimum amount of dark elixir you want to attack for')


def openDiscord(event):
    webbrowser.open_new('https://discord.gg/rtMSPx5EkC')

# GUI
root = tk.Tk()
root.geometry('440x260')
root.minsize(440, 260)
root.attributes('-topmost', True)
root.title('BONELZBOT v0.2.1')
try:
    icon = tk.PhotoImage(file=resourcePath('img/icon.png'))
    root.iconphoto(True, icon)
except Exception:
    pass

reader = easyocr.Reader(['en'], gpu=False)

frm = ttk.Frame(root, padding=10)
frm.grid(sticky='nsew')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frm.grid_columnconfigure(0, weight=1)
frm.grid_columnconfigure(1, weight=1)
frm.grid_rowconfigure(0, weight=1)
frm.grid_rowconfigure(1, weight=1)

style = ttk.Style()
style.configure('.', font=('TkDefaultFont', 9))
font_name = style.lookup('TLabelframe.Label', 'font')
if isinstance(font_name, tuple):
    font_name = font_name[0]
elif isinstance(font_name, str):
    font_name = font_name.split()[0]

try:
    default_font = tkFont.nametofont(font_name)
    bold_font = default_font.copy()
    bold_font.configure(weight='bold', size=9)
    style.configure('Bold.TLabelframe.Label', font=bold_font)
except Exception:
    pass

basicconfig = ttk.LabelFrame(frm, text='BASIC CONFIG', borderwidth=2, relief='ridge', style='Bold.TLabelframe')
basicconfig.grid(column=0, row=0, sticky='nsew')
ttk.Label(basicconfig, text='Slots (1-11): ').grid(column=0, row=0, sticky='w')
slotsinput = ttk.Entry(basicconfig)
slotsinput.grid(column=1, row=0)
infobutton = tk.Button(basicconfig, text='i', command=showSlotsInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=0, column=2, padx=(2, 0))
ttk.Label(basicconfig, text='Counts per Slot: ').grid(column=0, row=1, sticky='w')
countsslotinput = ttk.Entry(basicconfig)
countsslotinput.grid(column=1, row=1)
infobutton = tk.Button(basicconfig, text='i', command=showCountsSlotInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=1, column=2, padx=(2, 0))
ttk.Label(basicconfig, text='Spell-Slot: ').grid(column=0, row=2, sticky='w')
spellslotinput = ttk.Entry(basicconfig)
spellslotinput.grid(column=1, row=2)
infobutton = tk.Button(basicconfig, text='i', command=showSpellSlotInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=2, column=2, padx=(2, 0))
tdropcheck = BooleanVar(value=True)
tdropenabling = ttk.Checkbutton(basicconfig, text='Enable Trophy Drop', variable=tdropcheck, onvalue=True, offvalue=False, takefocus=0)
tdropenabling.grid(column=0, row=4, columnspan=2, sticky='w')

lootthresholds = ttk.LabelFrame(frm, text='LOOT THRESHOLDS', borderwidth=2, relief='ridge', style='Bold.TLabelframe')
lootthresholds.grid(column=1, row=0, sticky='nsew')
ttk.Label(lootthresholds, text='Gold ≥ ').grid(column=0, row=0, sticky='w')
ginput = ttk.Entry(lootthresholds)
ginput.grid(column=1, row=0)
ginput.insert(0, '800000')
infobutton = tk.Button(lootthresholds, text='i', command=showGoldInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=0, column=2, padx=(2, 0))
ttk.Label(lootthresholds, text='Elixir ≥ ').grid(column=0, row=1, sticky='w')
einput = ttk.Entry(lootthresholds)
einput.grid(column=1, row=1)
einput.insert(0, '800000')
infobutton = tk.Button(lootthresholds, text='i', command=showElixirInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=1, column=2, padx=(2, 0))
ttk.Label(lootthresholds, text='Dark ≥ ').grid(column=0, row=2, sticky='w')
dinput = ttk.Entry(lootthresholds)
dinput.grid(column=1, row=2)
dinput.insert(0, '10000')
infobutton = tk.Button(lootthresholds, text='i', command=showDarkInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=2, column=2, padx=(2, 0))

wallupgrade = ttk.LabelFrame(frm, text='WALL UPGRADE', borderwidth=2, relief='ridge', style='Bold.TLabelframe')
wallupgrade.grid(column=0, row=1, sticky='nsew')
wupcheck = BooleanVar(value=True)
wallupenabling = ttk.Checkbutton(wallupgrade, text='Enable Wall Upgrade', variable=wupcheck, onvalue=True, offvalue=False, takefocus=0)
wallupenabling.grid(column=0, row=0, columnspan=2, sticky='w')
infobutton = tk.Button(wallupgrade, text='i', command=showWallCostInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=1, column=2, padx=(2, 0))
ttk.Label(wallupgrade, text='Wall Cost: ').grid(column=0, row=1, sticky='w')
wcinput = ttk.Entry(wallupgrade)
wcinput.grid(column=1, row=1, padx=(30, 0))
infobutton = tk.Button(wallupgrade, text='i', command=showNumbWallInfo, font=('Arial', 9, 'bold'), bd=0, highlightthickness=0, relief='flat', cursor='hand2')
infobutton.grid(row=2, column=2, padx=(2, 0))
ttk.Label(wallupgrade, text='n. Walls: ').grid(column=0, row=2, sticky='w')
nwinput = ttk.Entry(wallupgrade)
nwinput.grid(column=1, row=2, padx=(30, 0))
ttk.Label(wallupgrade, text='Support Discord for any problem:', font=('Helvetica', 8, 'italic'), anchor=CENTER).grid(column=0, row=3, sticky='nsew', columnspan=2)
discord_link = tk.Label(wallupgrade, text='https://discord.gg/rtMSPx5EkC', fg='blue', cursor='hand2', font=('Helvetica', 8, 'italic', 'underline'), anchor=CENTER)
discord_link.grid(column=0, row=4, sticky='nsew', columnspan=2)
discord_link.bind('<Button-1>', openDiscord)

controllog = ttk.LabelFrame(frm, text='CONTROL & LOG', borderwidth=2, relief='ridge', style='Bold.TLabelframe')
controllog.grid(column=1, row=1, sticky='nsew')
startbutton = ttk.Button(controllog, text='Start Bot', command=toggleBot, takefocus=0)
stopbutton = ttk.Button(controllog, text='Stop Bot', command=toggleBot, takefocus=0)
startbutton.grid(column=0, row=0)
stopbutton.grid(column=1, row=0)
stopbutton.config(state='disabled')
logfrm = ttk.Frame(controllog, height=80, width=190, relief='ridge')
logfrm.grid(column=0, row=2, columnspan=2, pady=2, sticky='nsew')
logfrm.grid_propagate(False)
logwidget = scrolledtext.ScrolledText(logfrm, wrap='word', height=6, width=31, font=('Courier', 7), state='disabled')
logwidget.pack(expand=True, fill='both')

root.mainloop()
