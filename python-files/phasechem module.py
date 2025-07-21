import time
import numpy as np
from simple_pid import PID
from pymodbus.client.sync import ModbusTcpClient

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

# 센서 데이터 읽기 (P[GPa], T[°C])
def read_sensors():
    P_raw = client.read_holding_registers(0, 1).registers[0] / 1000  # 압력 kPa→GPa
    T_raw = client.read_holding_registers(1, 1).registers[0] / 10    # 온도 d°C→°C
    return P_raw, T_raw

# 제어 명령 전송
def adjust_controls(P_target, T_target):
    P_cmd = int(P_target * 1000)  # GPa→kPa
    T_cmd = int(T_target * 10)    # °C→d°C
    client.write_register(0, P_cmd)  # 압력 명령
    client.write_register(1, T_cmd)  # 온도 명령

# PID 제어기 설정
pid_P = PID(1.0, 0.05, 0.01, setpoint=1.5)  # 목표 압력 1.5 GPa
pid_T = PID(2.0, 0.1, 0.02, setpoint=550)   # 목표 온도 550°C

# 메인 제어 루프
def feedback_control_loop(duration=7200):
    start = time.time()
    while time.time() - start < duration:
        P, T = read_sensors()
        psi = calculate_phase_field(P, T, time.time() - start)
        
        # PID 피드백
        P_adjust = pid_P(P)
        T_adjust = pid_T(T)
        adjust_controls(P + P_adjust, T + T_adjust)

        # 로그 출력
        print(f"[{time.strftime('%H:%M:%S')}] P={P:.3f} GPa, T={T:.1f}°C, Ψ(t)={psi:.4f}")

        time.sleep(1)  # 1초 간격 제어

# 실행
if __name__ == "__main__":
    print("🔄 PhaseChem 위상장 제어 시작")
    feedback_control_loop()
