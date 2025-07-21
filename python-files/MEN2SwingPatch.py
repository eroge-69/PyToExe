import os, sys, time

def crc16_ccitt(data):
	crc = 0x0
	for byte in data:
		crc ^= byte << 8
		for _ in range(8):
			if crc & 0x8000:
				crc = crc << 1 ^ 0x1021
			else:
				crc <<= 1
			crc &= 0xFFFF
	return crc

original = open(sys.argv[1], "rb")
bytearr = bytearray(original.read())
original.close()

fazit = bytearr[0x100:0x100+0x17]
vcrn = bytearr[0x224C:0x224C+0x5]
train = bytearr[0x1414:0x1414+0x15]

print("Train:", train.decode())
print("FAZIT:", fazit.decode())
print("VCRN:", vcrn.hex().upper())

vin = 'TMBAE6NH7J4565086'.encode() # VIN can be any
timestamp = int(time.time()).to_bytes(4,'big') # timestamp can be any too

# Position and SWaP 
swaps_positions = [
	(0x2280, 0x22C0, b'\x00\x06\x03\x00'),
	(0x2290, 0x2380, b'\x00\x06\x08\x00'),
	(0x22A0, 0x1C40, b'\x00\x06\x09\x00'),
	(0x22B0, 0x1D00, b'\x00\x06\x01\x00'),
	(0x4BC0, 0x4C00, b'\x00\x06\x03\x00'),
	(0x4BD0, 0x4CC0, b'\x00\x06\x08\x00'),
	(0x4BE0, 0x4580, b'\x00\x06\x09\x00'),
	(0x4BF0, 0x4640, b'\x00\x06\x01\x00'),
	(0x7500, 0x7540, b'\x00\x06\x03\x00'),
	(0x7510, 0x7600, b'\x00\x06\x08\x00'),
	(0x7520, 0x6EC0, b'\x00\x06\x09\x00'),
	(0x7530, 0x6F80, b'\x00\x06\x01\x00'),
]

for position1, position2, swap in swaps_positions:
	pattern1 = b'\x00\x00\x00\x00\x00\x00' + swap + timestamp + b'\xFF\x01'
	pattern2 = b'\x11\x02' + swap + b'\x03' + vcrn + vin + b'\x00' + timestamp + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	bytearr[position1:position1+len(pattern1)] = pattern1
	bytearr[position2:position2+len(pattern2)] = pattern2

# Recalculate checksums
checksums = bytearray()
for start in range(0x0000, 0x7BBF, 0x40):
	checksums += int.to_bytes(crc16_ccitt(bytearr[start:start+0x40]), 2, 'little')

bytearr[0x7C00:0x7C00 + len(checksums)] = checksums

patched_filename = sys.argv[1] + "_patched.bin"

patched = open(patched_filename, "wb")
patched.write(bytearr)
patched.close()

print("Patched bin saved to", patched_filename);

# os.system("pause")