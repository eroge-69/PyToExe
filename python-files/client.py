
from pystyle import Colors, Colorate, Anime, Center
import requests
import asyncio
import json
import os

config = {}
connect = True

class Main:
	async def serverRequest(packet={"packet": "none"}):
		host = "http://127.0.0.1:7888"
		return requests.post(host, json=packet)
	
	async def packetHandler(packet):
		global config, connect
		packets = packet.json()
		if "packet" in packets[0]:
			if packets[0]["packet"] == "config":
				config = packets[0]
				return

		os.system('cls' if os.name == 'nt' else 'clear')
		for packet in packets:
			if packet["packet"] == "input":
				await Main.packetHandler(await Main.serverRequest({"packet": "input", "message": input(Colorate.Horizontal(config["theme"], packet["message"])), "index": packet["index"]}))
			elif packet["packet"] == "inputcolor":
				await Main.packetHandler(await Main.serverRequest({"packet": "input", "message": input(Colorate.Horizontal(packet["color"], packet["message"])), "index": packet["index"]}))
			elif packet["packet"] == "console":
				print(Colorate.Horizontal(config["theme"], f"\n{packet['message']}\n"))
			elif packet["packet"] == "consolecolor":
				print(Colorate.Horizontal(packet["color"], f"\n{packet['message']}\n"))
			elif packet["packet"] == "end":
				connect = False
			if "cd" in packet:
				await asyncio.sleep(packet["cd"])

	async def run():
		global config, connect
		while connect:
			answer = False
			for i in range(10):
				try:
					await Main.serverRequest()
					answer = True
					break
				except Exception as e:
					print(f"server not connect, retry: {i+1} wait...")
					await asyncio.sleep(3)
			if not answer:
				print("Server stoped..")
				break

			await Main.packetHandler(await Main.serverRequest({"packet": "config"}))
			await Main.packetHandler(await Main.serverRequest({"packet": "start"}))
		
if __name__ == "__main__":
	asyncio.run(Main.run())
