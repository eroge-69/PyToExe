import tkinter as tk
from tkinter import *
import webbrowser
import subprocess


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Central Page")
ventana.geometry("730x460")
ventana.resizable(1, 1)
ventana.config(bg="blue")

#crear los titulos

IC = LabelFrame(ventana,text="IC",padx=50, pady=10)
IC.grid(row=0, column=0,padx=10, pady=10)
HBI = LabelFrame(ventana,text="HBI",padx=40, pady=10)
HBI.grid(row=0, column=1,padx=10, pady=10)
PPV = LabelFrame(ventana,text="PPV",padx=40, pady=10)
PPV.grid(row=0, column=2,padx=10, pady=10)
HST = LabelFrame(ventana,text="HST",padx=40, pady=10)
HST.grid(row=0, column=3,padx=10, pady=10)
HDMX = LabelFrame(ventana,text="HDMX",padx=40, pady=10)
HDMX.grid(row=2, column=1,padx=10, pady=10)
General = LabelFrame(ventana,text="General",padx=40, pady=10)
General.grid(row=2, column=2,padx=10, pady=10)
Safety = LabelFrame(ventana,text="Safety",padx=40, pady=10)
Safety.grid(row=2, column=0,padx=10, pady=10)
Laser = LabelFrame(ventana,text="Laser\OLB",padx=40, pady=10)
Laser.grid(row=2, column=3,padx=10, pady=10)


def Mensaje():
    print("pronto")

# crear las direcciones
# direcciones IC
def openiar_url():
    url = "https://crvle-request-tool.intel.com/"
    webbrowser.open_new_tab(url)

def openiar_url2():
    url = "https://crvle-lot-control.intel.com/"
    webbrowser.open_new_tab(url)

def openiar_url3():
    url = "https://mms-frontend-prod.app.intel.com/#/"
    webbrowser.open_new_tab(url)

def openiar_url4():
    url = "https://sqlbiprd.intel.com/Reports/powerbi/MVP_Labs_Analytics/CRML/OPS/IC_Room/Pending%20VPO%20Returns"
    webbrowser.open_new_tab(url)

def openiar_url5():
    url = "Back up"
    webbrowser.open_new_tab(url)

#Direcciones HBI

def openiar_url6():
    url = "NTR"
    webbrowser.open_new_tab(url)

def openiar_url7():
    url = "https://attd-analytics-dev.intel.com/Reports/powerbi/Skyfleet/MPE/HBI/MPE_HBI_Cell_Health"
    webbrowser.open_new_tab(url)

def openiar_url8():
    url = "https://planner.cloud.microsoft/webui/plan/4bpeyPft0EqGxcgV1WLk2mQACq82/view/board?tid=46c98d88-e344-4ed4-8496-4ed7712e255d"
    webbrowser.open_new_tab(url)

def openiar_url9():
    url = "https://intel.sharepoint.com/sites/crvlepassdown/SitePages/HDBI---LCBI.aspx"
    webbrowser.open_new_tab(url)

def openiar_url10():
    url = "Back Up"
    webbrowser.open_new_tab(url)

#Direcciones PPV

def openiar_url11():
    url = "https://hsdes.intel.com/appstore/generalapps/#/pages/community/1303837087?queryId=1806972859&articleId=14018257938"
    webbrowser.open_new_tab(url)

def openiar_url12():
    url = "https://attd-analytics-dev.intel.com/Reports/powerbi/Skyfleet/MPE/SST/MPE_SST_Utilization_Report"
    webbrowser.open_new_tab(url)

def openiar_url13():
    url = "https://planner.cloud.microsoft/webui/plan/K9OjVSPShUqTlxOn8cVmwWQAE06H/view/board?tid=46c98d88-e344-4ed4-8496-4ed7712e255d"
    webbrowser.open_new_tab(url)

def openiar_url14():
    url = "https://intel.sharepoint.com/:x:/r/sites/MPECRVLSpace-PPVPassDown/_layouts/15/Doc.aspx?sourcedoc=%7B49E83F13-1326-4580-A4D1-F7EBF5CB9B1C%7D&file=FOCUS%20GENERAL%20PPV.xlsx&action=default&mobileredirect=true"
    webbrowser.open_new_tab(url)

def openiar_url15():
    url = "NTR"
    webbrowser.open_new_tab(url)

#direcciones de HST

def openiar_url16():
    url = "https://sqlbiprd.intel.com/Reports/powerbi/MVP_Labs_Analytics/CRML/PPV/SysUtilizationMonitor"
    webbrowser.open_new_tab(url)

def openiar_url17():
    url = "https://attd-analytics-dev.intel.com/Reports/powerbi/Skyfleet/MPE/HST/MPE_HST_Utilization_Report"
    webbrowser.open_new_tab(url)

def openiar_url18():
    url = "https://planner.cloud.microsoft/webui/plan/wnGZZrp2-0SkXWPp1uNJ2GQAA46s/view/board?tid=46c98d88-e344-4ed4-8496-4ed7712e255d"
    webbrowser.open_new_tab(url)

def openiar_url19():
    url = "https://intel.sharepoint.com/:x:/r/sites/mpecrvlehst/_layouts/15/Doc.aspx?sourcedoc=%7B91728DE4-B293-4237-8A19-6773ED8647E0%7D&file=HST%20Tracking%20Tables.xlsx&wdLOR=cECD0DEF2-5D46-410F-82C3-0B6CBAC97DE3&action=default&mobileredirect=true"
    webbrowser.open_new_tab(url)

def openiar_url20():
    url = "Back up"
    webbrowser.open_new_tab(url)

#direcciones de HDMX

def openiar_url21():
    url = "https://attd-analytics-dev.intel.com/Reports/powerbi/Skyfleet/MPE/HDMX/MPE_HDMx_Utilization_Report"
    webbrowser.open_new_tab(url)

def openiar_url22():
    url = "https://attd-analytics-dev.intel.com/Reports/powerbi/SkyFleet/Customer%20Reports/MPE/MPE_HDMx_Cell_Health"
    webbrowser.open_new_tab(url)

def openiar_url23():
    url = "https://lcferna1-desk4.amr.corp.intel.com/schedule"
    webbrowser.open_new_tab(url)

def openiar_url24():
    url = "https://attd-analytics.intel.com/Reports/powerbi/CMMS/MPE/HDMx_Collaterals_CMMS"
    webbrowser.open_new_tab(url)

def openiar_url25():
    url = "https://sqlbiprd.intel.com/Reports/powerbi/MVP_Labs_Analytics/CRML/Planning/OPS_HDMX_STB_Report"
    webbrowser.open_new_tab(url)

def openiar_url26():
    url = "Back up"
    webbrowser.open_new_tab(url)

def openiar_url27():
    url = "Back up"
    webbrowser.open_new_tab(url)

#direcciones de General

def openiar_url28():
    url = "Back up"
    webbrowser.open_new_tab(url)

def openiar_url29():
    url = "https://intel.sharepoint.com/sites/crlvespoc/SitePages/Home.aspx"
    webbrowser.open_new_tab(url)

def openiar_url30():
    url = "http://cmms-mpe.intel.com/CollateralDashboard.aspx"
    webbrowser.open_new_tab(url)

def openiar_url31():
    url = "https://wiki.ith.intel.com/display/PPVSERVERPDE/Server+PPV+Product+Development+Engineering"
    webbrowser.open_new_tab(url)

def openiar_url32():
    url = "https://fmweb.intel.com/WIINGSFactoryPortal/#/login"
    webbrowser.open_new_tab(url)

def openiar_url33():
    url = "Back up"
    webbrowser.open_new_tab(url)

def openiar_url34():
    url = "Back up"
    webbrowser.open_new_tab(url)

# direcciones de Safety

def openiar_url35():
    url = "https://app.smartsheet.com/b/form/62306a255f5849e0b87b76c909620e85"
    webbrowser.open_new_tab(url)

def openiar_url36():
    url = "https://intel.sharepoint.com/sites/globalehs/SitePages/EHS-Program-Standards.aspx#safety"
    webbrowser.open_new_tab(url)

def openiar_url37():
    url = "https://ichem.intel.com/home"
    webbrowser.open_new_tab(url)

#direcciones de Laser

def openiar_url38():
    url = "https://wiki.ith.intel.com/spaces/1Ayourrandomstuff/pages/1905379331/Laser+Mark+Rofin"
    webbrowser.open_new_tab(url)

def openiar_url39():
    url = "https://igpt.intel.com/marketPlaceAssistantShare/4afa688d-4361-4005-870b-1e5061cd9510"
    webbrowser.open_new_tab(url)

# abrir programas

def abrir_programa():
    appref_ms_path = r"C:\Mole 2.0.appref-ms"
    subprocess.run(['cmd', '/c', appref_ms_path], check=True)

def abrir_programa2():
    appref_ms_path = r"C:\Blaster20.appref-ms"
    subprocess.run(['cmd', '/c', appref_ms_path], check=True)

def abrir_programa3():
    appref_ms_path = r"C:\Wombat 2 V20 - 1 .appref-ms"
    subprocess.run(['cmd', '/c', appref_ms_path], check=True)

# Crear los botones

boton = tk.Button(IC, text="IC Request", command=openiar_url,padx=4)
boton.place(x=23, y=40)
boton.pack()

boton = tk.Button(IC, text="Lot Control", command=openiar_url2)
boton.place(x=21, y=70)
boton.pack()

boton = tk.Button(IC, text="MRS", command=openiar_url3, padx=19)
boton.place(x=38, y=100)
boton.pack()

boton = tk.Button(IC, text="VPO Return", command=openiar_url4,padx=0.4)
boton.place(x=21, y=130)
boton.pack()

boton = tk.Button(IC, text="Back Up", command=Mensaje,padx=10)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HBI, text="Utilizacion", command=openiar_url6,padx=3)
boton.place(x=23, y=40)
boton.pack()

boton = tk.Button(HBI, text="Tool status", command=openiar_url7)
boton.place(x=21, y=70)
boton.pack()

boton = tk.Button(HBI, text="Task", command=openiar_url8, padx=18)
boton.place(x=30, y=10)
boton.pack()

boton = tk.Button(HBI, text="Pass down", command=openiar_url9,padx=1)
boton.place(x=21, y=130)
boton.pack()

boton = tk.Button(HBI, text="  Back Up  ", command=Mensaje)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(PPV, text="Loops", command=openiar_url11,padx=11)
boton.place(x=23, y=40)
boton.pack()

boton = tk.Button(PPV, text="Utilization", command=openiar_url12)
boton.place(x=21, y=70)
boton.pack()

boton = tk.Button(PPV, text="Task", command=openiar_url13, padx=17)
boton.place(x=38, y=100)
boton.pack()

boton = tk.Button(PPV, text="Pass down", command=openiar_url14,padx=1)
boton.place(x=21, y=130)
boton.pack()

boton = tk.Button(PPV, text="Back Up", command=Mensaje,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HST, text="Utilizacion", command=openiar_url16,padx=3)
boton.place(x=23, y=40)
boton.pack()

boton = tk.Button(HST, text="Tool status", command=openiar_url17)
boton.place(x=21, y=70)
boton.pack()

boton = tk.Button(HST, text="Task", command=openiar_url18, padx=18)
boton.place(x=38, y=100)
boton.pack()

boton = tk.Button(HST, text="Pass down", command=openiar_url19,padx=1)
boton.place(x=21, y=130)
boton.pack()

boton = tk.Button(HST, text="Back Up", command=Mensaje,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Utilizacion", command=openiar_url21,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Tool Status", command=openiar_url22,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Prime time", command=openiar_url23,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="CMMS Status", command=openiar_url24,padx=1)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Stand by", command=openiar_url25,padx=13)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Task", command=openiar_url26,padx=24)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(HDMX, text="Basck Up", command=Mensaje,padx=11)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="One note", command=openiar_url28)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="Spoc", command=openiar_url29,padx=14)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="CMMS", command=openiar_url30,padx=10)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="TP Release", command=openiar_url31)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="Wings", command=openiar_url32,padx=12)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="FACR", command=openiar_url33,padx=14)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(General, text="Back Up", command=openiar_url34,padx=7)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(Safety, text="Good Catch", command=openiar_url35)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(Safety, text="       EHS       ", command=openiar_url36)
boton.place(x=10, y=10)
boton.pack()

boton = tk.Button(Safety, text="  Quimicos  ", command=openiar_url37)
boton.place(x=10, y=10)
boton.pack()

boton = tk.Button(Laser, text="Iset", command=openiar_url38,padx=12)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(Laser, text="IGPT", command=openiar_url39,padx=11)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(Laser, text="Back UP", command=openiar_url39)
boton.place(x=30, y=160)
boton.pack()

boton = tk.Button(ventana, text="Mole", command=abrir_programa)
boton.place(x=360, y=427)

boton = tk.Button(ventana, text="Blaster", command=abrir_programa2,padx=7)
boton.place(x=285, y=427)

boton = tk.Button(ventana, text="Wombat", command=abrir_programa3)
boton.place(x=415, y=427)
#boton.pack()

ventana.mainloop()