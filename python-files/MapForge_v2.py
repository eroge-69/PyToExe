# Data Manipulation & Excel
#import required libraries
import pandas as pd
import os 
import re
import numpy as np
import xlwings as xw 
import json
import itertools
import traceback
import logging
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal

pd.options.mode.chained_assignment = None  # default='warn'
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

# Define Base Directories
os.chdir(os.getcwd())
with open(os.path.join(os.getcwd(),'path.json'), 'r') as path_file:
    path = json.load(path_file)
BaseDir = path['base_directory']


#creating functions to generate mapping file for each domain as required

def generateB1Mapping(Study, BaseDir):
    StudyDir = os.path.join(BaseDir,Study)
    ###### Categorize Files - DTS & TV -----------------------------------------------------------------
    file_list =os.listdir(StudyDir)
    # Only the relevent files - TV & DTS (applicable domains), are neded
    Study_ = []
    Domain_ = []
    Type_ = []
    FileName_ = []
    Ext_ = []
    for file in file_list:
        if '_' in file:
            string = file.split('_')
            ext = file.split('.')
            #Study_.append(string[0])
            #Domain_.append(string[1][0:2])
            if "TV" in file or "tv" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('TV')
                FileName_.append(file)
                Ext_.append(ext[-1])
            elif "DTS" in file or "Data Transfer Specification" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('DTS')
                FileName_.append(file)
                Ext_.append(ext[-1])

    # All the files in the study directory
    fileAll = pd.DataFrame({'Study':Study_,'Domain':Domain_,'Type':Type_,'FileName':FileName_,'Ext':Ext_})
    applicableDomains = ['B1','TV']
    # Files with domain applicable to TVT
    fileApp= fileAll[fileAll['Domain'].isin(applicableDomains)]
    fileApp = fileApp[fileApp['Ext'].isin(['xlsx'])]
    fileApp.reset_index(drop=True, inplace=True)
    
    ###### Reading TV File -----------------------------------------------------------------
    TVdetails = fileApp[fileApp['Domain'].isin(["TV"])]
    TVData = pd.DataFrame()
    TVPath = os.path.join(StudyDir,TVdetails.iloc[0]['FileName'])
    nameTV = pd.ExcelFile(TVPath).sheet_names
    if len(nameTV) > 1:
        tabTV = [i for i in nameTV if i in 'TV'][0]
    else:
        tabTV = nameTV[0]
    TVData = pd.read_excel(TVPath, sheet_name=tabTV, keep_default_na=False)
    TVData.replace('', np.nan, inplace=True)
    TVData = TVData.dropna(thresh=3) # Removing all rows with more than 3 NaN. STUDY, DOMAIN, VISIT ought to be there in TV
    TVData.reset_index(drop=True,inplace=True)
    # Fixing the header for non standard TV files
        # Searching the following list in rows of TV Data & retriving the row number that has a match
    headTV1 = ['DOMAIN','CPEVENT','VISITDY']
    headTV2 = ['StudyIdentifier','VisitName','VisitNumber']

    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]
    headRow = 0
    if any(e in headTV1 for e in TVData.columns):
        TVData = TVData
    elif any(e in headTV2 for e in TVData.columns):
        TVData = TVData
    else:
        for i, row in TVData.iterrows():
            row = [str(x).replace(' ', '') for x in row]
            if any(e in headTV1 for e in list(row)):
                headRow = i
                break
            elif any(e in headTV2 for e in list(row)):
                headRow = i
                break
        TVData = TVData.set_axis(TVData.iloc[0], axis=1).iloc[headRow:]

    # Fixing the content rows for non standard TV files
        # Searching the study ID and TV in rows of TV Data & retriving the row number that has a match
    contentTV = [Study,'TV']
    for i, row in TVData.iterrows():
        if any(e in contentTV for e in list(row)):
            contentRow = i
            break
    TVData = TVData.drop(range(0,contentRow))
    TVData.reset_index(drop=True, inplace=True)
    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]

    if "VisitName" in TVData.columns:
        TVData.rename(columns={'VisitName':'CPEVENT'}, inplace=True)
    if "VISIT" in TVData.columns:
        TVData.rename(columns={'VISIT':'CPEVENT'}, inplace=True)

    TVData = TVData[['CPEVENT']]
    TVData.drop_duplicates(inplace=True)
    TVData.reset_index(drop=True, inplace=True)

    # Remove leading & trailing spaces from CPEVENT
    TVData['CPEVENT'] = TVData['CPEVENT'].str.replace(' ', '').str.upper()
    TVData_Visit = list(TVData['CPEVENT'])

    ###### Reading Data from DTS -----------------------------------------------------------------
    def extractB1data(StudyDir, fileB1):
        # B1details = fileApp[fileApp['Domain'].isin(["B1"])]
        # fileB1 = list(B1details['FileName'])[0]
        B1Path = os.path.join(StudyDir,fileB1)
        nameB1 = pd.ExcelFile(B1Path).sheet_names

        tabCover = [i for i in nameB1 if 'COVER' in i.upper().replace(' ','')][0]
        tabVisit = [i for i in nameB1 if 'VISIT' in i.upper().replace(' ','')][0]
        tabDCF = [i for i in nameB1 if 'DATACOLLECTIONFORMAT' in i.upper().replace(' ','')][0]
        tabDict = [i for i in nameB1 if 'DICTIONARY' in i.upper().replace(' ','')][0]

        # Extracting Vendor Name from Cover tab
        Data_1 = pd.read_excel(B1Path, sheet_name=tabCover, keep_default_na=False)
        Data_1 = Data_1.dropna(thresh=2) # Remove empty rows
        Data_1 = Data_1.dropna(thresh=len(Data_1) - 1, axis=1) # Remove empty columns
        Data_1.reset_index(drop=True, inplace=True)
        Data_1.columns = ['Col1','Col2']
        Vendor = Data_1.loc[Data_1['Col1'].str.contains('Vendor'), 'Col2'].squeeze()
        Vendor = Vendor.upper()

        # Extracting Visit Data
        Data_2 = pd.read_excel(B1Path, sheet_name=tabVisit, usecols='A', keep_default_na=False)
        Data_2 = Data_2.dropna()
        Data_2.reset_index(drop=True, inplace=True)
        headRow = []
        for i, row in Data_2.iterrows():
            if 'FOLDERNAME' in str(row[0]).upper() or 'FOLDER NAME' in str(row[0]).upper():
                headRow.append(i)
        # Sometimes there is a FOLDERNAME element with a big description under it. In such case the 1st headRow must be disregarded.
        if len(headRow) > 1:
            for i in range(headRow[0],headRow[1]):
                if len(Data_2.iloc[headRow[0]+1,0]) > 50:
                    headRow = headRow[1:]
        Data_2_1 = Data_2.drop(range(0,max(headRow)+1)) # Removing all the rows above & including 'FolderName'
        Data_2_1.drop_duplicates()
        Data_2_1.reset_index(drop=True, inplace=True)
        Data_2_1.columns = ['VisitName']
        Data_2_1['VisitName'] = Data_2_1['VisitName'].str.replace(' ', '').str.upper()
        CPEVENT = list(Data_2_1['VisitName']) # CPEVENT later to be merged with rest of DTS data
            #### Multiple Visit Sets - If there are more than 1 headRow 
        ## VisitSets = len(headRow)

        # Extract Data from Data Collection Format
        selectDCF = ["B1NAM","B1AYLNM","B1ALYNM","B1TEST","B1ORRESU","B1METHOD","B1SPEC"]
        Data_3 = pd.read_excel(B1Path, sheet_name=tabDCF, skiprows=list(range(0,5)), usecols = 'A,F,G', keep_default_na=False)
        Data_3.drop_duplicates()
        Data_3.columns = ['Variable','Variable2','Value']
        Data_3 = Data_3[Data_3['Variable'].isin(selectDCF)]
        Data_3['Variable'].replace('B1ALYNM', 'B1AYLNM', inplace=True)
        Data_3['Variable2'].replace('B1ALYNM', 'B1AYLNM', inplace=True)
        Data_3 = Data_3.sort_values(['Variable2'])
        Data_3.reset_index(drop=True, inplace=True)

        # Extracting info from Dictionary(Code-Decode)
        Data_4 = pd.read_excel(B1Path, sheet_name=tabDict, skiprows=list(range(0,5)), usecols = 'A,B', keep_default_na=False)
        Data_4.drop_duplicates()
        Data_4.columns = ['Variable2','Value2']
        Data_4['Variable2'].replace('B1ALYNM', 'B1AYLNM', inplace=True)
        Data_4 = Data_4[Data_4['Variable2'].isin(Data_3['Variable2'])]
        Data_4 = Data_4.sort_values(['Variable2'])
        Data_4.reset_index(drop=True, inplace=True)

        DCD = pd.merge(Data_3, Data_4, how ='left', on ='Variable2')
        DCD['Value2'] = DCD['Value2'].fillna(DCD['Value'])
        DCD.drop(columns=['Variable2','Value'], axis=1, inplace=True)
        DCD.rename(columns={'Value2':'Value'}, inplace=True)
        DCD = DCD.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
        DCD = DCD.transpose()
        DCD.columns = DCD.iloc[0]
        DCD.reset_index(drop=True, inplace=True)
        DCD.drop(0, axis=0, inplace=True)
        DCD.reset_index(drop=True, inplace=True)

        # Check if 'Timepoint' (case-insensitive) occurs in the DTS Tab names
        contains_timepoint = any('timepoint' in i.lower().replace(' ', '') for i in nameB1)
        if contains_timepoint == True:
            tabTPT = [i for i in nameB1 if 'TIMEPOINT' in i.upper().replace(' ','')][0]
            TPT1 = pd.read_excel(B1Path, sheet_name=tabTPT, usecols = 'B')
            TPT1.columns = ['TPTTXT']
            TPDummyList = TPT1['TPTTXT'].dropna().tolist()
            headTPT = []
            for i, row in TPT1.iterrows():
                if 'TPTTXT' in str(row[0]).upper():
                    headTPT.append(i)
            if len(headTPT) > 0:
                TPT1 = TPT1.drop(range(0,max(headTPT)+2))
                TPT1.reset_index(drop=True, inplace=True)
                TPTTXT = TPT1['TPTTXT'].dropna().tolist()
            if len(headTPT) == 0 or 'TPTTXT' not in TPDummyList:
                TPT2 = pd.read_excel(B1Path, sheet_name=tabTPT, usecols = 'C')
                TPT2.columns = ['TPTTXT']
                headTPT = []
                for i, row in TPT2.iterrows():
                    if 'TPTTXT' in str(row[0]).upper():
                        headTPT.append(i)
                TPT2 = TPT2.drop(range(0,max(headTPT)+2))
                TPTTXT = TPT2['TPTTXT'].dropna().tolist()
            DCD['TPTTXT'] = [TPTTXT]

        selectDCF = ["B1NAM","B1AYLNM","B1TEST","B1ORRESU","B1METHOD","B1SPEC"]
        for DCF in selectDCF+['TPTTXT']:
            if DCF not in DCD.columns:
                DCD[DCF] = [np.nan]

        AnalyteList = DCD.iloc[0]['B1AYLNM']
        VisitData = pd.DataFrame()
        if type(AnalyteList) is list:
            VisitData['STUDY_NAME'] = [Study]*len(AnalyteList)
            VisitData['VENDOR_NAME'] = [Vendor]*len(AnalyteList)
            VisitData['B1AYLNM'] = AnalyteList
            VisitData['B1ORRESU(Specified)'] = [pd.NA]*len(AnalyteList)
            VisitData['CPEVENT'] = [CPEVENT]*VisitData.shape[0]
        else:
            if np.isnan(AnalyteList):
                VisitData['STUDY_NAME'] = [Study]
                VisitData['VENDOR_NAME'] = [Vendor]
                VisitData['B1AYLNM'] = AnalyteList
                VisitData['B1ORRESU(Specified)'] = [pd.NA]
                VisitData['CPEVENT'] = [CPEVENT]
        ## Add Trial Visit Data
        # Initialize columns for each trial visit
        for Visit in TVData_Visit:
            VisitData[Visit] = 'No'  # Initialize with 'No'

        # Populate 'Yes' or 'No' based on DTS CPEVENT values
        for index, row in VisitData.iterrows():
            for visit in TVData_Visit:
                if visit in row['CPEVENT']:
                    VisitData.at[index, visit] = 'Yes'
        VisitData.drop(columns=['CPEVENT'], inplace=True)

        # Ensure that all scalar values in a DCD are converted to lists, including handling NaN value
        def ensure_list(value):
            if isinstance(value, float) and pd.isna(value):
                return []
            elif not isinstance(value, list):
                return [value]  # Convert scalar or non-list values to a list
            else:
                return value
        DCD = DCD.applymap(ensure_list)  # Apply the function to each element in the DataFrame

        MetaData = pd.DataFrame()
        # B1NAM	B1AYLNM	B1TEST	B1ORRESU	B1METHOD	B1SPEC	TPTTXT	CPEVENT
        c1 = pd.DataFrame({'B1NAM':[Vendor]})
        c2 = pd.DataFrame({'B1AYLNM':DCD.iloc[0]['B1AYLNM']})
        c3 = pd.DataFrame({'B1TEST':DCD.iloc[0]['B1TEST']})
        c4 = pd.DataFrame({'B1ORRESU':DCD.iloc[0]['B1ORRESU']})
        c5 = pd.DataFrame({'B1METHOD':DCD.iloc[0]['B1METHOD']})
        c6 = pd.DataFrame({'B1SPEC':DCD.iloc[0]['B1SPEC']})
        c7 = pd.DataFrame({'TPTTXT':DCD.iloc[0]['TPTTXT']})
        c8 = pd.DataFrame({'CPEVENT':CPEVENT})
        MetaData = pd.concat([c1,c2,c3,c4,c5,c6,c7,c8], axis=1)

        return [VisitData, MetaData, str(Vendor)]
    
    fileDTS = fileApp[fileApp['Type'].isin(['DTS'])]
    SVData = pd.DataFrame()
    MetaData_Split = []
    MData_Vendor = []

    ### Extract data from multiple B1 DTS
    B1details = fileDTS[fileDTS['Domain'].isin(["B1"])]
    for fileB1 in list(B1details['FileName']):
        d = extractB1data(StudyDir,fileB1)
        SVData = pd.concat([SVData,d[0]], axis=0)
        MetaData_Split.append(d[1])
        MData_Vendor.append('MetaData_'+d[2])
    
    # Function to get the list of indexes for duplicated vendors
    def get_duplicate_indexes(vendor_list):
        seen = {}
        duplicates = {}
        
        for i, vendor in enumerate(vendor_list):
            if vendor in seen:
                if vendor not in duplicates:
                    duplicates[vendor] = [seen[vendor]]  # Add the first occurrence index
                duplicates[vendor].append(i)
            else:
                seen[vendor] = i
        
        return duplicates

    # Get the dictionary of duplicated vendors and their indexes
    duplicate_indexes = get_duplicate_indexes(MData_Vendor)

    # The data with same vendor but from diff DTS needs to be put together as one data
    MetaData_SplitF = []
    MData_Dup = []
    temp_k = []
    temp_v = []
    MData_Sheets = []

    for key, value in duplicate_indexes.items():
        ConcatDF = pd.DataFrame()
        for i in value:
            ConcatDF = pd.concat([ConcatDF, MetaData_Split[i]], ignore_index=True)
        # Step 2 and 3: Remove NaN values and duplicates within each column
        ConcatDF = ConcatDF.apply(lambda col: col.dropna().drop_duplicates().reset_index(drop=True))

        # Ensure DataFrame columns have the same length by filling with NaNs
        max_length = max(ConcatDF.apply(len))
        ConcatDF = ConcatDF.apply(lambda col: col.reindex(range(max_length)))
        MetaData_SplitF.append(ConcatDF)
        temp_v.append(value)
        temp_k.append(key)
    
    MData_DupIndex = [item for sublist in temp_v for item in sublist] # Works only for value
    MetaData_Split2 = [v for i,v in enumerate(MetaData_Split) if i not in MData_DupIndex]
    MData_Vendor2 = [v for i,v in enumerate(MData_Vendor) if i not in MData_DupIndex]
    for df in MetaData_Split2:
        MetaData_SplitF.append(df)
    MData_Sheets = temp_k
    for vendor in MData_Vendor2:
        MData_Sheets.append(vendor)
    
    # Limiting the length of MData Sheet names
    def limit_length(input_list):
        return [item[:30] for item in input_list]

    MData_Sheets = limit_length(MData_Sheets)

    # Path to the template onboarding excel
    TempPath = os.path.join(BaseDir,"Templates","STUDY_B1_Metadata Consistency_Mapping file.xlsx")

    with xw.App(visible=False) as app:
        wb = xw.Book(TempPath)
        inputFile = str(Study)+"_B1_Metadata Consistency_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        wb.save(InputPath)
        wb.close()
    
    with xw.App(visible=False) as app:
        #saving mapping file template instance
        inputFile = str(Study)+"_B1_Metadata Consistency_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        MapFile = xw.Book(InputPath)

        Ins = MapFile.sheets['Instruction']

        ## B1NAM_SV
        Visit = MapFile.sheets['B1NAM_SV']
        Visit["A2"].options(pd.DataFrame, header=1, index=False, expand='table').value = SVData
        Visit.api.Move(None, After=Ins.api)

        ## MetaData_Vendor
        for sheetname, df in zip(MData_Sheets, MetaData_SplitF):
            MapFile.sheets['MetaData'].copy(name=sheetname)
            VenSheet = MapFile.sheets[sheetname]
            VenSheet["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value = df
            VenSheet.api.Move(None, After=Visit.api)

        MapFile.sheets['MetaData'].delete()

        #saving final file with new name
        inputFile1 = str(Study)+"_B1_Metadata Consistency_Mapping file.xlsx"
        InputPath1 = os.path.join(StudyDir, inputFile1)
        MapFile.save(InputPath1)
        MapFile.close()

    return inputFile1

def generateQSMapping(Study, BaseDir):
    StudyDir = os.path.join(BaseDir,Study)
    ###### Categorize Files - DTS & TV -----------------------------------------------------------------
    file_list =os.listdir(StudyDir)
    # Only the relevent files - TV & DTS (applicable domains), are neded
    Study_ = []
    Domain_ = []
    Type_ = []
    FileName_ = []
    Ext_ = []
    for file in file_list:
        if '_' in file:
            string = file.split('_')
            ext = file.split('.')
            #Study_.append(string[0])
            #Domain_.append(string[1][0:2])
            if "TV" in file or "tv" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('TV')
                FileName_.append(file)
                Ext_.append(ext[-1])
            elif "DTS" in file or "Data Transfer Specification" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('DTS')
                FileName_.append(file)
                Ext_.append(ext[-1])

    # All the files in the study directory
    fileAll = pd.DataFrame({'Study':Study_,'Domain':Domain_,'Type':Type_,'FileName':FileName_,'Ext':Ext_})
    applicableDomains = ['QS','TV']
    # Files with domain applicable to TVT
    fileApp= fileAll[fileAll['Domain'].isin(applicableDomains)]
    fileApp = fileApp[fileApp['Ext'].isin(['xlsx'])]
    fileApp.reset_index(drop=True, inplace=True)
    
    ###### Reading TV File -----------------------------------------------------------------
    TVdetails = fileApp[fileApp['Domain'].isin(["TV"])]
    TVData = pd.DataFrame()
    TVPath = os.path.join(StudyDir,TVdetails.iloc[0]['FileName'])
    nameTV = pd.ExcelFile(TVPath).sheet_names
    if len(nameTV) > 1:
        tabTV = [i for i in nameTV if i in 'TV'][0]
    else:
        tabTV = nameTV[0]
    TVData = pd.read_excel(TVPath, sheet_name=tabTV)
    TVData.replace('', np.nan, inplace=True)
    TVData = TVData.dropna(thresh=3) # Removing all rows with more than 3 NaN. STUDY, DOMAIN, VISIT ought to be there in TV
    TVData.reset_index(drop=True,inplace=True)
    # Fixing the header for non standard TV files
        # Searching the following list in rows of TV Data & retriving the row number that has a match
    headTV1 = ['DOMAIN','CPEVENT','VISITDY']
    headTV2 = ['StudyIdentifier','VisitName','VisitNumber']

    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]
    headRow = 0
    if any(e in headTV1 for e in TVData.columns):
        TVData = TVData
    elif any(e in headTV2 for e in TVData.columns):
        TVData = TVData
    else:
        for i, row in TVData.iterrows():
            row = [str(x).replace(' ', '') for x in row]
            if any(e in headTV1 for e in list(row)):
                headRow = i
                break
            elif any(e in headTV2 for e in list(row)):
                headRow = i
                break
        TVData = TVData.set_axis(TVData.iloc[0], axis=1).iloc[headRow:]

    # Fixing the content rows for non standard TV files
        # Searching the study ID and TV in rows of TV Data & retriving the row number that has a match
    contentTV = [Study,'TV']
    for i, row in TVData.iterrows():
        if any(e in contentTV for e in list(row)):
            contentRow = i
            break
    TVData = TVData.drop(range(0,contentRow))
    TVData.reset_index(drop=True, inplace=True)
    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]

    if "VisitName" in TVData.columns:
        TVData.rename(columns={'VisitName':'CPEVENT'}, inplace=True)
    if "VISIT" in TVData.columns:
        TVData.rename(columns={'VISIT':'CPEVENT'}, inplace=True)

    TVData = TVData[['CPEVENT']]
    TVData.drop_duplicates(inplace=True)
    TVData.reset_index(drop=True, inplace=True)

    # Remove leading & trailing spaces from CPEVENT
    TVData['CPEVENT'] = TVData['CPEVENT'].str.replace(' ', '').str.upper()
    TVData_Visit = list(TVData['CPEVENT'])

    ###### Reading Data from DTS -----------------------------------------------------------------
    def extractQSdata(StudyDir, fileQS):
        # QSdetails = fileApp[fileApp['Domain'].isin(["QS"])]
        # fileQS = list(QSdetails['FileName'])[0]
        QSPath = os.path.join(StudyDir,fileQS)
        nameQS = pd.ExcelFile(QSPath).sheet_names

        tabCover = [i for i in nameQS if 'COVER' in i.upper().replace(' ','')][0]
        tabVisit = [i for i in nameQS if 'VISIT' in i.upper().replace(' ','')][0]
        tabDCF = [i for i in nameQS if 'DATACOLLECTIONFORMAT' in i.upper().replace(' ','')][0]
        tabDict = [i for i in nameQS if 'DICTIONARY' in i.upper().replace(' ','')][0]
        tabTPT = [i for i in nameQS if 'TIMEPOINT' in i.upper().replace(' ','')][0]
        tabQS = [i for i in nameQS if 'QUESTION' in i.upper().replace(' ','')][0]

        ### Visit Data
        ## Extracting Domain from Cover tab
        Data_1 = pd.read_excel(QSPath, sheet_name=tabCover)
        Data_1 = Data_1.dropna(thresh=2) # Remove empty rows
        Data_1 = Data_1.dropna(thresh=len(Data_1) - 1, axis=1) # Remove empty columns
        Data_1.reset_index(drop=True, inplace=True)
        Data_1.columns = ['Col1','Col2']
        # Domain = Data_1.loc[Data_1['Col1'].str.contains('Domain'), 'Col2'].squeeze()
        Vendor = Data_1.loc[Data_1['Col1'].str.contains('Vendor'), 'Col2'].squeeze()
        Vendor = Vendor.upper()

        ## Extracting Visit Data from Folder(Visit) tab
        Data_2 = pd.read_excel(QSPath, sheet_name=tabVisit, usecols='A')
        Data_2 = Data_2.dropna()
        Data_2.reset_index(drop=True, inplace=True)
            # Determining the position of header row - FOLDERNAME
        headRow = []
        for i, row in Data_2.iterrows():
            if 'FOLDERNAME' in str(row[0]).upper() or 'FOLDER NAME' in str(row[0]).upper():
                headRow.append(i)
            # Sometimes there is a FOLDERNAME element with a big description under it. In such case the 1st headRow must be disregarded.
        if len(headRow) > 1:
            for i in range(headRow[0],headRow[1]):
                if len(Data_2.iloc[headRow[0]+1,0]) > 50:
                    headRow = headRow[1:]
        Data_2_1 = Data_2.drop(range(0,max(headRow)+1)) # Removing all the rows above & including 'FolderName'
        Data_2_1.drop_duplicates()
        Data_2_1.reset_index(drop=True, inplace=True)
        Data_2_1.columns = ['VisitName']
        Data_2_1['VisitName'] = Data_2_1['VisitName'].str.replace(' ', '').str.upper()
        CPEVENT = list(Data_2_1['VisitName']) # CPEVENT later to be merged with rest of DTS data
            # Multiple Visit Sets - If there are more than 1 headRow 
        # VisitSets = len(headRow)

        ## Extract Data - QSCAT	QSSCAT	NQVERNUM
            # Data Collection Format 
        selectDCF = ["QSCAT","QSSCAT","NQVERNUM"]
        Data_3 = pd.read_excel(QSPath, sheet_name=tabDCF, skiprows=list(range(0,5)), usecols = 'A,G')
        Data_3.drop_duplicates()
        Data_3.columns = ['Variable','Value']
        Data_3 = Data_3[Data_3['Variable'].isin(selectDCF)]
        Data_3.reset_index(drop=True, inplace=True)

            # Dictionary(Code-Decode)
        Data_4 = pd.read_excel(QSPath, sheet_name=tabDict, skiprows=list(range(0,5)), usecols = 'A,B')
        Data_4.drop_duplicates()
        Data_4.columns = ['Variable','Value2']
        Data_4 = Data_4[Data_4['Variable'].isin(Data_3['Variable'])]
        Data_4 = Data_4.sort_values(['Variable'])
        Data_4.reset_index(drop=True, inplace=True)

            # Data from DCF & DCD merged - Value from DCF combined with value from DCD
            # QSCAT most likely in DCF
        DCD = pd.merge(Data_3, Data_4, how ='left', on ='Variable')
        DCD['Value2'] = DCD['Value2'].fillna(DCD['Value'])
        DCD.drop(columns=['Value'], axis=1, inplace=True)
        DCD.rename(columns={'Value2':'Value'}, inplace=True)
        DCD = DCD.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
        DCD = DCD.transpose()
        DCD.columns = DCD.iloc[0]
        DCD.reset_index(drop=True, inplace=True)
        DCD.drop(0, axis=0, inplace=True)
        DCD.reset_index(drop=True, inplace=True)

        # noQSCAT = 0 # If QSCAT data not found or NULL -- noQSCAT = 1
        # if DCD['QSCAT'].isna().sum():
        #     noQSCAT = 1

        ### MetaData 
        ## Extract Data - QSSTAT UNIT SEX LGU
        selectDCD = ['ND','QSEVAL','UNIT','SEX','LGU']
            # Dictionary(Code-Decode)
        Data_5 = pd.read_excel(QSPath, sheet_name=tabDict, skiprows=list(range(0,5)), usecols = 'A,B')
        Data_5.drop_duplicates()
        Data_5.columns = ['Variable','Value']
        Data_5 = Data_5[Data_5['Variable'].isin(selectDCD)]
        Data_5 = Data_5.sort_values(['Variable'])
        Data_5.reset_index(drop=True, inplace=True)
        Data_5 = Data_5.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
        Data_5 = Data_5.transpose()
        Data_5.columns = Data_5.iloc[0]
        Data_5.reset_index(drop=True, inplace=True)
        Data_5.drop(0, axis=0, inplace=True)
        Data_5.reset_index(drop=True, inplace=True)
        Data_5.rename(columns={'ND':'QSSTAT'}, inplace=True)
            # Adding missing columns with NaN values
        for column in ['QSSTAT','QSEVAL','UNIT','SEX','LGU']:
            if column not in Data_5.columns:
                Data_5[column] = [np.nan]

        ## Extract Data - Timepoint
        TPT = pd.read_excel(QSPath, sheet_name=tabTPT, skiprows=list(range(0,7)), usecols = 'C')
        TPT.columns = ['TPTTXT']
        TPTTXT = TPT['TPTTXT'].dropna().tolist()

        ## Extract Data - Questions
        QUES = pd.read_excel(QSPath, sheet_name=tabQS, skiprows=list(range(0,14)), usecols='A,B,C,D,F',keep_default_na=False)
        QUES.drop_duplicates()
        QUES.columns = ['QSCAT','QSSCAT','QSTSTLG','QSTSTLG_STD','QSRESCD']


        # QUES['QSEVAL'] = list(Data_5['QSEVAL'])*QUES.shape[0]
        # QUES['QSSTAT'] = list(Data_5['QSSTAT'])*QUES.shape[0]
        # if isinstance(QUES.iloc[0]['QSEVAL'], list) and len(Data_5.iloc[0]['QSEVAL']) >= 1:
        #     QUES = QUES.explode('QSEVAL')
        # if isinstance(QUES.iloc[0]['QSSTAT'], list) and len(Data_5.iloc[0]['QSSTAT']) >= 1:
        #     QUES = QUES.explode('QSSTAT')
        QSEVAL = list(Data_5['QSEVAL'])
        QSSTAT = list(Data_5['QSSTAT'])
        UNIT = list(Data_5['UNIT'])
        SEX = list(Data_5['SEX'])
        LGU = list(Data_5['LGU'])

        # Visit Data Finalization
        ## Sometime QSSCAT is only listed in Question, in that case it needs to be added to VisitData
        if len(DCD['QSSCAT'].iloc[0]) < len(set(QUES['QSSCAT'].dropna())):
            DCD['QSSCAT'].iloc[0] = list(set(QUES['QSSCAT'].dropna()))

        VisitData = pd.DataFrame()
        VisitData['STUDY'] = [Study]
        VisitData['VENDOR_NAME'] = [Vendor]
        VisitData['QSCAT'] = DCD['QSCAT']
        VisitData['QSSCAT'] = DCD['QSSCAT']
        VisitData['NQVERNUM'] = DCD['NQVERNUM']
        if isinstance(VisitData.iloc[0]['QSCAT'], list) and len(VisitData.iloc[0]['QSCAT']) >= 1:
            VisitData = VisitData.explode('QSCAT')
        if isinstance(VisitData.iloc[0]['QSSCAT'], list) and len(VisitData.iloc[0]['QSSCAT']) >= 1:
            VisitData = VisitData.explode('QSSCAT')
        if isinstance(VisitData.iloc[0]['NQVERNUM'], list) and len(VisitData.iloc[0]['NQVERNUM']) >= 1:
            VisitData = VisitData.explode('NQVERNUM')
        VisitData.reset_index(drop=True, inplace=True)
        VisitData['CPEVENT'] = [CPEVENT]*VisitData.shape[0]

        ## Add Trial Visit Data
        # Initialize columns for each trial visit
        for Visit in TVData_Visit:
            VisitData[Visit] = 'No'  # Initialize with 'No'

        # Populate 'Yes' or 'No' based on DTS CPEVENT values
        for index, row in VisitData.iterrows():
            for visit in TVData_Visit:
                if visit in row['CPEVENT']:
                    VisitData.at[index, visit] = 'Yes'
        VisitData.drop(columns=['CPEVENT'], inplace=True)

        return [VisitData, QUES, QSEVAL, QSSTAT, UNIT, SEX, LGU, TPTTXT, CPEVENT]
    
    fileDTS = fileApp[fileApp['Type'].isin(['DTS'])]

    SVData = pd.DataFrame()
    MetaData = pd.DataFrame()
    combinedQSEVAL = []
    combinedQSSTAT = []
    combinedUNIT = []
    combinedSEX = []
    combinedLGU = []
    combinedTPTTXT = []
    combinedCPEVENT = []

    ### Extract data from multiple QS DTS
    QSdetails = fileDTS[fileDTS['Domain'].isin(["QS"])]
    for fileQS in list(QSdetails['FileName']):
        d = extractQSdata(StudyDir,fileQS)
        SVData = pd.concat([SVData,d[0]], axis=0)
        MetaData = pd.concat([MetaData,d[1]], axis=0)
        combinedQSEVAL = combinedQSEVAL + d[2]
        combinedQSSTAT = combinedQSSTAT + d[3]
        combinedUNIT = combinedUNIT + d[4]
        combinedSEX = combinedSEX + d[5]
        combinedLGU = combinedLGU + d[6]
        combinedTPTTXT = combinedTPTTXT + d[7]
        combinedCPEVENT = combinedCPEVENT + d[8]

    SVData.reset_index(drop=True, inplace=True)
    MetaData.reset_index(drop=True, inplace=True)

    def cleanLists(list_):
        # Remove NaNs
        clean_list = pd.Series(list_).dropna().tolist()
        # Flatten lists
        flat_list = list(itertools.chain.from_iterable(clean_list))
        # Remove NaNs 
        flat_list = pd.Series(flat_list).dropna().tolist()
        # Remove duplicates
        listFinal = list(set(flat_list))
        return listFinal

    def remove_duplicates(lst):
        seen = set()
        unique_list = []
        for item in lst:
            if item not in seen:
                unique_list.append(item)
                seen.add(item)
        return unique_list

    combinedQSEVAL = cleanLists(combinedQSEVAL)
    combinedQSSTAT = cleanLists(combinedQSSTAT)
    combinedUNIT = cleanLists(combinedUNIT)
    combinedSEX = cleanLists(combinedSEX)
    combinedLGU = cleanLists(combinedLGU)
    combinedTPTTXT = remove_duplicates(combinedTPTTXT)
    combinedCPEVENT = remove_duplicates(combinedCPEVENT)

    SVData.reset_index(drop=True, inplace=True)
    MetaData.reset_index(drop=True, inplace=True)

    # Path to the template onboarding excel
    TempPath = os.path.join(BaseDir,"Templates","STUDY_QS_MetaData Consistency Report_Mapping file.xlsx")

    with xw.App(visible=False) as app:
        wb = xw.Book(TempPath)
        inputFile = str(Study)+"_QS_MetaData Consistency Report_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        wb.save(InputPath)
        wb.close()

    with xw.App(visible=False) as app:
        #saving mapping file instance as a template
        inputFile = str(Study)+"_QS_MetaData Consistency Report_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        MapFile = xw.Book(InputPath)

        ## QSCAT_SV
        Visit = MapFile.sheets['QSCAT_SV']
        Visit.range("A2").options(index=False).value = SVData

        ## MetaData
        Meta = MapFile.sheets['MetaData']
        # QSEVAL QSSTAT	UNIT SEX LGU TPTTXT	CPEVENT
        Meta["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value = MetaData
        Meta.range("F1").options(index=False).value = pd.DataFrame({'QSEVAL':combinedQSEVAL})
        Meta.range("G1").options(index=False).value = pd.DataFrame({'QSSTAT':combinedQSSTAT})
        Meta.range("H1").options(index=False).value = pd.DataFrame({'UNIT':combinedUNIT})
        Meta.range("I1").options(index=False).value = pd.DataFrame({'SEX':combinedSEX})
        Meta.range("J1").options(index=False).value = pd.DataFrame({'LGU':combinedLGU})
        Meta.range("K1").options(index=False).value = pd.DataFrame({'TPTTXT':combinedTPTTXT})
        Meta.range("L1").options(index=False).value = pd.DataFrame({'CPEVENT':combinedCPEVENT})
        
        #saving the final file
        inputFile1 = str(Study)+"_QS_MetaData Consistency Report_Mapping file.xlsx"
        InputPath1 = os.path.join(StudyDir, inputFile1)
        MapFile.save(InputPath1)
        MapFile.close()
        
    return inputFile1

def generateLBMapping(Study, BaseDir):
    StudyDir = os.path.join(BaseDir,Study)
    ###### Categorize Files - DTS & TV -----------------------------------------------------------------
    file_list =os.listdir(StudyDir)
    # Only the relevent files - TV & DTS (applicable domains), are neded
    Study_ = []
    Domain_ = []
    Type_ = []
    FileName_ = []
    Ext_ = []
    for file in file_list:
        if '_' in file:
            string = file.split('_')
            ext = file.split('.')
            #Study_.append(string[0])
            #Domain_.append(string[1][0:2])
            if "TV" in file or "tv" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('TV')
                FileName_.append(file)
                Ext_.append(ext[-1])
            elif "DTS" in file or "Data Transfer Specification" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('DTS')
                FileName_.append(file)
                Ext_.append(ext[-1])

    # All the files in the study directory
    fileAll = pd.DataFrame({'Study':Study_,'Domain':Domain_,'Type':Type_,'FileName':FileName_,'Ext':Ext_})
    applicableDomains = ['LB','TV']
    # Files with domain applicable to TVT
    fileApp= fileAll[fileAll['Domain'].isin(applicableDomains)]
    fileApp = fileApp[fileApp['Ext'].isin(['xlsx'])]
    fileApp.reset_index(drop=True, inplace=True)
    
    ###### Reading TV File -----------------------------------------------------------------
    TVdetails = fileApp[fileApp['Domain'].isin(["TV"])]
    TVData = pd.DataFrame()
    TVPath = os.path.join(StudyDir,TVdetails.iloc[0]['FileName'])
    nameTV = pd.ExcelFile(TVPath).sheet_names
    if len(nameTV) > 1:
        tabTV = [i for i in nameTV if i in 'TV'][0]
    else:
        tabTV = nameTV[0]
    TVData = pd.read_excel(TVPath, sheet_name=tabTV)
    TVData.replace('', np.nan, inplace=True)
    TVData = TVData.dropna(thresh=3) # Removing all rows with more than 3 NaN. STUDY, DOMAIN, VISIT ought to be there in TV
    TVData.reset_index(drop=True,inplace=True)
    # Fixing the header for non standard TV files
        # Searching the following list in rows of TV Data & retriving the row number that has a match
    headTV1 = ['DOMAIN','CPEVENT','VISITDY']
    headTV2 = ['StudyIdentifier','VisitName','VisitNumber']

    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]
    headRow = 0
    if any(e in headTV1 for e in TVData.columns):
        TVData = TVData
    elif any(e in headTV2 for e in TVData.columns):
        TVData = TVData
    else:
        for i, row in TVData.iterrows():
            row = [str(x).replace(' ', '') for x in row]
            if any(e in headTV1 for e in list(row)):
                headRow = i
                break
            elif any(e in headTV2 for e in list(row)):
                headRow = i
                break
        TVData = TVData.set_axis(TVData.iloc[0], axis=1).iloc[headRow:]

    # Fixing the content rows for non standard TV files
        # Searching the study ID and TV in rows of TV Data & retriving the row number that has a match
    contentTV = [Study,'TV']
    for i, row in TVData.iterrows():
        if any(e in contentTV for e in list(row)):
            contentRow = i
            break
    TVData = TVData.drop(range(0,contentRow))
    TVData.reset_index(drop=True, inplace=True)
    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]

    if "VisitName" in TVData.columns:
        TVData.rename(columns={'VisitName':'CPEVENT'}, inplace=True)
    if "VISIT" in TVData.columns:
        TVData.rename(columns={'VISIT':'CPEVENT'}, inplace=True)

    TVData = TVData[['CPEVENT']]
    TVData.drop_duplicates(inplace=True)
    TVData.reset_index(drop=True, inplace=True)

    # Remove leading & trailing spaces from CPEVENT
    TVData['CPEVENT'] = TVData['CPEVENT'].str.replace(' ', '').str.upper()
    TVData_Visit = list(TVData['CPEVENT'])

    ###### Reading Data from DTS -----------------------------------------------------------------
    LBdetails = fileApp[fileApp['Domain'].isin(["LB"])]
    fileLB = list(LBdetails['FileName'])[0]
    LBPath = os.path.join(StudyDir,fileLB)
    nameLB = pd.ExcelFile(LBPath).sheet_names
    tabLB = [i for i in nameLB if 'PARAMETER' in i.upper().replace(' ','')][0]
    tabDCF = [i for i in nameLB if 'DATACOLLECTIONFORMAT' in i.upper().replace(' ','')][0]
    tabDict = [i for i in nameLB if 'DICTIONARY' in i.upper().replace(' ','')][0]
    tabCover = [i for i in nameLB if 'COVER' in i.upper().replace(' ','')][0]
    tabVisit = [i for i in nameLB if 'VISIT' in i.upper().replace(' ','')][0]
    tabUnit = [i for i in nameLB if 'LABUNIT' in i.upper().replace(' ','')][0]

    # Extracting Vendor
    Data_1 = pd.read_excel(LBPath, sheet_name=tabCover, keep_default_na=False)
    orig_Data_1 = Data_1
    Data_1 = Data_1.dropna(thresh=2) # Remove empty rows
    Data_1 = Data_1.dropna(thresh=len(Data_1) - 1, axis=1) # Remove empty columns
    Data_1.reset_index(drop=True, inplace=True)
    Data_1.columns = ['Col1','Col2']
    #Domain = Data_1.loc[Data_1['Col1'].str.contains('Domain'), 'Col2'].squeeze()
    Vendor = Data_1.loc[Data_1['Col1'].str.contains('Vendor'), 'Col2'].squeeze()
    Vendor = Vendor.upper()

    # Extracting Visit Data
    Data_2 = pd.read_excel(LBPath, sheet_name=tabVisit, usecols='A', keep_default_na=False)
    Data_2 = Data_2.dropna()
    Data_2.reset_index(drop=True, inplace=True)
    headRow = []
    for i, row in Data_2.iterrows():
        if 'FOLDERNAME' in str(row[0]).upper() or 'FOLDER NAME' in str(row[0]).upper():
                headRow.append(i)
    # Sometimes there is a FOLDERNAME element with a big description under it. In such case the 1st headRow must be disregarded.
    if len(headRow) > 1:
        for i in range(headRow[0],headRow[1]):
            if len(Data_2.iloc[headRow[0]+1,0]) > 50:
                headRow = headRow[1:]
    Data_2_1 = Data_2.drop(range(0,max(headRow)+1)) # Removing all the rows above & including 'FolderName'
    Data_2_1.drop_duplicates()
    Data_2_1.reset_index(drop=True, inplace=True)
    Data_2_1.columns = ['VisitName']
    Data_2_1['VisitName'] = Data_2_1['VisitName'].str.replace(' ','').str.upper()
    CPEVENT = list(Data_2_1['VisitName']) # CPEVENT later to be merged with rest of DTS data
        #### Multiple Visit Sets - If there are more than 1 headRow 
    # VisitSets = len(headRow)

    # Extract Test Data
        ## Find DTS Version
        ## DTS versions after 7 have a different table structure
    def findVerDTS(Data_1):
        VerDTS1 = Data_1.iloc[Data_1.shape[0]-1,]
        VerDTS1 = [x for x in VerDTS1 if pd.notnull(x)]
        VerDTS1 = np.char.replace(VerDTS1[0], ' ', '')

        VerDTS = str(VerDTS1).split('TemplateVersion:', 1)[1]
        VerDTS = (VerDTS[:2])
        VerDTS = int(VerDTS.replace('.', ''))
        return VerDTS

    VersionDTS = findVerDTS(orig_Data_1)

    if VersionDTS < 7:
        Data_3 = pd.read_excel(LBPath, sheet_name=tabLB, usecols='A,B,C', keep_default_na=False) # Test info usually starts after row 5 - skiprows=list(range(0,4))
    if VersionDTS >= 7:
        Data_3 = pd.read_excel(LBPath, sheet_name=tabLB, usecols='J,K,L', keep_default_na=False) # Test info usually starts after row 7 - skiprows=list(range(0,7))
    Data_3.columns = ['A','B','C']
    Data_3_Temp = pd.DataFrame({'A':Data_3['A']})
    # The relevent data starts after 'LBPARM'. Removing rest rows.
    headRow1 = []
    for i, row in Data_3_Temp.iterrows():
        if 'LBPARM' in str(row[0]).upper():
            headRow1.append(i)
    Data_3 = Data_3.drop(range(0,headRow1[0]+1)) # Removing all the rows above & including 'LBPARM'
    Data_3.reset_index(drop=True, inplace=True)

    Data_3.columns = ['LBPARM','PARMDES','Unit']
    Data_3['UNITS_EXPECTED'] = Data_3['Unit'].apply(lambda x: 'No' if pd.isnull(x) or x == '' else 'Yes')

    PARMData = pd.DataFrame()
    PARMData['STUDY_NAME'] = [Study]*Data_3.shape[0]
    PARMData['VENDOR_NAME'] = [Vendor]*Data_3.shape[0]
    PARMData['PARMDES'] = Data_3['PARMDES']
    PARMData['LBPARM'] = Data_3['LBPARM'].str.replace('\n', '').str.strip().str.upper()

    # Category data from Reference Metadata
    RefM = os.path.join(BaseDir,"Reference Metadata_LB.xlsx")
    RefMet = pd.read_excel(RefM, usecols='B,I', keep_default_na=False)
    RefMet.columns = ['LBPARM','CATEGORY']
    RefMet['CATEGORY'] = RefMet['CATEGORY'].str.replace('\n', '').str.strip()
    RefMet['LBPARM'] = RefMet['LBPARM'].str.replace('\n', '').str.strip()
    PARMData = pd.merge(PARMData, RefMet, how ='left', on ='LBPARM')
    PARMData['UNITS_EXPECTED'] = Data_3['UNITS_EXPECTED']
    PARMData['RANGES_EXPECTED'] = ['']*PARMData.shape[0]
    # Combining with Visits
    #LBData_Final = pd.concat([LBData.assign(CPEVENT=i) for i in CPEVENT], ignore_index=True)

    PARMData['CPEVENT'] = [CPEVENT]*PARMData.shape[0]

    ## Add Trial Visit Data
    # Initialize columns for each trial visit
    for Visit in TVData_Visit:
        PARMData[Visit] = 'No'  # Initialize with 'No'

    # Populate 'Yes' or 'No' based on DTS CPEVENT values
    for index, row in PARMData.iterrows():
        for visit in TVData_Visit:
            if visit in row['CPEVENT']:
                PARMData.at[index, visit] = 'Yes'
    PARMData.drop(columns=['CPEVENT'], inplace=True)

    Data_4 = pd.read_excel(LBPath, sheet_name=tabDCF, skiprows=list(range(0,5)), usecols = 'A,F', keep_default_na=False)
    Data_4.drop_duplicates()
    Data_4.columns = ['Variable','Value']
    selectDCF = ['CRNGFLG','RNGFLAG','CSTDTP','LBFAST','LBSPCCND','LBCSEX','LBSTAT','STATLB','QCFLGLB','LBQCFLG','TPTTXT','TPTU','RTPT']
    DCF = Data_4[Data_4['Variable'].isin(selectDCF)]
    DCF.reset_index(drop=True, inplace=True)

    # Extracting info from Dictionary(Code-Decode)
    Data_5 = pd.read_excel(LBPath, sheet_name=tabDict, usecols = 'A,B', keep_default_na=False)
    Data_5.drop_duplicates()
    Data_5.columns = ['Variable','Value']

    DCD = Data_5[Data_5['Variable'].isin(list(DCF['Value']))]
    DCD.reset_index(drop=True, inplace=True)

    # Extracting Prefered Units from Lab Units
    if VersionDTS < 7:
        Data_6 = pd.read_excel(LBPath, sheet_name=tabUnit, usecols = 'B', skiprows=list(range(0,7)), keep_default_na=False)
    if VersionDTS >= 7:
        Data_6 = pd.read_excel(LBPath, sheet_name=tabUnit, usecols = 'B', skiprows=list(range(0,6)), keep_default_na=False)
    Data_6.columns = ['CLABUNIT/LBORRESU']

    mdata = pd.merge(DCF,Data_5, how ='left', left_on=DCF['Value'].str.lower().str.replace(' ',''), right_on=Data_5['Variable'].str.lower().str.replace(' ',''))
    mdata.drop(columns=['key_0','Value_x','Variable_y'], inplace=True)
    mdata.rename(columns={'Variable_x':'Variable','Value_y':'Value'}, inplace=True)

    #Col = ['CRNGFLG/RNGFLAG','CRNGFLG/RNGFLAG','CSTDTP','LBFAST','LBSPCCND','LBCSEX','LBSTAT/STATLB','LBSTAT/STATLB','QCFLGLB/LBQCFLG','QCFLGLB/LBQCFLG','TPTTXT/TPTU/RTPT','TPTTXT/TPTU/RTPT','TPTTXT/TPTU/RTPT']
    for i, row in mdata.iterrows():
        if 'CRNGFLG' in row[0] or 'RNGFLAG' in row[0]:
            row[0] = 'CRNGFLG/RNGFLAG'
        elif 'LBSTAT' in row[0] or 'STATLB' in row[0]:
            row[0] = 'LBSTAT/STATLB'
        elif 'QCFLGLB' in row[0] or 'LBQCFLG' in row[0]:
            row[0] = 'QCFLGLB/LBQCFLG'
        elif 'TPTTXT' in row[0] or 'TPTU' in row[0] or 'RTPT' in row[0]:
            row[0] = 'TPTTXT/TPTU/RTPT'

    MetaData = mdata.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
    MetaData = MetaData.transpose()
    MetaData.columns = MetaData.iloc[0]
    MetaData.reset_index(drop=True, inplace=True)
    MetaData = MetaData.drop(0, axis=0)
    MetaData.reset_index(drop=True, inplace=True)

    PARMData.drop_duplicates(inplace=True)

    # Path to the template onboarding excel
    TempPath = os.path.join(BaseDir,"Templates","STUDY_Central Lab MetaData Consistency Report_Mapping file.xlsx")

    with xw.App(visible=False) as app:
        wb = xw.Book(TempPath)
        #saving the template instance 
        inputFile = str(Study)+"_Central Lab MetaData Consistency Report_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        wb.save(InputPath)
        wb.close()
    with xw.App(visible=False) as app:
        inputFile = str(Study)+"_Central Lab MetaData Consistency Report_Mapping file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        MapFile = xw.Book(InputPath)

        PARM = MapFile.sheets['PARM_SV']
        
        PARM.range("A2").options(index=False).value = PARMData['STUDY_NAME']
        PARM.range("B2").options(index=False).value = PARMData['VENDOR_NAME']
        PARM.range("C2").options(index=False).value = PARMData['PARMDES']
        PARM.range("D2").options(index=False).value = PARMData['LBPARM']
        PARM.range("E2").options(index=False).value = PARMData['CATEGORY']
        PARM.range("F2").options(index=False).value = PARMData['UNITS_EXPECTED']
        PARM.range("G2").options(index=False).value = PARMData['RANGES_EXPECTED']
        PARM["H2"].options(pd.DataFrame, header=1, index=False, expand='table').value = PARMData.iloc[:,7:]
        
        Meta = MapFile.sheets['MetaData']

        # 'CRNGFLG/RNGFLAG','CSTDTP','LBFAST','LBSPCCND','LBCSEX','LBSTAT/STATLB','QCFLGLB/LBQCFLG','TPTTXT/TPTU/RTPT', 'CLABUNIT/LBORRESU'
        Meta.range("A1").options(index=False).value = pd.DataFrame({'CRNGFLG/RNGFLAG':MetaData.iloc[0]['CRNGFLG/RNGFLAG']})
        Meta.range("B1").options(index=False).value = pd.DataFrame({'CSTDTP':MetaData.iloc[0]['CSTDTP']})
        Meta.range("C1").options(index=False).value = pd.DataFrame({'LBFAST':MetaData.iloc[0]['LBFAST']})
        Meta.range("D1").options(index=False).value = pd.DataFrame({'LBSPCCND':MetaData.iloc[0]['LBSPCCND']})
        Meta.range("E1").options(index=False).value = pd.DataFrame({'LBCSEX':MetaData.iloc[0]['LBCSEX']})
        Meta.range("F1").options(index=False).value = pd.DataFrame({'LBSTAT/STATLB':MetaData.iloc[0]['LBSTAT/STATLB']})
        Meta.range("G1").options(index=False).value = pd.DataFrame({'QCFLGLB/LBQCFLG':MetaData.iloc[0]['QCFLGLB/LBQCFLG']})
        Meta.range("H1").options(index=False).value = pd.DataFrame({'TPTTXT/TPTU/RTPT':MetaData.iloc[0]['TPTTXT/TPTU/RTPT']})
        Meta.range("I1").options(index=False).value = pd.DataFrame({'CLABUNIT/LBORRESU':Data_6['CLABUNIT/LBORRESU'].unique()})
        
        #saving file file with new name
        inputFile1 = str(Study)+"_Central Lab MetaData Consistency Report_Mapping file.xlsx"
        InputPath1 = os.path.join(StudyDir, inputFile1)
        MapFile.save(InputPath1)
        MapFile.close()
    return inputFile1

def generateZWMapping(Study, BaseDir):
    StudyDir = os.path.join(BaseDir,Study)
    ###### Categorize Files - DTS & TV -----------------------------------------------------------------
    file_list =os.listdir(StudyDir)
    # Only the relevent files - TV & DTS (applicable domains), are neded
    Study_ = []
    Domain_ = []
    Type_ = []
    FileName_ = []
    Ext_ = []
    for file in file_list:
        if '_' in file:
            string = file.split('_')
            ext = file.split('.')
            #Study_.append(string[0])
            #Domain_.append(string[1][0:2])
            if "TV" in file or "tv" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('TV')
                FileName_.append(file)
                Ext_.append(ext[-1])
            elif "DTS" in file or "Data Transfer Specification" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('DTS')
                FileName_.append(file)
                Ext_.append(ext[-1])

    # All the files in the study directory
    fileAll = pd.DataFrame({'Study':Study_,'Domain':Domain_,'Type':Type_,'FileName':FileName_,'Ext':Ext_})
    applicableDomains = ['ZW','TV']
    # Files with domain applicable to TVT
    fileApp= fileAll[fileAll['Domain'].isin(applicableDomains)]
    fileApp = fileApp[fileApp['Ext'].isin(['xlsx'])]
    fileApp.reset_index(drop=True, inplace=True)
    
    ###### Reading TV File -----------------------------------------------------------------
    TVdetails = fileApp[fileApp['Domain'].isin(["TV"])]
    TVData = pd.DataFrame()
    TVPath = os.path.join(StudyDir,TVdetails.iloc[0]['FileName'])
    nameTV = pd.ExcelFile(TVPath).sheet_names
    if len(nameTV) > 1:
        tabTV = [i for i in nameTV if i in 'TV'][0]
    else:
        tabTV = nameTV[0]
    TVData = pd.read_excel(TVPath, sheet_name=tabTV)
    TVData.replace('', np.nan, inplace=True)
    TVData = TVData.dropna(thresh=3) # Removing all rows with more than 3 NaN. STUDY, DOMAIN, VISIT ought to be there in TV
    TVData.reset_index(drop=True,inplace=True)
    # Fixing the header for non standard TV files
        # Searching the following list in rows of TV Data & retriving the row number that has a match
    headTV1 = ['DOMAIN','CPEVENT','VISITDY']
    headTV2 = ['StudyIdentifier','VisitName','VisitNumber']

    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]
    headRow = 0
    if any(e in headTV1 for e in TVData.columns):
        TVData = TVData
    elif any(e in headTV2 for e in TVData.columns):
        TVData = TVData
    else:
        for i, row in TVData.iterrows():
            row = [str(x).replace(' ', '') for x in row]
            if any(e in headTV1 for e in list(row)):
                headRow = i
                break
            elif any(e in headTV2 for e in list(row)):
                headRow = i
                break
        TVData = TVData.set_axis(TVData.iloc[0], axis=1).iloc[headRow:]

    # Fixing the content rows for non standard TV files
        # Searching the study ID and TV in rows of TV Data & retriving the row number that has a match
    contentTV = [Study,'TV']
    for i, row in TVData.iterrows():
        if any(e in contentTV for e in list(row)):
            contentRow = i
            break
    TVData = TVData.drop(range(0,contentRow))
    TVData.reset_index(drop=True, inplace=True)
    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]

    if "VisitName" in TVData.columns:
        TVData.rename(columns={'VisitName':'CPEVENT'}, inplace=True)
    if "VISIT" in TVData.columns:
        TVData.rename(columns={'VISIT':'CPEVENT'}, inplace=True)

    TVData = TVData[['CPEVENT']]
    TVData.drop_duplicates(inplace=True)
    TVData.reset_index(drop=True, inplace=True)

    # Remove leading & trailing spaces from CPEVENT
    TVData['CPEVENT'] = TVData['CPEVENT'].str.replace(' ', '').str.upper()
    TVData_Visit = list(TVData['CPEVENT'])

    ZWdetails = fileApp[fileApp['Domain'].isin(["ZW"])]
    fileZW = list(ZWdetails['FileName'])[0]
    ZWPath = os.path.join(StudyDir,fileZW)
    nameZW = pd.ExcelFile(ZWPath).sheet_names

    tabCover = [i for i in nameZW if 'COVER' in i.upper().replace(' ','')][0]
    tabVisit = [i for i in nameZW if 'VISIT' in i.upper().replace(' ','')][0]
    tabDict = [i for i in nameZW if 'DICTIONARY' in i.upper().replace(' ','')][0]

    ### Visit Data
    ## Extracting Domain from Cover tab
    Data_1 = pd.read_excel(ZWPath, sheet_name=tabCover, keep_default_na=False)
    Data_1 = Data_1.dropna(thresh=2) # Remove empty rows
    Data_1 = Data_1.dropna(thresh=len(Data_1) - 1, axis=1) # Remove empty columns
    Data_1.reset_index(drop=True, inplace=True)
    Data_1.columns = ['Col1','Col2']
    # Domain = Data_1.loc[Data_1['Col1'].str.contains('Domain'), 'Col2'].squeeze()
    Vendor = Data_1.loc[Data_1['Col1'].str.contains('Vendor'), 'Col2'].squeeze()
    Vendor = Vendor.upper()

    ## Extracting Visit Data from Folder(Visit) tab
    Data_2 = pd.read_excel(ZWPath, sheet_name=tabVisit, usecols='A', keep_default_na=False)
    Data_2 = Data_2.dropna()
    Data_2.reset_index(drop=True, inplace=True)
        # Determining the position of header row - FOLDERNAME
    headRow = []
    for i, row in Data_2.iterrows():
        if 'FOLDERNAME' in str(row[0]).upper() or 'FOLDER NAME' in str(row[0]).upper():
            headRow.append(i)
        # Sometimes there is a FOLDERNAME element with a big description under it. In such case the 1st headRow must be disregarded.
    if len(headRow) > 1:
        for i in range(headRow[0],headRow[1]):
            if len(Data_2.iloc[headRow[0]+1,0]) > 50:
                headRow = headRow[1:]
    Data_2_1 = Data_2.drop(range(0,max(headRow)+1)) # Removing all the rows above & including 'FolderName'
    Data_2_1.drop_duplicates()
    Data_2_1.reset_index(drop=True, inplace=True)
    Data_2_1.columns = ['VisitName']
    Data_2_1['VisitName'] = Data_2_1['VisitName'].str.replace(' ', '').str.upper()
    CPEVENT = list(Data_2_1['VisitName']) # CPEVENT later to be merged with rest of DTS data
        # Multiple Visit Sets - If there are more than 1 headRow 
    # VisitSets = len(headRow)

    ## Extract Data - ZWCAT, ZWSCAT, ZWTEST, UNIT, LAT, LOC
    # Dictionary(Code-Decode)
    selectDCD = ["ZWCAT","ZWSCAT","ZWTEST","UNIT","LAT","LOC"]
    DCD = pd.read_excel(ZWPath, sheet_name=tabDict, skiprows=list(range(0,5)), usecols = 'A,B,C', keep_default_na=False)
    DCD.drop_duplicates()
    DCD.columns = ['Variable','Value','Value2']
    DCD = DCD[DCD['Variable'].isin(selectDCD)]
    DCD.reset_index(drop=True, inplace=True)
    DCD['Value'] = DCD['Value'].str.replace('\t', '')

    DCD1 = DCD.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
    DCD1 = DCD1.transpose()
    DCD1.columns = DCD1.iloc[0]
    DCD1.reset_index(drop=True, inplace=True)
    DCD1.drop(0, axis=0, inplace=True)
    DCD1.reset_index(drop=True, inplace=True)
    # Adding missing columns with NaN values
    for column in selectDCD:
        if column not in DCD1.columns:
            DCD1[column] = [np.nan]

    DCD2 = DCD.groupby(['Variable'])['Value2'].apply(lambda x: list(x)).reset_index()
    DCD2 = DCD2.transpose()
    DCD2.columns = DCD2.iloc[0]
    DCD2.reset_index(drop=True, inplace=True)
    DCD2.drop(0, axis=0, inplace=True)
    DCD2.reset_index(drop=True, inplace=True)

    VisitData = pd.DataFrame()
    VisitData['Study_Name'] = [Study]
    VisitData['VENDOR_NAME'] = [Vendor]
    VisitData['ZWCAT'] = DCD1['ZWCAT']
    VisitData['ZWSCAT'] = DCD1['ZWSCAT']
    VisitData = VisitData.explode('ZWCAT')
    VisitData = VisitData.explode('ZWSCAT')
    VisitData['CPEVENT'] = [CPEVENT]*VisitData.shape[0]
    ## Add Trial Visit Data
    # Initialize columns for each trial visit
    for Visit in TVData_Visit:
        VisitData[Visit] = 'No'  # Initialize with 'No'

    # Populate 'Yes' or 'No' based on DTS CPEVENT values
    for index, row in VisitData.iterrows():
        for visit in TVData_Visit:
            if visit in row['CPEVENT']:
                VisitData.at[index, visit] = 'Yes'
    VisitData.drop(columns=['CPEVENT'], inplace=True)

    RefM = os.path.join(BaseDir,"Reference Metadata_ZW.xlsx")
    RM_Test = pd.read_excel(RefM, sheet_name='TEST_CATEGORY', keep_default_na=False)
    RM_Unit = pd.read_excel(RefM, sheet_name='TEST_UNITS', keep_default_na=False)

    selectTest = ['TESTCD','CAT','SCAT']
    RM_Test = RM_Test[selectTest]

    selectUnit = ['PARM','UNITTP','PREUNIT']
    RM_Unit = RM_Unit[selectUnit]
    RM_Unit.rename(columns={'PARM':'ZWTEST'}, inplace=True)
    # RM_Unit = RM_Unit[RM_Unit['UNITTP'].isin(['SI','CODED'])]
    RM_Unit.drop(columns=['UNITTP'], inplace=True)
    RM_Unit = RM_Unit[RM_Unit['ZWTEST'].isin(list(DCD1.iloc[0]['ZWTEST']))]
    RM_Unit.reset_index(drop=True, inplace=True)

    if type(DCD1.iloc[0]['UNIT']) is list:
        unitsDTS = [elem.strip().upper().replace(' ','') for elem in DCD1.iloc[0]['UNIT']]
        # Function to match units with accepted units list
        def match_units(unit, accepted_units):
            if unit.upper().replace(' ','') in accepted_units:
                return unit
            else:
                return np.nan

        # Apply the function to the 'unit' column
        RM_Unit['UNIT'] = RM_Unit['PREUNIT'].apply(lambda x: match_units(x, unitsDTS))
    else:
        if np.isnan(DCD1.iloc[0]['UNIT']):
            RM_Unit['UNIT'] = [np.nan]*RM_Unit.shape[0]
        
    RM_Unit.drop(columns=['PREUNIT'], inplace=True)
    RM_Unit.rename(columns={'UNIT':'ZWORRESU'}, inplace=True)
    RM_Unit.dropna(subset=['ZWORRESU'], inplace=True)
    RM_Unit.reset_index(drop=True, inplace=True)
    
    RM_Test = RM_Test[RM_Test['TESTCD'].isin(list(DCD1.iloc[0]['ZWTEST']))]
    RM_Test = RM_Test[RM_Test['CAT'].isin(list(DCD1.iloc[0]['ZWCAT']))]
    if isinstance(DCD1.iloc[0]['ZWSCAT'], list):
        if (~pd.isna(DCD1.iloc[0]['ZWSCAT'])[0]):
            RM_Test = RM_Test[RM_Test['SCAT'].isin(list(DCD1.iloc[0]['ZWSCAT']))]
    else:
        if (~np.isnan(DCD1.iloc[0]['ZWSCAT'])):
            RM_Test = RM_Test[RM_Test['SCAT'].isin(list(DCD1.iloc[0]['ZWSCAT']))]
    RM_Test.reset_index(drop=True,inplace=True)
    RM_Test.rename(columns={'TESTCD':'ZWTEST','CAT':'ZWCAT','SCAT':'ZWSCAT'}, inplace=True)

    MetaData = pd.DataFrame()
    MetaData['ZWTEST'] = DCD1.iloc[0]['ZWTEST']
    MetaData['ZWTEST2'] = DCD2.iloc[0]['ZWTEST']
    MetaData['ZWLAT'] = [DCD1.iloc[0]['LAT']]*MetaData.shape[0]
    MetaData['ZWLOC'] = [DCD1.iloc[0]['LOC']]*MetaData.shape[0]
    MetaData = MetaData.explode('ZWLOC')
    MetaData = MetaData.explode('ZWLAT')

    testNoCAT = list(set(DCD1.iloc[0]['ZWTEST']) - set(RM_Test['ZWTEST']))
    tempMD = pd.DataFrame()
    tempMD['ZWCAT'] = DCD1['ZWCAT']
    tempMD['ZWSCAT'] = np.nan # DCD1['ZWSCAT']
    tempMD['ZWTEST'] = [testNoCAT]
    tempMD = tempMD.explode('ZWTEST')
    tempMD = tempMD.explode('ZWSCAT')
    tempMD = tempMD.explode('ZWCAT')
    tempMD.reset_index(drop=True, inplace=True)
    tempMD = pd.concat([RM_Test, tempMD])
    tempMD.reset_index(drop=True, inplace=True)

    MetaData = pd.merge(MetaData, tempMD, how ='left', on ='ZWTEST')
    MetaData['Vendor_Name'] = [Vendor]*MetaData.shape[0]
    MetaData['Study_Name'] = [Study]*MetaData.shape[0]
    MetaData = pd.merge(MetaData, RM_Unit, how ='left', on ='ZWTEST')
    MetaData.drop(columns=['ZWTEST'], inplace=True)
    MetaData.rename(columns={'ZWTEST2':'ZWTEST'}, inplace=True)
    MetaData.reset_index(drop=True, inplace=True)
    MetaData = MetaData[['Study_Name','Vendor_Name','ZWCAT','ZWSCAT','ZWTEST','ZWORRESU','ZWLAT','ZWLOC']]

    # Path to the template onboarding excel
    TempPath = os.path.join(BaseDir,"Templates","STUDY_Actigraphy_Metadata_Mapping_File.xlsx")

    with xw.App(visible=False) as app:
        wb = xw.Book(TempPath)
        #saving mapping file instance as template
        inputFile = str(Study)+"_Actigraphy_Metadata_Mapping_File_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        wb.save(InputPath)
        wb.close()

    with xw.App(visible=False) as app:
        inputFile = str(Study)+"_Actigraphy_Metadata_Mapping_File_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        MapFile = xw.Book(InputPath)

        ## ZW_SV
        Visit = MapFile.sheets['ZW_SV']
        Visit.range("A2").options(index=False).value = VisitData

        ## MetaData - Mapping file
        Meta = MapFile.sheets['Mapping file']
        Meta["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value = MetaData

        inputFile1 = str(Study)+"_Actigraphy_Metadata_Mapping_File.xlsx"
        InputPath1 = os.path.join(StudyDir, inputFile1)
        MapFile.save(InputPath1)
        MapFile.close()
    return inputFile1

def generateEGMapping(Study, BaseDir):
    StudyDir = os.path.join(BaseDir,Study)
    ###### Categorize Files - DTS & TV -----------------------------------------------------------------
    file_list =os.listdir(StudyDir)
    # Only the relevent files - TV & DTS (applicable domains), are neded
    Study_ = []
    Domain_ = []
    Type_ = []
    FileName_ = []
    Ext_ = []
    for file in file_list:
        if '_' in file:
            string = file.split('_')
            ext = file.split('.')
            #Study_.append(string[0])
            #Domain_.append(string[1][0:2])
            if "TV" in file or "tv" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('TV')
                FileName_.append(file)
                Ext_.append(ext[-1])
            elif "DTS" in file or "Data Transfer Specification" in file:
                Study_.append(string[0])
                Domain_.append((string[1][0:2]).upper())
                Type_.append('DTS')
                FileName_.append(file)
                Ext_.append(ext[-1])

    # All the files in the study directory
    fileAll = pd.DataFrame({'Study':Study_,'Domain':Domain_,'Type':Type_,'FileName':FileName_,'Ext':Ext_})
    applicableDomains = ['EG','TV']
    # Files with domain applicable to TVT
    fileApp= fileAll[fileAll['Domain'].isin(applicableDomains)]
    fileApp = fileApp[fileApp['Ext'].isin(['xlsx'])]
    fileApp.reset_index(drop=True, inplace=True)
    
    ###### Reading TV File -----------------------------------------------------------------
    TVdetails = fileApp[fileApp['Domain'].isin(["TV"])]
    TVData = pd.DataFrame()
    TVPath = os.path.join(StudyDir,TVdetails.iloc[0]['FileName'])
    nameTV = pd.ExcelFile(TVPath).sheet_names
    if len(nameTV) > 1:
        tabTV = [i for i in nameTV if i in 'TV'][0]
    else:
        tabTV = nameTV[0]
    TVData = pd.read_excel(TVPath, sheet_name=tabTV)
    TVData.replace('', np.nan, inplace=True)
    TVData = TVData.dropna(thresh=3) # Removing all rows with more than 3 NaN. STUDY, DOMAIN, VISIT ought to be there in TV
    TVData.reset_index(drop=True,inplace=True)
    # Fixing the header for non standard TV files
        # Searching the following list in rows of TV Data & retriving the row number that has a match
    headTV1 = ['DOMAIN','CPEVENT','VISITDY']
    headTV2 = ['StudyIdentifier','VisitName','VisitNumber']

    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]
    headRow = 0
    if any(e in headTV1 for e in TVData.columns):
        TVData = TVData
    elif any(e in headTV2 for e in TVData.columns):
        TVData = TVData
    else:
        for i, row in TVData.iterrows():
            row = [str(x).replace(' ', '') for x in row]
            if any(e in headTV1 for e in list(row)):
                headRow = i
                break
            elif any(e in headTV2 for e in list(row)):
                headRow = i
                break
        TVData = TVData.set_axis(TVData.iloc[0], axis=1).iloc[headRow:]

    # Fixing the content rows for non standard TV files
        # Searching the study ID and TV in rows of TV Data & retriving the row number that has a match
    contentTV = [Study,'TV']
    for i, row in TVData.iterrows():
        if any(e in contentTV for e in list(row)):
            contentRow = i
            break
    TVData = TVData.drop(range(0,contentRow))
    TVData.reset_index(drop=True, inplace=True)
    TVData.columns = [str(x).replace(' ', '') for x in TVData.columns]

    if "VisitName" in TVData.columns:
        TVData.rename(columns={'VisitName':'CPEVENT'}, inplace=True)
    if "VISIT" in TVData.columns:
        TVData.rename(columns={'VISIT':'CPEVENT'}, inplace=True)

    TVData = TVData[['CPEVENT']]
    TVData.drop_duplicates(inplace=True)
    TVData.reset_index(drop=True, inplace=True)

    # Remove leading & trailing spaces from CPEVENT
    TVData['CPEVENT'] = TVData['CPEVENT'].str.replace(' ', '').str.upper()
    TVData_Visit = list(TVData['CPEVENT'])

    ###### Reading from DTS -----------------------------------------------------------------
    EGdetails = fileApp[fileApp['Domain'].isin(["EG"])]
    fileEG = list(EGdetails['FileName'])[0]
    EGPath = os.path.join(StudyDir,fileEG)
    nameEG = pd.ExcelFile(EGPath).sheet_names
    # tabDCF = [i for i in nameEG if 'DATACOLLECTIONFORMAT' in i.upper().replace(' ','')][0]
    tabCover = [i for i in nameEG if 'COVER' in i.upper().replace(' ','')][0]
    tabDict = [i for i in nameEG if 'DICTIONARY' in i.upper().replace(' ','')][0]
    tabVisit = [i for i in nameEG if 'VISIT' in i.upper().replace(' ','')][0]
    tabTPT = [i for i in nameEG if 'TIMEPOINT' in i.upper().replace(' ','')][0]

    # Extracting Vendor Name from Cover tab
    Data_1 = pd.read_excel(EGPath, sheet_name=tabCover, keep_default_na=False)
    Data_1 = Data_1.dropna(thresh=2) # Remove empty rows
    Data_1 = Data_1.dropna(thresh=len(Data_1) - 1, axis=1) # Remove empty columns
    Data_1.reset_index(drop=True, inplace=True)
    Data_1.columns = ['Col1','Col2']
    Domain = Data_1.loc[Data_1['Col1'].str.contains('Domain'), 'Col2'].squeeze()
    Vendor = Data_1.loc[Data_1['Col1'].str.contains('Vendor'), 'Col2'].squeeze()
    Vendor = Vendor.upper()

    # Extracting Visit Data from Folder(Visit) tab
    Data_2 = pd.read_excel(EGPath, sheet_name=tabVisit, usecols='A', keep_default_na=False)
    Data_2 = Data_2.dropna()
    Data_2.reset_index(drop=True, inplace=True)
    headRow = []
    for i, row in Data_2.iterrows():
        if 'FOLDERNAME' in str(row[0]).upper() or 'FOLDER NAME' in str(row[0]).upper():
            headRow.append(i)
    # Sometimes there is a FOLDERNAME element with a big description under it. In such case the 1st headRow must be disregarded.
    if len(headRow) > 1:
        for i in range(headRow[0],headRow[1]):
            if len(Data_2.iloc[headRow[0]+1,0]) > 50:
                headRow = headRow[1:]
    Data_2_1 = Data_2.drop(range(0,max(headRow)+1)) # Removing all the rows above & including 'FolderName'
    Data_2_1.drop_duplicates()
    Data_2_1.reset_index(drop=True, inplace=True)
    Data_2_1.columns = ['VisitName']
    Data_2_1['VisitName'] = Data_2_1['VisitName'].str.replace(' ', '').str.upper()
    CPEVENT = list(Data_2_1['VisitName']) # CPEVENT later to be merged with rest of DTS data
        #### Multiple Visit Sets - If there are more than 1 headRow 
    # VisitSets = len(headRow)

    # Extracting Test Data from Dictionary(Code-Decode)
    selectDCD = ['EGCAT','EGTEST','SUBJPOS','EGMETHOD','EGEVAL','EGSTRESC','UNIT','SEX','ND']
    Data_3 = pd.read_excel(EGPath, sheet_name=tabDict, skiprows=list(range(0,5)), usecols = 'A,B', keep_default_na=False)
    Data_3.drop_duplicates()
    Data_3.columns = ['Variable','Value']
    DCD = Data_3[Data_3['Variable'].isin(selectDCD)]
    DCD.reset_index(drop=True, inplace=True)


    RefM = os.path.join(BaseDir,"Reference Metadata_EG.xlsx")
    RefMet = pd.read_excel(RefM, usecols='F,I', keep_default_na=False)
    RefMet.columns = ['Test Name','Assessment']
    RefMet['Assessment'] = RefMet['Assessment'].str.replace('\n', '')
    RefMet['Assessment'] = RefMet['Assessment'].str.strip()
    RefMet['Test Name'] = RefMet['Test Name'].str.replace('\n', '')
    RefMet['Test Name'] = RefMet['Test Name'].str.strip()
    Test = DCD[DCD['Variable'].isin(['EGTEST'])]
    Test.reset_index(drop=True, inplace=True)
    Test.columns = ['Variable','Test Name']
    Test['Test Name'] = Test['Test Name'].str.replace('\n', '')
    Test['Test Name'] = Test['Test Name'].str.strip()
    Test = pd.merge(Test, RefMet, how ='left', on ='Test Name')
    Test.rename(columns={'Test Name':'EGTEST', 'Assessment':'EGCAT'}, inplace=True)

    # Extracting TimePoint Data from Timepoint tab
    Data_4 = pd.read_excel(EGPath, sheet_name=tabTPT, skiprows=list(range(0,5)), usecols = 'A,C', keep_default_na=False)
    Data_4.columns = ['TP_Visit','TPTTXT']
    TPTTXT = list(Data_4['TPTTXT'].unique())

    VisitData = pd.DataFrame()
    VisitData['PROJECT'] = [Study]*Test.shape[0]
    VisitData['EGNAM'] = [Vendor]*Test.shape[0]
    VisitData['EGCAT'] = Test['EGCAT']
    VisitData['EGTEST'] = Test['EGTEST']

    # EGGRPID = list(np.arange(1, len(TPTTXT) + 1))
    EGGRPID = list(np.arange(1, 3 + 1))
    VisitData = pd.concat([VisitData.assign(TPTTXT=i) for i in TPTTXT], ignore_index=True)
    VisitData = pd.concat([VisitData.assign(EGGRPID=i) for i in EGGRPID], ignore_index=True)

    VisitData['CPEVENT'] = [CPEVENT]*VisitData.shape[0]

    ## Add Trial Visit Data
    # Initialize columns for each trial visit
    for Visit in TVData_Visit:
        VisitData[Visit] = 'No'  # Initialize with 'No'

    # Populate 'Yes' or 'No' based on DTS CPEVENT values
    for index, row in VisitData.iterrows():
        for visit in TVData_Visit:
            if visit in row['CPEVENT']:
                VisitData.at[index, visit] = 'Yes'
    VisitData.drop(columns=['CPEVENT'], inplace=True)

    MetaData = DCD.groupby(['Variable'])['Value'].apply(lambda x: list(x)).reset_index()
    MetaData = MetaData.transpose()
    MetaData.columns = MetaData.iloc[0]
    MetaData.reset_index(drop=True, inplace=True)
    MetaData = MetaData.drop(0, axis=0)
    MetaData.reset_index(drop=True, inplace=True)

    # Path to the template onboarding excel
    TempPath = os.path.join(BaseDir,"Templates","STUDY_EG_Metadata_Report_Mapping_file.xlsx")

    with xw.App(visible=False) as app:
        wb = xw.Book(TempPath)
        #saving mapping file template instance
        inputFile = str(Study)+"_EG_Metadata_Report_Mapping_file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        wb.save(InputPath)
        wb.close()

    with xw.App(visible=False) as app:
        inputFile = str(Study)+"_EG_Metadata_Report_Mapping_file_template.xlsx"
        InputPath = os.path.join(StudyDir, inputFile)
        os.chdir(StudyDir)
        MapFile = xw.Book(InputPath)

        Visit = MapFile.sheets['Visit']
        
        Visit.range("A2").options(index=False).value = VisitData['PROJECT']
        Visit.range("B2").options(index=False).value = VisitData['EGNAM']
        Visit.range("C2").options(index=False).value = VisitData['EGCAT']
        Visit.range("D2").options(index=False).value = VisitData['EGTEST']
        Visit.range("E2").options(index=False).value = VisitData['TPTTXT']
        Visit.range("F2").options(index=False).value = VisitData['EGGRPID']
        Visit["G2"].options(pd.DataFrame, header=1, index=False, expand='table').value = VisitData.iloc[:,6:]
        
        Meta = MapFile.sheets['MetaData']

        # EGCAT	EGTEST	EGPOS	EGMETHOD	EGEVAL	EGRESCD	UNIT	SEX	EGSTAT	TPTTXT
        # 'EGCAT', 'EGEVAL', 'EGMETHOD', 'EGSTRESC', 'EGTEST', 'ND', 'SEX', 'SUBJPOS', 'UNIT'
        Meta.range("A1").options(index=False).value = pd.DataFrame({'EGCAT':MetaData.iloc[0]['EGCAT']})
        Meta.range("B1").options(index=False).value = pd.DataFrame({'EGTEST':MetaData.iloc[0]['EGTEST']})
        Meta.range("C1").options(index=False).value = pd.DataFrame({'EGPOS':MetaData.iloc[0]['SUBJPOS']})
        Meta.range("D1").options(index=False).value = pd.DataFrame({'EGMETHOD':MetaData.iloc[0]['EGMETHOD']})
        Meta.range("E1").options(index=False).value = pd.DataFrame({'EGEVAL':MetaData.iloc[0]['EGEVAL']})
        Meta.range("F1").options(index=False).value = pd.DataFrame({'EGRESCD':MetaData.iloc[0]['EGSTRESC']})
        Meta.range("G1").options(index=False).value = pd.DataFrame({'UNIT':MetaData.iloc[0]['UNIT']})
        Meta.range("H1").options(index=False).value = pd.DataFrame({'SEX':MetaData.iloc[0]['SEX']})
        Meta.range("I1").options(index=False).value = pd.DataFrame({'EGSTAT':MetaData.iloc[0]['ND']})
        Meta.range("J1").options(index=False).value = pd.DataFrame({'TPTTXT':TPTTXT})
        
        #saving final file as new file
        inputFile1 = str(Study)+"_EG_Metadata_Report_Mapping_file.xlsx"
        InputPath1 = os.path.join(StudyDir, inputFile1)
        MapFile.save(InputPath1)
        MapFile.close()
    return inputFile1


##creating ui to take input
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Create IDR Mapping File')
        self.setGeometry(100, 100, 400, 200)  # Increased height for the Close button

        layout = QVBoxLayout()

        # Domain Type Input
        self.report_type_input = QComboBox(self)
        self.report_type_input.addItems(['B1 Metadata Consistency', 'QS Metadata Consistency', 'Central Lab Metadata Consistency', 'Actigraphy Metadata', 'EG Metadata'])
        layout.addWidget(QLabel('IDR Report Name:'))
        layout.addWidget(self.report_type_input)

        # Study Name Input
        self.study_name_input = QLineEdit(self)
        self.study_name_input.setPlaceholderText('Enter Study Name')
        layout.addWidget(QLabel('Study Name:'))
        layout.addWidget(self.study_name_input)

        # Progress Bar
        # self.progress_bar = QProgressBar(self)
        # self.progress_bar.setRange(0, 100)
        # layout.addWidget(self.progress_bar)

        # Run Button
        self.run_button = QPushButton('Run Script', self)
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        # Close Button
        self.close_button = QPushButton('Close', self)
        self.close_button.clicked.connect(self.close_application)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
    
    def run_script(self):
        reportName = self.report_type_input.currentText()
        Study = self.study_name_input.text()
        StudyDir = os.path.join(BaseDir,Study)

        # Check if inputs are empty
        if not Study:
            QMessageBox.warning(self, 'Input Error', 'Please fill all fields.')
            return

        # Call the appropriate function based on the domain type
        try:
            if reportName == 'B1 Metadata Consistency':
                output = generateB1Mapping(Study, BaseDir)
            elif reportName == 'QS Metadata Consistency':
                output = generateQSMapping(Study, BaseDir)
            elif reportName == 'Central Lab Metadata Consistency':
                output = generateLBMapping(Study, BaseDir)
            elif reportName == 'Actigraphy Metadata':
                output = generateZWMapping(Study, BaseDir)
            elif reportName == 'EG Metadata':
                output = generateEGMapping(Study, BaseDir)
            else:
                QMessageBox.warning(self, 'Invalid Domain Type', 'Please select a valid domain type.')
                return
            QMessageBox.information(self, 'Success', f'Excel file generated: {output}')
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            last_frame = tb[-1]
            filename = last_frame.filename
            lineno = last_frame.lineno
            code_line = last_frame.line
            error_message = f"An error occurred on line {lineno} in {filename}:\n{code_line}\n{str(e)}"
            QMessageBox.critical(self, 'Error', error_message)
    
    def close_application(self):
        # Close the application
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


 