from PyQt5 import QtWidgets, uic

import cx_Oracle
import subprocess
import os
import psutil

#---------------Oracle Data Deletion from SCOTT User

def scott():

    # Oracle connection configuration
    username = 'scott'
    password = 'tiger'  # 🔐 Replace with your SCOTT password
    dsn = 'localhost/orcl'      # 🖥️ Replace with your Oracle SID/service name

    try:
        # Establish Oracle connection
        conn = cx_Oracle.connect(username, password, dsn)
        cursor = conn.cursor()
        print("🔗 Connected to Oracle Database.")

        # Step 1: Get all table names except EMP and DEPT
        cursor.execute("""
            SELECT table_name FROM user_tables
            WHERE table_name NOT IN ('EMP', 'DEPT')
        """)
        tables = cursor.fetchall()

        # Step 2: Drop each table permanently
        for (table_name,) in tables:
            try:
                drop_sql = f'DROP TABLE "{table_name}" PURGE'
                #print(f"🗑️ Dropping table permanently: {table_name}")
                cursor.execute(drop_sql)
            except Exception as e:
                print(f"❌ Error dropping {table_name}: {e}")

        # Step 3: Empty the recycle bin (for SCOTT user only)
        #print("🧹 Emptying Recycle Bin...")
        cursor.execute("PURGE RECYCLEBIN")

        conn.commit()
        print("✅ Work is Over.. All Un Necessary Tables are deleted..")

    except cx_Oracle.DatabaseError as e:
        print(f"❌ Database error: {e}")
    finally:
        # Cleanup
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            #print("🔒 Connection closed.")
            
            dlg.lab1.setText("Deleted Successfully in SCOTT User")
            print("Developed by *****----- RPC SOFTWARE TECHNOLOGIES *****....")

#-----------------------Tally Folder Delete

def tallydata():

    import shutil
    import os

    # Specify the path to the folder you want to delete
    folder_to_delete = "C:/Users/Public/TallyPrime/data/"  # Replace with the actual path

    # Check if the folder exists before attempting to delete it
    if os.path.exists(folder_to_delete):
        try:
            shutil.rmtree(folder_to_delete)
            
            #print(f"Folder '{folder_to_delete}' and its contents deleted successfully.")

            dlg.lab1.setText("Deleted Data Successfully..")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}.")
    else:
        print(f"Folder '{folder_to_delete}' does not exist.")

#-------------Enable WIFI

def enablewifi():
    os.system("cls")
    os.system("netsh interface set interface Wi-Fi enable")
    input()

#-------------Disable WIFI

def disablewifi():
    os.system("cls")
    os.system("netsh interface set interface Wi-Fi disable")
    input()


#--------------Host and IP Address

def hostip():

    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"\n\n\n\t\t\t\t\t\t Hostname: {hostname} \t IP Address : {ip_address}")
    
#------------------Shutdown

def sd():
    choice=input("Want to shut down your computer [Y/N] ")

    if ( choice == 'Y' or choice == 'y' ):

        os.system("shutdown /s /t 10")

    else:

        print("Continue your work")

#----------------CPU Usage

def cpu():

    cpu_percent = psutil.cpu_percent(interval=1)
    #print(f"CPU Usage: {cpu_percent}%")

    memory = psutil.virtual_memory()
    #print(f"Memory Usage: {memory.percent}%")

    disk = psutil.disk_usage('/')
    print(f"\n\n\t\t\tCPU Usage: {cpu_percent}% Memory Usage: {memory.percent}% Disk Usage: {disk.percent}%")

#-------------------------------

def oscontrol():
    
    while True:
        print("\n\n\n\n")
        print("\t\t\t\t\t        SYSTEM CONTROL ")
        print("\t\t\t\t\t        ================== \n")
        print("\t\t\t\t\t\t 1. Enable Wifi")
        print("\t\t\t\t\t\t 2. Disable Wifi")
        print("\t\t\t\t\t\t 3. Enable LAN")
        print("\t\t\t\t\t\t 4. Disable LAN")
        print("\t\t\t\t\t\t 5. Enable FIREWALL")
        print("\t\t\t\t\t\t 6. Disable FIREWALL")
        print("\t\t\t\t\t\t 7. HOST and IP ")
        print("\t\t\t\t\t\t 8. Check CPU Status")
        print("\t\t\t\t\t\t 9. Shut Down")
        print("\t\t\t\t\t\t 0. Back to Main Menu")


        choice = input("\n\n\n\t\t\t\t\t\t Enter your choice : ")

        if choice == '1':
            enablewifi()
            

        elif choice == '2':
            disablewifi()
            

        elif choice == '3':
            os.system("cls")
            os.system("netsh interface set interface Ethernet enable")            

        elif choice == '4':
            os.system("cls")
            os.system("netsh interface set interface Ethernet disable")

        elif choice == '5':
            os.system("cls")
            os.system("netsh advfirewall set allprofiles state on")            

        elif choice == '6':
            os.system("cls")
            os.system("netsh advfirewall set allprofiles state off")

        elif choice == '7':
            hostip()

        elif choice == '8':
            cpu()
            input()
            
        elif choice == '9':
            sd()
            
                      
        elif choice == '0':
            os.system("cls")
            #main()
            print("Exiting program.")
            break

        else:
            print("Invalid choice.")

#oscontrol()

app=QtWidgets.QApplication([])

dlg=uic.loadUi("oscontrol.ui")

dlg.pb1.clicked.connect(enablewifi)
dlg.pb2.clicked.connect(disablewifi)

dlg.pb7.clicked.connect(hostip)
dlg.pb8.clicked.connect(cpu)
dlg.pb9.clicked.connect(scott)
dlg.pb10.clicked.connect(tallydata)

dlg.show()
app.exec()

