# Import Module
from tkinter import *
import pyvisa
import time

# Font sizes
font_size = 20
font_table = 30
font_status = 10

# create root window
root = Tk()

# root window title and dimension
root.title("Testowanie Diod")
# Set geometry(widthxheight)
root.geometry('1180x580')

# adress ip label
lbl_ip = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = " Adres IP: ")
lbl_ip.grid(column=0, row=0)

# adress ip entry field
txt_ip = Entry(root, width=16, font=('Comic Sans MS',font_size))
with open("ip.txt") as f:
    txt_ip.insert(0,f.read())
    f.close()
txt_ip.grid(column =1, row =0)

# save adress ip function 
def clicked_ip():
    with open("ip.txt", "w") as f:
        f.write(str(txt_ip.get()))
    f.close()

# test diode function
def clicked_tst():
    #load adress ip
    ip_file = open("ip.txt")
    ip_adress = ip_file.read()
    ip_file.close()
    visa_adress = f"TCPIP0::{ip_adress}::inst0::INSTR"
    
    rm = pyvisa.ResourceManager()
    try:
        # connect to instrument
        lbl_status_info.insert(END, "Laczenie z miernikiem o adresie IP: "+str(ip_adress)+"\n")
        instrument = rm.open_resource(visa_adress)
        instrument.timeout = 5000

        # display connected instrumment
        idn = instrument.query("*IDN?")
        lbl_status_info.insert(END,"Polaczono z urzadzeniem:"+str(idn.strip())+"\n")
        # load recall 0
        lbl_status_info.insert(END,"Wybieranie recall 0\n")
        instrument.write("MMEM:LOAD:STAT 0")
        time.sleep(0.5)
        # turn on DC BIAS
        lbl_status_info.insert(END,"Właczanie BIAS ON\n")
        instrument.write(":BIAS:STAT ON")
        # read measurement
        rs = instrument.query(":FETCh?")
        lbl_status_info.insert(END,"Zmierzone Rs: " + rs+"\n")
        # load recall 1
        lbl_status_info.insert(END,"Wybieranie recall 1\n")
        instrument.write("MMEM:LOAD:STAT 1")
        time.sleep(0.5)
        # turn on DC BIAS
        lbl_status_info.insert(END,"Właczanie BIAS ON\n")
        instrument.write(":BIAS:STAT ON")
        # read measurement
        cs = instrument.query(":FETCh?")
        lbl_status_info.insert(END,"Zmierzone Cs: " + cs+"\n")
        # load recall 2
        lbl_status_info.insert(END,"Wybieranie recall 2\n")
        instrument.write("MMEM:LOAD:STAT 2")
        time.sleep(0.5)
        # turn on DC BIAS
        lbl_status_info.insert(END,"Właczanie BIAS ON\n")
        instrument.write(":BIAS:STAT ON")
        # read measurement
        vplist = instrument.query(":FETCh?")
        for x in range(19):
            time.sleep(0.1)
            vplist = vplist + instrument.query(":FETCh?")
        # turn off DC BIAS
        instrument.write(":BIAS:STAT OFF")
        lbl_status_info.insert(END,"Zmierzone Vplist: " + vplist+"\n")
        lbl_status_info.see("end")

        # convert string measurement to float
        rs = rs.split(",")[1]
        rsf = float(rs)
        cs = cs.split(",")[0]
        csf = float(cs)*pow(10,15)
        # find first measurement in sweep over 1mA
        vplist = vplist.split("\n")
        for row in vplist:
            i = float(row.split(",")[1])
            vp = float(row.split(",")[0])
            if i<-0.001:
                vp = -vp*1000
                break
        # show measurement in labels
        lbl_rs_val = Label(root, width=10, font=('Comic Sans MS',font_size), text = "%.2f Ohm" % rsf)
        lbl_rs_val.grid(column=1,row=1,stick='w')
        lbl_cs_val = Label(root, width=10, font=('Comic Sans MS',font_size), text = "%.3f pF" % (csf/1000))
        lbl_cs_val.grid(column=1,row=2,stick='w')
        lbl_vp_val = Label(root, width=10, font=('Comic Sans MS',font_size), text = "%.2f mV" % vp)
        lbl_vp_val.grid(column=1,row=3,stick='w')

        # box position variables
        q = 0
        col_p = 0
        row_p = 0

        # display blank table
        t = Table(root)

        # convert Rs value to horizontal position
        if rsf >= 1.1 and rsf < 1.2:
            col_p = 0
        if rsf >= 1.2 and rsf < 1.3:
            col_p = 1
        if rsf >= 1.3 and rsf < 1.4:
            col_p = 2
        if rsf >= 1.4 and rsf < 1.5:
            col_p = 3
        if rsf >= 1.5 and rsf < 1.6:
            col_p = 4

        # convert Cs value to vertical position
        if csf >= 240 and csf < 250:
            row_p = 0
        if csf >= 250 and csf < 260:
            row_p = 1
        if csf >= 260 and csf < 270:
            row_p = 2
        if csf >= 270 and csf < 280:
            row_p = 3
        if csf >= 280 and csf < 290:
            row_p = 4

        # convert Vp value to position (quarter)
        if vp >= 710 and vp < 720:
            q = 0
        if vp >= 720 and vp < 730:
            q = 1
            col_p = col_p + 5
        if vp >= 730 and vp < 740:
            q = 2
            row_p = row_p + 5
        if vp >= 740 and vp < 750:
            q = 3
            col_p = col_p + 5
            row_p = row_p + 5

        # display X in position
        e = Label(root, width=2, font=('Arial',font_table,'bold'), text = "X", borderwidth=1, relief="solid")
        e.grid(row=row_p+1, column=col_p+4)

        # display position value in label 
        lbl_pos_val = Label(root, width=10, font=('Comic Sans MS',font_size), text = "["+str(row_p+1)+","+str(col_p+1)+"]")
        lbl_pos_val.grid(column=1,row=4,stick='w')

    # display error
    except pyvisa.VisaIOError as e:
        lbl_status_info.insert(END,"Error: "+str(e)+"\n")
        lbl_status_info.see("end")

    # close connection and display info 
    finally:
        if 'instrument' in locals():
            instrument.close()
            lbl_status_info.insert(END,"Polaczenie zamkniete\n")

# save adress ip button
btn_ip = Button(root, width=10, font=('Comic Sans MS',font_size-5), text = "Zapisz", command=clicked_ip)
btn_ip.grid(column=2, row=0, sticky = "e")
# start test button
btn_tst = Button(root, width=10, font=('Comic Sans MS',font_size-5), text = "Testuj", command=clicked_tst)
btn_tst.grid(column=2, row=1, sticky = "e")
# Rs label
lbl_rs = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = "Rs = ")
lbl_rs.grid(column=0,row=1)
# Rs value label
lbl_rs_val = Label(root, width=10, anchor = "w", font=('Comic Sans MS',font_size), text = "")
lbl_rs_val.grid(column=1,row=1)
# Cs label
lbl_cs = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = "Cs = ")
lbl_cs.grid(column=0, row=2)
# Cs value label
lbl_cs_val = Label(root, width=10, anchor = "w", font=('Comic Sans MS',font_size), text = "")
lbl_cs_val.grid(column=1,row=2)
# Vp label
lbl_vp = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = "Vp = ")
lbl_vp.grid(column=0, row=3)
# Vp value label
lbl_vp_val = Label(root, width=10, anchor = "w", font=('Comic Sans MS',font_size), text = "")
lbl_vp_val.grid(column=1,row=3)
# position label
lbl_pos = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = "Pozycja: ")
lbl_pos.grid(column=0,row=4)
# position value label
lbl_pos_val = Label(root, width=10, anchor = "w", font=('Comic Sans MS',font_size), text = "")
lbl_pos_val.grid(column=1,row=4)
# status label
lbl_status = Label(root, width=10, anchor = "e", font=('Comic Sans MS',font_size), text = "Status: ")
lbl_status.grid(column=0,row=5)
# status text box
lbl_status_info = Text(root, width=int(26*font_size/font_status), height=int(5*font_table/font_status) , font=('Comic Sans MS',font_status))
lbl_status_info.grid(column=1,row=5,columnspan=2,rowspan=6,sticky="n")


class Table:
    
    def __init__(self,root):
        
        # create table
        for i in range(11):
            for j in range(11):
                # upper left corner
                if (i==0 and j==0):
                    self.e = Label(root, width=2, font=('Arial',font_table,'bold'), text = " ", borderwidth=1, relief="solid")
                    self.e.grid(row=i, column=j+3)
                # upper number index
                elif i==0:
                    self.e = Label(root, width=2, font=('Arial',font_table,'bold'), text = str(j), borderwidth=1, relief="solid")
                    self.e.grid(row=i, column=j+3)
                # left numer index
                elif j==0:
                    self.e = Label(root, width=2, font=('Arial',font_table,'bold'), text = str(i), borderwidth=1, relief="solid")
                    self.e.grid(row=i, column=j+3)
                # blank table
                else:
                    self.e = Label(root, width=2, font=('Arial',font_table,'bold'), text = " ", borderwidth=1, relief="solid")
                    self.e.grid(row=i, column=j+3)
    
#init table
t = Table(root)

# Execute Tkinter
root.resizable(0,0)
root.mainloop()

