import sys
from PyQt5.QtWidgets import QApplication,QWidget,QGridLayout,QVBoxLayout,QCheckBox,QLineEdit,QPushButton,QLabel,QTextEdit,QSpinBox,QProgressBar
from PyQt5 import QtGui
from random import random
import json

def randomOrder_key(element):
    return random()

class mainWidget(QWidget):
  def __init__(self):
    QWidget.__init__(self)  

    self.readData()
    self.__maxKanji=50
    self.__lastKanji=10
    self.__maxKanjiStart=50
    self.__lastKanjiStart=10

    self.__vbox=QVBoxLayout()
    
    s='Всего кандзи '+str(len(self.__kanjiBase))
    for k in [5,4,3,2,1,0]:
      if self.__jlpt[k]:
         s+=' | N%s: %s'%(str(k),str(self.__jlpt[k]))
    s+=' | Слов %s'%str(len(self.__kanjiWords))     
    self.__allLabel=QLabel(s)
    self.__vbox.addWidget(self.__allLabel)
    
    self.__grid=QGridLayout()
    
    self.__kanjiCheckBox = QCheckBox()
    self.__kanjiLineEdit=QLineEdit()
    self.__kanjiLineEdit.setStyleSheet("font-size: 30px;")
    
    self.__keyLineEdit=QLineEdit()
    self.__keyLineEdit.setStyleSheet("font-size: 30px;")
    
    self.__kanaCheckBox = QCheckBox()
    self.__kanaTextEdit=QTextEdit()
    
    self.__rusCheckBox = QCheckBox()
    self.__rusTextEdit=QTextEdit()
    
    self.__wordsCheckBox = QCheckBox()
    self.__wordsTextEdit=QTextEdit()
    self.__wordsTextEdit.setWordWrapMode(QtGui.QTextOption.NoWrap)
    self.__wordsTextEdit.setStyleSheet("font-size: 20px;")
    
    self.__nextButton=QPushButton('Следующий')
    self.__prevButton=QPushButton('Предыдущий')
    self.__progress=QProgressBar()
    
    self.__maxSpin=QSpinBox()
    self.__lastSpin=QSpinBox()
    self.__maxSpin.setRange(10,len(self.__kanjiBase))
    self.__maxSpin.valueChanged.connect(self.maxSpinChanged)
    self.__maxSpin.setValue(50)
    self.__lastSpin.setRange(10,self.__maxSpin.value())
    self.__lastSpin.valueChanged.connect(self.lastSpinChanged)
    self.__startButton=QPushButton('Старт')
    

    self.__grid.addWidget(self.__kanjiCheckBox,0,0)
    self.__grid.addWidget(self.__kanjiLineEdit,0,1)
    self.__grid.addWidget(self.__keyLineEdit,0,2)
    
    self.__grid.addWidget(self.__kanaCheckBox,1,0)
    self.__grid.addWidget(self.__kanaTextEdit,1,1)
    
    self.__grid.addWidget(self.__rusTextEdit,1,2)
    self.__grid.addWidget(self.__rusCheckBox,1,3)
    
    self.__grid.addWidget(self.__nextButton,4,1)
    self.__grid.addWidget(self.__prevButton,5,1)
    self.__grid.addWidget(self.__progress,6,1)
    
    self.__grid.addWidget(self.__maxSpin,4,2)
    self.__grid.addWidget(self.__lastSpin,5,2)
    self.__grid.addWidget(self.__startButton,6,2)
    
    
    self.__grid.addWidget(self.__wordsTextEdit,7,1,7,2)
    self.__grid.addWidget(self.__wordsCheckBox,7,0)
    
    self.__vbox.addLayout(self.__grid)
    self.setLayout(self.__vbox)

    self.__kanjiCheckBox.setChecked(False)
    self.__kanaCheckBox.setChecked(False)
    self.__rusCheckBox.setChecked(True)
    self.__wordsCheckBox.setChecked(False)
    
    self.__kanjiCheckBox.toggled.connect(self.update)
    self.__kanaCheckBox.toggled.connect(self.update)
    self.__rusCheckBox.toggled.connect(self.update)
    self.__wordsCheckBox.toggled.connect(self.update)
    self.__nextButton.clicked.connect(self.nextClick)
    self.__prevButton.clicked.connect(self.prevClick)
    self.__startButton.clicked.connect(self.start)
    
    self.start()

  def setCurRec(self,value):
    self.__curRec=value
    self.__progress.setValue(self.__curRec)
  
  def incCurRec(self):
    if self.__curRec<(len(self.__data)-1):self.__curRec+=1
    else:self.__curRec=0
    self.__progress.setValue(self.__curRec)
  
  def decCurRec(self):
    if self.__curRec>0:self.__curRec-=1
    else:self.__curRec=len(self.__data)-1
    self.__progress.setValue(self.__curRec)
  
  def maxSpinChanged(self):
    self.__lastSpin.setMaximum(self.__maxSpin.value())
    self.__maxKanji=self.__maxSpin.value()

  def lastSpinChanged(self):
    self.__maxSpin.setMinimum(self.__lastSpin.value())
    self.__lastKanji=self.__lastSpin.value()

  def start(self):
    self.__lastKanjiStart=self.__lastKanji
    self.__maxKanjiStart=self.__maxKanji
    self.setData()
    self.__progress.setMinimum(0)
    self.__progress.setMaximum(self.__maxKanji)
    self.setCurRec(0)
    self.update()

  def nextRec(self):
    if (not(self.__data[self.__curRec]["kanji"] in self.__lastStr)) \
       and(not(self.__data[self.__curRec]["kanji"] in self.__displayed)):
      self.__displdict[self.__data[self.__curRec]["kanji"]]+=1
#      self.__displayed.append(self.__data[self.__curRec]["kanji"])
      self.__displayed+=self.__data[self.__curRec]["kanji"]
    print(self.__data[self.__curRec]["kanji"],self.__displdict[self.__data[self.__curRec]["kanji"]])
    self.incCurRec()
    self.__kanjiCheckBox.setChecked(False)
    self.__kanaCheckBox.setChecked(False)
    self.__wordsCheckBox.setChecked(False)
    self.update()

  def prevRec(self):
    self.decCurRec()
    self.__kanjiCheckBox.setChecked(False)
    self.__kanaCheckBox.setChecked(False)
    self.__wordsCheckBox.setChecked(False)
    self.update()
    
  def nextClick(self):
    self.nextRec()  
  
  def prevClick(self):
    self.prevRec()
    
  def update(self):
    if self.__kanjiCheckBox.isChecked():
      self.__kanjiLineEdit.setText(self.__data[self.__curRec]["kanji"]) 
      s=self.__keydata[self.__data[self.__curRec]["key"]]["key"]+' '+self.__keydata[self.__data[self.__curRec]["key"]]["val"]
      self.__keyLineEdit.setText(s)
    else:
      self.__kanjiLineEdit.clear()
      self.__keyLineEdit.clear()
    if self.__rusCheckBox.isChecked():self.__rusTextEdit.setText(self.__data[self.__curRec]["rus"])  
    else:self.__rusTextEdit.clear()
    if self.__kanaCheckBox.isChecked():self.__kanaTextEdit.setText(self.__data[self.__curRec]["kana"])  
    else:self.__kanaTextEdit.clear()
    if self.__wordsCheckBox.isChecked():
      s=''
      for kw in self.__kanjiWords:
        if self.__data[self.__curRec]["kanji"] in kw["onlykanji"]:
          s+="%s - %s - %s\n"%(kw["kanji"],kw["kana"],kw["rus"])
      self.__wordsTextEdit.setText(s)  
    else:self.__wordsTextEdit.clear()
    
    #if self.__romanCheckBox.isChecked():self.__romanLineEdit.setText(self.__data[self.__curRec]["romaji"])  
    #else:self.__romanLineEdit.clear()
    #if self.__kanaCheckBox.isChecked():self.__kanaLineEdit.setText(self.__data[self.__curRec]["kana"])  
    #else:self.__kanaLineEdit.clear()
    #if self.__kanjiCheckBox.isChecked():self.__kanjiLineEdit.setText(self.__data[self.__curRec]["kanji"])  
    #else:self.__kanjiLineEdit.clear()
    
    #self.__curRecLabel.setText('%s из %s'%(self.__curRec+1,self.__lenData))
    #self.__rightLabel.setText('%s'%(self.__right)) 

  def readData(self):
    keyfile=open("keys.json","r",encoding="utf-8")
    keysjson=json.load(keyfile)
    self.__keydata={}
    for k in keysjson:
      d={}
      d["key"]=k["key"]
      d["val"]=k["val"]
      self.__keydata[k["num"]]=d
    vocfile=open("kanji.json","r",encoding="utf-8")
    self.__kanjiBase=json.load(vocfile)
    
    self.__jlpt=[0,0,0,0,0,0]
    self.__displdict={}
    
    for kb in self.__kanjiBase:
      self.__jlpt[kb['jlpt']]+=1
      self.__displdict[kb['kanji']]=kb['display']
      kb['random']=random()
    
    wordsfile=open("allwords.json","r",encoding="utf-8")
    wordsjson=json.load(wordsfile)
    self.__kanjiWords=[]
    kanjistr=[kb['kanji'] for kb in self.__kanjiBase]
    
    for wj in wordsjson:
      inbase=1  
      for wjok in wj["onlykanji"]:
        if not(wjok in kanjistr):inbase=0
      if inbase:self.__kanjiWords.append(wj)
          
  def setData(self):
#    self.__displayed=[] 
    self.__displayed=''
    for kb in self.__kanjiBase:
      kb['display']=self.__displdict[kb['kanji']]
    data10=self.__kanjiBase[-self.__lastKanjiStart:]
    self.__lastStr=[d['kanji'] for d in data10]
    data40=sorted(self.__kanjiBase[:-self.__lastKanjiStart],key=lambda item:(item["display"],item["random"]))[:self.__maxKanjiStart-self.__lastKanjiStart]
    self.__data=sorted(data10+data40,key=randomOrder_key)
    self.__lenData=self.__maxKanjiStart
    
  def save(self):
    for kb in self.__kanjiBase:
      kb['display']=self.__displdict[kb['kanji']]
      del kb['random']
    with open("kanji.json", "w") as write_file:
      json.dump(self.__kanjiBase,write_file,indent=2,ensure_ascii=False)
    fd=open('displayed.txt','a')
    fd.write(self.__displayed+'\n')
      
  
  def closeEvent(self,event): 
    self.save()
    event.accept()  
   
app = QApplication(sys.argv)

mw = mainWidget()
mw.show()

sys.exit(app.exec_()) 
