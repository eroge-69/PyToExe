import tableauserverclient as TSC
import pandas as pd
import subprocess

def run(cmd):
    subprocess.run(["powershell", "-Command", cmd], capture_output=True)

runPSCommand = 'C:/Scripts/AD_Update_TAB_Creator/ManageTableauGroups.ps1'

tableau_auth = TSC.TableauAuth('tabusr1', 'Prowess=Distant=Spud=Overgrown=Unspoiled3')
server = TSC.Server('https://tableau.microchip.com')
server.version = '3.5'

count=0
name = []
friendlyName = []
adGroup = []
adGroupStr = 'TAB-Creators'

with server.auth.sign_in(tableau_auth):
	for serverUsers in TSC.Pager(server.users):
		if(serverUsers.site_role=='Creator' or serverUsers.site_role=='ServerAdministrator' or serverUsers.site_role=='SiteAdministratorCreator'):
			print(serverUsers.name,serverUsers.fullname,serverUsers.site_role)
			name.append(serverUsers.name)
			friendlyName.append(serverUsers.fullname)
			adGroup.append(adGroupStr)
			count=count+1
			print(count)

csvResult = pd.DataFrame(
    {'Name': name,
     'Friendly Name': friendlyName,
     'AD Group': adGroup
    })

csvResult.to_csv('//overseer/Public/Dataservices/Tableau/AD_Script/Users and Site Roles.csv',index=False)

run(runPSCommand)

server.auth.sign_out()