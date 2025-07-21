import cpuinfo
import GPUtil
import psutil
import platform
import wx
import wmi
b = str(round(psutil.boot_time() / 1000000000, 2))
g = GPUtil.getGPUs()[0]
os=f"{platform.system()}{platform.release()}"
verjen= platform.version()
machine=f"Machine:, {platform.machine()}"
app = wx.App()
frame = wx.Frame(None, title="system info")
notebook=wx.Notebook(frame)
tab1=wx.Panel(notebook)
tab2=wx.Panel(notebook)
tab3=wx.Panel(notebook)
tab5=wx.Panel(notebook)
tab6=wx.Panel(notebook)
notebook.AddPage(tab1,"matherboard")
notebook.AddPage(tab2,"cpu")
notebook.AddPage(tab3,"ram")
notebook.AddPage(tab5,"gpu")
notebook.AddPage(tab6,"os")
labels = [
    f"Name: {g.name}",
    f"Driver: {g.driver}",
    f"Memory Used: {g.memoryUsed} MB",
    f"Memory Total: {g.memoryTotal} MB",
    f"UUID: {g.uuid}"]
sizer = wx.BoxSizer(wx.VERTICAL)
for text in labels:
    sizer.Add(wx.StaticText(tab5, label=text), 0, wx.ALL, 5)
tab5.SetSizer(sizer)
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(wx.StaticText(tab6, label=f"os={os}"), 0, wx.ALL, 5)
sizer.Add(wx.StaticText(tab6, label=f"version={verjen}"), 0, wx.ALL, 5)
sizer.Add(wx.StaticText(tab6, label=f"machine={machine}"), 0, wx.ALL, 5)
sizer.Add(wx.StaticText(tab6, label=f"boot time={b}"), 0, wx.ALL, 5)
tab6.SetSizer(sizer)
cpu=cpuinfo.get_cpu_info()
sizer = wx.BoxSizer(wx.VERTICAL)
info = [
    f"model={cpu['brand_raw']}",
    f"architect={cpu['arch']}",
    f"bits= {cpu['bits']}",
    f"Frequency= {cpu['hz_actual_friendly']}",
    f"builder= {cpu['vendor_id_raw']}"
]
cpu_info="\n".join(info)
sizer.Add(wx.StaticText(tab2, label=cpu_info), 0, wx.ALL, 5)
board = wmi.WMI().Win32_BaseBoard()[0]
info_matherboard = [
    f"builder: {board.Manufacturer}",
    f"model: {board.Product}",
    f"linesece: {board.SerialNumber}",
    f"version: {board.Version}",
    f"Label: {board.Tag}"
]
info_matherboard2="\n".join(info_matherboard)
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(wx.StaticText(tab1, label=info_matherboard2), 0, wx.ALL, 5)
c = wmi.WMI()
ram_info = []
for mem in c.Win32_PhysicalMemory():
    ram_info.append(f"Capacity= {int(mem.Capacity) // (1024**3)} GB")
    ram_info.append(f"speed= {mem.Speed} MHz")
    ram_info.append(f"type= {mem.MemoryType}")
    ram_info.append(f"builder= {mem.Manufacturer}")
    ram_info.append(f"Model {mem.PartNumber.strip()}")
sizer = wx.BoxSizer(wx.VERTICAL)
for text in ram_info:
    sizer.Add(wx.StaticText(tab3, label=text), 0, wx.ALL, 5)
tab3.SetSizer(sizer)
frame.Show()
app.MainLoop()