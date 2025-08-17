#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A320 Autopilot (UDP) — версия без NumPy для конвертации в EXE.
"""

import socket
import time
import math
from typing import Tuple, Optional

# ===== NETWORK =====
UDP_IP = "127.0.0.1"   # X-Plane host
SEND_PORT = 49000      # Port to SEND commands to X-Plane
LISTEN_PORT = 49005    # Port to LISTEN for telemetry
SOCK_TIMEOUT = 0.1     # seconds

# ===== UNITS =====
FT_TO_M = 0.3048
M_TO_FT = 3.28084
KT_TO_MS = 0.514444

# ===== A320 CONFIG =====
TARGET_ALT_FT = 36000    # FL360
CRUISE_MACH = 0.78
APPROACH_SPEED_KT = 135  # kts
FLARE_ALT_FT = 30        # flare start
RUNWAY_HEADING = 250     # example: RWY 25

MODE = "MOCK"  # AUTO = ждать UDP, MOCK = тестовый режим


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(val, hi))


class PIDController:
    """Classic PID controller."""
    def __init__(self, Kp=0.1, Ki=0.01, Kd=0.05, out_min=-1.0, out_max=1.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.out_min, self.out_max = out_min, out_max
        self.last_error = 0.0
        self.integral = 0.0

    def update(self, error: float, dt: float) -> float:
        dt = max(dt, 1e-3)
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        output = clamp(output, self.out_min, self.out_max)
        self.last_error = error
        return output


class A320Autopilot:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, LISTEN_PORT))
        self.sock.settimeout(SOCK_TIMEOUT)
        self.phase = "CRUISE"
        self.alt_pid = PIDController(0.05, 0.001, 0.01)
        self.speed_pid = PIDController(0.5, 0.01, 0.1)
        self.roll_pid = PIDController(0.8, 0.0, 0.3)
        self._mock_alt_ft = 20000.0
        self._mock_tas_kt = 280.0
        self._mock_hdg = 240.0

    def send_command(self, command: str, value: float) -> None:
        v = clamp(value, -1.0, 1.0)
        msg = f"{command} {v}\n".encode('utf-8')
        self.sock.sendto(msg, (UDP_IP, SEND_PORT))

    def recv_telemetry(self) -> Optional[Tuple[float, float, float]]:
        try:
            data, _ = self.sock.recvfrom(1024)
            text = data.decode('utf-8', errors='ignore').strip()
            parts = [p.strip() for p in text.split(",")]
            alt_m = float(parts[0])
            tas_ms = float(parts[1])
            hdg = float(parts[2])
            return alt_m * M_TO_FT, tas_ms / KT_TO_MS, hdg
        except Exception:
            return None

    def control_cruise(self, alt_ft, tas_kt, dt):
        alt_error = TARGET_ALT_FT - alt_ft
        pitch_cmd = self.alt_pid.update(alt_error, dt)
        mach = tas_kt * 0.0015
        speed_error = CRUISE_MACH - mach
        throttle_cmd = clamp(0.7 + self.speed_pid.update(speed_error, dt) * 0.2, 0.0, 1.0)
        self.send_command("elevator", pitch_cmd)
        self.send_command("throttle", throttle_cmd)

    def control_approach(self, alt_ft, tas_kt, heading, dt):
        hdg_err = (heading - RUNWAY_HEADING + 540.0) % 360.0 - 180.0
        loc_dev = math.sin(math.radians(hdg_err))
        gs_dev = 0.1 if alt_ft > 500 else 0.05
        roll_cmd = self.roll_pid.update(-loc_dev * 10.0, dt)
        self.send_command("aileron", roll_cmd)
        pitch_cmd = clamp(-2.5 - gs_dev * 2.0, -1.0, 1.0)
        self.send_command("elevator", pitch_cmd)
        speed_error = APPROACH_SPEED_KT - tas_kt
        throttle_cmd = clamp(0.3 + self.speed_pid.update(speed_error, dt) * 0.2, 0.0, 1.0)
        self.send_command("throttle", throttle_cmd)
        if alt_ft < FLARE_ALT_FT:
            self.phase = "FLARE"

    def control_flare(self, alt_ft, tas_kt, dt):
        flare_pitch = clamp(5.0 * (1.0 - math.exp(-max(alt_ft, 0.0) / 15.0)), -1.0, 1.0)
        self.send_command("elevator", flare_pitch)
        self.send_command("throttle", 0.25)
        if alt_ft < 1.0:
            self.phase = "ROLLOUT"
            self.send_command("brakes_max", 1.0)

    def mock_step(self, dt: float) -> Tuple[float, float, float]:
        if self.phase == "CRUISE":
            self._mock_alt_ft += (TARGET_ALT_FT - self._mock_alt_ft) * 0.02 * dt * 50
            self._mock_tas_kt += (450 - self._mock_tas_kt) * 0.01 * dt * 50
        elif self.phase in ("APPROACH", "FLARE", "ROLLOUT"):
            self._mock_alt_ft = max(self._mock_alt_ft - 30 * dt, 0.0)
            self._mock_tas_kt = max(self._mock_tas_kt - 1.5 * dt, 90.0)
            hdg_err = (RUNWAY_HEADING - self._mock_hdg + 540) % 360 - 180
            self._mock_hdg += clamp(hdg_err, -5.0, 5.0) * 0.05 * dt * 50
        return self._mock_alt_ft, self._mock_tas_kt, self._mock_hdg

    def run(self):
        print("🛫 A320 Autopilot: RUN")
        last_time = time.time()
        try:
            while True:
                now = time.time()
                dt = max(now - last_time, 1e-3)
                last_time = now
                telemetry = None if MODE == "MOCK" else self.recv_telemetry()
                if telemetry is None:
                    alt_ft, tas_kt, heading = self.mock_step(dt)
                else:
                    alt_ft, tas_kt, heading = telemetry

                if self.phase == "CRUISE":
                    self.control_cruise(alt_ft, tas_kt, dt)
                    if alt_ft < 3000.0:
                        self.phase = "APPROACH"
                elif self.phase == "APPROACH":
                    self.control_approach(alt_ft, tas_kt, heading, dt)
                elif self.phase == "FLARE":
                    self.control_flare(alt_ft, tas_kt, dt)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("⏹ Autopilot stopped")


if __name__ == "__main__":
    ap = A320Autopilot()
    ap.run()
