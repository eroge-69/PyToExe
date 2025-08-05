
from utils.logger_manager import LoggerManager

logger = LoggerManager.CreatLogger('BZ100PortableDetectorParamConfigTool')
import asyncio
import logging
import multiprocessing
import os
from qasync import QEventLoop
from models.language_model import LanguageEnum
import sys
from helpers.commom_helper import resource_path, switch_language
from PyQt5.QtCore import QSettings,QTranslator
from PyQt5.QtGui import QFont
from typing import Optional, TypeVar
from globalManager import GlobalManager
from models.paramConfigModel import ParamConfigModel
from mvvmFrameWork.AppBoot import ApplicationBase
from punq import Container, Scope
from widgets.busyingStateView_widget import StatusInfoViewModel
from widgets.notification import Notifier
from widgets.paginatedTableView_widget import PaginatedTableViewModel
from resources import icons_rc

IS_SINGLE_MODE = False

class App(ApplicationBase):
    translator = QTranslator()
    globalManager=GlobalManager()

    def __init__(self):
     super(ApplicationBase,self).__init__(sys.argv)
     self.loop=QEventLoop(self)#
     asyncio.set_event_loop(self.loop)  # 设置asyncio使用QEventLoop作为事件循环 
     self.init_language() 
     self.container = Container()      
    
    def init_language(self):
        try:        
          se= self.globalManager.appSetting.load()
          self.language:LanguageEnum=LanguageEnum( se.language)
          logger.info(f"3333333{self.language}")               
        except Exception  as e:
            logger.error(f"2222222{e}")
            self.language=LanguageEnum.CN
        if self.language:
            switch_language(self.translator, self.language)       

    def get_style_sheet(self):     
        return self. getsheet1()

    def restart_application(self):
        """重启应用程序lidergd"""
        # 关闭当前应用程序
        self.quit()
        #线程延迟1秒           
        # 重新启动应用程序
        python = sys.executable
        os.execl(python, python, *sys.argv)
    def init(self):
       self. init_language()
   
    def getsheet1(self):
        stylesheets_path = resource_path(["resources", "styles", "Ubuntu.qss"])
        with open(stylesheets_path, 'r') as file:
            qss_content= file.read()       
            return qss_content
    def start(self):
        from protocols.bz100_protocol.bz100Communicator import Bz100Communicator
        from protocols.e1000Communicator import E1000Communicator
        from viewModels.mainWindow_viewModel import MainWindowViewModel
        from viewModels.recordManagement_bx17x_viewModel import RecordManagementViewModel
        from views.recordManagement_bx17x_view import RecordManagementView
        from protocols.bx616Communicator import BX616Communicator
        from viewModels.parameterManagement_viewModel import ParamManagementViewModel
        from viewModels import deviceInfo_viewModel, firwareUpdateDialog_viewModel, recordManagement_bx616_viewModel, firwareUpdateDialog_viewModel
        from viewModels import recordManagement_bz100_viewModel
        from views import recordManagement_bx616_view, recordManagement_bz100_view, deviceInfo_view, firwareUpdateDialog_view
        from views.mainWindow_view import MainWindowView
        from views.parameterManagement_view import ParamConfigView
        from views.aboutDialog_view import AboutDialogView

        def register_service( container:  Container):
            app_settings = QSettings("Hanwei", "BZ100PortableDetectorParamConfigTool")
            self.container.register(QSettings, instance=app_settings, scope=Scope.singleton)
        
            # logging.RootLogger.root = logger
            self.container.register(Container, instance=self.container)
            self.container.register(GlobalManager,instance=self.globalManager, scope=Scope.singleton)
            self.container.register(StatusInfoViewModel, scope=Scope.singleton)
            self.container.register(logging.Logger, instance=logger)
            self.container.register(укаепрCommunicator)
            self.container.register(паваCommunicator)
            self.container.register(BннннCommunicator)
            self.container.register(PaginatedTableViewModel)
            # вввв
            self.container.register(RecordManagementViewModel)
            self.container.register(RecordManagementView)
            # аааа
            self.container.register(recordManagement_bx616_viewModel.RecordManagementViewModel)
            self.container.register(recordManagement_bx616_view.RecordManagementView)
            # гггггг
            self.container.register(recordManagement_bz100_viewModel.RecordManagementViewModel)
            self.container.register(recordManagement_bz100_view.RecordManagementView)

            self.container.register(ParamManagementViewModel)
            self.container.register(ParamConfigView)

            self.container.register(deviceInfo_viewModel.DeviceInfoViewModel)
            self.container.register(deviceInfo_view.DeviceInfoView)

            self.container.register(MainWindowViewModel)
            self.container.register(MainWindowView)

            # region 对话框
            self.container.register(firwareUpdateDialog_viewModel.FirmwareUpdateViewModel)
            self.container.register(firwareUpdateDialog_view.FirwareUpdateDialogView)
            self.container.register(ParamConfigModel, scope=Scope.singleton)
            self.container.register(Notifier, scope=Scope.singleton)
            self.container.register(QTranslator,instance=self.translator,scope=Scope.singleton)
            self.container.register(AboutDialogView, scope=Scope.singleton)
        def create_shell():
            try:        
                main: MainWindowView = self.container.resolve(MainWindowView)  # type: ignore
                main.add_Views(self.container.resolve(ParamConfigView))  # type: ignore
                main.add_Views(self.container.resolve(recordManagement_bz100_view.RecordManagementView))  # type: ignore
                main.add_Views(self.container.resolve(RecordManagementView))  # type: ignore
                main.add_Views(self.container.resolve(recordManagement_bx616_view.RecordManagementView))  # type: ignore
                main.add_Views(self.container.resolve(deviceInfo_view.DeviceInfoView))  # type: ignore
                return main
            except Exception as e:
                # 记录异常日志
                print(f"Error resolving MainWindowViewModel: {e}")
                raise e    
    
        style= self.get_style_sheet()
        if  style:
            self.setStyleSheet(style)

        register_service(self.container) 
        main = create_shell()     
        main.show()     
        with self.loop:
            return self.loop.run_forever() 
def checkSingelProcess():
    if os.path.exists(lock_file):
        print("程序已经在运行")
        return True
    else:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return False
def main():
    try:
        multiprocessing.freeze_support()   # 必须添加 
        app = App()
        app.setFont(QFont("Segoe UI", 9))  # 支持多语言的现代字体
        # 获取当前主窗体实例
        app.start()            
    except Exception as e:
        logger.error(f"Application start error: {e}", exc_info=True)
    finally:
        # 删除锁文件
        if os.path.exists(lock_file):
            os.remove(lock_file)
if __name__ == "__main__":
    lock_file = 'file.lock'
    try:
        if IS_SINGLE_MODE:
            if checkSingelProcess():
                sys.exit(0)
        else:
            main()
    except Exception as e:
        logger.error(f"Application start error: {e}", exc_info=True)
        sys.exit(0)