
import pyautogui,time
import pandas as pd
wb=pd.read_excel("C:\\Users\\kazim\\Drive'ım\\bes fon hisse\\Hisse Alımda Takip.xlsm",sheet_name=1)
c=input("Alım(a)/Satım(s) : ")
x=6
while True:
  try:
    fiyat=round(wb.iloc[x,2],2)
  except IndexError:
    break
  adet=int(round(wb.iloc[x,3],0))
  if c=="a":
    pyautogui.click(314,499)
  elif c=="s":
    pyautogui.click(373,495)
  time.sleep(1)
  pyautogui.click(912,345)
  pyautogui.hotkey("ctrl","a")
  pyautogui.write(str(fiyat))
  pyautogui.click(952,381)
  pyautogui.hotkey("ctrl","a")
  pyautogui.write(str(adet))
  pyautogui.click(850,503)
  pyautogui.click(812,531)
  x+=1