#vm2
#we add indentation in the txt file for readability
import os,subprocess,tkinter,openpyxl as opx
log_file=open(r"log_file.txt",'w')
files=os.walk(r'C:\Airtel_Report_Generation\Reports')
folders_to_visit={'STD':['Mobile External MAPA','AB External MAPA','BASL Homes','TS CFU (India) MAPA','TOTAL ANG','ANG + TNG','MS+4G (Srilanka) MAPA','Others-Common Cost Allocation','Own Retail MAPA','Others MAPA Excl CO','TNL ANG MAPA','TNL Office MAPA','Treasury Division','Others MAPA Incl Co','TNL CFU MAPA','TS-Common Cost Allocation MAPA','BAIN Consol','Bharti Airtel ex TowerCo Incl CO','Corporate Office MAPA','Infratel Consol','Other Holdings','Bharti Airtel InclTowerCo','Bharti Airtel ex TowerCo & CO','ALU P&L','India SA','Wynk MAPA','Oneweb India Communications Private Limited','TNL Homes MAPA','Airtel Payments Bank Ltd','One Airtel MAPA','MO-Common Cost Allocation','AB-Common Cost Allocation(800)'],\
                      'AB India Voice':['AB India Voice (Andhra Pradesh) MAPA','AB India Voice (Assam) MAPA','AB India Voice (Bihar) MAPA','AB India Voice (Chennai) MAPA','AB India Voice (Delhi) MAPA','AB India Voice (Elims - India) MAPA','AB India Voice (Gujarat) MAPA','AB India Voice (Haryana) MAPA','AB India Voice (Hexacom) MAPA','AB India Voice (Himachal Pradesh) MAPA','AB India Voice (J&K) MAPA','AB India Voice (JPO) MAPA','AB India Voice (Karnataka) MAPA','AB India Voice (Kerala) MAPA','AB India Voice (Kolkata) MAPA','AB India Voice (Maharashtra) MAPA','AB India Voice (MPCG) MAPA','AB India Voice (Mumbai) MAPA','AB India Voice (North East) MAPA','AB India Voice (Orissa) MAPA','AB India Voice (Punjab) MAPA','AB India Voice (Rajasthan) MAPA','AB India Voice (ROTN) MAPA','AB India Voice (Tamilnadu) MAPA','AB India Voice (UP (East)) MAPA','AB India Voice (UP (West)) MAPA','AB India Voice (West Bengal) MAPA'],
                      'MS CFU':['MS+4G (Andhra Pradesh) MAPA','MS+4G (Assam) MAPA','MS+4G (Bihar) MAPA','MS+4G (Chennai) MAPA','MS+4G (Delhi) MAPA','MS+4G (Elims - India) MAPA','MS+4G (Gujarat) MAPA','MS+4G (Haryana) MAPA','MS+4G (Hexacom) MAPA','MS+4G (Himachal Pradesh) MAPA','MS+4G (J&K) MAPA','MS+4G (JPO) MAPA','MS+4G (Karnataka) MAPA','MS+4G (Kerala) MAPA','MS+4G (Kolkata) MAPA','MS+4G (Maharashtra) MAPA','MS+4G (MPCG) MAPA','MS+4G (Mumbai) MAPA','MS+4G (North East) MAPA','MS+4G (Orissa) MAPA','MS+4G (Punjab) MAPA','MS+4G (Rajasthan) MAPA','MS+4G (ROTN) MAPA','MS+4G (Tamilnadu) MAPA','MS+4G (UP (East)) MAPA','MS+4G (UP (West)) MAPA','MS+4G (West Bengal) MAPA'],\
                      'Homes CFU':['Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA''Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA','Homes CFU (Andhra Pradesh) MAPA''Homes CFU (Andhra Pradesh) MAPA'],\
                    }
for i in files:
    folder=i[0].split("\\")[-1]#to get current folder name from path
    if folder not in folders_to_visit:
        continue
    log_file.write('In folder:'+folder+'\n')
    error_files_list=[]#saving the names of error files for all folders to call them later.
    error_file_name=folder+'_error_data.txt'#because the error files (.txt) are folder wise.
    error_files_list.append(error_file_name)
    file=open(error_file_name,'w')#file to display the errors present in the MAPA files from the given folder
    for j in i[-1]:#iterate through each file in the chosen folder
        if j[:j.index('.')] not in folders_to_visit[folder]:#check if the file is in the list of files to be visited/checked
            continue
        log_file.write('processing workbook:'+j+'\n')#processing workbook/MAPA
        workbook1=opx.load_workbook(str(i[0])+"\\"+str(j),data_only=True)
        data='workbook:'+j+'\n'
        error_in_file=0#flag to keep track of whether any errors have been foud in the file or not
        for sheet in workbook1:#iterate through all the sheets of the MAPA
            errors={}
            Sheet=str(sheet)#worksheet object to sheet
            start=Sheet.index('"')+1
            space=1#indentation for txt file
            sheet_name="worksheet:"+Sheet[start:-2]#getting the worksheet name
            data+=space*"   "+sheet_name+'\n'
            space+=1
            for row in sheet:
                for cell in row:
                    cell_value=str(cell.value)
                    if cell_value.startswith('#'):
                        error_in_file=1#error found in the file
                        if cell_value not in errors:
                            errors[cell_value]=[]
                        errors[cell_value].append(cell.coordinate)
            if errors:
                for k in errors:
                    data+=space*"   "+k+':'+str(errors[k])+'\n'
            else:
                data+=space*"   "+'no error found.\n'
        if error_in_file:
            log_file.write("error found in file :(\n")
        else:
            log_file.write("no errors found in file!\n")    
        file.write(data)
        log_file.write('processing done.\n')
    file.close()
    log_file.write("out of folder:"+folder+'\n')
    subprocess.Popen(['notepad.exe']+error_files_list)
log_file.write('done processing through all folders.\n')
log_file.close()
subprocess.Popen(['notepad.exe']+['log_file.txt'])

