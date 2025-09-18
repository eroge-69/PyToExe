# -*- coding: utf-8 -*- import os,sys import base64 import tkinter as tk
# from tkinter import filedialog def rename():  '''打开选择文件夹对话框'''  root =
# tk.Tk()  root.withdraw()  path =
# os.path.normpath(filedialog.askdirectory())#获得选择好的文件夹  filelist =
# os.listdir(path)  #该文件夹下所有的文件（包括文件夹）  i=0  for files in filelist:
# #遍历所有文件  try:  Olddir = os.path.join(path, files)  #原来的文件路径  if
# os.path.isdir(Olddir):  #如果是文件夹则跳过  continue  if files[0] == "." :
# #开头字符.  #涉及网络url传输,其中的+和/会被转义成_和-  #替换多个不同的字符串： translate()
# file_ed=files.translate(str.maketrans({'_': '/', '-': '+'}))
# decodestr=base64.b64decode(file_ed)  #文件名
# file_name=decodestr.decode('utf-8', errors='ignore')  filetype =
# ".mp3"  #文件扩展名  Newdir = os.path.normpath(os.path.join(path, file_name
# + filetype))  #新的文件路径  os.rename(Olddir, Newdir)  #重命名  i=i+1
# print(files + " -> " + file_name)  except Exception as e:  print
# (str(e))  print("转换完成文件名共计" + str(i) +"个") if __name__ == '__main__':
# rename()
