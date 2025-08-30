#!/usr/bin/env python
# coding: utf-8

# In[14]:


# modified for CfH 1.11 trace logs NBG
__DateLastUpdated__ = "20/07/2025"
__version__ = "1.2"
__status__ = "Development"

#Import modules
import os
import pandas as pd
import time
import re
from datetime import datetime


# Get the current year
current_year = datetime.now().year


readfiles = []
# store the timestamp the script was run to give unique names to the output files
timestampnow = time.strftime('%Y-%b-%d_%H%M', time.localtime())

print(f'Running Script')
print(f'Opening File Paths')

with open("FilePaths.txt", "r") as f:
    lines = f.readlines()

    for i in range(0, len(lines), 1):
        if "Directory" in lines[i]:
            directory = lines[i].split(" = ")[1][:-1]
        elif "Tracker" in lines[i]:
            tracker = lines[i].split(" = ")[1][:-1]
        elif "OID File" in lines[i]:
            OIDfile = lines[i].split(" = ")[1][:-1]
        elif "Output File" in lines[i]:
            outputfile = (lines[i].split(" = ")[1][:-5] + timestampnow + '.csv')

print(f'Opening Tracker File')
            
# open the tracker and read what files have been recently read
with open(tracker, "r") as fp:
    for line in fp:
        x = line[:-1]
        readfiles.append(x)

with open(OIDfile, "r") as foid:
    try:
        OID = int(foid.read())
    except:
        OID = 0
    if not OID:
        OID = 0

inServiceTrucks = 0
enRouteTrucks = 0
proposedTrucks = 0

#Open all of the IAssignment trace logs in the specified directory
print(f'Opening iAssignment Trace Logs')
print(f'Looping through all the logs')
log_files = [f for f in os.listdir(directory) if f.startswith("IAssignmentServer") and f.endswith(".log") and (os.path.getmtime(os.path.join(directory, f)) <= (time.time() - 60*60) or len(f) > 27) and f not in readfiles]
with open(outputfile, "w") as out:
#Loop through all of the logs
    
    for log_file in log_files:
        readfiles.append(log_file)
        with open(os.path.join(directory, log_file), "r") as f:
            lines = f.readlines()
#Loop through each line in each log file
            for i in range(0, len(lines), 1):

#Store truck-specific info from the assignment context prior to the actual destination decisions
                if "[TruckAssignerImpl] Assignment Trigger:" in lines[i]:

                    OID = OID + 1
                    timestamp_raw = str(current_year) + " " + lines[i][:15]
                    dt = datetime.strptime(timestamp_raw, "%Y %b %d %H:%M:%S")
                    timestamp = dt.strftime("%Y/%b/%d %H:%M:%S")
                    trigger = lines[i].split("Trigger: ")[1][:-1]

                if "[TruckAssignerImpl] Truck " in lines[i]:

                    truck = lines[i].split("Truck Origin: Truck ")[1].split()[0]

                    if "waypoint" in lines[i]:
                        location = lines[i].split("waypoint ")[1].split()[0]
                    elif "destination" in lines[i]:
                        location = lines[i].split("destination ")[1].split()[0]
                    else:
                        location = "N/A"
#Store destination specific info from each assignment evaluation
                if "Server: " in lines[i]:
#Provide context for the assignments the engine did not choose
                    
                    ETA = lines[i+1].split("ETA: ")[1].split()[0]

                    if "Reason not assigned: " in lines[i-2]:
                        assigned = False
                        try:
                            reason = lines[i-2].strip().split(" [")[1].split("] ")[0]
                            description = lines[i-2].strip().split("] ")[1]
                        except:
                            reason = "error"
                            description = "error"
                        destination = lines[i].split("Server: ")[1].split()[0]
                        invalid = lines[i + 4].split()[0]
                        invFuture = lines[i + 4].split()[1]
                        asap = lines[i + 4].split()[2]
                        scheduled = lines[i + 4].split()[4]
                        maxQueue = lines[i + 4].split()[5]
                        serverOnDelay = lines[i + 4].split()[6]
                        lockOrBar = lines[i + 4].split()[7]
                        grade = lines[i + 4].split()[9]
                        divert = lines[i + 4].split()[10]
                        circuit = lines[i + 4].split()[11]
                        onPlan = lines[i + 4].split()[12]
                        schPref = lines[i + 4].split()[15]
                        schReq = lines[i + 4].split()[16]
                        dev_cost = lines[i + 4].split()[17]
                        travel_time = lines[i + 4].split()[18]
                        
                        if lines[i+6].strip() == "":
                            actualRate=="" 
                            productionPlanRate==""
                            adjustedTargetRate==""
                            maxRate==""
                            historicalRate==""
                            historicalDuration==""
                        
                        else:                        
                            if lines[i+6].split()[0] == "Actual":
                                j = 6
                            elif lines[i+6].split()[0] == "Remaining":
                                j = 7
                            #Actual Rate: This rate is not the true rate but skewed by the EMA moving rate to be more reactive.
                            # This means it can be higher or lower than the true rate.
                            # It is calculated using history of what was loaded or dumped and also using what material will be moved by the existing assignments
                            actualRate = lines[i + j].split()[2]

                            #Production Plan Rate: This is the flow rate taken from the production plan.
                            productionPlanRate = lines[i + j].split()[7]

                            #Adjusted Target Rate: When computing the amount we want in the future we need to push trucks towards or push them away from a destination. We look at the target rate, take away the amount already dumped there and then give an adjusted future rate.
                            #This adjusted target rate is used in calculating this ratio actualRate / adjustedTargetRate.
                            #This ratio is then used to calculate the production component.
                            adjustedTargetRate = lines[i + j].split()[12]

                            #Maximum Rate: This is the maximum rate for a loading tool or processor.
                            #It is dependent on the number of trucks in the truck classes that can service the loading tool or processor but also looks at the number of trucks that can be serviced at that destination.
                            maxRate = lines[i + j].split()[16]

                            #Historical Rate: This calculates the rate from the material loaded or dumped for an arc.
                            historicalRate = lines[i + j].split()[20]

                            #Historical Duration: This gives the historical duration for an arc from the earliest time some truck was loaded or dumped.
                            historicalDuration = lines[i + j].split()[24]

                            k = i + j + 4

                            while True:

                                if lines[k].strip() == "-----" or lines[k].strip() == "ASAP" or len(lines[k].strip()) == 0:
                                    break

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "in-service":
                                        inServiceTrucks = inServiceTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "en-route":
                                        enRouteTrucks = enRouteTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "proposed":
                                        proposedTrucks = proposedTrucks + 1
                                except:
                                    pass

                                k = k + 1


                    elif "Reason not assigned: " in lines[i-3]:
                        assigned = False
                        try:
                            reason = lines[i - 3].strip().split(" [")[1].split("] ")[0]
                            description = lines[i - 3].strip().split("] ")[1]
                        except:
                            reason = "error"
                            description = "error"
                        destination = lines[i].split("Server: ")[1].split()[0]
                        invalid = lines[i + 4].split()[0]
                        invFuture = lines[i + 4].split()[1]
                        asap = lines[i + 4].split()[2]
                        scheduled = lines[i + 4].split()[4]
                        maxQueue = lines[i + 4].split()[5]
                        serverOnDelay = lines[i + 4].split()[6]
                        lockOrBar = lines[i + 4].split()[7]
                        grade = lines[i + 4].split()[9]
                        divert = lines[i + 4].split()[10]
                        circuit = lines[i + 4].split()[11]
                        onPlan = lines[i + 4].split()[12]
                        schPref = lines[i + 4].split()[15]
                        schReq = lines[i + 4].split()[16]
                        dev_cost = lines[i + 4].split()[17]
                        travel_time = lines[i + 4].split()[18]
                        
                        if lines[i+6].strip() == "":
                            actualRate=="" 
                            productionPlanRate==""
                            adjustedTargetRate==""
                            maxRate==""
                            historicalRate==""
                            historicalDuration==""
                        
                        else:
                            if lines[i + 6].split()[0] == "Actual":
                                j = 6
                            elif lines[i + 6].split()[0] == "Remaining":
                                j = 7

                            actualRate = lines[i + j].split()[2]
                            
                            productionPlanRate = lines[i + j].split()[7]

                            adjustedTargetRate = lines[i + j].split()[12]

                            maxRate = lines[i + j].split()[16]

                            historicalRate = lines[i + j].split()[20]

                            historicalDuration = lines[i + j].split()[24]

                            k = i + j + 4

                            while True:

                                if lines[k].strip() == "-----" or lines[k].strip() == "ASAP" or len(lines[k].strip()) == 0:
                                    break

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "in-service":
                                        inServiceTrucks = inServiceTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "en-route":
                                        enRouteTrucks = enRouteTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "proposed":
                                        proposedTrucks = proposedTrucks + 1
                                except:
                                    pass

                                k = k + 1
                    
                    elif "Reason not assigned: " in lines[i-1]:
                        assigned = False
                        try:
                            reason = lines[i - 1].strip().split(" [")[1].split("] ")[0]
                            description = lines[i - 1].strip().split("] ")[1]
                        except:
                            reason = "error"
                            description = "error"
                        destination = lines[i].split("Server: ")[1].split()[0]
                        invalid = lines[i + 4].split()[0]
                        invFuture = lines[i + 4].split()[1]
                        asap = lines[i + 4].split()[2]
                        scheduled = lines[i + 4].split()[4]
                        maxQueue = lines[i + 4].split()[5]
                        serverOnDelay = lines[i + 4].split()[6]
                        lockOrBar = lines[i + 4].split()[7]
                        grade = lines[i + 4].split()[9]
                        divert = lines[i + 4].split()[10]
                        circuit = lines[i + 4].split()[11]
                        onPlan = lines[i + 4].split()[12]
                        schPref = lines[i + 4].split()[15]
                        schReq = lines[i + 4].split()[16]
                        dev_cost = lines[i + 4].split()[17]
                        travel_time = lines[i + 4].split()[18]
                        
                        if lines[i+6].strip() == "":
                            actualRate=="" 
                            productionPlanRate==""
                            adjustedTargetRate==""
                            maxRate==""
                            historicalRate==""
                            historicalDuration==""
                        
                        else:
                            if lines[i + 6].split()[0] == "Actual":
                                j = 6
                            elif lines[i + 6].split()[0] == "Remaining":
                                j = 7

                            actualRate = lines[i + j].split()[2]
                            
                            productionPlanRate = lines[i + j].split()[7]

                            adjustedTargetRate = lines[i + j].split()[12]

                            maxRate = lines[i + j].split()[16]

                            historicalRate = lines[i + j].split()[20]

                            historicalDuration = lines[i + j].split()[24]

                            k = i + j + 4

                            while True:

                                if lines[k].strip() == "-----" or lines[k].strip() == "ASAP" or len(lines[k].strip()) == 0:
                                    break

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "in-service":
                                        inServiceTrucks = inServiceTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "en-route":
                                        enRouteTrucks = enRouteTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "proposed":
                                        proposedTrucks = proposedTrucks + 1
                                except:
                                    pass

                                k = k + 1
#Provide context for the assignment the engine did choose
                    else:
                        assigned = True
                        reason = "N/A"
                        description = "N/A"
                        destination = lines[i].split("Server: ")[1].split()[0]
                        invalid = lines[i + 4].split()[0]
                        invFuture = lines[i + 4].split()[1]
                        asap = lines[i + 4].split()[2]
                        scheduled = lines[i + 4].split()[4]
                        maxQueue = lines[i + 4].split()[5]
                        serverOnDelay = lines[i + 4].split()[6]
                        lockOrBar = lines[i + 4].split()[7]
                        grade = lines[i + 4].split()[9]
                        divert = lines[i + 4].split()[10]
                        circuit = lines[i + 4].split()[11]
                        onPlan = lines[i + 4].split()[12]
                        schPref = lines[i + 4].split()[15]
                        schReq = lines[i + 4].split()[16]
                        dev_cost = lines[i + 4].split()[17]
                        travel_time = lines[i + 4].split()[18]

                        if lines[i+6].strip() == "":
                            actualRate=="" 
                            productionPlanRate==""
                            adjustedTargetRate==""
                            maxRate==""
                            historicalRate==""
                            historicalDuration==""
                        
                        else:
                            if lines[i + 6].split()[0] == "Actual":
                                j = 6
                            elif lines[i + 6].split()[0] == "Remaining":
                                j = 7
                            
                            actualRate = lines[i + j].split()[2]
                            
                            productionPlanRate = lines[i + j].split()[7]

                            adjustedTargetRate = lines[i + j].split()[12]

                            maxRate = lines[i + j].split()[16]

                            historicalRate = lines[i + j].split()[20]

                            historicalDuration = lines[i + j].split()[24]

                            k = i + j + 4

                            while True:

                                if lines[k].strip() == "-----" or lines[k].strip() == "ASAP" or len(lines[k].strip()) == 0:
                                    break

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "in-service":
                                        inServiceTrucks = inServiceTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "en-route":
                                        enRouteTrucks = enRouteTrucks + 1
                                except:
                                    pass

                                try:
                                    if lines[k].split("(")[1].split(")")[0] == "proposed":
                                        proposedTrucks = proposedTrucks + 1
                                except:
                                    pass

                                k = k + 1
#It displays weird when there's scheduled assignments
                    
                    if destination == "at":
                        destination = "Scheduled Assignment"

                    if reason == "Dev":

                        if description.split()[4] == "has":
                            devReason = "Travel Component"

                        elif description.split()[4] == "results":
                            devReason = "Production Plan Overrun"

                        else:
                            devReason = "Other Production Plan Priority"

                    else:
                        devReason = "NA"

#Write the new data into the text file and generate an excel file which is where the magic happens for now
                    out.write(f"{str(OID)}\t{str(timestamp)}\t{str(truck)}\t{str(location)}\t{str(trigger)}\t{str(destination)}\t{str(ETA)}\t{str(assigned)}\t{str(reason)}\t{str(description)}\t{str(inServiceTrucks)}\t{str(enRouteTrucks)}\t{str(proposedTrucks)}\t{str(devReason)}\t{str(invalid)}\t{str(invFuture)}\t{str(asap)}\t{str(scheduled)}\t{str(maxQueue)}\t{str(serverOnDelay)}\t{str(lockOrBar)}\t{str(divert)}\t{str(circuit)}\t{str(onPlan)}\t{str(schPref)}\t{str(schReq)}\t{str(dev_cost)}\t{str(travel_time)}\t{str(actualRate)}\t{str(productionPlanRate)}\t{str(adjustedTargetRate)}\t{str(maxRate)}\t{str(historicalRate)}\t{str(historicalDuration)}\n")

                    enRouteTrucks = 0
                    inServiceTrucks = 0
                    proposedTrucks = 0

readfiles = readfiles[-1000:]

print(f'Updating Read File')
with open(tracker, "w") as fp:
    for readfile in readfiles:
        fp.write("%s\n" % readfile)

with open(OIDfile, "w") as foid:
    foid.write(str(OID))

df = pd.read_csv(outputfile, sep='\t',names=['OID','Timestamp', 'Truck', 'Location', 'Trigger','Destination', 'ETA', 'Assigned', 'Reason', 'Description', 'In Service Trucks', 'En-Route Trucks', 'Proposed Trucks', 'Deviation Reason', 'Invalid Assignment', 'Invalid Future Assignment', 'ASAP Assignment', 'Scheduled Assignment', 'Max Queue', 'Server on Delay', 'Lock or Bar', 'Divert', 'Circuit', 'On Production Plan', 'Scheduled Assignment Preference', 'Scheduled Assignment Required', 'Deviation Cost', 'Travel Time', 'Actual Rate', 'Production Plan Rate', 'Adjusted Target Rate', 'Max Rate', 'Historical Rate', 'Historical Duration'])
df.replace('-', '0', inplace=True)
df.to_csv(outputfile, sep=',', index=False)
print(f'Output File Created')


# In[ ]:




