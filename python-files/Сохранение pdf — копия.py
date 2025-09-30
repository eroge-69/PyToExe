# -*- coding:  utf-8 -*-
#https://forum.ascon.ru/index.php/topic,32760.0.html

import pythoncom, os, time
from win32com.client import Dispatch, gencache

#  Подключим описание интерфейсов API5
kompas6_api5_module = gencache.EnsureModule("{0422828C-F174-495E-AC5D-D31014DBBE87}", 0, 1, 0)
kompas_object = kompas6_api5_module.KompasObject(Dispatch("Kompas.Application.5")._oleobj_.QueryInterface(kompas6_api5_module.KompasObject.CLSID, pythoncom.IID_IDispatch))

#  Подключим описание интерфейсов API7
kompas_api7_module = gencache.EnsureModule("{69AC2981-37C0-4379-84FD-5DD2F3C0A520}", 0, 1, 0)
application = kompas_api7_module.IApplication(Dispatch("Kompas.Application.7")._oleobj_.QueryInterface(kompas_api7_module.IApplication.CLSID, pythoncom.IID_IDispatch))

iConverter = application.Converter (kompas_object.ksSystemPath(5) + "\Pdf2d.dll")

iDocument = application.ActiveDocument

if iDocument:

	if iDocument.DocumentType in (1, 3):
		directory = '%s\pdf %s' %(iDocument.Path, time.strftime("%d.%m.%Y"))

		if not os.path.exists(directory):
			os.makedirs(directory)

		iConverter.Convert (iDocument.PathName, directory + "\\" + iDocument.Name[:-4] + ".pdf", 0, False)
		application.MessageBoxEx("Создан файл\n" + iDocument.Name[:-4] + ".pdf", "Сохранение в *.pdf", 64)
	else:
		application.MessageBoxEx("Активный документ не является чертежом или спецификацией!", "Сохранение в *.pdf", 48)
else:
	application.MessageBoxEx("Нет активного документа!", "Сохранение в *.pdf", 48)



