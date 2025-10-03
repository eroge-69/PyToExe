#!/usr/bin/env python
# coding: utf-8

# In[52]:


import argparse
import csv
import contextlib
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import re
import multiprocessing
from F135WebAutomation import F135PageObject
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from pathlib import Path
import signal
import sys
import threading
from threading import Timer
import time


# In[53]:


# Utility Functions
def writeToCSV(filename, data):
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer object
        fieldnames = ["URL", "HttpErrorStatus", "Total Http Errors","Total Non-Http Errors"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        # Write the header row
        writer.writeheader()
    
        # Write the data rows
        for row in data:
            writer.writerow(row)
        print(f"File saved as {filename}")

def get_process(process_name):
    # Get the process ID (PID)
    try:
        cmd = f'tasklist /FI "IMAGENAME eq {process_name}" /NH'
        output = subprocess.check_output(cmd, shell=True).decode()
        lines = output.splitlines()
        return lines
    except subprocess.CalledProcessError as e:
        # Handle the case where the command returns a non-zero exit status
        if e.returncode == 1:
            print("javaw.exe process not found.")
        else:
            print(f"An error occurred: Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
            if e.stderr:
                print(f"Error output: {e.stderr.decode().strip()}")
    except FileNotFoundError:
        print("The 'tasklist' command was not found. Ensure it's in your system's PATH.")
    return None
            
def terminate_processes(process_name, pos = 0):
    # Get the process ID (PID)
    lines = get_process(process_name)
    if lines:
        print(lines)
        pid = int(lines[pos].split()[1])
        # Terminate the process
        terminate_process(pid, process_name)

def terminate_process(pid, name):
    try:
       # os.kill(pid, signal.SIGTERM)
        os.system("taskkill /F /pid "+str(pid))
        print(f"Terminated process {name} with PID {pid}")
    except ProcessLookupError:
        print(f"Process {name} not found")

def count_up():
    hours = 0
    minutes = 0
    seconds = 0

    while True:
        print(f"{hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
        seconds += 1

        if seconds == 60:
            seconds = 0
            minutes += 1

        if minutes == 60:
            minutes = 0
            hours += 1

@contextlib.contextmanager
def pushdir(new_dir):
    prevDir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prevDir)

def execStartJar(jarPath):
    subprocess.check_call(f"pushd {jarPath} && start.jar &", shell=True)

def stop_command(*procNames):
    noProcMsg = "INFO: No tasks are running which match the specified criteria."
    for procName in procNames:
        lines = get_process(procName)
        print(lines)
        for line in lines:
            if not noProcMsg in line:
                pid = int(lines[1].split()[1])
                terminate_process(pid, procName)
            
def run_command():

    """
    Automates generating and capturing screenshot of http 404 error for each given PWFF135 webpage
    Inputs: inputCSVFile, launchStartJar, launchHostName,launchStartJarWaitTime, 
    startJarFilePath, hostnameport, pwffilename, takeScreenshot, outputCSVFile
    Returns: void
    """
    screenshot = my_var.get() == True
    optVal = radiobutton_var.get()
    
    launchStartJar = optVal == "Option 1"
    launchHostName = optVal == "Option 2"
    defaultScriptPath = script_loc_entry.get()
    pwfFileName = pwfFileName_Entry.get()
    command = command_entry.get()
    csvInputDirPath = csv_input_entry.get()
    jarDirPath = jar_file_path_entry.get()
    defaultHostPath = host_entry.get()
    csvOutputPath = csv_output_entry.get()
    startJarLaunchTime = launchStartJarWait_Entry.get()
    takeScreenshot = my_var.get() == True

    if launchStartJar:
        if not jarDirPath:
            command = "Please Enter a valid Start Jar File Path"
            output_text.insert(tk.END, f"\n{command}\n")
            jar_file_path_entry.focus_set()
            return

        if not startJarLaunchTime:
            command = "Please Enter a valid Start Jar File Wait Time"
            output_text.insert(tk.END, f"\n{command}\n")
            launchStartJarWait_Entry.focus_set()
            return

    elif launchHostName:
        if not defaultHostPath:
            command = "Please Enter a valid hostname"
            output_text.insert(tk.END, f"\n{command}\n")
            host_entry.focus_set()
            return

        if not pwfFileName:
            command = "Please Enter a valid PWF File Name"
            output_text.insert(tk.END, f"\n{command}\n")
            pwfFileName_Entry.focus_set()
            return
        
    else:
        if not defaultHostPath:
            command = "Please Enter a valid hostname"
            output_text.insert(tk.END, f"\n{command}\n")
            host_entry.focus_set()
            return

        if not pwfFileName:
            command = "Please Enter a valid PWF File Name"
            output_text.insert(tk.END, f"\n{command}\n")
            pwfFileName_Entry.focus_set()
            return

        if not csvOutputPath:
            command = "Please Enter a valid CSV Output File"
            output_text.insert(tk.END, f"\n{command}\n")
            csv_output_entry.focus_set()
            return

        if not csvInputDirPath:
            command = "Please Enter a valid CSV Input File"
            output_text.insert(tk.END, f"\n{command}\n")
            csv_input_entry.focus_set()
            return    
    
    parser = argparse.ArgumentParser(description="F135HttpErrorWebAutomationTest")
    parser.add_argument('--inputCSVFile', default=f"{csvInputDirPath}")
    parser.add_argument('--launchStartJar', default=f"{launchStartJar}")
    parser.add_argument('--launchHostName', default=f"{launchHostName}")
    parser.add_argument('--launchStartJarWaitTime', default=f"{startJarLaunchTime}")
    parser.add_argument('--startJarFilePath', default=f"{jarDirPath}")
    parser.add_argument('--hostnameport', default=f"{defaultHostPath}")
    parser.add_argument('--pwffilename', default=f"{pwfFileName}")
    parser.add_argument('--takeScreenshot', default=f"{screenshot}")
    parser.add_argument('--outputCSVFile', default=f"{csvOutputPath}")
    args, unknown = parser.parse_known_args()

    print("Arguments: ")
    print(parser.parse_known_args())

    print("Request Type: F135HttpErrorWebAutomationTest\n")
    print("Start of F135HttpErrorWebAutomationTest\n")

    output_text.insert(tk.END, "Start of F135HttpErrorWebAutomationTest\n")

    os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"

    isLaunchHostName = True if args.launchHostName.upper() in ['TRUE', 'T'] else False
    isLaunchStartJar = True if args.launchStartJar.upper() in ['TRUE', 'T'] else False
    if isLaunchStartJar == True:
        noProcMsg = "INFO: No tasks are running which match the specified criteria."
        procName = "javaw.exe"
        lines = get_process(procName)
        print(lines)
        for line in lines:
            if not noProcMsg in line:
                pid = int(lines[1].split()[1])
                terminate_process(pid, procName)
        startDir = os.getcwd()
        startJarFilePath = args.startJarFilePath
        now = datetime.now()
        curDt = now.strftime("%m/%d/%Y - %H:%M:%S")
        print(f"Initiating execution of {startJarFilePath}\\start.jar on {curDt}")
        output_text.insert(tk.END, f"Initiating execution of {startJarFilePath}\\start.jar on {curDt}")
        try:
            timerThread = Timer(3, execStartJar, args=(f'{startJarFilePath}',))
            timerThread.start()
            if timerThread.is_alive():
                # Interrupts thread after parameterized seconds
                launchStartJarWaitTime = int(args.launchStartJarWaitTime)
                timerThread.join(timeout=launchStartJarWaitTime)
                os.system(f"popd {startJarFilePath}")
                print("\nInformation: Once start.jar is launched on the browser, copy the PWF file name after 127.0.0.1:Port#/, and then re-execute this script with parameter 'launchHostName' enabled to automate launching PWF-135 host URI on browser and proceed past 'I Agree' button without needing to re-launch start.jar file")
                output_text.insert(tk.END, "\nInformation: Once start.jar is launched on the browser, copy the PWF file name after 127.0.0.1:Port#/, and then re-execute this script with parameter 'launchHostName' enabled to automate launching PWF-135 host URI on browser and proceed past 'I Agree' button without needing to re-launch start.jar file")
        except:
            print(f"Error executing {startJarFilePath}\\start.jar:")
    elif isLaunchHostName == True:
        hostNamePort = args.hostnameport
        pwffilename = args.pwffilename
        driver = webdriver.Edge()
        f135Page = F135PageObject(f"{hostNamePort}/{pwffilename}/",driver)
        f135Page.launchPage()
        f135Page.login_direct()
        time.sleep(5)
        f135Page.closePage()
    else:
        files = []
        httpPart = args.hostnameport
        pwfUri = args.pwffilename
        with open(args.inputCSVFile, 'r') as file:
            reader = csv.reader(file)
            files = [list(chunk) for chunk in iter(lambda: [next(reader)], [])]
    
        data = [{}]
    
        takeScreenshot = True if args.takeScreenshot.upper() == "TRUE" else False
        httpErrCnt = 0
        nonHttpErrCnt = 0
        files = list(filter(None, files))
        for file in files:
            if any(file):
                driver = webdriver.Edge()
                htmlFile = file[0][0]
                if htmlFile.find(".htm") <= -1:
                    htmlFile = f"{htmlFile}.html"
                url = f"{httpPart}/{pwfUri}/{htmlFile}"
                url = url.replace("ï»¿", "")
                if url[-4:-1] != "htm" or not "html" in url:
                    url = url + ".html"
                f135Page = F135PageObject(url,driver)
                f135Page.launchPage()
                wait = WebDriverWait(driver, timeout=8000)
                #httpErrorEle = "//h2[text()='HTTP ERROR 404']"
                h2Ele = "//body"
                wait.until(EC.visibility_of_element_located((By.XPATH, h2Ele)))
                url = f135Page.getUrl()
                uriIndex = url.rfind("/")
                extIndex = url.rfind(".")
                uriParam = url[uriIndex + len("/") : extIndex]
                #assert(driver.title.find("404"))
                isHttpError = driver.title.find("404") > -1
                if isHttpError:
                    httpErrCnt = httpErrCnt + 1
                else:
                    nonHttpErrCnt = nonHttpErrCnt + 1
                if takeScreenshot == True:
                    #os.makedirs(directory_path, exist_ok=True)
                    fileImage = f"{uriParam}.png"
                    driver.save_screenshot(fileImage)
                    print(f"Screenshot saved as {fileImage}")
                httpErrorStatus = "Pass" if isHttpError else "Fail"
                print(f"\nHttp 404 Error Status for {url}, : {httpErrorStatus}")
                output_text.insert(tk.END, f"\nHttp 404 Error Status for {url}, : {httpErrorStatus}")
                f135Page.closePage()
                data.append({'URL': f'{url}', 'HttpErrorStatus': httpErrorStatus})
        data.insert(0, {'Total Http Errors': str(httpErrCnt),'Total Non-Http Errors': str(nonHttpErrCnt)})
        writeToCSV(f"{args.outputCSVFile}", data)
        del os.environ["SE_DRIVER_MIRROR_URL"]

    """
    command = os.path.join(defaultScriptPath, "F135HttpErrorWebAutomationTest.py")

    if takeScreenshot == True:
        command = f"{command} --takeScreenshot True"
    
    if optVal == "Option 1":
        if not jarDirPath:
            command = "Please Enter a valid Start Jar File Path"
            output_text.insert(tk.END, f"\n{command}\n")
            jar_file_path_entry.focus_set()
            return

        if not startJarLaunchTime:
            command = "Please Enter a valid Start Jar File Wait Time"
            output_text.insert(tk.END, f"\n{command}\n")
            launchStartJarWait_Entry.focus_set()
            return

        command = f"{command} --launchStartJar True --launchStartJarWaitTime {startJarLaunchTime}"

    elif optVal == "Option 2":
        if not defaultHostPath:
            command = "Please Enter a valid hostname"
            output_text.insert(tk.END, f"\n{command}\n")
            host_entry.focus_set()
            return

        if not pwfFileName:
            command = "Please Enter a valid PWF File Name"
            output_text.insert(tk.END, f"\n{command}\n")
            pwfFileName_Entry.focus_set()
            return

        command = f"{command} --hostnameport {defaultHostPath} --pwffilename {pwfFileName}"
        
    else:
        if not defaultHostPath:
            command = "Please Enter a valid hostname"
            output_text.insert(tk.END, f"\n{command}\n")
            host_entry.focus_set()
            return

        if not pwfFileName:
            command = "Please Enter a valid PWF File Name"
            output_text.insert(tk.END, f"\n{command}\n")
            pwfFileName_Entry.focus_set()
            return

        if not csvOutputPath:
            command = "Please Enter a valid CSV Output File"
            output_text.insert(tk.END, f"\n{command}\n")
            csv_output_entry.focus_set()
            return

        command = f"{command} --inputCSVFile {csvInputDirPath} --hostnameport {defaultHostPath} --pwffilename {pwfFileName} --outputCSVFile {csvOutputPath}"
       
        if takeScreenshot:
            command = f"{command} --takeScreenshot {takeScreenshot}"
    
    if command:
        try:
            # Execute the command and capture output
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=True
            )
            output_text.insert(tk.END, f"Command: {command}\n")
            output_text.insert(tk.END, f"Output:\n{result.stdout}\n")
            if result.stderr:
                output_text.insert(tk.END, f"Error:\n{result.stderr}\n")
        except subprocess.CalledProcessError as e:
            output_text.insert(tk.END, f"Command Error: {e}\n")
            output_text.insert(tk.END, f"Stderr: {e.stderr}\n")
        except Exception as e:
            output_text.insert(tk.END, f"An unexpected error occurred: {e}\n")
    else:
        output_text.insert(tk.END, "Please enter a command.\n")
    """
    print('Successfully Processed F135HttpErrorWebAutomationTest')
    output_text.insert(tk.END, '\nSuccessfully Processed F135HttpErrorWebAutomationTest\n')

def reset_fields():
    radiobutton_var.set("Option 1") # Set default radio button
    output_text.delete("1.0", tk.END)
    csv_input_entry.delete(0, tk.END)
    csv_output_entry.delete(0, tk.END)
    launchStartJarWait_Entry.delete(0, tk.END)


# In[54]:


# Create the main window
root = tk.Tk()
root.title("Run Releasability Verification GUI Version 3")

#root.state('zoomed')

root.geometry("1600x700") # Sets width to 1600 pixels and height to 700 pixels

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
    
# ISO Group Box
group_default_frame = tk.LabelFrame(root, text="Default Source Directories", padx=10, pady=10,bd=3)
group_default_frame.pack(padx=20, pady=20)
group_default_frame.place(x=120)
   
csv_input_label = tk.Label(group_default_frame, text="Input CSV File:")
csv_input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

csv_input_entry = tk.Entry(group_default_frame)
csv_input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
#csv_input_entry.insert(0, "C:\Users\E40006246\Documents\F135\Http404Error\2025\Q3_2025_RestrictedDMCVerificationInputOfficial.csv")
  
jar_file_path_label = tk.Label(group_default_frame, text="Start Jar File Path:")
jar_file_path_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
    
jar_file_path_entry = tk.Entry(group_default_frame)
jar_file_path_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
jar_file_path_entry.insert(0,"\\\pusehf11.pwus.us\\ME_AUTO\\techpubs\\F135_IETP\\IETP_Delivery\\Q3_2025\\22222\\PrePublish\\PWF135-77445-2J135-04_DVD_026_01")

host_label = tk.Label(group_default_frame, text="Hostname :")
host_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    
host_entry = tk.Entry(group_default_frame, width=78)
host_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
host_entry.insert(0,r"http://127.0.0.1:8000")

pwfFileName_Label = tk.Label(group_default_frame, text="PWF File Name:")
pwfFileName_Label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

pwfFileName_Entry = tk.Entry(group_default_frame, width=82)
pwfFileName_Entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
pwfFileName_Entry.insert(0,"PWF135-77445-2J135-04")

script_label = tk.Label(group_default_frame, text="Python Script Directory :")
script_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
    
script_loc_entry = tk.Entry(group_default_frame, width=78)
script_loc_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
script_loc_entry.insert(0,r"\\pusehf11.pwus.us\me_auto\techpubs\F135_IETP\IETP_Development\MilitaryEngineGUIs")

empty_label = tk.Label(group_default_frame, text="") 
empty_label.grid(row=2, column=5, sticky="ew", padx=5, pady=5)

group_default_frame2 = tk.LabelFrame(root, text="Parameters/Destination Directories", padx=10, pady=10,bd=3)
group_default_frame2.pack(padx=20, pady=20)
group_default_frame2.place(x=830)
   
csv_output_label = tk.Label(group_default_frame2, text="Output CSV File:")
csv_output_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
  
csv_output_entry = tk.Entry(group_default_frame2, width=58)
csv_output_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
#csv_output_entry.insert(0, "DM_Releasability_Validation_Q3_090825.csv")

launchStartJarWait_Label = tk.Label(group_default_frame2, text="Launch Start Jar Wait Time:")
launchStartJarWait_Label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
  
launchStartJarWait_Entry = tk.Entry(group_default_frame2, width=58)
launchStartJarWait_Entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
launchStartJarWait_Entry.insert(0, "15")

my_var = tk.BooleanVar()
checkbox = tk.Checkbutton(group_default_frame2,text="Take Screenshot",variable=my_var)
checkbox.grid(row=2, column=0, sticky="w", padx=5, pady=5)

# Radiobuttons
group_default_frame3 = tk.LabelFrame(root, text="Choose Run Option", padx=10, pady=10,bd=3)
group_default_frame3.pack(padx=20, pady=20)
group_default_frame3.place(x=828, y=screen_height*0.18)

radiobutton_var = tk.StringVar()
radiobutton_var.set("Option 1") # Default selection
radio1 = tk.Radiobutton(group_default_frame3, text="Step 1 - Initiate Start.jar", variable=radiobutton_var, value="Option 1").pack(side=tk.LEFT, padx=10)
#radio2 = tk.Radiobutton(group_default_frame3, text="Automate Start Jar", variable=radiobutton_var, value="Option 2").pack(side=tk.LEFT, padx=10)
radio3 = tk.Radiobutton(group_default_frame3, text="Step 2 - Run Releasability Validation", variable=radiobutton_var, value="Option 3").pack(side=tk.LEFT, padx=10)

command_entry = tk.Entry(root, width=50)
command_entry.pack(pady=5)
command_entry.place(x=580, y=screen_height*0.29)
command_entry.place_forget()
  
# Output display
output_label = tk.Label(root, text="Output:")
output_label.pack(pady=5)
output_label.place(x=screen_width*0.45, y=screen_height*0.35)

output_text = scrolledtext.ScrolledText(root, width=118, height=20)
output_text.pack(pady=5)
output_text.place(x=screen_width*0.15, y=screen_height*0.38)

# Run button
run_button = tk.Button(root, text="Run Script", command=run_command)
run_button.pack(pady=10)
run_button.place(x=screen_width*0.30, y=screen_height*0.28)

# Stop Script button
#run_button = tk.Button(root, text="Stop Script", command=lambda: stop_command("python.exe", "cmd.exe"))
#run_button.pack(pady=10)
#run_button.place(x=screen_width*0.35, y=screen_height*0.28)
    
# Reset & Close Button
reset_btn = tk.Button(root, text="Reset", command=reset_fields)
close_button = tk.Button(root, text="Exit", command=root.destroy)

reset_btn.place(x=630, y=screen_height*0.28)
close_button.place(x=screen_width*0.50, y=screen_height*0.28)
    
# Start the GUI event loop
root.mainloop()


# In[ ]:





# In[ ]:




