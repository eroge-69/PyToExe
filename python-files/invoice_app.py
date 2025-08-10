from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog,QPrintPreviewDialog
import  os.path
import sqlite3
import warnings
import sys
import fileicons
from Template import Template
from Add_Product import AddProduct
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton,QLineEdit, QListWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDate
from ClearLayout import clear_layout
from Cart import Cart
from printinvoice import PrintInvoice
from datetime import date
from datetime import datetime
from Licensesw import License
from generate import Generate

warnings.filterwarnings("ignore")

class Invoice(QtWidgets.QMainWindow):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    uifile = os.path.join(BASE_DIR,"invoice.ui")
    selectedproduct={}
    font = QFont("Arial", 12)
    font.setBold(True)
    cartlist=[]
    def __init__(self):
        super(Invoice,self).__init__()
        uic.loadUi(self.uifile,self)
        if os.path.exists(os.path.join(self.BASE_DIR,"license.txt")):
            with open('license.txt', 'r') as file:
                # Write content to the file
                #file.write(f"{l1}-{l2}-{l3}-{l4}-{l5}-{l6}-{l7}-{l8}")
                readlicence=file.read()
                file.close()
            splitlicense=readlicence.split("-")
            date_to_check = datetime(date.today().year, date.today().month, date.today().day)
            start_date = datetime(2025, 8, 9)
            end_date = datetime(2026, 8, 9)

            #currentdate=str(date.today().day)+'/'+str(date.today().month)+'/'+str(date.today().year)
            if splitlicense[0]=="HASH" and splitlicense[1]=="VIK2" and splitlicense[2]=="O24P" and splitlicense[3]=="ORAN" and splitlicense[4]=="DLA1" and splitlicense[5]=="998H" and splitlicense[6]=="ARSH" and splitlicense[7]=="ITHA": 
                #if int(date.today().year)< 2026 and int(date.today().month)< 9 and int(date.today().day) < 8
                if start_date <= date_to_check <= end_date:
                    self.setEnabled(True)
                else:
                    self.statusbarinvoiceapp.setFont(self.font)
                    self.statusbarinvoiceapp.showMessage("Update the license inorder to use the Invoice Application")
                    self.centralwidget.hide()
                    #self.setEnabled(False)
                    #self.hide()
                    #self.actionlicense.setEnabled(True)
                    self.menuAdd.menuAction().setVisible(False)
                    self.menulicense.menuAction().setVisible(True)
                    
            else:
                self.statusbarinvoiceapp.setFont(self.font)
                self.statusbarinvoiceapp.showMessage("Update the license inorder to use the Invoice Application")
                self.centralwidget.hide()
                #self.setEnabled(False)
                #self.hide()
                #self.actionlicense.setEnabled(True)
                self.menuAdd.menuAction().setVisible(False)
                self.menulicense.menuAction().setVisible(True)
        else:
            self.statusbarinvoiceapp.setFont(self.font)
            self.statusbarinvoiceapp.showMessage("Purchase the license inorder to use the Invoice Application")
            self.centralwidget.hide()
            #self.setEnabled(False)
            #self.hide()
            #self.actionlicense.setEnabled(True)
            self.menuAdd.menuAction().setVisible(False)
            self.menulicense.menuAction().setVisible(True)
        
        self.actionTemplate.triggered.connect(self.template)
        self.actionExit.triggered.connect(self.close)
        self.addpushButton.clicked.connect(self.Add)
        self.actionAdd.triggered.connect(self.Add)
        self.deletepushButton.clicked.connect(self.Delete)
        self.actionDelete.triggered.connect(self.Delete)
        self.pushButton_addCart.clicked.connect(self.AddCart)
        self.pushButton_Cart.clicked.connect(self.Cart)
        self.pushButton_removecart.clicked.connect(self.RemoveCart)
        self.pushButton_save.clicked.connect(self.SaveProduct)
        self.actionsavemenu.triggered.connect(self.SaveProduct)
        self.actionlicense.triggered.connect(self.License)
        self.actionGenerate_Consolidated.triggered.connect(self.GenerateConsolidated)
        
        self.cartlist=[]
        if os.path.exists(os.path.join(self.BASE_DIR,"Cart.db")):
            self.conn = sqlite3.connect("Cart.db")
            self.cursor = self.conn.cursor()
            listOfTables = self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='CartInformation'; """).fetchall()
            if listOfTables==[]:
                self.cursor.execute("CREATE TABLE IF NOT EXISTS CartInformation (row int, fields TEXT)")

            self.cursor.execute("SELECT fields FROM CartInformation WHERE row = "+str(1))
            data=self.cursor.fetchone()
            #print(data)
            if data:
                retrieved_json, = data
                #print(retrieved_json)
                self.cartlist = json.loads(retrieved_json)
                self.pushButton_Cart.setText("Cart "+str(len(self.cartlist)))
                self.conn.close()
        
        self.verticallayout = QVBoxLayout() #groupbox
        if os.path.exists(os.path.join(self.BASE_DIR,"Template.db")):
            self.actionTemplate.setEnabled(False)
        
        if os.path.exists(os.path.join(self.BASE_DIR,"Products.db")):
            self.conn = sqlite3.connect("Products.db")
            self.cursor = self.conn.cursor()
            listOfTables = self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='ProductInformation'; """).fetchall()
            self.pushButton_addCart.hide()
            self.pushButton_Cart.hide() #my_button.hide()
            self.pushButton_removecart.hide()
            self.pushButton_save.hide()
            if self.cartlist:
                self.pushButton_removecart.setVisible(True)
                self.pushButton_addCart.setVisible(True)
                self.pushButton_Cart.setVisible(True)
                
            if listOfTables:
                self.cursor = self.conn.cursor()
                self.cursor.execute('SELECT COUNT(*) FROM ProductInformation')
                rows = self.cursor.fetchone()[0]
                for i in range(1,rows+1):
                    #print(i)
                    self.cursor = self.conn.cursor()
                    self.cursor.execute("SELECT fields FROM ProductInformation WHERE row = "+str(i))
                    data=self.cursor.fetchone()
                    if data:
                        retrieved_json, = data
                        retrieved_product_dict = json.loads(retrieved_json)
                        for key in retrieved_product_dict:
                            self.listWidget.addItem(retrieved_product_dict[key])
                            break
            self.conn.close()
        self.listWidget.itemClicked.connect(self.selectProduct)
    def Cart(self):
        self.cartwindow = Cart()
        self.cartwindow.BuyProceedClicked.connect(self.proceedtoBuy)
        self.cartwindow.show()
        # w = PrintInvoice()
        # w.show()
    def proceedtoBuy(self,boolvalue):
        self.invoice = PrintInvoice()
        self.invoice.orderconfirmed.connect(self.clearCart)
        self.invoice.show()
    
    def GenerateConsolidated(self):
        self.gen=Generate()
        self.gen.show()
        self.gen.close()
        if os.path.exists(os.path.join(self.BASE_DIR,('Invoice_Consolidated.xlsx'))):
            self.statusbarinvoiceapp.showMessage("Consolidated invoice file is generated...!!!")
    
    def clearCart(self,boolvalue):
        self.cartlist=[]
        self.pushButton_removecart.setVisible(False)
        self.pushButton_Cart.setVisible(False)
        
    def RemoveCart(self):
        item=self.listWidget.currentItem()
        if item and item.text() in self.cartlist:
            self.cartlist.remove(item.text())
            if len(self.cartlist)==0:
                self.pushButton_Cart.hide() #my_button.hide()
                self.pushButton_removecart.hide()
            self.pushButton_Cart.setText("Cart "+str(len(self.cartlist)))
            self.conn = sqlite3.connect("Cart.db")
            self.cursor = self.conn.cursor()
            listOfTables = self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='CartInformation'; """).fetchall()
            if listOfTables==[]:
                self.cursor.execute("CREATE TABLE IF NOT EXISTS CartInformation (row int, fields TEXT)")
                return
            else:
                self.cursor.execute('SELECT COUNT(*) FROM CartInformation')
                rows = self.cursor.fetchone()[0]
                if rows:
                    sql_update_query = """UPDATE CartInformation SET fields = ? WHERE row = ?;"""
                    list_as_json = json.dumps(self.cartlist)
                    self.cursor.execute(sql_update_query, (list_as_json,1))
            self.conn.commit()
            self.conn.close()
    
    def AddCart(self):
        item=self.listWidget.currentItem()
        self.conn = sqlite3.connect("Cart.db")
        self.cursor = self.conn.cursor()
        listOfTables = self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='CartInformation'; """).fetchall()
        if listOfTables==[]:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS CartInformation (row int, fields TEXT)")

        if item and item.text():
            #print(item.text())
            if item.text() in self.cartlist:
                pass
            else:
                self.cartlist.append(item.text())
                self.pushButton_removecart.setVisible(True)
                self.pushButton_Cart.setVisible(True)
                #self.cartitemscount+=1
                self.pushButton_Cart.setText("Cart "+str(len(self.cartlist)))
                
                self.cursor.execute('SELECT COUNT(*) FROM CartInformation')
                rows = self.cursor.fetchone()[0]
                list_as_json = json.dumps(self.cartlist)
                if rows:
                    sql_update_query = """UPDATE CartInformation SET fields = ? WHERE row = ?;"""
                    
                    self.cursor.execute(sql_update_query, (list_as_json,1))
                else:
                    self.cursor.execute("INSERT INTO CartInformation (row,fields) VALUES (?,?)", (1,list_as_json))
                    
                self.conn.commit()
                self.cursor.close()
                self.conn.close()
                    
    
    def selectProduct(self,item:QListWidgetItem):
        #item.text()
        clear_layout(self.verticallayout)
        #clear_layout(self.gridlayout_5)
        self.pushButton_save.setVisible(True)
        self.pushButton_addCart.setVisible(True)
        self.selectedproduct={}
        self.conn = sqlite3.connect("Products.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT COUNT(*) FROM ProductInformation')
        rows = self.cursor.fetchone()[0]
        #print(rows)
        for i in range(1,rows+1):
            self.cursor.execute("SELECT fields FROM ProductInformation WHERE row = "+str(i))
            data=self.cursor.fetchone()
            if data:
                retrieved_json, = data
                retrieved_product_dict = json.loads(retrieved_json)
                if item.text() in retrieved_product_dict.values():
                    #print(retrieved_product_dict)
                    self.horizontallayout=QHBoxLayout()
                    self.cursor.execute("SELECT ImagePath,ImageBinary FROM ProductImages WHERE row = "+str(i))
                    data =self.cursor.fetchone()
                    #print(data)
                    imgpath,ImgBinary=data
                    label=QLabel()
                    if imgpath == 'Image':
                        label.setText(ImgBinary)
                        font = QFont("Arial", 10)
                        label.setFixedSize(200, 30)
                        label.setFont(font)
                        label.adjustSize()
                    else:
                        pixmap = QtGui.QPixmap()
                        pixmap.loadFromData(ImgBinary)
                        label.setFixedSize(300, 300)
                        label.setScaledContents(True)
                        label.setPixmap(pixmap)
                        
                    self.horizontallayout.addWidget(label)
                    self.horizontallayout.addStretch()
                    self.verticallayout.addLayout(self.horizontallayout)
                    
                    for key in retrieved_product_dict:
                        self.horizontallayout=QHBoxLayout()
                        if 'image' in key.lower():
                            self.selectedproduct[key]=retrieved_product_dict[key]
                            pass
                        else:
                            label=QLabel(key)
                            font = QFont("Arial", 10)
                            #label.setFixedSize(100, 30)
                            label.setFont(font)
                            label.adjustSize()
                            self.horizontallayout.addWidget(label)
                            
                        
                        if 'date' in key.lower():
                            date=QDateEdit()
                            date.setCalendarPopup(True)
                            date_temp=retrieved_product_dict[key].split("/")
                            #print(date_temp)
                            date_Qdate=QDate(int(date_temp[0]),int(date_temp[1]),int(date_temp[2]))
                            date.setDate(date_Qdate)
                            font = QFont("Arial", 10)
                            date.setFont(font)
                            self.selectedproduct[key]=date

                            self.horizontallayout.addWidget(date)
                            self.horizontallayout.addStretch()
                        
                        elif 'image' in key.lower():
                            pass
                            # #print(i)
                            # self.cursor.execute("SELECT ImagePath,ImageBinary FROM ProductImages WHERE row = "+str(i))
                            # data =self.cursor.fetchone()
                            # #print(data)
                            # imgpath,ImgBinary=data
                            # label=QLabel()
                            # if imgpath == 'Image':
                                # label.setText(retrieved_product_dict[key])
                                # font = QFont("Arial", 10)
                                # label.setFixedSize(200, 30)
                                # label.setFont(font)
                                # label.adjustSize()
                            # else:
                                # pixmap = QtGui.QPixmap()
                                # pixmap.loadFromData(ImgBinary,'png')
                                # label.setPixmap(pixmap)
                            # self.horizontallayout.addWidget(label)
                            # self.horizontallayout.addStretch()
                        else:
                            lineedit=QLineEdit()
                            font = QFont("Arial", 10)
                            lineedit.setFont(font)
                            lineedit.setMinimumWidth(300)
                            lineedit.setFixedSize(300, 30)
                            lineedit.setText(retrieved_product_dict[key])
                            self.horizontallayout.addWidget(lineedit)
                            self.horizontallayout.addStretch()
                            self.selectedproduct[key]=lineedit
                        self.verticallayout.addLayout(self.horizontallayout)
                    self.groupbox_product.setLayout(self.verticallayout)
                    break
        self.conn.close()

    def Add(self):
        if os.path.exists(os.path.join(self.BASE_DIR,"Template.db")):            
            self.add = AddProduct()
            self.add.SaveClicked.connect(self.sub_window_addproduct)
            self.add.show()
            #print(self.add.product_details)
    
    def SaveProduct(self):
        sav_prod={}
        #print(sav_prod)
        if os.path.exists(os.path.join(self.BASE_DIR,"Products.db")):
            item=self.listWidget.currentItem()
            if item:
                #print(self.selectedproduct)
                for key in self.selectedproduct.keys():
                    if ('image' not in key.lower()) and ('date' not in key.lower()):
                        sav_prod[key]=self.selectedproduct[key].text()
                    elif  ('image' not in key.lower()) and ('date' in key.lower()):
                        sav_prod[key]=f"{self.selectedproduct[key].date().toPyDate().year}/{self.selectedproduct[key].date().toPyDate().month}/{self.selectedproduct[key].date().toPyDate().day}"
                    elif 'image' in key.lower():
                        sav_prod[key]=self.selectedproduct[key]
                #print(self.selectedproduct)
                self.conn = sqlite3.connect("Products.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute('SELECT COUNT(*) FROM ProductInformation')
                #print(type(self.cursor.fetchone()))
                rows = self.cursor.fetchone()[0]
                for i in range(1,rows+1):
                    self.cursor.execute("SELECT fields FROM ProductInformation WHERE row = "+str(i))
                    retrieved_json,=self.cursor.fetchone()
                    retrieved_product_dict = json.loads(retrieved_json)
                    if item.text() in retrieved_product_dict.values():
                        #print(item.text())
                        list_as_json = json.dumps(sav_prod)
                        sql_update_query = """UPDATE ProductInformation SET fields = ? WHERE row = ?;"""
                        self.cursor.execute(sql_update_query, (list_as_json,i))
                        self.conn.commit()
                        self.conn.close()
                        break
                
                
    def Delete(self):

        #item.text -> product name
        if os.path.exists(os.path.join(self.BASE_DIR,"Products.db")):
            item=self.listWidget.currentItem()            
            self.conn = sqlite3.connect("Products.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT COUNT(*) FROM ProductInformation')
            #print(type(self.cursor.fetchone()))
            rows = self.cursor.fetchone()[0]
            #print(rows)
            for i in range(1,rows+1):
                self.cursor.execute("SELECT fields FROM ProductInformation WHERE row = "+str(i))
                data=self.cursor.fetchone()
                #print(data)
                if data:
                    retrieved_json, = data
                    retrieved_product_dict = json.loads(retrieved_json)
                    if item.text() in retrieved_product_dict.values():
                        #print(item.text())
                        self.cursor = self.conn.cursor()
                        sql_delete_query = "DELETE FROM ProductInformation WHERE row = ?"
                        self.cursor.execute(sql_delete_query, (i,))
                        self.conn.commit()
                        
                        self.cursor = self.conn.cursor()
                        sqlimg_delete_query = "DELETE FROM ProductImages WHERE row = ?"
                        self.cursor.execute(sqlimg_delete_query, (i,))
                        self.conn.commit()
                        self.cursor.close()
                        self.conn.close()
                        break
            row = self.listWidget.row(item)
            self.listWidget.takeItem(row)
            clear_layout(self.verticallayout)
    
    def sub_window_addproduct(self,product_details):
        #print(product_details)
        for key in product_details:
            item1 = QListWidgetItem(product_details[key])
            self.listWidget.addItem(item1)
            self.listWidget.setCurrentItem(item1)
            self.selectProduct(item1)
            #list_widget.item(0).setSelected(True)
            break
    
    def template(self):
        self.temp=Template()
        self.temp.show()
        #print(os.path.join(self.BASE_DIR,"Template.db"))
        if os.path.exists(os.path.join(self.BASE_DIR,"Template.db")):
            self.actionTemplate.setEnabled(False)
    
    def License(self):
        self.lic = License()
        self.lic.show()
        self.statusbarinvoiceapp.setFont(self.font)
        self.statusbarinvoiceapp.showMessage("After saving the license, close the tool & reopen")

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Invoice()
    w.show()
    sys.exit(app.exec_())