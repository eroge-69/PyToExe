import os
import serial
import threading
import time as tm
import msvcrt  # For Windows
from datetime import datetime
import sys
import os
from cryptography.fernet import Fernet
import time

FoTaCmd_Type = -1
total_packet = -1
packet_no = -1
DataReceived = 0
g_fileName =""
key = b'0S4RoXNk7jXQNCuO7amr8XAn8DxhYY3iziKQZeIBeQY='
fernet = Fernet(key)


def Create_Txt_file(FileName):
    with open(FileName, "w") as file:
        file.write("Logs are Recorded......\n\n")


def log_data(tag, data):
    """Thread-safe logging to file"""
    now = datetime.now()
    
    timestamp = now.strftime("%H:%M:%S")
    data = " ".join(f"{x:02X}" for x in data)

    # Combined log line
    log_line = f"[{timestamp}] [{tag}]: {data}"

    with open(g_fileName, "a") as file:
        file.write(log_line + "\n")

        


def keyboard_hit():
    return msvcrt.kbhit()

def read_key():
    return msvcrt.getwch()

def SerialRxTx_Print(Tx_Command):
    now = datetime.now()
    print(now.strftime("%H:%M:%S") ,"[TX]:", *[f"{x:02X}" for x in Tx_Command])

def bs_crc16_update(crc, a):
    crc ^= a
    for _ in range(8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc >>= 1
    return crc

def bs_compute_crc(data):
    crc = 0xFFFF
    for b in data:
        crc = bs_crc16_update(crc, b)
    return crc

def bs_convert_hex_to_ascii(crc, width):
    try:
        hex_str = f"{crc:0{width}X}"  # width=4, uppercase hex
        return [ord(c) for c in hex_str]
    except:
        return None

def cal_checksum(msg):
    return sum(msg) & 0xFF

def send_fota_reset_cmd(FoTa_File_Type):

    global total_packet
    global packet_no

    cmd_send = [0] * 26
    cmd_send[0] = 0x55
    cmd_send[1] = 0xAA
    cmd_send[2] = 0x00
    cmd_send[3] = 0x06
    cmd_send[4] = 0x00
    cmd_send[5] = 0x13  # Data length
    cmd_send[6] = 0x65
    cmd_send[7] = 0x03
    cmd_send[8] = 0x00
    cmd_send[9] = 0x0F
    cmd_send[10] = 0x2A
    cmd_send[11] = 0x30
    cmd_send[12] = 0x37
    cmd_send[13] = 0x36
    cmd_send[14] = 0x34
    cmd_send[15] = 0x30
    cmd_send[16] = 0x30
    cmd_send[17] = 0x30
    cmd_send[18] = FoTa_File_Type
    cmd_send[19] = 0x31
	
    # CRC calculation on cmd_send[10:20]
    crc = bs_compute_crc(cmd_send[10:20])
    crc_buf = bs_convert_hex_to_ascii(crc, 4)
	
    if crc_buf is None:
        print("CRC FAILED STATE CMD")
    else:
        cmd_send[20] = crc_buf[0]
        cmd_send[21] = crc_buf[1]
        cmd_send[22] = crc_buf[2]
        cmd_send[23] = crc_buf[3]
        cmd_send[24] = 0x23
        cmd_send[25] = cal_checksum(cmd_send[:25])
        # Print full command as hex for verification
        #print("Final CMD_SEND:", [f"{byte:02X}" for byte in cmd_send])
    return cmd_send


def send_fota_EOT_cmd(FoTa_File_Type):

    global total_packet
    global packet_no

    cmd_send = bytearray(18)
    cmd_send[0] = 0x55
    cmd_send[1] = 0xAA
    cmd_send[2] = 0x00
    cmd_send[3] = 0X73
    cmd_send[4] = 0X00
    cmd_send[5] = 0X0B
    cmd_send[6] = 0x30
    cmd_send[7] = 0x30
    cmd_send[8] = 0x30
    cmd_send[9] = FoTa_File_Type
    cmd_send[10] = ((total_packet >> 8) & 0xFF)
    cmd_send[11] = total_packet & 0xFF
    cmd_send[12] = 0x04
    cmd_send[13] = ((total_packet >> 8 ) & 0xFF)
    cmd_send[14] = (total_packet & 0xFF)
    packet_no_comliment = (~total_packet)
    cmd_send[15] = ((packet_no_comliment >> 8) & 0xff)
    cmd_send[16] = packet_no_comliment & 0xFF
    cmd_send[17] = cal_checksum(cmd_send[:17])
    
    return cmd_send

def send_fota_ETB_cmd(FoTa_File_Type):
    
    global total_packet
    global packet_no

    cmd_send = bytearray(18)
    cmd_send[0] = 0x55
    cmd_send[1] = 0xAA
    cmd_send[2] = 0x00
    cmd_send[3] = 0x73
    cmd_send[4] = 0x00
    cmd_send[5] = 0x0B
    cmd_send[6] = 0x30
    cmd_send[7] = 0x30
    cmd_send[8] = 0x30
    cmd_send[9] = FoTa_File_Type & 0xFF
    cmd_send[10] = ((total_packet >> 8) & 0xFF)
    cmd_send[11] = (total_packet & 0xFF)
    cmd_send[12] = 0x17
    cmd_send[13] = ((total_packet >> 8) & 0xFF)
    cmd_send[14] = (total_packet & 0xFF)
    total_packet_comliment = (~total_packet)
    cmd_send[15] = ((total_packet_comliment >> 8) & 0xFF)
    cmd_send[16] = total_packet_comliment & 0xFF
	
    cmd_send[17] = cal_checksum(cmd_send[:17])

    return cmd_send


def send_FW_CRC_cmd(FoTa_File_Type):

    global total_packet
    global packet_no

    cmd_send = bytearray(25)
    cmd_send[0] = 0x55
    cmd_send[1] = 0xAA
    cmd_send[2] = 0x00
    cmd_send[3] = 0x06

    cmd_send[4] = 0x00
    cmd_send[5] = 0x12

    cmd_send[6] = 0x65
    cmd_send[7] = 0x03

    cmd_send[8] = 0x00
    cmd_send[9] = 0x0E

    cmd_send[10] = 0x2A

    cmd_send[11] = 0x30
    cmd_send[12] = 0x36

    cmd_send[13] = 0x41
    cmd_send[14] = 0x41

    cmd_send[15] = 0x30
    cmd_send[16] = 0x30
    cmd_send[17] = 0x30
    cmd_send[18] = FoTa_File_Type


    # CRC calculation on cmd_send[10:20]
    crc = bs_compute_crc(cmd_send[10:19])
    crc_buf = bs_convert_hex_to_ascii(crc, 4)

    if crc_buf is None:
        print("CRC FAILED STATE CMD")
    else:
        cmd_send[19] = crc_buf[0]
        cmd_send[20] = crc_buf[1]
        cmd_send[21] = crc_buf[2]
        cmd_send[22] = crc_buf[3]
        cmd_send[23] = 0x23
        cmd_send[24] = cal_checksum(cmd_send[:24])

    return cmd_send
    


def send_soh_command(FoTa_File_Type,data):

    #print("Data Len:", len(data), "Data:", data)
    PacketLen = len(data)
    total_length = PacketLen + 20  # 17 bytes header + data + CRC + checksum

    cmd_send = bytearray(total_length)  # Properly sized bytearray

    cmd_send[0] = 0x55
    cmd_send[1] = 0xAA
    cmd_send[2] = 0x00
    cmd_send[3] = 0x73
    #print("Hello_4")

    data_length = PacketLen + 13

    cmd_send[4] = (data_length >> 8) & 0xFF
    cmd_send[5] = data_length & 0xFF
    cmd_send[6] = 0x30
    cmd_send[7] = 0x30
    cmd_send[8] = 0x30
    cmd_send[9] = FoTa_File_Type
    cmd_send[10] = (total_packet >> 8) & 0xFF
    cmd_send[11] = (total_packet & 0xFF)
    cmd_send[12] = 0x01
    cmd_send[13] = (packet_no >> 8) & 0xFF
    cmd_send[14] = (packet_no & 0xFF)
    packet_no_compliment = ~packet_no
    cmd_send[15] = (packet_no_compliment >> 8) & 0xFF
    cmd_send[16] = (packet_no_compliment & 0xFF)

    #print("Hello_1")

    cmd_send[17:17+PacketLen] = data[:PacketLen]  # Add payload
    #print("Hello_2")

    crc_in_hex = bs_compute_crc(cmd_send[17:17+PacketLen])  # CRC of payload only
    #print("Hello_3")

    cmd_send[17 + PacketLen] = (crc_in_hex >> 8) & 0xFF
    cmd_send[18 + PacketLen] = crc_in_hex & 0xFF

    checksum = cal_checksum(cmd_send[:19 + PacketLen])
    cmd_send[19 + PacketLen] = checksum & 0xFF  # Always keep bytes in 0-255 range

    #print("SOH Packet", cmd_send.hex())
    return cmd_send

def get_com_port():
    com_port = input("Enter COM port (e.g., COM3 or /dev/ttyUSB0): ").strip()
    if not com_port:
        raise ValueError("COM port cannot be empty.")
    return com_port

def get_baud_rate():
    while True:
        baud_input = input("Enter baud rate (e.g., 9600): ").strip()
        if baud_input.isdigit():
            return int(baud_input)
        else:
            print("Invalid baud rate. Please enter a numeric value.")

def get_input_file_path():
    while True:
        file_path = input("Enter full path to the input file: ").strip()
        if os.path.isfile(file_path):
            return file_path
        else:
            print("File does not exist. Please enter a valid path.")

def get_FoTa_file_type():
    while True:
        val =['1','2','4','8']
        value = input("Enter Value for type of file\nPress:\n1 for IDU EE\n2 for IDU Main\n4 for ODU EE\n8 for ODU Main:\n")
        if not value in val:
            print("Value out of Range. Please enter a valid value.")
        return (value)

def get_Product_type():
    while True:
        val =['3','4','6']
        user_inpt = input("Enter Below value for following Product Line\nPress:\n3 for Split-AC(SAC),Cascase-AC(CSAC), Multi Split AC(MSAC)\n4 for Logic Controller\n6 for Inverter Drive\n")
        if not user_inpt in val:
            print("Value out of Range. Please enter a valid value.")
        return (user_inpt)
    
def receive_data(ser):
    global DataReceived
    global g_fileName
    print("\n--- Starting to receive data from the device ---")
    while True:
        try:
            if ser.in_waiting > 0:
                DataReceived = 1
                tm.sleep(0.15) # wait for 100ms to get full packet
                response = ser.read(ser.in_waiting)
                if response:
                    now = datetime.now()
                    log_data("RX" , response)
                    print(now.strftime("%H:%M:%S") , "[RX]:", *[f"{x:02X}" for x in response])
                    DataReceived = 0
            tm.sleep(0.05)
        except serial.SerialException as e:
            print(f"\nSerial exception while receiving: {e}")
            break
        except Exception as e:
            print(f"\nError while receiving: {e}")
            break

def send_file_over_serial(com_port, baud_rate, file_path):
    global FoTaCmd_Type
    global total_packet
    global packet_no
    global DataReceived
    global g_fileName
    
    file_size = os.path.getsize(file_path)
    print(f"\nFile size: {file_size} bytes")

    if file_size > 1024:
        total_packet = file_size//1024
        if (file_size % 1024) != 0:
            total_packet = total_packet+1
        read_buf_len = 1024
    else:
        read_buf_len = file_size
        total_packet = 1

    packet_no = 0

    print("Size of File:",file_size,"Total Packets:",total_packet,"packet_no:",packet_no)

    try:
        with serial.Serial(com_port, baud_rate, timeout=1) as ser, open(file_path, 'rb') as file:
            # Start receiver thread
            recv_thread = threading.Thread(target=receive_data, args=(ser,), daemon=True)
            recv_thread.start()
            tm.sleep(0.2)  # Pause for 0.2 seconds

            print("************Press Below key of Transmit:******************          \n\
                    'r' for RESET COMMAND          \n\
                    '1' for CURRENT SOH          \n\
                    '2' for PREVIOUS SOH          \n\
                    '3' for EOT          \n\
                    '4' for ETB          \n\
                    'c' for Firmware CRC          \n\
                    'e' for QUIT")

            
            
            while True:
                if DataReceived == 1:
                    tm.sleep(1)
                    
                if keyboard_hit():
                    user_input = read_key()
                    print(f"[Key]: You pressed '{user_input}'")
                    if user_input.lower() == 'e':    # To stop program
                        print("--> EXIT")
                        break
                
                    elif user_input == 'r':             # Send Reset Commmand
                        Tx_Command = send_fota_reset_cmd(FoTaCmd_Type)
                        #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                        SerialRxTx_Print(Tx_Command)
                        log_data("TX" , Tx_Command)
                        ser.write(bytearray(Tx_Command))
                    
                    elif user_input == '2':             #Send Previous SOH
                        if packet_no != 0:
                            Tx_Command = send_soh_command(FoTaCmd_Type,chunk)
                            #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                            SerialRxTx_Print(Tx_Command)
                            log_data("TX" , Tx_Command)
                            ser.write(bytearray(Tx_Command))
                        else:
                            print("First Send The first Current packet")
                    
                    elif user_input == '1':             #Send Current SOH
                        
                        if packet_no < total_packet:
                            packet_no = packet_no + 1
                            file.seek((packet_no-1)*1024)
                            if packet_no == total_packet:
                                chunk_size = file_size - (packet_no-1)*1024
                            else:
                                chunk_size = 1024
                            chunk = file.read(chunk_size)

                        #print("Chunk:",chunk,"\n\nSize of Chunk",len(chunk))
                            
                        
                            Tx_Command = send_soh_command(FoTaCmd_Type,chunk)
                            #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                            SerialRxTx_Print(Tx_Command)
                            log_data("TX" , Tx_Command)
                            ser.write(bytearray(Tx_Command))

                        else:
                            print("You have reached the last packet, Now you can send only last packet by pressing key: 2 or restart the script")
                    
                    elif user_input == '3':             #Send EOT
                        Tx_Command = send_fota_EOT_cmd(FoTaCmd_Type)
                        #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                        SerialRxTx_Print(Tx_Command)
                        log_data("TX" , Tx_Command)
                        ser.write(bytearray(Tx_Command))
                    
                    elif user_input == '4':             #Send ETB
                        Tx_Command = send_fota_ETB_cmd(FoTaCmd_Type)
                        #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                        SerialRxTx_Print(Tx_Command)
                        log_data("TX" , Tx_Command)
                        ser.write(bytearray(Tx_Command))

                                            
                    elif user_input == 'c':             #Send ETB
                        Tx_Command = send_FW_CRC_cmd(FoTaCmd_Type)
                        #print("[TX]:", *[f"{x:02X}" for x in Tx_Command])
                        SerialRxTx_Print(Tx_Command)
                        log_data("TX" , Tx_Command)
                        ser.write(bytearray(Tx_Command))

                    

                tm.sleep(1)  # Pause for 1 seconds
            
                
                

    except KeyboardInterrupt:
        print("\nTerminated by user.")
    except serial.SerialException as e:
        print(f"\nSerial error: {e}")
    except Exception as e:
        print(f"\nError during file transfer: {e}")



def validate_license():
    if not os.path.exists("license.key"):
        print("License file not found. Please contact admin.")
        sys.exit(1)

    try:
        with open("license.key", "rb") as f:
            token = f.read()

        expiry = int(fernet.decrypt(token).decode())
        current_time = int(time.time())

        if current_time > expiry:
            print("License expired. Please request a new one.")
            sys.exit(1)
    except Exception as e:
        print("Invalid license file. Contact admin.")
        sys.exit(1)

def main():
    global FoTaCmd_Type
    global g_fileName

    # Call before any real work starts
    validate_license()
    try:
        com_port = get_com_port()
        print("\n")
        baud_rate = get_baud_rate()
        print("\n")
        input_file_path = get_input_file_path()
        print("\n")
        PCBType = int(get_Product_type())
        print("\n")
        FileType = int(get_FoTa_file_type())
        print("\n")
        

        print("\n--- Configuration ---")
        print(f"COM Port: {com_port}")
        print(f"Baud Rate: {baud_rate}")
        print(f"Input File: {input_file_path}")
        FoTaCmd_Type = ((((PCBType<<4)&0xFF) | FileType) & 0xFF)
        print(f"FoTa byte value: {FoTaCmd_Type:02X}")


        now = datetime.now()
        Time = now.strftime("%H%M%S")
        g_fileName = "Log_" + Time + ".txt"

        Create_Txt_file(g_fileName)


        send_file_over_serial(com_port, baud_rate, input_file_path)

        print("All the data are saved in text file: ",g_fileName,".................")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("________Version: 1.0.3________\n")
    main()
