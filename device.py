import sanic
import websockets
import asyncio
import paramiko
import os
import json
from config import *
from sanic.log import logger
from common.utils import is_file_or_dir
from common.logger import LOGGING_CONFIG
from common.salt import saltenc
from common.service_info import GetFullSystemData

device_app=sanic.Sanic("infrastructure", log_config=LOGGING_CONFIG)
device_app.config.WEBSOCKET_PING_TIMEOUT = 30

@device_app.post("/report")
def report(request):
    try:
        try:
            logger.debug('building sftp connection')
            transport = paramiko.Transport(sftp_host, sftp_port)
            transport.connect(None, username=sftp_usrname, password=sftp_pwd)
            logger.debug('sftp connection built successfully')
        except Exception:
            logger.debug('build sftp connection error')
        # 尝试传输日志文件
        try:
            sftp = paramiko.SFTPClient.from_transport(transport)
            for f in os.listdir(sftp_log_pth):
                if is_file_or_dir(f):
                    sftp.put(sftp_log_pth+f, sftp_remote_log_pth+f)
                else:
                    for ff in os.listdir(sftp_log_pth+f):
                        if is_file_or_dir(ff):
                            sftp.put(sftp_log_pth+f+"/"+ff, sftp_remote_log_pth+f+"/"+ff)
                        else:
                            for fff in os.listdir(sftp_log_pth+f+"/"+ff):
                                if is_file_or_dir(fff):
                                    sftp.put(sftp_log_pth+f+"/"+ff+"/"+fff, sftp_remote_log_pth+f+"/"+ff+"/"+fff)    
            transport.close()
        except Exception:
            logger.debug('sftp transport process error')
        finally:
            logger.info()
        return "success"
    except Exception:
        logger.error('sftp error')
    finally:
        logger.info('logs sftp upload finish')

async def connect_edge(edge_app):
    logger.debug('start connect cloud')
    try:
        # async with websockets.connect("ws://{}:{}/device_login".format(edge_host, str(edge_port))) as ws:
        async with websockets.connect("ws://" + edge_host +":"+ str(edge_port) + "/device_login") as ws:      
            logger.info('websocket to edge start')      
            content = {"method":"auth","params":[device_id, saltenc(device_id, pwd)]}
            content = json.dumps(content)
            await ws.send(content)
            auth = await ws.recv()
            if auth:
                logger.info('websocket auth successfully')
                globals()["ws_edge"]=ws
                while True:
                    resp = await ws.recv()
                    resp = json.loads(resp)
                    print(resp)
        logger.info('websocket to edge end')   
    except Exception:
        logger.error('websocket with edge process error')
    finally:
        globals()["ws_edge"]=None

async def heartbeat(edge_app):
    while True:
        await asyncio.sleep(10)
        if globals()["ws_edge"]!=None:
            print(globals()["ws_edge"])
            logger.debug("heartbeat status report")
            ws = globals()["ws_edge"]
            content = {"method":"heartbeat", "params":[GetFullSystemData()]}
            content = json.dumps(content)
            await ws.send(content)

@device_app.before_server_start
async def main_start(*_):
    logger.debug("background process start")
    device_app.add_task(heartbeat(device_app))
    device_app.add_task(connect_edge(device_app))


def start():
    device_app.run(host=device_host, port=device_port, access_log=True, debug=True)

if __name__ == "__main__":
    start()