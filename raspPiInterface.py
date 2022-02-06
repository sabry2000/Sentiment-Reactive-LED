import asyncio

import websockets
import socket

# create handler for each connection
colors = []
starts = []
ends = []

async def server(websocket, path):
    global colors, starts, ends

    print("Created server")
    name = await websocket.recv()

    if name == "RPi":
        numOfElements = len(colors)

        await websocket.send(numOfElements)
        confirm = await websocket.recv()

        if confirm == "OK":
            for i, color in enumerate(colors):
                await websocket.send(color)
                await websocket.send(starts[i])
                await websocket.send(ends[i])
                
            print(confirm)      

def sendSentimentAnalysisResults(sar_df):
    global colors, starts, ends
    
    sentiments = sar_df['sentiment'].tolist()
    starts = sar_df['start'].tolist()
    ends = sar_df['end'].tolist()
    
    colors = []
    for sentiment in sentiments:
        if sentiment == "POSITIVE":
            color = "g"
        elif sentiment == "NEGATIVE":
            color = "r"
        else:
            color = "b"
        
        colors.append(color)

    host = '192.168.0.24' #Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server Started")

    data, addr = s.recvfrom(1024)
    name = data.decode('utf-8')

    print(name)

    if name == "RPi":
        numOfElements = len(colors)

        s.sendto(str(numOfElements).encode('utf-8'), addr)
        print("Sent number of elements")

        data, addr = s.recvfrom(1024)
        confirm = data.decode('utf-8')

        if confirm == "OK":
            for i, color in enumerate(colors):
                s.sendto(color.encode('utf-8'), addr)
                #data, addr = s.recvfrom(1024)
                s.sendto(str(starts[i]).encode('utf-8'), addr)
                #data, addr = s.recvfrom(1024)
                s.sendto(str(ends[i]).encode('utf-8'), addr)
                data, addr = s.recvfrom(1024)
                x = data.decode('utf-8')
                print(i)

                
            print(confirm)   
            s.close()

    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)

    #start_server = websockets.serve(server, "localhost", 8765)   
    #asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_forever()