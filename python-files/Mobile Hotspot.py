#Mobiler Hotspot
command=input("What Language would you like?\nWelche Sprache wählen Sie?\nFor English press e.\nFür Deutsch drücken sie g.\nPlease press Enter to continue.\nBitte drücken sie Enter um zu bestätigen.\n")
if command=="e":
	ssid=input("What name(ssid) would you like for your Mobile Wlan Hotspot?\n")
	key_yes_or_no=input("Would you like a Password?\nPress y if you like a Password?\nPress n if you dont like a Password\n")
	if key_yes_or_no=="y":
		key=input("What Password would you like?")
		make=("C:\Windows\System32\netsh.exe netsh wlan set hostednetwork mode=allow ssid={} key={} keyUsage=persistent".format(ssid,key))
		start=("C:\Windows\System32\netsh.exe netsh wlan start hostednetwork")
		stop=("C:\Windows\System32\netsh.exe netsh wlan stop hostednetwork")
		print("Please make 3 Links on your Desktop:\n\make\nPath:\n{}\n\start\nPath:\n{}\n\nstop\nPath:\n{}\n\n\nPlease stat make as Administrator to make your mobile hotspot.\nWith start you start it and with stop you stop it.".format(erstellen,starten,beenden))

	if key_yes_or_no=="n":
		print("Ok")
		make=("C:\Windows\System32\netsh.exe netsh wlan set hostednetwork mode=allow ssid={} keyUsage=persistent".format(ssid))
		start=("C:\Windows\System32\netsh.exe netsh wlan start hostednetwork")
		stop=("C:\Windows\System32\netsh.exe netsh wlan stop hostednetwork")
		print("Please make 3 Links on your Desktop:\n\make\nPath:\n{}\n\start\nPath:\n{}\n\nstop\nPath:\n{}\n\n\nPlease stat make as Administrator to make your mobile hotspot.\nWith start you start it and with stop you stop it.".format(erstellen,starten,beenden))

if command=="g":
	ssid=input("Welchen Namen(SSID) soll ihr Mobiler Hotspot haben?\n")
	key_yes_or_no=input("Möchten sie einen Sicherheitsschlüssel(Passwort)?\nDrücken Sie j wenn sie einen Möchten.\nDrücken Sie n Wenn Sie keinen möchten.\n")
	if key_yes_or_no=="j":
		key=input("Welchen Sicherheitsschlüssel möchten Sie?\n")
		erstellen=("C:\Windows\System32\netsh.exe netsh wlan set hostednetwork mode=allow ssid={} key={} keyUsage=persistent".format(ssid,key))
		starten=("C:\Windows\System32\netsh.exe netsh wlan start hostednetwork")
		beenden=("C:\Windows\System32\netsh.exe netsh wlan stop hostednetwork")
		print("Bitte erstellen Sie 3 Verknüpfungen auf ihrem Desktop:\n\nErstellen\nPfad(Speicerort des Elements):\n{}\n\nStarten\nPfad:\n{}\n\nBeenden\nPfad:\n{}\n\n\nBitte führen Sie Erstellen als Administrator aus, um Ihren Mobilen Hotspot zu erstellen.\nMit Starten starten Sie ihn und mit beenden beenden sie ihn.".format(erstellen,starten,beenden))
	if key_yes_or_no=="n":
		print(Ok)
		erstellen=("C:\Windows\System32\netsh.exe netsh wlan set hostednetwork mode=allow ssid={} keyUsage=persistent".format(ssid))
		starten=("C:\Windows\System32\netsh.exe netsh wlan start hostednetwork")
		beenden=("C:\Windows\System32\netsh.exe netsh wlan stop hostednetwork")
		print("Bitte erstellen Sie 3 Verknüpfungen auf ihrem Desktop:\n\nErstellen\nPfad(Speicerort des Elements):\n{}\n\nStarten\nPfad:\n{}\n\nBeenden\nPfad:\n{}\n\n\nBitte führen Sie Erstellen als Administrator aus, um Ihren Mobilen Hotspot zu erstellen.\nMit Starten starten Sie ihn und mit beenden beenden sie ihn.".format(erstellen,starten,beenden))
