import can
import time

def parse_version_response(data):
    if len(data) < 7:
        raise ValueError('Invalid response length')
    xx = data[4]
    yy = data[5]
    zz = data[6]
    return f"{xx}.{yy}.{zz}"

def uds_send_receive_pcan(channel='PCAN_USBBUS1', bitrate=500000):
    bus = can.interface.Bus(channel=channel, interface='pcan', bitrate=bitrate)
    
    request_id = 0x068D  # UDS 요청 ID, 필요시 환경에 맞게 변경
    response_id = 0x068E # UDS 응답 ID, 실제 받는 ID로 맞춤
    
    request_data = [0x03, 0x22, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00]
    
    msg = can.Message(arbitration_id=request_id, data=request_data, is_extended_id=False)
    print(f"Sending UDS request: {msg}")
    bus.send(msg)
    
    response = None
    start = time.time()
    while time.time() - start < 2.0:
        recv = bus.recv(timeout=0.2)
        if recv:
            print(f"Received UDS message ID: {hex(recv.arbitration_id)}")
            if recv.arbitration_id == response_id:
                data = list(recv.data)
                print(f"Received UDS data: {data}")
                if data[:2] == [0x07, 0x62]:  # Positive response (SID+0x40)
                    response = data
                    break
    bus.shutdown()
    
    if not response:
        raise TimeoutError('No matching UDS response received')
    
    return parse_version_response(response)


def collect_analog_current_data(channel='PCAN_USBBUS1', bitrate=500000, duration=5):
    bus = can.interface.Bus(channel=channel, interface='pcan', bitrate=bitrate)
    msg_id = 0x3C2  # 메시지 ID (16진수 962)

    data_points = []
    start = time.time()

    try:
        while time.time() - start < duration:
            msg = bus.recv(timeout=0.5)
            if msg and msg.arbitration_id == msg_id:
                data_points.append(msg.data)
    finally:
        bus.shutdown()

    return data_points

def extract_analog_current(values):
    currents = []
    for data in values:
        if len(data) >= 8:
            # 바이트 1~3 (인덱스 1,2,3)에서 24비트 big-endian signed 정수 추출
            raw_val = (data[1] << 16) | (data[2] << 8) | data[3]
            
            offset = -8388608
            analog_current = raw_val + offset
            currents.append(analog_current)
    return currents

def analyze_current(currents):
    if not currents:
        return None, None, None
    avg_val = sum(currents) / len(currents)
    min_val = min(currents)
    max_val = max(currents)
    return avg_val, min_val, max_val


if __name__ == '__main__':
    try:
        version = uds_send_receive_pcan()
        print(f"최종 version = {version}")
    except Exception as e:
        print(f"UDS 통신 오류: {e}")

    print("\nAnalogCurrent 데이터 5초간 수집 중...")
    data_points = collect_analog_current_data()
    currents = extract_analog_current(data_points)
    avg_val, min_val, max_val = analyze_current(currents)
    
    if avg_val is not None:
        print(f"AVG AnalogCurrent: {avg_val:.2f} mA")
        print(f"MIN AnalogCurrent: {min_val} mA")
        print(f"MAX AnalogCurrent: {max_val} mA")
        if abs(avg_val) <= 50 and abs(min_val) <= 50 and abs(max_val) <= 50:
            print("무부하 전류값 이상없음")
        else:
            print("무부하 전류값 이상 존재")
    else:
        print("AnalogCurrent 데이터 없음")
