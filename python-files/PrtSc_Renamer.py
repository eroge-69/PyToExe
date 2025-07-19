import os
import datetime

path = "."  # 要遍历的目录, C:\Users\Username\Pictures\Screenshots
# path = input("Input the path:")
os.chdir(path)
info_list = []
for filename in os.listdir(path):
    info = {}
    if filename.endswith(").png") and ("屏幕截图" or "Screenshot" in filename):
        m_time = os.path.getmtime(filename)
        dt_m = datetime.datetime.fromtimestamp(m_time)
        info["name"] = filename
        info["time"] = (
            str(dt_m.year)
            + "-"
            + str("%.2d" % dt_m.month)
            + "-"
            + str("%.2d" % dt_m.day)
            + " "
            + str("%.2d" % dt_m.hour)
            + str("%.2d" % dt_m.minute)
            + str("%.2d" % dt_m.second)
        )
        # print(info)
        info_list.append(info)
# info_list = sorted(info_list, key=lambda d: d["time"])
# print(info_list)

for info in info_list:
    old_name = info["name"]
    new_name = "屏幕截图 " + info["time"] + ".png"
    os.rename(old_name, new_name)
    print(old_name, "->", new_name)
    # 屏幕截图(11).png -> 屏幕截图 2022-03-30 184953.png

# os.system('pause')
# pyinstaller -F  PrtSc_Renamer.py