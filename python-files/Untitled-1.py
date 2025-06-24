import pyodbc
from datetime import datetime, timedelta
import json
import requests
import win32event
import win32api
import sys
import winerror
import time
from tkinter import messagebox
import schedule
import logging
import time

SERVER = 'localhost'
DATABASE = 'jxc'
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;Encrypt=no'

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

mutex = win32event.CreateMutex(None, False, 'my_python_program_mutex')
URL = "https://smart.ilabx.cn/ay230050z/AY220052Z/"
MixingPlantManufactureSaveUrl = 'MixingPlantManufacture/saveData'
MixingPlantOutmasterSaveUrl = 'MixingPlantOutmaster/saveData'
MixingPlantRecipeSaveUrl = 'MixingPlantRecipe/saveData'
MixingPlantTaskSaveUrl = 'MixingPlantTask/saveData'
# 配置日志记录
logging.basicConfig(
    filename='banhezhan.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def post_data(url, data, timeout=5):
    try:
        json_data = json.dumps(data)
    except Exception as e:
        logging.error(f"{url}JSON转换失败,Data:{data},错误信息：{str(e)}")
        return False
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(URL+url, data=json_data, headers=headers, timeout=timeout)
        response.raise_for_status()
        logging.info(f"{url}请求成功")
        return True
    except requests.exceptions.Timeout:
        logging.error(f"{url}请求超时")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"{url}请求失败，错误信息：{str(e)}")
        return False

def calculate_time_difference_in_seconds(time_str1, time_str2):
    # 将字符串解析为 datetime 对象
    time_obj1 = datetime.strptime(time_str1, "%Y-%m-%d %H:%M:%S.%f")
    time_obj2 = datetime.strptime(time_str2, "%Y-%m-%d %H:%M:%S.%f")
    time_difference = time_obj2 - time_obj1
    # 返回时间差的秒数
    return time_difference.total_seconds()


def fetch_as_dict(cursor, query):
    """执行SQL查询并将结果转换为字典列表"""
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]  # 获取列名
    results = []
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))  # 将每行数据与列名配对转换为字典
        results.append(row_dict)
    return results


# 根据日期查询运输单表OutMaster
def query_OutMaster(DeliveryDate):
    sql_query = f"SELECT TOP 1000 * FROM dbo.OutMaster WHERE DeliveryDate > '{DeliveryDate}'"
    OutMaster = fetch_as_dict(cursor, sql_query)
    return OutMaster
# 根据日期查询生产数据表manufacture
def query_manufacture(mDateTime):
    sql_query = f"SELECT TOP 1000 * FROM dbo.manufacture WHERE mDateTime > '{mDateTime}'"
    Manufacture = fetch_as_dict(cursor, sql_query)
    return Manufacture

def query_recipe():
    sql_query = f"SELECT TOP 150 * FROM dbo.recipe "
    Recipe = fetch_as_dict(cursor, sql_query)
    return Recipe

def send_Outmaster(OutMasters):
    for OutMaster in OutMasters:
        try: 
            mixingPlantOutmaster = {
                "orgId": 1709,
                "type": 2,
                "deliveryID": OutMaster['DeliveryID'],
                "deliveryName": OutMaster['DeliveryName'],
                "deliveryDate": OutMaster['DeliveryDate'].strftime("%Y-%m-%d %H:%M:%S"),
                "taskID": OutMaster['TaskID'],
                "orderID": OutMaster['OrderID'],
                "itemNo": OutMaster['ItemNo'],
                "recipeNo": OutMaster['RecipeNo'],
                "quantity": float(OutMaster['Quantity']),
                "itemNo": OutMaster['ItemNo'],  # 单车盘数
                "truckID": OutMaster['TruckID'],
                "shipAdd": OutMaster['ShipAdd'],
                "distance": float(OutMaster['Distance']),
                "employeeID": OutMaster['EmployeeID'],
                "companyName": OutMaster['CompanyName'],
                "projectPart": OutMaster['ProjectPart'],
                "projectCmpy": OutMaster['ProjectCmpy'],
                "stationName": OutMaster['StationName'],
                "planCount": float(OutMaster['PlanCount']),
                "endCount": float(OutMaster['EndCount']),
                "fname": OutMaster['FName'],
                "projectName": OutMaster['ProjectName'],
                "outCount": OutMaster['OutCount'],
                "reserve2": OutMaster['reserve2'],
                "cementID": OutMaster['CementID'],
                "cementName": OutMaster['CementName'],
                "intensityLevel": OutMaster['intensityLevel'],
                "ksd": OutMaster['ksd'],
                "kzd": OutMaster['kzd'],
                "tld": OutMaster['tld'],
                "sljdj": OutMaster['sljdj'],
                "sszdlj": OutMaster['sszdlj'],
                "workMethod": OutMaster['WorkMethod'],
                "dname": OutMaster['dName'],
                "taskName": OutMaster['TaskName'],
                "slurryQuantity": float(OutMaster['SlurryQuantity']),
                "slurryRecipeNo": OutMaster['SlurryRecipeNo'],
                "totalItemNo": OutMaster['TotalItemNo']
            }
        except Exception as e:
            logging.error(f"{OutMaster['DeliveryID']}数据转换失败,错误信息：{str(e)}")
            continue

        if post_data(MixingPlantOutmasterSaveUrl, mixingPlantOutmaster) == False:
            return False
    return True

def send_recipe(Recipes):
    for Recipe in Recipes:
        mixingPlantRecipe = {
            "orgId": 1709,
            "type": 2,
            "recipeID": Recipe['RecipeID'],
            "recipeName": Recipe['RecipeName'],
            "recipeSN1": Recipe['RecipeSN1'],
            "recipeSN2": Recipe['RecipeSN2'],
            "recipeSN3": Recipe['RecipeSN3'],
            "recipeFMH": Recipe['RecipeFMH'],
            "recipeFJJ": Recipe['RecipeFJJ'],
            "recipeKF": Recipe['RecipeKF'],
            "recipeWJJ1": Recipe['RecipeWJJ1'],
            "recipeWJJ2": Recipe['RecipeWJJ2'],
            "recipeDSL": Recipe['RecipeDSL'],
            "recipeZSL": Recipe['RecipeZSL'],
            "recipeXSL": Recipe['RecipeXSL'],
            "recipeSZ": Recipe['RecipeSZ'],
            "recipeSZ1": Recipe['RecipeSZ1'],
            "recipeSHUI": Recipe['RecipeSHUI'],
            "recipeOth1": Recipe['RecipeOth1']
        }
        if post_data(MixingPlantRecipeSaveUrl, mixingPlantRecipe) == False:
            return False
    return True

def send_manufacture(Manufactures):
    for Manufacture in Manufactures:
        mixingPlantManufacture = {
            "orgId": 1709,
            "type": 2,
            "mDateTime": Manufacture['mDateTime'].strftime("%Y-%m-%d %H:%M:%S"),
            "RecipeID": Manufacture['RecipeID'],
            "ItemID": Manufacture['ItemID'],
            "StationID": Manufacture['StationID'],
            "ItemNO": Manufacture['ItemNO'],
            "OperatorID": Manufacture['OperatorID'],
            "DeliveryID": Manufacture['DeliveryID'],
            "RecipeSN1": Manufacture['RecipeSN1'],
            "ActualSN1": Manufacture['ActualSN1'],
            "RecipeSN2": Manufacture['RecipeSN2'],  
            "ActualSN2": Manufacture['ActualSN2'],
            "RecipeSN3": Manufacture['RecipeSN3'],
            "ActualSN3": Manufacture['ActualSN3'],
            "RecipeFMH": Manufacture['RecipeFMH'],
            "ActualFMH": Manufacture['ActualFMH'],
            "RecipeFJJ": Manufacture['RecipeFJJ'],
            "ActualFJJ": Manufacture['ActualFJJ'],
            "RecipeKF": Manufacture['RecipeKF'],
            "ActualKF": Manufacture['ActualKF'],
            "RecipeWJJ1": Manufacture['RecipeWJJ1'],
            "ActualWJJ1": Manufacture['ActualWJJ1'],
            "RecipeWJJ2": Manufacture['RecipeWJJ2'],
            "ActualWJJ2": Manufacture['ActualWJJ2'],
            "RecipeDSL": Manufacture['RecipeDSL'],
            "ActualDSL": Manufacture['ActualDSL'],
            "RecipeZSL": Manufacture['RecipeZSL'],
            "ActualZSL": Manufacture['ActualZSL'],
            "RecipeXSL": Manufacture['RecipeXSL'],
            "ActualXSL": Manufacture['ActualXSL'],
            "RecipeSZ": Manufacture['RecipeSZ'],
            "ActualSZ": Manufacture['ActualSZ'],
            "RecipeSZ1": Manufacture['RecipeSZ1'],
            "ActualSZ1": Manufacture['ActualSZ1'],
            "RecipeSHUI": Manufacture['RecipeSHUI'],
            "ActualSHUI": Manufacture['ActualSHUI'],
            "RecipeOth1": Manufacture['RecipeOth1'],
            "ActualOth1": Manufacture['ActualOth1'],
            "RecipeOth2": Manufacture['RecipeOth2'],
            "ActualOth2": Manufacture['ActualOth2']
        }
        if post_data(MixingPlantManufactureSaveUrl, mixingPlantManufacture) == False:
            return False
    return True
def rtxt():
    with open(r'D:\awsa\MixingPlant\datetime.txt', 'r') as file:
        content = file.read()
        datetime = str(content)
        return datetime


def wtxt(datetiem):
    with open(r'D:\awsa\MixingPlant\datetime.txt', 'w') as file:
        file.write(datetiem)
# 主业务
def main():
    logging.info('start service ...') 
    BuildTime = rtxt()
    OutMaster = query_OutMaster(BuildTime)  # 查询运输单
    manufacture = query_manufacture(BuildTime)
    wtxt(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        if send_Outmaster(OutMaster)==False:
            logging.error('请求错误，稍后再试')
            wtxt(BuildTime)
            return 
    except Exception as e:
        logging.error(f"BuildTime={BuildTime},send_Outmaster错误{e}")
    try:
        send_manufacture(manufacture)
        # send_recipe(query_recipe())
    except Exception as e:
        logging.error(f"BuildTime={BuildTime},send_manufacture错误{e}")
    logging.info('end service ...')


if __name__ == '__main__':
    mutex = win32event.CreateMutex(None, False, 'Mixingplant')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        cursor.close()
        conn.close()
        messagebox.showinfo("程序通知", "程序正在运行,不要重复启动")
        sys.exit(0)
    main()
    schedule.every(5).minutes.do(main)

    while True:
        # 运行所有可以运行的任务
        schedule.run_pending()
        time.sleep(1)
