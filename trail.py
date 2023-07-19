import asyncio
import websockets
import json
from uuid import uuid4
import re

######################################### Variables ############################################################################

#Read the README.md for instructions of how to use. 

#What summon command do you want to prefix to the coordinate?
prefix_command = "summon blockbuilders:trail"
#Where do you want to write the mcfunction to?
output_file = "/Users/joe/Library/Application Support/minecraftpe/games/com.mojang/development_behavior_packs/BP/functions/trail.mcfunction"

####################################################################################################################################
async def blockbuilders_ws(websocket):
    print('Connected')
    # Subscribe to the PlayerMessage event
    await websocket.send(
        # Send the subscribe message
        json.dumps({
            "header": {
                "version": 1,
                "requestId": f'{uuid4()}',
                # Subscribe to the PlayerMessage event
                "messageType": "commandRequest",
                "messagePurpose": "subscribe"
            },
            "body": {
                "eventName": "PlayerMessage"
            },
        }))

    try:
        async for msg in websocket:
            # Load the message
            msg = json.loads(msg)
            # Print the message
            print(msg)
            # Check if the message is a chat message
            if 'message' in msg['body']:
                # Get the message
                message = msg['body']['message']
                # Check if the message starts with [
                if message.startswith('['):
                    # use regex to remove everything between [ and ]
                    message = re.sub(r'\[.*?\]', '', message)
                    print(message)
                    # Writes the command to a functions file.
                    with open(output_file, 'a') as f:
                        f.write(f"{prefix_command}{message}" + '\n')

            
    except websockets.exceptions.ConnectionClosedError:
        print('Disconnected from MineCraft')


async def main():
    async with websockets.serve(blockbuilders_ws, host='localhost', port=3000):
        print('command to connect: /connect localhost:3000')
        await asyncio.Future()


asyncio.run(main())
