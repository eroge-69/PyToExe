# Made by im-razvan - CS2 TriggerBot W/O Memory Writing
import pymem, pymem.process, keyboard, time
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform

mouse = Controller()

# https://github.com/a2x/cs2-dumper/
dwEntityList = 30139936
dwLocalPlayerPawn = 28265344
m_iIDEntIndex = 5940
m_iTeamNum = 1003

triggerKey = "alt"

def main():
    print("TriggerBot started.")
    pm = pymem.Pymem("cs2.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    while True:

        if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
            continue

        if keyboard.is_pressed(triggerKey):
            player = pm.read_longlong(client + dwLocalPlayerPawn)
            entityId = pm.read_int(player + m_iIDEntIndex)

            if entityId > 0:
                entList = pm.read_longlong(client + dwEntityList)

                entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                entityTeam = pm.read_int(entity + m_iTeamNum)
                playerTeam = pm.read_int(player + m_iTeamNum)

                isHuman = 1 if (entityTeam==2 or entityTeam==3) else 0

                if entityTeam != playerTeam and isHuman:
                    time.sleep(uniform(0.01, 0.05))
                    mouse.click(Button.left)

            time.sleep(0.03)
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    main()