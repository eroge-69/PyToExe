
import numpy as np
import math
pi=np.pi
MaterialList=["BeCu","TBC","A+","BC","TWH","UWH","WH", "MWH","ReW","TW","UW","W","G+","TBC-C"]
YoungList=[13000,13000,11900,13000,35000,35000,35000,35000,35000,34000,34000,34000,34000,13000]
fix_coeff=[0.01,0.01,0.003,0.01,0.005,0.005,0.005,0.005,0.005,0.005,0.005,0.005,0.003,0.005]
length_list=list(np.arange(100,800,50))
fric_coeff_list=[1,0.96,0.93,0.9,0.87,0.85,0.8,0.78,0.77,0.76,0.74,0.73,0.72,0.7]
class ProbeProperty():
    #dia针径， tip_dia针尖径, layer层, moment力臂,length针长,tip_angle尖角度

    def __init__(self, dia, contact_angle ,length, tip_dia, angle, moment, taper_length, OD, material):
        
        self.length=length
        self.dia=dia
        self.tip_dia=tip_dia
        self.moment=moment
        self.angle=angle
        self.contact_angle=contact_angle
        self.OD=OD
        self.taper_length=taper_length
        self.material=material
        #compute bending angle
        self.bend_angle=angle+contact_angle
        #compute tip_angle
        self.tip_angle=2*np.atan((dia/2)/taper_length)
        
    def compute_taper(self):
        #Unit Convert
        dia=self.dia*25.4/1000
        tip_dia=self.tip_dia*25.4
        tip_angle=self.tip_angle
        length=self.length*25.4
        if self.material != "TBC-C":
            self.taper=((dia*1000-tip_dia)/2)/np.tan(tip_angle/2)-length/np.cos(13/180*pi)+length*np.tan(tip_angle/2+13*pi/180)
            self.taper=self.taper/1000
        else:
            tip_angle=tip_angle+0.3/180*pi
            
            self.taper=((dia*1000-tip_dia)/2)/np.tan(tip_angle/2)-length/np.cos(13/180*pi)+length*np.tan(tip_angle/2+13*pi/180)
            self.taper=self.taper/1000
          
    def test(self, pitch, layer):
        self.layer=layer
        dia=self.dia
        self.parallel_test=pitch*layer-dia*25.4
        self.parallel_res=(self.parallel_test>3*25.4)
        self.diamond_test=pitch*layer*np.cos(pi/4)-dia*25.4
        self.diamond_res=(self.diamond_test>3*25.4)
    def lean_test(self,real_size, pin_number,enter_angle):
        layer=self.layer
        dia=self.dia
        taper=self.taper
        self.lean=(real_size+2*taper*1000*np.sin(enter_angle/180*pi))/pin_number*layer-dia*25.4
        self.lean_test_res=(self.lean>3*25.4)
    def compute_bend_tip(self):
        length=self.length*25.4
        tip_angle=self.tip_angle
        bend_angle=self.bend_angle/180*pi
        tip_dia=self.tip_dia*25.4
        bend=[0,0]
        mat=self.material
        coeff=fix_coeff[MaterialList.index(mat)]*1000
        if self.material != "TBC-C":
            self.bend_tip_length=math.ceil(length/np.cos(tip_angle/2+bend_angle-pi/2))
        else:
            tip_angle=tip_angle+0.3/180*pi
            self.bend_tip_length=math.ceil(length/np.cos(tip_angle/2+bend_angle-pi/2))
        bend_tip_length=self.bend_tip_length
        if self.material != "TBC-C":
            bend[0]=math.ceil(2*bend_tip_length*np.tan(tip_angle/2)+tip_dia)+coeff
            bend[1]=2*bend_tip_length*np.tan(tip_angle/2)+tip_dia+2.9+coeff
            bend[1]=bend[1]-bend[1]%5
        else:
            tip_angle=tip_angle+0.3/180*pi
            bend[0]=math.ceil(2*bend_tip_length*np.tan(tip_angle/2)+tip_dia)+coeff
            bend[1]=2*bend_tip_length*np.tan(tip_angle/2)+tip_dia+2.9+coeff
            bend[1]=bend[1]-bend[1]%5
        self.bend=bend
    def compute_wantou(self, compensation):
        if self.dia*1000>self.bend[0]:
            if compensation:
                self.wantou=self.bend[1]/1000
            else:
                self.wantou=self.bend[0]/1000
        else:
            self.wantou=None
        if self.wantou != None:
            self.wantou_fixed=self.wantou-fix_coeff[MaterialList.index(self.material)]
    def compute_pressure(self):
        dia=self.dia*25.4/1000
        self.square=pi*(dia**4)/64
        OD=self.OD*25.4
        moment=self.moment*25.4
        y=YoungList[MaterialList.index(self.material)]
        self.pressure=(3*y*self.square*OD)/(self.taper**3*(dia/self.wantou_fixed-1)+(moment/1000)**3)
        #front_length先端长
    def compute_scrub(self,perp, BC):
        slide={"Before":0,"Perp":0,"BC":0}
        front_length=self.length*25.4-self.length*25.4%50
        if front_length>750:
            mu=0.7
        else:
            mu=fric_coeff_list[length_list.index(front_length)]
            
        self.front_length=front_length
        self.mu=mu
        wantou=self.wantou


        moment=self.moment*25.4
        OD=self.OD*25.4
        angle=self.angle/180*pi
        length=self.length*25.4

        slide['Perp']=mu*(((moment*np.tan(angle)+length+500*wantou)**2+moment**2-(moment*np.tan(angle)+length+500*wantou-OD)**2)**0.5-moment)
        slide['Before']=slide['Perp']/mu
        if length>750:
            slide['BC']=0.3*slide['Perp']
        else:
            slide['BC']=(-0.001*length+1.15)*slide['Perp']
        if perp:
            if BC:
                self.scrub=slide['BC']
            else:
                self.scrub=slide['Perp']
        else:
            self.scrub=slide['Before']
        self.slide=slide
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout,QWidget,QHBoxLayout,QCheckBox,QLabel,QListWidget
class TestResDisplay(QWidget):
    def __init__(self,prop):
        super().__init__()
        layout=QVBoxLayout()
        print(f"{prop.parallel_res}{prop.diamond_res}{prop.lean_test_res}")
        if prop.parallel_res:
            layout.addWidget(QLabel(f"平行进针: {round(prop.parallel_test,3)} um, OK"))
        else:
            layout.addWidget(QLabel(f"平行进针: {round(prop.parallel_test,3)} um, NG"))

        if prop.diamond_res:
            layout.addWidget(QLabel(f"菱形进针: {round(prop.diamond_test,3)} um, OK"))
        else:
            layout.addWidget(QLabel(f"菱形进针: {round(prop.diamond_test,3)} um, NG"))

        if prop.lean_test_res:
            layout.addWidget(QLabel(f"斜向拉针: {round(prop.lean,4)} um, OK"))
        else:
            layout.addWidget(QLabel(f"斜向拉针: {round(prop.lean,4)} um, NG"))
        
        self.setLayout(layout)
class TestWindow(QWidget):
    def __init__(self,prop):
        super().__init__()
        self.w=None
        self.property=prop
        layout_top=QHBoxLayout()
        layout_top.addWidget(QLabel("平行菱形测试参数"))
        
        layout_top.addWidget(QLabel("斜向测试参数"))
        top_widget=QWidget()
        top_widget.setLayout(layout_top)
        layout_bot=QHBoxLayout()
        widget_0=QLineEdit()
        widget_0.setPlaceholderText("Pitch(um)")
        widget_0.textChanged.connect(self.input_pitch)
        widget_1=QLineEdit()
        widget_1.setPlaceholderText("层数")
        widget_1.textChanged.connect(self.input_layer)
        widget_left=QWidget()
        layout_l=QVBoxLayout()
        layout_l.addWidget(widget_0)
        layout_l.addWidget(widget_1)
        widget_left.setLayout(layout_l)
        widget_2=QWidget()
        layout_r=QVBoxLayout()
        widget_3=QLineEdit()
        widget_3.setPlaceholderText("Real Size(um)")
        widget_3.textChanged.connect(self.input_realsize)
        widget_4=QLineEdit()
        widget_4.setPlaceholderText("针数")
        widget_4.textChanged.connect(self.input_number)
        widget_5=QLineEdit()
        widget_5.setPlaceholderText("拉针角度(°)")
        widget_5.textChanged.connect(self.input_enter_angle)
        layout_r.addWidget(widget_3)
        layout_r.addWidget(widget_4)
        layout_r.addWidget(widget_5)
        widget_2.setLayout(layout_r)
        layout_bot.addWidget(widget_left)
        layout_bot.addWidget(widget_2)
        widget_bot=QWidget()
        widget_bot.setLayout(layout_bot)
        layout=QVBoxLayout()
        button=QPushButton("测试")
        button.clicked.connect(self.display_test_res)
        layout.addWidget(top_widget)
        layout.addWidget(widget_bot)
        layout.addWidget(button)
        
        self.setLayout(layout)
        #连接输入信号
    def input_pitch(self,s):
        self.pitch=float(s)
    def input_layer(self,s):
        self.layer=float(s)
    def input_realsize(self,s):
        self.real_size=float(s)
    def input_number(self,s):
        self.number=float(s)
    def input_enter_angle(self,s):
        self.enter_angle=float(s)
    def display_test_res(self):
        prop=self.property
        prop.test(pitch=self.pitch,layer=self.layer)
        prop.lean_test(real_size=self.real_size,pin_number=self.number,enter_angle=self.enter_angle)
        if self.w is None:
            self.w = TestResDisplay(prop)
            self.w.show()
        else:
            self.w.close()  # Close window.
            self.w = None

        
  
class ResultWindow(QWidget):
    def __init__(self,prop):
        super().__init__()
        self.w=None
        self.property=prop
        layout_l=QVBoxLayout()
        self.widget_0=QLabel(f"Taper:{round(prop.taper,4)} mm")
        self.widget_1=QLabel(f"弯头:{prop.wantou} mm")
        self.widget_2=QLabel(f"修正弯头:{prop.wantou_fixed} mm")
        self.widget_3=QLabel(f"bend tip length: {prop.bend_tip_length}")
        self.widget_4=QLabel(f"IO: {prop.square}")
        self.widget_5=QLabel(f"针压(: {prop.pressure} g")
        self.widget_6=QLabel(f"Scrub: {prop.scrub} um")
        layout_l.addWidget(self.widget_0)
        layout_l.addWidget(self.widget_1)
        layout_l.addWidget(self.widget_2)
        layout_l.addWidget(self.widget_3)
        layout_l.addWidget(self.widget_4)
        layout_l.addWidget(self.widget_5)
        layout_l.addWidget(self.widget_6)
        widget_l=QWidget()
        widget_l.setLayout(layout_l)
        button=QPushButton("Test")
        button.clicked.connect(self.new_window)
        layout_f=QHBoxLayout()
        layout_f.addWidget(widget_l)
        layout_f.addWidget(button)
        
        self.setLayout(layout_f)

    def new_window(self):
        property=self.property
        if self.w is None:
            self.w = TestWindow(property)
            self.w.show()
        else:
            self.w.close()  # Close window.
            self.w = None
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

      
        self.w=None
        self.compensation=0
        self.setWindowTitle("App")
        widget_0=QLineEdit()
        widget_0.setPlaceholderText("接地角(°)")
        '''widget_1=QLineEdit()
        widget_1.setPlaceholderText("层数")'''
        widget_2=QLineEdit()
        widget_2.setPlaceholderText("针径(mil)")
        widget_3=QLineEdit()
        widget_3.setPlaceholderText("角度(°)")
        widget_4=QLineEdit()
        widget_4.setPlaceholderText("针长(mil)")
        widget_5=QLineEdit()
        widget_5.setPlaceholderText("针尖径(mil)")
        widget_6=QLineEdit()
        widget_6.setPlaceholderText("力臂(mil)")
        widget_7=QLineEdit()
        widget_7.setPlaceholderText("OD(mil)")
        widget_8=QLineEdit()
        widget_8.setPlaceholderText("锥度长(mil)")
        widget_9 = QListWidget()
        widget_9.addItems(MaterialList)
        widget_10=QCheckBox("弯头补偿")

        
        widget_0.textChanged.connect(self.text_changed_0)
        #widget_1.textChanged.connect(self.text_changed_1)
        widget_2.textChanged.connect(self.text_changed_2)
        widget_3.textChanged.connect(self.text_changed_3)
        widget_4.textChanged.connect(self.text_changed_4)
        widget_5.textChanged.connect(self.text_changed_5)
        widget_6.textChanged.connect(self.text_changed_6)
        widget_7.textChanged.connect(self.text_changed_7)
        widget_8.textChanged.connect(self.text_changed_8)
        widget_9.currentTextChanged.connect(self.text_changed_9)
        widget_10.stateChanged.connect(self.show_state)
        layout = QVBoxLayout()
        layout.addWidget(widget_0)
        #layout.addWidget(widget_1)
        layout.addWidget(widget_2)
        layout.addWidget(widget_3)
        layout.addWidget(widget_4)
        layout.addWidget(widget_5)
        layout.addWidget(widget_6)
        layout.addWidget(widget_7)
        layout.addWidget(widget_8)
        layout.addWidget(widget_9)
        layout.addWidget(widget_10)
        widget_l=QWidget()
        widget_l.setLayout(layout)
        
        button=QPushButton("Continue")
        button.clicked.connect(self.the_button_was_clicked)
        button.clicked.connect(self.show_new_window)
        widget_r=button
        layout_f=QHBoxLayout()
        layout_f.addWidget(widget_l)
        layout_f.addWidget(widget_r)
        widget=QWidget()
        widget.setLayout(layout_f)
        self.setCentralWidget(widget)


    def text_changed_0(self, s):
        self.contact_angle=float(s)
    '''def text_changed_1(self, s):
        self.layer=int(s)'''
    def text_changed_2(self, s):
        self.dia=float(s)
    def text_changed_3(self, s):
        self.angle=float(s)
    def text_changed_4(self, s):
        self.length=float(s)
    def text_changed_5(self, s):
        self.tip_dia=float(s)
    def text_changed_6(self, s):
        self.moment=float(s)
    def text_changed_7(self, s):
        self.OD=float(s)
    def text_changed_8(self, s):
        self.taper_length=float(s)
    def text_changed_9(self, s):
        self.material=s
    def show_state(self, s):
        self.compensation=(s!=0)

    def the_button_was_clicked(self):
        self.property=ProbeProperty(contact_angle=self.contact_angle,dia=self.dia,length=self.length,tip_dia=self.tip_dia,angle=self.angle,moment=self.moment,OD=self.OD,material=self.material,taper_length=self.taper_length)
        property=self.property
        #Compute Parameters
        property.compute_taper()
        property.compute_bend_tip()
        property.compute_wantou(self.compensation)
        property.compute_pressure()
        property.compute_scrub(property.contact_angle==90,0)
    def show_new_window(self, checked):
        property=self.property
        if self.w is None:
            self.w = ResultWindow(property)
            self.w.show()
        else:
            self.w.close()  # Close window.
            self.w = None
        




app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()