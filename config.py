import time

device_id = "dedajfaiuhfahifiua"
device_host = "localhost"
device_port = 84
edge_host = "localhost"
edge_port = 82
log_path = "./Logs/"
remote_log_path = "./Logs/" + device_id + "/"

sftp_usrname = "aibuz"
sftp_pwd = "123456"
sftp_log_pth = "D:/Grade 3 Sec/devops_device/Logs/"
sftp_remote_log_pth = "D:/Grade 3 Sec/devops_edge/Logs/" + device_id + "/"
sftp_host = '127.0.0.1'
sftp_port = 22

pwd = "the edge password"

globals()["ws_cloud"] = None

today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
