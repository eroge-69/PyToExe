import time
from simconnect import SimConnect, AircraftRequests, SIMCONNECT_PERIOD

def main():
    print("Connecting to SimConnect...")
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=SIMCONNECT_PERIOD.SECOND)

    last_on_ground = False

    print("Monitoring landing rate. Press Ctrl+C to stop.")
    try:
        while True:
            on_ground = aq.get("GROUND_VELOCITY") is not None
            vertical_speed = aq.get("VERTICAL_SPEED")  # feet per minute

            # Alternatively, get the gear status to detect touchdown
            gear_deploy = aq.get("GEAR_POSITION")  # 0 = up, 1 = down

            print(f"Gear: {gear_deploy}, Vertical Speed: {vertical_speed:.2f} ft/min")

            if gear_deploy == 1 and not last_on_ground:
                print(f"*** Landed! Landing rate: {vertical_speed:.2f} ft/min ***")

            last_on_ground = (gear_deploy == 1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
