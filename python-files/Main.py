import requests
import xml.etree.ElementTree as ET
import time

timestr = time.strftime("%d-%m-%Y")
# Define the API endpoint and parameters
api_url = "https://10.0.111.1/api/?type=export&category=configuration&key="
api_key = "LUFRPT0xL3VKcGQweEVrRWlwWVhkRFZVRnZ5RDdWT2M9ejAyNktlT0ZHc3lONWNla2xpRGJFR3UrcE5GbkVuZnRZRFJoc3NNdzNjWkxtMVV1UmMvMHhuU001bnZHbjdWUw=="
params = {"key": api_key}
requests.packages.urllib3.disable_warnings()
response = requests.get(api_url, params=params, verify=False)  # Set verify=False if using self-signed certificates
if response.status_code == 200:
    data = response.text
    root1 = ET.Element(data)
    #print(root1)
    b_xml = ET.tostring(root1)
    with open("HQ_PaloAlto_Config_Backup-"+timestr+".xml", "wb") as f:
        f.write(b_xml)

else:
    print(f"Error: {response.status_code}, {response.reason}")



