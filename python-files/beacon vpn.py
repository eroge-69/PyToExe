import os
import subprocess

def start_beacon_vpn(config_file):
    # config_file would be a .ovpn or .conf from your VPN sever
    print("starting beacon vpn...")

    subprocess.run(["openvpn","--config", config-file])

    if __name__== "__main__":

     start_beacon_vpn("beacon.ovpn")
