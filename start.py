# Need libpcap-dev

import time
import sys

if sys.version_info.major == 2:
    from lib.py2server import Py2HoneyPokeServer as PyHoneyPokeServer
else:
    from lib.py3server import Py3HoneyPokeServer as PyHoneyPokeServer

server = PyHoneyPokeServer(53, "tcp")
server.start()

while True:
    time.sleep(2)