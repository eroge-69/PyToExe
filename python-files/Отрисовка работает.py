from pythoncom import connect, VT_EMPTY
from win32com.client import gencache, VARIANT
import os
import time

# Инициализация констант и API
con0 = gencache.EnsureModule('{75C9F5D0-B5B8-4526-8681-9903C567D2ED}', 0, 1, 0).constants  # kompas6_constants
con3 = gencache.EnsureModule('{2CAF168C-7961-4B90-9DA2-701419BEEFE3}', 0, 1, 0).constants  # kompas6_constants_3d
API5 = gencache.EnsureModule('{0422828C-F174-495E-AC5D-D31014DBBE87}', 0, 1, 0)  # kompas6_api5_module
API7 = gencache.EnsureModule('{69AC2981-37C0-4379-84FD-5DD2F3C0A520}', 0, 1, 0)  # kompas_api7_module

class Kompas3DHelper:
    def __init__(self):
        self.kompas = None
        self.application = None
        self.connect_to_kompas()

    def connect_to_kompas(self):
        """Подключение к Компас-3D"""
        try:
            self.kompas = API5.KompasObject(connect('Kompas.Application.5'))
            self.application = self.kompas.ksGetApplication7()
            print("✓ Успешное подключение к Компас-3D")
            return True
        except Exception as e:
            print(f"✗ Ошибка подключения к Компас-3D: {e}")
            return False

    def get_active_document_path(self):
        """Получает путь к активному документу"""
        try:
            active_doc = self.application.ActiveDocument
            if active_doc:
                return active_doc.PathName
            return None
        except Exception as e:
            print(f"✗ Ошибка получения пути активного документа: {e}")
            return None

    def get_active_document_directory(self):
        """Получает директорию активного документа"""
        try:
            active_doc_path = self.get_active_document_path()
            if active_doc_path and os.path.exists(active_doc_path):
                return os.path.dirname(active_doc_path)
            return None
        except Exception as e:
            print(f"✗ Ошибка получения директории активного документа: {e}")
            return None

    def edit_accuracy_model_displaying(self, file_path, accuracy_level=10):
        """
        Изменение точности отрисовки модели с принудительным применением настроек
        """
        if not os.path.exists(file_path):
            print(f"✗ Файл не найден: {file_path}")
            return False

        try:
            documents = self.application.Documents
            was_opened = False
            kompas_doc = None

            # Проверяем, открыт ли уже документ
            for i in range(documents.Count):
                try:
                    doc = documents.Item(i)
                    if doc and hasattr(doc, 'PathName') and doc.PathName:
                        if doc.PathName.lower() == file_path.lower():
                            kompas_doc = doc
                            was_opened = True
                            break
                except:
                    continue

            # Если документ не открыт, открываем его
            if not kompas_doc:
                try:
                    kompas_doc = documents.Open(file_path, True, False)
                    was_opened = False
                    time.sleep(1)
                    print(f"✓ Файл открыт: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"✗ Ошибка открытия файла {os.path.basename(file_path)}: {e}")
                    return False

            if not kompas_doc:
                print(f"✗ Не удалось открыть документ: {os.path.basename(file_path)}")
                return False

            # Получаем и изменяем настройки документа
            try:
                doc_settings = kompas_doc.DocumentSettings
                doc_3d_settings = API7.IDocument3DSettings(doc_settings)

                # Текущее и новое значение точности
                current_accuracy = doc_3d_settings.AccuracyModelDisplaying
                doc_3d_settings.AccuracyModelDisplaying = accuracy_level
                new_accuracy = doc_3d_settings.AccuracyModelDisplaying

                print(f"  Точность: {current_accuracy} → {new_accuracy}")

                # Сохраняем изменения
                kompas_doc.Save()
                print("  ✓ Изменения сохранены")

                # Для применения настроек закрываем и открываем заново
                if not was_opened:
                    kompas_doc.Close(1)
                    time.sleep(0.3)
                    # Открываем и сразу закрываем для применения настроек
                    reopened_doc = documents.Open(file_path, False, False)
                    time.sleep(0.3)
                    reopened_doc.Save()
                    reopened_doc.Close(1)
                else:
                    # Если документ был открыт, просто сохраняем
                    kompas_doc.Save()

                print("  ✓ Настройки применены!")
                return True

            except Exception as e:
                print(f"✗ Ошибка при работе с настройками: {e}")
                return False

        except Exception as e:
            print(f"✗ Общая ошибка: {e}")
            return False

    def process_multiple_files(self, folder_path, file_extensions=(".m3d", ".a3d"), accuracy_level=10, recursive=False):
        """
        Пакетная обработка всех файлов в папке
        """
        if not os.path.exists(folder_path):
            print(f"✗ Папка не найдена: {folder_path}")
            return False

        processed_count = 0
        error_count = 0

        print(f"📁 Обработка папки: {folder_path}")
        print(f"📄 Расширения: {', '.join(file_extensions)}")
        print(f"🎯 Точность: {accuracy_level}")
        print("-" * 60)

        file_list = []

        # Собираем список файлов для обработки
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if any(file_name.lower().endswith(ext.lower()) for ext in file_extensions):
                        file_path = os.path.join(root, file_name)
                        file_list.append(file_path)
        else:
            for file_name in os.listdir(folder_path):
                if any(file_name.lower().endswith(ext.lower()) for ext in file_extensions):
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        file_list.append(file_path)

        # Сортируем файлы для удобства
        file_list.sort()

        # Обрабатываем файлы
        for file_path in file_list:
            print(f"🔧 Обрабатываем: {os.path.basename(file_path)}")

            if self.edit_accuracy_model_displaying(file_path, accuracy_level):
                processed_count += 1
            else:
                error_count += 1

            # Небольшая пауза между файлами
            time.sleep(0.3)
            print()

        # Итоговая статистика
        print("=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
        print(f"   ✅ Успешно: {processed_count} файлов")
        print(f"   ❌ Ошибки: {error_count} файлов")
        print(f"   📋 Всего: {len(file_list)} файлов")

        if processed_count > 0:
            print("\n💡 Для полного применения настроек рекомендуется:")
            print("   - Перезагрузить Компас-3D")
            print("   - Или переоткрыть документы")

        return processed_count > 0

def main():
    print("=" * 60)
    print("🎯 КОМПАС-3D - УЛУЧШЕНИЕ ГРАФИКИ")
    print("=" * 60)

    # Создаем экземпляр помощника
    kompas_helper = Kompas3DHelper()

    if not kompas_helper.application:
        print("✗ Не удалось подключиться к Компас-3D")
        print("   Убедитесь, что Компас-3D запущен")
        return

    # Получаем путь к директории активного документа
    active_directory = kompas_helper.get_active_document_directory()

    if not active_directory:
        print("✗ Не удалось определить директорию активного документа")
        print("   Убедитесь, что документ открыт в Компас-3D и сохранен")
        return

    print(f"📂 Директория активного документа: {active_directory}")
    print()

    # Пакетная обработка файлов в папке активного документа
    success = kompas_helper.process_multiple_files(
        active_directory,
        file_extensions=(".m3d", ".a3d"),
        accuracy_level=10,
        recursive=True
    )

    if success:
        print("\n🎉 Обработка завершена успешно!")
    else:
        print("\n⚠️  Обработка завершена с ошибками")

if __name__ == "__main__":
    main()