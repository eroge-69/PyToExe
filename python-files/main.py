import os 
import re 
import pandas as pd 

def extract_names(text):
    return re.findall(r'\\b[A-Z])[a-z]*\\b',text)
    
    def 
    extract_names_from_files_and_write_to_excel(directory,excel_path):
        all_names = []
        for filename in
        os.listdir(directory):
            with
            open(os.path.join(directory,filename),'r') as file:
                text=
                file.read()
                names=
                extract_names(text)
                for name
                in names:
                    all_names.append({'filename':filename,'name':})
                    df=pd.dataframe(all_names)
                    df.to_excel(excel_path,index=False)
                    return df