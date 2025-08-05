#定义一类使用属性存储全局变量
# 1. 串口名称
# 2. 设备型号
# 3. 界面的索引
# 4. 串口通信类
# 5. 设备通信类
# 6. 设备状态信息
# 7. 设备参数信息


import os
from typing import List
from entities.deviceModel import PRODUCT_MODEL_ALIAS, ProductModel
from helpers.commom_helper import resource_path
from models.app_setting_model import AppSetting
from models.paramConfigModel import ParamConfigModel
from models.param_model import ParamItemModel
from models.record_model import GasType
from protocols.bz100_protocol.paramConfig import CommonParam
from protocols.bz100_protocol.sensorParam import ChannelParam
from utils.jsonFile_util import JsonSerializer
from PyQt5.QtCore import QObject, pyqtSignal,QTranslator

from enum import Enum

from enum import Enum

from utils.serialUtils.modbusRtu_util import ModbusDataConverter
from utils.serialUtils.serial_util import ComportDeviceInfo

app_setting_filename: str = resource_path(["settings", "app_setting.json"])


class Language(Enum):
    Chinese = 0x00
    English = 0x02
    Russian = 0x03


# 定义 LanguageItemModel 类
class LanguageItemModel:
    def __init__(self):
        super().__init__()
        self.language = None
        self.display_name = ""
        self.icon_name = ""


class AppSettings:
    Title = "便携式探测器参数管理工具"  # Assuming GetResourceString() returns the string directly
    LogoPath = "Resources/Images/Hanwei.png"
    FactoryWebsite = "https://www.hanwei.cn"
    Copyright = "Copyright©2023汉威科技集团股份有限公司"  # Assuming GetResourceString() returns the string directly
 
class DeviceInfor:
   def __init__(self):
       self.product_model = ParamItemModel("product_model", "产品型号", "")
       self.software_version = ParamItemModel("software_version", "软件版本", "")
       self.hardware_version = ParamItemModel("hardware_version", "硬件版本", "")
       self.host_production_date = ParamItemModel("host_production_date", "设备出厂日期", "")   



AvalableSelectedProductModels=[
        ProductModel.__,
        ProductModel.BZ100,
        ProductModel.BX171,
        ProductModel.E110,
        ProductModel.E410,
        # ProductModel.E410P,
        # ProductModel.E410_D,
        # ProductModel.E410P_D,
        ProductModel.E1000,
        # ProductModel.BX170,
        # ProductModel.BX172,
        ProductModel.BX176,
        ProductModel.BX616,
        ProductModel.E4000,
        ProductModel.E6000
 ]
    #  BZ100 = 0x0001
    #  BX171 = 0x0041 
    #  E110 = 0x0030
    #  E410 = 0x0031
    #  E410P = 0x0032
    #  E410_D= 0x0033
    #  E410P_D = 0x0034

    #  E1000 = 0x0010
    #  BX170 = 0x0042  
    #  BX172 = 0x0043 
    #  BX176 = 0x0044 

    #  BX616= 0x0045
    #  E4000= 0x0047
    #  E6000 = 0x0012       
        

class GlobalManager(QObject):
    
    _port_name:str
    _current_index:int
    _serial_util:object
    _device_communicator:object
    _device_status_info:object
    _device_param_info:object
    gasType_dic:dict[int,GasType]={}

    deviceInfor=DeviceInfor()
    paramConfigModel=ParamConfigModel()
    language_changed_signal = pyqtSignal()

    avalable_channel_num=ParamItemModel[list[int]]("available_channel_num", "可用通道数",[1,2,3,4])

    #获取ProductModel所有枚举成员
    avalable_products_model=ParamItemModel[list(ProductModel)]("avalable_productModel","可用产品型号",AvalableSelectedProductModels)
    device_model_display_name=ParamItemModel[str]("device_model_display_name","设备型号",None)
  
    def __init__(self):
        super().__init__()
        self.port_name = None
        self.port_name_Model=ParamItemModel[ComportDeviceInfo]("port_name","串口名称",None)
        self.device_model_itemModel=ParamItemModel[ProductModel]("device_model_itemModel","设备型号",ProductModel.__,lambda name,vlue:self.device_model_changed(vlue))

        self.device_picture_path_model=ParamItemModel[str]("device_picture_path","设备图片路径",None)
        # self.port_name_Model.on_param_value_changed_signal.connect(lambda name,obj:setattr(self,name,obj))
        self.language_items = [
            LanguageItemModel(),
            LanguageItemModel(),
            LanguageItemModel(),
        ]     
        self.language = Language.Chinese
        self.sub_module_index=0
        self.module_index = 0
        self.serial_util = None
        self.device_communicator = None
        self.device_status_info = None
        self.device_param_info = None
        self.device_infor = DeviceInfor()
        self.appSetting=AppSetting()
    def device_model_changed(self,model:ProductModel):
         file_name= resource_path(["resources","images",f"{model.name}.png"])
         self.device_picture_path_model.value=file_name
         self.device_model_display_name.value=PRODUCT_MODEL_ALIAS[ model] 
     

        
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GlobalManager, cls).__new__(cls)
        return cls.instance
    
   
    @property
    def device_model(self):
        return self.device_model_itemModel.value
    @device_model.setter
    def device_model(self,new_value):
        self.device_model_itemModel.value=new_value


    @property
    def port_name(self):
        if self.port_name_Model.value is None: return None
        return self.port_name_Model.value.device if self.port_name_Model.value else None
       

    @port_name.setter
    def port_name(self, value):
        self._port_name = value
    @property
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, value):
        self._current_index = value

    @property
    def serial_util(self):
        return self._serial_util

    @serial_util.setter
    def serial_util(self, value):
        self._serial_util = value

    @property
    def device_communicator(self):
        return self._device_communicator

    @device_communicator.setter
    def device_communicator(self, value):
        self._device_communicator = value

    @property
    def device_status_info(self):
        return self._device_status_info

    @device_status_info.setter
    def device_status_info(self, value):
        self._device_status_info = value

    @property
    def device_param_info(self):
        return self._device_param_info

    @device_param_info.setter
    def device_param_info(self, value):
        self._device_param_info = value

    def clear(self):
        self._port_name = None
        self._device_model = None
        self._current_index = 0
        self._serial_util = None
        self._device_communicator = None
        self._device_status_info = None
        self._device_param_info = None