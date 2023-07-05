import time

device_id = "dedajfaiuhfahifiua"
device_host = "localhost"
device_port = 84
edge_host = "localhost"
edge_port = 83
log_path = "./Logs/"
remote_log_path = "./Logs/" + device_id + "/"

pwd = "the password 42"

globals()["ws_cloud"] = None

today = time.strftime('%Y-%m-%d',time.localtime(time.time()))