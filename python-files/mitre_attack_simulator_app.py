import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import filedialog

#########################################################################################################################################################################################
#########################################################################################################################################################################################
# this is the code for the MITRE ATT&CK Tabletop Simulator Author: Kenneth Ray. This will create a GUI that allows you to simulate different MITRE ATT&CK tactics and generate a scenario.
# The GUI will allow you to select which tactics you want to simulate, and the scenario will be generated in the text box below.
# The scenario will be generated in the text box inside the GUI.
# it will also allow you to save the scenario to a file.
#########################################################################################################################################################################################


############################################################################################################################################################################################
############################################################### Data classifications #######################################################################################################
## Each data classification has a name, id, and a list of subcategories it contains a table top observable for each subcategory
## this is used in the random generation of each defined tactic.
############################################################################################################################################################################################

############################################################## Reconnaissance techniques (TA0043) ######################################################################################

recon_techniques = [
    {
        "name": "Active Scanning",
        "id": "T1595",
        "sub": [
            ("Scanning IP Blocks", "T1595.001",
             "Network logs show ICMP echo requests targeting sequential IPs in the 10.0.0.0/24 range."),
            ("Vulnerability Scanning", "T1595.002",
             "Web server logs indicate a flood of HTTP requests probing endpoints like /admin or /phpmyadmin."),
            ("Wordlist Scanning", "T1595.003",
             "The perimeter firewall logged repeated 404 responses from attempts to reach common directory names such as /backup/, /test/, and /old/.")
        ]
    },
    {
        "name": "Gather Victim Host Information",
        "id": "T1592",
        "sub": [
            ("Hardware", "T1592.001",
             "SNMP queries retrieved system model names and serial numbers from multiple hosts."),
            ("Software", "T1592.002",
             "Endpoints initiated unusual outbound connections immediately following software inventory collection."),
            ("Firmware", "T1592.003",
             "An asset discovery tool captured BIOS and firmware versions across various network zones."),
            ("Client Configurations", "T1592.004",
             "Web proxy logs show browser fingerprinting attempts via custom JavaScript payloads.")
        ]
    },
    {
        "name": "Gather Victim Org Information",
        "id": "T1591",
        "sub": [
            ("Determine Physical Locations", "T1591.001",
             "Traffic analysis indicated repeated connection attempts from an IP geolocated near a secure facility."),
            ("Business Relationships", "T1591.002",
             "A trusted vendor notified they werew recently breached by an adversary-linked company."),
            ("Identify Business Tempo", "T1591.003",
             "Phishing campaigns mirrored the organization's financial reporting cadence."),
            ("Identify Roles", "T1591.004",
             "Profiles were scraped on LinkedIn seeking employees in admin and security roles.")
        ]
    }
]

############################################################ Resource Development techniques (TA0042) ##################################################################################

resource_dev_techniques = [
    {
        "name": "Acquire Infrastructure",
        "id": "T1583",
        "sub": [
            ("Domains", "T1583.001",
             "A newly registered domain closely mimicking your company’s name was observed resolving against internal servers."),
            ("DNS Server", "T1583.002",
             "External DNS servers were configured that divert queries from your domain to unknown IP addresses."),
            ("Virtual Private Server", "T1583.003",
             "Outbound traffic was traced to a leased VPS located in a high-risk region correlating with initial phishing dispatch."),
            ("Server", "T1583.004",
             "Internet scans revealed a newly accessible server that appears provisioned for C2 operations."),
            ("Botnet", "T1583.005",
             "Endpoint telemetry logged beaconing to IPs recognized as botnet command-and-control infrastructure."),
            ("Web Services", "T1583.006",
             "Adversaries were seen leveraging generic web services (e.g., public file-sharing platforms) for data exfiltration."),
            ("Serverless", "T1583.007",
             "Connections were observed to serverless cloud functions (e.g., AWS Lambda) being used as proxies to evade detection."),
            ("Malvertising", "T1583.008",
             "Security tools flagged malicious ad campaigns that redirected users to phishing domains mimicking your login portal.")
        ]
    },
    {
        "name": "Establish Accounts",
        "id": "T1585",
        "sub": [
            ("Social Media Accounts", "T1585.001",
             "A fake LinkedIn account impersonating a senior manager was created and used to send connection requests."),
            ("Email Accounts", "T1585.002",
             "An email address with minor typos of your domain was seen sending credential-collection emails to employees.")
        ]
    },
    {
        "name": "Obtain Capabilities",
        "id": "T1588",
        "sub": [
            ("Malware", "T1588.001",
             "A newly surfaced malware sample was uploaded to VirusTotal that targets your endpoint client."),
            ("Tool", "T1588.002",
             "Your organization was included in a third-party report featuring a tool targeting your VPN appliance."),
            ("Code Signing Certificates", "T1588.003",
             "Suspicious code-signing certificates were issued for domains resembling your asset names."),
            ("Digital Certificates", "T1588.004",
             "A Let’s Encrypt certificate was issued for a phishing domain masquerading as your portal."),
            ("Exploits", "T1588.005",
             "Dark web posts included a live exploit exploit aligning with a critical vulnerability on your perimeter."),
            ("Vulnerabilities", "T1588.006",
             "A vulnerability database record indicates unpatched systems matching your public IP range."),
            ("Artificial Intelligence", "T1588.007",
             "Activity detected where adversaries utilized AI tools to craft phishing content tailored to your organizational branding.")
        ]
    }
]

############################################################## initaial_access_techniques (TA0001) ####################################################################################

initial_access_techniques = [
    {
        "name": "Drive-by Compromise",
        "id": "T1189",
        "sub": [
            ("Drive-by Compromise", "T1189",
             "Web proxy logs show users redirected to a suspicious site that loads obfuscated JavaScript and browser exploits.")
        ]
    },
    {
        "name": "Exploit Public-Facing Application",
        "id": "T1190",
        "sub": [
            ("Exploit Public-Facing Application", "T1190",
             "External scans show exploitation of a known vulnerability (e.g., Log4Shell) on a public web application.")
        ]
    },
    {
        "name": "Hardware Additions",
        "id": "T1200",
        "sub": [
            ("Hardware Additions", "T1200",
             "Physical security logs indicate a USB device was inserted into a secure workstation outside of working hours.")
        ]
    },
    {
        "name": "Phishing",
        "id": "T1566",
        "sub": [
            ("Spearphishing Attachment", "T1566.001",
             "Multiple users reported receiving emails with suspicious attachments named like 'HR_Policy_Update.pdf.exe'."),
            ("Spearphishing Link", "T1566.002",
             "Clickstream data shows employees accessing a fake login page hosted on a domain that mimics the company’s name."),
            ("Spearphishing via Service", "T1566.003",
             "A message sent through Microsoft Teams contained a malicious link disguised as a document shared from OneDrive.")
        ]
    },
    {
        "name": "Replication Through Removable Media",
        "id": "T1091",
        "sub": [
            ("Replication Through Removable Media", "T1091",
             "A malware alert was triggered after a file on a USB stick was executed on an air-gapped machine.")
        ]
    },
    {
        "name": "Supply Chain Compromise",
        "id": "T1195",
        "sub": [
            ("Compromise Software Dependencies and Development Tools", "T1195.001",
             "A compromised third-party npm package was found executing post-install scripts to download additional payloads."),
            ("Compromise Software Supply Chain", "T1195.002",
             "An internal tool was updated with malicious code after a compromise in a contractor’s source repo."),
            ("Compromise Hardware Supply Chain", "T1195.003",
             "Security team discovered undocumented firmware behavior in a batch of new devices from a supplier.")
        ]
    },
    {
        "name": "Trusted Relationship",
        "id": "T1199",
        "sub": [
            ("Trusted Relationship", "T1199",
             "A partner VPN account was used to access internal systems from an unrecognized IP address without MFA.")
        ]
    },
    {
        "name": "Valid Accounts",
        "id": "T1078",
        "sub": [
            ("Local Accounts", "T1078.001",
             "Authentication logs show unusual logins to privileged local accounts outside business hours."),
            ("Domain Accounts", "T1078.002",
             "A domain admin account was used to access resources in a way inconsistent with normal patterns."),
            ("Cloud Accounts", "T1078.004",
             "An API token tied to a cloud account was used from a foreign IP for administrative operations."),
            ("Default Accounts", "T1078.003",
             "A default admin account (e.g., admin:admin) was successfully used to access a web management portal.")
        ]
    }
]

################################################################ execution_techniques (TA0002) ########################################################################################

execution_techniques = [
    {
        "name": "Command and Scripting Interpreter",
        "id": "T1059",
        "sub": [
            ("PowerShell", "T1059.001",
             "PowerShell logs reveal encoded commands executed via an Invoke-Expression call under SYSTEM context."),
            ("AppleScript", "T1059.002",
             "Mac audit logs show AppleScript triggered GUI events to open sensitive files without user interaction."),
            ("Cloud API", "T1059.009",
             "Cloud monitoring shows API calls to AWS SSM RunCommand executing payloads on EC2 instances."),
            ("AutoHotKey/AutoIT", "T1059.010",
             "Security software flagged an AutoIt script automating application installs with hidden payloads."),
            ("Lua", "T1059.011",
             "Application logs show embedded Lua scripts invoked to execute unauthorized network connections."),
            ("Hypervisor CLI", "T1059.012",
             "Hypervisor logs show CLI commands injected to modify VM snapshots outside maintenance windows.")
        ]
    },
    {
        "name": "Exploit Public-Facing Application",
        "id": "T1190",
        "sub": [
            ("Exploit Public-Facing Application", "T1190",
             "Web application firewall logs show a suspicious payload exploiting a known CVE in the web login interface.")
        ]
    },
    {
        "name": "Drive-by Compromise",
        "id": "T1189",
        "sub": [
            ("Drive-by Compromise", "T1189",
             "Proxy logs record redirects from legitimate site to a malicious exploit domain delivering obfuscated JS payloads.")
        ]
    },
    {
        "name": "Cloud Administration Command",
        "id": "T1651",
        "sub": [
            ("Cloud Administration Command", "T1651",
             "Cloud audit logs show unauthorized use of Azure RunCommand to deploy scripts on virtual machines.")
        ]
    },
    {
        "name": "Container Administration Command",
        "id": "T1609",
        "sub": [
            ("Container Administration Command", "T1609",
             "Kubernetes audit logs show exec into containers orchestrated outside CI/CD pipelines.")
        ]
    },
    {
        "name": "Deploy Container",
        "id": "T1610",
        "sub": [
            ("Deploy Container", "T1610",
             "Logging indicates a new privileged container deployed by an unknown user in production namespace.")
        ]
    },
    {
        "name": "Exploit for Client Execution",
        "id": "T1203",
        "sub": [
            ("Exploit for Client Execution", "T1203",
             "User endpoint logs show exploitation of a vulnerable media player via crafted file to trigger code execution.")
        ]
    },
    {
        "name": "Inter-Process Communication",
        "id": "T1559",
        "sub": [
            ("Component Object Model (COM)", "T1559.001",
             "Process creation logs show a COM call used to launch DLL injection into explorer.exe."),
            ("Dynamic Data Exchange (DDE)", "T1559.002",
             "Email attachment triggered a DDE auto-send macro that executed a payload via Word.")
        ]
    },
    {
        "name": "Service Execution",
        "id": "T1206",  # conceptual placeholder; MITRE specific subtech missing
        "sub": [
            ("Service Execution", "T1206",
             "Registry and service manager logs show a new service created to run malware at startup.")
        ]
    }
]

############################################################# persistence techniques (TA0003) #########################################################################################


persistence_techniques = [
    {
        "name": "Account Manipulation",
        "id": "T1098",
        "sub": [
            ("Create Account", "T1136",
             "Audit logs show a newly created admin-level user account with no recent business justification."),
            ("Modify Existing Account", "T1098.002",
             "Security alerts capture privilege escalation of an existing account to domain admin."),
        ]
    },
    {
        "name": "Scheduled Task/Job",
        "id": "T1053",
        "sub": [
            ("At (Windows, Unix)", "T1053.002",
             "Task history logs show a scheduled job created using 'at' to run malicious script at reboot."),
            ("Cron", "T1053.003",
             "Crontab entries were added to execute a script hourly, unrelated to standard administration."),
            ("Scheduled Task (schtasks)", "T1053.005",
             "A Windows scheduled task was created to launch PowerShell payload at login via schtasks.")
        ]
    },
    {
        "name": "Boot or Logon Autostart Execution",
        "id": "T1547",
        "sub": [
            ("Registry Run Keys / Startup Folder", "T1547.001",
             "Registry Run key was modified to launch malware on boot; detected via registry auditing."),
            ("Active Setup", "T1547.014",
             "Registry Active Setup key added entry to execute unknown .exe after user logs in."),
            ("Login Items (Mac)", "T1547.015",
             "Mac endpoint logs show a new login item added to automatically open a malicious app at login."),
            ("Boot or Logon Initialization Scripts", "T1547.003",
             "Startup scripts were found modified to include execution of unauthorized scripts at boot.")
        ]
    },
    {
        "name": "Hijack Execution Flow",
        "id": "T1574",
        "sub": [
            ("DLL Search Order Hijacking", "T1574.001",
             "Security event logs show that a malicious DLL was loaded due to hijacked search path."),
            ("Other Hijack Execution Flow", "T1574.999",  # catch-all
             "Indicators show unauthorized control flow redirection via altered binary logic.")
        ]
    },
    {
        "name": "Event Triggered Execution",
        "id": "T1546",
        "sub": [
            ("WMI Event Subscription", "T1546.003",
             "WMI subscription created to run script on system event; logged in WMI repository."),
            ("Screensaver", "T1546.002",
             "Screensaver executable was replaced with a malicious .scr that executes when idle."),
        ]
    },
    {
        "name": "Web Shell",
        "id": "T1505.003",
        "sub": [
            ("Web Shell", "T1505.003",
             "Unexpected web shell file detected on server, allowing remote code execution via web requests.")
        ]
    },
    {
        "name": "Server Software Component",
        "id": "T1505",
        "sub": [
            ("SQL Stored Procedures", "T1505.001",
             "Database logs show creation of malicious stored procedure enabling persistent backdoor access.")
        ]
    },
    {
        "name": "Other Techniques",
        "id": "T1543",
        "sub": [
            ("Systemd Service", "T1543.002",
             "New systemd service was registered to run unauthorized binary on system startup."),
            ("Service Registry Permissions Weakness", "T1543.003",
             "A service's registry permissions were weakened allowing attackers to replace its binary path.")
        ]
    }
]

############################################################# PRIVILEGE ESCALATION (TA0004) ###########################################################################################

privilege_escalation_techniques = [
    {
        "name": "Abuse Elevation Control Mechanism",
        "id": "T1548",
        "sub": [
            ("Bypass User Access Control", "T1548.002",
             "System logs show execution of a binary that bypassed User Account Control (UAC) prompting."),
            ("Sudo and Sudo Caching", "T1548.003",
             "Command history reveals a user exploited cached sudo privileges to run unauthorized commands."),
            ("Setuid and Setgid", "T1548.001",
             "A setuid-root executable was modified, enabling privilege escalation on Linux endpoints."),
        ]
    },
    {
        "name": "Exploitation for Privilege Escalation",
        "id": "T1068",
        "sub": [
            ("Exploitation for Privilege Escalation", "T1068",
             "Exploit attempt detected targeting a known Windows kernel vulnerability to escalate privileges.")
        ]
    },
    {
        "name": "Process Injection",
        "id": "T1055",
        "sub": [
            ("DLL Injection", "T1055.001",
             "Security logs reveal DLL injection into a high-privilege process like lsass.exe."),
            ("Reflective DLL Injection", "T1055.002",
             "Memory forensics detected reflective DLL injection to evade disk-based detection."),
            ("Process Hollowing", "T1055.003",
             "Analysis shows a legitimate process hollowed out and replaced with malicious code."),
            ("Thread Execution Hijacking", "T1055.004",
             "Malware hijacked a thread in a system process to execute with elevated privileges."),
            ("Atom Bombing", "T1055.005",
             "Unusual usage of Windows Atom Tables to inject code into privileged processes observed.")
        ]
    },
    {
        "name": "Valid Accounts",
        "id": "T1078",
        "sub": [
            ("Local Accounts", "T1078.001",
             "Local admin account used to execute commands inconsistent with normal user activity."),
            ("Domain Accounts", "T1078.002",
             "Domain account privileges escalated and used during off-hours on sensitive systems."),
            ("Cloud Accounts", "T1078.004",
             "Cloud admin account accessed management console from an unexpected location."),
            ("Default Accounts", "T1078.003",
             "Default credentials found and used to gain elevated access on network devices.")
        ]
    },
    {
        "name": "Setuid and Setgid",
        "id": "T1548.001",
        "sub": [
            ("Setuid and Setgid", "T1548.001",
             "An unusual setuid executable was found on a Linux system allowing privilege escalation.")
        ]
    },
    {
        "name": "Accessibility Features",
        "id": "T1546.008",
        "sub": [
            ("Accessibility Features", "T1546.008",
             "An accessibility feature was enabled to allow execution of unauthorized code at login.")
        ]
    },
    {
        "name": "Boot or Logon Autostart Execution",
        "id": "T1547",
        "sub": [
            ("Boot or Logon Autostart Execution", "T1547",
             "A service or startup item was modified to launch with elevated privileges upon reboot.")
        ]
    }
]

################################################################## Defence Evasion (TA0005) ##########################################################################################

defense_evasion_techniques = [
    {
        "name": "Impair Defenses",
        "id": "T1562",
        "sub": [
            ("Disable or Modify Tools", "T1562.001",
             "EDR logs show the endpoint agent's service was stopped by an unauthorized process."),
            ("Disable Windows Event Logging", "T1562.002",
             "Windows audit logs reveal a script cleared security event logs during lateral movement."),
            ("Disable or Modify System Firewall", "T1562.004",
             "Local firewall settings were disabled via PowerShell on multiple workstations simultaneously."),
        ]
    },
    {
        "name": "Obfuscated Files or Information",
        "id": "T1027",
        "sub": [
            ("Software Packing", "T1027.002",
             "Binary uploaded to the endpoint was packed using a commercial packer to evade signature-based detection."),
            ("Steganography", "T1027.003",
             "Threat hunting identified malicious code hidden inside an image file downloaded from an internal web server."),
            ("Encoding/Encryption", "T1027.001",
             "PowerShell scripts used Base64-encoded payloads decoded at runtime to avoid detection."),
        ]
    },
    {
        "name": "Masquerading",
        "id": "T1036",
        "sub": [
            ("Match Legitimate Name or Location", "T1036.005",
             "A malicious executable was named 'svchost.exe' and placed in the System32 directory."),
            ("Masquerade Task or Service", "T1036.004",
             "A new service named 'Windows Update Helper' was created but linked to a suspicious binary."),
        ]
    },
    {
        "name": "Modify Registry",
        "id": "T1112",
        "sub": [
            ("Modify Registry", "T1112",
             "Registry keys were modified to disable Windows Defender real-time monitoring.")
        ]
    },
    {
        "name": "Indicator Removal on Host",
        "id": "T1070",
        "sub": [
            ("Clear Windows Event Logs", "T1070.001",
             "A script executed to clear all Windows event logs just prior to malware execution."),
            ("File Deletion", "T1070.004",
             "Temporary payload files were deleted immediately after execution to evade forensic recovery."),
            ("Clear Command History", "T1070.003",
             "Bash history was manually cleared after a series of suspicious commands were run."),
        ]
    },
    {
        "name": "Signed Binary Proxy Execution",
        "id": "T1218",
        "sub": [
            ("Rundll32", "T1218.011",
             "Rundll32.exe was used to execute a DLL from a non-standard directory."),
            ("Mshta", "T1218.005",
             "Mshta.exe launched a remote HTML applet containing embedded JavaScript malware."),
            ("InstallUtil", "T1218.004",
             "InstallUtil.exe was used to install a .NET assembly that wasn't part of any known software deployment."),
        ]
    },
    {
        "name": "Modify Authentication Process",
        "id": "T1556",
        "sub": [
            ("Network Provider DLL", "T1556.002",
             "A custom network provider DLL was registered to intercept and forward credentials during login."),
        ]
    },
    {
        "name": "Rootkit",
        "id": "T1014",
        "sub": [
            ("Rootkit", "T1014",
             "Kernel-level driver found hiding process activity from the Task Manager and sysmon.")
        ]
    },
    {
        "name": "File and Directory Permissions Modification",
        "id": "T1222",
        "sub": [
            ("Linux and Mac File Permissions Modification", "T1222.002",
             "File permissions were modified using chmod to allow world write on a sensitive script."),
        ]
    }
]

################################################################# Credential Access (TA0006) ##########################################################################################

credential_access_techniques = [
    {
        "name": "Brute Force",
        "id": "T1110",
        "sub": [
            ("Password Guessing", "T1110.001",
             "Authentication logs show repeated login attempts with common passwords across multiple accounts."),
            ("Password Spraying", "T1110.003",
             "SIEM alerts triggered on successful logins after multiple failed attempts using common passwords."),
            ("Credential Stuffing", "T1110.004",
             "Multiple user accounts accessed using previously leaked credentials from another breach."),
        ]
    },
    {
        "name": "Credential Dumping",
        "id": "T1003",
        "sub": [
            ("LSASS Memory", "T1003.001",
             "Memory dump of lsass.exe detected; common technique for harvesting user passwords."),
            ("SAM", "T1003.002",
             "The Security Account Manager (SAM) file was accessed and copied to a remote location."),
            ("DCSync", "T1003.006",
             "DC logs show a standard user account issuing DCSync requests for all domain credentials."),
            ("LSA Secrets", "T1003.004",
             "Registry access logs show dumping of LSA Secrets for stored service account passwords.")
        ]
    },
    {
        "name": "Input Capture",
        "id": "T1056",
        "sub": [
            ("Keylogging", "T1056.001",
             "User reports sluggish performance; endpoint inspection found hidden keylogger in user space."),
            ("GUI Input Capture", "T1056.002",
             "Malware captured GUI interactions to bypass multi-factor prompts."),
            ("Credential API Hooking", "T1056.004",
             "DLL injected into explorer.exe hooked credential input fields at the OS level.")
        ]
    },
    {
        "name": "Unsecured Credentials",
        "id": "T1552",
        "sub": [
            ("Credentials in Files", "T1552.001",
             "AWS access keys were found in plaintext within a developer’s script directory."),
            ("Credentials in Registry", "T1552.002",
             "Windows registry contained plaintext service credentials for a third-party application."),
            ("Private Keys", "T1552.004",
             "A private SSH key was stored unencrypted in a shared folder accessible to all domain users.")
        ]
    },
    {
        "name": "Steal or Forge Kerberos Tickets",
        "id": "T1558",
        "sub": [
            ("Golden Ticket", "T1558.001",
             "Security logs show use of a forged TGT with a 10-year expiration — indicating Golden Ticket attack."),
            ("Silver Ticket", "T1558.002",
             "Unusual access to a specific service using forged service tickets detected."),
        ]
    },
    {
        "name": "Forced Authentication",
        "id": "T1187",
        "sub": [
            ("Forced Authentication", "T1187",
             "SMB traffic showed NTLM authentication attempts sent to an attacker-controlled system.")
        ]
    },
    {
        "name": "Adversary-in-the-Middle",
        "id": "T1557",
        "sub": [
            ("LLMNR/NBT-NS Poisoning and Relay", "T1557.001",
             "NetBIOS poisoning detected, enabling credential interception during name resolution.")
        ]
    },
    {
        "name": "Man-in-the-Middle",
        "id": "T1557.002",
        "sub": [
            ("Man-in-the-Middle", "T1557.002",
             "A rogue network device was intercepting traffic and replaying captured credentials.")
        ]
    }
]

################################################################# Discovery (TA0007) #################################################################################################
discovery_techniques = [
    {
        "name": "Account Discovery",
        "id": "T1087",
        "sub": [
            ("Local Account", "T1087.001",
             "Adversary used 'net user' or 'Get-LocalUser' to list all local accounts on a compromised host."),
            ("Domain Account", "T1087.002",
             "PowerShell used to enumerate domain users from a workstation."),
            ("Email Account", "T1087.003",
             "Email headers accessed to discover internal user address formats for future phishing.")
        ]
    },
    {
        "name": "System Information Discovery",
        "id": "T1082",
        "sub": [
            ("System Information Discovery", "T1082",
             "Commands like 'systeminfo' or 'uname -a' were run to gather OS and patch level details.")
        ]
    },
    {
        "name": "Process Discovery",
        "id": "T1057",
        "sub": [
            ("Process Discovery", "T1057",
             "Adversary ran tasklist or ps commands to identify running processes and security tools.")
        ]
    },
    {
        "name": "System Owner/User Discovery",
        "id": "T1033",
        "sub": [
            ("System Owner/User Discovery", "T1033",
             "User context determined via 'whoami' and 'query user'; helps scope privilege levels.")
        ]
    },
    {
        "name": "Permission Groups Discovery",
        "id": "T1069",
        "sub": [
            ("Local Groups", "T1069.001",
             "Audit logs show enumeration of local groups to identify privileged accounts."),
            ("Domain Groups", "T1069.002",
             "LDAP queries used to list domain groups and roles assigned to user accounts.")
        ]
    },
    {
        "name": "Network Service Scanning",
        "id": "T1046",
        "sub": [
            ("Network Service Scanning", "T1046",
             "Nmap scans or PowerShell TCP pings were run from compromised endpoints.")
        ]
    },
    {
        "name": "Network Share Discovery",
        "id": "T1135",
        "sub": [
            ("Network Share Discovery", "T1135",
             "SMB shares were queried and mapped, identifying accessible file shares.")
        ]
    },
    {
        "name": "Remote System Discovery",
        "id": "T1018",
        "sub": [
            ("Remote System Discovery", "T1018",
             "Adversary listed connected remote systems using net view or custom scripts.")
        ]
    },
    {
        "name": "Software Discovery",
        "id": "T1518",
        "sub": [
            ("Security Software Discovery", "T1518.001",
             "AV and EDR presence identified through registry keys and known process names.")
        ]
    },
    {
        "name": "Cloud Infrastructure Discovery",
        "id": "T1580",
        "sub": [
            ("Cloud Infrastructure Discovery", "T1580",
             "Cloud CLI commands used to list EC2, IAM roles, and cloud configurations.")
        ]
    },
    {
        "name": "Cloud Service Dashboard",
        "id": "T1538",
        "sub": [
            ("Cloud Service Dashboard", "T1538",
             "Browser history shows access to AWS/Azure console to observe service usage.")
        ]
    },
    {
        "name": "File and Directory Discovery",
        "id": "T1083",
        "sub": [
            ("File and Directory Discovery", "T1083",
             "Recursive searches for sensitive filenames and file extensions were executed.")
        ]
    }
]

############################################################### Lateral Movement (TA0008) ############################################################################################

lateral_movement_techniques = [
    {
        "name": "Remote Services",
        "id": "T1021",
        "sub": [
            ("Remote Desktop Protocol (RDP)", "T1021.001",
             "Security logs indicate successful RDP login from a non-jump host outside of business hours."),
            ("SMB/Windows Admin Shares", "T1021.002",
             "Suspicious copy of tools like PsExec to ADMIN$ share from a peer system."),
            ("Secure Shell (SSH)", "T1021.004",
             "SSH access established from a previously unused IP to a production server."),
            ("VNC", "T1021.005",
             "VNC session initiated to a workstation, bypassing typical remote access policies.")
        ]
    },
    {
        "name": "Pass the Hash",
        "id": "T1550.002",
        "sub": [
            ("Pass the Hash", "T1550.002",
             "Windows event logs show NTLM authentication using a known hash without password entry.")
        ]
    },
    {
        "name": "Pass the Ticket",
        "id": "T1550.003",
        "sub": [
            ("Pass the Ticket", "T1550.003",
             "Kerberos tickets reused across multiple systems from the same attacker-controlled host.")
        ]
    },
    {
        "name": "Remote Services: Windows Remote Management",
        "id": "T1021.006",
        "sub": [
            ("Windows Remote Management (WinRM)", "T1021.006",
             "WinRM used to execute remote PowerShell commands on multiple endpoints.")
        ]
    },
    {
        "name": "Exploitation of Remote Services",
        "id": "T1210",
        "sub": [
            ("Exploitation of Remote Services", "T1210",
             "Exploit attempt detected against RDP service with known vulnerability CVE-2019-0708.")
        ]
    },
    {
        "name": "Internal Spearphishing",
        "id": "T1534",
        "sub": [
            ("Internal Spearphishing", "T1534",
             "Email sent from compromised user account containing malicious document to internal staff.")
        ]
    },
    {
        "name": "Replication Through Removable Media",
        "id": "T1091",
        "sub": [
            ("Replication Through Removable Media", "T1091",
             "Malware copied to USB drive that was later inserted into another secure segment system.")
        ]
    },
    {
        "name": "Use Alternate Authentication Material",
        "id": "T1550",
        "sub": [
            ("Web Session Cookie", "T1550.004",
             "Browser session cookie stolen and reused to access internal dashboard without password."),
            ("Application Access Token", "T1550.001",
             "OAuth token extracted and replayed to impersonate a cloud app user."),
        ]
    }
]

############################################################# Collection (TA0009) ###################################################################################################

collection_techniques = [
    {
        "name": "Data from Local System",
        "id": "T1005",
        "sub": [
            ("Data from Local System", "T1005",
             "Script executed to recursively search user directories for documents, spreadsheets, and key files.")
        ]
    },
    {
        "name": "Automated Collection",
        "id": "T1119",
        "sub": [
            ("Automated Collection", "T1119",
             "Tool configured to automatically harvest files with sensitive extensions (.docx, .xlsx) every 6 hours.")
        ]
    },
    {
        "name": "Clipboard Data",
        "id": "T1115",
        "sub": [
            ("Clipboard Data", "T1115",
             "Malware scraped clipboard contents at regular intervals, capturing copied passwords.")
        ]
    },
    {
        "name": "Input Capture",
        "id": "T1056",
        "sub": [
            ("Keylogging", "T1056.001",
             "Keylogger installed silently capturing user keystrokes during login and sensitive sessions."),
            ("GUI Input Capture", "T1056.002",
             "Screenshots captured of GUI elements during remote desktop sessions."),
        ]
    },
    {
        "name": "Screen Capture",
        "id": "T1113",
        "sub": [
            ("Screen Capture", "T1113",
             "Malware took periodic screenshots and stored them in a hidden folder for later upload.")
        ]
    },
    {
        "name": "Audio Capture",
        "id": "T1123",
        "sub": [
            ("Audio Capture", "T1123",
             "Microphone was activated and audio recordings saved without user interaction.")
        ]
    },
    {
        "name": "Video Capture",
        "id": "T1125",
        "sub": [
            ("Video Capture", "T1125",
             "Webcam video was recorded during active user sessions and saved to encrypted container.")
        ]
    },
    {
        "name": "Data Staged",
        "id": "T1074",
        "sub": [
            ("Local Data Staging", "T1074.001",
             "Files gathered and zipped into a staging directory before exfiltration."),
            ("Remote Data Staging", "T1074.002",
             "Files exfiltrated to a remote staging server prior to external transfer.")
        ]
    },
    {
        "name": "Email Collection",
        "id": "T1114",
        "sub": [
            ("Local Email Collection", "T1114.001",
             "Outlook .ost files were accessed directly to collect emails and attachments."),
            ("Remote Email Collection", "T1114.002",
             "IMAP used to access user's mailbox and download messages from a remote IP."),
        ]
    },
    {
        "name": "Data from Network Shared Drive",
        "id": "T1039",
        "sub": [
            ("Data from Network Shared Drive", "T1039",
             "Mapped drives scanned for business documents; files copied to attacker’s working directory.")
        ]
    }
]

########################################################### Command and Control (TA0011) ############################################################################################

command_and_control_techniques = [
    {
        "name": "Application Layer Protocol",
        "id": "T1071",
        "sub": [
            ("Web Protocols (HTTP/S)", "T1071.001",
             "Outbound HTTPS traffic to a rare domain observed with large encrypted payloads."),
            ("DNS", "T1071.004",
             "DNS requests were used to encode and exfiltrate data from an internal server."),
            ("Email", "T1071.003",
             "Suspicious outbound email from service account containing encoded command data."),
        ]
    },
    {
        "name": "Non-Application Layer Protocol",
        "id": "T1095",
        "sub": [
            ("Non-Application Layer Protocol", "T1095",
             "Custom malware used raw TCP sockets to connect to external IPs on non-standard ports.")
        ]
    },
    {
        "name": "Ingress Tool Transfer",
        "id": "T1105",
        "sub": [
            ("Ingress Tool Transfer", "T1105",
             "New executable downloaded via PowerShell from an IP not seen before in logs.")
        ]
    },
    {
        "name": "Remote Access Software",
        "id": "T1219",
        "sub": [
            ("Remote Access Software", "T1219",
             "Unauthorized instance of AnyDesk installed and connected to external control server.")
        ]
    },
    {
        "name": "Proxy",
        "id": "T1090",
        "sub": [
            ("External Proxy", "T1090.002",
             "C2 traffic observed routed through public proxy services such as Tor."),
            ("Internal Proxy", "T1090.001",
             "Internal compromised host acting as relay node for C2 traffic."),
        ]
    },
    {
        "name": "Multilayer Encryption",
        "id": "T1079",
        "sub": [
            ("Multilayer Encryption", "T1079",
             "Traffic double-encrypted using TLS and additional obfuscation layers before leaving the network.")
        ]
    },
    {
        "name": "Standard Cryptographic Protocol",
        "id": "T1032",
        "sub": [
            ("Standard Cryptographic Protocol", "T1032",
             "Encrypted C2 traffic mimicked legitimate TLS communications to evade detection.")
        ]
    },
    {
        "name": "Fallback Channels",
        "id": "T1008",
        "sub": [
            ("Fallback Channels", "T1008",
             "When primary C2 was blocked, malware switched to an alternate port and protocol to maintain access.")
        ]
    },
    {
        "name": "Domain Fronting",
        "id": "T1172",
        "sub": [
            ("Domain Fronting", "T1172",
             "TLS SNI showed a common CDN while traffic was actually routed to a malicious backend.")
        ]
    },
    {
        "name": "Uncommonly Used Port",
        "id": "T1065",
        "sub": [
            ("Uncommonly Used Port", "T1065",
             "C2 server used TCP port 4433, not normally used in the environment.")
        ]
    },
    {
        "name": "Web Service",
        "id": "T1102",
        "sub": [
            ("Bidirectional Communication", "T1102.002",
             "C2 traffic used Dropbox API to send and receive encrypted instructions."),
            ("Dead Drop Resolver", "T1102.001",
             "HTTP GET requests used to receive commands from attacker-controlled Pastebin.")
        ]
    }
]

############################################################# Exfiltration (TA0010)##################################################################################################

exfiltration_techniques = [
    {
        "name": "Exfiltration Over Web Service",
        "id": "T1567",
        "sub": [
            ("Exfiltration to Cloud Storage", "T1567.002",
             "Files uploaded from infected host to attacker-controlled Dropbox account via API."),
            ("Exfiltration Over Web Service", "T1567.001",
             "Large encoded payloads sent via HTTP POST to external domain mimicking GitHub."),
        ]
    },
    {
        "name": "Exfiltration Over Alternative Protocol",
        "id": "T1048",
        "sub": [
            ("Exfiltration Over Unencrypted/Obfuscated Non-C2 Protocol", "T1048.003",
             "Unusual outbound FTP traffic from a workstation to an external IP."),
            ("Exfiltration Over Symmetric Encrypted Non-C2 Protocol", "T1048.002",
             "Outbound SFTP transfers from internal dev server to unknown IP not whitelisted."),
        ]
    },
    {
        "name": "Scheduled Transfer",
        "id": "T1029",
        "sub": [
            ("Scheduled Transfer", "T1029",
             "Exfiltration task set to run every 6 hours via scheduled PowerShell job.")
        ]
    },
    {
        "name": "Data Encrypted for Impact",
        "id": "T1486",
        "sub": [
            ("Data Encrypted for Impact", "T1486",
             "Files were encrypted with unknown tool before being sent out of the network.")
        ]
    },
    {
        "name": "Data Compressed",
        "id": "T1560",
        "sub": [
            ("Data Compressed", "T1560",
             "Sensitive documents zipped with password protection before exfiltration.")
        ]
    },
    {
        "name": "Data Staged",
        "id": "T1074",
        "sub": [
            ("Local Data Staging", "T1074.001",
             "Data collected and stored in %AppData% before being compressed for exfiltration."),
            ("Remote Data Staging", "T1074.002",
             "Intermediate server used inside the environment to gather and forward exfiltrated data.")
        ]
    },
    {
        "name": "Exfiltration Over Command and Control Channel",
        "id": "T1041",
        "sub": [
            ("Exfiltration Over C2 Channel", "T1041",
             "Small chunks of base64-encoded data sent over existing HTTP C2 connection.")
        ]
    },
    {
        "name": "Transfer Data to Cloud Account",
        "id": "T1537",
        "sub": [
            ("Transfer Data to Cloud Account", "T1537",
             "AWS CLI used to sync local files to attacker-controlled S3 bucket.")
        ]
    },
    {
        "name": "Exfiltration Over Physical Medium",
        "id": "T1052",
        "sub": [
            ("Exfiltration Over Removable Media", "T1052.001",
             "USB drive connected to secure workstation; file access spike detected before disconnection.")
        ]
    }
]

############################################################### impact(TA0040) ######################################################################################################

impact_techniques = [
    {
        "name": "Data Destruction",
        "id": "T1485",
        "sub": [
            ("Data Destruction", "T1485",
             "Critical data directories were overwritten using disk wiping utilities, making recovery impossible.")
        ]
    },
    {
        "name": "Data Encrypted for Impact",
        "id": "T1486",
        "sub": [
            ("Data Encrypted for Impact", "T1486",
             "Hundreds of files were encrypted using AES-256 with a ransom note placed in each folder.")
        ]
    },
    {
        "name": "Defacement",
        "id": "T1491",
        "sub": [
            ("Internal Defacement", "T1491.001",
             "Intranet homepage replaced with a political message after web server compromise."),
            ("External Defacement", "T1491.002",
             "Corporate website homepage altered to display adversary's logo and messaging.")
        ]
    },
    {
        "name": "Disk Wipe",
        "id": "T1561",
        "sub": [
            ("Disk Content Wipe", "T1561.001",
             "A custom wiper tool was executed, erasing all partitions on infected systems."),
            ("Disk Structure Wipe", "T1561.002",
             "Boot sector and partition tables were overwritten, rendering devices unbootable.")
        ]
    },
    {
        "name": "Endpoint Denial of Service",
        "id": "T1499",
        "sub": [
            ("OS Exhaustion Flood", "T1499.001",
             "Thousands of processes were spawned on the endpoint, exhausting CPU and memory resources."),
            ("Service Exhaustion Flood", "T1499.002",
             "Adversary created thousands of HTTP requests per second to crash a targeted local service."),
        ]
    },
    {
        "name": "Network Denial of Service",
        "id": "T1498",
        "sub": [
            ("Direct Network Flood", "T1498.001",
             "Unusual spike in inbound SYN packets overwhelmed the perimeter firewall."),
            ("Reflection Amplification", "T1498.002",
             "Attackers abused NTP services to amplify traffic in a DDoS campaign."),
        ]
    },
    {
        "name": "Resource Hijacking",
        "id": "T1496",
        "sub": [
            ("Resource Hijacking", "T1496",
             "Compromised servers used to mine Monero, causing sustained CPU saturation.")
        ]
    },
    {
        "name": "Service Stop",
        "id": "T1489",
        "sub": [
            ("Service Stop", "T1489",
             "Windows Defender and EDR processes were forcibly terminated via administrative PowerShell.")
        ]
    },
    {
        "name": "System Shutdown/Reboot",
        "id": "T1529",
        "sub": [
            ("System Shutdown/Reboot", "T1529",
             "Critical systems were rebooted remotely during business hours, causing service disruptions.")
        ]
    },
    {
        "name": "Inhibit System Recovery",
        "id": "T1490",
        "sub": [
            ("Inhibit System Recovery", "T1490",
             "Shadow copies, backups, and recovery partitions were deleted prior to ransomware deployment.")
        ]
    }
]


######################################################################################################################################
######################################### defining functions #########################################################################
## rather than breaking the each into a single function that pull the classification information I decided to uee a function for each
## this can be further modulized by defining a function for use in each function since they do the same thing. I just didnt want to
## compplicate the code too much
######################################################################################################################################

def get_random_recon():
    tech = random.choice(recon_techniques)
    sub = random.choice(tech["sub"])
    return {
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

############################################ resource development ####################################################################

def get_random_resource_dev():
    tech = random.choice(resource_dev_techniques)
    sub = random.choice(tech["sub"])
    return {
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

########################################### Initial Access ###########################################################################

# Function to return a random Initial Access sub-technique and scenario
def get_random_initial_access():
    tech = random.choice(initial_access_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Initial Access",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }



######################################### execution ##################################################################################

def get_random_execution():
    tech = random.choice(execution_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Execution",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

######################################## persistence ################################################################################

def get_random_persistence():
    tech = random.choice(persistence_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Persistence",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

####################################### privilege escalation ########################################################################

def get_random_privilege_escalation():
    tech = random.choice(privilege_escalation_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Privilege Escalation",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

###################################### Defense Evasion #############################################################################

def get_random_defense_evasion():
    tech = random.choice(defense_evasion_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Defense Evasion",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

##################################### Credential Access ############################################################################

def get_random_credential_access():
    tech = random.choice(credential_access_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Credential Access",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

################################### Discovery ######################################################################################

def get_random_discovery():
    tech = random.choice(discovery_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Discovery",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

################ Lateral Movement ##################################################################################################

def get_random_lateral_movement():
    tech = random.choice(lateral_movement_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Lateral Movement",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

################################################################### collection ###################################################

def get_random_collection():
    tech = random.choice(collection_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Collection",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }


####################################################################### Command and Control ######################################

def get_random_command_and_control():
    tech = random.choice(command_and_control_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Command and Control",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

####################################################################### exfiltration ###############################################

def get_random_exfiltration():
    tech = random.choice(exfiltration_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Exfiltration",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }

####################################################################### Impact #####################################################


def get_random_impact():
    tech = random.choice(impact_techniques)
    sub = random.choice(tech["sub"])
    return {
        "tactic": "Impact",
        "technique": tech["name"],
        "tech_id": tech["id"],
        "sub_technique": sub[0],
        "sub_id": sub[1],
        "observable": sub[2]
    }


###########################################
#### attack simuulator setup functions ####
###########################################

def print_scenario(name, data):
    print(f"\n=== {name} Scenario ===")
    print(f"Technique: {data['technique']} ({data['tech_id']})")
    print(f"Sub-technique: {data['sub_technique']} ({data['sub_id']})")
    print(f"Tabletop Observable: {data['observable']}")

# key/value pairs for usse in the gui
tactic_functions = {
    "Reconnaissance": get_random_recon,
    "Resource Development": get_random_resource_dev,
    "Initial Access": get_random_initial_access,
    "Execution": get_random_execution,
    "Persistence": get_random_persistence,
    "Privilege Escalation": get_random_privilege_escalation,
    "Defense Evasion": get_random_defense_evasion,
    "Credential Access": get_random_credential_access,
    "Discovery": get_random_discovery,
    "Lateral Movement": get_random_lateral_movement,
    "Collection": get_random_collection,
    "Command and Control": get_random_command_and_control,
    "Exfiltration": get_random_exfiltration,
    "Impact": get_random_impact
   
}

#############################################################################################################################
#################################### Main Function DEFS #####################################################################
#############################################################################################################################


def format_scenario(name, data):
    return (
        f"=== {name} Scenario ===\n"
        f"Technique: {data['technique']} ({data['tech_id']})\n"
        f"Sub-technique: {data['sub_technique']} ({data['sub_id']})\n"
        f"Tabletop Observable: {data['observable']}\n\n"
    )

### set up the gui using a class. and define internal functions related to the gui
class MitreAttackSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MITRE ATT&CK Tabletop Simulator Author: Kenneth Ray")
        self.geometry("700x600")

        ttk.Label(self, text="Select MITRE ATT&CK tactics to simulate:", font=("Arial", 14)).pack(pady=10)

        self.tactic_vars = {}
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=5, fill="x")

        for tactic in tactic_functions.keys():
            var = tk.BooleanVar()
            ttk.Checkbutton(frame, text=tactic, variable=var).pack(anchor='w')
            self.tactic_vars[tactic] = var

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Select All", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate Scenario", command=self.generate_scenarios).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="View Tactic Descriptions", command=self.show_tactic_descriptions).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save to File", command=self.save_to_file).pack(side="left", padx=5)



        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=25, font=("Courier", 10))
        self.output.pack(padx=10, pady=10, fill="both", expand=True)

    def select_all(self):
        for var in self.tactic_vars.values():
            var.set(True)

    def clear_all(self):
        for var in self.tactic_vars.values():
            var.set(False)

    def generate_scenarios(self):
        selected = [t for t, var in self.tactic_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("No selection", "Please select at least one tactic.")
            return
        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, "=== MITRE ATT&CK Tabletop Simulator Scenarios ===\n\n")
        for tactic in selected:
            func = tactic_functions[tactic]
            data = func()
            self.output.insert(tk.END, format_scenario(tactic, data))
    
    def show_tactic_descriptions(self):
        desc_window = tk.Toplevel(self)
        desc_window.title("MITRE ATT&CK Tactic Descriptions")
        desc_window.geometry("650x600")

        desc_text = scrolledtext.ScrolledText(desc_window, wrap=tk.WORD, font=("Arial", 10))
        desc_text.pack(padx=10, pady=10, fill="both", expand=True)

    # Dictionary of tactic descriptions
        descriptions = {
            "Reconnaissance": "🔍 The adversary gathers information about the target environment prior to exploitation.\nExamples: Scanning websites, WHOIS lookups, collecting emails.\n",
            "Resource Development": "🛠 The attacker sets up infrastructure, tools, or accounts used later in the attack.\nExamples: Creating domains/accounts, acquiring malware.\n",
            "Initial Access": "🚪 The attacker gains initial entry into the environment.\nExamples: Phishing, exploiting public-facing apps.\n",
            "Execution": "▶️ Malicious code is executed on a system.\nExamples: PowerShell, command-line, malicious files.\n",
            "Persistence": "🔒 Maintain access across reboots or credential changes.\nExamples: New accounts, scheduled tasks, startup scripts.\n",
            "Privilege Escalation": "🔼 Gain higher-level permissions.\nExamples: UAC bypass, exploits, credential manipulation.\n",
            "Defense Evasion": "🛡 Evade detection and security controls.\nExamples: Obfuscation, disable logging, uninstall AV.\n",
            "Credential Access": "🔑 Steal account credentials.\nExamples: Keylogging, hash dumping, brute force.\n",
            "Discovery": "🧭 Explore internal network and gather information.\nExamples: System scanning, user account enumeration.\n",
            "Lateral Movement": "🔁 Move from one system to another.\nExamples: RDP, pass-the-hash, exploiting remote services.\n",
            "Collection": "📦 Gather sensitive data from systems, typically for exfiltration or manipulation.\nExamples: Screenshots, file collection, keylogging.\n",
            "Command and Control (C2)": "🛰 Communicate with compromised systems.\nExamples: HTTP/DNS C2, remote shell, custom protocols.\n",
            "Exfiltration": "📤 Move data out of the environment.\nExamples: Uploading data via C2, compression + encryption.\n",
            "Impact": "💥 Impacts of the attacker to disrupt, manipulate, or destroy data and systems.\nExamples: Ransomware, data wipe, service defacement.\n",
            }

        for tactic, desc in descriptions.items():
            desc_text.insert(tk.END, f"=== {tactic} ===\n{desc}\n")
    def save_to_file(self):
        content = self.output.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Empty Output", "There is no scenario to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Scenario As..."
            )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Scenario saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")


## run the application


if __name__ == "__main__":
    app = MitreAttackSimulatorApp()
    app.mainloop()


