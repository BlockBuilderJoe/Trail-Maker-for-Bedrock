import asyncio
import websockets
import json
from uuid import uuid4
import os

######################################### Variables ############################################################################
#Read the README.md for instructions of how to use. 

#What summon command do you want to prefix to the coordinate?
entity_name = "blockbuilders:trail"
#Where do you want to write the mcfunction to?
path_to_functions_folder = "/Users/joe/Library/Application Support/minecraftpe/games/com.mojang/development_behavior_packs/BP/functions"

####################################################################################################################################
async def blockbuilders_ws(websocket):
    print('Connected')
    #Function to make a trail based on the position of the player in the game.
    async def trail(message):
        trail_command = message.split()#splits the message into a so we can extract the filename and undo command if it exists.
        #Undo command
        if len(trail_command) == 4: # if there is a trail_command[3] then it will run the undo command.
            if not os.path.exists(os.path.join(path_to_functions_folder, trail_command[1], trail_command[2])): #check if the file exists
                await send(f"say {trail_command[2]} doesn't exist") #if it doesn't exist then send a message to the player and
                return #return to the main function
            
            with open(os.path.join(path_to_functions_folder, trail_command[1], trail_command[2]), 'r') as f: #read the file to undo
                #if len(f.readlines()) == 0: #if the file is empty then
                    #await send(f"say {trail_command[2]} is empty") #send a message to the player and 
                    #return #return to the main function
                    
                lines = f.readlines() #read the linesin the function.
                last_line = lines[-1] #get the last line
                last_line = last_line.split() #split the last line
                x, y, z = last_line[2], last_line[3], last_line[4] #get the x, y, z coordinates
                await send(f"kill @e[type={entity_name}, x={x}, y={y}, z={z}, r=1]") #kill the entity in the game session.
                lines.pop() #remove the last line from the file
                with open(os.path.join(path_to_functions_folder, trail_command[1], trail_command[2]), 'w') as f: #open the function file in write mode.
                    f.writelines(lines) #write the lines back to the .mcfunction file
        else:
            await send(f"summon {entity_name} ~ ~ ~") #Summons the trail at the players position.
            player_response = json.loads(await websocket.recv()) # Reads the response from the game session.
            player_x, player_y, player_z  = player_response['body']['spawnPos']['x'], player_response['body']['spawnPos']['y'], player_response['body']['spawnPos']['z'] #stores the build positions in variables.
            if not os.path.exists(os.path.join(path_to_functions_folder, trail_command[1])): #create the path to the function file if it doesn't exist.
                print("Path doesn't exist, creating path")
                os.makedirs(os.path.join(path_to_functions_folder, trail_command[1])) 
            with open(os.path.join(path_to_functions_folder, trail_command[1], trail_command[2]), 'a') as f: #Uses an os join command to open the function file based on the path_to_functions_folder variable and the filename which is trail_command[1].
                f.write(f"summon {entity_name} {player_x} {player_y} {player_z}\n") #Writes the command to the file.
        
    ###Formats any command json that needs to be sent to the game session.
    async def format_command(cmd):
        msg = {
            "header": {
                "version": 1,
                "requestId": f'{uuid4()}',
                "messagePurpose": "commandRequest",
                "messageType": "commandRequest"
            },
            "body": {
                "version": 1,
                "commandLine": cmd,
                "origin": {
                    "type": "player"
                }
            }
        }
        return msg

    ###Function to send the command to the game session
    async def send(cmd):
        msg = await format_command(cmd)#Formats the command as json. 
        await websocket.send(json.dumps(msg))#sends the message
    #subscribes to any messages the player sends
        await websocket.send(
            json.dumps({
                "header": {
                    "version": 1,                     # Use version 1 message protocol
                    "requestId": f'{uuid4()}',        # A unique ID for the request
                    "messageType": "commandRequest",  # This is a request ...
                    "messagePurpose": "subscribe"     # ... to subscribe to ...
                },
                "body": {
                    "eventName": "PlayerMessage",

                },
            
            }))
        message = json.dumps
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
            msg = json.loads(msg) # Load the message
            if 'message' in msg['body']: # Check if the message is a chat message
                message = msg['body']['message'] # Get the message
                if message.startswith('trail'): # Check if the message starts with trail
                     await trail(message)  # Run the trail function
    except websockets.exceptions.ConnectionClosedError: # type: ignore
        print('Disconnected from MineCraft')

async def main():
    async with websockets.serve(blockbuilders_ws, host='localhost', port=3000): # type: ignore
        print('command to connect: /connect localhost:3000')
        await asyncio.Future()


asyncio.run(main())