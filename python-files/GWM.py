print("Running...")

import pandas as pd
# import pandasgui as pdg
import os
import sys

# Get path to folder containing the executable or script
if getattr(sys, 'frozen', False):
    # Running as an executable
    base_path = os.path.dirname(sys.executable)
else:
    # Running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

Configs_Path = os.path.join(base_path, 'Configs.xlsx')
Configs = pd.read_excel(Configs_Path, sheet_name=None)
Base_Commisssion = Configs["Base_Commission"]
Base_Incentive = Configs["Base_Incentive"]
Sale_Deduction = Configs["Sale_Deduction"]
Other = Configs["Other"]

Data_Path = os.path.join(base_path, "Raw_Data.xlsx")
df = pd.read_excel(Data_Path)
i = col_index = df.columns.get_loc('IAM')
df['มูลค่าส่วนลดของแถม'] = df['มูลค่าส่วนลดของแถม'].fillna(0)
df.iloc[:, 11:] = df.iloc[:, 11:].fillna(0)
df = df.sort_values(by="IAM")

# Certified
certified_rows = df[df['Certified'] == 'Yes']
df = df[df['Certified'] != 'Yes']

# ยอดขาย
counts = df["IAM"].value_counts()
df.insert(i+1, "ยอดขาย", df["IAM"].map(counts))
df["ยอดขาย"] = df.duplicated(subset="IAM").apply(lambda x: None if x else True) * df["ยอดขาย"]

# ค่าคอม
if (len(df.index) > Other.loc[Other['Key'] == "เป้า 100%", 'Value'].values[0]):
    Achive100 = True
    Base_Commission_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['Comm 100%']))
    GSPO_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['GSPO 100%']))
    Fleet_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['Fleet 100%']))
else :
    Achive100 = False
    Base_Commission_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['Comm 1-99%']))
    GSPO_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['GSPO 1-99%']))
    Fleet_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['Fleet 1-99%']))

Part_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['จอง/ส่งมอบ']))
Fleet_Part_Dict = dict(zip(Base_Commisssion['Model'], Base_Commisssion['Fleet จอง/ส่งมอบ']))

def select_dict(row):
    if row["Fleet"] == "Yes":
        if row["จอง"] == "Yes" and row["ส่ง"] == "Yes":
            return Fleet_Dict
        else :
            return Fleet_Part_Dict
    elif row["GSPO"] == "Yes":
        return GSPO_Dict
    elif row["จอง"] == "Yes" and row["ส่ง"] == "Yes":
        return Base_Commission_Dict
    else:
        return Part_Dict
    
def get_commission(row):
    commission_map = select_dict(row)
    model = row["รุ่นรถ"]
    return commission_map.get(model, 0)

    
df.insert(12,"ค่าคอม",0)
df["ค่าคอม"] = df.apply(get_commission, axis=1)


# ตำแหน่งอื่น
def incentive100(row):
    if Achive100:
        if row["GSPO"] != "Yes" and row["Fleet"] != "Yes":
            return Base_Incentive["Incentive 100%"]
        return 0

df.insert(i+7,"100%", 0)
df["100%"] = df.apply(incentive100, axis=1)
incentive_col = list(Base_Incentive.columns)
incentive_col.remove("Incentive 100%")
for idx, col_name in enumerate(incentive_col):
    df.insert(i + 7 + idx, col_name, Base_Incentive[col_name].values[0])

# หักค่าคอม
def com_deduct_match(sale_value):
    row = Sale_Deduction[
        (Sale_Deduction["Sale_From"] <= sale_value) & 
        (sale_value <= Sale_Deduction["Sale_To"])
    ]
    return {
        "IAM": row["IAM"].values[0],
        "Manager_Sales": row["ผจก ขาย"].values[0],
        "Manager_General": row["ผจก ทั่วไป"].values[0],
    }

def deduct(row):
    Deduct_Dict = com_deduct_match(row["มูลค่าส่วนลดของแถม"])
    row["หักค่าคอม"] = Deduct_Dict["IAM"]
    row["ผจก ขาย"] -= Deduct_Dict["Manager_Sales"]
    row["ผจก ทั่วไป"] -= Deduct_Dict["Manager_General"]
    return row

df.insert(i+4, "หักค่าคอม", 0)
df = df.apply(deduct, axis=1)

# Post Processing
df.insert(i+5, "ค่าคอมหลังหัก", df["ค่าคอม"]-df["หักค่าคอม"])
df.insert(i+9, "รวม", 0)
df["รวม"] = df.iloc[:, i+5:i+9].sum(axis=1)


df.insert(i+10, "รวมทั้งสิ้น", 0)
df["รวมทั้งสิ้น"] = df.groupby('IAM')['รวม'].transform('sum')
df["รวมทั้งสิ้น"] = df.duplicated(subset="IAM").apply(lambda x: None if x else True) * df["รวมทั้งสิ้น"]

df["IAM"] = df.duplicated(subset="IAM").apply(lambda x: None if x else True) * df["IAM"]

df = pd.concat([df, certified_rows], ignore_index=True)

output_file = os.path.join(base_path, "output.xlsx")
# downloads_path = Path.home() / "Downloads"
# output_file = downloads_path / "output.xlsx"

df.to_excel(output_file, index=False)
print("Finished")
# pdg.show(df)

