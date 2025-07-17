import random
import time
import sys
import paramiko
import telnetlib
import threading
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsPixmapItem, QGraphicsTextItem, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import ipaddress
import socket

# Basic Network Device Class
class NetworkDevice:
    def __init__(self, device_type, routing_protocol=None):
        self.device_type = device_type
        self.routing_protocol = routing_protocol
        self.connected_devices = []
        self.ip_address = None
        self.routing_table = {}
        self.ssh_service = None
        self.telnet_service = None
        self.interfaces = {}

# SSH Service Simulation using paramiko
class SSHServer:
    def __init__(self, device):
        self.device = device
        self.is_open = True
        self.port = 22
        self.users = {"admin": "admin123"}

    def start(self):
        print(f"SSH server on {self.device.device_type} is listening on port {self.port}.")
        threading.Timer(5.0, self.accept_connection).start()

    def accept_connection(self):
        print(f"Accepted SSH connection on {self.device.device_type}.")
        self.authenticate()

    def authenticate(self):
        username = "admin"
        password = "admin123"
        if self.users.get(username) == password:
            print(f"SSH Authentication successful on {self.device.device_type}.")
        else:
            print(f"SSH Authentication failed on {self.device.device_type}.")

# Telnet Service Simulation using telnetlib
class TelnetServer:
    def __init__(self, device):
        self.device = device
        self.is_open = True
        self.port = 23
        self.users = {"admin": "admin123"}

    def start(self):
        print(f"Telnet server on {self.device.device_type} is listening on port {self.port}.")
        threading.Timer(5.0, self.accept_connection).start()

    def accept_connection(self):
        print(f"Accepted Telnet connection on {self.device.device_type}.")
        self.authenticate()

    def authenticate(self):
        username = "admin"
        password = "admin123"
        if self.users.get(username) == password:
            print(f"Telnet Authentication successful on {self.device.device_type}.")
        else:
            print(f"Telnet Authentication failed on {self.device.device_type}.")

# Static Routing Simulation
class StaticRouting:
    def __init__(self, device):
        self.device = device
        self.routing_table = {}

    def add_static_route(self, destination, gateway, netmask):
        self.routing_table[destination] = {"gateway": gateway, "netmask": netmask}
        print(f"Static route added: {destination} via {gateway} with netmask {netmask}.")

    def display_routing_table(self):
        print(f"Routing Table for {self.device.device_type}: {self.routing_table}")

# VPN (IPsec and GRE) Simulation
class VPN:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2
        self.vpn_tunnel = None

    def create_vpn_tunnel(self):
        """Simulate creating an IPsec VPN tunnel between two devices."""
        print(f"Creating IPsec VPN tunnel between {self.device1.device_type} and {self.device2.device_type}.")
        self.vpn_tunnel = (self.device1, self.device2)

    def send_vpn_traffic(self, packet):
        """Simulate sending traffic through the VPN tunnel."""
        if self.vpn_tunnel:
            print(f"Sending encrypted packet {packet.data} through VPN tunnel between {self.device1.device_type} and {self.device2.device_type}.")
        else:
            print(f"No VPN tunnel established for packet {packet.data}.")

# Routing Protocols (RIP, OSPF, EIGRP, BGP)
class RoutingProtocol:
    def __init__(self, protocol_type, device):
        self.protocol_type = protocol_type
        self.device = device
        self.routing_table = {}

    def advertise_routes(self):
        """Simulate routing protocol advertisements (e.g., RIP, OSPF, EIGRP, BGP)."""
        if self.protocol_type == "RIP":
            print(f"Advertising routes with RIP protocol from {self.device.device_type}.")
        elif self.protocol_type == "OSPF":
            print(f"Advertising routes with OSPF protocol from {self.device.device_type}.")
        elif self.protocol_type == "EIGRP":
            print(f"Advertising routes with EIGRP protocol from {self.device.device_type}.")
        elif self.protocol_type == "BGP":
            print(f"Advertising routes with BGP protocol from {self.device.device_type}.")

    def receive_route_update(self, source_device, route_info):
        """Simulate receiving routing updates from other devices."""
        print(f"{self.device.device_type} received routing update from {source_device.device_type}: {route_info}")
        self.routing_table.update(route_info)

    def display_routing_table(self):
        """Display the current routing table."""
        print(f"{self.device.device_type} routing table ({self.protocol_type}): {self.routing_table}")

# Switching Technology (STP, VLAN, EtherChannel, Port Security, DTP)
class SwitchingTechnology:
    def __init__(self, switch):
        self.switch = switch
        self.vlans = {}  # VLANs and their members
        self.etherchannel = []  # Store aggregated links
        self.port_security = {}  # MAC addresses per port
        self.stp_state = {}  # STP State for each port
        self.dtp_enabled = False  # DTP status

    def configure_vlan(self, vlan_id, ports):
        """Configure VLANs on the switch."""
        self.vlans[vlan_id] = ports
        print(f"VLAN {vlan_id} configured with ports: {ports}")

    def configure_etherchannel(self, ports):
        """Configure EtherChannel (link aggregation) for the given ports."""
        self.etherchannel.append(ports)
        print(f"EtherChannel configured for ports: {ports}")

    def configure_port_security(self, port, max_mac_addresses):
        """Configure port security by limiting the number of MAC addresses allowed per port."""
        self.port_security[port] = max_mac_addresses
        print(f"Port security configured on port {port} with a max of {max_mac_addresses} MAC addresses.")

    def configure_stp(self, port, state):
        """Configure Spanning Tree Protocol state for a port (e.g., Forwarding, Blocking)."""
        self.stp_state[port] = state
        print(f"STP configured on port {port} with state: {state}")

    def enable_dtp(self):
        """Enable Dynamic Trunking Protocol."""
        self.dtp_enabled = True
        print(f"DTP enabled on {self.switch.device_type}.")

# Switch Class to include all switching technologies
class Switch(NetworkDevice):
    def __init__(self, device_type, routing_protocol=None):
        super().__init__(device_type, routing_protocol)
        self.switching_technology = SwitchingTechnology(self)

    def process_packets(self):
        print(f"{self.device_type} switch processing packets...")

# Packet Class for Simulation
class Packet:
    def __init__(self, source, destination, data, port=None, vlan=None):
        self.source = source
        self.destination = destination
        self.data = data
        self.port = port
        self.vlan = vlan

# GUI Visualization and Network Simulation
class NetworkSimulationEngine:
    def __init__(self, devices, update_interval=1):
        self.devices = devices
        self.update_interval = update_interval
        self.running = True

    def start(self):
        while self.running:
            self.update_network()
            time.sleep(self.update_interval)

    def update_network(self):
        print("Updating Network...")
        
        # Simulate STP updates
        for device in self.devices:
            if isinstance(device, Switch):
                for port, state in device.switching_technology.stp_state.items():
                    print(f"Port {port} on {device.device_type} is in STP state: {state}")
                
        # Simulate routing protocol updates
        for device in self.devices:
            if isinstance(device, Router):
                device.routing_protocol.advertise_routes()

        # Simulate VPN traffic flow
        for device in self.devices:
            if isinstance(device, VPN):
                device.send_vpn_traffic(Packet("192.168.1.1", "192.168.1.2", "Sample Data"))

    def stop(self):
        self.running = False
        print("Simulation stopped.")

class Router(NetworkDevice):
    def __init__(self, device_type, routing_protocol=None):
        super().__init__(device_type, routing_protocol)
        self.routing_protocol = RoutingProtocol("OSPF", self)

    def process_packets(self):
        print(f"{self.device_type} router processing packets...")

# PyQt5 GUI Class
class NetworkSimulationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Network Simulator with Switching Technologies")

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.devices = [Switch("Switch1"), Router("Router1", "RIP"), Router("Router2", "OSPF")]
        self.device_items = []

        self.init_ui()
        self.simulation_engine = NetworkSimulationEngine(self.devices)

        # Set up SSH and Telnet services on devices
        self.setup_services()

    def init_ui(self):
        router_pixmap = QPixmap("router_icon.png")
        switch_pixmap = QPixmap("switch_icon.png")

        router_item = QGraphicsPixmapItem(router_pixmap)
        switch_item = QGraphicsPixmapItem(switch_pixmap)

        router_item.setPos(100, 100)
        switch_item.setPos(300, 100)

        self.scene.addItem(router_item)
        self.scene.addItem(switch_item)

        eth_channel_label = QGraphicsTextItem("EtherChannel Active")
        eth_channel_label.setPos(150, 130)
        self.scene.addItem(eth_channel_label)

        vlan_label = QGraphicsTextItem("VLAN 10")
        vlan_label.setPos(350, 130)
        self.scene.addItem(vlan_label)

        self.device_items = [router_item, switch_item]

    def setup_services(self):
        """Set up SSH and Telnet services on devices."""
        for device in self.devices:
            if isinstance(device, Router):
                device.ssh_service = SSHServer(device)
                device.telnet_service = TelnetServer(device)
                device.ssh_service.start()
                device.telnet_service.start()

    def update_visualization(self):
        stp_state_label = QGraphicsTextItem("STP State: Forwarding")
        stp_state_label.setPos(100, 250)
        self.scene.addItem(stp_state_label)

        mpls_label = QGraphicsTextItem("MPLS Label: 100")
        mpls_label.setPos(350, 250)
        self.scene.addItem(mpls_label)

    def start_simulation(self):
        self.simulation_engine.start()

    def stop_simulation(self):
        self.simulation_engine.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NetworkSimulationApp()
    window.show()

    # Create VPN between devices
    vpn = VPN(window.devices[1], window.devices[2])  # VPN between Router1 and Router2
    vpn.create_vpn_tunnel()

    # Add static routes to devices
    window.devices[1].routing_protocol.add_static_route("10.0.0.0", "192.168.1.1", "255.255.255.0")
    window.devices[2].routing_protocol.add_static_route("10.0.0.0", "192.168.1.2", "255.255.255.0")

    # Configure VLANs and EtherChannel on switch
    window.devices[0].switching_technology.configure_vlan(10, ["eth0", "eth1"])
    window.devices[0].switching_technology.configure_etherchannel(["eth0", "eth1"])
    window.devices[0].switching_technology.configure_stp("eth0", "Forwarding")
    
    # Start the simulation
    window.start_simulation()

    sys.exit(app.exec_())
