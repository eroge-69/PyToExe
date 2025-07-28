import os
os.system('cls')
# __________________________
import time
import datetime
import getpass
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import urllib.request

#---chromedriverpath is ----C:\Users\Farshad\AppData\Local\Programs\Python\Python310\Scripts

#---config url check connection
def connect(host):
    try:
        urllib.request.urlopen(host,timeout=3 ) #Python 3.x
        return True
    except:
        return False
#---------------

#---config gmail
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

subject = "Control Naghshe"
body = "NewProjects are recieved..........."
sender = "fmardani@gmail.com"
recipients = ["fmardani@gmail.com",]
mailpassword = "dydfxeqlpzpylcrh"
#---------------

# password = input("Type Ur Pass.....>>")
password = getpass.getpass("Enter Password :")

#create chromeoptions instance
options = webdriver.ChromeOptions()

#---options.add_argument(r"--user-data-dir=C:/Users/Farshad\AppData/Local/Google/Chrome/User Data")
options.add_argument('--ignore-certificate-errors')  # برای خطاهای SSL

driver = webdriver.Chrome(options=options)
# نصب خودکار درایور Chrome و ایجاد نمونه مرورگر
#---driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#____________________________________________________

cnct= False
while cnct == False :
    cnct = connect('https://observer.tehran.ir/')
    if cnct == False :
        print("Internet connection lost , waiting.....")
        time.sleep(5)
print("Internet Connection is OKAY")

driver.get("https://observer.tehran.ir/Login.aspx")

Select(driver.find_element(By.ID , "MainContent_ctrlLogin_cmbMemberShipType")).select_by_value("2")
time.sleep(1)
driver.find_element(By.ID , "MainContent_ctrlLogin_txtEngOrgUser").send_keys("mardani-f")
driver.find_element(By.ID , "MainContent_ctrlLogin_txtPassword").send_keys(password)
driver.find_element(By.ID , "MainContent_ctrlLogin_btnLogin").click()
time.sleep(1)

myloop = 1
while myloop ==1 :
    driver.find_element(By.ID , "MainContent_ctrlUserMenus_TrvRightMenut0").click()
    time.sleep(1)
    no_new_project = driver.find_element(By.ID , "MainContent_ctrl4_lblTotalRequest").text

    curtime = datetime.datetime.now()
    print("----------------------------")
    print("Current time: = %s:%s:%s" % (curtime.hour, curtime.minute, curtime.second))
    print("Number of new Project = " , no_new_project )
    print("----------------------------")

    if int(no_new_project) > 0 :
        print("________________________________________")
        print("________________________________________")
        print("You got ", no_new_project , "Project")
        print("________________________________________")
        print("________________________________________")
        send_email(subject, body, sender, recipients, mailpassword)
        myloop = 0

    time.sleep(300)

    cnct= False
    while cnct == False :
        cnct = connect('https://observer.tehran.ir/')
        if cnct == False :
            print("Internet connection lost , waiting.....")
            time.sleep(5)
    print("Internet Connection is OKAY")

    driver.find_element(By.ID , "lblHome").click()
    time.sleep(10)


CloseProg = input("Do u wanna to close WebPage.....? (type    Y     to Quit)")
while CloseProg.capitalize() != "Y":
    CloseProg = input("Do u wanna to close WebPage.....? (type    Y     to Quit)")
else :
    driver.quit()

