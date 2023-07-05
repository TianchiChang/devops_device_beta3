import sanic
import websockets
import asyncio
import paramiko
import os
import json
from config import *
from sanic.log import logger
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
            transport = paramiko.Transport(sock=globals()['ws_edge'])
            transport.connect(None, username=device_id, password=saltenc(device_id))
            logger.debug('sftp connection built successfully')
        except Exception:
            logger.debug('build sftp connection error')
        # 尝试传输日志文件
        try:
            sftp = paramiko.SFTPClient.from_transport(transport)
            for f in os.listdir(log_path): # 遍历设备操作日志目录，将所有的logfile上传
                sftp.put(log_path+f, remote_log_path+f)
            transport.close()
        except Exception:
            logger.debug('sftp transport process error')
        finally:
            logger.info()
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
                    if resp["method"] == "report":
                            logger.info('receive report command')
                            try:
                                try:
                                    logger.info('sftp log transport process start')
                                    # transport = paramiko.Transport(sock=ws)
                                    # transport = paramiko.Transport(edge_host, edge_port)
                                    # transport.connect(None, username=device_id, password=saltenc(device_id))
                                    logger.debug('sftp connection built successfully')
                                except Exception:
                                    logger.error('build sftp connection error')
                                # 尝试传输日志文件
                                try:
                                    # sftp = paramiko.SFTPClient.from_transport(transport)
                                    sftp = paramiko.SFTPClient.from_transport(ws)
                                    for f in os.listdir(log_path): # 遍历设备操作日志目录，将所有的logfile上传
                                        sftp.put(log_path+f, remote_log_path+f)
                                    # transport.close()
                                except Exception:
                                    logger.error('sftp transport process error')
                            except Exception:
                                logger.error('sftp error')
                            finally:
                                logger.debug('logs sftp upload finish')
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