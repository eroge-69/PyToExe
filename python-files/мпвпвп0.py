# importing libraries
from cProfile import label
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#import Csv
import sys

import random


keymap = {}
for key, value in vars(Qt).items():
    if isinstance(value, Qt.Key):
        keymap[value] = key.partition('_')[2]

modmap = {
    Qt.ControlModifier: keymap[Qt.Key_Control],
    Qt.AltModifier: keymap[Qt.Key_Alt],
    Qt.ShiftModifier: keymap[Qt.Key_Shift],
    Qt.MetaModifier: keymap[Qt.Key_Meta],
    Qt.GroupSwitchModifier: keymap[Qt.Key_AltGr],
    Qt.KeypadModifier: keymap[Qt.Key_NumLock],
}



class Window(QMainWindow,):

	ochislo = 0
	primer = 0


	def __init__(self):
		super().__init__()
		self.fraza = ''
		self.capybara = []
		self.prev_key = []
		# setting title
		self.setWindowTitle("Python ")

		# setting geometry
		self.setGeometry(100, 100, 400, 420)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

		# method for widgets

	#def caca(self):
			#self.e = 0
			#self.d = self.e
		#self.o = 0

	def UiComponents(self):

		# creating a label
		self.label = QLabel(self)

		# setting geometry to the label
		self.label.setGeometry(5, 45, 350, 35)

		# creating label multi line
		self.label.setWordWrap(True)

		# setting style sheet to the label
		self.label.setStyleSheet("QLabel"
								"{"
								"border : 4px solid black;"
								"background : white;"
								"}")

		# setting alignment to the label
		self.label.setAlignment(Qt.AlignRight)

		# setting font
		self.label.setFont(QFont('Arial', 15))



		# creating a label
		self.label1 = QLabel(self)

		# setting geometry to the label
		self.label1.setGeometry(5, 5, 350, 35)

		# creating label multi line
		self.label1.setWordWrap(True)

		# setting style sheet to the label
		self.label1.setStyleSheet("QLabel"
								"{"
								"border : 4px solid black;"
								"background : white;"
								"}")

		# setting alignment to the label
		self.label1.setAlignment(Qt.AlignRight)

		# setting font
		self.label1.setFont(QFont('Arial', 15))

		#push_point = QPushButton(".", self)

		# setting geometry
		#push_point.setGeometry(95, 300, 80, 40)

		# creating a label

		self.label2 = QLabel(self)

		# setting geometry to the label
		self.label2.setGeometry(275, 250, 80, 40)

		# creating label multi line
		self.label2.setWordWrap(True)

		# setting style sheet to the label
		self.label2.setStyleSheet("QLabel"
								"{"
								"border : 4px solid black;"
								"background : white;"
								"}")

		# setting alignment to the label
		self.label2.setAlignment(Qt.AlignRight)

		# setting font
		self.label2.setFont(QFont('Arial', 15))


		self.label3 = QLabel(self)

		# setting geometry to the label
		self.label3.setGeometry(275, 200, 80, 40)

		# creating label multi line
		self.label3.setWordWrap(True)

		# setting style sheet to the label
		self.label3.setStyleSheet("QLabel"
								"{"
								"border : 4px solid black;"
								"background : white;"
								"}")

		# setting alignment to the label
		self.label3.setAlignment(Qt.AlignRight)

		# setting font
		self.label3.setFont(QFont('Arial', 15))
		self.pokaz = False#True
		# adding number button to the screen
		# creating a push button
		push1 = QPushButton("1", self)

		# setting geometry
		push1.setGeometry(5, 150, 80, 40)

		# creating a push button
		push2 = QPushButton("2", self)

		# setting geometry
		push2.setGeometry(95, 150, 80, 40)

		# creating a push button
		push3 = QPushButton("3", self)

		# setting geometry
		push3.setGeometry(185, 150, 80, 40)

		# creating a push button
		push4 = QPushButton("4", self)

		# setting geometry
		push4.setGeometry(5, 200, 80, 40)

		# creating a push button
		push5 = QPushButton("5", self)

		# setting geometry
		push5.setGeometry(95, 200, 80, 40)

		# creating a push button
		push6 = QPushButton("6", self)

		# setting geometry
		push6.setGeometry(185, 200, 80, 40)

		# creating a push button
		push7 = QPushButton("7", self)

		# setting geometry
		push7.setGeometry(5, 250, 80, 40)

		# creating a push button
		push8 = QPushButton("8", self)

		# setting geometry
		push8.setGeometry(95, 250, 80, 40)

		# creating a push button
		push9 = QPushButton("9", self)

		# setting geometry
		push9.setGeometry(185, 250, 80, 40)

		# creating a push button
		push0 = QPushButton("0", self)

		# setting geometry
		push0.setGeometry(5, 300, 80, 40)

		# adding operator push button
		# creating push button
		push_equal = QPushButton("=", self)

		# setting geometry
		push_equal.setGeometry(275, 300, 80, 40)

		# adding equal button a color effect
		c_effect = QGraphicsColorizeEffect()
		c_effect.setColor(Qt.blue)
		push_equal.setGraphicsEffect(c_effect)

		push_max = QPushButton("MAX", self)

		# setting geometry
		push_max.setGeometry(185, 300, 80, 40)

		pushnastr = QPushButton('#',self)
		pushnastr.setGeometry(275, 150, 80, 40)


		# clear button
		push_clear = QPushButton("Clear", self)
		push_clear.setGeometry(5, 100, 200, 40)

		# del one character button
		push_del = QPushButton("Del", self)
		push_del.setGeometry(210, 100, 145, 40)


		#self.push_pri = QPushButton("pri", self)
		#self.push_pri.setGeometry(360, 100, 50, 40)
		# adding action to each of the button
		#self.push_pri.hide()
		#self.push_x= QPushButton("*", self)

		# setting geometry
		#self.push_x.setGeometry(360, 150, 50, 40)
		#self.push_x.hide()

		self.radio0 = QRadioButton('+',self)
		self.radio1 = QRadioButton('-', self)
		self.radio2 = QRadioButton('*', self)
		self.radio3 = QRadioButton('/', self)

		self.radio0.hide()
		self.radio1.hide()
		self.radio2.hide()
		self.radio3.hide()

		self.radio0.setGeometry(360, 140, 50, 40)
		self.radio1.setGeometry(360, 180, 50, 40)
		self.radio2.setGeometry(360, 220, 50, 40)
		self.radio3.setGeometry(360, 260, 50, 40)




		self.setStyleSheet('QRadioButton{'
						   'font-size:15px;'
						   'font-family: Arial;'
						   'pading: 10px;'
						   '}')




		push_equal.clicked.connect(self.action_equal)
		push0.clicked.connect(self.action0)
		push1.clicked.connect(self.action1)
		push2.clicked.connect(self.action2)
		push3.clicked.connect(self.action3)
		push4.clicked.connect(self.action4)
		push5.clicked.connect(self.action5)
		push6.clicked.connect(self.action6)
		push7.clicked.connect(self.action7)
		push8.clicked.connect(self.action8)
		push9.clicked.connect(self.action9)
		pushnastr.clicked.connect(self.action_nastr)
		push_clear.clicked.connect(self.action_clear)
		push_del.clicked.connect(self.action_del)
		#self.push_pri.clicked.connect(self.action_pri)
		push_max.clicked.connect(self.action_max)
		#self.push_x.clicked.connect(self.action_x)
		self.radio0.toggled.connect(self.actionVibor)
		self.radio1.toggled.connect(self.actionVibor)
		self.radio2.toggled.connect(self.actionVibor)
		self.radio3.toggled.connect(self.actionVibor)
	def action_equal(self):
		g = self.label1.text()
		if g == '':
			self.action_pri()
		else:

		#get the label text
			equation = self.label1.text()
		#
		# try:
		# 	# getting the ans

			ans = eval(equation)
			self.number = int(self.number)
			if int(self.label.text()) == ans:
			#self.label1.setText('Правильно')
				self.label.setText("")
				self.fraza = 'нет'
			else:
			#self.label1.setText('Неправильно')
				self.label.setText("")
				Window.ochislo = window.ochislo + 1
			#	Window.ochislo = str()
				self.label2.setText(str(Window.ochislo))
				self.fraza = 'да'
			Window.primer = Window.primer + 1
			o = sys.stdout
			with open('123123123.txt', 'a') as f:
				vrema = datetime.now()
				sys.stdout = f
				for i in range(1):
					print('время когда решены все примеры:',vrema,'Пример:',self.a,'максимальное значение:',self.max,'номер примера:',window.primer,' ошибка есть:',self.fraza)
			self.label3.setText(str(Window.primer))
			self.label.setText(self.action_pri())
			#self.label2 = int(self.label2)
			#self.label2.setText(self.o)
		#self.e = self.e + 1
		#self.label3.setText(self.e)
		#setting text to the label
		# 	self.label.setText(str(ans))
		#
		# except:
		# 	# setting text to the label
		# 	self.label.setText("Wrong Input")

		# Сохранить оригинальный `sys.stdout`


		#if Window.primer == 10:
			#o = sys.stdout
		# Перенаправить stdout в файл
			#with open('123123123.txt', 'a') as f:
				#vrema = datetime.now()
				#sys.stdout = f
				#for i in range(1):
					#print(' максимальное значение:',self.max,' всего примеров:',window.primer,' ошибок всего:',window.ochislo,'время когда решены все примеры:',vrema,'все максимальные значения:',self.capybara)
			#Window.primer = 0
			#Window.ochislo = 0
			#self.label2.setText(str(Window.ochislo))
			#self.label3.setText(str(Window.primer))
		# Восстановить стандартный вывод






	def action_max(self):
		self.max = int(self.label.text())
		#print(self.max)
		self.label.setText('')
		self.label1.setText('')
		self.capybara.append(self.max)
	def action0(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "0")

	def action1(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "1")

	def action2(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "2")

	def action3(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "3")

	def action4(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "4")

	def action5(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "5")

	def action6(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "6")

	def action7(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "7")

	def action8(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "8")

	def action9(self):
		# appending label text
		text = self.label.text()
		self.label.setText(text + "9")

	def action_clear(self):
		# clearing the label text
		self.label.setText("")

	def action_del(self):
		# clearing a single digit
		text = self.label.text()
		self.label.setText(text[:len(text)-1])
	def action_pri(self):
		if self.r1 == True:
			pervoeslagaemoe = random.randint(1,self.max)
			vtoroeslagaemoe = random.randint(1, pervoeslagaemoe)
			number = pervoeslagaemoe - vtoroeslagaemoe
			pervoeslagaemoe = str(pervoeslagaemoe)
			vtoroeslagaemoe = str(vtoroeslagaemoe)
			a = (pervoeslagaemoe + ' - ' + vtoroeslagaemoe)

		elif self.r0 == True:
			pervoeslagaemoe = random.randint(1,self.max)
			vtoroeslagaemoe = random.randint(1,self.max)
			number = pervoeslagaemoe + vtoroeslagaemoe
			pervoeslagaemoe = str(pervoeslagaemoe)
			vtoroeslagaemoe = str(vtoroeslagaemoe)
			a = (pervoeslagaemoe + ' + ' + vtoroeslagaemoe)
		# return number
		elif self.r2 == True:
			pervoeslagaemoe = random.randint(1, self.max)
			vtoroeslagaemoe = random.randint(1, self.max)
			number = pervoeslagaemoe * vtoroeslagaemoe
			pervoeslagaemoe = str(pervoeslagaemoe)
			vtoroeslagaemoe = str(vtoroeslagaemoe)
			a = (pervoeslagaemoe + ' * ' + vtoroeslagaemoe)
		elif self.r3 == True:
			self.c = False
			while self.c == False:
				pervoeslagaemoe = random.randint(1, self.max)
				vtoroeslagaemoe = random.randint(1,pervoeslagaemoe)
				number = pervoeslagaemoe%vtoroeslagaemoe
				if number == 0:
					self.c  = True
				else:
					self.c = False
			number = pervoeslagaemoe / vtoroeslagaemoe
			pervoeslagaemoe = str(pervoeslagaemoe)
			vtoroeslagaemoe = str(vtoroeslagaemoe)
			a = (pervoeslagaemoe + ' / ' + vtoroeslagaemoe)


		self.a = a
		self.number = number
		text = self.label1.text()
		self.label1.setText(a)




	def action_nastr(self):
		if self.pokaz == True:
			self.radio0.hide()
			self.radio1.hide()
			self.radio2.hide()
			self.radio3.hide()
			self.pokaz = False
			#self.setGeometry(100, 100, 400, 420)
		else:
			#self.setGeometry(100, 100, 430, 420)
			self.radio0.show()
			self.radio1.show()
			self.radio2.show()
			self.radio3.show()
			self.pokaz = True



	def actionVibor(self):
		if self.radio0.isChecked():
			self.r0 = True
			self.r1 = False
			self.r2 = False
			self.r3 = False
		elif self.radio1.isChecked():
			self.r0 = False
			self.r1 = True
			self.r2 = False
			self.r3 = False
		elif self.radio2.isChecked():
			self.r0 = False
			self.r1 = False
			self.r2 = True
			self.r3 = False

		elif self.radio3.isChecked():
			self.r0 = False
			self.r1 = False
			self.r2 = False
			self.r3 = True




	#def action_point(self):
		#self.e = 0
		#self.d = 0

    #def Vichitanie():!
        #


   # def Slojenie():


#create pyqt5 app

	def keyPressEvent(self, event):
		#_key, _keys = self.keyevent_to_string(event)
		# раскомментируйте строку  ниже, чтобы увидеть что происходит
		#print(f'------> {_key}, {event.text()}, {event.key()}, {_keys}')

		key = event.key()

		#if self.prev_key:
			#for k in self.prev_key:
				#k.setStyleSheet("")

		if key == Qt.Key_0:
			self.action0()
			# print(f'Нажали: {_key}')
			#self.W.setStyleSheet("background-color: #ccc; color: red;")
			#self.Ctrl.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.Ctrl, self.W]
		# ...
		elif key== Qt.Key_1:
			self.action1()
			# print(f'Нажали: {_key}')
			#self.W.setStyleSheet("background-color: #ccc; color: red;")
			#self.Alt.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.Alt, self.W]
		# ...
		elif key == Qt.Key_2:
			self.action2()
			# print(f'Нажали: {_key}')
			#self.W.setStyleSheet("background-color: #ccc; color: red;")
			#self.ShifL.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.ShifL, self.W]
		# ...

		elif key == Qt.Key_3:
			self.action3()
			# print('Нажали: w')
			#self.W.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.W, ]
		elif key == Qt.Key_4:
			self.action4()
			# print('Нажали: a')
			#self.A.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.A, ]
		elif key == Qt.Key_5:
			self.action5()
			# print('Нажали: s')
			#self.S.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.S, ]
		elif key == Qt.Key_6:
			self.action6()
			# print('Нажали: d')
			#self.D.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.D, ]
		# ...
		elif key == Qt.Key_7:
			self.action7()
			# print('Нажали: Escape')
			#self.esc.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.esc, ]
		elif key == Qt.Key_8:
			self.action8()
			# print('Нажали: Tab')
			#self.Tab.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.Tab, ]
		elif key == Qt.Key_9:
			self.action9()
			#print('Нажали: Backspace')
			#self.Backspace.setStyleSheet("background-color: #ccc; color: red;")
			#self.prev_key = [self.Backspace, ]

















App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())