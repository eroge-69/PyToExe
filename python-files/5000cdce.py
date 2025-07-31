#!/usr/bin/env python3
"""
DSU Client for reWASD -> ViGEm DS4 Bridge
Receives DSU protocol data from reWASD UDP server and emulates DS4 controller

Usage:
    python dsu_client.py

Requirements:
    pip install pyvigem
    Install ViGEmBus driver: https://github.com/nefarius/ViGEmBus/releases
"""

import socket
import struct
import zlib
import time
import threading
from typing import Optional, Dict, Any

try:
    from pyvigem.client import VigemClient
    from pyvigem.target import DS4Controller
    VIGEM_AVAILABLE = True
except ImportError:
    print("[!] pyvigem not installed. Run: pip install pyvigem")
    VIGEM_AVAILABLE = False

class DSUToDS4Bridge:
    """Bridge between reWASD DSU server and ViGEm DS4 controller"""
    
    # DSU Protocol Constants
    DSU_MAGIC = b"DSUS"
    DSU_VERSION = 1001
    DSU_MSG_CONTROLLER_DATA = 0x100002
    
    def __init__(self, rewasd_host: str = "127.0.0.1", rewasd_port: int = 26760):
        self.rewasd_host = rewasd_host
        self.rewasd_port = rewasd_port
        
        # Network
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        # ViGEm
        self.vigem_client: Optional[VigemClient] = None
        self.ds4_controller: Optional[DS4Controller] = None
        
        # Statistics
        self.packets_received = 0
        self.packets_processed = 0
        self.last_packet_time = 0
        
    def connect(self) -> bool:
        """Initialize UDP socket and ViGEm DS4 controller"""
        if not VIGEM_AVAILABLE:
            print("[!] ViGEm library not available")
            return False
            
        try:
            # Create UDP socket for receiving data
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(1.0)  # 1 second timeout for graceful shutdown
            self.socket.bind(("0.0.0.0", 0))  # Bind to any available port
            
            print(f"[+] UDP socket created, listening for data from {self.rewasd_host}:{self.rewasd_port}")
            
            # Initialize ViGEm
            self.vigem_client = VigemClient()
            self.vigem_client.connect()
            
            # Create virtual DS4 controller
            self.ds4_controller = DS4Controller(self.vigem_client)
            self.ds4_controller.connect()
            
            print("[+] Virtual DS4 controller connected via ViGEm")
            return True
            
        except Exception as e:
            print(f"[!] Failed to connect: {e}")
            self.disconnect()
            return False
    
    def parse_dsu_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parse DSU controller data packet according to cemuhook protocol"""
        if len(data) < 80:
            return None
            
        try:
            # Parse header (first 20 bytes)
            if not data.startswith(self.DSU_MAGIC):
                return None
                
            version = struct.unpack('<H', data[4:6])[0]
            packet_length = struct.unpack('<H', data[6:8])[0]
            crc32_received = struct.unpack('<I', data[8:12])[0]
            server_id = struct.unpack('<I', data[12:16])[0]
            msg_type = struct.unpack('<I', data[16:20])[0]
            
            # Validate protocol
            if version != self.DSU_VERSION:
                return None
                
            if msg_type != self.DSU_MSG_CONTROLLER_DATA:
                return None
                
            # Verify CRC32
            temp_data = bytearray(data)
            temp_data[8:12] = b'\x00\x00\x00\x00'
            calculated_crc = zlib.crc32(temp_data) & 0xffffffff
            if calculated_crc != crc32_received:
                return None
            
            # Parse controller data (from offset 20 onwards)
            # Based on cemuhook protocol specification
            return {
                'slot': data[20],
                'state': data[21],  # 0=disconnected, 2=connected
                'model': data[22],
                'connection_type': data[23],
                'mac': data[24:30].hex(),
                'battery': data[30],
                'connected': data[31] == 1,
                'packet_number': struct.unpack('<I', data[32:36])[0],
                
                # Button data
                'dpad_buttons': data[36],      # bits: left, down, right, up, options, r3, l3, share
                'face_buttons': data[37],      # bits: triangle, circle, cross, square, r1, l1, r2, l2
                'home_button': data[38],
                'touchpad_button': data[39],
                
                # Analog sticks (0-255, 128=center)
                'left_stick_x': data[40],
                'left_stick_y': data[41],
                'right_stick_x': data[42],
                'right_stick_y': data[43],
                
                # Analog triggers (found at different offsets)
                'left_trigger': data[54],      # L2 analog
                'right_trigger': data[55],     # R2 analog
                
                # Timestamp
                'timestamp': struct.unpack('<Q', data[48:56])[0],
            }
            
        except (struct.error, IndexError) as e:
            print(f"[!] Error parsing packet: {e}")
            return None
    
    def update_ds4_controller(self, controller_data: Dict[str, Any]) -> None:
        """Update ViGEm DS4 controller with parsed data"""
        if not controller_data or not controller_data.get('connected', False):
            return
            
        try:
            report = self.ds4_controller.report
            
            # Map D-Pad buttons (byte 36)
            dpad = controller_data['dpad_buttons']
            report.set_button_state("dpad_left", bool(dpad & 0x01))
            report.set_button_state("dpad_down", bool(dpad & 0x02))
            report.set_button_state("dpad_right", bool(dpad & 0x04))
            report.set_button_state("dpad_up", bool(dpad & 0x08))
            
            # Options and Share buttons
            report.set_button_state("options", bool(dpad & 0x10))
            report.set_button_state("share", bool(dpad & 0x80))
            
            # Stick clicks
            report.set_button_state("thumb_right", bool(dpad & 0x20))  # R3
            report.set_button_state("thumb_left", bool(dpad & 0x40))   # L3
            
            # Face and shoulder buttons (byte 37)
            face = controller_data['face_buttons']
            report.set_button_state("triangle", bool(face & 0x01))
            report.set_button_state("circle", bool(face & 0x02))  
            report.set_button_state("cross", bool(face & 0x04))
            report.set_button_state("square", bool(face & 0x08))
            report.set_button_state("shoulder_right", bool(face & 0x10))  # R1
            report.set_button_state("shoulder_left", bool(face & 0x20))   # L1
            
            # Trigger buttons (digital)
            report.set_button_state("trigger_right", bool(face & 0x40))   # R2
            report.set_button_state("trigger_left", bool(face & 0x80))    # L2
            
            # PS/Home button
            report.set_button_state("ps", bool(controller_data['home_button']))
            
            # Touchpad button
            report.set_button_state("touchpad", bool(controller_data['touchpad_button']))
            
            # Analog sticks (0-255 -> 0-255, with Y-axis inversion)
            report.left_thumb_x = controller_data['left_stick_x']
            report.left_thumb_y = 255 - controller_data['left_stick_y']  # Invert Y
            report.right_thumb_x = controller_data['right_stick_x']
            report.right_thumb_y = 255 - controller_data['right_stick_y']  # Invert Y
            
            # Analog triggers (0-255)
            report.left_trigger = controller_data['left_trigger']
            report.right_trigger = controller_data['right_trigger']
            
            # Send update to system
            self.ds4_controller.update_report(report)
            self.packets_processed += 1
            
        except Exception as e:
            print(f"[!] Error updating DS4 controller: {e}")
    
    def receive_loop(self) -> None:
        """Main loop for receiving UDP packets from reWASD"""
        print(f"[+] Starting DSU client, waiting for data from reWASD...")
        
        while self.running:
            try:
                # Receive UDP packet
                data, addr = self.socket.recvfrom(1024)
                self.packets_received += 1
                self.last_packet_time = time.time()
                
                # Only process packets from reWASD server
                if addr[0] == self.rewasd_host and addr[1] == self.rewasd_port:
                    # Parse DSU packet
                    controller_data = self.parse_dsu_packet(data)
                    
                    if controller_data:
                        # Update virtual DS4 controller
                        self.update_ds4_controller(controller_data)
                        
                        # Debug output (optional)
                        if self.packets_processed % 100 == 0:  # Print every 100th packet
                            print(f"[DSU] Processed {self.packets_processed} packets, "
                                  f"Buttons: {controller_data['dpad_buttons']:02x}|{controller_data['face_buttons']:02x}")
                
            except socket.timeout:
                continue  # Normal timeout, check if still running
            except Exception as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"[!] Error in receive loop: {e}")
                break
    
    def start(self) -> None:
        """Start the DSU client"""
        if not self.connect():
            return
            
        self.running = True
        
        # Start the receive loop in current thread
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the DSU client"""
        self.running = False
        self.disconnect()
        
        print(f"[+] Statistics: {self.packets_received} received, {self.packets_processed} processed")
        print("[+] DSU client stopped")
    
    def disconnect(self) -> None:
        """Clean up all resources"""
        if self.ds4_controller:
            try:
                self.ds4_controller.disconnect()
            except:
                pass
            self.ds4_controller = None
            
        if self.vigem_client:
            try:
                self.vigem_client.disconnect()
            except:
                pass
            self.vigem_client = None
            
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

def main():
    """Main entry point"""
    print("DSU Client for reWASD -> ViGEm DS4 Bridge")
    print("==========================================")
    
    if not VIGEM_AVAILABLE:
        print("[!] Please install pyvigem: pip install pyvigem")
        print("[!] And install ViGEmBus driver from: https://github.com/nefarius/ViGEmBus/releases")
        return
    
    # Create and start DSU client
    client = DSUToDS4Bridge()
    
    try:
        client.start()
    except Exception as e:
        print(f"[!] Fatal error: {e}")
    finally:
        client.stop()

if __name__ == "__main__":
    main()