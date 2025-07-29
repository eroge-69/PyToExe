from __future__ import print_function
from collections import defaultdict 
from xml.etree import cElementTree as ET 
from tkinter import * 
from tkinter import filedialog 
from queue import Queue 
from random import shuffle
from concurrent.futures import ThreadPoolExecutor 
from datetime import datetime 
import urllib.request, os, time, sys, asyncio, threading, itertools, math 
def ParseXML(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(ParseXML, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
def Loading():
    print("Im Trying my best here...")
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
def multithreadDownload():
    global download
    global downloadQueue
    while not downloadQueue.empty():
        image = downloadQueue.get() 
        imageName = image.replace("https://img.rule34.xxx/images/", "").replace("/", "_")
        imageName = imageName.replace("https:__rule34.xxx_images_", "")
        name  = "{}/{}/{}".format(dirname, SearchTerm, imageName)
        if not os.path.isfile(name):
            try:    
                urllib.request.urlretrieve(image, name)
            except:
                pass 
        download +=1
        downloadQueue.task_done() 
    return
def downloading():
    """Gives the user a simple progress bar"""
    global download
    global total
    global threads
    while download != total:
        prog_bar_str = ''
        percentage = 0.0
        progress_bar = 50
        percentage = download / total
        for i in range(progress_bar):
            if (percentage < 1 / progress_bar * i):
                prog_bar_str += '_' 
            else:
                prog_bar_str += '■'
        clear()
        print("Downloading {} files using {} threads".format(total, threads))
        uprint(prog_bar_str)
        print("{}/{} downloaded".format(download, total))
        print(SearchTerm)
        time.sleep(0.1)
def Main():
    global total
    global pages
    global imgList
    global SearchTerm
    global dirname
    global Ready
    dirname = inputdirname
    ready = True
    url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={}".format(SearchTerm)
    pid = 0
    if os.path.isfile("{}/{}/cachedsearch.r34".format(dirname, SearchTerm)):
        print("Found an inprogress download...\n\nResuming")
        f = open(("{}/{}/cachedsearch.r34".format(dirname, SearchTerm)), "r")        
        imgList = f.read()
        imgList = imgList.splitlines()
        total = len(imgList)
        pages = int(total / 100)
        f.close()
        time.sleep(1)
        Download()
    else:
        if (not urlCheck(url)): 
            clear()
            print("No results")
            time.sleep(2)
            clear()
        else:
            clear()
            Process(url)
            clear()
            download = "y"
            shorter = "y"

            if "y" in shorter.lower():
                Download()
            else:
                return
def urlCheck(url):
    try: 
        raw =  ET.XML(urllib.request.urlopen(url).read())
        parsed = ParseXML(raw) 
        if parsed['posts']['@count'] == "0":
            return False
        else:
            return True
    except:
        return False
def Process(url): 
    global total
    global pages
    global imgList
    print("Stand by...")
    imgList = []
    PID = 0
    t = True
    cachedCount = 0
    while t:
        tempURL = "{}&pid={}".format(url, PID)
        raw =  ET.XML(urllib.request.urlopen(tempURL).read())
        raw = ParseXML(raw)
        if cachedCount == 0:
            cachedCount = raw['posts']['@count']
        clear()
        print("Standy by...\n\nFound {} pages\nFound {} images\nExpecting {} images".format(PID, len(imgList), cachedCount)) 
        
        if len(imgList) >= int(raw['posts']['@count']):
            t = False 
        else:
            for data in raw['posts']['post']:
                imgList.append(str(data['@file_url']))
            PID = PID +1
    pages = PID 
    total = len(imgList)
def Download():
    global total
    global pages
    global imgList
    global SearchTerm
    global dirname
    global download
    global downloadQueue
    global threads
    clear()
    print("Writing backup file in case of unexcpected close... (lets the program resume in the event of an error)")
    if not (os.path.exists("{}/{}".format(dirname, SearchTerm))):
        os.mkdir("{}/{}".format(dirname, SearchTerm))
    f = open(("{}/{}/cachedsearch.r34".format(dirname, SearchTerm)), "w")
    urlList = ""
    for url in imgList:
        urlList += url + "\n"
    f.write(urlList)
    f.close()
    time.sleep(3)
    clear()
    start_time = datetime.now()
    download = 0
    threads = threadwant 
    downloadQueue = Queue()
    for image in imgList: 
        downloadQueue.put(image)    
    t = threading.Thread(target=downloading)
    t.start()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.submit(multithreadDownload)
    downloadQueue.join()
    if t.isAlive:
        t.join()
    end_time = datetime.now()
    clear() 
    print("Download complete")
    print("Downloaded {}/{} images".format(download, total))
    print('Download time: {}'.format(end_time - start_time))
    os.unlink("{}/{}/cachedsearch.r34".format(dirname, SearchTerm))
    time.sleep(3)

salmonella = "b"
while salmonella != "a":
    january = input("do you want to run the archive list or the taglist (A OR T) :")
    if january.lower() == "t":
        f = open("Taglist.txt", "r")
        salmonella = "a"

    elif january.lower() == "a":
        f = open("ArchiveTagList.txt", "r")
        salmonella = "a"
        
contents = f.read()
contents = str(contents)
currentData = contents.split()
f.close()
root = Tk()
root.withdraw() #get rid of that ugly tkinter window 
inputdirname = filedialog.askdirectory(parent=root, initialdir="/", title='Please select a download location')
threadwant = int(input("How many threads do you want (cores x 2) : "))
tagsdone = 0
dan = len(currentData)
xenoblade = "a"
tagsdonenextloop = 0
while tagsdone != dan:
    print("directory : ",inputdirname)
    time.sleep(3)
    mythra = currentData[tagsdone]
    tagsdone += 1
    SearchTerm = str(mythra)
    f=open("LastTagBeforeCrash.txt","w")
    health = str(SearchTerm)
    f.write(health)
    f.close()
    print("downloading :",SearchTerm)
    time.sleep(3)
    dirname = SearchTerm
    global Ready
    Ready = False
    t = threading.Thread(target=Loading)
    t.start()
    Main() #And so begins the storm of porn
