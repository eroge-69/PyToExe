import sys
import ctypes
import binascii

class bp25_struct(ctypes.LittleEndianStructure):
    # struct bp25_struct
    # {
    #     uint8_t start
    #     uint16_t len
    #     uint8_t cmd
    #     uint8_t reserve1[8]
    #     uint8_t fall_log
    #     uint8_t reserve2
    #     uint8_t lock_key[2]
    #     uint8_t reserve3[8]
    #     uint16_t impact
    #     uint16_t small_impact
    #     uint16_t area
    #     uint16_t fall_th
    #     uint16_t fall_dur
    #     uint8_t xor_code
    #     uint8_t end
    # }
    _pack_ = 1
    _fields_ = [
        ("start", ctypes.c_ubyte), 
        ("len", ctypes.c_ushort),
        ("cmd", ctypes.c_ubyte),
        ("reserve1", ctypes.c_ubyte * 8),
        ("fall_log", ctypes.c_ubyte),
        ("reserve2", ctypes.c_ubyte),
        ("lock_key", ctypes.c_ubyte * 2),
        ("reserve3", ctypes.c_ubyte * 8),
        ("large_impact", ctypes.c_ushort),
        ("small_impact", ctypes.c_ushort),
        ("impact_area", ctypes.c_ushort),
        ("fall_th", ctypes.c_ushort),
        ("fall_dur", ctypes.c_ushort),
        ("xor_code", ctypes.c_ubyte),
        ("end", ctypes.c_ubyte)
    ]

def get_xor_code(bytes) -> int:
    xor = 0
    for byte in bytes:
        xor ^= byte
    return xor

def cmd_gen_fall_pack():
    print("Please input large impact: 0 ~ 16 unit:G")
    large_impact = float(input("large impact : "))
    print("Please input small impact: 0 ~ 16 unit:G")
    small_impact = float(input("small impact : "))
    print("Please input impact area: 0 ~ 65535 unit:G*ms")
    impact_area = float(input("impact area : "))
    print("Please input fall threshold: 0 ~ 1 unit:G")
    fall_threshold = float(input("impact area : "))
    print("Please input fall duration: 0 ~ 65535 unit:ms")
    fall_duration = float(input("fall duration : "))
    print("Please input fall log type: lite, full, none")
    fall_log = str(input("fall log : "))

    bp25_t = bp25_struct()
    bp25_t.large_impact = int(large_impact / 0.00025 + 0.5)
    bp25_t.small_impact = int(small_impact / 0.00025 + 0.5)
    bp25_t.impact_area = int(impact_area + 0.5)
    bp25_t.fall_th = int(fall_threshold / 0.00025 + 0.5)
    bp25_t.fall_dur = int(fall_duration + 0.5)

    if fall_log == "lite":
        bp25_t.fall_log = 0x6F
    elif fall_log == "full":
        bp25_t.fall_log = 0xF6
    else:
        bp25_t.fall_log = 0x00

    bp25_t.start = 0x02
    bp25_t.len = ctypes.sizeof(bp25_t) - 3
    bp25_t.cmd = 0x5A
    ctypes.memset(bp25_t.reserve1, 0x00, ctypes.sizeof(bp25_t.reserve1))
    bp25_t.lock_key[0] = 0x50
    bp25_t.lock_key[1] = 0x44
    ctypes.memset(bp25_t.reserve3, 0x00, ctypes.sizeof(bp25_t.reserve3))
    xor_data = ctypes.string_at(ctypes.addressof(bp25_t), ctypes.sizeof(bp25_t) - 2)
    bp25_t.xor_code = get_xor_code(bytearray(xor_data))
    bp25_t.end = 0x03
    raw_data = ctypes.string_at(ctypes.addressof(bp25_t), ctypes.sizeof(bp25_t))
    hex_str = binascii.b2a_hex(raw_data).upper().decode('utf-8')
    print(f"\n Result:\n\t {hex_str}")

    return

def ap00_parse_param(pack: bytes) -> int:
    ''' 
    IWAP00862022102714301,01,1.73,1C0000A60000000000000050440080000000005CFF577A41512A00C10D2600#
    mcu_ver                [0]
    reserve1[2]            [2]
    high_g_int             [3]
    reserve2[5]            [8]
    reserve3               [9]
    fall_log               [10]
    lock_key[2]            [12]
    reserve4               [13]
    limit_times            [14]
    reserve5[4]            [18]
    limit_flag             [19]
    limit_cnt              [20]
    impact_th              [22]
    small_impact_th        [24]
    small_impact_area      [26]
    fall_th                [28]
    fall_dur               [30]
    '''
    if len(pack) != 31:
        print("error AP00 package size")
        return -1

    if pack[10] == 0x6F:
        print("fall log:\tlite")
    elif pack[10] == 0xF6:
        print("fall log:\tfull")
    else:
        print("fall log:\tnone")

    large_impact = (pack[22] << 8 | pack[21]) * 0.00025
    small_impact = (pack[24] << 8 | pack[23]) * 0.00025
    impact_area = pack[26] << 8 | pack[25]
    fall_th = (pack[28] << 8 | pack[27]) * 0.00025
    fall_dur = pack[30] << 8 | pack[29]
    print("large impact:\t", large_impact)
    print("small impact:\t", small_impact)
    print("impact area:\t", impact_area)
    print("fall threshold:\t", fall_th)
    print("fall duration:\t", fall_dur)

    return 0

def ap26_parse_param(pack: bytes) -> int:
    ''' 
    IWAP26,822063,022200AB1E0000F00000000000000050440080000000005CFF409C30753700B0042C016503#
    start               [0]
    len                 [2]
    cmd                 [3]
    mcu_ver             [4]
    reserve1[2]         [6]
    high_g_int          [7]
    reserve2[5]         [12]
    fall_log            [13]
    reserve3            [14]
    lock_key[2]         [16]
    reserve4            [17]
    limit_times         [18]
    reserve5[4]         [22]
    limit_flag          [23]
    limit_cnt           [24]
    impact_th           [26]
    small_impact_th     [28]
    small_impact_area   [30]
    fall_th             [32]
    fall_dur            [34]
    xor_code            [35]
    end                 [36]
    '''
    if len(pack) != 37:
        print("error AP26 package size")
        return -1

    if pack[13] == 0x6F:
        print("fall log:\tlite")
    elif pack[13] == 0xF6:
        print("fall log:\tfull")
    else:
        print("fall log:\tnone")

    large_impact = (pack[26] << 8 | pack[25]) * 0.00025
    small_impact = (pack[28] << 8 | pack[27]) * 0.00025
    impact_area = pack[30] << 8 | pack[29]
    fall_th = (pack[32] << 8 | pack[31]) * 0.00025
    fall_dur = pack[34] << 8 | pack[33]
    print("large impact:\t", large_impact)
    print("small impact:\t", small_impact)
    print("impact area:\t", impact_area)
    print("fall threshold:\t", fall_th)
    print("fall duration:\t", fall_dur)

    return 0

def bp25_parse_param(pack: bytes) -> int:
    ''' 
    IWBP25,862022102714301,731620,0221005A0000000000000000000050440000000000000000409C30753700B0042C015A03#
    start               [0]
    len                 [2]
    cmd                 [3]
    reserve1[8]         [11]
    fall_log            [12]
    reserve3            [13]
    lock_key[2]         [15]
    reserve4[8]         [23]
    impact_th           [25]
    small_impact_th     [27]
    small_impact_area   [29]
    fall_th             [31]
    fall_dur            [33]
    xor_code            [34]
    end                 [35]
    '''
    if len(pack) != 36:
        print("error BP25 package size")
        return -1

    if pack[12] == 0x6F:
        print("fall log:\tlite")
    elif pack[12] == 0xF6:
        print("fall log:\tfull")
    else:
        print("fall log:\tnone")

    large_impact = (pack[25] << 8 | pack[24]) * 0.00025
    small_impact = (pack[27] << 8 | pack[26]) * 0.00025
    impact_area = pack[29] << 8 | pack[28]
    fall_th = (pack[31] << 8 | pack[30]) * 0.00025
    fall_dur = pack[33] << 8 | pack[32]
    print("large impact:\t", large_impact)
    print("small impact:\t", small_impact)
    print("impact area:\t", impact_area)
    print("fall threshold:\t", fall_th)
    print("fall duration:\t", fall_dur)

    return 0

def cmd_gen_fall_param():
    print("Please input package type: 1-AP00, 2-AP26, 3-BP25")
    pack_type = int(input("type: "))
    if pack_type < 1 or pack_type > 3:
        print("Are you ShyBoy???")
        return
    print("Please input package data")
    pack_str = str(input("data: "))
    pack_hex = bytes.fromhex(pack_str)
    if pack_type == 1:
        ap00_parse_param(pack_hex)
    elif pack_type == 2:
        ap26_parse_param(pack_hex)
    else:
        bp25_parse_param(pack_hex)
    return

cmd_dict = {
    1: cmd_gen_fall_pack,
    2: cmd_gen_fall_param
}

def main():
    print("+++++++++++++++++++++++ Usage ++++++++++++++++++++++++")
    print("+    1 : generate BP25 pakage from fall parameters   +")
    print("+    2 : parsing fall parameters from package        +")
    print("+    3 : parsing lite fall log                       +")
    print("+    4 : parsing full fall log                       +")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    try:
        cmd = int(input("Input command : "))
        if cmd in cmd_dict:
            cmd_dict[cmd]()
        else:
            print("Are you ShyBoy???")
    except:
        print("Are you ShyBoy???")
        sys.exit()

if __name__ == "__main__":
    main()