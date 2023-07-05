import json
from sanic import Sanic
from config import *
from common.salt import saltdec
import aioconsole

app = Sanic(__name__)

@app.websocket("/device_login")
async def edge_login(request,ws):
    auth_data = await ws.recv()
    print(auth_data)
    target = json.loads(auth_data)["params"][1]
    dec_target = saltdec(target, pwd)
    origin = json.loads(auth_data)["params"][0]
    if dec_target==origin:
        await ws.send("success")
        while True:
            receive_data = await ws.recv()
            print(receive_data)
            content = await aioconsole.ainput("command: ")
            await ws.send({'method':content, 'params':[]})
        
    
if __name__ == "__main__":
    app.run(host=edge_host, port=edge_port)