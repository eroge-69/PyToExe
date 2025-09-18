# Note: The SysEx message below is an example and may not be exact.
# You MUST consult the MODX Data List for the correct addresses and formats.
# Make sure to install the library first: pip install mido python-rtmidi

import mido
import time

# The SysEx message to change the name of Slot 1 on Page 1
# F0 (Start) 43 (Yamaha) 10 (Param Change) 7F 1C (MODX) ... (Address) ... (Data) ... F7 (End)
# This is a simplified representation.
slot_name = "My Python Pad"
encoded_name = [ord(c) for c in slot_name] # Convert string to ASCII bytes

# Construct the SysEx message (addresses are hypothetical)
# [Start, Manu ID, Group ID, Model ID, Addr High, Addr Mid, Addr Low, Data..., End]
sys_ex_msg = [
    0xF0, 0x43, 0x10, 0x7F, 0x1C,  # Standard Header
    0x60, 0x02, 0x0C,              # Example address for Live Set Slot 1 Name
    *encoded_name,                 # The actual name data
    0xF7                           # End of Exclusive
]

try:
    # 1. Find the MODX MIDI port
    modx_port_name = None
    for name in mido.get_output_names():
        if 'MODX' in name:
            modx_port_name = name
            break
    
    if not modx_port_name:
        raise IOError("MODX port not found. Is it connected and turned on?")

    print(f"Found MODX on port: {modx_port_name}")

    # 2. Open the port and send the message
    with mido.open_output(modx_port_name) as out_port:
        msg = mido.Message('sysex', data=sys_ex_msg[1:-1]) # mido adds F0 and F7
        print(f"Sending SysEx message: {msg}")
        out_port.send(msg)
        print("Message sent! Check your MODX screen.")

except Exception as e:
    print(f"An error occurred: {e}")