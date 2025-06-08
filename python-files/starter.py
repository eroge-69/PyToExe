import os



num = 20 #int(input("Enter Number of instances: "))
sval = 0 #int(input("Enter Starting Value: "))
gap = 150 #int(input("Enter Gap Value: "))
pro = 0 #int(input("Enter Protection Value: "))
idd = 0





for i in range(0,num):
    vv = sval+gap
    os.system("start run.py " + str(sval+pro) + " " + str(vv) + " " + str(idd))
    sval += gap
    idd += 1
