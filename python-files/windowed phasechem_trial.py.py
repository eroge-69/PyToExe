import time
import numpy as np
import pandas as pd
from simple_pid import PID
from pymodbus.client.sync import ModbusTcpClient
import os
from datetime import datetime, timedelta

# 트라이얼 만료 확인 (2025-07-21부터 8일 후 만료)
start_date = datetime(2025, 7, 21)
expiration_date = start_date + timedelta(days=8)

if datetime.now() > expiration_date:
    print("❌ Trial version expired. Please contact for full version.")
    exit()

# HIP 컨트롤러 접속 설정
client = ModbusTcpClient('192.168.0.50', port=502)  # 장비 IP/포트 입력

# PhaseChem 엔진: 위상장 곡률 Ψ(t) 계산
def calculate_phase_field(P, T, t):
    # 공명 주파수 및 위상 변수
    omega = 0.05  # 공명 주파수 [rad/s]
    delta = np.pi / 4  # 위상차
    A = 0.1 * P / 2  # 압력 기반 진폭 스케일링
    psi = A * np.sin(omega * t + delta)
    return psi

# 안전 연결 함수
def safe_connect():
    try:
        if not client.connect():
            raise ConnectionError("Modbus 연결 실패")
        print("✅ 장비 연결 성공")
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        exit(1)

# 센서 데이터 읽기 (P[GPa], T[°C]) - 에러 처리 추가
def safe_read_sensors():
    try:
        P_raw = client.read_holding_registers(0, 1).registers[0] / 1000  # 압력 kPa→GPa
        T_raw = client.read_holding_registers(1, 1).registers[0] / 10    # 온도 d°C→°C
        if not (0 <= P_raw <= 10 and 0 <= T_raw <= 1000):  # 합리적 범위 검증
            raise ValueError("센서 데이터 이상")
        return P_raw, T_raw
    except Exception as e:
        print(f"❌ 센서 오류: {e}")
        return None, None

# 제어 명령 전송 - 에러 처리 추가
def adjust_controls(P_target, T_target):
    try:
        P_cmd = int(P_target * 1000)  # GPa→kPa
        T_cmd = int(T_target * 10)    # °C→d°C
        client.write_register(0, P_cmd)  # 압력 명령
        client.write_register(1, T_cmd)  # 온도 명령
    except Exception as e:
        print(f"❌ 제어 명령 오류: {e}")

# 동적 프로파일: 합성 단계별 압력/온도 목표값 (램프업, 유지, 냉각)
def dynamic_profile(t):
    if t < 1200:  # 램프업: 0-100°C in 20min (예: 550°C 목표 시 1200초 내 상승)
        return 1.5, min(550, t * (550 / 1200))  # 선형 램프업
    elif t < 6000:  # 유지: 1.5 GPa, 550°C for ~1.3 hours
        return 1.5, 550
    else:  # 냉각: 선형 하강 to 25°C
        return 0, max(25, 550 - (t - 6000) * (550 - 25) / 1200)  # 20min 냉각

# 데이터 로깅 및 이상 감지
def log_data(t, P, T, psi):
    data = {'Time': time.strftime('%H:%M:%S'), 'Pressure(GPa)': P, 'Temperature(°C)': T, 'Psi': psi}
    df = pd.DataFrame([data])
    df.to_csv('phasechem_log.csv', mode='a', header=not os.path.exists('phasechem_log.csv'), index=False)
    if P is not None and T is not None:
        if abs(P - 1.5) > 0.2 or abs(T - 550) > 50:
            print(f⚠️ 이상 감지: P={P:.3f}, T={T:.1f}")

# PID 제어기 설정
pid_P = PID(1.0, 0.05, 0.01, setpoint=1.5)  # 목표 압력 1.5 GPa
pid_T = PID(2.0, 0.1, 0.02, setpoint=550)   # 목표 온도 550°C

# 메인 제어 루프
def feedback_control_loop(duration=7200):
    safe_connect()
    start = time.time()
    while time.time() - start < duration:
        elapsed = time.time() - start
        P_target, T_target = dynamic_profile(elapsed)
        pid_P.setpoint = P_target
        pid_T.setpoint = T_target
        
        P, T = safe_read_sensors()
        if P is None or T is None:
            print("🚨 제어 중단: 센서 오류")
            break
        
        psi = calculate_phase_field(P, T, elapsed)
        
        # PID 피드백
        P_adjust = pid_P(P)
        T_adjust = pid_T(T)
        adjust_controls(P + P_adjust, T + T_adjust)
        
        # 로그 출력 및 이상 감지
        log_data(elapsed, P, T, psi)
        print(f"[{time.strftime('%H:%M:%S')}] P={P:.3f} GPa (Target: {P_target:.3f}), T={T:.1f}°C (Target: {T_target:.1f}), Ψ(t)={psi:.4f}")
        
        time.sleep(1)  # 1초 간격 제어
    
    client.close()
    print("✅ 제어 루프 종료. 로그 파일: phasechem_log.csv")

# 실행
if __name__ == "__main__":
    print("🔄 PhaseChem 위상장 제어 시작 (8일 트라이얼 버전)")
    feedback_control_loop()