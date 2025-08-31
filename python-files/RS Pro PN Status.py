import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
service = Service(executable_path="chromedriver.exe")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
options = webdriver.ChromeOptions()
options.page_load_strategy = 'none'
c=0
with open('RS links.txt') as f:
    hhh=[]
    for line in f:
        url= line
        print(url)
        hhh.append(url.strip())
h = 0
print(len(hhh),"URLs found")
input("Press Enter to start\n")
file1 = open("RS Pro PN Status.txt","w")
file1.write("PN\t""Status\t""Current Link\t""Link\t""Date&Time")
file1.write("\n")
file1.close()
with webdriver.Chrome(service=service,options=options) as driver:
    for h in range(len(hhh)):
        link=hhh[h]
        driver.get(link)
        
        try:
            wait = WebDriverWait(driver,10)
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div[1]/main/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div/div/dl/dd[1]')))
            driver.execute_script("window.stop();")
            #time.sleep(0.5)
            pn = driver.find_element(By.XPATH,'//*[@id="__next"]/div[1]/main/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div/div/dl/dd[1]').text
            status = driver.find_element(By.XPATH,'//*[@id="__next"]/div[1]/main/div[1]/div[3]/div[2]/div[1]/div/div[1]/div/div/span/span[2]/span').text
            time.sleep(1)
            current_time = datetime.datetime.now()
            file1 = open("RS Pro PN Status.txt","a")
            file1.write(f"{pn}\t"f"{status}\t"f"{driver.current_url}\t"f"{hhh[h]}\t"f"{current_time}")
            file1.write("\n")
            file1.close()

        except:
            current_time = datetime.datetime.now()
            file1 = open("RS Pro PN Status.txt","a")
            file1.write("Error\t""Error\t"f"{driver.current_url}\t"f"{hhh[h]}\t"f"{current_time}")
            file1.write("\n")
            file1.close()
        c=c+1
        if c==100:
            driver.close()
            time.sleep(2)
            driver=webdriver.Chrome(service=service,options=options)
            c=0
        print(h+1,"URL Done")
        print(len(hhh)-h-1,"URL in prog")
input("Press Enter to Exit\n")
