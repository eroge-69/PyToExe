import sys
import PyQt4 
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtCore,QtGui
from PyQt4.QtGui  import *
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4.QtCore import QTimer
from  PyQt4  import uic
import fnmatch
import os 
from functools import partial
import signal
from T3 import Ui_MainWindow as gui_mainwin


import os,sys

from functools import partial

 # Import Qt modules
from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QProcess
from functools import partial
import fnmatch
import subprocess
RT_OUT_PATH ="./"

class Main(QtGui.QMainWindow):
	def initsettings(self,):
		self.button_dict = {'browse_oceb':	{'button':self.ui.BrowseFile,'bt':self.ocebfiles ,'finish':None} }								
		return 
	
	def FLAGS1(self,final):
		print "eneterd" 
		#settings_data = self.remapSettingsForBT(self.getInputFromSettings())
		cmd = "/opt/py27/bin/python  NAV_PARMETERS_DISPLAY.pyc "+"_ILDE_PDIS_RAW_"+str(1)
		self.initProcess(cmd,final)
		
		return	
	def ocebfiles(self,final):
		self.ui.filenamebox.clear()
		self.ocebfiles= fnmatch.filter(os.listdir('./'),"*LO"+"*.DAT")
		for n_t in range(0,len(self.ocebfiles),1):
			self.ui.filenamebox.addItem(str(self.ocebfiles[n_t]))
		return
	def colorbutton(self):
		color = QtGui.QColorDialog.getColor()
		self.ui.pdisLabelSettingColor.setStyleSheet("background-color: %s"%(color.name()))
		return
	def flags3(self,final):
		print self.ui.filenamebox.currentText()
		print final
		cmd = "python mil_extraction.pyc "+str(10)+" "+str(self.ui.filenamebox.currentText())+" "+"ClkCorr"
		rtn=self.initProcess(cmd,final)
		app.processEvents()
		return
		
	def bias(self,final):
		print self.ui.filenamebox.currentText()
		print final
		cmd = "python mil_extraction.pyc "+str(10)+" "+str(self.ui.filenamebox.currentText())+" "+"ClkBias"
		rtn=self.initProcess(cmd,final)
		app.processEvents()
		return
	def drift(self,final):
		print self.ui.filenamebox.currentText()
		print final
		cmd = "python mil_extraction.pyc "+str(10)+" "+str(self.ui.filenamebox.currentText())+" "+"ClkDrift"
		rtn=self.initProcess(cmd,final)
		app.processEvents()
		return
		
	def flags2(self,final):
		print self.ui.filenamebox.currentText()
		print final
		#cmd = "python line_plot.py "+"./ "+self.color+" 1 "+str(2)
		#cmd = "/opt/py27/bin/python  NAV_PARMETERS_DISPLAY.py "+RT_OUT_PATH+" "+self.color+" "+self.ui.filenamebox.currentText()
		#cmd = "/opt/py27/bin/python  NAV_PARMETERS_DISPLAY.py "+RT_OUT_PATH+""self.color
		cmd = "python mil_extraction.pyc "+str(10)+" "+str(self.ui.filenamebox.currentText())+" "+"flags2"
		rtn=self.initProcess(cmd,final)
		app.processEvents()
		return
	def flags4(self,final):
		print self.ui.filenamebox.currentText()
		print final
		#cmd = "python line_plot.py "+"./ "+self.color+" 1 "+str(2)
		#cmd = "/opt/py27/bin/python  NAV_PARMETERS_DISPLAY.py "+RT_OUT_PATH+" "+self.color+" "+self.ui.filenamebox.currentText()
		#cmd = "/opt/py27/bin/python  NAV_PARMETERS_DISPLAY.py "+RT_OUT_PATH+""self.color
		cmd = "python mil_extraction.py  "+str(9)+" "+str(self.ui.filenamebox.currentText())+" "+"flag3"
		rtn=self.initProcess(cmd,final)
		app.processEvents()
		return
	def commonStart(self):
		print "Please wait Request is in Process"
		return

	def commonFinish(self):
		print "finished"
		#self.ui.status.setText("")
		return
	
	def initProcess(self,cmd,final):
		
		self.program = cmd.split()[0]
		#print program,"HI"
		self.arguments =cmd.split()[1:]
		process = QProcess(self)
		print "command", self.program
		print "arguments",self.arguments
		process.started.connect(self.commonStart)

		try:
			process.finished.connect(self.commonFinish)
		except:
			print "Warning!!! Process called without a finish callback"

		#process.start(program,arguments)
		#print program
		#os.execv("mil_extraction.py",self.arguments)
		app.processEvents()
		#pid =process.startDetached(self.program,self.arguments)
		print (process.startDetached(cmd))
		return




	def connectUIButtons(self,ui_type,prop_type='browse_oceb'):
		self.color=self.ui.pdisLabelSettingColor.palette().color(QtGui.QPalette.Window).name()
		print self.color
		
		self.ui.pdisButtonSettingColor.clicked.connect(self.colorbutton)
		self.ui.BatchReceiverClock_3.clicked.connect(self.flags3)
		self.ui.BatchSatelliteClock_3.clicked.connect(self.flags4)
		self.ui.BatchSatelliteClock_2.clicked.connect(self.flags2)
		self.ui.BatchPreResidue_2.clicked.connect(self.bias)
		self.ui.BatchReceiverClock_2.clicked.connect(self.drift)
		
		for (button_name,button_prop) in self.button_dict.items():
			if(button_prop[ui_type] == None):
				button_prop['button'].setEnabled(False)
				continue

			button_prop['button'].setEnabled(True)

			try:
				button_prop['button'].clicked.disconnect()
			except:
				print button_name + " disconnect when changing to " + ui_type

			button_prop['button'].clicked.connect(partial(button_prop[ui_type],button_prop['finish']))

		return
								

	def __init__(self, parent=None):
		super(Main, self).__init__(parent)
		self.ui=gui_mainwin()
		self.ui.setupUi(self)
		self.initsettings();
		self.connectUIButtons('bt')
		app.processEvents()
		#self.ui.BatchSatelliteClock_3.clicked.connect(self.printing)
		return

	

def main(title):
	global app
	app = QtGui.QApplication(sys.argv)
	
	window=Main()
	window.setWindowTitle(title)
	window.show()
	app.processEvents()
     
	sys.exit(app.exec_())

if __name__ == "__main__":
	try:
		title = sys.argv[1]
	except:
		title = "DESIGNER"
	main(title)
			
