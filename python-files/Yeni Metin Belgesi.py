import comtypes
import ctypes
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from comtypes.client import CreateObject

# Core Audio API GUID’leri
CLSID_MMDeviceEnumerator = '{BCDE0395-E52F-467C-8E3D-C4579291692E}'
IID_IMMDeviceEnumerator = '{A95664D2-9614-4F35-A746-DE8DB63617E6}'
IID_IMMDevice = '{D666063F-1587-4E43-81F1-B948E807363F}'
IID_IPolicyConfigVista = '{568b9108-44bf-40b4-9006-86afe5b5a620}'

# PolicyConfig arayüzü
class IPolicyConfigVista(comtypes.IUnknown):
    _iid_ = ctypes.GUID(IID_IPolicyConfigVista)
    _methods_ = [
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetMixFormat'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetDeviceFormat'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetDeviceFormat'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetProcessingPeriod'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetProcessingPeriod'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetShareMode'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetShareMode'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetPropertyValue'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetPropertyValue'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetDefaultEndpoint',
                         (['in'], ctypes.LPWSTR),
                         (['in'], ctypes.c_int)),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'SetEndpointVisibility'),
    ]

# IMMDevice arayüzü
class IMMDevice(comtypes.IUnknown):
    _iid_ = ctypes.GUID(IID_IMMDevice)
    _methods_ = [
        ctypes.COMMETHOD([], ctypes.HRESULT, 'Activate'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'OpenPropertyStore'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetId',
                         (['out'], ctypes.POINTER(ctypes.LPWSTR))),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetState')
    ]

# IMMDeviceEnumerator arayüzü
class IMMDeviceEnumerator(comtypes.IUnknown):
    _iid_ = ctypes.GUID(IID_IMMDeviceEnumerator)
    _methods_ = [
        ctypes.COMMETHOD([], ctypes.HRESULT, 'EnumAudioEndpoints'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetDefaultAudioEndpoint'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'GetDevice',
                         (['in'], ctypes.LPWSTR),
                         (['out'], POINTER(POINTER(IMMDevice)))),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'RegisterEndpointNotificationCallback'),
        ctypes.COMMETHOD([], ctypes.HRESULT, 'UnregisterEndpointNotificationCallback'),
    ]

# Hedef cihaz ismi
TARGET_DEVICE = "Hoparlör (Realtek(R) Audio)"

def set_default_audio_device(device_name):
    enumerator = CreateObject(CLSID_MMDeviceEnumerator, interface=IMMDeviceEnumerator)
    devices = enumerator.EnumAudioEndpoints(0, 1)  # eRender = 0, DEVICE_STATE_ACTIVE = 1
    collection = devices[0]
    count = collection.GetCount()

    for i in range(count):
        device = collection.Item(i)
        id_str = device.GetId()
        props = device.OpenPropertyStore(0)
        prop_value = props.GetValue(ctypes.byref(ctypes.GUID("{b3f8fa53-0004-438e-9003-51a46e139bfc}"), 14))
        name = prop_value.pwszVal
        if device_name.lower() in name.lower():
            policy = CreateObject(CLSID_MMDeviceEnumerator, interface=IPolicyConfigVista)
            policy.SetDefaultEndpoint(id_str, 0)  # eConsole
            policy.SetDefaultEndpoint(id_str, 1)  # eMultimedia
            policy.SetDefaultEndpoint(id_str, 2)  # eCommunications
            print(f"[OK] Varsayılan ses çıkışı değiştirildi: {name}")
            return True
    print("[HATA] Cihaz bulunamadı.")
    return False

if __name__ == "__main__":
    set_default_audio_device(TARGET_DEVICE)
