#!/usr/bin/env python3

import serial
import struct
import sys

with serial.Serial(sys.argv[1], 115200) as ser:
	while True:
		pkt = ser.read(10)
		#print("PKT: ", pkt)
		status_disp, r_range_code, r_disp, sign_code, v_range_code, v_disp = struct.unpack('BB3s BB3s', pkt)
				
		#print(f"status_disp='{status_disp:#x}'")

		r_disp = struct.unpack('I', r_disp + b'\x00')[0]
		resistance = float(r_disp) / 1e4

		r_disp_code = (status_disp & 0xF0) >> 4

		if r_disp_code == 0x05:
			r_unit_disp = 'mΩ'
		elif r_disp_code == 0x06:
			r_unit_disp = 'mΩ'
			resistance = 'OL'
		elif r_disp_code == 0x09:
			r_unit_disp = 'Ω'
		elif r_disp_code == 0x0a:
			r_unit_disp = 'Ω'
			resistance = 'OL'
		else:
			print(f"Unknown display code '{r_status_disp_code:#x}'")

		#print(f"r_disp_code='{r_disp_code:#x}' r_unit_disp='{r_unit_disp}'")

		r_unit = r_unit_disp

		if r_range_code == 1:
			r_range = '0-20 mΩ'
			r_range_unit = 'mΩ'
		elif r_range_code == 2:
			r_range = '0-200 mΩ'
			r_range_unit = 'mΩ'
		elif r_range_code == 3:
			r_range = '0-2 Ω'
			r_range_unit = 'Ω'
		elif r_range_code == 4:
			r_range = '0-20 Ω'
			r_range_unit = 'Ω'
		elif r_range_code == 5:
			r_range = '0-200 Ω'
			r_range_unit = 'Ω'
		elif r_range_code == 6:
			r_range = 'AUTO'
			r_range_unit = None
		else: 
			r_range = None
			r_range_unit = None
			print(f"Unknown resistance range code '{r_range_code:#x}'")

		if r_range_unit and r_unit_disp != r_range_unit:
			print(f"Display unit '{r_unit_disp}' override by range unit '{r_range_unit}' for selected range '{r_range}'")

			# Range unit has preference
			r_unit = r_range_unit
		
		print(f"RESISTANCE range='{r_range}' {resistance} {r_unit}")

		sign_multiplier = None
		if sign_code == 1:
			sign_multiplier = 1.0
		elif sign_code == 0:
			sign_multiplier = -1.0
		else:
			print(f"Unknown sign code '{sign_code:#x}'")

		v_disp = struct.unpack('I', v_disp + b'\x00')[0]
		voltage = sign_multiplier * float(v_disp) / 1e4

		v_disp_code = ( status_disp & 0x0F )
		if v_disp_code == 0x04:
			pass # Nop, everything is OK
		elif v_disp_code == 0x08:
			voltage = 'OL'

		if v_range_code == 1:
			v_range = '0-20 V'
		elif v_range_code == 2:
			v_range = '0-100 V'
		elif v_range_code == 3:
			v_range = 'AUTO'
		else:
			v_range = 'Unknown'
			print(f"Unknown voltage range code '{v_range_code:#x}'")

		#print(f"v_range_code='{v_range_code:#x}' v_range='{v_range}'")
		
		print(f"VOLTAGE range='{v_range}', {voltage} V")
