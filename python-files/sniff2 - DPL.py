from flask import Flask, jsonify, render_template_string
from scapy.all import sniff, TCP, IP, Raw
import struct
import threading
import time
import json

app = Flask(__name__)
MQTT_PORT = 1883
mqtt_devices = {}  # {topic: {'ip': 'x.x.x.x', 'last_seen': timestamp, 'payload': payload}}

# Complete topic to machine name mapping with manual IDs (same as before)
topic_mapping = [
{"topic": "DF9F1B_cnt", "machine": "IMM-250-209 ", "manual_id": "1442000317"},
{"topic": "D51F34_cnt", "machine": "IMM-250-210 ", "manual_id": "1442000318"},
{"topic": "DD3461_cnt", "machine": "IMM-250-211", "manual_id": "1442000319"},
{"topic": "E070AF_cnt", "machine": "IMM-250-212", "manual_id": "1442000320"},
{"topic": "DAEC1E_cnt", "machine": "IMM-250-213", "manual_id": "1442000321"},
{"topic": "4D3AB7_cnt", "machine": "IMM-250-214", "manual_id": "1442000322"},
{"topic": "3F60D3_cnt", "machine": "IMM-250-215", "manual_id": "1442000323"},
{"topic": "A86B2D_cnt", "machine": "IMM-250-216", "manual_id": "1442000324"},
{"topic": "218121_cnt", "machine": "IMM-250-217", "manual_id": "1442000325"},
{"topic": "82B191_cnt", "machine": "IMM-250-218", "manual_id": "1442000326"},
{"topic": "CB34EB_cnt", "machine": "IMM-250-219", "manual_id": "1442000327"},
{"topic": "FD3428_cnt", "machine": "IMM-250-220", "manual_id": "1442000328"},
{"topic": "22B5C6_cnt", "machine": "IMM-250-221", "manual_id": "1442000329"},
{"topic": "1FE972_cnt", "machine": "IMM-250-222", "manual_id": "1442000330"},
{"topic": "994056_cnt", "machine": "IMM-250-223", "manual_id": "1442000331"},
{"topic": "4D38BD_cnt", "machine": "IMM-160-108", "manual_id": "1442000332"},
{"topic": "50F399_cnt", "machine": "IMM-160-109", "manual_id": "1442000333"},
{"topic": "F3105_cnt", "machine": "IMM-160-110", "manual_id": "1442000334"},
{"topic": "7C2206_cnt", "machine": "IMM-160-111", "manual_id": "1442000335"},
{"topic": "8A3FB4_cnt", "machine": "IMM-160-112", "manual_id": "1442000336"},
{"topic": "F259F_cnt", "machine": "IMM-250-224", "manual_id": "1442000337"},
{"topic": "F42447_cnt", "machine": "IMM-250-225", "manual_id": "1442000338"},
{"topic": "1F7AD9_cnt", "machine": "IMM-250-226", "manual_id": "1442000339"},
{"topic": "9833A6_cnt", "machine": "IMM-250-227", "manual_id": "1442000340"},
{"topic": "50F399_cnt", "machine": "IMM-250-228", "manual_id": "1442000341"},
{"topic": "525F15_cnt", "machine": "IMM-250-229", "manual_id": "1442000342"},
{"topic": "DF65C4_cnt", "machine": "IMM-250-230", "manual_id": "1442000343"},
{"topic": "CB3D83_cnt", "machine": "IMM-250-231", "manual_id": "1442000344"},
{"topic": "95A1F2_cnt", "machine": "IMM-250-232", "manual_id": "1442000345"},
{"topic": "94CB46_cnt", "machine": "IMM-250-233", "manual_id": "1442000346"},
{"topic": "B4625E_cnt", "machine": "IMM-250-234", "manual_id": "1442000347"},
{"topic": "7C2416_cnt", "machine": "IMM-250-235", "manual_id": "1442000348"},
{"topic": "EAA1E_cnt", "machine": "IMM-250-236", "manual_id": "1442000349"},
{"topic": "DED652_cnt", "machine": "IMM-250-237", "manual_id": "1442000350"},
{"topic": "22A629_cnt", "machine": "IMM-250-238", "manual_id": "1442000351"},
{"topic": "C72655_cnt", "machine": "IMM-528-01", "manual_id": "1442000352"}
]


# Create dictionaries for quick lookup
topic_to_machine = {item['topic']: item['machine'] for item in topic_mapping}
topic_to_id = {item['topic']: item['manual_id'] for item in topic_mapping}
allowed_topics = {item['topic'] for item in topic_mapping}

# Updated HTML Template with payload display
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MQTT Device Monitor DPL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        .search-container { margin-bottom: 20px; }
        input[type="text"] {
            padding: 8px 12px;
            width: 400px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td { 
            padding: 12px 15px; 
            border: 1px solid #ddd; 
            text-align: left; 
        }
        th { 
            background-color: #f8f9fa;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f1f1f1; }
        .online { color: #28a745; font-weight: bold; }
        .offline { color: #dc3545; font-weight: bold; }
        .payload { 
            max-width: 300px; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
        }
        .payload.expanded { 
            white-space: normal; 
            overflow: visible;
            max-width: none;
        }
        .show-more {
            color: #007bff;
            cursor: pointer;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <h1>🏭 DPL IoT Monitor</h1>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="🔍 Search by machine, topic, IP or ID...">
    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Manual ID</th>
                <th>Machine Name</th>
                <th>Topic</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Payload</th>
            </tr>
        </thead>
        <tbody id="data"></tbody>
    </table>

    <script>
        let allData = [];

        async function fetchData() {
            try {
                const res = await fetch('/data');
                allData = await res.json();
                filterData();
            } catch (error) {
                console.error('Fetch error:', error);
            }
        }

        function togglePayload(element) {
            element.parentElement.classList.toggle('expanded');
        }

        function renderTable(data) {
            const table = document.getElementById('data');
            table.innerHTML = '';
            
            if (data.length === 0) {
                table.innerHTML = '<tr><td colspan="7" style="text-align: center;">No matching devices found</td></tr>';
                return;
            }

            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                const statusClass = row.status === "Online" ? "online" : "offline";
                const payloadText = row.payload ? JSON.stringify(row.payload) : "-";
                
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.manual_id || "-"}</td>
                    <td>${row.machine || "-"}</td>
                    <td><code>${row.topic}</code></td>
                    <td>${row.ip || "-"}</td>
                    <td class="${statusClass}">${row.status}</td>
                    <td class="payload">
                        ${payloadText}
                        ${payloadText.length > 30 ? '<span class="show-more" onclick="togglePayload(this)"> [show more]</span>' : ''}
                    </td>
                `;
                table.appendChild(tr);
            });
        }

        function filterData() {
            const keyword = document.getElementById('searchInput').value.toLowerCase();
            const filtered = allData.filter(row => 
                (row.machine && row.machine.toLowerCase().includes(keyword)) ||
                row.topic.toLowerCase().includes(keyword) ||
                (row.ip && row.ip.toLowerCase().includes(keyword)) ||
                (row.manual_id && row.manual_id.toLowerCase().includes(keyword)) ||
                (row.payload && JSON.stringify(row.payload).toLowerCase().includes(keyword))
            );
            renderTable(filtered);
        }

        document.getElementById('searchInput').addEventListener('input', filterData);
        setInterval(fetchData, 2000);
        fetchData(); // Initial load
    </script>
    <div class="footer">Developed by DIP MIS Automation</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    current_time = time.time()
    data = []
    for item in topic_mapping:  # Maintain original order
        topic = item['topic']
        info = mqtt_devices.get(topic, {})
        last_seen = info.get('last_seen', 0)
        ip = info.get('ip', '')
        payload = info.get('payload', None)
        status = "Online" if current_time - last_seen <= 30 else "Offline"
        data.append({
            "manual_id": item['manual_id'],
            "machine": item['machine'],
            "topic": topic,
            "ip": ip,
            "status": status,
            "payload": payload
        })
    return jsonify(data)

import struct

def extract_mqtt_payload(payload_bytes):
    try:
        index = 1
        multiplier = 1
        remaining_length = 0

        while True:
            byte = payload_bytes[index]
            remaining_length += (byte & 127) * multiplier
            multiplier *= 128
            index += 1
            if not (byte & 128):
                break

        if len(payload_bytes) < index + 2:
            return None, None

        topic_length = struct.unpack(">H", payload_bytes[index:index+2])[0]
        topic_start = index + 2

        if len(payload_bytes) < topic_start + topic_length:
            return None, None

        topic = payload_bytes[topic_start:topic_start + topic_length].decode('utf-8', errors='ignore')
        payload_start = topic_start + topic_length

        if len(payload_bytes) > payload_start:
            raw_data = payload_bytes[payload_start:].decode('utf-8', errors='ignore').strip()

            # ✅ Cut at "0\" and remove both the 0 and the backslash
            split_index = raw_data.find('0\\')
            if split_index != -1:
                raw_data = raw_data[:split_index]

            # ✅ Extract digits only from the beginning
            import re
            match = re.match(r'^(\d+)', raw_data)
            cleaned = match.group(1) if match else ''

            return topic, cleaned

        return topic, None

    except Exception as e:
        print("Payload decode error:", e)
        return None, None


        return topic, None
    except Exception as e:
        print(f"Error extracting payload: {e}")
        return None, None

def packet_callback(packet):
    try:
        if packet.haslayer(TCP) and packet.haslayer(IP) and packet.haslayer(Raw):
            ip = packet[IP]
            tcp = packet[TCP]
            
            if tcp.dport == MQTT_PORT or tcp.sport == MQTT_PORT:
                payload = bytes(packet[Raw].load)
                if len(payload) > 0:
                    mqtt_type = (payload[0] & 0xF0) >> 4
                    if mqtt_type == 3:  # PUBLISH message
                        topic, payload_data = extract_mqtt_payload(payload)
                        if topic and topic in allowed_topics:
                            mqtt_devices[topic] = {
                                "ip": ip.src,
                                "last_seen": time.time(),
                                "payload": payload_data
                            }
    except Exception as e:
        print(f"Packet processing error: {e}")

def sniff_thread():
    print("🚀 Starting MQTT sniffer...")
    try:
        sniff(filter=f"tcp port {MQTT_PORT}", prn=packet_callback, store=0)
    except Exception as e:
        print(f"Sniffing error: {e}")

if __name__ == '__main__':
    try:
        print("🔧 Initializing...")
        threading.Thread(target=sniff_thread, daemon=True).start()
        app.run(host='0.0.0.0', port=2500, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"🔥 Critical error: {e}")
