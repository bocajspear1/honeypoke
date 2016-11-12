import os
import threading
import time
import hashlib



class HoneyPokeServer(threading.Thread):

    def __init__(self, port, protocol, queue):
        threading.Thread.__init__(self)
        self._port = port
        self._protocol = protocol
        self.daemon = True
        self._queue = queue


    def ready(self):
        self._queue.put(True)

    def save_large(self, data):
        m = hashlib.md5()
        m.update(data)
        output_filename = "./large/" + str(time.time()) + "-" + m.hexdigest() + ".large"

        out_file = open(output_filename, "wb")
        out_file.write(data)
        out_file.close()

        return output_filename

