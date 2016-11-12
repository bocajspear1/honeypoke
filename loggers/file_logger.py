import datetime

class FileLogger(object):

    def __init__(self):
        pass
    
    def log(self, remote_ip, remote_port, protocol, port, data, is_binary):
        log_path = "./logs/port-" + protocol + "-" + str(port) + ".log"

        output_file = open(log_path, "a")
        now = datetime.datetime.now().isoformat()
        output_file.write(now + " - From {}:{} - {}\n".format(remote_ip, remote_port, data))
        output_file.close()
