import os
import datetime
import threading


class HoneyPokeServer(threading.Thread):

    def __init__(self, port, protocol, queue):
        threading.Thread.__init__(self)
        self._port = port
        self._protocol = protocol
        self._log_path = "./logs/port-" + self._protocol + "-" + str(self._port) + ".log"
        self.daemon = True
        self._queue = queue

    def write_input(self, remote_host, remote_port, data):
        output_file = open(self._log_path, "a")
        now = datetime.datetime.now().isoformat()
        output_file.write(now + " - From {}:{} - {}\n".format(remote_host, remote_port, data))
        output_file.close()

    def ready(self):
        self._queue.put(True)


