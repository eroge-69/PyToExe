import csv
import sys
import tkinter.filedialog
import struct
import obd.commands
import obd.protocols.protocol

pid_map = dict([
    (0, 'PID_WSPIERANE_PIDY'),
    (1, 'PID_CISNIENIE_PALIWA_NA_LISTWIE'),
    (2, 'PID_CISNIENIE_PALIWA_EMULOWANE'),
    (3, 'PID_CISNIENIE_MAP'),
    (4, 'PID_CISNIENIE_GAZU'),
    (5, 'PID_TEMPERATURA_GAZU'),
    (6, 'PID_TEMPERATURA_REDUKTORA'),
    (7, 'PID_TEMPERATURA_WEWNETRZNA'),
    (8, 'PID_OBROTY_SILNIKA'),
    (9, 'PID_NAPIECIE_ZASILANIA'),
    (10, 'PID_ETAP_AUTOKALIBRACJI'),
    (11, 'PID_STAN_SYSTEMU'),
    (12, 'PID_FLAGI_SYSTEMOWE'),
    (13, 'PID_KOMUNIKAT_AUTOKALIBRACJI'),
    (14, 'PID_WPG_WARTOSC_MIERZONA'),
    (15, 'PID_WPG_WSKAZANIE'),
    (16, 'PID_CZAS_WTRYSKU_BENZYNY_1'),
    (17, 'PID_CZAS_WTRYSKU_BENZYNY_2'),
    (18, 'PID_CZAS_WTRYSKU_BENZYNY_3'),
    (19, 'PID_CZAS_WTRYSKU_BENZYNY_4'),
    (20, 'PID_CZAS_WTRYSKU_BENZYNY_5'),
    (21, 'PID_CZAS_WTRYSKU_BENZYNY_6'),
    (22, 'PID_CZAS_WTRYSKU_BENZYNY_7'),
    (23, 'PID_CZAS_WTRYSKU_BENZYNY_8'),
    (24, 'PID_DAWKA_BENZYNY_1'),
    (25, 'PID_DAWKA_BENZYNY_2'),
    (26, 'PID_DAWKA_BENZYNY_3'),
    (27, 'PID_DAWKA_BENZYNY_4'),
    (28, 'PID_DAWKA_BENZYNY_5'),
    (29, 'PID_DAWKA_BENZYNY_6'),
    (30, 'PID_DAWKA_BENZYNY_7'),
    (31, 'PID_DAWKA_BENZYNY_8'),
    (32, 'PID_CZAS_WTRYSKU_GAZU_1'),
    (33, 'PID_CZAS_WTRYSKU_GAZU_2'),
    (34, 'PID_CZAS_WTRYSKU_GAZU_3'),
    (35, 'PID_CZAS_WTRYSKU_GAZU_4'),
    (36, 'PID_CZAS_WTRYSKU_GAZU_5'),
    (37, 'PID_CZAS_WTRYSKU_GAZU_6'),
    (38, 'PID_CZAS_WTRYSKU_GAZU_7'),
    (39, 'PID_CZAS_WTRYSKU_GAZU_8'),
    (40, 'PID_LAMBDA_1'),
    (41, 'PID_LAMBDA_2'),
    (42, 'PID_LAMBDA_1_WR'),
    (43, 'PID_LAMBDA_2_WR'),
    (44, 'PID_STFT_B1_PB'),
    (45, 'PID_STFT_B2_PB'),
    (46, 'PID_LTFT_B1_PB'),
    (47, 'PID_LTFT_B2_PB'),
    (48, 'PID_STFT_B1_LPG'),
    (49, 'PID_STFT_B2_LPG'),
    (50, 'PID_LTFT_B1_LPG'),
    (51, 'PID_LTFT_B2_LPG'),
    (52, 'PID_STATUS_PETLI_PALIWOWEJ'),
    (53, 'PID_STATUS_POLACZENIA_OBD'),
    (54, 'PID_ZMIENNE_KALIBRACYJNE_dummy'),
    (55, 'PID_TEMPERATURA_SPALIN'),
    (56, 'PID_PEDAL_PRZYSPIESZENIA'),
    (57, 'PID_KNOCK_SENSOR'),
    (58, 'PID_FLAGI_UAKTUALNIENIA'),
    (59, 'PID_UDZIAL_DIESLA'),
    (60, 'PID_ODCHYLKA_LAMBDY'),
    (61, 'PID_KONFIGURACJA_WSKAZNIKOW'),
    (62, 'PID_PALIWO_CR_WIDOCZNE'),
    (63, 'PID_LAMBDA_DIESEL'),
    (64, 'PID_POSTEP_AUTOKALIBRACJI'),
    (65, 'PID_SYGN_OBCIAZENIE_SILNIKA'),
    (66, 'PID_ZADANY_KWZ'),
    (67, 'PID_NAP_PK_PK_CKP'),
    (68, 'PID_NAP_POTENCJOMETRU'),
    (69, 'PID_SYGN_NAPIECIOWY_ROZ'),
    (70, 'PID_OBCIAZENIE_SILNIKA'),
    (71, 'PID_FLAGI_SYSTEMOWE_NEW'),
    (72, 'PID_TEMPERATURA_SILNIKA_EMULOWANA'),
    (73, 'PID_ILOSC_WTRYSKOW'),
    (74, 'PID_CZAS_IMPULSU_1'),
    (75, 'PID_CZAS_IMPULSU_2'),
    (76, 'PID_CZAS_IMPULSU_3'),
    (77, 'PID_CZAS_IMPULSU_4'),
    (78, 'PID_DAWKA_ON'),
    (79, 'PID_OBECNY_KWZ'),
    (80, 'PID_RZECZYWISTY_KWZ'),
    (81, 'PID_EMULOWANY_KWZ'),
    (82, 'PID_LICZNIKI_ZUZYCIA_GAZU'),
    (83, 'PID_ISA2'),
    (84, 'PID_FAZA_WALKA_1'),
    (85, 'PID_FAZA_WALKA_2'),
    (86, 'PID_ISA2_STFT_BANK1'),
    (87, 'PID_ISA2_STFT_BANK2'),
    (88, 'PID_ISA2_CHWILOWA_ODCH_BANK1'),
    (89, 'PID_ISA2_CHWILOWA_ODCH_BANK2'),
    (90, 'PID_OBD_ADAPT_STFT_BANK1'),
    (91, 'PID_OBD_ADAPT_LTFT_BANK1'),
    (92, 'PID_OBD_ADAPT_STFT_BANK2'),
    (93, 'PID_OBD_ADAPT_LTFT_BANK2'),
    (94, 'PID_OBD_ADAPT_WYP_KOR_BANK1_APP'),
    (95, 'PID_OBD_ADAPT_WYP_KOR_BANK2_APP'),
    (96, 'PID_CISNIENIE_PALIWA_NA_LISTWIE2'),
    (97, 'PID_CISNIENIE_PALIWA_EMULOWANE2'),
    (98, 'PID_KNOCK_SENSOR1'),
    (99, 'PID_KNOCK_SENSOR2'),
    (100, 'PID_GC_TOTAL_TIME'),
    (101, 'PID_GC_DAILY_TIME'),
    (102, 'PID_GC_SINCE_REFUEL'),
    (103, 'PID_GC_INST_TIME'),
    (104, 'PID_NAPIECIE_AUX'),
    (105, 'PID_NAPIECIE_STER_POMPY_BENZ'),
    (106, 'PID_LAMBDA_EMULOWANA'),
    (107, 'PID_STATUS_IGL'),
    (108, 'PID_CISNIENIE_BENZYNY'),
    (109, 'PID_OBD_ADAPT_WYP_KOR_BANK1'),
])

def get_int(ar):
    return int.from_bytes(ar, byteorder='big', signed=False)

def get_double(ar):
    return struct.unpack('>d', ar)[0]

graphdata = None
frame_labels = None
obd_keys = []
sum_labels_added = False  # kontrola, żeby nie dodać wiele razy

def process_chunk(type, dataA, dataB):
    global graphdata, frame_labels, obd_keys, sum_labels_added

    if type == 2:  # graph data
        frame_labels = []
        frame_format = []

        for i in range(0, len(dataA) // 10):
            offset = i * 10
            id = dataA[offset]
            size = dataA[offset+9]
            if size == 0:
                continue
            name = pid_map.get(id, "UNKNOWN_" + str(id))
            multipier = get_double(dataA[offset+1:offset+9])
            if multipier == 0.0:
                multipier = 1.0
            frame_labels.append(name)
            frame_format.append((size, multipier))
        
        graphdata = []
        offset = 0
        while offset < len(dataB):
            s = []
            for entry in frame_format:
                s.append(get_int(dataB[offset:offset+entry[0]]) * entry[1])
                offset += entry[0]
            graphdata.append(s)

    if type == 10:  # OBD data
        if graphdata is None:
            return

        lastframe = 0
        lastcontent = []
        offset = 0

        while offset < len(dataB):
            frame = min(get_int(dataB[offset:offset+4]), len(graphdata))
            size = dataB[offset+4]
            offset += 5
            pakend = offset + size
            s = {}
            while offset < pakend:
                pid = dataB[offset]
                pidsize = dataB[offset+1]
                s[pid] = dataB[offset+2:offset+2+pidsize]
                offset += 2 + pidsize

            for pid in s.keys():
                if pid not in obd_keys:
                    obd_keys.append(pid)
                    if obd.commands.has_pid(1, pid):
                        frame_labels.append("OBD " + obd.commands[1][pid].name)
                    else:
                        frame_labels.append("OBD PID" + str(pid))

            # dodaj dodatkowe kolumny dla sum korekt (tylko raz)
            if not sum_labels_added:
                frame_labels.append("OBD SUM_FUELTRIM_B1")
                frame_labels.append("OBD SUM_FUELTRIM_B2")
                sum_labels_added = True

            row = []
            for pid in obd_keys:
                value = s.get(pid, None)
                if value is None:
                    row.append(None)
                    continue

                decoded_value = None
                try:
                    libdata = bytearray([1, pid])
                    libdata.extend(value)
                    if obd.commands.has_pid(1, pid):
                        msg = obd.protocols.protocol.Message([])
                        msg.data = libdata
                        decoded = obd.commands[1][pid].decode([msg])
                        if hasattr(decoded, 'magnitude'):
                            decoded_value = decoded.magnitude
                        elif isinstance(decoded, tuple):
                            decoded_value = decoded[0]
                        else:
                            decoded_value = decoded
                except Exception:
                    decoded_value = None

                # ręczne dekodowanie STFT/LTFT i kilku podstawowych PID
                if decoded_value is None:
                    A = value[0]
                    B = value[1] if len(value) > 1 else 0
                    if pid in [0x06, 0x07, 0x08, 0x09]:
                        decoded_value = (A - 128) * 100.0 / 128.0
                    elif pid == 0x0C:  # RPM
                        decoded_value = ((A * 256) + B) / 4
                    elif pid == 0x0D:  # Speed
                        decoded_value = A
                    elif pid == 0x11:  # Throttle
                        decoded_value = A * 100.0 / 255.0
                    else:
                        decoded_value = int.from_bytes(value, "big")

                row.append(decoded_value)

            # suma korekt
            stft_b1 = row[obd_keys.index(0x06)] if 0x06 in obd_keys else None
            ltft_b1 = row[obd_keys.index(0x07)] if 0x07 in obd_keys else None
            stft_b2 = row[obd_keys.index(0x08)] if 0x08 in obd_keys else None
            ltft_b2 = row[obd_keys.index(0x09)] if 0x09 in obd_keys else None

            sum_b1 = stft_b1 + ltft_b1 if (stft_b1 is not None and ltft_b1 is not None) else None
            sum_b2 = stft_b2 + ltft_b2 if (stft_b2 is not None and ltft_b2 is not None) else None

            row.append(sum_b1)
            row.append(sum_b2)

            for j in range(lastframe, frame):
                graphdata[j].extend(lastcontent)
            lastframe = frame
            lastcontent = row

        for j in range(lastframe, len(graphdata)):
            graphdata[j].extend(lastcontent)

def process_data(data):
    magic = data[:8].decode('utf-8')
    if magic != 'Ugic_Osc':
        raise Exception('bad magic')
    if data[8] != 1:
        raise Exception('unsupported version')

    chunks_count = data[10]
    checksum_read = data[11]
    checksum_actual = sum(data[12:]) & 0xff
    if checksum_read != checksum_actual:
        raise Exception("invalid checksum")

    offset = 12
    for i in range(chunks_count):
        type = data[offset]
        offset += 1
        lenA = get_int(data[offset:offset+2]); offset += 2
        dataA = data[offset:offset+lenA]; offset += lenA
        lenB = get_int(data[offset:offset+4]); offset += 4
        dataB = data[offset:offset+lenB]; offset += lenB
        process_chunk(type, dataA, dataB)

    if offset != len(data):
        raise Exception("invalid file, trailing data after all chunks")

if len(sys.argv) > 1:
    input = sys.argv[1]
else:
    input = tkinter.filedialog.askopenfilename(filetypes=[('Ugic .osc files', '.osc')])

with open(input, 'rb') as f:
    data = bytearray(f.read())
    process_data(data)

    if graphdata is None:
        raise Exception('invalid file, graph data missing')
    
    with open(input + ".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(frame_labels)
        for row in graphdata:
            writer.writerow(row)
