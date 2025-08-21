import pandas as pd
import numpy as np
import csv
import re
import io

cols_TAB = ['ID_WMO', 'YEAR', 'COMPLETEYEAR', 'MONTH', 'DATE','HR', 'CARD', 'HEIGHTONE','PRESSONE','DRYBULBONE','DEWPOINTONE','HEIGHTTWO','PRESSTWO','DRYBULBTWO','DEWPOINTTWO','HEIGHTTHREE','PRESSTHREE','DRYBULBTHREE','DEWPOINTTHREE','HEIGHTFOUR','PRESSFOUR', 
'DRYBULBFOUR','DEWPOINTFOUR','HEIGHTFIVE','PRESSFIVE','DRYBULBFIVE','DEWPOINTFIVE', 'CARDIND']

#to create dataframe(creating distinct columnar data) of selected file 

def file_read(file):
    try:
        rs_df = pd.DataFrame()
       
        rows = []
        rs_data_array = []
        with open (file, "r") as testfile:
            for row in testfile:
                stn = str(row[0:5])
                year = row[5:7]
                completeyear = row[80:82] + row[5:7]
                current_year = completeyear
                month = str(row[7:9]).zfill(2)
                date = row[9:11]
                hr = row[11:13]
                card = row[13:14]
                heightone = row[14:18]
                pressone = row[18:21]
                drybulbone = row[21:24]
                dewpointone = row[24:27]
    
                heighttwo = row[27:31]
                presstwo = row[31:34]
                drybulbtwo = row[34:37]
                dewpointtwo = row[37:40]
    
                heightthree = row[40:44]
                pressthree = row[44:47]
                drybulbthree = row[47:50]
                dewpointthree= row[50:53]
    
                heightfour = row[53:57]
                pressfour = row[57:60]
                drybulbfour = row[60:63]
                dewpointfour = row[63:66]
    
                heightfive = row[66:70]
                pressfive = row[70:73]
                drybulbfive = row[73:76]
                dewpointfive = row[76:79]
    
                cardind = row[79:80]
                
                
                rs_rowdata = stn, year, completeyear, month, date,hr, card, heightone,pressone,drybulbone,dewpointone,heighttwo,presstwo,drybulbtwo,dewpointtwo,heightthree,pressthree,drybulbthree,dewpointthree,heightfour,pressfour, drybulbfour,dewpointfour,heightfive,pressfive,drybulbfive,dewpointfive,cardind
                rs_data_array.append(rs_rowdata)
            
        testfile.close()
        rs_df = pd.DataFrame(rs_data_array, columns = cols_TAB)
    
        rs_df = (rs_df.replace(r'^\s*$', np.nan, regex=True)).replace({None: np.nan})
        cols_calcTAB = ['DRYBULBONE','DEWPOINTONE','HEIGHTONE','PRESSONE','HEIGHTTWO','DRYBULBTWO','DEWPOINTTWO','PRESSTWO','HEIGHTTHREE','PRESSTHREE','DRYBULBTHREE','DEWPOINTTHREE','HEIGHTFOUR','PRESSFOUR','DRYBULBFOUR','DEWPOINTFOUR','HEIGHTFIVE','PRESSFIVE','DRYBULBFIVE','DEWPOINTFIVE']

        for i in cols_calcTAB:
            col = i + '_CALC'
            rs_df[col] = rs_df[i].apply(lambda x: float(x))

        print('len rs_df', len(rs_df))
        return convert_temp(rs_df, file)

    
    except Exception as e:
        exception = 'Error reading file: '+ str(e)
        print('Error reading file: '+ str(e))
        return  exception

   
# to convert to tempearture, dewpoint to negative values whereevr required(odd values are converted to negative values)
	
def convert_temp(rs_df, file):
    
    rs_df['DRYBULBONE_CALC'] = rs_df['DRYBULBONE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DEWPOINTONE_CALC'] = rs_df['DEWPOINTONE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DRYBULBTWO_CALC'] = rs_df['DRYBULBTWO_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DEWPOINTTWO_CALC'] = rs_df['DEWPOINTTWO_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DRYBULBTHREE_CALC'] = rs_df['DRYBULBTHREE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DEWPOINTTHREE_CALC'] = rs_df['DEWPOINTTHREE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DRYBULBFOUR_CALC'] = rs_df['DRYBULBFOUR_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DEWPOINTFOUR_CALC'] = rs_df['DEWPOINTFOUR_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DRYBULBFIVE_CALC'] = rs_df['DRYBULBFIVE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)
    
    rs_df['DEWPOINTFIVE_CALC'] = rs_df['DEWPOINTFIVE_CALC'].apply(lambda x: (-1 * x) if(x % 2 == 1) else x)

    print('after temp adjust')

    return height_correction(rs_df, file)
    
#adjust height based on pressure levels

def height_correction(rs_df, file):
    rows_value = []
    newrs_df = pd.DataFrame()
    for index, row in rs_df.iterrows():
        press_one = rs_df.loc[index]["PRESSONE_CALC"]
        height_one = rs_df.loc[index]["HEIGHTONE_CALC"]
        press_two = rs_df.loc[index]["PRESSTWO_CALC"]
        height_two = rs_df.loc[index]["HEIGHTTWO_CALC"]
        press_three = rs_df.loc[index]["PRESSTHREE_CALC"]
        height_three =rs_df.loc[index]["HEIGHTTHREE_CALC"]
        press_four = rs_df.loc[index]["PRESSFOUR_CALC"]
        height_four =rs_df.loc[index]["HEIGHTFOUR_CALC"]
        press_five = rs_df.loc[index]["PRESSFIVE_CALC"]
        height_five =rs_df.loc[index]["HEIGHTFIVE_CALC"]
        
        
        #first
        if((200 <= press_one <= 300) & (height_one <= 4000)):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 10000
            rows_value.append(index)
            
        elif((50 <= press_one <= 80) & (height_one <= 4000)):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one  + 20000
            rows_value.append(index)
    
    
        elif(50 <= press_one <= 80):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one  + 10000
            rows_value.append(index)
    
        elif((15 <= press_one <= 25) & (height_one <= 4000)):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 30000
            rows_value.append(index)
    
    
        elif(15 <= press_one <= 25):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 20000
            rows_value.append(index)
          
    
        elif(80 <= press_one <= 200):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 10000
            rows_value.append(index)
          
    
        elif(25 <= press_one <= 50):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 20000
            rows_value.append(index)
           
    
        elif(press_one <= 15):
            rs_df.at[index, 'HEIGHTONE_CALC'] = height_one + 30000
            rows_value.append(index)
            
    
        #second
        if((200 <= press_two <= 300) & (height_two <= 4000)):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two + 10000
            rows_value.append(index)
            
        elif((50 <= press_two <= 80) & (height_two <= 4000)):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two  + 20000
            rows_value.append(index)
    
        elif(50 <= press_two <= 80):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two  + 10000
            rows_value.append(index)
    
        elif((15 <= press_two <= 25) & (height_two <= 4000)):
            rs_df.at[index, 'HEIGHTWO_CALC'] = height_two + 30000
            rows_value.append(index)
          
    
        elif(15 <= press_two <= 25):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two + 20000
            rows_value.append(index)
    
        
        elif(80 <= press_two <= 200):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two + 10000
            rows_value.append(index)
          
    
        elif(25 <= press_two <= 50):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two + 20000
            rows_value.append(index)
          
    
        elif(press_two <= 15):
            rs_df.at[index, 'HEIGHTTWO_CALC'] = height_two + 30000
            rows_value.append(index)
    
    
        #third
        if((200 <= press_three <= 300) & (height_three <= 4000)):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 10000
            rows_value.append(index)
            
        elif((50 <= press_three <= 80) & (height_three <= 4000)):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three  + 20000
            rows_value.append(index)
    
        elif(50 <= press_three <= 80):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three  + 10000
            rows_value.append(index)
          
    
        elif((15 <= press_three <= 25) & (height_three <= 4000)):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 30000
            rows_value.append(index)
    
    
        elif(15 <= press_three <= 25):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 20000
            rows_value.append(index)
    
        elif(80 <= press_three <= 200):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 10000
            rows_value.append(index)
          
    
        elif(25 <= press_three <= 50):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 20000
            rows_value.append(index)
            
    
        elif(press_three <= 15):
            rs_df.at[index, 'HEIGHTTHREE_CALC'] = height_three + 30000
            rows_value.append(index)
    
    
        #fourth
        if((200 <= press_four <= 300) & (height_four <= 4000)):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 10000
            rows_value.append(index)
            
        elif((50 <= press_four <= 80) & (height_four <= 4000)):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four  + 20000
            rows_value.append(index)
    
        elif(50 <= press_four <= 80):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four  + 10000
            rows_value.append(index)
          
    
        elif((15 <= press_four <= 25) & (height_four <= 4000)):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 30000
            rows_value.append(index)
    
        elif(15 <= press_four <= 25):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 20000
            rows_value.append(index)
          
    
        elif(80 <= press_four <= 200):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 10000
            rows_value.append(index)
          
    
        elif(25 <= press_four <= 50):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 20000
            rows_value.append(index)
           
    
        elif(press_four <= 15):
            rs_df.at[index, 'HEIGHTFOUR_CALC'] = height_four + 30000
            rows_value.append(index)
    
    
         #fifth   
        if((200 <= press_five <= 300) & (height_five <= 4000)):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 10000
            rows_value.append(index)
            
        elif((50 <= press_five <= 80) & (height_five <= 4000)):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five  + 20000
            rows_value.append(index)
    
        elif(50 <= press_five <= 80):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five  + 10000
            rows_value.append(index)
    
        elif((15 <= press_five <= 25) & (height_five <= 4000)):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 30000
            rows_value.append(index)
    
        elif(15 <= press_five <= 25):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 20000
            rows_value.append(index)
    
        elif(80 <= press_five <= 200):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 10000
            rows_value.append(index)
          
    
        elif(25 <= press_five <= 50):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 20000
            rows_value.append(index)
           
    
        elif(press_five <= 15):
            rs_df.at[index, 'HEIGHTFIVE_CALC'] = height_five + 30000
            rows_value.append(index)

    print('after height adjust')
    return create_correctedfile(rs_df, file)
	

#creating new dataframe for new pressure height adjusted values

def create_correctedfile(rs_df, file):
    count = 0
    newrs_df = pd.DataFrame()
    for index, row in rs_df.iterrows():
        if(pd.notnull(rs_df.at[index, 'PRESSONE_CALC'])):
            new_row = pd.DataFrame({'Station':rs_df.loc[index]["ID_WMO"], 'Date':rs_df.loc[index]["COMPLETEYEAR"] + rs_df.loc[index]['MONTH'] + rs_df.loc[index]['DATE'] +  row['HR'], 'Pres':rs_df.at[index, 'PRESSONE_CALC'], 'Height':rs_df.at[index, 'HEIGHTONE_CALC'], 'DryBulb':rs_df.at[index, 'DRYBULBONE_CALC'], 'WetBulb':rs_df.at[index, 'DEWPOINTONE_CALC']}, index = [0])
            newrs_df = pd.concat([new_row,newrs_df.loc[:]]).reset_index(drop=True)
    
        if(pd.notnull(rs_df.at[index, 'PRESSTWO_CALC'])):
            new_row = pd.DataFrame({'Station':rs_df.loc[index]["ID_WMO"], 'Date':rs_df.loc[index]["COMPLETEYEAR"] + rs_df.loc[index]['MONTH'] + rs_df.loc[index]['DATE'] +  row['HR'], 'Pres':rs_df.at[index, 'PRESSTWO_CALC'], 'Height':rs_df.at[index, 'HEIGHTTWO_CALC'], 'DryBulb':rs_df.at[index, 'DRYBULBTWO_CALC'], 'WetBulb':rs_df.at[index, 'DEWPOINTTWO_CALC']}, index = [0])
            newrs_df = pd.concat([new_row,newrs_df.loc[:]]).reset_index(drop=True) 
    
        if(pd.notnull(rs_df.at[index, 'PRESSTHREE_CALC'])):
            new_row = pd.DataFrame({'Station':rs_df.loc[index]["ID_WMO"], 'Date':rs_df.loc[index]["COMPLETEYEAR"] + rs_df.loc[index]['MONTH'] + rs_df.loc[index]['DATE'] +  row['HR'], 'Pres':rs_df.at[index, 'PRESSTHREE_CALC'], 'Height':rs_df.at[index, 'HEIGHTTHREE_CALC'],'DryBulb':rs_df.at[index, 'DRYBULBTHREE_CALC'], 'WetBulb':rs_df.at[index, 'DEWPOINTTHREE_CALC']}, index = [0])
            newrs_df = pd.concat([new_row,newrs_df.loc[:]]).reset_index(drop=True)
    
        if(pd.notnull(rs_df.at[index, 'PRESSFOUR_CALC'])):
            new_row = pd.DataFrame({'Station':rs_df.loc[index]["ID_WMO"], 'Date':rs_df.loc[index]["COMPLETEYEAR"] + rs_df.loc[index]['MONTH'] + rs_df.loc[index]['DATE'] +  row['HR'], 'Pres':rs_df.at[index, 'PRESSFOUR_CALC'], 'Height':rs_df.at[index, 'HEIGHTFOUR_CALC'], 'DryBulb':rs_df.at[index, 'DRYBULBFOUR_CALC'], 'WetBulb':rs_df.at[index, 'DEWPOINTFOUR_CALC']}, index = [0])
            newrs_df = pd.concat([new_row,newrs_df.loc[:]]).reset_index(drop=True)  
    
    
        if(pd.notnull(rs_df.at[index, 'PRESSFIVE_CALC'])):
            new_row = pd.DataFrame({'Station':rs_df.loc[index]["ID_WMO"], 'Date':rs_df.loc[index]["COMPLETEYEAR"] + rs_df.loc[index]['MONTH'] + rs_df.loc[index]['DATE'] +  row['HR'], 'Pres':rs_df.at[index, 'PRESSFIVE_CALC'], 'Height':rs_df.at[index, 'HEIGHTFIVE_CALC'], 'DryBulb':rs_df.at[index, 'DRYBULBFIVE_CALC'], 'WetBulb':rs_df.at[index, 'DEWPOINTFIVE_CALC']}, index = [0])
            newrs_df = pd.concat([new_row,newrs_df.loc[:]]).reset_index(drop=True)

        count = count + 1
        if(count % 10000 == 0):
            print('record created', count)


    
    cols_newrscal_after = ['DryBulb', 'WetBulb']

    newrs_df = newrs_df.replace(np.nan,'99999', regex=True)
    
    for i in cols_newrscal_after:
     newrs_df[i]  =  newrs_df[i].map(str)

    
    newrs_df['DryBulb'] = newrs_df['DryBulb'].apply(lambda x: str(x).zfill(2) if(len(re.findall(r'\d+', str(x))[0]) == 1) else x )
    newrs_df['WetBulb'] = newrs_df['WetBulb'].apply(lambda x: str(x).zfill(2) if(len(re.findall(r'\d+', str(x))[0]) == 1) else x )

    newrs_df["UDD"] = np.nan
    newrs_df["UFF"] = np.nan
    newrs_df["UFF2"] = np.nan
    newrs_df["UFFM"] = np.nan
    

    
    newrs_df['DryBulb'] = newrs_df['DryBulb'].apply(lambda x: x.zfill(3) if((len(re.findall(r'\d+', x)[0]) == 1) & ('-' in x)) else x)
    newrs_df['WetBulb'] = newrs_df['WetBulb'].apply(lambda x: x.zfill(3) if((len(re.findall(r'\d+', x)[0]) == 1)& ('-' in x)) else x)

    newrs_df = newrs_df.replace('99999','', regex=True)
    
    newrs_df = (newrs_df.sort_values(['Station', 'Date', 'Pres'],ascending=[True, True, False])).reset_index(drop=True)

    
    converted_file = file.rsplit('/', 1)[0] + '//' + 'convertedfile.DAT'
    print('converted_file', converted_file)
    newrs_df.to_csv(converted_file,  sep = ';', index = False, header = False)
    return converted_file
    
    
	
	
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox


start = time.time()

top = Tk()
top.geometry("500x400") 
top.wm_title("RS Card Data correction")

filetype = StringVar()
filetype.set(' ')


def hide_label():
    convert_label.grid_forget()

    
def show_label():
   convert_label.grid(row = 28,column = 0, sticky = "W")

def selectfile():
    end_label.config(text="")
    hide_label()
    filepath = filedialog.askopenfilename(initialdir = "/",title = "Select a File")
    if(len(filepath) > 0):
        filename = (filepath.rsplit('.', 1)[0]).rsplit('/', 1)[-1]
        print("Filename {0},Input {1}".format(filename, filetype.get()))
           
        show_label()
        print('filename', filepath)
        selected_file_label.config(text=f"Selected File Name: {filepath}")
        convert_data = file_read(filepath)
    
        if isinstance(convert_data, str):
            if "Error" in convert_data:
                hide_label()
                messagebox.showerror('Python Error', convert_data)
                end_label.config(text="Execution Ended", fg='#f00', font='TimesNewRoman 10 bold')
                return
            
            else:
                if(len(convert_data)> 0):
                    convert_label.config(text=f"Converted File Name: {convert_data}")
            
    else:
        messagebox.showerror('Python Error', 'File not chosen')
        hide_label()
        end_label.config(text="Execution Ended", fg='#f00', font='TimesNewRoman 10 bold')
        


label = tk.Label(top, text='Select file type :')
label.grid(row = 1,column = 0, sticky = "W")

selected_file_label = tk.Label(top)
selected_file_label.grid(row=24,column=0, sticky="W")

convert_label = tk.Label(top)


selectButton = tk.Button(top, text = "Select file", command = selectfile)
selectButton.grid(row=15,column=0, sticky = "W", pady = 20)


end_label = tk.Label(top)
end_label.grid(row=38,column=0, sticky="W")

top.mainloop()




