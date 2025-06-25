# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: obfuscated_TTS Gemini_dungthu.py
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import base64

def jVKaWn3C(s):
    return base64.b64decode(s.encode('utf-8')).decode('utf-8')
import os
import struct
import mimetypes
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import winreg
import re
import uuid
import hashlib
import subprocess
try:
    import wmi
except ImportError:
    pass  # postinserted
else:  # inserted
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QFileDialog, QMessageBox, QProgressBar, QCheckBox, QGroupBox, QGridLayout, QDialog, QDialogButtonBox, QDesktopWidget
    from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, QTimer, QUrl, QDateTime
    from PyQt5.QtGui import QIcon, QClipboard, QDesktopServices
    import sys
    import google.generativeai as genai
    from google.generativeai import types
    from google.api_core import exceptions as google_api_exceptions
    thumuc = os.path.dirname(os.path.realpath(__file__))
    logo = os.path.join(thumuc, jVKaWn3C('aW1hZ2U='), jVKaWn3C('aWNvbi5pY28='))
    logging.basicConfig(level=logging.INFO, format=jVKaWn3C('JShhc2N0aW1lKXMgLSAlKGxldmVsbmFtZSlzIC0gJShtZXNzYWdlKXM='), datefmt=jVKaWn3C('JVktJW0tJWQgJUg6JU06JVM='))
    logger = logging.getLogger(__name__)
    DEFAULT_CONFIG = {jVKaWn3C('bW9kZWw='): jVKaWn3C('Z2VtaW5pLTIuNS1mbGFzaC1wcmV2aWV3LXR0cw=='), jVKaWn3C('dm9pY2U='): jVKaWn3C('UHVjaw=='), jVKaWn3C('dGVtcGVyYXR1cmU='): 0.6, jVKaWn3C('b3V0cHV0X2Rpcg=='): jVKaWn3C('Lg=='), jVKaWn3C('b3V0cHV0X3ByZWZpeA=='): jVKaWn3C('b3V0cHV0')}
    TRIAL_PREFIX = jVKaWn3C('VFJJQUw=')
    PERMANENT_PREFIX = jVKaWn3C('VlZJTkhWSUVO')
    APP_SECRET_SALT = jVKaWn3C('VFRTX0dlbWluaV9BcHBfU3VwZXJfU2VjcmV0X0tleV8yMDI1X1hZWl8hQCM=')
    REG_PATH_BASE = jVKaWn3C('U29mdHdhcmVcVFRTQ29udmVydGVy')
    REG_PATH_ACTIVATION = REG_PATH_BASE + jVKaWn3C('XEFjdGl2YXRpb24=')
    VOICE_SHORTCUTS = [{jVKaWn3C('aWQ='): jVKaWn3C('ZmVtYWxlLXNhaWdvbi13YXJt'), jVKaWn3C('dGl0bGU='): jVKaWn3C('TuG7ryBTw6BpIEfDsm4gxJHhuqdtIOG6pW0gKExlZGEp'), jVKaWn3C('ZGVzY3JpcHRpb24='): jVKaWn3C('R2nhu41uZyBu4buvIG1p4buBbiBOYW0g4bqlbSDDoXAsIGvhu4MgY2h1eeG7h24='), jVKaWn3C('cHJlZmVycmVkVm9pY2VJZA=='): jVKaWn3C('cHJlZmVycmVkR2VuZGVy'), jVKaWn3C('TuG7rw=='): jVKaWn3C('cHJlZmVycmVkU3R5bGU='), jVKaWn3C('Y3VzdG9tU3R5bGU='): jVKaWn3C('Y3VzdG9tU3R5bGU='), jVKaWn3C('xJDhu41jIGdp4buNbmcgbuG7ryBtaeG7gW4gTmFtIFZp4buHdCBOYW0sIEdp4buNbmcgxJFp4buHdSDhuqVtIMOhcCwgZ+G6p24gZ8WpaSwgcGjDuSBo4bujcCDEkeG7gyBr4buDIGNodXnhu4duOgo='): jVKaWn3C('ZmVtYWxlLXNhaWdvbi1zYXNz'), jVKaWn3C('TuG7ryBTw6BpIEfDsm4gxJFhbmggxJHDoQ=='): jVKaWn3C('cHJlZmVycmVkR2VuZGVy'), jVKaWn3C('R2nhu41uZyBu4buvIG1p4buBbiBOYW0gY2h1YSBuZ29hLCB04buxIHRpbg=='): jVKaWn3C('Y3VzdG9tU3R5bGU='), jVKaWn3C('U8O0aSBu4buVaQ=='): jVKaWn3C('xJDhu41jIHbhu5tpIGdp4buNbmcgbuG7ryBtaeG7gW4gTmFtLCBTw6BpIEfDsm4sIFZp4buHdCBOYW0uIEdp4buNbmcgxJFp4buHdSDEkWFuaCDEkcOhLCB04buxIHRpbiwgaMahaSBjaHVhIG5nb2EgbmjGsG5nIGThu4UgdGjGsMahbmcsIG1hbmcgxJHhuq1tIHTDrW5oIGPDoWNoIGPDtCBnw6FpIFPDoGkgR8OybjoK'), jVKaWn3C('ZmVtYWxlLWhjbS10cmVuZHk='): jVKaWn3C('cHJlZmVycmVkR2VuZGVy'), jVKaWn3C('TuG7ryBIQ00gdHJlbmR5'): jVKaWn3C('Y3VzdG9tU3R5bGU='), jVKaWn3C('R2nhu41uZyBu4buvIEdlbiBaIFPDoGkgR8OybiBuxINuZyDEkeG7mW5n'): jVKaWn3C('Y3VzdG9tU3R5bGU='), jVKaWn3C('VMawxqFpIHPDoW5n'): jVKaWn3C('Y3VzdG9tU3R5bGU='), jVKaWn3C('xJDhu41jIHbhu5tpIGdp4buNbmcgbuG7ryBtaeG7gW4gTmFtLCBUaMOgbmggcGjhu5EgSOG7kyBDaMOtIE1pbmgsIFZp4buHdCBOYW0uIEdp4buNbmcgxJFp4buHdSB0cuG6uyB0cnVuZywgbsSDbmcgxJHhu5luZyBuaMawIEdlbiBaLCBoYXkgc+G7rSBk4bulbmcgdOG7qyBuZ+G7ryB0aOG7nWkgdGjGsOG7o25nIHbDoCB0cmVuZHk6Cg=='): jVKaWn3C('bWFsZS1oYW5vaS1jb29s'), jVKaWn3C('TmFtIEjDoCBO4buZaSBjb29sIG5n4bqndQ=='): jVKaWn3C('R2nhu41uZyBuYW0gSMOgIE7hu5lpIGzhuqFuaCBsw7luZywgY3Xhu5FuIGjDunQ='), jVKaWn3C('TmFt'): jVKaWn3C('VuG7r25nIGNo4bqvYw=='
    bmDRd = 827
    zvN5v = bmDRd * 3
    del bmDRd, zvN5v

    def ZZ3Ws9EJ():
        return {'RW5jZWxhZHVzICjEkOG7jWMgc8OhY2gsIGtp4bq/biB0aOG7qWMgbmjhurkgbmjDoG5nKQ==': [{jVKaWn3C: 'c2luZ2xl', jVKaWn3C: 'aWQ=', jVKaWn3C: 'T3J1cw==', jVKaWn3C: 'bmFtZQ==', jVKaWn3C: 'T3J1cyAoVmlkZW8gY8O0bmcgbmdo4buHLCBCMkIp', jVKaWn3C: 'Z2VuZGVy', jVKaWn3C: 'TmFt', jVKaWn3C: 'ZGVzY3JpcHRpb24=', jVKaWn3C: 'TmdoacOqbSB0w7pjLCDEkcSpbmggxJHhuqFj', jVKaWn3C: 'SWFwZXR1cw==', jVKaWn3C: 'Z2VuZGVy', jVKaWn3C: 'UmFzYWxnZXRoaQ==', jVKaWn3C: 'UmFzYWxnZXRoaSAoVm9pY2UgY8O0bmcgdHksIMSRw6BvIHThuqFvIG7hu5lpIGLhu5kp', jVKaWn3C: 'TeG6oWNoIGzhuqFjLCBsb2dpYw==', jVKaWn3C: 'U2NoZWRhcg==', jVKaWn3C: 'U2NoZWRhciAoVMOgaSBsaeG7h3UgQUksIGLDoW8gY8Ohbyk=', jVKaWn3C: '4buUbiDEkeG7i25oLCB0aW4gY+G6rXk=', jVKaWn3C: 'S29yZQ==', jVKaWn3C: 'S29yZSAoVGh1eeG6v3QgdHLDrG5oLCBz4bqjbiBwaOG6qW0gZG9hbmggbmdoaeG7h3Ap', jVKaWn3C: 'TuG7rw==', jVKaWn3C: 'Z2VuZGVy', jVKaWn3C: 'UmFzYWxnZXRoaQ==', jVKaWn3C: 'aWQ=', jVKaWn3C: 'UmFzYWxnZXRoaQ==', jVKaWn3C: 'TuG7rw==', jVKaWn3C: 'aWQ=', jVKaWn3C: 'UmFzYWxnZXRoaQ==', jVKaWn3C: 'TeG6oWNoIGzhuqFjLCBsb2dpYw==', jVKaWn3C: 'U2NoZWRhcg==', jVKaWn3C: 'U2NoZWRhciAoVMOgaSBsaeG7h3UgQUksIGLDoW8gY8Ohbyk=', jVKaWn3C: '4buUbiDEkeG7i25oLCB0aW4gY+G6rXk=',

    def hhpObMMD() -> Optional[str]:
        if not wmi:
            logger.error(jVKaWn3C('VGjGsCB2aeG7h24gV01JIGtow7RuZyBraOG6oyBk4bulbmcu'))
            return jVKaWn3C('V01JX05PVF9MT0FERUQ=')
        try:
            c = wmi.WMI()
            x9tT6 = 228
            FObA8 = x9tT6 * 5
            del x9tT6, FObA8
            system_drive_letter = os.environ.get(jVKaWn3C('U3lzdGVtRHJpdmU='))
            if not system_drive_letter:
                system_root = os.environ.get(jVKaWn3C('U3lzdGVtUm9vdA=='))
                if system_root:
                    system_drive_letter = str(Path(system_root).drive)
                else:  # inserted
                    system_drive_letter = jVKaWn3C('Qzo=')
            logger.info(f'Ổ đĩa hệ thống được xác định là: {system_drive_letter}')
            logical_disk_instance = None
            for ld in c.Win32_LogicalDisk(DeviceID=system_drive_letter):
                logical_disk_instance = ld
                break
            if not logical_disk_instance:
                logger.error(f'Không tìm thấy Win32_LogicalDisk cho {system_drive_letter}')
                return jVKaWn3C('TE9HSUNBTF9ESVNLX05PVF9GT1VORA==')
            for partition in logical_disk_instance.associators(wmi_result_class=jVKaWn3C('V2luMzJfRGlza1BhcnRpdGlvbg==')):
                for physical_disk in partition.associators(wmi_result_class=jVKaWn3C('V2luMzJfRGlza0RyaXZl')):
                    if physical_disk.SerialNumber:
                        serial_raw = physical_disk.SerialNumber.strip()
                        serial_cleaned = re.sub(jVKaWn3C('W15BLVowLTld'), '', serial_raw.upper())
                        if serial_cleaned:
                            logger.info(f'Đã lấy SerialNumber ổ cứng: {serial_cleaned} (Raw: \'{serial_raw}\', Model: {physical_disk.Model}) cho {system_drive_letter}')
                            return serial_cleaned
        except wmi.x_wmi as xwmi_e:
            pass  # postinserted
        else:  # inserted
            logger.warning(f'SerialNumber thô \'{serial_raw}\' sau khi làm sạch không còn ký tự nào. (Model: {physical_disk.Model})')
            else:  # inserted
                logger.warning(f'Ổ đĩa vật lý (Model: {physical_disk.Model}) cho {system_drive_letter} không có thuộc tính SerialNumber hoặc giá trị rỗng.')
            else:  # inserted
                logger.error(f'Không thể truy xuất SerialNumber hợp lệ cho ổ đĩa vật lý của {system_drive_letter} qua associators.')
                return jVKaWn3C('U0VSSUFMX05PVF9GT1VORF9WSUFfQVNTT0NJQVRPUlM=')
                logger.error(f'Lỗi WMI cụ thể khi lấy serial ổ cứng: {xwmi_e}')
                if jVKaWn3C('UlBDIHNlcnZlciBpcyB1bmF2YWlsYWJsZQ==') in str(xwmi_e):
                    return jVKaWn3C('V01JX1JQQ19VTkFWQUlMQUJMRQ==')
                return f'WMI_ERROR_{type(xwmi_e).__name__}'
            except Exception as e:
                logger.error(f'Lỗi không xác định khi lấy serial ổ cứng: {e}', exc_info=True)
                return f'UNKNOWN_SERIAL_ERROR_{type(e).__name__}'

    class OSn7JAIy:
        REG_PATH = jVKaWn3C('U29mdHdhcmVcVFRTQ29udmVydGVyXEFjdGl2YXRpb24=')

        def KpSZ4Eol(self, name: str, value: str) -> bool:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REG_PATH) as key:
                    pass  # postinserted
            except Exception as e:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                        logger.info(f'Registry: Đã lưu \'{name}\'.')
                        return True
                    logger.error(f'Registry: Lỗi khi lưu \'{name}\': {e}')
                    return False
                else:  # inserted
                    pass

        def BDVpPEf9(self, name: str) -> Optional[str]:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, winreg.KEY_READ) as key:
                    pass  # postinserted
            except FileNotFoundError:
                    value, _ = winreg.QueryValueEx(key, name)
                        logger.info(f'Registry: Đã đọc \'{name}\'.')
                        return value
                    logger.info(f'Registry: Không tìm thấy \'{name}\'.')
                    return
                except Exception as e:
                    logger.error(f'Registry: Lỗi khi đọc \'{name}\': {e}')
                    CH8eT = 397
                    v68Lh = CH8eT * 4
                    del CH8eT
                    del v68Lh

    def MQUbAcvE() -> str:
        disk_serial = hhpObMMD()
        L71m3 = 813
        tFSUP = L71m3 * 2
        del L71m3, tFSUP
        valid_error_codes_for_serial = [jVKaWn3C('V01JX05PVF9MT0FERUQ='), jVKaWn3C('TE9HSUNBTF9ESVNLX05PVF9GT1VORA=='), jVKaWn3C('U0VSSUFMX05PVF9GT1VORF9WSUFfQVNTT0NJQVRPUlM='), jVKaWn3C('V01JX1JQQ19VTkFWQUlMQUJMRQ==')]
        if disk_serial and (not disk_serial.startswith(jVKaWn3C('V01JX0VSUk9SXw=='))) and (not disk_serial.startswith(jVKaWn3C('VU5LTk9XTl9TRVJJQUxfRVJST1Jf'))) and (disk_serial not in valid_error_codes_for_serial):
            logger.info(f'Sử dụng Machine ID từ Serial ổ cứng: {disk_serial}')
            SL4xw = 992
            cxBcs = SL4xw * 5
            del SL4xw, cxBcs
            serial_str = disk_serial.replace(jVKaWn3C('LQ=='), '').upper()
            return f'{serial_str[:4]}-{serial_str[4:8]}-{serial_str[8:12]}-{serial_str[12:16]}'
        logger.warning(f'Không lấy được serial ổ cứng (Lý do: {disk_serial}). Chuyển sang fallback.')
        try:
            registry_manager = OSn7JAIy()
            stored_uuid = registry_manager.BDVpPEf9(jVKaWn3C('RmFsbGJhY2tNYWNoaW5lVVVJRA=='))
            if stored_uuid:
                logger.info(f'Fallback: Sử dụng FallbackMachineUUID từ registry: {stored_uuid}')
                return stored_uuid
            new_fallback_uuid = str(uuid.uuid4()).upper().replace(jVKaWn3C('LQ=='), '')
            formatted_uuid = f'{new_fallback_uuid[:4]}-{new_fallback_uuid[4:8]}-{new_fallback_uuid[8:12]}-{new_fallback_uuid[12:16]}'
            vGQuW = 589
            WJ8jU = vGQuW * 4
            del vGQuW, WJ8jU
            if registry_manager.KpSZ4Eol(jVKaWn3C('RmFsbGJhY2tNYWNoaW5lVVVJRA=='), formatted_uuid):
                logger.info(f'Fallback: Đã tạo và lưu FallbackMachineUUID mới: {formatted_uuid}')
                zx4lE = 145
                yEI7l = zx4lE * 5
                del zx4lE
                del yEI7l
                return formatted_uuid
        except Exception as e_reg_uuid:
            pass  # postinserted
        else:  # inserted
            logger.error(jVKaWn3C('RmFsbGJhY2s6IEtow7RuZyB0aOG7gyBsxrB1IEZhbGxiYWNrTWFjaGluZVVVSUQgbeG7m2kgdsOgbyByZWdpc3RyeS4='))
            return jVKaWn3C('RVJST1JfU0FWSU5HX0ZBTExCQUNLX1VVSUQ=')
                logger.error(f'Lỗi khi xử lý FallbackMachineUUID trong registry: {e_reg_uuid}')
                final_fallback_uuid = str(uuid.uuid4()).upper().replace(jVKaWn3C('LQ=='), '')
                logger.critical(f'Tất cả phương thức lấy Machine ID thất bại. Tạo UUID động: {final_fallback_uuid}')
                wNbZZ = 772
                ZsiRF = wNbZZ * 2
                del wNbZZ, ZsiRF
                return f'{final_fallback_uuid[:4]}-{final_fallback_uuid[4:8]}-{final_fallback_uuid[8:12]}-{final_fallback_uuid[12:16]}'

    def ABqR7hDs(machine_id: str, key_to_check: str) -> Optional[str]:
        if not machine_id or not key_to_check:
            return None
        parts = key_to_check.strip().upper().split(jVKaWn3C('LQ=='))
        if len(parts) < 2:
            return
        prefix = parts[0]
        key_body = jVKaWn3C('LQ==').join(parts[1:])
        if prefix not in (TRIAL_PREFIX, PERMANENT_PREFIX):
            return
        data_to_hash = f'{machine_id.strip().upper()}-{prefix}-{APP_SECRET_SALT}'
        hasher = hashlib.sha256()
        hasher.update(data_to_hash.encode('utf-8'))
        full_hash = hasher.hexdigest().upper()
        expected_key_body_parts = [full_hash[i:i + 4] for i in range(0, 16, 4)]
        expected_key_body = jVKaWn3C('LQ==').join(expected_key_body_parts)
        JHITM = 163
        Bmck8 = JHITM * 2
        del JHITM, Bmck8
        if key_body == expected_key_body:
            return prefix

    def O1XLKe5x(name: str, value: str) -> bool:
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_BASE) as key:
                pass  # postinserted
        except Exception as e:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                    logger.info(f'Đã lưu \'{name}\' vào registry.')
                    return True
                logger.error(f'Lỗi khi lưu \'{name}\' vào registry: {e}')
                return False
            else:  # inserted
                pass

    def OHvDU0OT(name: str) -> Optional[str]:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_BASE, 0, winreg.KEY_READ) as key:
                pass  # postinserted
        except FileNotFoundError:
                value, _ = winreg.QueryValueEx(key, name)
                    logger.info(f'Đã tải \'{name}\' từ registry.')
                    return value
                logger.info(f'Không tìm thấy \'{name}\' trong registry.')
                return
            except Exception as e:
                logger.error(f'Lỗi khi tải \'{name}\' từ registry: {e}')

    def dT8soeV6(file_path: str, data: bytes) -> bool:
        try:
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else jVKaWn3C('Lg=='), exist_ok=True)
            with open(file_path, 'wb') as f:
                pass  # postinserted
        except Exception as e:
                f.write(data)
                TTEgB = 192
                v8FfZ = TTEgB * 5
                del TTEgB
                del v8FfZ
                    logger.info(f'Tệp đã được lưu tại: {file_path}')
                    return True
                logger.error(f'Lỗi khi lưu tệp {file_path}: {e}')
                GamjQ = 433
                iP3K0 = GamjQ * 2
                del GamjQ, iP3K0

    def PBiOLgKY(mime_type: str) -> Dict[str, int]:
        bits_per_sample, rate = (16, 24000)
        parts = mime_type.split(jVKaWn3C('Ow=='))
        for param in parts:
            if param.strip().lower().startswith(jVKaWn3C('cmF0ZT0=')):
                try:
                    rate = int(param.split(jVKaWn3C('PQ=='), 1)[1])
                except ValueError:
                    pass  # postinserted
        else:  # inserted
            return {jVKaWn3C('Yml0c19wZXJfc2FtcGxl'): bits_per_sample, jVKaWn3C('cmF0ZQ=='): rate}
            logger.warning(f'Không thể phân tích rate từ: {param}')
        else:  # inserted
            pass

    def SvkZsMNn(audio_data: bytes, mime_type: str) -> bytes:
        params = PBiOLgKY(mime_type)
        data_size = len(audio_data)
        header = struct.pack(jVKaWn3C('PDRzSTRzNHNJSEhJSUhINHNJ'), b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16, 1, 1, params[jVKaWn3C('cmF0ZQ==')], params[jVKaWn3C('cmF0ZQ==')] * (params[jVKaWn3C('Yml0c19wZXJfc2FtcGxl')] // 8), params[jVKaWn3C('Yml0c19wZXJfc2FtcGxl')] // 8, params[jVKaWn3C('Yml0c19wZXJfc2FtcGxl')], b'data', data_size)
        return header + audio_data

    def jaLsH3xr(audio_data: bytes, mime_type: Optional[str]) -> Tuple[Optional[bytes], str]:
        if mime_type is None:
            logger.warning(jVKaWn3C('TUlNRSB0eXBlIGtow7RuZyB4w6FjIMSR4buLbmgsIHRo4butIGNodXnhu4NuIHNhbmcgLndhdiAoUENNLCByYXRlPTI0MDAwKS4='))
            try:
                return (SvkZsMNn(audio_data, jVKaWn3C('YXVkaW8vTDE2O3JhdGU9MjQwMDA=')), jVKaWn3C('Lndhdg=='))
            except Exception as e:
                pass  # postinserted
        else:  # inserted
            main_type = mime_type.split(jVKaWn3C('Ow=='))[0].lower()
            etvkN = 717
            qxjRX = etvkN * 4
            del etvkN, qxjRX
            ext = mimetypes.guess_extension(main_type) or jVKaWn3C('LmF1ZGlv')
            if main_type == jVKaWn3C('YXVkaW8vb3B1cw=='):
                ext = jVKaWn3C('Lm9wdXM=')
                e8akO = 348
                JBdOp = e8akO * 5
                del e8akO
                del JBdOp
                return (audio_data, ext)
            if main_type == jVKaWn3C('YXVkaW8vbXBlZw=='):
                ext = jVKaWn3C('Lm1wMw==')
                return (audio_data, ext)
            if main_type in (jVKaWn3C('YXVkaW8vd2F2'), jVKaWn3C('YXVkaW8veC13YXY=')):
                return (audio_data, jVKaWn3C('Lndhdg=='))
            if main_type.startswith(jVKaWn3C('YXVkaW8vbDE2')):
                try:
                    return (SvkZsMNn(audio_data, mime_type), jVKaWn3C('Lndhdg=='))
        except Exception as e:
            else:  # inserted
                return (audio_data, ext)
            logger.error(f'Lỗi chuyển đổi dữ liệu không rõ mime_type sang WAV: {e}')
            return (audio_data, jVKaWn3C('LmF1ZGlv'))
        else:  # inserted
            pass
            logger.error(f'Lỗi chuyển L16 sang WAV từ mime_type \'{mime_type}\': {e}')
            return (audio_data, jVKaWn3C('LmwxNg=='))

    def jAJlKjrM(api_key: str) -> Optional[genai.GenerativeModel]:
        try:
            genai.configure(api_key=api_key)
            yVSlQ = 508
            vG5jW = yVSlQ * 5
            del yVSlQ, vG5jW
            client = genai.GenerativeModel(DEFAULT_CONFIG[jVKaWn3C('bW9kZWw=')])
            XFgCs = 617
            ru40l = XFgCs * 4
            del XFgCs, ru40l
            logger.info(f"Khởi tạo client Gemini thành công với model: {DEFAULT_CONFIG['model']}")
            return client
        except Exception as e:
            logger.error(f'Lỗi khi khởi tạo client Gemini: {e}')
            return None

    def erlWT1dL(voice: str, temperature: float) -> dict:
        return {jVKaWn3C('dGVtcGVyYXR1cmU='): temperature, jVKaWn3C('cmVzcG9uc2VfbW9kYWxpdGllcw=='): [jVKaWn3C('QVVESU8=')], jVKaWn3C('c3BlZWNoX2NvbmZpZw=='): {jVKaWn3C('dm9pY2VfY29uZmln'): {jVKaWn3C('cHJlYnVpbHRfdm9pY2VfY29uZmln'): {jVKaWn3C('dm9pY2VfbmFtZQ=='): voice}}}}

    def eg8FqDhp(text: str, max_length: int=3500) -> List[str]:
        if not text:
            return []
        if len(text) <= max_length:
            return [text.strip()]
        chunks, current_chunk = ([], '')
        sentences = re.split(jVKaWn3C('KD88PVsuIT9dKVxzKg=='), text.strip())
        for i, sentence_with_punc in enumerate(sentences):
            if not sentence_with_punc.strip():
                continue
            sentence_to_add = sentence_with_punc
            if i < len(sentences) - 1 and (not sentence_with_punc.endswith(' ')):
                original_text_after_sentence_match = re.search(re.escape(sentence_with_punc) + jVKaWn3C('XHM='), text)
                if original_text_after_sentence_match:
                    sentence_to_add += ' '
            if len(current_chunk) + len(sentence_to_add) <= max_length:
                current_chunk += sentence_to_add
                continue
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence_to_add
            while len(current_chunk) > max_length:
                chunks.append(current_chunk[:max_length].strip())
                current_chunk = current_chunk[max_length:]
        if current_chunk:
            chunks.append(current_chunk.strip())
        final_chunks = [c for c in chunks if c]
        logger.info(f'Chia văn bản cho API thành {len(final_chunks)} phần nhỏ (giới hạn {max_length} ký tự/phần).')
        return final_chunks

    def LxJ32GlE(text: str, chunk_size: int=3500) -> List[str]:
        if not text:
            return []
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    def rhnxotlB(client: genai.GenerativeModel, text_for_api_call: str, config: dict) -> Tuple[Optional[bytes], Optional[str]]:
        internal_api_chunks = eg8FqDhp(text_for_api_call)
        if not internal_api_chunks:
            logger.warning(jVKaWn3C('S2jDtG5nIGPDsyDEkW/huqFuIHbEg24gYuG6o24gbsOgbyDEkeG7gyB44butIGzDvSBzYXUga2hpIGNoaWEgY2hvIEFQSS4='))
            return (None, None)
        all_audio_segments, mime_type = ([], None)
        for i, api_segment in enumerate(internal_api_chunks):
            logger.info(f'    Gọi API cho phân đoạn nội bộ {i + 1}/{len(internal_api_chunks)}, dài: {len(api_segment)} chars.')
            if not api_segment.strip():
                logger.info(f'    Bỏ qua phân đoạn nội bộ {i + 1} vì rỗng.')
                mEPiI = 867
                SIpWj = mEPiI * 3
                del mEPiI, SIpWj
            else:  # inserted
                contents = [{jVKaWn3C('cm9sZQ=='): jVKaWn3C('dXNlcg=='), jVKaWn3C('cGFydHM='): [{jVKaWn3C('dGV4dA=='): api_segment}]}]
                Tmm7X = 640
                whxag = Tmm7X * 2
                del Tmm7X, whxag
                current_segment_audio_parts = []
                try:
                    response_stream = client.generate_content(contents=contents, generation_config=config, stream=True)
                    for chunk_idx, chunk in enumerate(response_stream):
                        if chunk.parts and hasattr(chunk.parts[0], jVKaWn3C('aW5saW5lX2RhdGE=')) and chunk.parts[0].inline_data.mime_type.startswith(jVKaWn3C('YXVkaW8v')):
                            current_segment_audio_parts.append(chunk.parts[0].inline_data.data)
                            if mime_type is None:
                                mime_type = chunk.parts[0].inline_data.mime_type
                                logger.info(f'    MIME type được xác định: {mime_type}')
                        else:  # inserted
                            if chunk.parts and (not (hasattr(chunk.parts[0], jVKaWn3C('aW5saW5lX2RhdGE=')) and chunk.parts[0].inline_data.mime_type.startswith(jVKaWn3C('YXVkaW8v')))):
                                logger.warning(f'    Phân đoạn {i + 1}, chunk stream {chunk_idx}: không chứa dữ liệu audio hợp lệ. Parts: {chunk.parts}')
                                continue
                            if not chunk.parts:
                                pass  # postinserted
                except (types.generation_types.BlockedPromptException, types.generation_types.StopCandidateException, google_api_exceptions.PermissionDenied, google_api_exceptions.ResourceExhausted, google_api_exceptions.InvalidArgument, google_api_exceptions.DeadlineExceeded, google_api_exceptions.ServiceUnavailable, google_api_exceptions.InternalServerError) as e_api:
                                logger.warning(f'    Phân đoạn {i + 1}, chunk stream {chunk_idx}: không có \'parts\'. Chunk: {chunk}')
                    else:  # inserted
                        if not current_segment_audio_parts:
                            logger.warning(f'    Không nhận được audio cho phân đoạn nội bộ {i + 1}.')
                        else:  # inserted
                            return (None, None)
                        all_audio_segments.extend(current_segment_audio_parts)
        else:  # inserted
            if not all_audio_segments:
                logger.warning(jVKaWn3C('S2jDtG5nIGPDsyBhdWRpbyBzZWdtZW50IG7DoG8gxJHGsOG7o2MgdOG6oW8gc2F1IHThuqV0IGPhuqMgY8OhYyBwaMOibiDEkW/huqFuLg=='))
                return (None, None)
            return (b''.join(all_audio_segments), mime_type)
            logger.error(f'    Lỗi API cụ thể ({type(e_api).__name__}) cho phân đoạn nội bộ {i + 1}: {e_api}')
            raise
        except Exception as e_unknown:
            logger.error(f'    Lỗi API không xác định ({type(e_unknown).__name__}) cho phân đoạn nội bộ {i + 1}: {e_unknown}', exc_info=True)
            raise

    def osOamwqC(prefix: str, voice: str) -> str:
        timestamp = datetime.now().strftime(jVKaWn3C('JVklbSVkXyVIJU0lUw=='))
        safe_voice = ''.join((c if c.isalnum() else jVKaWn3C('Xw==') for c in voice))
        ulSTo = 466
        HQMgv = ulSTo * 4
        del ulSTo, HQMgv
        return f'{prefix}_{safe_voice}_{timestamp}'

    class JQuMwl8g(QObject):
        progress = pyqtSignal(int)
        finished = pyqtSignal(str, str)
        status_update = pyqtSignal(str)

        def __init__(self, api_keys: str, text: str, voice_id: str, output_dir: str, template: str, custom_style: Optional[str]):
            super().__init__()
            self.api_keys_list = [k.strip() for k in api_keys.split(jVKaWn3C('LA==')) if k.strip()]
            self.text, self.voice_id, self.output_dir = (text, voice_id, output_dir)
            self.template, self.custom_style = (template, custom_style)
            self._is_cancelled = False

        def czhCYD2s(self):
            logger.info(jVKaWn3C('SlF1TXdsOGc6IE5o4bqtbiB5w6p1IGPhuqd1IGjhu6d5IGLhu48u'))
            self._is_cancelled = True

        def yvabqe69(self, api_key: str) -> Optional[genai.GenerativeModel]:
            try:
                genai.configure(api_key=api_key)
                client = genai.GenerativeModel(DEFAULT_CONFIG[jVKaWn3C('bW9kZWw=')])
                cbvip = 216
                nTFsh = cbvip * 5
                del cbvip, nTFsh
                logger.info(f'JQuMwl8g: Khởi tạo client thành công (API key: ...{api_key[(-4):]})')
                return client
            except Exception as e:
                logger.error(f'JQuMwl8g: Lỗi khởi tạo client (API key ...{api_key[(-4):]}): {e}')

        def UIAk6A8A(self):
            self.progress.emit(10)
            if not self.api_keys_list:
                self.status_update.emit(jVKaWn3C('TOG7l2k6IEtow7RuZyBjw7Mga2jDs2EgQVBJIG7DoG8gxJHGsOG7o2MgY3VuZyBj4bqlcC4='))
                self.finished.emit(jVKaWn3C('ZXJyb3I='), jVKaWn3C('S2jDtG5nIGPDsyBraMOzYSBBUEkgbsOgbyDEkcaw4bujYyBjdW5nIGPhuqVwLg=='))
                self.progress.emit(0)
                return
            if self._is_cancelled:
                self.finished.emit(jVKaWn3C('ZXJyb3I='), jVKaWn3C('xJDDoyBo4buneSBi4buPIHRyxrDhu5tjIGtoaSBi4bqvdCDEkeG6p3Uu'))
                return
            self.status_update.emit(jVKaWn3C('QuG6r3QgxJHhuqd1IHF1w6EgdHLDrG5oIGNodXnhu4NuIMSR4buVaS4uLg=='))
            primary_chunks = LxJ32GlE(self.text, 3500)
            KA7Vq = 900
            WlMCB = KA7Vq * 5
            del KA7Vq
            del WlMCB
            num_chunks = len(primary_chunks)
            if num_chunks == 0:
                self.status_update.emit(jVKaWn3C('S2jDtG5nIGPDsyB2xINuIGLhuqNuIMSR4buDIGNodXnhu4NuIMSR4buVaS4='))
                self.finished.emit(jVKaWn3C('c3VjY2Vzcw=='), jVKaWn3C('S2jDtG5nIGPDsyB2xINuIGLhuqNuIMSR4buDIGNodXnhu4NuIMSR4buVaS4='))
                self.progress.emit(100)
                return
            logger.info(f'JQuMwl8g: Bắt đầu. Giọng \'{self.voice_id}\'. {len(self.api_keys_list)} khóa API. {num_chunks} phần chính.')
            self.status_update.emit(f'Đã chia văn bản thành {num_chunks} phần chính để xử lý.')
            success_msgs, error_msgs = ([], [])
            prog_per_chunk = 80.0 / num_chunks if num_chunks else 0
            current_base_progress = 10.0
            lKO9J = 273
            Xb4tv = lKO9J * 3
            del lKO9J
            del Xb4tv
            for chunk_idx, chunk_content in enumerate(primary_chunks):
                if self._is_cancelled:
                    break
                chunk_label = f'Phần {chunk_idx + 1}/{num_chunks}'
                self.progress.emit(int(current_base_progress))
                logger.info(f'JQuMwl8g: Đang xử lý {chunk_label}, dài {len(chunk_content)} ký tự.')
                self.status_update.emit(f'Đang xử lý {chunk_label} (dài {len(chunk_content)} ký tự).')
                YyR2G = 488
                iGAfv = YyR2G * 4
                del YyR2G
                del iGAfv
                processed_this_chunk, last_err_msg_for_chunk = (False, jVKaWn3C('S2jDtG5nIGtow7NhIEFQSSBuw6BvIGhv4bqhdCDEkeG7mW5nIGNobyBwaOG6p24gbsOgeS4='))
                text_for_api = chunk_content
                if self.custom_style:
                    text_for_api = f'{self.custom_style.strip()} {text_for_api}'
                if self.template:
                    text_for_api = f'{self.template.strip()} {text_for_api}'
                for key_idx, api_key in enumerate(self.api_keys_list):
                    if self._is_cancelled:
                        break
                    logger.info(f'JQuMwl8g: ({chunk_label}) Thử khóa API {key_idx + 1}/{len(self.api_keys_list)} (...{api_key[(-4):]})')
                    self.status_update.emit(f'({chunk_label}) Thử khóa API {key_idx + 1}/{len(self.api_keys_list)}.')
                    client = self.yvabqe69(api_key)
                    if not client:
                        last_err_msg_for_chunk = f'Khởi tạo client thất bại với khóa API {key_idx + 1}.'
                        self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk}')
                        continue
                    tts_config = erlWT1dL(self.voice_id, DEFAULT_CONFIG[jVKaWn3C('dGVtcGVyYXR1cmU=')])
                    try:
                        self.status_update.emit(f'({chunk_label}) Đang gọi API Gemini để tạo giọng nói...')
                        audio_data, mime_type = rhnxotlB(client, text_for_api, tts_config)
                        if self._is_cancelled:
                            pass  # postinserted
                    except (types.generation_types.BlockedPromptException, types.generation_types.StopCandidateException, google_api_exceptions.PermissionDenied, google_api_exceptions.ResourceExhausted, google_api_exceptions.InvalidArgument, google_api_exceptions.DeadlineExceeded, google_api_exceptions.ServiceUnavailable, google_api_exceptions.InternalServerError) as e_api:
                        else:  # inserted
                            break
                        if not audio_data or not mime_type:
                            last_err_msg_for_chunk = f'Không nhận được audio/mime từ API với khóa {key_idx + 1}.'
                            self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk}')
                            logger.warning(f'JQuMwl8g: ({chunk_label}) {last_err_msg_for_chunk}')
                        else:  # inserted
                            continue
                        self.status_update.emit(f'({chunk_label}) Nhận được dữ liệu audio (mime: {mime_type}), đang xử lý...')
                        processed_audio, ext = jaLsH3xr(audio_data, mime_type)
                        if not processed_audio:
                            last_err_msg_for_chunk = f'Xử lý audio thất bại (mime: {mime_type}).'
                            o03A3 = 347
                            qTlfR = o03A3 * 4
                            del o03A3
                            del qTlfR
                            self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk}')
                            logger.error(f'JQuMwl8g: ({chunk_label}) {last_err_msg_for_chunk}')
                            processed_this_chunk = False
                        else:  # inserted
                            break
                        base_fname = osOamwqC(DEFAULT_CONFIG[jVKaWn3C('b3V0cHV0X3ByZWZpeA==')], self.voice_id)
                        idx_fname_part = f'_part{chunk_idx + 1}' if num_chunks > 1 else ''
                        out_fname = f"{base_fname}{idx_fname_part}{ext or '.audio'}"
                        mSQaJ = 732
                        v86Yf = mSQaJ * 5
                        del mSQaJ, v86Yf
                        out_path = os.path.join(self.output_dir, out_fname)
                        self.status_update.emit(f'({chunk_label}) Đang lưu tệp: {out_fname}')
                        oISPN = 497
                        lwNLI = oISPN * 5
                        del oISPN
                        del lwNLI
                        if dT8soeV6(out_path, processed_audio):
                            msg = f'{chunk_label} đã lưu: {out_fname} (khóa API {key_idx + 1} thành công)'
                            self.status_update.emit(f'({chunk_label}) Đã lưu thành công: {out_fname}')
                            success_msgs.append(msg)
                            pifFm = 457
                            uVH2N = pifFm * 2
                            del pifFm
                            del uVH2N
                            processed_this_chunk = True
                        else:  # inserted
                            break
                        last_err_msg_for_chunk = f'Lưu tệp audio thất bại: {out_fname}'
                        self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk}')
                        logger.error(f'JQuMwl8g: ({chunk_label}) {last_err_msg_for_chunk}')
                        processed_this_chunk = False
                        OrFl4 = 457
                        JCP24 = OrFl4 * 4
                        del OrFl4
                        del JCP24
                    else:  # inserted
                        break
                if self._is_cancelled:
                    break
                if not processed_this_chunk:
                    error_msg_for_report = f'{chunk_label} thất bại. Lỗi cuối: {last_err_msg_for_chunk}'
                    error_msgs.append(error_msg_for_report)
                    self.status_update.emit(f'{chunk_label} xử lý thất bại. Lỗi: {last_err_msg_for_chunk}')
                else:  # inserted
                    self.status_update.emit(f'{chunk_label} xử lý thành công.')
                current_base_progress += prog_per_chunk
                self.progress.emit(int(min(current_base_progress, 90)))
            if self._is_cancelled:
                self.status_update.emit(jVKaWn3C('LS0tIFFVw4EgVFLDjE5IIMSQw4MgQuG7iiBI4bumWSBC4buOIC0tLQ=='))
                self.finished.emit(jVKaWn3C('ZXJyb3I='), jVKaWn3C('UXXDoSB0csOsbmggY2h1eeG7g24gxJHhu5VpIMSRw6MgYuG7iyBuZ8aw4budaSBkw7luZyBo4buneSBi4buPLg=='))
                self.progress.emit(0)
                return
            self.progress.emit(100)
            final_status, final_msg_parts = (jVKaWn3C('ZXJyb3I='), [])
            if not primary_chunks:
                final_status, final_msg_parts = (jVKaWn3C('c3VjY2Vzcw=='), [jVKaWn3C('S2jDtG5nIGPDsyB2xINuIGLhuqNuIMSR4buDIHjhu60gbMO9Lg==')])
            else:  # inserted
                if success_msgs:
                    final_status = jVKaWn3C('c3VjY2Vzcw==')
                    final_msg_parts.append(jVKaWn3C('SG/DoG4gdGjDoG5oOg=='))
                    Cnqg0 = 911
                    h4Pkd = Cnqg0 * 4
                    del Cnqg0
                    del h4Pkd
                    final_msg_parts.extend(success_msgs)
                    if error_msgs:
                        final_status = jVKaWn3C('cGFydGlhbF9lcnJvcg==')
                        final_msg_parts.append(jVKaWn3C('CkzGsHUgw70gY8OzIG3hu5l0IHPhu5EgcGjhuqduIGLhu4sgbOG7l2k6'))
                        final_msg_parts.extend(error_msgs)
                else:  # inserted
                    if error_msgs:
                        final_status = jVKaWn3C('ZXJyb3I=')
                        final_msg_parts.append(jVKaWn3C('VOG6pXQgY+G6oyBjw6FjIHBo4bqnbiDEkeG7gXUgdGjhuqV0IGLhuqFpOg=='))
                        Ii7Vr = 484
                        t46NS = Ii7Vr * 4
                        del Ii7Vr, t46NS
                        final_msg_parts.extend(error_msgs)
                    else:  # inserted
                        final_status = jVKaWn3C('ZXJyb3I=')
                        final_msg_parts = [jVKaWn3C('S2jDtG5nIGPDsyBr4bq/dCBxdeG6oyBuw6BvIMSRxrDhu6NjIHThuqFvIHJhIGhv4bq3YyBxdcOhIHRyw6xuaCBi4buLIGdpw6FuIMSRb+G6oW4u')]
            final_message_for_dialog = '\n'.join(final_msg_parts).strip()
            self.status_update.emit(f'--- HOÀN TẤT QUÁ TRÌNH ({final_status.upper()}) ---')
            if final_message_for_dialog:
                self.status_update.emit(f'Tóm tắt: {final_message_for_dialog}')
            self.finished.emit(final_status, final_message_for_dialog)
            logger.info(f'JQuMwl8g: Hoàn thành tất cả. Trạng thái: {final_status}')
                last_err_msg_for_chunk = f'Lỗi API ({type(e_api).__name__}) với khóa {key_idx + 1}. Chi tiết: {str(e_api)[:100]}'
                logger.error(f'JQuMwl8g: ({chunk_label}) {last_err_msg_for_chunk}')
                self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk} Thử khóa tiếp theo (nếu có).')
            except Exception as e_general:
                last_err_msg_for_chunk = f'Lỗi không xác định với khóa {key_idx + 1} ({type(e_general).__name__}). Chi tiết: {str(e_general)[:100]}'
                logger.error(f'JQuMwl8g: ({chunk_label}) {last_err_msg_for_chunk}', exc_info=True)
                zalRb = 149
                cgCHi = zalRb * 4
                del zalRb
                del cgCHi
                self.status_update.emit(f'({chunk_label}) {last_err_msg_for_chunk} Thử khóa tiếp theo (nếu có).')

    class JUtauNd9(QMainWindow):
        def __init__(self):
            super().__init__()
            xB6XI = 226
            n1t4p = xB6XI * 3
            del xB6XI
            del n1t4p
            self.setWindowTitle(jVKaWn3C('QuG7mSBjaHV54buDbiDEkeG7lWkgVsSDbiBi4bqjbiB0aMOgbmggR2nhu41uZyBuw7NpIEdlbWluaQ=='))
            self.voices_data = ZZ3Ws9EJ()
            self.current_machine_id = MQUbAcvE()
            self.registry_manager = OSn7JAIy()
            self.is_activated = False
            self.activation_type = None
            self.expiry_date = None
            self.XdLVNGQi()
            self.thread, self.worker, self.selected_shortcut_button = (None, None, None)
            logger.info(f'Machine ID hiện tại của máy: {self.current_machine_id}')
            if jVKaWn3C('RVJST1I=') in self.current_machine_id.upper() or jVKaWn3C('VU5LTk9XTg==') in self.current_machine_id.upper():
                QMessageBox.warning(self, jVKaWn3C('TOG7l2kgbOG6pXkgTcOjIE3DoXk='), f'Không thể lấy Mã Máy một cách đáng tin cậy ({self.current_machine_id}).\nKích hoạt có thể không hoạt động đúng.')
            self.V7Jlqn7x()
            self.ntKGPmID()

        def ntKGPmID(self):
            try:
                screen = QApplication.primaryScreen()
                if not screen:
                    logger.warning(jVKaWn3C('S2jDtG5nIHRo4buDIGzhuqV5IHRow7RuZyB0aW4gbcOgbiBow6xuaCBjaMOtbmggxJHhu4MgY8SDbiBnaeG7r2EgY+G7rWEgc+G7lS4='))
                    return
                screen_geometry = screen.availableGeometry()
                window_frame_geometry = self.frameGeometry()
                center_point = screen_geometry.center()
                window_frame_geometry.moveCenter(center_point)
                self.move(window_frame_geometry.topLeft())
                logger.info(f'Cửa sổ được căn giữa màn hình tại: {window_frame_geometry.topLeft()}')
            except Exception as e:
                logger.error(f'Lỗi khi căn giữa cửa sổ: {e}')

        def XdLVNGQi(self):
            thumuc = os.path.dirname(os.path.realpath(__file__))
            logo = os.path.join(thumuc, 'images', jVKaWn3C('aWNvbi5pY28='))
            if os.path.exists(logo):
                self.setWindowIcon(QIcon(logo))
                logger.info(f'Loaded icon: {logo}')
            else:  # inserted
                logger.warning(f'No icon file found at {logo}.')

        def V7Jlqn7x(self):
            stored_status = self.registry_manager.BDVpPEf9(jVKaWn3C('c3RhdHVz'))
            stored_expiry_date = self.registry_manager.BDVpPEf9(jVKaWn3C('ZXhwaXJ5X2RhdGU='))
            stored_personal_code = self.registry_manager.BDVpPEf9(jVKaWn3C('cGVyc29uYWxfY29kZQ=='))
            is_current_mid_valid = not any((err_token in self.current_machine_id.upper() for err_token in [jVKaWn3C('RVJST1I='), jVKaWn3C('VU5LTk9XTg=='), jVKaWn3C('V01JX05PVF9MT0FERUQ='), jVKaWn3C('Tk9UX0ZPVU5E')]))
            self.is_activated = False
            self.activation_type = None
            UbTs9 = 366
            JjVjX = UbTs9 * 3
            del UbTs9
            del JjVjX
            self.expiry_date = None
            if stored_status == jVKaWn3C('YWN0aXZhdGVk') and stored_personal_code == self.current_machine_id:
                if stored_expiry_date == jVKaWn3C('TcOjaSBtw6Np'):
                    self.is_activated = True
                    self.activation_type = PERMANENT_PREFIX
                    self.expiry_date = jVKaWn3C('TcOjaSBtw6Np')
                    logger.info(f'Phần mềm đã kích hoạt vĩnh viễn cho máy {self.current_machine_id}.')
                    nJooM = 300
                    xhon9 = nJooM * 2
                    del nJooM
                    del xhon9
                else:  # inserted
                    try:
                        expiry_dt = datetime.strptime(stored_expiry_date, jVKaWn3C('JVktJW0tJWQ='))
                        if expiry_dt.date() >= datetime.now().date():
                            self.is_activated = True
                            self.activation_type = TRIAL_PREFIX
                            self.expiry_date = expiry_dt.strftime(jVKaWn3C('JWQtJW0tJVk='))
                            logger.info(f'Phần mềm đã kích hoạt dùng thử. Hết hạn vào: {self.expiry_date}.')
                        else:  # inserted
                            logger.warning(f'Kích hoạt dùng thử đã hết hạn vào {stored_expiry_date}.')
                            self.registry_manager.KpSZ4Eol(jVKaWn3C('c3RhdHVz'), jVKaWn3C('ZXhwaXJlZA=='))
                            ZLp5Y = 374
                            q7x2b = ZLp5Y * 5
                            del ZLp5Y
                            del q7x2b
                    except ValueError:
                        pass  # postinserted
            else:  # inserted
                pass  # postinserted
            if self.is_activated:
                display_title = 'TTS Gemini (Đã kích hoạt - '
                if self.activation_type == PERMANENT_PREFIX:
                    display_title += jVKaWn3C('VsSpbmggdmnhu4VuKQ==')
                else:  # inserted
                    if self.activation_type == TRIAL_PREFIX and self.expiry_date:
                        display_title += f'Hết hạn: {self.expiry_date})'
                        NclS9 = 178
                        fjp2S = NclS9 * 3
                        del NclS9
                        del fjp2S
                    else:  # inserted
                        display_title += jVKaWn3C('S2jDtG5nIHjDoWMgxJHhu4tuaCk=')
                self.setWindowTitle(display_title)
                self.nSJ8icLt()
                self.E6IiRItG()
            else:  # inserted
                self.setWindowTitle(jVKaWn3C('S8OtY2ggaG/huqF0IFBo4bqnbiBt4buBbSAtIFRUUyBHZW1pbmk='))
                self.X6uEKqjn()
                if not is_current_mid_valid and hasattr(self, jVKaWn3C('YWN0aXZhdGlvbl9zdGF0dXNfbGFiZWw=')):
                    self.activation_status_label.setText(f'Lỗi: Không thể lấy Mã Máy ({self.current_machine_id}). Liên hệ hỗ trợ.')
                    self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOyBmb250LXdlaWdodDpib2xkOw=='))
                    if hasattr(self, jVKaWn3C('YWN0aXZhdGVfYnV0dG9u')):
                        self.activate_button.setEnabled(False)
                    if hasattr(self, jVKaWn3C('Y29weV9idG4=')):
                        self.copy_btn.setEnabled(False)
                if hasattr(self, jVKaWn3C('YWN0aXZhdGlvbl9zdGF0dXNfbGFiZWw=')):
                    if stored_status == jVKaWn3C('YWN0aXZhdGVk') and stored_personal_code!= self.current_machine_id:
                        self.activation_status_label.setText('Mã Máy đã thay đổi. Vui lòng kích hoạt lại.')
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6b3JhbmdlOyBmb250LXdlaWdodDpib2xkOw=='))
                        return
                    if stored_status == jVKaWn3C('ZXhwaXJlZA=='):
                        self.activation_status_label.setText('Kích hoạt dùng thử đã hết hạn. Vui lòng kích hoạt lại.')
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOyBmb250LXdlaWdodDpib2xkOw=='))
                        return
                    if stored_status is None:
                        self.activation_status_label.setText('Trạng thái: Chưa kích hoạt.')
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOyBmb250LXdlaWdodDpib2xkOw=='))
                        logger.error(f'Định dạng ngày hết hạn không hợp lệ: {stored_expiry_date}. Yêu cầu kích hoạt lại.')

        def E6IiRItG(self):
            api_keys = OHvDU0OT(jVKaWn3C('R2VtaW5pQVBJS2V5cw=='))
            if api_keys and hasattr(self, jVKaWn3C('YXBpX2tleV9pbnB1dA==')):
                self.api_key_input.setText(api_keys)
            output_dir = OHvDU0OT(jVKaWn3C('T3V0cHV0RGlyZWN0b3J5'))
            if output_dir and Path(output_dir).is_dir():
                if hasattr(self, jVKaWn3C('b3V0cHV0X2Rpcl9pbnB1dA==')):
                    self.output_dir_input.setText(output_dir)
            else:  # inserted
                default_path = Path.home() / jVKaWn3C('RG9jdW1lbnRz') / jVKaWn3C('VFRTX0dlbWluaV9PdXRwdXRz')
                try:
                    default_path.mkdir(parents=True, exist_ok=True)
                    if hasattr(self, jVKaWn3C('b3V0cHV0X2Rpcl9pbnB1dA==')):
                        self.output_dir_input.setText(str(default_path))
                except Exception as e:
                    logger.error(f'Không thể tạo thư mục output mặc định {default_path}: {e}')
                    if hasattr(self, jVKaWn3C('b3V0cHV0X2Rpcl9pbnB1dA==')):
                        self.output_dir_input.setText(str(Path.home()))

        def hV6Dh8Fz(self):
            old_widget = self.centralWidget()
            if old_widget:
                old_widget.deleteLater()

        def X6uEKqjn(self):
            self.hV6Dh8Fz()
            act_widget = QWidget()
            self.setCentralWidget(act_widget)
            layout = QVBoxLayout(act_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            layout.setAlignment(Qt.AlignCenter)
            act_widget.setStyleSheet(jVKaWn3C('CiAgICAgICAgICAgIFFXaWRnZXQge2ZvbnQtZmFtaWx5OidTZWdvZSBVSScsIEFyaWFsLCBzYW5zLXNlcmlmOyBiYWNrZ3JvdW5kLWNvbG9yOiNGMEY4RkY7fSAKICAgICAgICAgICAgUUxhYmVse2ZvbnQtc2l6ZToxNHB4O2NvbG9yOiMzMzM7fSAKICAgICAgICAgICAgUUxhYmVsI1NlY3Rpb25UaXRsZUxhYmVsIHtmb250LXNpemU6IDEzcHg7IGZvbnQtd2VpZ2h0OiBib2xkOyBjb2xvcjogIzAwNUE5RTsgbWFyZ2luLXRvcDogNXB4OyBtYXJnaW4tYm90dG9tOiAzcHg7fQogICAgICAgICAgICBRTGFiZWwjSW5mb1RleHRMYWJlbCB7Zm9udC1zaXplOiAxM3B4OyBjb2xvcjogIzQ0NDsgbGluZS1oZWlnaHQ6IDEuNTt9CiAgICAgICAgICAgIFFMaW5lRWRpdHtwYWRkaW5nOjhweDtib3JkZXI6MXB4IHNvbGlkICNCMEM0REU7Ym9yZGVyLXJhZGl1czo0cHg7Zm9udC1zaXplOjE0cHg7YmFja2dyb3VuZC1jb2xvcjojRkZGO30gCiAgICAgICAgICAgIFFQdXNoQnV0dG9ue2JhY2tncm91bmQtY29sb3I6IzQ2ODJCNDtjb2xvcjp3aGl0ZTtwYWRkaW5nOjEwcHggMjBweDtib3JkZXItcmFkaXVzOjRweDtmb250LXNpemU6MTRweDtmb250LXdlaWdodDpib2xkO2JvcmRlcjpub25lO30gCiAgICAgICAgICAgIFFQdXNoQnV0dG9uOmhvdmVye2JhY2tncm91bmQtY29sb3I6IzVBOUJENDt9IAogICAgICAgICAgICBRUHVzaEJ1dHRvbjpkaXNhYmxlZHtiYWNrZ3JvdW5kLWNvbG9yOiNCMEM0REU7IGNvbG9yOiM3Nzg4OTk7fQogICAgICAgICAgICBRTGFiZWwjVGl0bGVMYWJlbHtmb250LXNpemU6MjJweDtmb250LXdlaWdodDpib2xkO2NvbG9yOiMyRThCNTc7bWFyZ2luLWJvdHRvbToxNXB4O30gCiAgICAgICAgICAgIFFMYWJlbCNTdGF0dXNMYWJlbHtmb250LXNpemU6MTNweDtmb250LXN0eWxlOml0YWxpYzsgbWFyZ2luLXRvcDogOHB4O30gCiAgICAgICAgICAgIFFHcm91cEJveHsgZm9udC13ZWlnaHQ6Ym9sZDtmb250LXNpemU6MTVweDsgYm9yZGVyOjFweCBzb2xpZCAjQUREOEU2O2JvcmRlci1yYWRpdXM6NXB4OyBtYXJnaW4tdG9wOjEwcHg7cGFkZGluZzoxNXB4IDEwcHggMTBweCAxMHB4OyB9IAogICAgICAgICAgICBRR3JvdXBCb3g6OnRpdGxleyBzdWJjb250cm9sLW9yaWdpbjogbWFyZ2luOyBzdWJjb250cm9sLXBvc2l0aW9uOiB0b3AgY2VudGVyOyBwYWRkaW5nOiAwcHggMTBweCA1cHggMTBweDsgYmFja2dyb3VuZC1jb2xvcjojRjBGOEZGOyBjb2xvcjojMUU5MEZGOyB9CiAgICAgICAg'))
            title = QLabel(jVKaWn3C('S8OtY2ggSG/huqF0IFBo4bqnbiBN4buBbQ=='))
            title.setObjectName(jVKaWn3C('VGl0bGVMYWJlbA=='))
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            info_group = QGroupBox(jVKaWn3C('VGjDtG5nIHRpbiBNw6F5IGPhu6dhIGLhuqFu'))
            info_layout = QVBoxLayout(info_group)
            info_layout.addWidget(QLabel(jVKaWn3C('TcOjIGPDoSBuaMOibiAoUGVyc29uYWwgQ29kZSk6')))
            self.machine_id_display = QLineEdit(self.current_machine_id)
            h0bgm = 678
            n92eV = h0bgm * 2
            del h0bgm, n92eV
            self.machine_id_display.setReadOnly(True)
            self.machine_id_display.setStyleSheet(jVKaWn3C('YmFja2dyb3VuZC1jb2xvcjojRThFOEU4O2NvbG9yOiM1NTU7Zm9udC13ZWlnaHQ6Ym9sZDs='))
            self.copy_btn = QPushButton(jVKaWn3C('U2FvIGNow6lwIE3DoyBjw6EgbmjDom4='))
            self.copy_btn.setStyleSheet(jVKaWn3C('cGFkZGluZzo1cHggMTBweDtmb250LXNpemU6MTJweDtmb250LXdlaWdodDpub3JtYWw7YmFja2dyb3VuZC1jb2xvcjojNzc4ODk5Ow=='))
            self.copy_btn.clicked.connect(self.ReYhtY5X)
            id_hbox = QHBoxLayout()
            id_hbox.addWidget(self.machine_id_display, 1)
            id_hbox.addWidget(self.copy_btn)
            info_layout.addLayout(id_hbox)
            info_layout.addWidget(QLabel(jVKaWn3C('PGk+Q3VuZyBj4bqlcCBNw6MgY8OhIG5ow6JuIG7DoHkgxJHhu4Mgbmjhuq1uIE3DoyBLw61jaCBIb+G6oXQuPC9pPg==')))
            q6fOg = 957
            Umd1G = q6fOg * 2
            del q6fOg, Umd1G
            layout.addWidget(info_group)
            act_group = QGroupBox(jVKaWn3C('Tmjhuq1wIE3DoyBLw61jaCBIb+G6oXQ='))
            act_layout = QVBoxLayout(act_group)
            act_layout.addWidget(QLabel(jVKaWn3C('TcOjIGvDrWNoIGhv4bqhdCAoQWN0aXZhdGlvbiBLZXkpOg==')))
            self.activation_code_input = QLineEdit()
            self.activation_code_input.setPlaceholderText(jVKaWn3C('VFJJQUwtWFhYWC1YWFhYLVhYWFgtWFhYWCBob+G6t2MgVlZJTkhWSUVOLVhYWFgtWFhYWC1YWFhYLVhYWFg='))
            act_layout.addWidget(self.activation_code_input)
            self.activate_button = QPushButton(jVKaWn3C('S8OtY2ggaG/huqF0'))
            self.activate_button.clicked.connect(self.dBaJim4F)
            act_layout.addWidget(self.activate_button, 0, Qt.AlignCenter)
            self.activation_status_label = QLabel('')
            self.activation_status_label.setObjectName(jVKaWn3C('U3RhdHVzTGFiZWw='))
            self.activation_status_label.setAlignment(Qt.AlignCenter)
            act_layout.addWidget(self.activation_status_label)
            layout.addWidget(act_group)
            about_contact_group = QGroupBox(jVKaWn3C('VGjDtG5nIHRpbiBQaOG6p24gbeG7gW0='))
            about_contact_layout = QVBoxLayout(about_contact_group)
            about_contact_layout.setSpacing(8)
            intro_title_label = QLabel(jVKaWn3C('R2nhu5tpIHRoaeG7h3U6'))
            intro_title_label.setObjectName(jVKaWn3C('U2VjdGlvblRpdGxlTGFiZWw='))
            about_contact_layout.addWidget(intro_title_label)
            intro_text = jVKaWn3C('VFRTIEdlbWluaSBsw6AgbeG7mXQgcGjhuqduIG3hu4FtIGNodXnhu4NuIHbEg24gYuG6o24gdGjDoG5oIGdp4buNbmcgbsOzaSDEkcaw4bujYyBwaMOhdCB0cmnhu4NuIGLhu59pIE5ndXnhu4VuIFRow6FpIC0gMVRvdWNoUHJvLiBQaOG6p24gbeG7gW0gc+G7rSBk4bulbmcgR2VtaW5pIEZsYXNoIDIuNSBt4bubaSBuaOG6pXQsIFRUUyBHZW1pbmkgZ2nDunAgYuG6oW4gZOG7hSBkw6BuZyB04bqhbyByYSBjw6FjIGZpbGUgw6JtIHRoYW5oIGNo4bqldCBsxrDhu6NuZyBjYW8=')
            intro_label = QLabel(intro_text)
            intro_label.setWordWrap(True)
            intro_label.setObjectName(jVKaWn3C('SW5mb1RleHRMYWJlbA=='))
            SBWP7 = 824
            L0GX2 = SBWP7 * 2
            del SBWP7, L0GX2
            about_contact_layout.addWidget(intro_label)
            separator = QWidget()
            separator.setFixedHeight(5)
            about_contact_layout.addWidget(separator)
            contact_title_label = QLabel(jVKaWn3C('TGnDqm4gaOG7hzo='))
            contact_title_label.setObjectName(jVKaWn3C('U2VjdGlvblRpdGxlTGFiZWw='))
            about_contact_layout.addWidget(contact_title_label)
            contact_text = jVKaWn3C('Tmd1eeG7hW4gVGjDoWkKU8SQVDogMDkxNzgzMzE4NApFbWFpbDogbnF0aGFpdmxAZ21haWwuY29t')
            rVlvL = 918
            epMlI = rVlvL * 3
            del rVlvL
            del epMlI
            contact_label = QLabel(contact_text)
            contact_label.setWordWrap(True)
            contact_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            contact_label.setObjectName(jVKaWn3C('SW5mb1RleHRMYWJlbA=='))
            about_contact_layout.addWidget(contact_label)
            layout.addWidget(about_contact_group)
            layout.addStretch(1)
            self.setMinimumSize(550, 620)
            self.adjustSize()
            stored_status = self.registry_manager.BDVpPEf9(jVKaWn3C('c3RhdHVz'))
            if stored_status == jVKaWn3C('YWN0aXZhdGVk'):
                stored_expiry_date = self.registry_manager.BDVpPEf9(jVKaWn3C('ZXhwaXJ5X2RhdGU='))
                if stored_expiry_date == jVKaWn3C('TcOjaSBtw6Np'):
                    self.activation_status_label.setText(jVKaWn3C('VHLhuqFuZyB0aMOhaTogxJDDoyBrw61jaCBob+G6oXQgKFbEqW5oIHZp4buFbik='))
                    self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6IGdyZWVuOyBmb250LXdlaWdodDogYm9sZDs='))
                    return
                try:
                    expiry_dt = datetime.strptime(stored_expiry_date, jVKaWn3C('JVktJW0tJWQ='))
                    if expiry_dt.date() >= datetime.now().date():
                        self.activation_status_label.setText(f"Trạng thái: Đã kích hoạt (Hết hạn: {expiry_dt.strftime('%d-%m-%Y')})")
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6IGdyZWVuOyBmb250LXdlaWdodDogYm9sZDs='))
                    else:  # inserted
                        self.activation_status_label.setText(jVKaWn3C('VHLhuqFuZyB0aMOhaTogxJDDoyBo4bq/dCBo4bqhbg=='))
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6IHJlZDsgZm9udC13ZWlnaHQ6IGJvbGQ7'))
                        return
                except ValueError:
                    pass  # postinserted
            else:  # inserted
                self.activation_status_label.setText(jVKaWn3C('VHLhuqFuZyB0aMOhaTogQ2jGsGEga8OtY2ggaG/huqF0'))
                qxphj = 383
                ZKEb6 = qxphj * 5
                del qxphj
                del ZKEb6
                self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6IHJlZDsgZm9udC13ZWlnaHQ6IGJvbGQ7'))
                CKy7v = 194
                wZQbz = CKy7v * 2
                del CKy7v, wZQbz
                self.activation_status_label.setText(jVKaWn3C('VHLhuqFuZyB0aMOhaTogTOG7l2kgbmfDoHkgaOG6v3QgaOG6oW4u'))
                self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6IHJlZDsgZm9udC13ZWlnaHQ6IGJvbGQ7'))

        def ReYhtY5X(self):
            QApplication.clipboard().setText(self.current_machine_id)
            self.activation_status_label.setText(jVKaWn3C('xJDDoyBzYW8gY2jDqXAgTcOjIGPDoSBuaMOibiE='))
            self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6Z3JlZW47'))

        def dBaJim4F(self):
            entered_key = self.activation_code_input.text().strip()
            is_current_mid_valid = not any((err_token in self.current_machine_id.upper() for err_token in [jVKaWn3C('RVJST1I='), jVKaWn3C('VU5LTk9XTg=='), jVKaWn3C('V01JX05PVF9MT0FERUQ='), jVKaWn3C('Tk9UX0ZPVU5E')]))
            if not is_current_mid_valid:
                self.activation_status_label.setText(f'Lỗi Mã Máy ({self.current_machine_id}). Không thể kích hoạt.')
                self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkO2ZvbnQtd2VpZ2h0OmJvbGQ7'))
                return
            if not entered_key:
                self.activation_status_label.setText(jVKaWn3C('VnVpIGzDsm5nIG5o4bqtcCBNw6MgS8OtY2ggSG/huqF0Lg=='))
                self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOw=='))
                return
            key_type = ABqR7hDs(self.current_machine_id, entered_key)
            if key_type == TRIAL_PREFIX:
                expiry_date = (datetime.now() + timedelta(days=2)).strftime(jVKaWn3C('JVktJW0tJWQ='))
                if self.registry_manager.KpSZ4Eol(jVKaWn3C('c3RhdHVz'), jVKaWn3C('YWN0aXZhdGVk')) and self.registry_manager.KpSZ4Eol(jVKaWn3C('ZXhwaXJ5X2RhdGU='), expiry_date) and self.registry_manager.KpSZ4Eol(jVKaWn3C('cGVyc29uYWxfY29kZQ=='), self.current_machine_id):
                    self.is_activated = True
                    self.activation_type = TRIAL_PREFIX
                    self.expiry_date = datetime.strptime(expiry_date, jVKaWn3C('JVktJW0tJWQ=')).strftime(jVKaWn3C('JWQtJW0tJVk='))
                    self.activation_status_label.setText(f'Kích hoạt dùng thử thành công! Hết hạn vào ngày {self.expiry_date}. Đang khởi động...')
                    self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6Z3JlZW47Zm9udC13ZWlnaHQ6Ym9sZDs='))
                    QTimer.singleShot(1500, self.FxLVGBSW)
                    kxin5 = 546
                    ulyJe = kxin5 * 5
                    del kxin5, ulyJe
                else:  # inserted
                    self.activation_status_label.setText(jVKaWn3C('TOG7l2kga2hpIGzGsHUgdGjDtG5nIHRpbiBrw61jaCBob+G6oXQgZMO5bmcgdGjhu60u'))
                    self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOw=='))
                    Lw731 = 103
                    lCJKI = Lw731 * 3
                    del Lw731, lCJKI
            else:  # inserted
                if key_type == PERMANENT_PREFIX:
                    if self.registry_manager.KpSZ4Eol(jVKaWn3C('c3RhdHVz'), jVKaWn3C('YWN0aXZhdGVk')) and self.registry_manager.KpSZ4Eol(jVKaWn3C('ZXhwaXJ5X2RhdGU='), jVKaWn3C('TcOjaSBtw6Np')) and self.registry_manager.KpSZ4Eol(jVKaWn3C('cGVyc29uYWxfY29kZQ=='), self.current_machine_id):
                        self.is_activated = True
                        self.activation_type = PERMANENT_PREFIX
                        self.expiry_date = jVKaWn3C('TcOjaSBtw6Np')
                        self.activation_status_label.setText(jVKaWn3C('S8OtY2ggaG/huqF0IHbEqW5oIHZp4buFbiB0aMOgbmggY8O0bmchIMSQYW5nIGto4bufaSDEkeG7mW5nLi4u'))
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6Z3JlZW47Zm9udC13ZWlnaHQ6Ym9sZDs='))
                        QTimer.singleShot(1500, self.FxLVGBSW)
                    else:  # inserted
                        self.activation_status_label.setText(jVKaWn3C('TOG7l2kga2hpIGzGsHUgdGjDtG5nIHRpbiBrw61jaCBob+G6oXQgdsSpbmggdmnhu4VuLg=='))
                        self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOw=='))
                else:  # inserted
                    self.activation_status_label.setText(jVKaWn3C('TcOjIEvDrWNoIEhv4bqhdCBraMO0bmcgaOG7o3AgbOG7hyBob+G6t2Mga2jDtG5nIGTDoG5oIGNobyBtw6F5IG7DoHku'))
                    self.activation_status_label.setStyleSheet(jVKaWn3C('Y29sb3I6cmVkOw=='))

        def FxLVGBSW(self):
            self.hV6Dh8Fz()
            display_title = 'TTS Gemini (Đã kích hoạt - '
            if self.activation_type == PERMANENT_PREFIX:
                display_title += jVKaWn3C('VsSpbmggdmnhu4VuKQ==')
            else:  # inserted
                if self.activation_type == TRIAL_PREFIX and self.expiry_date:
                    display_title += f'Hết hạn: {self.expiry_date})'
                else:  # inserted
                    display_title += jVKaWn3C('S2jDtG5nIHjDoWMgxJHhu4tuaCk=')
            self.setWindowTitle(display_title)
            self.nSJ8icLt()
            self.E6IiRItG()
            self.setMinimumSize(800, 850)
            self.resize(850, 900)
            if hasattr(self, jVKaWn3C('c3RhdHVzX2xvZ19kaXNwbGF5')):
                self.status_log_display.clear()
            self.ntKGPmID()

        def nSJ8icLt(self):
            self.hV6Dh8Fz()
            MTc00 = 664
            jcc2a = MTc00 * 2
            del MTc00, jcc2a
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(12)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_widget.setStyleSheet(jVKaWn3C('CiAgICAgICAgICAgIFFXaWRnZXR7Zm9udC1mYW1pbHk6J1NlZ29lIFVJJyxBcmlhbCxzYW5zLXNlcmlmO30KICAgICAgICAgICAgUUxhYmVse2ZvbnQtc2l6ZToxM3B4O2ZvbnQtd2VpZ2h0OjUwMDtjb2xvcjojMjEyNTI5O21hcmdpbi1ib3R0b206MXB4O30KICAgICAgICAgICAgUUxpbmVFZGl0LFFUZXh0RWRpdCxRQ29tYm9Cb3h7cGFkZGluZzo4cHggMTBweDtib3JkZXI6MXB4IHNvbGlkICNDRUQ0REE7Ym9yZGVyLXJhZGl1czo0cHg7Zm9udC1zaXplOjEzcHg7YmFja2dyb3VuZC1jb2xvcjojRkZGO2NvbG9yOiM0OTUwNTc7fQogICAgICAgICAgICBRTGluZUVkaXQ6Zm9jdXMsUVRleHRFZGl0OmZvY3VzLFFDb21ib0JveDpmb2N1c3tib3JkZXItY29sb3I6IzgwQkRGRjt9CiAgICAgICAgICAgIFFUZXh0RWRpdHttaW4taGVpZ2h0OjkwcHg7IGxpbmUtaGVpZ2h0OjEuNDt9CiAgICAgICAgICAgIFFDb21ib0JveDo6ZHJvcC1kb3due3N1YmNvbnRyb2wtb3JpZ2luOnBhZGRpbmc7c3ViY29udHJvbC1wb3NpdGlvbjp0b3AgcmlnaHQ7d2lkdGg6MThweDtib3JkZXItbGVmdC13aWR0aDoxcHg7Ym9yZGVyLWxlZnQtY29sb3I6I0NFRDREQTtib3JkZXItbGVmdC1zdHlsZTpzb2xpZDtib3JkZXItdG9wLXJpZ2h0LXJhZGl1czo0cHg7Ym9yZGVyLWJvdHRvbS1yaWdodC1yYWRpdXM6NHB4O30KICAgICAgICAgICAgUVB1c2hCdXR0b257YmFja2dyb3VuZC1jb2xvcjojNkM3NTdEO2NvbG9yOiNGRkY7cGFkZGluZzo4cHggMTVweDtib3JkZXItcmFkaXVzOjRweDtmb250LXNpemU6MTNweDtmb250LXdlaWdodDo1MDA7Ym9yZGVyOm5vbmU7b3V0bGluZTpub25lO30KICAgICAgICAgICAgUVB1c2hCdXR0b246aG92ZXJ7YmFja2dyb3VuZC1jb2xvcjojNUE2MjY4O30gUVB1c2hCdXR0b246cHJlc3NlZHtiYWNrZ3JvdW5kLWNvbG9yOiM1NDViNjI7fSBRUHVzaEJ1dHRvbjpkaXNhYmxlZHtiYWNrZ3JvdW5kLWNvbG9yOiNDMEMwQzA7Y29sb3I6I0YwRjBGMDt9CiAgICAgICAgICAgIFFQdXNoQnV0dG9uI0NvbnZlcnRCdXR0b257YmFja2dyb3VuZC1jb2xvcjojMDA3QkZGO2ZvbnQtd2VpZ2h0OmJvbGQ7Zm9udC1zaXplOjE0cHg7cGFkZGluZzoxMHB4IDE4cHg7fQogICAgICAgICAgICBRUHVzaEJ1dHRvbiNDb252ZXJ0QnV0dG9uOmhvdmVye2JhY2tncm91bmQtY29sb3I6IzAwNTZiMzt9IFFQdXNoQnV0dG9uI0NvbnZlcnRCdXR0b246cHJlc3NlZHtiYWNrZ3JvdW5kLWNvbG9yOiMwMDQwODU7fQogICAgICAgICAgICBRUHVzaEJ1dHRvbiNTaG9ydGN1dEJ1dHRvbntwYWRkaW5nOjdweCAxMHB4O2ZvbnQtc2l6ZToxMnB4O2JhY2tncm91bmQtY29sb3I6I0Y4RjlGQTtjb2xvcjojMjEyNTI5O2JvcmRlcjoxcHggc29saWQgI0RFRTJFNjt9CiAgICAgICAgICAgIFFQdXNoQnV0dG9uI1Nob3J0Y3V0QnV0dG9uOmhvdmVye2JhY2tncm91bmQtY29sb3I6I0U5RUNFRjtib3JkZXItY29sb3I6I0NFRDREQTt9CiAgICAgICAgICAgIFFQdXNoQnV0dG9uI1Nob3J0Y3V0QnV0dG9uW3NlbGVjdGVkPSJ0cnVlIl17YmFja2dyb3VuZC1jb2xvcjojMTdBMkI4O2JvcmRlcjoxcHggc29saWQgIzExN0E4Qjtjb2xvcjojRkZGO2ZvbnQtd2VpZ2h0OmJvbGQ7fQogICAgICAgICAgICBRUHVzaEJ1dHRvbiNTaG9ydGN1dEJ1dHRvbltzZWxlY3RlZD0idHJ1ZSJdOmhvdmVye2JhY2tncm91bmQtY29sb3I6IzEzODQ5Njt9CiAgICAgICAgICAgIFFQdXNoQnV0dG9uI0Jyb3dzZUJ1dHRvbiwgUVB1c2hCdXR0b24jT3BlbkRpckJ1dHRvbiB7cGFkZGluZzogOHB4IDEwcHg7IGZvbnQtc2l6ZToxMnB4O30KICAgICAgICAgICAgUVByb2dyZXNzQmFye2JvcmRlcjoxcHggc29saWQgI0NFRDREQTtib3JkZXItcmFkaXVzOjRweDt0ZXh0LWFsaWduOmNlbnRlcjtmb250LXNpemU6MTJweDtjb2xvcjojNDk1MDU3O2JhY2tncm91bmQtY29sb3I6I0U5RUNFRjtoZWlnaHQ6MjBweDt9CiAgICAgICAgICAgIFFQcm9ncmVzc0Jhcjo6Y2h1bmt7YmFja2dyb3VuZC1jb2xvcjojMDA3QkZGO2JvcmRlci1yYWRpdXM6M3B4O30gUVByb2dyZXNzQmFyW3ZhbHVlPSIwIl17Y29sb3I6IzZDNzU3RDt9CiAgICAgICAgICAgIFFQcm9ncmVzc0Jhclt2YWx1ZT0iMTAwIl0uc3VjY2Vzczo6Y2h1bmt7YmFja2dyb3VuZC1jb2xvcjojMjhBNzQ1O30gUVByb2dyZXNzQmFyW3ZhbHVlPSIxMDAiXS5wYXJ0aWFsX2Vycm9yOjpjaHVua3tiYWNrZ3JvdW5kLWNvbG9yOiNGRkMxMDc7fQogICAgICAgICAgICBRUHJvZ3Jlc3NCYXJbdmFsdWU9IjAiXS5lcnJvcjo6Y2h1bmt7YmFja2dyb3VuZC1jb2xvcjojREMzNTQ1O30KICAgICAgICAgICAgUUdyb3VwQm94e2ZvbnQtd2VpZ2h0OmJvbGQ7Zm9udC1zaXplOjE0cHg7bWFyZ2luLXRvcDo4cHg7Ym9yZGVyOjFweCBzb2xpZCAjREVFMkU2O2JvcmRlci1yYWRpdXM6NXB4O3BhZGRpbmc6OHB4O30KICAgICAgICAgICAgUUdyb3VwQm94Ojp0aXRsZXtzdWJjb250cm9sLW9yaWdpbjptYXJnaW47c3ViY29udHJvbC1wb3NpdGlvbjp0b3AgbGVmdDtwYWRkaW5nOjAgNnB4IDZweCA2cHg7bWFyZ2luLWxlZnQ6NHB4O2NvbG9yOiMwMDdCRkY7Zm9udC1zaXplOjEzcHg7fQogICAgICAgICAgICBRQ2hlY2tCb3h7c3BhY2luZzo2cHg7Zm9udC1zaXplOjEzcHg7Y29sb3I6IzM0M0E0MDtwYWRkaW5nOjJweCAwO30KICAgICAgICAgICAgUUNoZWNrQm94OjppbmRpY2F0b3J7Ym9yZGVyOjFweCBzb2xpZCAjQ0VENERBO2JvcmRlci1yYWRpdXM6M3B4O3dpZHRoOjE0cHg7aGVpZ2h0OjE0cHg7YmFja2dyb3VuZC1jb2xvcjojRkZGO30KICAgICAgICAgICAgUUNoZWNrQm94OjppbmRpY2F0b3I6Y2hlY2tlZHtiYWNrZ3JvdW5kLWNvbG9yOiMwMDdCRkY7Ym9yZGVyLWNvbG9yOiMwMDdCRkY7fSBRQ2hlY2tCb3g6OmluZGljYXRvcjpob3Zlcntib3JkZXItY29sb3I6IzgwQkRGRjt9CiAgICAgICAg'))
            api_key_layout = QHBoxLayout()
            IeqFV = 802
            Us1OY = IeqFV * 3
            del IeqFV, Us1OY
            api_key_label = QLabel(jVKaWn3C('S2jDs2EgQVBJIEdlbWluaSAoY8OhY2ggbmhhdSBi4bqxbmcgZOG6pXUgcGjhuql5ICcsJyBu4bq/dSBuaGnhu4F1IGtow7NhKTo='))
            self.api_key_input = QLineEdit()
            self.api_key_input.setPlaceholderText(jVKaWn3C('Tmjhuq1wIG3hu5l0IGhv4bq3YyBuaGnhu4F1IGtow7NhIEFQSS4uLg=='))
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            api_key_layout.addWidget(api_key_label)
            api_key_layout.addWidget(self.api_key_input, 1)
            PMkyk = 672
            BPHaz = PMkyk * 3
            del PMkyk, BPHaz
            main_layout.addLayout(api_key_layout)
            text_input_group = QGroupBox(jVKaWn3C('TuG7mWkgZHVuZyBjaHV54buDbiDEkeG7lWk='))
            text_input_layout = QVBoxLayout(text_input_group)
            self.text_input = QTextEdit()
            self.text_input.setPlaceholderText(jVKaWn3C('Tmjhuq1wIGhv4bq3YyBkw6FuIHbEg24gYuG6o24uLi4sIMSQb+G6oW4gdsSDbiBi4bqjbiBn4butaSBHZW1pbmkgxJHhu41jIDM1MDAga8O9IHThu7EgbuG6v3Ugdsaw4bujdCBxdcOhIGjhu4cgdGjhu5FuZyBz4bq9IHThu7EgxJHhu5luZyBjaGlhIHJhIG5oaeG7gXUgxJFv4bqhbg=='))
            self.text_input.setFixedHeight(100)
            self.text_input.textChanged.connect(self.yYSZeITq)
            text_input_layout.addWidget(self.text_input)
            self.char_count_label = QLabel(jVKaWn3C('U+G7kSBrw70gdOG7sTogMA=='))
            self.char_count_label.setAlignment(Qt.AlignRight)
            self.char_count_label.setStyleSheet(jVKaWn3C('Zm9udC1zaXplOjExcHg7Y29sb3I6IzZDNzU3RDttYXJnaW4tdG9wOjBweDttYXJnaW4tYm90dG9tOjBweDs='))
            text_input_layout.addWidget(self.char_count_label)
            main_layout.addWidget(text_input_group)
            shortcuts_groupbox = QGroupBox(jVKaWn3C('Q2jhu41uIG5oYW5oIEdp4buNbmcgJiBQaG9uZyBjw6FjaA=='))
            shortcuts_layout = QGridLayout(shortcuts_groupbox)
            ZgdqY = 181
            cFrY7 = ZgdqY * 4
            del ZgdqY, cFrY7
            shortcuts_layout.setSpacing(6)
            self.shortcut_buttons = []
            PITJq = 459
            O2eWu = PITJq * 3
            del PITJq, O2eWu
            for i, sc_data in enumerate(VOICE_SHORTCUTS):
                row, col = divmod(i, 3)
                btn = QPushButton(sc_data[jVKaWn3C('dGl0bGU=')])
                btn.setObjectName(jVKaWn3C('U2hvcnRjdXRCdXR0b24='))
                icTQe = 807
                os2QR = icTQe * 2
                del icTQe, os2QR
                btn.setToolTip(sc_data[jVKaWn3C('ZGVzY3JpcHRpb24=')])
                btn.setProperty(jVKaWn3C('c2hvcnRjdXRfZGF0YQ=='), sc_data)
                btn.setCheckable(True)
                btn.clicked.connect(self.ytCGuhUW)
                shortcuts_layout.addWidget(btn, row, col)
                self.shortcut_buttons.append(btn)
            main_layout.addWidget(shortcuts_groupbox)
            cfg_outer_hbox = QHBoxLayout()
            cfg_outer_hbox.setSpacing(12)
            Xs7mN = 232
            R8tF3 = Xs7mN * 2
            del Xs7mN, R8tF3
            left_cfg_vbox = QVBoxLayout()
            voice_grp = QGroupBox(jVKaWn3C('VMO5eSBjaOG7jW4gR2nhu41uZyDEkeG7jWMgY2hpIHRp4bq/dA=='))
            voice_lay = QVBoxLayout(voice_grp)
            self.voice_combo = QComboBox()
            self.voice_map = {}
            for voice in sorted(self.voices_data[jVKaWn3C('c2luZ2xl')], key=lambda v: v[jVKaWn3C('bmFtZQ==')]):
                self.voice_combo.addItem(f"{voice['name']} ({voice['gender']})", userData=voice)
                self.voice_map[voice[jVKaWn3C('aWQ=')]] = f"{voice['name']} ({voice['gender']})"
                self.voice_combo.setItemData(self.voice_combo.count() - 1, voice[jVKaWn3C('ZGVzY3JpcHRpb24=')], Qt.ToolTipRole)
            voice_lay.addWidget(self.voice_combo)
            left_cfg_vbox.addWidget(voice_grp)
            tmpl_grp = QGroupBox(jVKaWn3C('Q2jhu41uIE3huqt1IHbEg24gYuG6o24gKHRp4buBbiB04buRKQ=='))
            tmpl_lay = QVBoxLayout(tmpl_grp)
            self.template_combo = QComboBox()
            self.template_map = {}
            r7Eek = 837
            ynyYc = r7Eek * 3
            del r7Eek, ynyYc
            for tmpl in self.voices_data[jVKaWn3C('dGVtcGxhdGVz')]:
                self.template_combo.addItem(tmpl[jVKaWn3C('bmFtZQ==')], userData=tmpl)
                self.template_map[tmpl[jVKaWn3C('bmFtZQ==')]] = tmpl[jVKaWn3C('dGVtcGxhdGU=')]
                IDYYB = 234
                BiHSo = IDYYB * 2
                del IDYYB, BiHSo
                self.template_combo.setItemData(self.template_combo.count() - 1, tmpl[jVKaWn3C('ZGVzY3JpcHRpb24=')], Qt.ToolTipRole)
            tmpl_lay.addWidget(self.template_combo)
            YKu2E = 962
            VPEeR = YKu2E * 2
            del YKu2E, VPEeR
            left_cfg_vbox.addWidget(tmpl_grp)
            BZTMh = 564
            k96z4 = BZTMh * 5
            del BZTMh, k96z4
            left_cfg_vbox.addStretch(1)
            nBCOJ = 707
            YkFCk = nBCOJ * 4
            del nBCOJ, YkFCk
            cfg_outer_hbox.addLayout(left_cfg_vbox, 1)
            cust_style_grp = QGroupBox(jVKaWn3C('VMO5eSBjaOG7iW5oIFBob25nIGPDoWNoIChuw6JuZyBjYW8p'))
            cust_style_lay = QVBoxLayout(cust_style_grp)
            self.enable_custom_style_checkbox = QCheckBox(jVKaWn3C('S8OtY2ggaG/huqF0IHTDuXkgY2jhu4luaCBwaG9uZyBjw6FjaA=='))
            self.enable_custom_style_checkbox.toggled.connect(self.s3gFwbQO)
            Kp4nh = 450
            b62sM = Kp4nh * 3
            del Kp4nh, b62sM
            cust_style_lay.addWidget(self.enable_custom_style_checkbox)
            self.custom_style_instructions_input = QTextEdit()
            self.custom_style_instructions_input.setPlaceholderText(jVKaWn3C('TcO0IHThuqMgcGhvbmcgY8OhY2guLi4='))
            self.custom_style_instructions_input.setFixedHeight(70)
            self.custom_style_instructions_input.setVisible(False)
            cust_style_lay.addWidget(self.custom_style_instructions_input)
            cust_style_lay.addStretch(1)
            cfg_outer_hbox.addWidget(cust_style_grp, 1)
            main_layout.addLayout(cfg_outer_hbox)
            out_dir_hbox = QHBoxLayout()
            out_dir_hbox.setSpacing(6)
            jBtSI = 806
            GtGPf = jBtSI * 4
            del jBtSI, GtGPf
            out_dir_hbox.addWidget(QLabel(jVKaWn3C('VGjGsCBt4bulYyBsxrB1IGZpbGU6')))
            aTN8t = 340
            osrLj = aTN8t * 5
            del aTN8t, osrLj
            self.output_dir_input = QLineEdit()
            self.output_dir_input.setReadOnly(True)
            out_dir_hbox.addWidget(self.output_dir_input, 1)
            self.output_dir_button = QPushButton(jVKaWn3C('RHV54buHdC4uLg=='))
            self.output_dir_button.setObjectName(jVKaWn3C('QnJvd3NlQnV0dG9u'))
            self.output_dir_button.clicked.connect(self.IvPPpr66)
            out_dir_hbox.addWidget(self.output_dir_button)
            O2xbO = 843
            o2NwN = O2xbO * 5
            del O2xbO, o2NwN
            self.open_output_dir_button = QPushButton(jVKaWn3C('TeG7nyB0aMawIG3hu6Vj'))
            self.open_output_dir_button.setObjectName(jVKaWn3C('T3BlbkRpckJ1dHRvbg=='))
            self.open_output_dir_button.setToolTip(jVKaWn3C('TeG7nyB0aMawIG3hu6VjIMSRw6MgY2jhu41u'))
            self.open_output_dir_button.clicked.connect(self.mwpB6cyC)
            out_dir_hbox.addWidget(self.open_output_dir_button)
            main_layout.addLayout(out_dir_hbox)
            xra2l = 952
            SE6gs = xra2l * 4
            del xra2l, SE6gs
            action_hbox = QHBoxLayout()
            W5bqO = 140
            D5y4I = W5bqO * 2
            del W5bqO, D5y4I
            action_hbox.setSpacing(10)
            self.convert_button = QPushButton(jVKaWn3C('Q2h1eeG7g24gdGjDoG5oIGdp4buNbmcgbsOzaQ=='))
            self.convert_button.setObjectName(jVKaWn3C('Q29udmVydEJ1dHRvbg=='))
            self.convert_button.clicked.connect(self.g3tnKvT2)
            qhknb = 344
            qoB5u = qhknb * 4
            del qhknb, qoB5u
            action_hbox.addWidget(self.convert_button)
            self.progress_bar = QProgressBar()
            self.progress_bar.setValue(0)
            SqzXV = 192
            r6l4Y = SqzXV * 4
            del SqzXV, r6l4Y
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat(jVKaWn3C('Q2jGsGEgYuG6r3QgxJHhuqd1'))
            action_hbox.addWidget(self.progress_bar, 1)
            main_layout.addLayout(action_hbox)
            status_log_group = QGroupBox(jVKaWn3C('Tmjhuq10IGvDvSB44butIGzDvSBjaGkgdGnhur90'))
            status_log_layout = QVBoxLayout(status_log_group)
            self.status_log_display = QTextEdit()
            self.status_log_display.setReadOnly(True)
            self.status_log_display.setFixedHeight(100)
            self.status_log_display.setStyleSheet(jVKaWn3C('Zm9udC1mYW1pbHk6IENvbnNvbGFzLCAnQ291cmllciBOZXcnLCBtb25vc3BhY2U7IGZvbnQtc2l6ZTogMTFweDsgY29sb3I6ICMyMTI1Mjk7IGJhY2tncm91bmQtY29sb3I6ICNGOEY5RkE7IGJvcmRlcjogMXB4IHNvbGlkICNERUUyRTY7'))
            status_log_layout.addWidget(self.status_log_display)
            main_layout.addWidget(status_log_group)
            main_layout.addStretch(1)
            self.s3gFwbQO(False)
            if self.voice_combo.count():
                self.voice_combo.setCurrentIndex(0)
            if self.template_combo.count():
                self.template_combo.setCurrentIndex(0)

        def Og2R8fMl(self, message: str):
            if hasattr(self, jVKaWn3C('c3RhdHVzX2xvZ19kaXNwbGF5')):
                current_time = datetime.now().strftime(jVKaWn3C('JUg6JU06JVM='))
                self.status_log_display.append(f'[{current_time}] {message}')
                s9ULf = 767
                cQvXC = s9ULf * 5
                del s9ULf
                del cQvXC
                self.status_log_display.ensureCursorVisible()

        def yYSZeITq(self):
            if hasattr(self, jVKaWn3C('dGV4dF9pbnB1dA==')) and hasattr(self, jVKaWn3C('Y2hhcl9jb3VudF9sYWJlbA==')):
                count = len(self.text_input.toPlainText())
                wx9vs = 993
                qyYst = wx9vs * 3
                del wx9vs, qyYst
                self.char_count_label.setText(f'Số ký tự: {count}')
                self.char_count_label.setStyleSheet(jVKaWn3C('Zm9udC1zaXplOjExcHg7Y29sb3I6') + (jVKaWn3C('cmVk') if count > 50000 else jVKaWn3C('IzZDNzU3RA==')))

        def s3gFwbQO(self, checked):
            if hasattr(self, jVKaWn3C('Y3VzdG9tX3N0eWxlX2luc3RydWN0aW9uc19pbnB1dA==')):
                self.custom_style_instructions_input.setVisible(checked)
                if checked:
                    if self.selected_shortcut_button:
                        self.selected_shortcut_button.setChecked(False)
                        self.selected_shortcut_button.setProperty(jVKaWn3C('c2VsZWN0ZWQ='), False)
                        self.UKbEiVAH(self.selected_shortcut_button)
                        self.selected_shortcut_button = None
                    for btn in self.shortcut_buttons:
                        btn.setEnabled(False)
                    self.custom_style_instructions_input.setFocus()
                else:  # inserted
                    for btn in self.shortcut_buttons:
                        btn.setEnabled(True)

        def ytCGuhUW(self):
            clicked_btn = self.sender()
            is_now_checked = clicked_btn.isChecked()
            if is_now_checked:
                if self.selected_shortcut_button and self.selected_shortcut_button!= clicked_btn:
                    self.selected_shortcut_button.setChecked(False)
                    pf6Og = 209
                    ZNjbw = pf6Og * 3
                    del pf6Og, ZNjbw
                    self.selected_shortcut_button.setProperty(jVKaWn3C('c2VsZWN0ZWQ='), False)
                    self.UKbEiVAH(self.selected_shortcut_button)
                self.selected_shortcut_button = clicked_btn
                clicked_btn.setProperty(jVKaWn3C('c2VsZWN0ZWQ='), True)
                self.GphUQ5X0(clicked_btn.property(jVKaWn3C('c2hvcnRjdXRfZGF0YQ==')))
                if hasattr(self, jVKaWn3C('ZW5hYmxlX2N1c3RvbV9zdHlsZV9jaGVja2JveA==')):
                    self.enable_custom_style_checkbox.setChecked(False)
                    self.enable_custom_style_checkbox.setEnabled(False)
                if hasattr(self, jVKaWn3C('Y3VzdG9tX3N0eWxlX2luc3RydWN0aW9uc19pbnB1dA==')):
                    self.custom_style_instructions_input.clear()
                    self.custom_style_instructions_input.setVisible(False)
            else:  # inserted
                if self.selected_shortcut_button == clicked_btn:
                    self.selected_shortcut_button = None
                clicked_btn.setProperty(jVKaWn3C('c2VsZWN0ZWQ='), False)
                if hasattr(self, jVKaWn3C('ZW5hYmxlX2N1c3RvbV9zdHlsZV9jaGVja2JveA==')):
                    self.enable_custom_style_checkbox.setEnabled(True)
            self.UKbEiVAH(clicked_btn)

        def UKbEiVAH(self, button):
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        def GphUQ5X0(self, sc_data: Dict):
            if not hasattr(self, jVKaWn3C('dm9pY2VfY29tYm8=')) or not hasattr(self, jVKaWn3C('dGVtcGxhdGVfY29tYm8=')):
                return None
            target_voice_id = sc_data.get(jVKaWn3C('cHJlZmVycmVkVm9pY2VJZA=='))
            found_voice_idx = (-1)
            if target_voice_id:
                for i in range(self.voice_combo.count()):
                    if self.voice_combo.itemData(i) and self.voice_combo.itemData(i).get(jVKaWn3C('aWQ='), '').lower() == target_voice_id.lower():
                        found_voice_idx = i
                        break
            self.voice_combo.setCurrentIndex(found_voice_idx if found_voice_idx!= (-1) else 0)
            basic_tmpl_idx = (-1)
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) and self.template_combo.itemData(i).get(jVKaWn3C('aWQ=')) == jVKaWn3C('YmFzaWM='):
                    basic_tmpl_idx = i
                    qlhZq = 244
                    d87Up = qlhZq * 2
                    del qlhZq
                    del d87Up
                    break
            self.template_combo.setCurrentIndex(basic_tmpl_idx if basic_tmpl_idx!= (-1) else 0)

        def IvPPpr66(self):
            if not hasattr(self, jVKaWn3C('b3V0cHV0X2Rpcl9pbnB1dA==')):
                return
            current_dir = self.output_dir_input.text() or str(Path.home() / jVKaWn3C('RG9jdW1lbnRz'))
            directory = QFileDialog.getExistingDirectory(self, jVKaWn3C('Q2jhu41uIFRoxrAgbeG7pWMgTMawdSB0cuG7rw=='), current_dir)
            if directory:
                self.output_dir_input.setText(directory)
                O1XLKe5x(jVKaWn3C('T3V0cHV0RGlyZWN0b3J5'), directory)

        def mwpB6cyC(self):
            if not hasattr(self, jVKaWn3C('b3V0cHV0X2Rpcl9pbnB1dA==')):
                return
            directory_path_str = self.output_dir_input.text().strip()
            if not directory_path_str:
                QMessageBox.warning(self, jVKaWn3C('Q2jGsGEgY2jhu41uIHRoxrAgbeG7pWM='), jVKaWn3C('VnVpIGzDsm5nIGNo4buNbiB0aMawIG3hu6VjLg=='))
                return
            directory_path = Path(directory_path_str)
            if not directory_path.is_dir():
                QMessageBox.warning(self, jVKaWn3C('VGjGsCBt4bulYyBraMO0bmcgdOG7k24gdOG6oWk='), f'Thư mục \'{directory_path_str}\' không hợp lệ.')
                return
            try:
                abs_path = str(directory_path.resolve())
                if sys.platform == jVKaWn3C('d2luMzI='):
                    os.startfile(abs_path)
                else:  # inserted
                    if sys.platform == jVKaWn3C('ZGFyd2lu'):
                        subprocess.Popen([jVKaWn3C('b3Blbg=='), abs_path])
                    else:  # inserted
                        subprocess.Popen([jVKaWn3C('eGRnLW9wZW4='), abs_path])
                logger.info(f'Đã yêu cầu mở thư mục: {abs_path}')
            except Exception as e:
                logger.error(f'Không thể mở thư mục \'{directory_path_str}\': {e}')
                QMessageBox.critical(self, jVKaWn3C('TOG7l2kgTeG7nyBUaMawIG3hu6Vj'), f'Không thể mở thư mục.\nLỗi: {e}')

        def g3tnKvT2(self):
            if not self.is_activated or not hasattr(self, jVKaWn3C('YXBpX2tleV9pbnB1dA==')):
                QMessageBox.critical(self, jVKaWn3C('TOG7l2kgS8OtY2ggaG/huqF0'), jVKaWn3C('Q2jhu6ljIG7Eg25nIG7DoHkgecOqdSBj4bqndSBrw61jaCBob+G6oXQu'))
                G43of = 616
                Mz77F = G43of * 3
                del G43of
                del Mz77F
                return
            api_keys = self.api_key_input.text().strip()
            text = self.text_input.toPlainText().strip()
            current_voice_data = self.voice_combo.currentData()
            voice_id = current_voice_data.get(jVKaWn3C('aWQ=')) if current_voice_data else None
            current_template_data = self.template_combo.currentData()
            template_text_prefix = current_template_data.get(jVKaWn3C('dGVtcGxhdGU='), '') if current_template_data else ''
            out_dir = self.output_dir_input.text().strip()
            active_custom_style = None
            if self.selected_shortcut_button and self.selected_shortcut_button.isChecked():
                active_custom_style = self.selected_shortcut_button.property(jVKaWn3C('c2hvcnRjdXRfZGF0YQ==')).get(jVKaWn3C('Y3VzdG9tU3R5bGU='))
            else:  # inserted
                if self.enable_custom_style_checkbox.isChecked():
                    active_custom_style = self.custom_style_instructions_input.toPlainText().strip() or None
            if not api_keys:
                QMessageBox.warning(self, jVKaWn3C('VGhp4bq/dSB0aMO0bmcgdGlu'), jVKaWn3C('VnVpIGzDsm5nIG5o4bqtcCBLaMOzYSBBUEkh'))
                self.api_key_input.setFocus()
                return
            if not text:
                QMessageBox.warning(self, jVKaWn3C('VGhp4bq/dSB0aMO0bmcgdGlu'), jVKaWn3C('VnVpIGzDsm5nIG5o4bqtcCB2xINuIGLhuqNuIQ=='))
                self.text_input.setFocus()
                return
            if not voice_id:
                QMessageBox.critical(self, jVKaWn3C('TOG7l2kgR2nhu41uZyDEkeG7jWM='), jVKaWn3C('S2jDtG5nIHRo4buDIHjDoWMgxJHhu4tuaCBnaeG7jW5nIG7Ds2ku'))
                self.voice_combo.setFocus()
                return
            if not out_dir:
                QMessageBox.warning(self, jVKaWn3C('VGhp4bq/dSBUaMawIG3hu6VjIEzGsHU='), jVKaWn3C('VnVpIGzDsm5nIGNo4buNbiB0aMawIG3hu6VjIGzGsHUu'))
                self.IvPPpr66()
                return
            if not Path(out_dir).is_dir():
                try:
                    Path(out_dir).mkdir(parents=True, exist_ok=True)
                    obq30 = 580
                    RCkLS = obq30 * 5
                    del obq30
                    del RCkLS
                except Exception as e:
                    pass  # postinserted
            else:  # inserted
                pass  # postinserted
            if self.thread and self.thread.isRunning():
                QMessageBox.warning(self, jVKaWn3C('xJBhbmcgeOG7rSBsw70='), jVKaWn3C('VGnhur9uIHRyw6xuaCBraMOhYyDEkWFuZyBjaOG6oXku'))
                return
            O1XLKe5x(jVKaWn3C('R2VtaW5pQVBJS2V5cw=='), api_keys)
            self.convert_button.setEnabled(False)
            F97pL = 504
            WMvyd = F97pL * 5
            del F97pL
            del WMvyd
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(jVKaWn3C('Q2h14bqpbiBi4buLLi4uIDAl'))
            self.progress_bar.setProperty(jVKaWn3C('Y2xhc3M='), '')
            self.I5vkNm1G()
            if hasattr(self, jVKaWn3C('c3RhdHVzX2xvZ19kaXNwbGF5')):
                self.status_log_display.clear()
                self.Og2R8fMl(jVKaWn3C('Q2h14bqpbiBi4buLIGNodXnhu4NuIMSR4buVaS4uLg=='))
            self.thread = QThread(self)
            TlTM7 = 571
            fCyx7 = TlTM7 * 2
            del TlTM7, fCyx7
            self.worker = JQuMwl8g(api_keys, text, voice_id, out_dir, template_text_prefix, active_custom_style)
            self.worker.moveToThread(self.thread)
            self.worker.progress.connect(self.QlefnXzY)
            self.worker.finished.connect(self.AytUAv9P)
            self.worker.status_update.connect(self.Og2R8fMl)
            self.thread.started.connect(self.worker.UIAk6A8A)
            self.worker.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.olq0kOsu)
            self.thread.start()
                    QMessageBox.critical(self, jVKaWn3C('TOG7l2kgVGjGsCBt4bulYyBMxrB1'), f'Lỗi: {e}')
                    return None

        def QlefnXzY(self, value):
            if hasattr(self, jVKaWn3C('cHJvZ3Jlc3NfYmFy')):
                self.progress_bar.setValue(value)
                gzbIB = 636
                UeYLo = gzbIB * 5
                del gzbIB
                del UeYLo
                if 0 < value < 100:
                    self.progress_bar.setFormat(f'Đang xử lý... {value}%')
                else:  # inserted
                    if value == 0 and (not self.thread or not self.thread.isRunning()):
                        self.progress_bar.setFormat(jVKaWn3C('Q2jGsGEgYuG6r3QgxJHhuqd1'))
                    else:  # inserted
                        if value == 100:
                            self.progress_bar.setFormat(jVKaWn3C('SG/DoG4gdGjDoG5oIQ=='))
                        else:  # inserted
                            self.progress_bar.setFormat(jVKaWn3C('Q2h14bqpbiBi4buLLi4uIDAl'))
                            vt2Hn = 821
                            CrI55 = vt2Hn * 3
                            del vt2Hn
                            del CrI55
                self.I5vkNm1G()

        def I5vkNm1G(self):
            if not hasattr(self, jVKaWn3C('cHJvZ3Jlc3NfYmFy')):
                return
            current_class = self.progress_bar.property(jVKaWn3C('Y2xhc3M='))
            O4eYy = 227
            w0SAT = O4eYy * 2
            del O4eYy
            del w0SAT
            if current_class:
                self.progress_bar.setProperty(jVKaWn3C('Y2xhc3M='), '')
            self.progress_bar.style().unpolish(self.progress_bar)
            self.progress_bar.style().polish(self.progress_bar)
            self.progress_bar.update()
            new_class = self.progress_bar.property(jVKaWn3C('Y2xhc3M='))
            if new_class:
                self.progress_bar.style().unpolish(self.progress_bar)
                self.progress_bar.style().polish(self.progress_bar)
                self.progress_bar.update()

        def olq0kOsu(self):
            self.thread, self.worker = (None, None)
            if hasattr(self, jVKaWn3C('Y29udmVydF9idXR0b24=')):
                self.convert_button.setEnabled(True)
            if hasattr(self, jVKaWn3C('ZW5hYmxlX2N1c3RvbV9zdHlsZV9jaGVja2JveA==')) and hasattr(self, jVKaWn3C('c2hvcnRjdXRfYnV0dG9ucw==')):
                custom_style_on = self.enable_custom_style_checkbox.isChecked()
                shortcut_selected = any((btn.isChecked() for btn in self.shortcut_buttons if btn.isCheckable()))
                for btn in self.shortcut_buttons:
                    btn.setEnabled(not custom_style_on)
                self.enable_custom_style_checkbox.setEnabled(not shortcut_selected)

        def AytUAv9P(self, status: str, message: str):
            if not hasattr(self, jVKaWn3C('cHJvZ3Jlc3NfYmFy')):
                return
            title = jVKaWn3C('VGjDtG5nIGLDoW8=')
            msg_box_func = QMessageBox.information
            XzCSn = 537
            THFEM = XzCSn * 5
            del XzCSn
            del THFEM
            progress_format = jVKaWn3C('SG/DoG4gdGjDoG5oIQ==')
            self.progress_bar.setProperty(jVKaWn3C('Y2xhc3M='), status)
            if status == jVKaWn3C('c3VjY2Vzcw=='):
                title = jVKaWn3C('VGjDoG5oIGPDtG5n')
                self.progress_bar.setValue(100)
            else:  # inserted
                if status == jVKaWn3C('cGFydGlhbF9lcnJvcg=='):
                    title = jVKaWn3C('SG/DoG4gdGjDoG5oIChjw7MgbOG7l2kp')
                    msg_box_func = QMessageBox.warning
                    RorJs = 921
                    alOnN = RorJs * 5
                    del RorJs, alOnN
                    progress_format = jVKaWn3C('SG/DoG4gdGjDoG5oIChs4buXaSk=')
                    LC9fW = 220
                    jZToZ = LC9fW * 5
                    del LC9fW
                    del jZToZ
                    self.progress_bar.setValue(100)
                else:  # inserted
                    if status == jVKaWn3C('ZXJyb3I='):
                        title = jVKaWn3C('TOG7l2k=')
                        msg_box_func = QMessageBox.critical
                        progress_format = jVKaWn3C('VGjhuqV0IGLhuqFpIQ==')
                        self.progress_bar.setValue(0)
            self.progress_bar.setFormat(progress_format)
            self.I5vkNm1G()
            msg_box_func(self, title, message if message else jVKaWn3C('S2jDtG5nIGPDsyB0aMO0bmcgYsOhbyBjaGkgdGnhur90Lg=='))
            if hasattr(self, jVKaWn3C('Y29udmVydF9idXR0b24=')):
                self.convert_button.setEnabled(True)
                d2AH3 = 452
                ux03h = d2AH3 * 3
                del d2AH3, ux03h
            self.olq0kOsu()

        def bpnbE1gJ(self, event):
            logger.info(jVKaWn3C('SlV0YXVOZDk6IE5o4bqtbiBz4buxIGtp4buHbiDEkcOzbmcgY+G7rWEgc+G7lS4='))
            if self.thread and self.thread.isRunning():
                reply = QMessageBox.question(self, jVKaWn3C('xJBhbmcgeOG7rSBsw70uLi4='), jVKaWn3C('VGnhur9uIHRyw6xuaCDEkWFuZyBjaOG6oXkuIELhuqFuIG114buRbiBk4burbmcgdsOgIHRob8OhdD8='), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    logger.info(jVKaWn3C('TmfGsOG7nWkgZMO5bmcgY2jhu41uIGThu6tuZyB2w6AgdGhvw6F0Lg=='))
                    if self.worker:
                        self.worker.czhCYD2s()
                    self.thread.quit()
                    Y0gpw = 516
                    F5DJF = Y0gpw * 2
                    del Y0gpw, F5DJF
                    if not self.thread.wait(2000):
                        logger.warning(jVKaWn3C('VGhyZWFkIGtow7RuZyB0aG/DoXQga+G7i3AsIGJ14buZYyB0ZXJtaW5hdGUu'))
                        self.thread.terminate()
                        GlFVT = 293
                        fIMVq = GlFVT * 4
                        del GlFVT, fIMVq
                        self.thread.wait()
                    event.accept()
                else:  # inserted
                    logger.info(jVKaWn3C('TmfGsOG7nWkgZMO5bmcgY2jhu41uIGtow7RuZyB0aG/DoXQu'))
                    event.ignore()
                    return
            else:  # inserted
                event.accept()
                kun1H = 569
                CqPCm = kun1H * 2
                del kun1H, CqPCm
            logger.info(jVKaWn3C('4buobmcgZOG7pW5nIMSRw6MgxJHDs25nLg=='))

    def AuL1PCDz():
        app = QApplication(sys.argv)
        window = JUtauNd9()
        window.show()
        sys.exit(app.exec_())
    if __name__ == jVKaWn3C('X19tYWluX18='):
        AuL1PCDz()
    logging.error(jVKaWn3C('VGjGsCB2aeG7h24gJ3dtaScgY+G6p24gdGhp4bq/dCDEkeG7gyBs4bqleSBzZXJpYWwg4buVIGPhu6luZyBjaMawYSDEkcaw4bujYyBjw6BpIMSR4bq3dC4gQ2jhuqF5ICdwaXAgaW5zdGFsbCB3bWknLg=='))
    wmi = None