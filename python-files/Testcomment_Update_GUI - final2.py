import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout,QComboBox, QMessageBox,QLabel,QLineEdit
from PyQt5.QtGui import QPixmap, QPainter,QFont
from PyQt5.QtCore import Qt, QRect
import psycopg2
import pandas as pd

class BackgroundWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.background_pixmap = QPixmap('zff.png')
        #if self.background_pixmap.isNull():
            #QMessageBox.critical(self, "Error", "Background image 'zff.png' not found.")

    #def paintEvent(self, event):
        #painter = QPainter(self)
        #painter.drawPixmap(QRect(0, 0, self.width(), self.height()), self.background_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Exam TestCase Comment Updator')
        self.setGeometry(0, 0, 800, 600)
        self.central_widget = BackgroundWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        control_layout = QVBoxLayout()
        heading = QLabel("Report Test Comment Update")
        heading.setFont(QFont("Arial", 20, QFont.Bold))  
        #heading.setStyleSheet("color: #2E86C1;")
        heading.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(heading)
        
        self.DB_label = QLabel("Data Base: ")
        self.text_label = QLabel("Test Comment: ")
        self.link_label = QLabel("EXAM Report Link: ")
        #textbox = QLineEdit()
        
        
        #main_layout.addWidget(label)
       

        self.comment_box = QTextEdit(self)
        #self.Heading_box = QTextEdit(self)
        #self.comment_box.setPlaceholderText("Test Comment")
        self.exam_report_box = QTextEdit(self)
        #self.exam_report_box.setPlaceholderText("Exam Report Link")

        self.setup_text_boxes()

        self.start_button = QPushButton('Start', self)
        self.stop_button = QPushButton('Stop', self)

        self.setup_buttons()

        self.dropdown = QComboBox(self)
        self.setup_dropdown()
        self.dropdown.setFixedSize(150, 40)
        
        control_layout.addWidget(self.DB_label)
        control_layout.addWidget(self.dropdown)
        control_layout.addWidget(self.text_label)
        control_layout.addWidget(self.comment_box)       
        control_layout.addWidget(self.link_label)
        control_layout.addWidget(self.exam_report_box)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(-10)
        #control_layout.setContentsMargins(0, 0, 0, 0)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(button_layout)
        self.central_widget.setLayout(main_layout)

        self.selected_db = None

    def setup_text_boxes(self):
        self.comment_box.setFixedSize(750, 200)
        self.exam_report_box.setFixedSize(750, 50)
        #self.Heading_box.setFixedSize(650, 100)

    def setup_buttons(self):
        self.start_button.setFixedSize(100, 40)
        self.stop_button.setFixedSize(100, 40)
        self.start_button.setStyleSheet("background-color: #5150ff; color: white;")
        self.stop_button.setStyleSheet("background-color: #5150ff; color: white;")

        self.start_button.clicked.connect(self.get_text_and_connect_to_DB)


    def setup_dropdown(self):
        #self.dropdown.addItem("Data_Base")
        self.dropdown.addItem("PLZ")
        self.dropdown.addItem("Local_DB")
        self.dropdown.addItem("Local_DB_VDI")
        self.dropdown.addItem("PLZ_local_postgre")
        self.dropdown.currentIndexChanged.connect(self.dropdown_changed)

    def dropdown_changed(self, index):
        db = {
            'PLZ': {'DB': 'exam_rmdb', 'user': 'exam_rmdb', 'host': 'HDRC01765.zf-world.com', 'pwd': '1RPc22Zwz58_zbR1'},
            'Local_DB': {'DB': 'exam_rmdb', 'user': 'exam_rmdb', 'host': 'HDRC02916.zf-world.com', 'pwd': '773iu]8Q0#4+9dD2'},
            'Local_DB_VDI': {'DB': 'exam_rmdb', 'user': 'exam_rmdb', 'host': 'FRDR49488.zf-world.com', 'pwd': '_38(FE[I1[!9gqE4'},
            'PLZ_local_postgre':{'DB': 'exam_rmdb', 'user': 'exam_rmdb', 'host': 'PLZV00022.emea.zf-world.com', 'pwd': 'exam'}
        }
        selected_option = self.dropdown.currentText()
        self.selected_db = db.get(selected_option)



    def get_text_and_connect_to_DB(self):
        # conn = psycopg2.connect(
        #        database="exam_rmdb",user="exam_rmdb",
        #        password='exam',host='PLZV00022.emea.zf-world.com',
        #        port='5432')
        #Replace PCNAME in below line with correct hostname


        conn = psycopg2.connect(
            database=self.selected_db['DB'],user=self.selected_db['user'],
            password=self.selected_db['pwd'],host=self.selected_db['host'],
            port='5432')
        cursor = conn.cursor()
        comment = self.comment_box.toPlainText()
        
        reportid = (self.exam_report_box.toPlainText()).split('/')[-1]
        print(reportid)
        
        cursor.execute("select exam_rmdb.grp.name,exam_rmdb.test.id,exam_rmdb.test.name,exam_rmdb.test.valuation,exam_rmdb.test.initialvaluation,exam_rmdb.test.testcomment,exam_rmdb.test.valuationcomment,exam_rmdb.metadataitem.label,exam_rmdb.metadataitem.value\
                from exam_rmdb.report inner join exam_rmdb.grp on exam_rmdb.grp.report_id = exam_rmdb.report.id\
               inner join exam_rmdb.test on exam_rmdb.test.grp_id=exam_rmdb.grp.id\
               	inner join exam_rmdb.metadata on exam_rmdb.metadata.report_id = exam_rmdb.report.id\
                inner join exam_rmdb.metadataitem on exam_rmdb.metadataitem.metadata_id=exam_rmdb.metadata.id\
               where exam_rmdb.report.id="+reportid+" and exam_rmdb.test.type=1")
        item = cursor.fetchall()
        #print(item)
        for temp in item:
            
            #print(temp)      
            #print(temp[2]  + ":::::" + temp[5])
            
            #testcomment_temp =  temp[5]+ "\n" + comment #to append in the data base
            testcomment_temp =  comment
            #valuationcomment_temp = temp[6]  + "\n" + comment #to append in the data base
            valuationcomment_temp = comment
            #print("**"+valuationcomment_temp)           
            cursor.execute(
                      "UPDATE test SET testcomment='" + testcomment_temp + "' \
                       WHERE id =" + str(temp[1]), 
                      ("testcomment",testcomment_temp));
            cursor.execute(
                      "UPDATE test SET valuationcomment='" + valuationcomment_temp + "' \
                       WHERE id =" + str(temp[1]), 
                      ("valuationcomment",valuationcomment_temp));
            

        #dataframe = pd.DataFrame(item,columns=["grp_name","test_id","test_name","finalvaluation","initialvaluation","test_comment","valuationcomment,val_id"])
        #dataframe.to_excel("c:\\temp\\plzdata.xlsx")                
        conn.commit()
        cursor.close()
        QMessageBox.information(self, "Success", "Test comments have been updated successfully.")
       
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
