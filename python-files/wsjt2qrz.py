import socket
import json
import requests

# QRZ.com API settings
api_key = "061C-98F4-3B68-2F35"
api_url = "https://logbook.qrz.com/api"

# UDP settings
udp_host = "127.0.0.1"
udp_port = 2237

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_host, udp_port))

while True:
    # Receive data from WSJT-X
    data, addr = sock.recvfrom(1024)
    try:
        # Try to parse JSON data
        qso_data = json.loads(data.decode())

        # Extract relevant QSO information
        if qso_data["type"] == "qso_logged":
            dx_call = qso_data.get("dx_call")
            dx_grid = qso_data.get("dx_grid")
            frequency = qso_data.get("frequency")
            mode = qso_data.get("mode")
            date_off = qso_data.get("date_off")
            time_off = qso_data.get("time_off")
            tx_power = qso_data.get("tx_power")
            operator = qso_data.get("operator")
            station_callsign = qso_data.get("station_callsign")
            my_grid = qso_data.get("my_grid")

            # Prepare ADIF data
            adif_data = f"""
            <CALL:{len(dx_call)}>{dx_call}
            <GRIDSQUARE:{len(dx_grid)}>{dx_grid}
            <FREQ:{len(str(frequency))}>{frequency}
            <MODE:{len(mode)}>{mode}
            <QSO_DATE:{len(date_off.split('T')[0].replace('-',''))}>{date_off.split('T')[0].replace('-','')}
            <TIME_ON:{len(time_off)}>{time_off}
            <TX_PWR:{len(tx_power)}>{tx_power}
            <OPERATOR:{len(operator)}>{operator}
            <STATION_CALLSIGN:{len(station_callsign)}>{station_callsign}
            <MY_GRIDSQUARE:{len(my_grid)}>{my_grid}
            <EOR>
            """

            # Send ADIF data to QRZ.com
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/x-adif"}
            data = {"adif": adif_data}
            response = requests.post(api_url, headers=headers, data=data)

            # Check response status
            if response.status_code == 200:
                print("QSO logged successfully!")
            else:
                print(f"Error logging QSO: {response.text}")

    except json.JSONDecodeError:
        # Handle non-JSON data (if any)
        print("Received non-JSON data:", data)